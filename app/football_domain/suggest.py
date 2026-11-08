"""suggest_tasks_for_phase: convierte un SessionSlot de U1 en sugerencias de
tareas de fútbol coherentes con la fase (tabla fase×estrategia de C5/C6).

Determinista. La carga de la tarea HEREDA del target_load del slot (RNF-5):
U2 no recalcula cargas, las respeta.
"""
from __future__ import annotations

from periodization_engine import I18nText, MicroPhase, SessionSlot

from .adapted.apply import apply_adaptations
from .exercise import (
    AspectTags,
    DiagramSpec,
    Exercise,
    LoadSpec,
    PlayerSetup,
    SpaceSpec,
)
from .game_model import DidacticStrategy, SpaceCategory, TaskType

# Tabla determinista fase del microciclo -> (tipo de tarea, estrategia, espacio).
# Fuente: tabla fase×bloque×estrategia de C6 + especificidad C4.
_PHASE_TABLE: dict[MicroPhase, tuple[TaskType, DidacticStrategy, SpaceCategory]] = {
    MicroPhase.RECOVERY: (TaskType.GENERAL, DidacticStrategy.CIRCUITS, SpaceCategory.REDUCED),
    MicroPhase.STIMULATING: (TaskType.SPECIAL, DidacticStrategy.POSITION_GAMES, SpaceCategory.MEDIUM),
    MicroPhase.OPTIMIZATION: (TaskType.DIRECTED, DidacticStrategy.CHUNKS, SpaceCategory.SMALL),
    MicroPhase.COMPETITIVE: (TaskType.COMPETITIVE, DidacticStrategy.SSP, SpaceCategory.REAL),
}

_SPACE_DIMS: dict[SpaceCategory, tuple[float, float]] = {
    SpaceCategory.REDUCED: (10, 10),
    SpaceCategory.SMALL: (20, 15),
    SpaceCategory.MEDIUM: (30, 25),
    SpaceCategory.LARGE: (45, 35),
    SpaceCategory.REAL: (0, 0),  # se completa con dimensiones del formato
}


def suggest_tasks_for_phase(slot: SessionSlot, fmt) -> list[Exercise]:
    """Devuelve una o más tareas base coherentes con la fase del slot y el formato.

    En v1 devuelve una tarea base reglada por fase; U5/LLM puede enriquecer o
    generar variantes. El tamaño de equipos se escala al formato.
    """
    task_type, strategy, space_cat = _PHASE_TABLE.get(
        slot.micro_phase,
        (TaskType.SPECIAL, DidacticStrategy.POSITION_GAMES, SpaceCategory.MEDIUM),
    )

    if space_cat == SpaceCategory.REAL:
        dims = (fmt.field_length_m, fmt.field_width_m)
    else:
        dims = _SPACE_DIMS[space_cat]

    # Equipos a partir de jugadores del formato (situación preferencial simple).
    per_side = max(1, fmt.players_on_field - 1)
    setup = PlayerSetup(team_a=per_side, team_b=per_side)

    base = Exercise(
        id=f"auto-{fmt.id}-{slot.micro_phase.value}-d{slot.day_index}",
        name=I18nText(
            f"Tarea {task_type.value} ({slot.micro_phase.value})",
            f"{task_type.value} task ({slot.micro_phase.value})",
        ),
        task_type=task_type,
        didactic_strategy=strategy,
        objective=I18nText(
            "Trabajar el contenido de la fase manteniendo la carga objetivo.",
            "Work the phase content while keeping the target load.",
        ),
        duration_min=20,
        space=SpaceSpec(length_m=dims[0], width_m=dims[1], category=space_cat),
        n_players=setup,
        # HERENCIA DE CARGA: respeta el target_load del slot (U1).
        load=LoadSpec(
            volume_pct=slot.target_load.volume_pct,
            intensity_pct=slot.target_load.intensity_pct,
        ),
        aspects=AspectTags(),
        diagram_spec=DiagramSpec(players_a=per_side, players_b=per_side, balls=1),
    )

    # Inyecta adaptaciones si el formato es adaptado (no-op si convencional).
    base = apply_adaptations(base, fmt)
    return [base]
