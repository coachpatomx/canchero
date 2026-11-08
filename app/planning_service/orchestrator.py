"""PlanningService — orquestador que encadena U1→U2→U3→U4 (RF-1, RF-11).

El cerebro de coordinación. Determinista sin LLM. No conoce FastAPI (RNF-1):
recibe repo y conector LLM por inyección.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from periodization_engine import (
    I18nText,
    Macrocycle,
    Microcycle,
    SessionSlot,
    build_full_tree,
    compute_load_curve,
    get_model,
)
from periodization_engine.errors import (
    DomainError,
    DomainErrorKind,
    Err,
    Ok,
    Result,
)

from app.diagrams import render_task_diagram
from app.football_domain import get_format, suggest_tasks_for_phase
from app.football_domain.exercise import AspectTags
from app.persistence import SessionDoc, TrainingPlan

from .intent import parse_intent
from .session_request import Alignment, PlanContext, PlanInput, SessionRequest


@dataclass
class PlanningService:
    repo: object            # PlanRepository (U4)
    llm: object             # LlmConnector (U5)
    clock_iso: str = "2026-11-07T00:00:00Z"  # inyectable; sin reloj real

    # ---------------------------------------------------------------- #
    # RF-1: plan completo
    # ---------------------------------------------------------------- #
    def generate_plan(self, pin: PlanInput) -> Result[TrainingPlan]:
        model_res = get_model(pin.model_id)
        if isinstance(model_res, Err):
            return model_res
        fmt_res = get_format(pin.format_id)
        if isinstance(fmt_res, Err):
            return fmt_res
        macro_res = build_full_tree(pin.season, model_res.value)
        if isinstance(macro_res, Err):
            return macro_res
        macro = macro_res.value
        fmt = fmt_res.value

        sessions: list[SessionDoc] = []
        for m_i, meso in enumerate(macro.mesocycles):
            for mi_i, micro in enumerate(meso.microcycles):
                sessions.append(
                    self._build_session_doc(micro, meso_index=m_i, micro_index=mi_i,
                                            fmt=fmt, lang=pin.lang)
                )

        plan = TrainingPlan(
            id=macro.id,
            title=I18nText(pin.title_es, pin.title_en),
            created_at=self.clock_iso,
            macro=macro,
            format_id=pin.format_id,
            sessions=tuple(sessions),
            objectives=tuple(pin.season.objectives),
            lang=pin.lang,
        )
        return Ok(plan)

    # ---------------------------------------------------------------- #
    # RF-11: sesión suelta alineada al macro (regla S1.b)
    # ---------------------------------------------------------------- #
    def generate_session(
        self, request: SessionRequest, context: PlanContext, roster=None
    ) -> Result[tuple[SessionDoc, Alignment]]:
        fmt_res = get_format(request.format_id)
        if isinstance(fmt_res, Err):
            return fmt_res
        fmt = fmt_res.value
        intent = parse_intent(request.text)

        if context.macro is not None:
            # Alinear a un microciclo del macro vigente.
            micro = self._pick_microcycle(context.macro, request.week_index,
                                          intent.timeframe)
            if micro is None:
                return Err(DomainError(DomainErrorKind.UNSATISFIABLE_PLAN,
                                       detail="semana fuera del macro"))
            doc = self._build_session_doc(micro, meso_index=0, micro_index=micro.week_index - 1,
                                          fmt=fmt, lang=request.lang, intent=intent)
            doc = self._author_rich(doc, request, fmt, micro)
            doc = self._attach_individual_goals(doc, roster, request.lang)
            return Ok((doc, Alignment.FULL))

        # Sin macro: NO se inventa. La UI debe ofrecer entrevista (RF-3).
        # Si se llega aquí sin macro, se genera una sesión suelta marcada 'none'.
        slot = self._synthetic_slot(intent)
        doc = self._assemble(slot, fmt, request.lang, intent, week=0, meso=0, micro=0)
        doc = self._author_rich(doc, request, fmt, None)
        doc = self._attach_individual_goals(doc, roster, request.lang)
        return Ok((doc, Alignment.NONE))

    def _author_rich(self, doc: SessionDoc, request, fmt, micro):
        """Si el LLM está activo, enriquece la sesión con bloques narrativos de
        calidad profesional. Si no, deja la sesión determinista intacta (RF-10)."""
        if not self.llm.is_enabled():
            return doc
        from .session_author import build_prompt, parse_llm_session
        micro_ctx = {}
        if micro is not None:
            slot = micro.session_slots[0] if micro.session_slots else None
            micro_ctx = {
                "week": micro.week_index,
                "micro_type": micro.type.value,
                "volume": micro.target_volume_pct,
                "intensity": micro.target_intensity_pct,
                "phase": slot.micro_phase.value if slot else "stimulating",
            }
        prompt = build_prompt(request, fmt, micro_ctx, request.lang)
        res = self.llm.complete(prompt)
        if isinstance(res, Err):
            return doc  # degradación: conserva la determinista
        data = parse_llm_session(res.value)
        if not data:
            return doc
        blocks = tuple(data.get("bloques", []))
        return replace(
            doc,
            objective=I18nText(data.get("objetivo", doc.objective.es), doc.objective.en),
            objective_specific=data.get("objetivo_especifico", ""),
            adaptation_notes=data.get("notas_adaptacion", ""),
            rich_blocks=blocks,
            source="llm",
            duration_min=request.duration_min,
            category=request.category,
        )

    def _attach_individual_goals(self, doc: SessionDoc, roster, lang: str) -> SessionDoc:
        """Inserta los objetivos individuales de U6 en la sesión (plantilla mejorada)."""
        if roster is None:
            return doc
        from app.player_tracking import get_session_individual_goals
        goals = tuple(get_session_individual_goals(roster, lang))
        return replace(doc, individual_goals=goals)

    # ---------------------------------------------------------------- #
    # RF-6: edición
    # ---------------------------------------------------------------- #
    def edit_session_duration(self, doc: SessionDoc, task_index: int,
                              new_duration: int) -> Result[SessionDoc]:
        if not (0 <= task_index < len(doc.exercises)):
            return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL,
                                   detail="task_index fuera de rango"))
        if new_duration <= 0:
            return Err(DomainError(DomainErrorKind.INVALID_MODEL_RULES,
                                   detail="duración <= 0"))
        exs = list(doc.exercises)
        exs[task_index] = replace(exs[task_index], duration_min=new_duration)
        return Ok(replace(doc, exercises=tuple(exs)))

    # ---------------------------------------------------------------- #
    # RF-10: enriquecimiento LLM opcional (no-op si deshabilitado)
    # ---------------------------------------------------------------- #
    def enrich_session(self, doc: SessionDoc) -> SessionDoc:
        if not self.llm.is_enabled():
            return doc  # offline / determinista: sin cambios estructurales
        # Con LLM activo: enriquecer SOLO la redacción del objetivo de cada tarea.
        # La estructura, cargas, formato y diagramas NO se tocan (RF-10).
        new_exs = []
        for ex in doc.exercises:
            prompt = (
                "Redacta en 1-2 frases, en español claro para un entrenador, la "
                f"descripción de este ejercicio de fútbol. Tipo: {ex.task_type.value}. "
                f"Estrategia: {ex.didactic_strategy.value}. Objetivo actual: "
                f"{ex.objective.es}. No inventes cargas ni dimensiones."
            )
            res = self.llm.complete(prompt)
            if isinstance(res, Ok) and res.value.strip():
                enriched = I18nText(res.value.strip(), ex.objective.en)
                new_exs.append(replace(ex, objective=enriched))
            else:
                new_exs.append(ex)  # si el LLM falla, se conserva lo determinista
        return replace(doc, exercises=tuple(new_exs))

    # ---------------------------------------------------------------- #
    # helpers
    # ---------------------------------------------------------------- #
    def _pick_microcycle(self, macro: Macrocycle, week_index, timeframe):
        target = week_index
        if target is None and timeframe == "this_week":
            target = 1  # "esta semana" -> primer microciclo por defecto
        if target is None:
            target = 1
        for meso in macro.mesocycles:
            for micro in meso.microcycles:
                if micro.week_index == target:
                    return micro
        return None

    def _synthetic_slot(self, intent) -> SessionSlot:
        from periodization_engine import LoadPoint, MicroPhase, SessionTypeHint
        return SessionSlot(
            day_index=1, micro_phase=MicroPhase.STIMULATING, relative_to_match=None,
            target_load=LoadPoint(unit_index=1, volume_pct=40, intensity_pct=60),
            session_type=SessionTypeHint.COMPLEX,
        )

    def _build_session_doc(self, micro: Microcycle, meso_index: int,
                           micro_index: int, fmt, lang: str, intent=None) -> SessionDoc:
        # Usa el primer slot representativo del microciclo (día estimulador si hay).
        slot = micro.session_slots[0] if micro.session_slots else self._synthetic_slot(intent)
        return self._assemble(slot, fmt, lang, intent,
                              week=micro.week_index, meso=meso_index, micro=micro_index,
                              load_pct=(micro.target_volume_pct, micro.target_intensity_pct))

    def _assemble(self, slot: SessionSlot, fmt, lang: str, intent,
                  week: int, meso: int, micro: int, load_pct=None) -> SessionDoc:
        tasks = suggest_tasks_for_phase(slot, fmt)
        # Inyecta el contenido pedido (intent) en los aspectos de la primera tarea.
        if intent is not None and intent.has_content and tasks:
            tasks[0] = replace(
                tasks[0],
                aspects=AspectTags(
                    technical=intent.technical,
                    tactical=intent.tactical,
                    physical=intent.physical,
                ),
            )
        svgs = tuple(render_task_diagram(t, fmt, lang).svg for t in tasks)
        if load_pct:
            load_label = I18nText(f"vol {load_pct[0]}% / int {load_pct[1]}%",
                                  f"vol {load_pct[0]}% / int {load_pct[1]}%")
        else:
            load_label = I18nText("carga base", "base load")
        objective = I18nText(
            "Sesión alineada al microciclo" if lang == "es" else "Session aligned to microcycle",
            "Session aligned to microcycle",
        )
        return SessionDoc(
            week_index=week, meso_index=meso, micro_index=micro, date="",
            load_label=load_label, objective=objective,
            exercises=tuple(tasks), svgs=svgs,
        )
