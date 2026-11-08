"""Motor de periodización: derivación determinista de la jerarquía de ciclos.

Todas las funciones son puras: mismas entradas -> misma salida. Sin reloj del
sistema, sin aleatoriedad, sin I/O (RNF-2, RNF-5). Fuente metodológica: C3/C4.
"""
from __future__ import annotations

import hashlib
import json

from .domain import (
    LoadCurve,
    LoadPoint,
    Macrocycle,
    Mesocycle,
    MesocycleType,
    Microcycle,
    MicrocycleType,
    MicroPhase,
    Period,
    PeriodizationModel,
    PeriodKind,
    PeriodStage,
    Provenance,
    SeasonParams,
    SessionSlot,
    SessionTypeHint,
)
from .errors import DomainError, DomainErrorKind, Err, Ok, Result
from .loadtable import START_FITNESS_RAMP, base_load

ENGINE_VERSION = "1.0.0"

MIN_SEASON_WEEKS = 4


# --------------------------------------------------------------------------- #
# Hash determinista de entradas (para MacrocycleId y Provenance)
# --------------------------------------------------------------------------- #
def _season_hash(season: SeasonParams, model_id: str) -> str:
    canonical = {
        "start_date": season.start_date,
        "duration_weeks": season.duration_weeks,
        "training_days_per_week": season.training_days_per_week,
        "matches_per_week": season.matches_per_week,
        "competition_type": season.competition_type.value,
        "start_fitness": season.start_fitness.value,
        "category": season.category,
        "objectives": sorted(season.objectives),
        "model_id": model_id,
        "engine_version": ENGINE_VERSION,
    }
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------- #
# Macro -> Períodos
# --------------------------------------------------------------------------- #
def _allocate_weeks(total_weeks: int, weights: list[float]) -> list[int]:
    """Reparte ``total_weeks`` entre períodos según sus pesos, garantizando que
    la suma sea exactamente ``total_weeks``.

    Si hay más períodos que semanas, solo los primeros ``total_weeks`` períodos
    (por peso descendente, con el orden original como desempate) reciben 1 semana
    y el resto se descarta — un período de 0 semanas no tiene sentido. Esto
    mantiene el reparto determinista.
    """
    n = len(weights)
    if total_weeks >= n:
        total_weight = sum(weights)
        # Reparto base por el método del mayor residuo (Hamilton).
        exact = [total_weeks * w / total_weight for w in weights]
        floor = [max(1, int(f)) for f in exact]  # mínimo 1 semana por período
        assigned = sum(floor)
        remainders = sorted(
            range(n), key=lambda i: (exact[i] - int(exact[i])), reverse=True
        )
        diff = total_weeks - assigned
        idx = 0
        # Si sobran semanas, repartir de una en una por mayor residuo.
        while diff > 0:
            floor[remainders[idx % n]] += 1
            diff -= 1
            idx += 1
        # Si faltan (porque floor forzó mínimos), quitar de los de mayor cuota
        # que tengan > 1 semana.
        while diff < 0:
            big = sorted(range(n), key=lambda i: floor[i], reverse=True)
            for i in big:
                if floor[i] > 1:
                    floor[i] -= 1
                    diff += 1
                    break
            else:
                break
        return floor
    # Menos semanas que períodos: elegir los total_weeks de mayor peso.
    chosen = set(
        sorted(range(n), key=lambda i: (weights[i], -i), reverse=True)[:total_weeks]
    )
    return [1 if i in chosen else 0 for i in range(n)]


def _build_periods(total_weeks: int, model: PeriodizationModel) -> tuple[Period, ...]:
    templates = model.rules.period_plan
    weights = [t.weight for t in templates]
    alloc = _allocate_weeks(total_weeks, weights)

    periods: list[Period] = []
    week = 1
    for template, weeks in zip(templates, alloc):
        if weeks <= 0:
            continue  # período descartado por falta de semanas
        start = week
        end = week + weeks - 1
        periods.append(
            Period(kind=template.kind, stage=template.stage,
                   start_week=start, end_week=end)
        )
        week = end + 1
    return tuple(periods)


