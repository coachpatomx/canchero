"""Modelo Por Bloques (Issurin): bloques concentrados acumulación→transmutación→
realización. Fuente: C3 + validación web D4."""
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
    id="blocks",
    name=I18nText(es="Por bloques (Issurin)", en="Block periodization (Issurin)"),
    source=ModelSource.BUILTIN,
    rules=ModelRules(
        period_plan=(
            PeriodTemplate(PeriodKind.PREPARATORY, PeriodStage.GENERAL, weight=0.25),
            PeriodTemplate(PeriodKind.PREPARATORY, PeriodStage.SPECIAL, weight=0.20),
            PeriodTemplate(PeriodKind.COMPETITIVE, PeriodStage.COMPETITIVE, weight=0.45),
            PeriodTemplate(PeriodKind.TRANSITION, PeriodStage.TRANSITION, weight=0.10),
        ),
        # Bloques: carga concentrada (shock) seguida de realización (precompetitivo).
        micro_wave=(
            MicrocycleType.DEVELOPMENTAL,
            MicrocycleType.SHOCK,
            MicrocycleType.SHOCK,
            MicrocycleType.PRECOMPETITIVE,
        ),
        meso_length_weeks=4,
    ),
)
