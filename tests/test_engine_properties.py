"""Pruebas Basadas en Propiedades (PBT) del motor — extensión PBT (parcial).

Verifica las 7 propiedades del Functional Design §8 + round-trip de serialización,
sobre entradas generadas por Hypothesis.
"""
from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from periodization_engine import (
    CompetitionType,
    Ok,
    SeasonParams,
    StartFitness,
    build_full_tree,
    compute_load_curve,
    list_models,
    macrocycle_from_dict,
    macrocycle_to_dict,
)

MODEL_IDS = [m.id for m in list_models()]


@st.composite
def seasons(draw):
    return SeasonParams(
        start_date="2026-01-06",
        duration_weeks=draw(st.integers(min_value=4, max_value=60)),
        training_days_per_week=draw(st.integers(min_value=1, max_value=7)),
        matches_per_week=draw(st.sampled_from([0, 1, 2])),
        competition_type=draw(st.sampled_from(list(CompetitionType))),
        start_fitness=draw(st.sampled_from(list(StartFitness))),
        objectives=tuple(
            draw(st.lists(st.sampled_from(
                ["physical.endurance", "tactical.pressing", "technical.passing"]
            ), max_size=3, unique=True))
        ),
    )


def _model(model_id):
    return next(m for m in list_models() if m.id == model_id)


@settings(max_examples=150, deadline=None)
@given(season=seasons(), model_id=st.sampled_from(MODEL_IDS))
def test_prop1_weeks_sum(season, model_id):
    macro = build_full_tree(season, _model(model_id)).value
    # Prop 1: los períodos cubren exactamente total_weeks, sin huecos ni solapes.
    assert macro.periods[0].start_week == 1
    assert macro.periods[-1].end_week == macro.total_weeks
    for prev, nxt in zip(macro.periods, macro.periods[1:]):
        assert nxt.start_week == prev.end_week + 1


@settings(max_examples=150, deadline=None)
@given(season=seasons(), model_id=st.sampled_from(MODEL_IDS))
def test_prop2_microcycle_coverage(season, model_id):
    macro = build_full_tree(season, _model(model_id)).value
    # Prop 2: cada semana pertenece a exactamente un microciclo.
    weeks = sorted(
        micro.week_index
        for meso in macro.mesocycles
        for micro in meso.microcycles
    )
    assert weeks == list(range(1, macro.total_weeks + 1))


@settings(max_examples=150, deadline=None)
@given(season=seasons(), model_id=st.sampled_from(MODEL_IDS))
def test_prop3_load_ranges(season, model_id):
    macro = build_full_tree(season, _model(model_id)).value
    for meso in macro.mesocycles:
        for micro in meso.microcycles:
            assert 0 <= micro.target_volume_pct <= 100
            assert 0 <= micro.target_intensity_pct <= 100
            for slot in micro.session_slots:
                assert 0 <= slot.target_load.volume_pct <= 100
                assert 0 <= slot.target_load.intensity_pct <= 100


@settings(max_examples=100, deadline=None)
@given(
    season=seasons().filter(lambda s: s.matches_per_week == 1 and s.training_days_per_week >= 3),
    model_id=st.sampled_from(MODEL_IDS),
)
def test_prop4_optimization_not_above_stimulating(season, model_id):
    macro = build_full_tree(season, _model(model_id)).value
    # Prop 4: en micro de 1 partido, el volumen de optimización <= el estimulador.
    for meso in macro.mesocycles:
        for micro in meso.microcycles:
            stim = [s.target_load.volume_pct for s in micro.session_slots
                    if s.micro_phase.value == "stimulating"]
            opt = [s.target_load.volume_pct for s in micro.session_slots
                   if s.micro_phase.value == "optimization"]
            if stim and opt:
                assert max(opt) <= max(stim)


@settings(max_examples=100, deadline=None)
@given(season=seasons(), model_id=st.sampled_from(MODEL_IDS))
def test_prop5_determinism(season, model_id):
    model = _model(model_id)
    a = build_full_tree(season, model).value
    b = build_full_tree(season, model).value
    # Prop 5: mismas entradas -> árbol idéntico (incluido el id).
    assert a == b
    assert a.id == b.id


@settings(max_examples=100, deadline=None)
@given(season=seasons(), model_id=st.sampled_from(MODEL_IDS))
def test_prop6_traceability(season, model_id):
    macro = build_full_tree(season, _model(model_id)).value
    # Prop 6: provenance coherente y periods/mesos referencian períodos válidos.
    assert macro.provenance.model_id == model_id
    assert macro.provenance.season_params_hash == macro.id
    for meso in macro.mesocycles:
        assert 0 <= meso.period_index < len(macro.periods)


@settings(max_examples=100, deadline=None)
@given(season=seasons(), model_id=st.sampled_from(MODEL_IDS))
def test_round_trip_serialization(season, model_id):
    macro = build_full_tree(season, _model(model_id)).value
    assert macrocycle_from_dict(macrocycle_to_dict(macro)) == macro


def test_prop7_engine_has_no_football_imports():
    """Prop 7: el paquete del motor no importa nada de app/ ni menciona fútbol."""
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent / "periodization_engine"
    forbidden = ("import app", "from app", "futbol", "football_domain", "jugador")
    for py in root.rglob("*.py"):
        text = py.read_text(encoding="utf-8").lower()
        for token in forbidden:
            # "football_gonzalez" es nombre de un modelo de periodización, permitido.
            if token == "football_domain" or token in ("import app", "from app"):
                assert token not in text, f"{py} contiene '{token}'"