def build_macrocycle(
    season: SeasonParams, model: PeriodizationModel
) -> Result[Macrocycle]:
    if season.duration_weeks < MIN_SEASON_WEEKS:
        return Err(DomainError(DomainErrorKind.INVALID_SEASON_DURATION,
                               detail=f"{season.duration_weeks} < {MIN_SEASON_WEEKS}"))
    if not (1 <= season.training_days_per_week <= 7):
        return Err(DomainError(DomainErrorKind.INVALID_SEASON_DURATION,
                               detail="training_days_per_week fuera de 1..7"))
    if season.matches_per_week not in (0, 1, 2):
        return Err(DomainError(DomainErrorKind.INVALID_SEASON_DURATION,
                               detail="matches_per_week debe ser 0, 1 o 2"))

    problems = model.rules.validate()
    if problems:
        return Err(DomainError(DomainErrorKind.INVALID_MODEL_RULES,
                               detail="; ".join(problems)))

    periods = _build_periods(season.duration_weeks, model)
    season_hash = _season_hash(season, model.id)
    macro = Macrocycle(
        id=season_hash,
        model_id=model.id,
        total_weeks=season.duration_weeks,
        periods=periods,
        provenance=Provenance(season_params_hash=season_hash,
                              model_id=model.id,
                              engine_version=ENGINE_VERSION),
    )
    return Ok(macro)


# --------------------------------------------------------------------------- #
# Período -> Mesociclos
# --------------------------------------------------------------------------- #
def _mesotype_for_period(period: Period) -> MesocycleType:
    if period.kind == PeriodKind.TRANSITION or period.kind == PeriodKind.RECOVERY:
        return MesocycleType.RECOVERY
    if period.kind == PeriodKind.COMPETITIVE:
        return MesocycleType.COMPETITIVE
    if period.stage == PeriodStage.GENERAL:
        return MesocycleType.BASE
    return MesocycleType.DEVELOPMENT


def derive_mesocycles(
    macro: Macrocycle, model: PeriodizationModel, season: SeasonParams
) -> tuple[Mesocycle, ...]:
    meso_len = model.rules.meso_length_weeks
    mesos: list[Mesocycle] = []
    for p_index, period in enumerate(macro.periods):
        period_weeks = period.end_week - period.start_week + 1
        week = period.start_week
        while week <= period.end_week:
            end = min(week + meso_len - 1, period.end_week)
            mesos.append(
                Mesocycle(
                    type=_mesotype_for_period(period),
                    period_index=p_index,
                    start_week=week,
                    end_week=end,
                    objective_focus=season.objectives,
                )
            )
            week = end + 1
    return tuple(mesos)


# --------------------------------------------------------------------------- #
# Mesociclo -> Microciclos
# --------------------------------------------------------------------------- #
def _ramp(pct: int, factor: float) -> int:
    return max(0, min(100, round(pct * factor)))


def derive_microcycles(
    meso: Mesocycle,
    macro: Macrocycle,
    model: PeriodizationModel,
    season: SeasonParams,
) -> tuple[Microcycle, ...]:
    wave = model.rules.micro_wave
    period = macro.periods[meso.period_index]
    ramp_factor = START_FITNESS_RAMP.get(season.start_fitness.value, 1.0)
    # La rampa inicial solo aplica al primer período preparatorio.
    apply_ramp = period.stage in (PeriodStage.GENERAL,) and meso.period_index == 0

    micros: list[Microcycle] = []
    for offset, week in enumerate(range(meso.start_week, meso.end_week + 1)):
        # En período competitivo, forzar tipo competición/precompetitivo.
        if period.kind == PeriodKind.COMPETITIVE and meso.type == MesocycleType.COMPETITIVE:
            micro_type = MicrocycleType.COMPETITION
        elif meso.type == MesocycleType.RECOVERY:
            micro_type = MicrocycleType.RECOVERY
        else:
            micro_type = wave[offset % len(wave)]

        vol, inten = base_load(micro_type)
        if apply_ramp:
            vol = _ramp(vol, ramp_factor)
            inten = _ramp(inten, ramp_factor)

        phases = _micro_phases(season.matches_per_week)
        micros.append(
            Microcycle(
                type=micro_type,
                week_index=week,
                matches_this_week=season.matches_per_week,
                target_volume_pct=vol,
                target_intensity_pct=inten,
                phases=phases,
            )
        )
    return tuple(micros)


def _micro_phases(matches_per_week: int) -> tuple[MicroPhase, ...]:
    if matches_per_week == 0:
        return (MicroPhase.STIMULATING,)
    if matches_per_week == 1:
        return (
            MicroPhase.RECOVERY,
            MicroPhase.STIMULATING,
            MicroPhase.OPTIMIZATION,
            MicroPhase.COMPETITIVE,
        )
    # 2 partidos: dos mini-ciclos
    return (
        MicroPhase.RECOVERY,
        MicroPhase.STIMULATING,
        MicroPhase.COMPETITIVE,
        MicroPhase.RECOVERY,
        MicroPhase.OPTIMIZATION,
        MicroPhase.COMPETITIVE,
    )


