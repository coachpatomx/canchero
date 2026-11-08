"""Entidades de seguimiento individual (U6). Metodología FMF Manual 1:
Potenciar / Mejorar / Eliminar. Inmutables."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from periodization_engine import I18nText

MASTERY_THRESHOLD = 90  # > 90% = dominado (criterio FMF)


class ObjectiveCategory(str, Enum):
    POTENTIATE = "potentiate"   # Potenciar
    IMPROVE = "improve"         # Mejorar
    ELIMINATE = "eliminate"     # Eliminar


class Fundamental(str, Enum):
    FID = "fid"
    FGL = "fgl"
    FCU = "fcu"
    FCL = "fcl"


# Prioridad para seleccionar objetivos en la sesión (eliminate primero).
CATEGORY_PRIORITY = {
    ObjectiveCategory.ELIMINATE: 0,
    ObjectiveCategory.IMPROVE: 1,
    ObjectiveCategory.POTENTIATE: 2,
}


@dataclass(frozen=True)
class IndividualObjective:
    id: str
    category: ObjectiveCategory
    content: I18nText
    fundamental: Fundamental | None = None
    progress_pct: int = 0

    @property
    def mastered(self) -> bool:
        return self.progress_pct > MASTERY_THRESHOLD


@dataclass(frozen=True)
class Observation:
    id: str
    session_ref: str
    note: I18nText
    created_at: str


@dataclass(frozen=True)
class Player:
    id: str
    name: str
    position_key: str
    objectives: tuple[IndividualObjective, ...] = ()
    observations: tuple[Observation, ...] = ()


@dataclass(frozen=True)
class Roster:
    team_name: str
    players: tuple[Player, ...] = ()


@dataclass(frozen=True)
class PlayerSpec:
    name: str
    position_key: str


@dataclass(frozen=True)
class PlayerDossier:
    player: Player
    potentiate: tuple[IndividualObjective, ...]
    improve: tuple[IndividualObjective, ...]
    eliminate: tuple[IndividualObjective, ...]
    mastered_count: int
