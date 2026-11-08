"""periodization_engine — Motor de periodización determinista y reutilizable.

Paquete agnóstico al deporte (RNF-7): no conoce fútbol ni ningún dominio
concreto. Expone la API pública del motor (U1) para que la capa de dominio
(U2) y el orquestador (U5) la consuman.

Principio rector: mismas entradas -> mismo árbol (RF-10, RNF-5). Sin I/O, sin
reloj del sistema, sin aleatoriedad.
"""
from __future__ import annotations

from .domain import (  # noqa: F401
    CompetitionType,
    I18nText,
    LoadCurve,
    LoadPoint,
    Macrocycle,
    Mesocycle,
    MesocycleType,
    Microcycle,
    MicrocycleType,
    MicroPhase,
    ModelRules,
    ModelSource,
    Period,
    PeriodizationModel,
    PeriodKind,
    PeriodStage,
    PeriodTemplate,
    Provenance,
    SeasonParams,
    SessionSlot,
    SessionTypeHint,
    StartFitness,
)
from .engine import (  # noqa: F401
    ENGINE_VERSION,
    build_full_tree,
    build_macrocycle,
    compute_load_curve,
    derive_mesocycles,
    derive_microcycles,
    derive_session_slots,
)
from .errors import (  # noqa: F401
    DomainError,
    DomainErrorKind,
    Err,
    Ok,
    Result,
)
from .models import (  # noqa: F401
    get_model,
    list_models,
    register_custom_model,
)
from .serialization import (  # noqa: F401
    load_curve_to_dict,
    macrocycle_from_dict,
    macrocycle_to_dict,
)

__all__ = [
    "ENGINE_VERSION",
    # entidades
    "I18nText", "SeasonParams", "PeriodizationModel", "ModelRules",
    "PeriodTemplate", "Macrocycle", "Period", "Mesocycle", "Microcycle",
    "SessionSlot", "LoadPoint", "LoadCurve", "Provenance",
    # enums
    "CompetitionType", "StartFitness", "PeriodKind", "PeriodStage",
    "MesocycleType", "MicrocycleType", "MicroPhase", "SessionTypeHint",
    "ModelSource",
    # funciones del motor
    "build_macrocycle", "derive_mesocycles", "derive_microcycles",
    "derive_session_slots", "compute_load_curve", "build_full_tree",
    # modelos
    "list_models", "get_model", "register_custom_model",
    # errores
    "DomainError", "DomainErrorKind", "Ok", "Err", "Result",
    # serialización
    "macrocycle_to_dict", "macrocycle_from_dict", "load_curve_to_dict",
]
