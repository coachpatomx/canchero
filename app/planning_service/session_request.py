"""Tipos de entrada/contexto del orquestador."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from periodization_engine import Macrocycle, SeasonParams


class Alignment(str, Enum):
    FULL = "full"       # alineada a un microciclo/fase del macro vigente
    PARTIAL = "partial"  # macro construido ad-hoc por entrevista
    NONE = "none"       # sesión suelta, usuario rechazó datos de temporada


@dataclass(frozen=True)
class PlanInput:
    season: SeasonParams
    model_id: str
    format_id: str
    title_es: str = "Plan de temporada"
    title_en: str = "Season plan"
    lang: str = "es"


@dataclass(frozen=True)
class SessionRequest:
    """Petición de una sesión concreta (RF-11)."""

    text: str                 # petición en lenguaje natural
    format_id: str
    week_index: int | None = None  # semana objetivo si se conoce
    lang: str = "es"


@dataclass(frozen=True)
class PlanContext:
    """Contexto para generar/alinear una sesión."""

    macro: Macrocycle | None
    format_id: str
    lang: str = "es"
