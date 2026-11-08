"""Entidades de dominio del motor de periodización.

Todo es inmutable (``frozen=True``) y agnóstico al deporte (RNF-7): aquí no hay
ninguna referencia a fútbol, jugadores, conos ni balones. Solo ciclos, fases y
cargas abstractas.

Fuente metodológica: knowledge-base/metodologia-fmf.md (C3, C4).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# --------------------------------------------------------------------------- #
# Texto bilingüe (D6). El motor transporta claves es/en; no decide el idioma.
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class I18nText:
    es: str
    en: str


# --------------------------------------------------------------------------- #
# Enums (clave estable en inglés; etiquetas bilingües en LABELS más abajo)
# --------------------------------------------------------------------------- #
class PeriodKind(str, Enum):
    PREPARATORY = "preparatory"
    COMPETITIVE = "competitive"
    TRANSITION = "transition"
    # Variantes del esquema de A. González para fútbol (torneos cortos):
    RESISTANCE = "resistance"
    STRENGTH = "strength"
    SPEED = "speed"
    RECOVERY = "recovery"


class PeriodStage(str, Enum):
    GENERAL = "general"
    SPECIAL = "special"
    PRECOMPETITIVE = "precompetitive"
    COMPETITIVE = "competitive"
    TRANSITION = "transition"


class MesocycleType(str, Enum):
    BASE = "base"
    DEVELOPMENT = "development"
    STABILIZATION = "stabilization"
    COMPETITIVE = "competitive"
    RECOVERY = "recovery"


class MicrocycleType(str, Enum):
    INTRODUCTORY = "introductory"
    DEVELOPMENTAL = "developmental"
    SHOCK = "shock"
    RECOVERY = "recovery"
    PRECOMPETITIVE = "precompetitive"
    COMPETITION = "competition"


class MicroPhase(str, Enum):
    RECOVERY = "recovery"
    STIMULATING = "stimulating"
    OPTIMIZATION = "optimization"
    COMPETITIVE = "competitive"


class SessionTypeHint(str, Enum):
    SELECTIVE = "selective"
    COMPLEX = "complex"
    SUPPLEMENTARY = "supplementary"


class CompetitionType(str, Enum):
    LEAGUE = "league"
    SHORT_TOURNAMENT = "short_tournament"
    CUP = "cup"
    FRIENDLY_ONLY = "friendly_only"


class StartFitness(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModelSource(str, Enum):
    BUILTIN = "builtin"
    CUSTOM = "custom"


# --------------------------------------------------------------------------- #
# Entrada
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SeasonParams:
    """Parámetros de temporada (entrada del usuario vía formulario o entrevista)."""

    start_date: str  # ISO-8601 (YYYY-MM-DD); el motor no usa el reloj del sistema
    duration_weeks: int
    training_days_per_week: int
    matches_per_week: int  # 0, 1 o 2
    competition_type: CompetitionType = CompetitionType.LEAGUE
    start_fitness: StartFitness = StartFitness.MEDIUM
    category: str = ""
    objectives: tuple[str, ...] = ()  # claves abstractas, p. ej. "physical.endurance"


# --------------------------------------------------------------------------- #
# Modelo de periodización (reglas como DATOS → RF-4)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class PeriodTemplate:
    """Plantilla de un período dentro del plan del modelo."""

    kind: PeriodKind
    stage: PeriodStage
    weight: float  # peso relativo sobre el total de semanas (se escala)


@dataclass(frozen=True)
class ModelRules:
    """Reglas declarativas que gobiernan la derivación. Un modelo custom es
    simplemente otra instancia de ``ModelRules`` (RF-4)."""

    period_plan: tuple[PeriodTemplate, ...]
    # Secuencia de tipos de microciclo que se repite (ondulación) dentro de los
    # mesociclos de desarrollo. Clave: patrón ondulante del modelo.
    micro_wave: tuple[MicrocycleType, ...]
    # Nº objetivo de microciclos por mesociclo (2..8 según C3).
    meso_length_weeks: int = 4
    restart_in_competition: bool = False

    def validate(self) -> list[str]:
        """Devuelve lista de problemas; vacía si es válido."""
        problems: list[str] = []
        if not self.period_plan:
            problems.append("period_plan vacío")
        if not self.micro_wave:
            problems.append("micro_wave vacío")
        if not (2 <= self.meso_length_weeks <= 8):
            problems.append("meso_length_weeks fuera de rango 2..8")
        total_weight = sum(p.weight for p in self.period_plan)
        if total_weight <= 0:
            problems.append("suma de pesos de period_plan no positiva")
        return problems


@dataclass(frozen=True)
class PeriodizationModel:
    id: str
    name: I18nText
    source: ModelSource
    rules: ModelRules


# --------------------------------------------------------------------------- #
# Salida: jerarquía de ciclos
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class LoadPoint:
    unit_index: int
    volume_pct: int
    intensity_pct: int


@dataclass(frozen=True)
class LoadCurve:
    points: tuple[LoadPoint, ...]


@dataclass(frozen=True)
class SessionSlot:
    day_index: int
    micro_phase: MicroPhase
    relative_to_match: int | None
    target_load: LoadPoint
    session_type: SessionTypeHint


@dataclass(frozen=True)
class Microcycle:
    type: MicrocycleType
    week_index: int  # 1-based dentro del macro
    matches_this_week: int
    target_volume_pct: int
    target_intensity_pct: int
    phases: tuple[MicroPhase, ...]
    session_slots: tuple[SessionSlot, ...] = ()


@dataclass(frozen=True)
class Mesocycle:
    type: MesocycleType
    period_index: int  # índice del período padre
    start_week: int
    end_week: int
    objective_focus: tuple[str, ...]
    microcycles: tuple[Microcycle, ...] = ()


@dataclass(frozen=True)
class Period:
    kind: PeriodKind
    stage: PeriodStage
    start_week: int
    end_week: int


@dataclass(frozen=True)
class Provenance:
    season_params_hash: str
    model_id: str
    engine_version: str


@dataclass(frozen=True)
class Macrocycle:
    id: str
    model_id: str
    total_weeks: int
    periods: tuple[Period, ...]
    provenance: Provenance
    mesocycles: tuple[Mesocycle, ...] = ()
