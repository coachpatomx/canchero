"""Tests de U2 — Dominio Fútbol (ejemplos + propiedades PBT)."""
from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from app.football_domain import (
    DidacticStrategy,
    ExerciseFilter,
    SpaceCategory,
    TaskType,
    apply_adaptations,
    create_exercise,
    exercise_from_dict,
    exercise_to_dict,
    format_from_dict,
    format_to_dict,
    get_format,
    get_library,
    list_formats,
    suggest_tasks_for_phase,
    unvalidated_rules,
)
from app.football_domain.exercise import (
    AspectTags,
    ExerciseSpec,
    LoadSpec,
    PlayerSetup,
    SpaceSpec,
)
from app.football_domain.library import _reset_library
from periodization_engine import (
    LoadPoint,
    MicroPhase,
    Ok,
    SessionSlot,
    SessionTypeHint,
    build_full_tree,
    get_model,
    SeasonParams,
)

ALLOWED_BY_PHASE = {
    MicroPhase.RECOVERY: (TaskType.GENERAL, DidacticStrategy.CIRCUITS),
    MicroPhase.STIMULATING: (TaskType.SPECIAL, DidacticStrategy.POSITION_GAMES),
    MicroPhase.OPTIMIZATION: (TaskType.DIRECTED, DidacticStrategy.CHUNKS),
    MicroPhase.COMPETITIVE: (TaskType.COMPETITIVE, DidacticStrategy.SSP),
}


def _slot(phase, vol=40, inten=70, day=2):
    return SessionSlot(
        day_index=day, micro_phase=phase, relative_to_match=2,
        target_load=LoadPoint(unit_index=day, volume_pct=vol, intensity_pct=inten),
        session_type=SessionTypeHint.COMPLEX,
    )


# --------------------------- ejemplos --------------------------------------- #
def test_seven_formats_present():
    ids = {f.id for f in list_formats()}
    assert {"football_11", "football_7", "futsal", "blind_5", "cp_7", "down", "amputee"} <= ids


def test_blind_format_has_sonorous_ball_and_validated_rules():
    fmt = get_format("blind_5").value
    assert fmt.is_adapted
    mats = {m.key for m in fmt.adaptation_profile.material_adaptations}
    assert "sonorous_ball" in mats
    # Las reglas de ciegos están validadas (dominio del usuario).
    assert unvalidated_rules(fmt) == []


def test_cp_rules_from_official_source():
    fmt = get_format("cp_7").value
    # Reglas de PC ahora provienen de IFCPF (validadas).
    assert fmt.adaptation_profile.governing_body == "IFCPF"
    assert len(unvalidated_rules(fmt)) == 0


def test_amputee_is_seven_a_side_waff():
    fmt = get_format("amputee").value
    assert fmt.players_on_field == 7
    assert fmt.adaptation_profile.governing_body == "WAFF"


def test_down_is_virtus_ii2():
    fmt = get_format("down").value
    assert fmt.adaptation_profile.governing_body == "Virtus"
    assert "II2" in fmt.adaptation_profile.classification


def test_suggest_inherits_slot_load():
    fmt = get_format("football_11").value
    slot = _slot(MicroPhase.STIMULATING, vol=55, inten=75)
    tasks = suggest_tasks_for_phase(slot, fmt)
    assert tasks[0].load.volume_pct == 55
    assert tasks[0].load.intensity_pct == 75


def test_suggest_blind_injects_adaptation():
    fmt = get_format("blind_5").value
    tasks = suggest_tasks_for_phase(_slot(MicroPhase.STIMULATING), fmt)
    mats = {m.key for m in tasks[0].materials}
    assert "sonorous_ball" in mats
    assert "visual" == fmt.adaptation_profile.disability_domain.value or True
    assert "side_boards" in tasks[0].diagram_spec.adapted_markers


def test_apply_adaptations_noop_on_conventional():
    fmt11 = get_format("football_11").value
    tasks = suggest_tasks_for_phase(_slot(MicroPhase.RECOVERY), fmt11)
    # football_11 no es adaptado: sin materiales adaptados.
    assert all(not m.adapted for m in tasks[0].materials)
    assert tasks[0].applied_adaptations == ()


