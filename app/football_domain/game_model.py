"""Vocabulario de modelo de juego y enums de dominio del fútbol (C1/C2/C4/C6).

Todo texto de cara al usuario es bilingüe (I18nText de U1, D6). Los enums usan
clave estable en inglés; las etiquetas es/en viven en tablas LABELS.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from periodization_engine import I18nText


# --------------------------------------------------------------------------- #
# Enums de dominio (C4 tipos de tarea, C6 estrategias y espacios)
# --------------------------------------------------------------------------- #
class TaskType(str, Enum):
    GENERAL = "general"
    DIRECTED = "directed"
    SPECIAL = "special"
    COMPETITIVE = "competitive"


class DidacticStrategy(str, Enum):
    PERCEPTION_GAMES = "perception_games"
    POSITION_GAMES = "position_games"
    CHUNKS = "chunks"
    LINE_GAMES = "line_games"
    SSP = "ssp"  # situaciones simuladoras preferenciales
    CIRCUITS = "circuits"


class SpaceCategory(str, Enum):
    REDUCED = "reduced"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    REAL = "real"


class Fundamental(str, Enum):
    FID = "fid"  # individual por demarcación
    FGL = "fgl"  # grupal de línea
    FCU = "fcu"  # colectivo universal
    FCL = "fcl"  # colectivo de línea


class GamePhase(str, Enum):
    OFFENSE_ORGANIZED = "offense_organized"
    TRANSITION_DEF_TO_ATT = "transition_def_to_att"
    DEFENSE_ORGANIZED = "defense_organized"
    TRANSITION_ATT_TO_DEF = "transition_att_to_def"


# Etiquetas bilingües (D6). La UI (U5) resuelve el idioma.
STRATEGY_LABELS: dict[DidacticStrategy, I18nText] = {
    DidacticStrategy.PERCEPTION_GAMES: I18nText("Juegos de percepción", "Perception games"),
    DidacticStrategy.POSITION_GAMES: I18nText("Juegos de posición", "Position games"),
    DidacticStrategy.CHUNKS: I18nText("Chunks", "Chunks"),
    DidacticStrategy.LINE_GAMES: I18nText("Juegos de línea", "Line games"),
    DidacticStrategy.SSP: I18nText("Situaciones simuladoras preferenciales",
                                   "Preferential simulation situations"),
    DidacticStrategy.CIRCUITS: I18nText("Circuitos / estaciones", "Circuits / stations"),
}

TASK_TYPE_LABELS: dict[TaskType, I18nText] = {
    TaskType.GENERAL: I18nText("General", "General"),
    TaskType.DIRECTED: I18nText("Dirigido", "Directed"),
    TaskType.SPECIAL: I18nText("Especial", "Special"),
    TaskType.COMPETITIVE: I18nText("Competitivo", "Competitive"),
}


@dataclass(frozen=True)
class GameModelRef:
    """Referencia a un elemento del modelo de juego que trabaja una tarea."""

    phase: GamePhase
    moment: str  # clave de momento (C1), p. ej. "progression", "finishing"
    fundamental: Fundamental


@dataclass(frozen=True)
class GameModelVocabulary:
    """Catálogo bilingüe de dinámicas/fases/momentos/fundamentos (C1/C2)."""

    dynamics: tuple[I18nText, ...]
    phases: tuple[I18nText, ...]
    moments: tuple[I18nText, ...]
    fundamentals: tuple[I18nText, ...]


def get_game_model_vocabulary() -> GameModelVocabulary:
    return GameModelVocabulary(
        dynamics=(I18nText("Con balón", "With ball"), I18nText("Sin balón", "Without ball")),
        phases=(
            I18nText("Ataque organizado", "Organized attack"),
            I18nText("Transición defensa-ataque", "Defense-to-attack transition"),
            I18nText("Defensa organizada", "Organized defense"),
            I18nText("Transición ataque-defensa", "Attack-to-defense transition"),
        ),
        moments=(
            I18nText("Inicio estático", "Static build-up"),
            I18nText("Inicio dinámico", "Dynamic build-up"),
            I18nText("Progresión", "Progression"),
            I18nText("Ataque en tres cuartos", "Attack in the final third"),
            I18nText("Finalización", "Finishing"),
        ),
        fundamentals=(
            I18nText("FID — individual por demarcación", "FID — individual by position"),
            I18nText("FGL — grupal de línea", "FGL — line group"),
            I18nText("FCU — colectivo universal", "FCU — universal collective"),
            I18nText("FCL — colectivo de línea", "FCL — line collective"),
        ),
    )
