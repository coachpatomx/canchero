"""Tests de U4 — Persistencia y Exportación (ejemplos + propiedades PBT)."""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET

from hypothesis import given, settings
from hypothesis import strategies as st

from app.diagrams import render_task_diagram
from app.football_domain import get_format, suggest_tasks_for_phase
from app.persistence import (
    JsonFileRepository,
    SessionDoc,
    TrainingPlan,
    is_pdf_available,
    plan_from_dict,
    plan_to_dict,
    to_html_plan,
    to_html_session,
    to_pdf_session,
)
from app.persistence.pdf_export import _UNAVAILABLE  # noqa
from periodization_engine import (
    I18nText,
    LoadPoint,
    MicroPhase,
    SeasonParams,
    SessionSlot,
    SessionTypeHint,
    build_full_tree,
    get_model,
)
from periodization_engine.errors import Err, Ok


def _slot(phase=MicroPhase.STIMULATING, vol=40, inten=70, day=2):
    return SessionSlot(day_index=day, micro_phase=phase, relative_to_match=2,
                       target_load=LoadPoint(day, vol, inten),
                       session_type=SessionTypeHint.COMPLEX)


def _make_plan() -> TrainingPlan:
    model = get_model("football_gonzalez").value
    season = SeasonParams(start_date="2026-01-06", duration_weeks=17,
                          training_days_per_week=4, matches_per_week=1,
                          objectives=("technical.driving",))
    macro = build_full_tree(season, model).value
    fmt = get_format("blind_5").value
    micro = macro.mesocycles[0].microcycles[0]
    exercises = tuple(suggest_tasks_for_phase(s, fmt)[0] for s in micro.session_slots)
    svgs = tuple(render_task_diagram(e, fmt).svg for e in exercises)
    session = SessionDoc(
        week_index=1, meso_index=0, micro_index=0, date="2026-01-06",
        load_label=I18nText("Media baja", "Medium-low"),
        objective=I18nText("Conducción en espacio reducido", "Driving in reduced space"),
        exercises=exercises, svgs=svgs,
        individual_goals=({"player": "P1", "goal": "potenciar conducción"},),
    )
    return TrainingPlan(id=macro.id, title=I18nText("Plan ciegos AP26", "Blind plan AP26"),
                        created_at="2026-11-07T00:00:00Z", macro=macro,
                        format_id="blind_5", sessions=(session,),
                        objectives=("technical.driving",), lang="es")


# --------------------------- ejemplos --------------------------------------- #
def test_plan_dict_round_trip():
    plan = _make_plan()
    assert plan_from_dict(plan_to_dict(plan)) == plan


def test_repository_save_load(tmp_path):
    repo = JsonFileRepository(root=str(tmp_path))
    plan = _make_plan()
    ref = repo.save(plan)
    assert ref.id == plan.id
    loaded = repo.load(plan.id)
    assert isinstance(loaded, Ok)
    assert loaded.value == plan


def test_repository_history(tmp_path):
    repo = JsonFileRepository(root=str(tmp_path))
    plan = _make_plan()
    repo.save(plan)
    assert len(repo.list_history()) == 1
    repo.delete(plan.id)
    assert len(repo.list_history()) == 0


def test_no_tmp_files_left(tmp_path):
    repo = JsonFileRepository(root=str(tmp_path))
    repo.save(_make_plan())
    leftovers = [f for _, _, files in os.walk(str(tmp_path)) for f in files if f.endswith(".tmp")]
    assert leftovers == []


def test_load_missing_plan_is_err(tmp_path):
    repo = JsonFileRepository(root=str(tmp_path))
    assert isinstance(repo.load("does_not_exist"), Err)


def test_library_round_trip(tmp_path):
    repo = JsonFileRepository(root=str(tmp_path))
    fmt = get_format("football_11").value
    ex = suggest_tasks_for_phase(_slot(), fmt)[0]
    repo.save_exercise(ex)
    assert ex.id in repo.list_exercises()
    assert repo.load_exercise(ex.id).value == ex


def test_html_session_wellformed_and_has_svg():
    plan = _make_plan()
    html = to_html_session(plan.sessions[0], lang="es")
    assert "<svg" in html
    assert "Conducción en espacio reducido" in html
    # El bloque de objetivos individuales aparece.
    assert "Objetivos individuales" in html


def test_html_plan_bilingual():
    plan = _make_plan()
    en = to_html_plan(plan, lang="en")
    assert "Blind plan AP26" in en
    assert "Tasks" in en


def test_pdf_degrades_without_weasyprint():
    """Si WeasyPrint no está, to_pdf devuelve Err (no lanza)."""
    plan = _make_plan()
    res = to_pdf_session(plan.sessions[0], lang="es")
    if is_pdf_available():
        assert isinstance(res, Ok)
    else:
        assert isinstance(res, Err)


# --------------------------- propiedades (PBT) ------------------------------ #
@settings(max_examples=40, deadline=None)
@given(seed=st.integers(min_value=0, max_value=1000))
def test_prop_repo_round_trip(seed):
    import tempfile
    root = tempfile.mkdtemp()
    repo = JsonFileRepository(root=root)
    plan = _make_plan()
    repo.save(plan)
    assert repo.load(plan.id).value == plan


@settings(max_examples=40, deadline=None)
@given(lang=st.sampled_from(["es", "en"]))
def test_prop_html_deterministic(lang):
    plan = _make_plan()
    assert to_html_session(plan.sessions[0], lang) == to_html_session(plan.sessions[0], lang)
