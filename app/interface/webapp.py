"""App web local (RF-2) con FastAPI. Capa fina sobre PlanningService.

FastAPI es dependencia opcional (grupo web). El import está aislado aquí; el
orquestador no depende de FastAPI (RNF-1).
"""
from __future__ import annotations

from app.football_domain import get_format, list_formats
from app.persistence import is_pdf_available, to_html_session
from app.planning_service import (
    PlanContext,
    PlanInput,
    PlanningService,
    SessionRequest,
)
from periodization_engine import SeasonParams, list_models
from periodization_engine.errors import Err


def _esc_html(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


from .templates import (
    render_home,
    render_macro_interview,
    render_plan,
    render_plan_studio,
    render_roster,
    render_session,
    render_session_interview,
    render_session_studio,
    render_sessions_history,
)


def create_app(service: PlanningService):
    """Crea la app FastAPI. Importa FastAPI de forma perezosa."""
    from fastapi import FastAPI, Form, Request
    from fastapi.responses import HTMLResponse, Response

    app = FastAPI(title="Canchero")
    # Dar a las plantillas acceso al repo para listar planes/sesiones recientes.
    from .templates import set_repo_ref
    set_repo_ref(service.repo)
    _plans: dict[str, object] = {}       # cache en memoria de la sesión web
    _sessions: dict[str, object] = {}
    _session_order: list[str] = []       # historial de sesiones (orden)
    _state: dict[str, str] = {"active_plan_id": "", "active_category": ""}
    _chat: dict[str, list] = {}          # historial de chat del estudio (macro), por plan_id
    _session_chat: dict[str, list] = {}  # historial de chat del estudio de sesión, por sid

    # Sirve los archivos estáticos (logo Canchero, favicon) desde app/interface/static
    import os
    from fastapi.responses import FileResponse

    _STATIC = os.path.join(os.path.dirname(__file__), "static")

    @app.get("/static/{name}")
    def static_file(name: str):
        path = os.path.join(_STATIC, os.path.basename(name))
        if not os.path.exists(path):
            return Response(status_code=404)
        return FileResponse(path)

    @app.get("/favicon.ico")
    def favicon():
        return FileResponse(os.path.join(_STATIC, "canchero.svg"),
                            media_type="image/svg+xml")

    @app.get("/", response_class=HTMLResponse)
    def home():
        history = service.repo.list_history()
        llm_on = bool(getattr(service.llm, "is_enabled", lambda: False)())
        return render_home(history, list_models(), list_formats(), llm_on=llm_on)

    # Lógica de creación de plan — compartida por POST y GET (GET para entornos
    # con proxy/CDN que bloquean POST de formularios, p. ej. CloudFront).
    def _do_create_plan(duration_weeks, training_days_per_week, matches_per_week,
                        model_id, format_id, lang, title="", category=""):
        plan_title = title.strip() or "Plan de temporada"
        pin = PlanInput(
            season=SeasonParams(
                start_date="2026-01-06",
                duration_weeks=int(duration_weeks),
                training_days_per_week=int(training_days_per_week),
                matches_per_week=int(matches_per_week),
            ),
            model_id=model_id, format_id=format_id, lang=lang,
            title_es=plan_title, title_en=plan_title,
        )
        res = service.generate_plan(pin)
        if isinstance(res, Err):
            return HTMLResponse(f"<p>Error: {res.error.message_es}</p>", status_code=400)
        plan = res.value
        service.repo.save(plan)
        _plans[plan.id] = plan
        _state["active_plan_id"] = plan.id
        _state["active_category"] = category
        return HTMLResponse(render_plan(plan, lang, service.repo.list_sessions()))

    @app.post("/plan", response_class=HTMLResponse)
    def create_plan(
        title: str = Form(""),
        duration_weeks: int = Form(...),
        training_days_per_week: int = Form(...),
        matches_per_week: int = Form(...),
        model_id: str = Form(...),
        format_id: str = Form(...),
        category: str = Form(""),
        lang: str = Form("es"),
    ):
        return _do_create_plan(duration_weeks, training_days_per_week,
                               matches_per_week, model_id, format_id, lang, title, category)

    @app.get("/plan", response_class=HTMLResponse)
    def create_plan_get(
        title: str = "",
        duration_weeks: int = 20,
        training_days_per_week: int = 4,
        matches_per_week: int = 1,
        model_id: str = "traditional",
        format_id: str = "football_11",
        category: str = "",
        lang: str = "es",
    ):
        return _do_create_plan(duration_weeks, training_days_per_week,
                               matches_per_week, model_id, format_id, lang, title, category)

    # ---- Entrevista conversacional para crear el macro (estilo AI-DLC) ---- #
    import json as _json

    def _decode_answers(s: str) -> dict:
        try:
            return _json.loads(s) if s else {}
        except (ValueError, TypeError):
            return {}

    @app.get("/plan/new", response_class=HTMLResponse)
    def plan_new(mode: str = "guided", lang: str = "es"):
        from app.planning_service import macro_interview as mi
        answers: dict = {}
        q = mi.next_question(answers)
        return HTMLResponse(render_macro_interview(answers, q, mode, lang))

    @app.get("/plan/new/answer", response_class=HTMLResponse)
    def plan_new_answer(step: str = "", value: str = "", answers: str = "",
                        mode: str = "guided", lang: str = "es"):
        from app.planning_service import macro_interview as mi
        a = _decode_answers(answers)
        if step:
            a[step] = value
        q = mi.next_question(a)
        return HTMLResponse(render_macro_interview(a, q, mode, lang))

    @app.get("/plan/new/create", response_class=HTMLResponse)
    def plan_new_create(answers: str = "", lang: str = "es"):
        from app.planning_service import macro_interview as mi
        a = _decode_answers(answers)
        if not mi.is_complete(a):
            q = mi.next_question(a)
            return HTMLResponse(render_macro_interview(a, q, "guided", lang))
        kw = mi.to_plan_input_kwargs(a)
        meta = kw.pop("_meta", {})
        resp = _do_create_plan(
            kw["duration_weeks"], kw["training_days_per_week"], kw["matches_per_week"],
            kw["model_id"], kw["format_id"], lang, kw["title"], kw["category"],
        )
        # Guardar metadatos (equipo, fecha de inicio, competencias) del plan nuevo.
        pid = _state.get("active_plan_id", "")
        if pid and meta:
            try:
                service.repo.save_plan_meta(pid, meta)
            except Exception:
                pass
        # Llevar directo al estudio (chat + vista previa).
        if pid:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=f"/plan/{pid}/chat", status_code=303)
        return resp

    @app.get("/plan/new/express", response_class=HTMLResponse)
    def plan_new_express(text: str = "", lang: str = "es"):
        """Modo experto: intenta extraer todo de una frase con el LLM; si no hay
        LLM o falla, cae a valores razonables y abre la entrevista con lo que pudo."""
        from app.planning_service import macro_interview as mi
        a = mi.express_parse(text, service.llm)
        # La categoría es opcional: si todo lo demás está, no debe bloquear.
        if "category" not in a:
            faltan = [k for k in mi.STEPS if k != "category"
                      and (a.get(k) in (None, ""))]
            if not faltan:
                a["category"] = "__none__"
        q = mi.next_question(a)
        if q is None:  # logró todo -> generar directo
            return plan_new_create(answers=_json.dumps(a), lang=lang)
        # Faltó algún dato: continúa la entrevista GUIADA con lo que ya se tiene.
        return HTMLResponse(render_macro_interview(a, q, "guided", lang))

    @app.get("/plan/{plan_id}/excel")
    def export_plan_excel(plan_id: str):
        plan = _plans.get(plan_id)
        if plan is None:
            res = service.repo.load(plan_id)
            if isinstance(res, Err):
                return Response(status_code=404)
            plan = res.value
        from app.persistence import plan_to_xlsx_bytes
        data = plan_to_xlsx_bytes(plan)
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="macrociclo-{plan_id}.xlsx"'},
        )

    @app.get("/plan/{plan_id}/matrix", response_class=HTMLResponse)
    def view_plan_matrix(plan_id: str, lang: str = "es", team: str = "",
                         coordinator: str = "", coach: str = "", period_label: str = ""):
        plan = _plans.get(plan_id)
        if plan is None:
            res = service.repo.load(plan_id)
            if isinstance(res, Err):
                return HTMLResponse("<p>Plan no encontrado</p>", status_code=404)
            plan = res.value
            _plans[plan_id] = plan
        from app.persistence import to_html_plan_matrix
        meta = service.repo.load_plan_meta(plan_id)
        html = to_html_plan_matrix(
            plan, lang,
            team=team or meta.get("team", ""),
            coordinator=coordinator or meta.get("coordinator", ""),
            coach=coach or meta.get("coach", ""),
            period_label=period_label or meta.get("period_label", ""),
            start_date=meta.get("start_date", ""),
            competitions=meta.get("competitions", []),
            category=meta.get("category", ""),
            days_per_week=meta.get("days_per_week", 0),
            title_override=meta.get("title_override", ""),
        )
        return HTMLResponse(html)

    def _load_plan(plan_id):
        plan = _plans.get(plan_id)
        if plan is None:
            res = service.repo.load(plan_id)
            if isinstance(res, Err):
                return None
            plan = res.value
            _plans[plan_id] = plan
        return plan

    @app.get("/plan/{plan_id}/chat", response_class=HTMLResponse)
    def plan_studio(plan_id: str, lang: str = "es", team: str = "",
                    coordinator: str = "", coach: str = "", period_label: str = ""):
        plan = _load_plan(plan_id)
        if plan is None:
            return HTMLResponse("<p>Plan no encontrado</p>", status_code=404)
        meta = {"team": team, "coordinator": coordinator, "coach": coach,
                "period_label": period_label}
        _llm_on = bool(getattr(service.llm, "is_enabled", lambda: False)())
        return HTMLResponse(render_plan_studio(plan, lang, _chat.get(plan_id, []), meta, _llm_on))

    @app.get("/plan/{plan_id}/chat/apply", response_class=HTMLResponse)
    def plan_studio_apply(plan_id: str, instruction: str = "", lang: str = "es",
                          team: str = "", coordinator: str = "", coach: str = "",
                          period_label: str = ""):
        plan = _load_plan(plan_id)
        if plan is None:
            return HTMLResponse("<p>Plan no encontrado</p>", status_code=404)
        meta = {"team": team, "coordinator": coordinator, "coach": coach,
                "period_label": period_label}
        hist = _chat.setdefault(plan_id, [])
        instruction = (instruction or "").strip()
        if instruction:
            from dataclasses import replace as _replace
            from app.planning_service.plan_editor import edit_macro_from_text
            hist.append({"role": "user", "text": instruction})
            plan_meta = service.repo.load_plan_meta(plan_id)
            new_macro, new_meta, message = edit_macro_from_text(
                service.llm, plan.macro, instruction, plan_meta)
            # Reconstruir el plan con el macro mutado y persistir.
            plan = _replace(plan, macro=new_macro)
            _plans[plan_id] = plan
            try:
                service.repo.save(plan)
                service.repo.save_plan_meta(plan_id, new_meta)
            except Exception:
                pass  # si falla el guardado, al menos la cache queda actualizada
            hist.append({"role": "assistant", "text": message})
        # Recargar meta para que el estudio y la vista previa reflejen los cambios.
        _llm_on = bool(getattr(service.llm, "is_enabled", lambda: False)())
        return HTMLResponse(render_plan_studio(plan, lang, hist,
                                               service.repo.load_plan_meta(plan_id), _llm_on))

    @app.get("/plan/{plan_id}", response_class=HTMLResponse)
    def view_plan(plan_id: str, lang: str = "es"):
        plan = _load_plan(plan_id)
        if plan is None:
            return HTMLResponse("<p>Plan no encontrado</p>", status_code=404)
        _state["active_plan_id"] = plan_id  # abrir un plan lo hace activo
        return HTMLResponse(render_plan(plan, lang, service.repo.list_sessions()))

    def _do_create_session(req_kwargs, plan_id, lang, sheet_meta=None):
        effective_plan_id = plan_id or _state.get("active_plan_id", "")
        macro = None
        if effective_plan_id:
            # Cargar el plan elegido (de cache o disco) para alinear la sesión.
            plan_obj = _plans.get(effective_plan_id)
            if plan_obj is None:
                loaded = service.repo.load(effective_plan_id)
                if not isinstance(loaded, Err):
                    plan_obj = loaded.value
                    _plans[effective_plan_id] = plan_obj
            if plan_obj is not None:
                macro = plan_obj.macro
        # Hereda categoría del plan activo si no se especificó en la sesión.
        if not req_kwargs.get("category"):
            req_kwargs["category"] = _state.get("active_category", "")
        fmt_id = req_kwargs["format_id"]
        ctx = PlanContext(macro=macro, format_id=fmt_id, lang=lang)
        try:
            res = service.generate_session(SessionRequest(**req_kwargs), ctx)
            if isinstance(res, Err):
                return HTMLResponse(f"<p>Error: {res.error.message_es}</p>", status_code=400)
            doc, alignment = res.value
            # Aplicar estilo de hoja y metadatos de encabezado (plantilla inclusiva).
            if sheet_meta:
                from dataclasses import replace as _replace
                doc = _replace(
                    doc,
                    sheet_style=sheet_meta.get("sheet_style", "dark"),
                    team_name=sheet_meta.get("team_name", ""),
                    coach_name=sheet_meta.get("coach_name", ""),
                    schedule=sheet_meta.get("schedule", ""),
                    session_number=sheet_meta.get("session_number", ""),
                    format_id=sheet_meta.get("format_id", "") or doc.format_id,
                )
            # Persistir la sesión en disco (historial de sesiones).
            sid = service.repo.save_session(doc, plan_id=effective_plan_id)
            _sessions[sid] = doc
            _session_order.append(sid)
            return HTMLResponse(render_session(doc, alignment, lang,
                                               pdf_available=is_pdf_available(), sid=sid))
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return HTMLResponse(
                f"<h3>Ocurrió un error al generar la sesión</h3>"
                f"<p>El equipo puede revisar el detalle abajo. La planificación "
                f"determinista no se ve afectada.</p>"
                f"<pre style='white-space:pre-wrap;background:#161b22;color:#f4f4f0;"
                f"padding:12px;border-radius:8px'>{_esc_html(str(e))}\n\n{_esc_html(tb)}</pre>"
                f"<p><a href='/'>← Inicio</a></p>",
                status_code=500,
            )

    def _int_or(v, default):
        try:
            return int(v)
        except (TypeError, ValueError):
            return default

    from fastapi import Query

    # ---- Entrevista conversacional para crear una SESIÓN ---- #
    def _plans_for_picker():
        rows = []
        for ref in service.repo.list_history():
            rows.append({"id": ref.id, "title": ref.title_es})
        return rows

    def _resolve_sheet_style(style, format_id):
        if style and style != "auto":
            return style
        adaptados = {"blind_5", "cp_7", "down", "amputee"}
        return "inclusivo" if format_id in adaptados else "dark"

    @app.get("/session/new", response_class=HTMLResponse)
    def session_new(lang: str = "es"):
        from app.planning_service import session_interview as si
        answers: dict = {}
        q = si.next_question(answers, _plans_for_picker())
        return HTMLResponse(render_session_interview(answers, q, _plans_for_picker(), lang))

    @app.get("/session/new/answer", response_class=HTMLResponse)
    def session_new_answer(step: str = "", value: str = "", answers: str = "", lang: str = "es"):
        from app.planning_service import session_interview as si
        a = _decode_answers(answers)
        if step:
            a[step] = value
        plans = _plans_for_picker()
        q = si.next_question(a, plans)
        return HTMLResponse(render_session_interview(a, q, plans, lang))

    @app.get("/session/new/create", response_class=HTMLResponse)
    def session_new_create(answers: str = "", lang: str = "es"):
        from app.planning_service import session_interview as si
        a = _decode_answers(answers)
        plans = _plans_for_picker()
        if not si.is_complete(a, plans):
            q = si.next_question(a, plans)
            return HTMLResponse(render_session_interview(a, q, plans, lang))
        # Formato: hereda del plan elegido, o del plan activo, o football_11.
        plan_id = "" if a.get("plan") in ("__none__", "", None) else a.get("plan")
        fmt = "football_11"
        src_plan = plan_id or _state.get("active_plan_id", "")
        if src_plan:
            loaded = service.repo.load(src_plan)
            if not isinstance(loaded, Err):
                fmt = loaded.value.format_id or fmt
        kw = si.to_session_kwargs(a, default_format=fmt)
        req = kw["request"]
        req["format_id"] = fmt
        style = _resolve_sheet_style(kw.get("sheet_style", "auto"), fmt)
        sheet_meta = dict(sheet_style=style, team_name="", coach_name="",
                          schedule="", session_number="", format_id=fmt)
        # Reusar el mismo flujo que el formulario clásico.
        resp = _do_create_session(req, plan_id, lang, sheet_meta)
        # _do_create_session renderiza la sesión; para llevar al estudio de sesión
        # buscamos el último sid creado.
        if _session_order:
            sid = _session_order[-1]
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=f"/session/{sid}/chat", status_code=303)
        return resp

    @app.get("/session", response_class=HTMLResponse)
    def create_session_get(
        text: str = "",
        format_id: str = "football_11",
        plan_id: str = "",
        lang: str = "es",
        duration_min: str = "90",
        category: str = "",
        n_players: str = "",
        schedule: str = "",
        phase: str = "",
        technical_focus: list[str] = Query(default=[]),
        technical_focus_extra: str = "",
        tactical_focus: list[str] = Query(default=[]),
        tactical_focus_extra: str = "",
        physical_focus: list[str] = Query(default=[]),
        physical_focus_extra: str = "",
        materials: str = "",
        week_index: str = "",
        sheet_style: str = "dark",
        team_name: str = "",
        coach_name: str = "",
        session_number: str = "",
    ):
        def _combine(vals, extra):
            out = [v.strip() for v in vals if v.strip()]
            if extra and extra.strip():
                out += [x.strip() for x in extra.split(",") if x.strip()]
            return ", ".join(out)

        kwargs = dict(
            text=text, format_id=format_id, lang=lang,
            duration_min=_int_or(duration_min, 90),
            category=category, n_players=_int_or(n_players, 0),
            schedule=schedule, phase=phase,
            technical_focus=_combine(technical_focus, technical_focus_extra),
            tactical_focus=_combine(tactical_focus, tactical_focus_extra),
            physical_focus=_combine(physical_focus, physical_focus_extra),
            materials=materials,
            week_index=(_int_or(week_index, 0) or None),
        )
        sheet_meta = dict(
            sheet_style=(sheet_style or "dark"),
            team_name=team_name, coach_name=coach_name,
            schedule=schedule, session_number=session_number,
            format_id=format_id,
        )
        return _do_create_session(kwargs, plan_id, lang, sheet_meta)

    def _get_session(sid):
        doc = _sessions.get(sid)
        if doc is None:
            res = service.repo.load_session(sid)
            if isinstance(res, Err):
                return None
            doc = res.value
            _sessions[sid] = doc
        return doc

    @app.get("/session/{sid}/print", response_class=HTMLResponse)
    def print_session(sid: str, lang: str = "es"):
        doc = _get_session(sid)
        if doc is None:
            return HTMLResponse("<p>No encontrada</p>", status_code=404)
        return to_html_session(doc, lang)

    @app.get("/session/{sid}/view", response_class=HTMLResponse)
    def view_session(sid: str, lang: str = "es"):
        doc = _get_session(sid)
        if doc is None:
            return HTMLResponse("<p>No encontrada</p>", status_code=404)
        from app.planning_service import Alignment
        return HTMLResponse(render_session(doc, Alignment.FULL, lang,
                                           pdf_available=is_pdf_available(), sid=sid))

    @app.get("/session/{sid}/preview", response_class=HTMLResponse)
    def preview_session(sid: str, lang: str = "es"):
        """Solo el cuerpo imprimible de la sesión (para el iframe del estudio)."""
        doc = _get_session(sid)
        if doc is None:
            return HTMLResponse("<p>No encontrada</p>", status_code=404)
        from app.persistence.html_export import session_body_html
        return HTMLResponse(session_body_html(doc, lang))

    @app.get("/session/{sid}/chat", response_class=HTMLResponse)
    def session_studio(sid: str, lang: str = "es"):
        doc = _get_session(sid)
        if doc is None:
            return HTMLResponse("<p>Sesión no encontrada</p>", status_code=404)
        _llm_on = bool(getattr(service.llm, "is_enabled", lambda: False)())
        return HTMLResponse(render_session_studio(
            doc, sid, lang, _session_chat.get(sid, []), _llm_on))

    @app.get("/session/{sid}/chat/apply", response_class=HTMLResponse)
    def session_studio_apply(sid: str, instruction: str = "", lang: str = "es"):
        doc = _get_session(sid)
        if doc is None:
            return HTMLResponse("<p>Sesión no encontrada</p>", status_code=404)
        hist = _session_chat.setdefault(sid, [])
        instruction = (instruction or "").strip()
        if instruction:
            from app.planning_service.session_editor import edit_session_from_text
            hist.append({"role": "user", "text": instruction})
            new_doc, message = edit_session_from_text(service.llm, doc, instruction)
            _sessions[sid] = new_doc
            try:
                service.repo.update_session(sid, new_doc)
            except Exception:
                pass
            hist.append({"role": "assistant", "text": message})
            doc = new_doc
        _llm_on = bool(getattr(service.llm, "is_enabled", lambda: False)())
        return HTMLResponse(render_session_studio(doc, sid, lang, hist, _llm_on))

    @app.get("/session/{sid}/pdf")
    def pdf_session_route(sid: str, lang: str = "es"):
        doc = _get_session(sid)
        if doc is None:
            return Response(status_code=404)
        from app.persistence import to_pdf_session
        res = to_pdf_session(doc, lang)
        if isinstance(res, Err):
            return HTMLResponse("<p>PDF nativo no disponible. Usa Imprimir → Guardar como PDF.</p>",
                                status_code=409)
        return Response(content=res.value, media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="sesion-{sid}.pdf"'})

    @app.get("/sessions", response_class=HTMLResponse)
    def sessions_history(lang: str = "es"):
        return HTMLResponse(render_sessions_history(service.repo.list_sessions(), lang))

    # ---- gestión de equipo / objetivos (U6) ---- #
    from app.player_tracking import (
        IndividualObjective,
        ObjectiveCategory,
        PlayerSpec,
        add_player,
        create_roster,
        set_individual_objectives,
    )
    from periodization_engine import I18nText

    _roster = {"r": create_roster("Mi equipo", [])}

    @app.get("/roster", response_class=HTMLResponse)
    def roster_view(lang: str = "es"):
        return render_roster(_roster["r"], lang)

    def _do_add_player(name, position_key, lang):
        _roster["r"] = add_player(_roster["r"], PlayerSpec(name=name, position_key=position_key))
        return HTMLResponse(render_roster(_roster["r"], lang))

    @app.post("/roster/player", response_class=HTMLResponse)
    def roster_add_player(name: str = Form(...), position_key: str = Form(...),
                          lang: str = Form("es")):
        return _do_add_player(name, position_key, lang)

    @app.get("/roster/player", response_class=HTMLResponse)
    def roster_add_player_get(name: str = "", position_key: str = "fw", lang: str = "es"):
        if not name:
            return HTMLResponse(render_roster(_roster["r"], lang))
        return _do_add_player(name, position_key, lang)

    def _do_set_objective(player_id, category, content, lang):
        player = next((p for p in _roster["r"].players if p.id == player_id), None)
        if player is None:
            return HTMLResponse("<p>Jugador no encontrado</p>", status_code=404)
        new_obj = IndividualObjective(
            id=f"obj-{len(player.objectives)+1}",
            category=ObjectiveCategory(category),
            content=I18nText(content, content),
        )
        res = set_individual_objectives(_roster["r"], player_id,
                                        list(player.objectives) + [new_obj])
        if isinstance(res, Err):
            return HTMLResponse(f"<p>Error: {res.error.message_es}</p>", status_code=400)
        _roster["r"] = res.value
        return HTMLResponse(render_roster(_roster["r"], lang))

    @app.post("/roster/objective", response_class=HTMLResponse)
    def roster_set_objective(player_id: str = Form(...), category: str = Form(...),
                             content: str = Form(...), lang: str = Form("es")):
        return _do_set_objective(player_id, category, content, lang)

    @app.get("/roster/objective", response_class=HTMLResponse)
    def roster_set_objective_get(player_id: str = "", category: str = "potentiate",
                                 content: str = "", lang: str = "es"):
        if not player_id or not content:
            return HTMLResponse(render_roster(_roster["r"], lang))
        return _do_set_objective(player_id, category, content, lang)

    return app
