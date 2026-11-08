"""Formatos de fútbol como datos (RF-7). 7 formatos precargados + registry.

Añadir un formato nuevo es añadir datos, no tocar lógica.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from periodization_engine import I18nText
from periodization_engine.errors import (
    DomainError,
    DomainErrorKind,
    Err,
    Ok,
    Result,
)

from .adapted.profiles import PROFILES, AdaptationProfile, RuleNote


@dataclass(frozen=True)
class Position:
    key: str
    name: I18nText


@dataclass(frozen=True)
class FootballFormat:
    id: str
    name: I18nText
    players_on_field: int
    field_length_m: float
    field_width_m: float
    match_duration_min: int
    is_adapted: bool = False
    adaptation_profile: AdaptationProfile | None = None
    rules_notes: tuple[RuleNote, ...] = ()
    positions: tuple[Position, ...] = ()

    def validate(self) -> list[str]:
        problems: list[str] = []
        if self.players_on_field < 1:
            problems.append("players_on_field < 1")
        if self.field_length_m <= 0 or self.field_width_m <= 0:
            problems.append("dimensiones no positivas")
        if self.is_adapted and self.adaptation_profile is None:
            problems.append("formato adaptado sin adaptation_profile")
        return problems


def _pos(key: str, es: str, en: str) -> Position:
    return Position(key, I18nText(es, en))


_DEFENSE_POSITIONS = (
    _pos("gk", "Portero/a", "Goalkeeper"),
    _pos("cb", "Central", "Center-back"),
    _pos("fb", "Lateral", "Full-back"),
    _pos("dm", "Medio centro", "Defensive mid"),
    _pos("wm", "Interior/Extremo", "Interior/Winger"),
    _pos("fw", "Delantero/a", "Forward"),
)


_BUILTIN: dict[str, FootballFormat] = {
    "football_11": FootballFormat(
        id="football_11", name=I18nText("Fútbol 11", "11-a-side football"),
        players_on_field=11, field_length_m=105, field_width_m=68,
        match_duration_min=90, positions=_DEFENSE_POSITIONS,
    ),
    "football_7": FootballFormat(
        id="football_7", name=I18nText("Fútbol 7", "7-a-side football"),
        players_on_field=7, field_length_m=60, field_width_m=40,
        match_duration_min=60, positions=_DEFENSE_POSITIONS[:5],
    ),
    "futsal": FootballFormat(
        id="futsal", name=I18nText("Fútbol sala", "Futsal"),
        players_on_field=5, field_length_m=40, field_width_m=20,
        match_duration_min=40, positions=_DEFENSE_POSITIONS[:5],
    ),
    "blind_5": FootballFormat(
        id="blind_5", name=I18nText("Fútbol 5 para ciegos", "Blind football (5-a-side)"),
        players_on_field=5, field_length_m=40, field_width_m=20,
        match_duration_min=40, is_adapted=True, adaptation_profile=PROFILES["blind_5"],
        rules_notes=PROFILES["blind_5"].rule_adaptations, positions=_DEFENSE_POSITIONS[:5],
    ),
    "cp_7": FootballFormat(
        id="cp_7", name=I18nText("Fútbol 7 PC", "CP football (7-a-side)"),
        players_on_field=7, field_length_m=70, field_width_m=50,
        match_duration_min=60, is_adapted=True, adaptation_profile=PROFILES["cp_7"],
        rules_notes=PROFILES["cp_7"].rule_adaptations, positions=_DEFENSE_POSITIONS[:5],
    ),
    "down": FootballFormat(
        id="down", name=I18nText("Fútbol para personas con síndrome de Down",
                                 "Football for people with Down syndrome"),
        players_on_field=7, field_length_m=60, field_width_m=40,
        match_duration_min=50, is_adapted=True, adaptation_profile=PROFILES["down"],
        rules_notes=PROFILES["down"].rule_adaptations, positions=_DEFENSE_POSITIONS[:5],
    ),
    "amputee": FootballFormat(
        id="amputee", name=I18nText("Fútbol para amputados", "Amputee football"),
        players_on_field=7, field_length_m=70, field_width_m=60,  # 6 de campo + portero (WAFF)
        match_duration_min=50, is_adapted=True, adaptation_profile=PROFILES["amputee"],
        rules_notes=PROFILES["amputee"].rule_adaptations, positions=_DEFENSE_POSITIONS[:5],
    ),
}

_CUSTOM: dict[str, FootballFormat] = {}


def list_formats() -> list[FootballFormat]:
    return list(_BUILTIN.values()) + list(_CUSTOM.values())


def get_format(format_id: str) -> Result[FootballFormat]:
    fmt = _BUILTIN.get(format_id) or _CUSTOM.get(format_id)
    if fmt is None:
        return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL, detail=f"format {format_id}"))
    return Ok(fmt)


def register_format(fmt: FootballFormat) -> Result[FootballFormat]:
    problems = fmt.validate()
    if problems:
        return Err(DomainError(DomainErrorKind.INVALID_MODEL_RULES, detail="; ".join(problems)))
    if fmt.id in _BUILTIN:
        return Err(DomainError(DomainErrorKind.INVALID_MODEL_RULES,
                               detail=f"id '{fmt.id}' choca con un formato precargado"))
    _CUSTOM[fmt.id] = fmt
    return Ok(fmt)


def unvalidated_rules(fmt: FootballFormat) -> list[RuleNote]:
    """Reglas aún no validadas por el usuario (para que U5 muestre aviso)."""
    return [r for r in fmt.rules_notes if not r.validated]


def _reset_custom_formats() -> None:
    _CUSTOM.clear()
