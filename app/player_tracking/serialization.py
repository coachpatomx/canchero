"""Serialización del Roster a/desde dict JSON-nativo (RNF-6)."""
from __future__ import annotations

from dataclasses import asdict

from periodization_engine import I18nText

from .models import (
    Fundamental,
    IndividualObjective,
    Observation,
    ObjectiveCategory,
    Player,
    Roster,
)


def _enums_to_values(obj):
    if isinstance(obj, dict):
        return {k: _enums_to_values(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_enums_to_values(v) for v in obj]
    if obj is None:
        return None
    if hasattr(obj, "value") and not isinstance(obj, (str, int, float, bool)):
        return obj.value
    return obj


def roster_to_dict(roster: Roster) -> dict:
    return _enums_to_values(asdict(roster))


def _i18n(d: dict) -> I18nText:
    return I18nText(es=d["es"], en=d["en"])


def _obj_from_dict(d: dict) -> IndividualObjective:
    return IndividualObjective(
        id=d["id"],
        category=ObjectiveCategory(d["category"]),
        content=_i18n(d["content"]),
        fundamental=Fundamental(d["fundamental"]) if d["fundamental"] else None,
        progress_pct=d["progress_pct"],
    )


def _obs_from_dict(d: dict) -> Observation:
    return Observation(id=d["id"], session_ref=d["session_ref"],
                       note=_i18n(d["note"]), created_at=d["created_at"])


def _player_from_dict(d: dict) -> Player:
    return Player(
        id=d["id"], name=d["name"], position_key=d["position_key"],
        objectives=tuple(_obj_from_dict(o) for o in d["objectives"]),
        observations=tuple(_obs_from_dict(o) for o in d["observations"]),
    )


def roster_from_dict(d: dict) -> Roster:
    return Roster(
        team_name=d["team_name"],
        players=tuple(_player_from_dict(p) for p in d["players"]),
    )
