"""U2 — Dominio Fútbol (+ adaptado).

Pone el fútbol sobre el motor abstracto (U1): formatos, ejercicios, biblioteca,
vocabulario de modelo de juego y adaptaciones. Depende de ``periodization_engine``;
nunca al revés (RNF-7).
"""
from __future__ import annotations

from .adapted import apply_adaptations, is_adapted  # noqa: F401
from .exercise import (  # noqa: F401
    AspectTags,
    Constraint,
    DiagramSpec,
    Exercise,
    ExerciseSpec,
    LoadSpec,
    Material,
    PlayerSetup,
    SpaceSpec,
)
from .formats import (  # noqa: F401
    FootballFormat,
    Position,
    get_format,
    list_formats,
    register_format,
    unvalidated_rules,
)
from .game_model import (  # noqa: F401
    DidacticStrategy,
    Fundamental,
    GameModelRef,
    GameModelVocabulary,
    GamePhase,
    SpaceCategory,
    TaskType,
    get_game_model_vocabulary,
)
from .library import (  # noqa: F401
    ExerciseFilter,
    create_exercise,
    get_library,
)
from .serialization import (  # noqa: F401
    exercise_from_dict,
    exercise_to_dict,
    format_from_dict,
    format_to_dict,
)
from .suggest import suggest_tasks_for_phase  # noqa: F401

__all__ = [
    "FootballFormat", "Position", "list_formats", "get_format",
    "register_format", "unvalidated_rules",
    "Exercise", "ExerciseSpec", "SpaceSpec", "Material", "LoadSpec",
    "PlayerSetup", "AspectTags", "Constraint", "DiagramSpec",
    "TaskType", "DidacticStrategy", "SpaceCategory", "Fundamental",
    "GamePhase", "GameModelRef", "GameModelVocabulary",
    "get_game_model_vocabulary",
    "create_exercise", "get_library", "ExerciseFilter",
    "suggest_tasks_for_phase", "apply_adaptations", "is_adapted",
    "exercise_to_dict", "exercise_from_dict", "format_to_dict", "format_from_dict",
]
