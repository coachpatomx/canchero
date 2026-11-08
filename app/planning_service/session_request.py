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
    """Petición de una sesión concreta (RF-11).

    Combina texto libre con variables estructuradas (desplegables en la UI) que
    enriquecen el prompt del LLM y la plantilla determinista.
    """

    text: str                       # petición en lenguaje natural
    format_id: str
    week_index: int | None = None   # semana objetivo si se conoce
    lang: str = "es"
    # Variables estructuradas (todas opcionales; afinan el prompt)
    duration_min: int = 90          # duración total de la sesión
    category: str = ""              # Sub-23/19/17/15/13 o libre
    n_players: int = 0              # nº de jugadores (0 = según formato)
    schedule: str = ""              # matutino/vespertino u hora
    phase: str = ""                 # fase de sesión o del micro si se fuerza
    technical_focus: str = ""       # fundamento técnico
    tactical_focus: str = ""        # fundamento táctico
    physical_focus: str = ""        # capacidad física
    materials: str = ""             # material disponible (texto libre)


@dataclass(frozen=True)
class PlanContext:
    """Contexto para generar/alinear una sesión."""

    macro: Macrocycle | None
    format_id: str
    lang: str = "es"