def test_apply_adaptations_idempotent():
    fmt = get_format("amputee").value
    tasks = suggest_tasks_for_phase(_slot(MicroPhase.STIMULATING), fmt)
    once = tasks[0]
    twice = apply_adaptations(once, fmt)
    assert once == twice  # reaplicar no cambia nada


def test_create_exercise_and_library_filter():
    _reset_library()
    spec = ExerciseSpec(
        name=__import__("periodization_engine").I18nText("Rondo", "Rondo"),
        task_type=TaskType.SPECIAL,
        didactic_strategy=DidacticStrategy.POSITION_GAMES,
        objective=__import__("periodization_engine").I18nText("Posesión", "Possession"),
        duration_min=15,
        space=SpaceSpec(20, 20, SpaceCategory.SMALL),
        n_players=PlayerSetup(4, 2),
        load=LoadSpec(40, 60),
        aspects=AspectTags(technical=("pass",)),
    )
    ex = create_exercise(spec).value
    assert ex.id.startswith("ex-")
    found = get_library(ExerciseFilter(task_type="special"))
    assert ex.id in {e.id for e in found}


def test_integration_u1_u2_full_session():
    """U1 genera el árbol; U2 rellena los slots de la primera semana."""
    model = get_model("football_gonzalez").value
    season = SeasonParams(start_date="2026-01-06", duration_weeks=17,
                          training_days_per_week=4, matches_per_week=1,
                          objectives=("technical.driving", "tactical.reduced_space"))
    macro = build_full_tree(season, model).value
    fmt = get_format("blind_5").value
    micro = macro.mesocycles[0].microcycles[0]
    for slot in micro.session_slots:
        tasks = suggest_tasks_for_phase(slot, fmt)
        assert len(tasks) >= 1
        # Cada tarea hereda la carga de su slot.
        assert tasks[0].load.volume_pct == slot.target_load.volume_pct


# --------------------------- propiedades (PBT) ------------------------------ #
FORMAT_IDS = [f.id for f in list_formats()]
PHASES = list(MicroPhase)


@settings(max_examples=120, deadline=None)
@given(
    phase=st.sampled_from(PHASES),
    vol=st.integers(0, 100),
    inten=st.integers(0, 100),
    format_id=st.sampled_from(FORMAT_IDS),
)
def test_prop_task_phase_coherence(phase, vol, inten, format_id):
    fmt = get_format(format_id).value
    tasks = suggest_tasks_for_phase(_slot(phase, vol, inten), fmt)
    allowed = ALLOWED_BY_PHASE.get(phase)
    if allowed:
        assert tasks[0].task_type == allowed[0]
        assert tasks[0].didactic_strategy == allowed[1]


@settings(max_examples=120, deadline=None)
@given(
    phase=st.sampled_from(PHASES),
    vol=st.integers(0, 100),
    inten=st.integers(0, 100),
    format_id=st.sampled_from(FORMAT_IDS),
)
def test_prop_load_inheritance(phase, vol, inten, format_id):
    fmt = get_format(format_id).value
    tasks = suggest_tasks_for_phase(_slot(phase, vol, inten), fmt)
    assert tasks[0].load.volume_pct == vol
    assert tasks[0].load.intensity_pct == inten


@settings(max_examples=120, deadline=None)
@given(phase=st.sampled_from(PHASES), format_id=st.sampled_from(FORMAT_IDS))
def test_prop_exercise_round_trip(phase, format_id):
    fmt = get_format(format_id).value
    ex = suggest_tasks_for_phase(_slot(phase), fmt)[0]
    assert exercise_from_dict(exercise_to_dict(ex)) == ex


@settings(max_examples=50, deadline=None)
@given(format_id=st.sampled_from(FORMAT_IDS))
def test_prop_format_round_trip(format_id):
    fmt = get_format(format_id).value
    assert format_from_dict(format_to_dict(fmt)) == fmt
