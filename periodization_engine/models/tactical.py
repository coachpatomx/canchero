"""Periodización Táctica (Frade): morfociclo patrón semanal estable, el juego
como eje. Fuente: C4/C5/C6 + validación web D4."""
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
    id="tactical",
    name=I18nText(es="Periodización Táctica (Frade)",
                  en="Tactical Periodization (Frade)"),
    source=ModelSource.BUILTIN,
    rules=ModelRules(
        period_plan=(
            PeriodTemplate(PeriodKind.PREPARATORY, PeriodStage.SPECIAL, weight=0.20),
            PeriodTemplate(PeriodKind.COMPETITIVE, PeriodStage.COMPETITIVE, weight=0.70),
            PeriodTemplate(PeriodKind.TRANSITION, PeriodStage.TRANSITION, weight=0.10),
        ),
        # Morfociclo estable: patrón semanal repetido en competencia.
        micro_wave=(
            MicrocycleType.COMPETITION,
            MicrocycleType.COMPETITION,
            MicrocycleType.COMPETITION,
            MicrocycleType.RECOVERY,
        ),
        meso_length_weeks=4,
    ),
)
