"""Tests de U6 — Seguimiento Individual (ejemplos + propiedades PBT)."""
from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from app.player_tracking import (
    IndividualObjective,
    ObjectiveCategory,
    PlayerSpec,
    Roster,
    add_observation,
    create_roster,
    get_player_dossier,
    get_session_individual_goals,
    roster_from_dict,
    roster_to_dict,
    set_individual_objectives,
    update_progress,
)
from periodization_engine import I18nText
from periodization_engine.errors import Err, Ok


def _roster():
    return create_roster("Selección ciegos", [
        PlayerSpec(name="Jugador 1", position_key="fw"),
        PlayerSpec(name="Jugador 2", position_key="cb"),
    ])


def _obj(cat, content_es, progress=0, oid="o1"):
    return IndividualObjective(id=oid, category=cat,
                               content=I18nText(content_es, content_es),
                               progress_pct=progress)


# --------------------------- ejemplos --------------------------------------- #
def test_create_roster():
    r = _roster()
    assert len(r.players) == 2
    assert r.players[0].position_key == "fw"


def test_set_objectives_potentiate_improve_eliminate():
    r = _roster()
    pid = r.players[0].id
    objs = [
        _obj(ObjectiveCategory.POTENTIATE, "conducción", oid="a"),
        _obj(ObjectiveCategory.IMPROVE, "orientación por sonido", oid="b"),
        _obj(ObjectiveCategory.ELIMINATE, "perder referencia del balón", oid="c"),
    ]
    res = set_individual_objectives(r, pid, objs)
    assert isinstance(res, Ok)
    dossier = get_player_dossier(res.value, pid).value
    assert len(dossier.potentiate) == 1
    assert len(dossier.improve) == 1
    assert len(dossier.eliminate) == 1


def test_update_progress_and_mastery():
    r = _roster()
    pid = r.players[0].id
    r = set_individual_objectives(r, pid, [_obj(ObjectiveCategory.IMPROVE, "pase", oid="x")]).value
    r = update_progress(r, pid, "x", 95).value
    dossier = get_player_dossier(r, pid).value
    assert dossier.mastered_count == 1


def test_update_progress_out_of_range_is_err():
    r = _roster()
    pid = r.players[0].id
    r = set_individual_objectives(r, pid, [_obj(ObjectiveCategory.IMPROVE, "pase", oid="x")]).value
    assert isinstance(update_progress(r, pid, "x", 150), Err)


def test_set_objectives_is_immutable():
    r = _roster()
    pid = r.players[0].id
    r2 = set_individual_objectives(r, pid, [_obj(ObjectiveCategory.IMPROVE, "pase")]).value
    # El roster original no cambió.
    assert r.players[0].objectives == ()
    assert len(r2.players[0].objectives) == 1


def test_observation_is_traceable():
    r = _roster()
    pid = r.players[0].id
    r = add_observation(r, pid, "sess-1", I18nText("buena sesión", "good session"),
                        "2026-11-07T00:00:00Z").value
    assert r.players[0].observations[0].session_ref == "sess-1"


def test_session_goals_order_and_filter():
    r = _roster()
    pid = r.players[0].id
    objs = [
        _obj(ObjectiveCategory.POTENTIATE, "potenciar", oid="p"),
        _obj(ObjectiveCategory.ELIMINATE, "eliminar", oid="e"),
        _obj(ObjectiveCategory.IMPROVE, "mejorar", oid="i"),
        _obj(ObjectiveCategory.IMPROVE, "dominado", progress=95, oid="d"),
    ]
    r = set_individual_objectives(r, pid, objs).value
    goals = get_session_individual_goals(r, lang="es")
    cats = [g["category"] for g in goals]
    # El dominado (95%) se filtra; orden eliminate -> improve -> potentiate.
    assert "potentiate" in cats and "eliminate" in cats
    assert cats.index("eliminate") < cats.index("improve") < cats.index("potentiate")
    assert all(g["goal"] != "dominado" for g in goals)


def test_roster_round_trip():
    r = _roster()
    pid = r.players[0].id
    r = set_individual_objectives(r, pid, [_obj(ObjectiveCategory.ELIMINATE, "x", oid="z")]).value
    r = add_observation(r, pid, "s1", I18nText("n", "n"), "2026-11-07T00:00:00Z").value
    assert roster_from_dict(roster_to_dict(r)) == r


# --------------------------- propiedades (PBT) ------------------------------ #
@settings(max_examples=100, deadline=None)
@given(progress=st.integers(min_value=0, max_value=100))
def test_prop_mastery_threshold(progress):
    r = _roster()
    pid = r.players[0].id
    r = set_individual_objectives(r, pid, [_obj(ObjectiveCategory.IMPROVE, "p", oid="m")]).value
    r = update_progress(r, pid, "m", progress).value
    dossier = get_player_dossier(r, pid).value
    assert dossier.mastered_count == (1 if progress > 90 else 0)


@settings(max_examples=100, deadline=None)
@given(progress=st.integers(min_value=-50, max_value=200))
def test_prop_progress_range_guard(progress):
    r = _roster()
    pid = r.players[0].id
    r = set_individual_objectives(r, pid, [_obj(ObjectiveCategory.IMPROVE, "p", oid="m")]).value
    res = update_progress(r, pid, "m", progress)
    if 0 <= progress <= 100:
        assert isinstance(res, Ok)
    else:
        assert isinstance(res, Err)


@settings(max_examples=60, deadline=None)
@given(n=st.integers(min_value=1, max_value=5))
def test_prop_roster_round_trip(n):
    r = create_roster("T", [PlayerSpec(f"P{i}", "fw") for i in range(n)])
    assert roster_from_dict(roster_to_dict(r)) == r
