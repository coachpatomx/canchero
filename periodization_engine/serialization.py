"""Serialización a/desde dict JSON-nativo (RNF-6).

U1 no persiste (eso es U4), pero sus entidades deben convertirse a dicts planos
para que U4 las guarde en JSON. ``from_dict(to_dict(x)) == x`` (round-trip,
verificado con PBT).
"""
from __future__ import annotations

from dataclasses import asdict

from .domain import (
    LoadCurve,
    LoadPoint,
    Macrocycle,
    Mesocycle,
    MesocycleType,
    Microcycle,
    MicrocycleType,
    MicroPhase,
    Period,
    PeriodKind,
    PeriodStage,
    Provenance,
    SessionSlot,
    SessionTypeHint,
)


def macrocycle_to_dict(macro: Macrocycle) -> dict:
    """Convierte un Macrocycle (con toda su jerarquía) a dict JSON-nativo.

    ``asdict`` recorre recursivamente los dataclasses; los enums (subclase de str)
    se serializan a su valor string de forma natural vía ``.value`` al volcar.
    """
    return _enums_to_values(asdict(macro))


def _enums_to_values(obj):
    if isinstance(obj, dict):
        return {k: _enums_to_values(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_enums_to_values(v) for v in obj]
    # Enums StrEnum: asdict ya devuelve el valor str en la mayoría de casos, pero
    # por robustez normalizamos cualquier Enum restante.
    if hasattr(obj, "value") and not isinstance(obj, (str, int, float, bool)):
        return obj.value
    return obj


def macrocycle_from_dict(data: dict) -> Macrocycle:
    """Reconstruye un Macrocycle desde su dict."""
    return Macrocycle(
        id=data["id"],
        model_id=data["model_id"],
        total_weeks=data["total_weeks"],
        periods=tuple(_period_from_dict(p) for p in data["periods"]),
        provenance=Provenance(**data["provenance"]),
        mesocycles=tuple(_meso_from_dict(m) for m in data["mesocycles"]),
    )


def _period_from_dict(d: dict) -> Period:
    return Period(
        kind=PeriodKind(d["kind"]),
        stage=PeriodStage(d["stage"]),
        start_week=d["start_week"],
        end_week=d["end_week"],
    )


def _meso_from_dict(d: dict) -> Mesocycle:
    return Mesocycle(
        type=MesocycleType(d["type"]),
        period_index=d["period_index"],
        start_week=d["start_week"],
        end_week=d["end_week"],
        objective_focus=tuple(d["objective_focus"]),
        microcycles=tuple(_micro_from_dict(m) for m in d["microcycles"]),
    )


def _micro_from_dict(d: dict) -> Microcycle:
    return Microcycle(
        type=MicrocycleType(d["type"]),
        week_index=d["week_index"],
        matches_this_week=d["matches_this_week"],
        target_volume_pct=d["target_volume_pct"],
        target_intensity_pct=d["target_intensity_pct"],
        phases=tuple(MicroPhase(p) for p in d["phases"]),
        session_slots=tuple(_slot_from_dict(s) for s in d["session_slots"]),
    )


def _slot_from_dict(d: dict) -> SessionSlot:
    return SessionSlot(
        day_index=d["day_index"],
        micro_phase=MicroPhase(d["micro_phase"]),
        relative_to_match=d["relative_to_match"],
        target_load=LoadPoint(**d["target_load"]),
        session_type=SessionTypeHint(d["session_type"]),
    )


def load_curve_to_dict(curve: LoadCurve) -> dict:
    return _enums_to_values(asdict(curve))
