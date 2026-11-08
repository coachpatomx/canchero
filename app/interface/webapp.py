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

from .templates import render_home, render_plan, render_roster, render_session


def create_app(service: PlanningService):
    """Crea la app FastAPI. Importa FastAPI de forma perezosa."""
    from fastapi import FastAPI, Form, Request
    from fastapi.responses import HTMLResponse, Response

    app = FastAPI(title="Canchero")
    _plans: dict[str, object] = {}       # cache en memoria de la sesión web
    _sessions: dict[str, object] = {}
    _state: dict[str, str] = {"active_plan_id": ""}  # último plan creado/abierto

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
        return render_home(history, list_models(), list_formats())

    # Lógica de creación de plan — compartida por POST y GET (GET para entornos
    # con proxy/CDN que bloquean POST de formularios, p. ej. CloudFront).
    def _do_create_plan(duration_weeks, training_days_per_week, matches_per_week,
                        model_id, format_id, lang):
        pin = PlanInput(
            season=SeasonParams(
                start_date="2026-01-06",
                duration_weeks=int(duration_weeks),
                training_days_per_week=int(training_days_per_week),
                matches_per_week=int(matches_per_week),
            ),
            model_id=model_id, format_id=format_id, lang=lang,
        )
        res = service.generate_plan(pin)
        if isinstance(res, Err):
            return HTMLResponse(f"<p>Error: {res.error.message_es}</p>", status_code=400)
        plan = res.value
        service.repo.save(plan)
        _plans[plan.id] = plan
        _state["active_plan_id"] = plan.id
        return HTMLResponse(render_plan(plan, lang))

    @app.post("/plan", response_class=HTMLResponse)
    def create_plan(
        duration_weeks: int = Form(...),
        training_days_per_week: int = Form(...),
        matches_per_week: int = Form(...),
        model_id: str = Form(...),
        format_id: str = Form(...),
        lang: str = Form("es"),
    ):
        return _do_create_plan(duration_weeks, training_days_per_week,
                               matches_per_week, model_id, format_id, lang)

    @app.get("/plan", response_class=HTMLResponse)
    def create_plan_get(
        duration_weeks: int = 20,
        training_days_per_week: int = 4,
        matches_per_week: int = 1,
        model_id: str = "traditional",
        format_id: str = "football_11",
        lang: str = "es",
    ):
        return _do_create_plan(duration_weeks, training_days_per_week,
                               matches_per_week, model_id, format_id, lang)

    def _do_create_session(text, format_id, plan_id, lang):
        effective_plan_id = plan_id or _state.get("active_plan_id", "")
        macro = None
        if effective_plan_id and effective_plan_id in _plans:
            macro = _plans[effective_plan_id].macro
        ctx = PlanContext(macro=macro, format_id=format_id, lang=lang)
        res = service.generate_session(SessionRequest(text=text, format_id=format_id, lang=lang), ctx)
        if isinstance(res, Err):
            return HTMLResponse(f"<p>Error: {res.error.message_es}</p>", status_code=400)
        doc, alignment = res.value
        sid = f"{format_id}-{doc.week_index}"
        _sessions[sid] = doc
        return HTMLResponse(render_session(doc, alignment, lang, pdf_available=is_pdf_available()))

    @app.post("/session", response_class=HTMLResponse)
    def create_session(
        text: str = Form(...),
        format_id: str = Form(...),
        plan_id: str = Form(""),
        lang: str = Form("es"),
    ):
        return _do_create_session(text, format_id, plan_id, lang)

    @app.get("/session", response_class=HTMLResponse)
    def create_session_get(
        text: str = "",
        format_id: str = "football_11",
        plan_id: str = "",
        lang: str = "es",
    ):
        return _do_create_session(text, format_id, plan_id, lang)

    @app.get("/session/{sid}/print", response_class=HTMLResponse)
    def print_session(sid: str, lang: str = "es"):
        doc = _sessions.get(sid)
        if doc is None:
            return HTMLResponse("<p>No encontrada</p>", status_code=404)
        return to_html_session(doc, lang)

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
