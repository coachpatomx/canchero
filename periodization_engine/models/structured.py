"""Entrenamiento Estructurado (Seirul·lo): estructuras del jugador, situaciones
simuladoras preferenciales, carga por especificidad. Fuente: C5/C6 + web D4."""
from __future__ import annotations

from ..domain import (
    I18nText,
    MicrocycleType,
    ModelRules,
    ModelSource,
    PeriodizationModel,
    PeriodKind,
    PeriodStage,
    PeriodTemplate,
)

MODEL = PeriodizationModel(
    id="structured",
    name=I18nText(es="Entrenamiento Estructurado (Seirul·lo)",
                  en="Structured Training (Seirul·lo)"),
    source=ModelSource.BUILTIN,
    rules=ModelRules(
        period_plan=(
            PeriodTemplate(PeriodKind.PREPARATORY, PeriodStage.SPECIAL, weight=0.25),
            PeriodTemplate(PeriodKind.COMPETITIVE, PeriodStage.COMPETITIVE, weight=0.65),
            PeriodTemplate(PeriodKind.TRANSITION, PeriodStage.TRANSITION, weight=0.10),
        ),
        micro_wave=(
            MicrocycleType.DEVELOPMENTAL,
            MicrocycleType.DEVELOPMENTAL,
            MicrocycleType.PRECOMPETITIVE,
            MicrocycleType.RECOVERY,
        ),
        meso_length_weeks=4,
    ),
)
