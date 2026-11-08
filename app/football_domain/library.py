"""Biblioteca de ejercicios en memoria (RF-9). U4 se encarga de persistir.

U2 mantiene el catálogo en memoria; la persistencia a disco (JSON) es
responsabilidad de U4. Aquí solo creación, filtrado y acceso.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from periodization_engine.errors import (
    DomainError,
    DomainErrorKind,
    Err,
    Ok,
    Result,
)

from .exercise import Exercise, ExerciseSpec, DiagramSpec


_LIBRARY: dict[str, Exercise] = {}
_counter = {"n": 0}


def _next_id() -> str:
    _counter["n"] += 1
    return f"ex-{_counter['n']:05d}"


def create_exercise(spec: ExerciseSpec) -> Result[Exercise]:
    if spec.duration_min <= 0:
        return Err(DomainError(DomainErrorKind.INVALID_MODEL_RULES,
                               detail="duration_min <= 0"))
    diagram = spec.diagram_spec or DiagramSpec(
        players_a=spec.n_players.team_a,
        players_b=spec.n_players.team_b,
    )
    ex = Exercise(
        id=_next_id(),
        name=spec.name,
        task_type=spec.task_type,
        didactic_strategy=spec.didactic_strategy,
        objective=spec.objective,
        duration_min=spec.duration_min,
        space=spec.space,
        n_players=spec.n_players,
        load=spec.load,
        aspects=spec.aspects,
        diagram_spec=diagram,
    )
    _LIBRARY[ex.id] = ex
    return Ok(ex)


@dataclass(frozen=True)
class ExerciseFilter:
    task_type: str | None = None
    strategy: str | None = None
    max_duration_min: int | None = None


def get_library(filter: ExerciseFilter | None = None) -> list[Exercise]:
    items = list(_LIBRARY.values())
    if filter is None:
        return items
    if filter.task_type:
        items = [e for e in items if e.task_type.value == filter.task_type]
    if filter.strategy:
        items = [e for e in items if e.didactic_strategy.value == filter.strategy]
    if filter.max_duration_min is not None:
        items = [e for e in items if e.duration_min <= filter.max_duration_min]
    return items


def _reset_library() -> None:
    _LIBRARY.clear()
    _counter["n"] = 0
