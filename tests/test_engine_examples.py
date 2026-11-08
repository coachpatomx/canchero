"""Tests de ejemplo concretos del motor de periodización (U1)."""
from __future__ import annotations

import pytest

from periodization_engine import (
    CompetitionType,
    Err,
    Ok,
    SeasonParams,
    StartFitness,
    build_full_tree,
    build_macrocycle,
    compute_load_curve,
    get_model,
    list_models,
    macrocycle_from_dict,
    macrocycle_to_dict,
)
from periodization_engine.domain import ModelRules, PeriodizationModel, ModelSource, I18nText
from periodization_engine.models import register_custom_model, _reset_custom_models


def _season(weeks=40, days=4, matches=1):
    return SeasonParams(
        start_date="2026-01-06",
        duration_weeks=weeks,
        training_days_per_week=days,
        matches_per_week=matches,
        competition_type=CompetitionType.LEAGUE,
        start_fitness=StartFitness.MEDIUM,
        objectives=("physical.endurance", "tactical.pressing"),
    )


def test_six_builtin_models_present():
    ids = {m.id for m in list_models()}
    assert ids == {
        "traditional", "blocks", "atr", "tactical", "structured",
        "football_gonzalez",
    }


def test_build_macrocycle_traditional_covers_all_weeks():
    model = get_model("traditional").value
    res = build_macrocycle(_season(40), model)
    assert isinstance(res, Ok)
    macro = res.value
    # Los períodos cubren exactamente 1..40 sin huecos ni solapes.
    assert macro.periods[0].start_week == 1
    assert macro.periods[-1].end_week == 40
    for prev, nxt in zip(macro.periods, macro.periods[1:]):
        assert nxt.start_week == prev.end_week + 1


def test_duration_too_short_is_error():
    model = get_model("traditional").value
    res = build_macrocycle(_season(weeks=2), model)
    assert isinstance(res, Err)


def test_full_tree_has_slots_per_training_day():
    model = get_model("traditional").value
    macro = build_full_tree(_season(weeks=12, days=4), model).value
    for meso in macro.mesocycles:
        for micro in meso.microcycles:
            assert len(micro.session_slots) == 4


def test_gonzalez_restart_flag():
    model = get_model("football_gonzalez").value
    assert model.rules.restart_in_competition is True
    macro = build_full_tree(_season(weeks=16), model).value
    assert macro.total_weeks == 16


def test_load_curve_one_point_per_week():
    model = get_model("traditional").value
    macro = build_full_tree(_season(weeks=20), model).value
    curve = compute_load_curve(macro)
    weeks = [p.unit_index for p in curve.points]
    assert weeks == sorted(weeks)
    assert len(curve.points) == 20


def test_unknown_model_is_error():
    assert isinstance(get_model("does_not_exist"), Err)


def test_serialization_round_trip():
    model = get_model("atr").value
    macro = build_full_tree(_season(weeks=24), model).value
    d = macrocycle_to_dict(macro)
    back = macrocycle_from_dict(d)
    assert back == macro


def test_register_custom_model_and_reject_invalid():
    _reset_custom_models()
    bad = PeriodizationModel(
        id="mine_bad",
        name=I18nText(es="Mío", en="Mine"),
        source=ModelSource.CUSTOM,
        rules=ModelRules(period_plan=(), micro_wave=(), meso_length_weeks=99),
    )
    assert isinstance(register_custom_model(bad), Err)


def test_pretemporada_no_matches():
    model = get_model("traditional").value
    macro = build_full_tree(_season(weeks=8, days=5, matches=0), model).value
    # Con 0 partidos todos los slots son de fase estimuladora.
    slot_phases = {
        s.micro_phase.value
        for meso in macro.mesocycles
        for micro in meso.microcycles
        for s in micro.session_slots
    }
    assert slot_phases == {"stimulating"}
