"""Modelo de ejercicio/tarea de fútbol (C4, C6 + plantilla mejorada).

Cubre los campos de la plantilla mejorada que pidió el usuario: materiales,
cargas, volumen, aspectos (téc/tác/fís/psi), dimensiones, y los DATOS para que
U3 dibuje el diagrama (no el SVG en sí).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

from periodization_engine import I18nText

from .game_model import DidacticStrategy, GameModelRef, SpaceCategory, TaskType


@dataclass(frozen=True)
class Material:
    """Material/equipamiento de una tarea (incluye adaptados: balón sonoro...)."""

    key: str                 # clave estable, p. ej. "cone", "sonorous_ball"
    name: I18nText
    quantity: int = 1
    adapted: bool = False    # True si proviene de una adaptación


@dataclass(frozen=True)
class SpaceSpec:
    length_m: float
    width_m: float
    category: SpaceCategory


@dataclass(frozen=True)
class LoadSpec:
    """Carga relativa de la tarea. Hereda del SessionSlot de U1 (RNF-5)."""

    volume_pct: int
    intensity_pct: int


@dataclass(frozen=True)
class PlayerSetup:
    """Situación preferencial: p. ej. 2v1, 8v8+4 comodines."""

    team_a: int
    team_b: int
    jokers: int = 0


@dataclass(frozen=True)
class AspectTags:
    """Los 4 aspectos (estructuras del futbolista, C2/C4). Claves de contenido."""

    technical: tuple[str, ...] = ()
    tactical: tuple[str, ...] = ()
    physical: tuple[str, ...] = ()
    psychological: tuple[str, ...] = ()


@dataclass(frozen=True)
class Constraint:
    """Normativa / gradiente (facilita o dificulta) de la tarea (C6)."""

    description: I18nText
    gradient: str = "neutral"  # "facilitate" | "hinder" | "neutral"


@dataclass(frozen=True)
class DiagramSpec:
    """DATOS para que U3 renderice el SVG. No es el SVG."""

    players_a: int
    players_b: int
    cones: int = 0
    balls: int = 1
    zones: tuple[str, ...] = ()      # claves de zona (de los momentos C1)
    arrows: tuple[str, ...] = ()     # claves de movimiento, p. ej. "pass", "run"
    adapted_markers: tuple[str, ...] = ()  # p. ej. "side_boards", "guide"


@dataclass(frozen=True)
class Exercise:
    id: str
    name: I18nText
    task_type: TaskType
    didactic_strategy: DidacticStrategy
    objective: I18nText
    duration_min: int
    space: SpaceSpec
    n_players: PlayerSetup
    load: LoadSpec
    aspects: AspectTags
    diagram_spec: DiagramSpec
    materials: tuple[Material, ...] = ()
    game_model_refs: tuple[GameModelRef, ...] = ()
    constraints: tuple[Constraint, ...] = ()
    lang_available: tuple[str, ...] = ("es", "en")
    applied_adaptations: tuple[str, ...] = ()  # set de adaptaciones ya aplicadas

    def with_materials(self, extra: tuple[Material, ...]) -> "Exercise":
        return replace(self, materials=self.materials + extra)


@dataclass(frozen=True)
class ExerciseSpec:
    """Entrada para crear un ejercicio (desde formulario, biblioteca o RF-11)."""

    name: I18nText
    task_type: TaskType
    didactic_strategy: DidacticStrategy
    objective: I18nText
    duration_min: int
    space: SpaceSpec
    n_players: PlayerSetup
    load: LoadSpec
    aspects: AspectTags = field(default_factory=AspectTags)
    diagram_spec: DiagramSpec | None = None
