"""Modelo Tradicional / lineal (Matveyev). Fuente: C3."""
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
    id="traditional",
    name=I18nText(es="Tradicional (Matveyev)", en="Traditional (Matveyev)"),
    source=ModelSource.BUILTIN,
    rules=ModelRules(
        period_plan=(
            PeriodTemplate(PeriodKind.PREPARATORY, PeriodStage.GENERAL, weight=0.30),
            PeriodTemplate(PeriodKind.PREPARATORY, PeriodStage.SPECIAL, weight=0.15),
            PeriodTemplate(PeriodKind.COMPETITIVE, PeriodStage.PRECOMPETITIVE, weight=0.10),
            PeriodTemplate(PeriodKind.COMPETITIVE, PeriodStage.COMPETITIVE, weight=0.35),
            PeriodTemplate(PeriodKind.TRANSITION, PeriodStage.TRANSITION, weight=0.10),
        ),
        micro_wave=(
            MicrocycleType.INTRODUCTORY,
            MicrocycleType.DEVELOPMENTAL,
            MicrocycleType.DEVELOPMENTAL,
            MicrocycleType.SHOCK,
            MicrocycleType.RECOVERY,
        ),
        meso_length_weeks=4,
    ),
)