# --------------------------------------------------------------------------- #
# Microciclo -> SessionSlots
# --------------------------------------------------------------------------- #
def derive_session_slots(
    micro: Microcycle, season: SeasonParams
) -> tuple[SessionSlot, ...]:
    days = season.training_days_per_week
    base_vol = micro.target_volume_pct
    base_inten = micro.target_intensity_pct
    slots: list[SessionSlot] = []

    for day in range(1, days + 1):
        phase, rel_to_match, type_hint, vol_f, inten_f = _slot_profile(
            day, days, season.matches_per_week
        )
        slots.append(
            SessionSlot(
                day_index=day,
                micro_phase=phase,
                relative_to_match=rel_to_match,
                target_load=LoadPoint(
                    unit_index=day,
                    volume_pct=max(0, min(100, round(base_vol * vol_f))),
                    intensity_pct=max(0, min(100, round(base_inten * inten_f))),
                ),
                session_type=type_hint,
            )
        )
    return tuple(slots)


def _slot_profile(day: int, total_days: int, matches: int):
    """Perfil de carga intra-microciclo: concentración central y descenso hacia
    el partido (C4). Devuelve (fase, rel_al_partido, tipo_sesión, factor_vol,
    factor_intensidad)."""
    if matches == 0:
        # Pretemporada: carga sostenida/ascendente, pico central.
        mid = (total_days + 1) / 2
        factor = 1.0 - abs(day - mid) / (total_days + 1) * 0.4
        return (MicroPhase.STIMULATING, None, SessionTypeHint.COMPLEX, factor, factor)

    # 1 partido: el último día de entrenamiento es el más cercano al partido.
    days_to_match = total_days - day + 1  # día 1 = más lejos, último = más cerca
    if day == 1:
        return (MicroPhase.RECOVERY, days_to_match, SessionTypeHint.SUPPLEMENTARY, 0.5, 0.4)
    if days_to_match <= 2:
        # optimización (tapering): baja volumen, mantiene intensidad moderada
        return (MicroPhase.OPTIMIZATION, days_to_match, SessionTypeHint.SELECTIVE, 0.6, 0.7)
    # días centrales: estimulador, carga alta
    return (MicroPhase.STIMULATING, days_to_match, SessionTypeHint.COMPLEX, 1.0, 1.0)


# --------------------------------------------------------------------------- #
# Curva de carga
# --------------------------------------------------------------------------- #
def compute_load_curve(macro: Macrocycle) -> LoadCurve:
    """Curva de volumen/intensidad por microciclo a lo largo del macro."""
    points: list[LoadPoint] = []
    for meso in macro.mesocycles:
        for micro in meso.microcycles:
            points.append(
                LoadPoint(
                    unit_index=micro.week_index,
                    volume_pct=micro.target_volume_pct,
                    intensity_pct=micro.target_intensity_pct,
                )
            )
    points.sort(key=lambda p: p.unit_index)
    return LoadCurve(points=tuple(points))


# --------------------------------------------------------------------------- #
# Encadenado completo (modo "completo" de Q5=C)
# --------------------------------------------------------------------------- #
def build_full_tree(
    season: SeasonParams, model: PeriodizationModel
) -> Result[Macrocycle]:
    macro_res = build_macrocycle(season, model)
    if isinstance(macro_res, Err):
        return macro_res
    macro = macro_res.value

    mesos = derive_mesocycles(macro, model, season)
    full_mesos: list[Mesocycle] = []
    for meso in mesos:
        micros = derive_microcycles(meso, macro, model, season)
        full_micros = tuple(
            Microcycle(
                type=m.type,
                week_index=m.week_index,
                matches_this_week=m.matches_this_week,
                target_volume_pct=m.target_volume_pct,
                target_intensity_pct=m.target_intensity_pct,
                phases=m.phases,
                session_slots=derive_session_slots(m, season),
            )
            for m in micros
        )
        full_mesos.append(
            Mesocycle(
                type=meso.type,
                period_index=meso.period_index,
                start_week=meso.start_week,
                end_week=meso.end_week,
                objective_focus=meso.objective_focus,
                microcycles=full_micros,
            )
        )

    return Ok(
        Macrocycle(
            id=macro.id,
            model_id=macro.model_id,
            total_weeks=macro.total_weeks,
            periods=macro.periods,
            provenance=macro.provenance,
            mesocycles=tuple(full_mesos),
        )
    )
