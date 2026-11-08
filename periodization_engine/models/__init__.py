"""Registro de modelos de periodización (6 precargados + custom).

Fuente: D4 (6 modelos) y knowledge-base C3. Cada modelo es una instancia de
``PeriodizationModel`` cuyas reglas (``ModelRules``) son DATOS, de modo que
``register_custom_model`` solo añade otra instancia (RF-4).
"""
from __future__ import annotations

from ..domain import PeriodizationModel
from ..errors import DomainError, DomainErrorKind, Err, Ok, Result
from .atr import MODEL as ATR
from .blocks import MODEL as BLOCKS
from .football_gonzalez import MODEL as FOOTBALL_GONZALEZ
from .structured import MODEL as STRUCTURED
from .tactical import MODEL as TACTICAL
from .traditional import MODEL as TRADITIONAL

_BUILTIN: dict[str, PeriodizationModel] = {
    m.id: m
    for m in (TRADITIONAL, BLOCKS, ATR, TACTICAL, STRUCTURED, FOOTBALL_GONZALEZ)
}

# Registro de modelos personalizados en memoria (el llamador persiste vía U4).
_CUSTOM: dict[str, PeriodizationModel] = {}


def list_models() -> list[PeriodizationModel]:
    """Modelos precargados + custom registrados, en orden estable."""
    return list(_BUILTIN.values()) + list(_CUSTOM.values())


def get_model(model_id: str) -> Result[PeriodizationModel]:
    model = _BUILTIN.get(model_id) or _CUSTOM.get(model_id)
    if model is None:
        return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL, detail=model_id))
    return Ok(model)


def register_custom_model(model: PeriodizationModel) -> Result[PeriodizationModel]:
    """Valida y registra un modelo personalizado (RF-4)."""
    problems = model.rules.validate()
    if problems:
        return Err(
            DomainError(DomainErrorKind.INVALID_MODEL_RULES, detail="; ".join(problems))
        )
    if model.id in _BUILTIN:
        return Err(
            DomainError(
                DomainErrorKind.INVALID_MODEL_RULES,
                detail=f"id '{model.id}' choca con un modelo precargado",
            )
        )
    _CUSTOM[model.id] = model
    return Ok(model)


def _reset_custom_models() -> None:
    """Solo para tests: limpia el registro custom."""
    _CUSTOM.clear()
