"""Modelo de datos del plan de entrenamiento y su serialización (RF-6, RF-9).

Compone los serializers de U1 (macrocycle) y U2 (exercise/format) para lograr
un round-trip completo (RNF-6).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from periodization_engine import I18nText, Macrocycle
from periodization_engine.serialization import (
    macrocycle_from_dict,
    macrocycle_to_dict,
)

from app.football_domain.serialization import exercise_from_dict, exercise_to_dict
from app.football_domain.exercise import Exercise


@dataclass(frozen=True)
class SessionDoc:
    """Una sesión materializada, lista para exportar."""

    week_index: int
    meso_index: int
    micro_index: int
    date: str                      # ISO-8601 o "" si no mapeada aún
    load_label: I18nText
    objective: I18nText
    exercises: tuple[Exercise, ...]
    svgs: tuple[str, ...] = ()     # SVG pre-renderizados (U3), opcional
    individual_goals: tuple[dict, ...] = ()  # enlaza a U6 (dict ligero por ahora)
    # Sesión rica generada por LLM (bloques narrativos). Vacío si fue determinista.
    rich_blocks: tuple[dict, ...] = ()
    source: str = "deterministic"  # "deterministic" | "llm"
    objective_specific: str = ""
    adaptation_notes: str = ""
    duration_min: int = 0
    category: str = ""


@dataclass(frozen=True)
class PlanRef:
    """Metadatos para listar el historial sin cargar el plan completo."""

    id: str
    title_es: str
    title_en: str
    created_at: str
    model_id: str
    format_id: str


@dataclass(frozen=True)
class TrainingPlan:
    id: str
    title: I18nText
    created_at: str
    macro: Macrocycle
    format_id: str
    sessions: tuple[SessionDoc, ...]
    objectives: tuple[str, ...]
    lang: str = "es"

    def to_ref(self) -> PlanRef:
        return PlanRef(
            id=self.id, title_es=self.title.es, title_en=self.title.en,
            created_at=self.created_at, model_id=self.macro.model_id,
            format_id=self.format_id,
        )


# --------------------------------------------------------------------------- #
# Serialización
# --------------------------------------------------------------------------- #
def _i18n_to_dict(t: I18nText) -> dict:
    return {"es": t.es, "en": t.en}


def _i18n(d: dict) -> I18nText:
    return I18nText(es=d["es"], en=d["en"])


def _session_to_dict(s: SessionDoc) -> dict:
    return {
        "week_index": s.week_index,
        "meso_index": s.meso_index,
        "micro_index": s.micro_index,
        "date": s.date,
        "load_label": _i18n_to_dict(s.load_label),
        "objective": _i18n_to_dict(s.objective),
        "exercises": [exercise_to_dict(e) for e in s.exercises],
        "svgs": list(s.svgs),
        "individual_goals": list(s.individual_goals),
        "rich_blocks": list(s.rich_blocks),
        "source": s.source,
        "objective_specific": s.objective_specific,
        "adaptation_notes": s.adaptation_notes,
        "duration_min": s.duration_min,
        "category": s.category,
    }


def _session_from_dict(d: dict) -> SessionDoc:
    return SessionDoc(
        week_index=d["week_index"],
        meso_index=d["meso_index"],
        micro_index=d["micro_index"],
        date=d["date"],
        load_label=_i18n(d["load_label"]),
        objective=_i18n(d["objective"]),
        exercises=tuple(exercise_from_dict(e) for e in d["exercises"]),
        svgs=tuple(d["svgs"]),
        individual_goals=tuple(d["individual_goals"]),
        rich_blocks=tuple(d.get("rich_blocks", ())),
        source=d.get("source", "deterministic"),
        objective_specific=d.get("objective_specific", ""),
        adaptation_notes=d.get("adaptation_notes", ""),
        duration_min=d.get("duration_min", 0),
        category=d.get("category", ""),
    )


def plan_to_dict(plan: TrainingPlan) -> dict:
    return {
        "id": plan.id,
        "title": _i18n_to_dict(plan.title),
        "created_at": plan.created_at,
        "macro": macrocycle_to_dict(plan.macro),
        "format_id": plan.format_id,
        "sessions": [_session_to_dict(s) for s in plan.sessions],
        "objectives": list(plan.objectives),
        "lang": plan.lang,
    }


def plan_from_dict(d: dict) -> TrainingPlan:
    return TrainingPlan(
        id=d["id"],
        title=_i18n(d["title"]),
        created_at=d["created_at"],
        macro=macrocycle_from_dict(d["macro"]),
        format_id=d["format_id"],
        sessions=tuple(_session_from_dict(s) for s in d["sessions"]),
        objectives=tuple(d["objectives"]),
        lang=d["lang"],
    )
