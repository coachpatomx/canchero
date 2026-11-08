"""Modelo ATR: Acumulación → Transformación → Realización. Fuente: C3 + D4."""
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
    id="atr",
    name=I18nText(es="ATR (Acumulación-Transformación-Realización)",
                  en="ATR (Accumulation-Transmutation-Realization)"),
    source=ModelSource.BUILTIN,
    rules=ModelRules(
        period_plan=(
            PeriodTemplate(PeriodKind.PREPARATORY, PeriodStage.GENERAL, weight=0.30),
            PeriodTemplate(PeriodKind.PREPARATORY, PeriodStage.SPECIAL, weight=0.15),
            PeriodTemplate(PeriodKind.COMPETITIVE, PeriodStage.COMPETITIVE, weight=0.45),
            PeriodTemplate(PeriodKind.TRANSITION, PeriodStage.TRANSITION, weight=0.10),
        ),
        # A: desarrollo (volumen), T: choque (intensidad), R: precompetitivo.
        micro_wave=(
            MicrocycleType.DEVELOPMENTAL,
            MicrocycleType.DEVELOPMENTAL,
            MicrocycleType.SHOCK,
            MicrocycleType.PRECOMPETITIVE,
        ),
        meso_length_weeks=4,
    ),
)
