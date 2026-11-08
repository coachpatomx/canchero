"""Tabla C3 de distribución de cargas por tipo de microciclo.

Valores guía parafraseados de la metodología FMF (C3, knowledge-base). El motor
toma el punto medio del rango como valor determinista por defecto; un modelo
custom puede fijar valores exactos.
"""
from __future__ import annotations

from .domain import MicrocycleType

# (volumen_min, volumen_max, intensidad_min, intensidad_max) en %
_RANGES: dict[MicrocycleType, tuple[int, int, int, int]] = {
    MicrocycleType.INTRODUCTORY: (10, 30, 40, 60),
    MicrocycleType.DEVELOPMENTAL: (30, 50, 60, 80),
    MicrocycleType.SHOCK: (30, 50, 90, 100),
    MicrocycleType.RECOVERY: (10, 30, 20, 50),
    MicrocycleType.PRECOMPETITIVE: (10, 30, 70, 100),
    MicrocycleType.COMPETITION: (10, 30, 90, 100),
}


def _midpoint(lo: int, hi: int) -> int:
    return (lo + hi) // 2


def base_load(micro_type: MicrocycleType) -> tuple[int, int]:
    """Devuelve (volume_pct, intensity_pct) por defecto (punto medio del rango)."""
    v_lo, v_hi, i_lo, i_hi = _RANGES[micro_type]
    return _midpoint(v_lo, v_hi), _midpoint(i_lo, i_hi)


# Factor de rampa inicial según nivel de forma al empezar (modula las primeras
# semanas para no partir demasiado alto si el equipo llega desentrenado).
START_FITNESS_RAMP: dict[str, float] = {
    "low": 0.85,
    "medium": 1.0,
    "high": 1.1,
}
