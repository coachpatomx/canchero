"""Tests de U5 — PlanningService (orquestador). Sin levantar servidor."""
from __future__ import annotations

import tempfile

from hypothesis import given, settings
from hypothesis import strategies as st

from app.llm import LlmConfig, NullConnector, build_connector
from app.persistence import JsonFileRepository
from app.planning_service import (
    Alignment,
    PlanContext,
    PlanInput,
    PlanningService,
    SessionRequest,
    answer,
    parse_intent,
    start_interview,
    to_plan_input,
)
from periodization_engine import SeasonParams
from periodization_engine.errors import Err, Ok


def _svc():
    repo = JsonFileRepository(root=tempfile.mkdtemp())
    return PlanningService(repo=repo, llm=NullConnector())


def _pin(weeks=17, model="football_gonzalez", fmt="blind_5"):
    return PlanInput(
        season=SeasonParams(start_date="2026-01-06", duration_weeks=weeks,
                            training_days_per_week=4, matches_per_week=1,
                            objectives=("technical.driving", "tactical.reduced_space")),
        model_id=model, format_id=fmt, lang="es",
    )


# --------------------------- intent ----------------------------------------- #
def test_parse_intent_driving_reduced_space():
    intent = parse_intent("esta semana quiero una sesión de conducción en espacio reducido")
    assert "driving" in intent.technical
    assert intent.space is not None and intent.space.value == "reduced"
    assert intent.timeframe == "this_week"


# --------------------------- generate_plan ---------------------------------- #
def test_generate_plan_full_tree():
    svc = _svc()
    res = svc.generate_plan(_pin())
    assert isinstance(res, Ok)
    plan = res.value
    assert plan.macro.total_weeks == 17
    assert len(plan.sessions) == 17  # una SessionDoc por microciclo


def test_generate_plan_unknown_model_is_err():
    svc = _svc()
    res = svc.generate_plan(_pin(model="nope"))
    assert isinstance(res, Err)


def test_generate_plan_deterministic():
    svc = _svc()
    a = svc.generate_plan(_pin()).value
    b = svc.generate_plan(_pin()).value
    assert a.id == b.id
    assert a == b


# --------------------------- generate_session (RF-11) ----------------------- #
def test_session_aligned_when_macro_present():
    svc = _svc()
    plan = svc.generate_plan(_pin()).value
    ctx = PlanContext(macro=plan.macro, format_id="blind_5", lang="es")
    req = SessionRequest(text="esta semana quiero conducción en espacio reducido",
                         format_id="blind_5", lang="es")
    res = svc.generate_session(req, ctx)
    assert isinstance(res, Ok)
    doc, alignment = res.value
    assert alignment == Alignment.FULL
    # El contenido pedido se inyectó en los aspectos.
    assert "driving" in doc.exercises[0].aspects.technical


def test_session_no_macro_is_none_alignment():
    """Sin macro NO se inventa: la sesión suelta queda marcada 'none'."""
    svc = _svc()
    ctx = PlanContext(macro=None, format_id="football_11", lang="es")
    req = SessionRequest(text="sesión de pase", format_id="football_11", lang="es")
    res = svc.generate_session(req, ctx)
    assert isinstance(res, Ok)
    _, alignment = res.value
    assert alignment == Alignment.NONE


def test_session_inherits_microcycle_load():
    svc = _svc()
    plan = svc.generate_plan(_pin()).value
    ctx = PlanContext(macro=plan.macro, format_id="blind_5", lang="es")
    req = SessionRequest(text="conducción", format_id="blind_5", week_index=2, lang="es")
    doc, _ = svc.generate_session(req, ctx).value
    micro = next(m for meso in plan.macro.mesocycles for m in meso.microcycles
                 if m.week_index == 2)
    # La carga de la tarea respeta el slot del microciclo 2.
    assert doc.exercises[0].load.volume_pct == micro.session_slots[0].target_load.volume_pct


# --------------------------- edición ---------------------------------------- #
def test_edit_session_duration():
    svc = _svc()
    plan = svc.generate_plan(_pin()).value
    ctx = PlanContext(macro=plan.macro, format_id="blind_5", lang="es")
    doc, _ = svc.generate_session(SessionRequest("conducción", "blind_5", 1), ctx).value
    res = svc.edit_session_duration(doc, 0, 35)
    assert isinstance(res, Ok)
    assert res.value.exercises[0].duration_min == 35


# --------------------------- LLM off ---------------------------------------- #
def test_enrich_noop_when_llm_disabled():
    svc = _svc()
    plan = svc.generate_plan(_pin()).value
    ctx = PlanContext(macro=plan.macro, format_id="blind_5", lang="es")
    doc, _ = svc.generate_session(SessionRequest("conducción", "blind_5", 1), ctx).value
    assert svc.enrich_session(doc) == doc  # sin cambios con NullConnector


def test_llm_config_never_holds_key():
    cfg = LlmConfig(provider="openai", api_key_env_var="MY_KEY_VAR")
    # La config guarda el NOMBRE de la variable, no la clave.
    assert cfg.api_key_env_var == "MY_KEY_VAR"
    assert "sk-" not in repr(cfg)
    # Sin la variable en entorno, el conector queda deshabilitado.
    assert build_connector(cfg).is_enabled() is False


# --------------------------- entrevista (RF-3) ------------------------------ #
def test_interview_builds_plan_input():
    state = start_interview()
    for reply in ("12", "4", "1", "traditional", "football_11"):
        state = answer(state, reply)
    assert state.done
    pin = to_plan_input(state)
    assert pin.season.duration_weeks == 12
    assert pin.model_id == "traditional"


# --------------------------- propiedades (PBT) ------------------------------ #
@settings(max_examples=40, deadline=None)
@given(weeks=st.integers(min_value=4, max_value=40))
def test_prop_plan_sessions_match_weeks(weeks):
    svc = _svc()
    plan = svc.generate_plan(_pin(weeks=weeks, model="traditional", fmt="football_11")).value
    assert len(plan.sessions) == weeks


@settings(max_examples=40, deadline=None)
@given(week=st.integers(min_value=1, max_value=17))
def test_prop_aligned_session_is_full(week):
    svc = _svc()
    plan = svc.generate_plan(_pin()).value
    ctx = PlanContext(macro=plan.macro, format_id="blind_5", lang="es")
    doc, alignment = svc.generate_session(
        SessionRequest("conducción", "blind_5", week), ctx).value
    assert alignment == Alignment.FULL
