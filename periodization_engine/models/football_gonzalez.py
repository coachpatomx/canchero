"""Esquema de A. González para fútbol (torneos cortos tipo liga MX).

Reinicia ciclos en plena competencia: Resistencia → Fuerza → Velocidad →
Recuperación, en ciclos cortos (4-9 semanas). Fuente: C3 (esquema alternativo
para fútbol). Añadido como 6º modelo a petición del usuario (D4 ampliada).
"""
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
    id="football_gonzalez",
    name=I18nText(es="Esquema A. González (fútbol, torneos cortos)",
                  en="A. González scheme (football, short tournaments)"),
    source=ModelSource.BUILTIN,
    rules=ModelRules(
        period_plan=(
            PeriodTemplate(PeriodKind.RESISTANCE, PeriodStage.GENERAL, weight=0.25),
            PeriodTemplate(PeriodKind.STRENGTH, PeriodStage.SPECIAL, weight=0.25),
            PeriodTemplate(PeriodKind.SPEED, PeriodStage.COMPETITIVE, weight=0.35),
            PeriodTemplate(PeriodKind.RECOVERY, PeriodStage.TRANSITION, weight=0.15),
        ),
        micro_wave=(
            MicrocycleType.DEVELOPMENTAL,
            MicrocycleType.SHOCK,
            MicrocycleType.PRECOMPETITIVE,
            MicrocycleType.RECOVERY,
        ),
        meso_length_weeks=3,  # ciclos cortos
        restart_in_competition=True,
    ),
)
