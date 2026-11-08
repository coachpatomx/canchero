"""U6 — Seguimiento Individual por Deportista.

Roster por demarcación, objetivos individuales (Potenciar/Mejorar/Eliminar,
Manual 1 FMF), observaciones y dossier. Alimenta el bloque de objetivos
individuales de la sesión (plantilla mejorada). Depende de U2 (posiciones).
"""
from __future__ import annotations

from .models import (  # noqa: F401
    Fundamental,
    IndividualObjective,
    Observation,
    ObjectiveCategory,
    Player,
    PlayerDossier,
    PlayerSpec,
    Roster,
)
from .serialization import roster_from_dict, roster_to_dict  # noqa: F401
from .tracking import (  # noqa: F401
    add_observation,
    add_player,
    create_roster,
    get_player_dossier,
    get_session_individual_goals,
    set_individual_objectives,
    update_progress,
)

__all__ = [
    "Roster", "Player", "PlayerSpec", "IndividualObjective", "Observation",
    "ObjectiveCategory", "Fundamental", "PlayerDossier",
    "create_roster", "add_player", "set_individual_objectives",
    "update_progress", "add_observation", "get_player_dossier",
    "get_session_individual_goals",
    "roster_to_dict", "roster_from_dict",
]
