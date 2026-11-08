"""Lienzo del campo (cancha esquemática) por formato, en coordenadas de píxel.

Sistema normalizado: ancho fijo de 1000 u. escalado a la proporción del campo
del formato; alto derivado. Media cancha o cancha completa.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import svg_primitives as p

CANVAS_W = 1000
MARGIN = 40
GREEN = "#2e7d32"
GRASS = "#43a047"


@dataclass(frozen=True)
class PitchGeom:
    width: int
    height: int
    inner_x: float
    inner_y: float
    inner_w: float
    inner_h: float


def pitch_geometry(field_length_m: float, field_width_m: float, half: bool) -> PitchGeom:
    length = field_length_m if field_length_m > 0 else 100.0
    width_m = field_width_m if field_width_m > 0 else 64.0
    if half:
        length = length / 2.0
    ratio = width_m / length
    inner_w = CANVAS_W - 2 * MARGIN
    inner_h = inner_w * ratio
    total_w = CANVAS_W
    total_h = int(inner_h + 2 * MARGIN)
    return PitchGeom(total_w, total_h, MARGIN, MARGIN, inner_w, inner_h)


def draw_pitch(geom: PitchGeom, half: bool) -> str:
    body = p.rect(0, 0, geom.width, geom.height, fill=GRASS, stroke="none")
    body += p.rect(geom.inner_x, geom.inner_y, geom.inner_w, geom.inner_h,
                   fill=GREEN, stroke="#ffffff", stroke_width=3)
    cx = geom.inner_x + geom.inner_w / 2
    # Línea media (solo cancha completa) y círculo central.
    if not half:
        p_line = p.line(cx, geom.inner_y, cx, geom.inner_y + geom.inner_h,
                        stroke="#ffffff", stroke_width=2)
        body += p_line
        body += p.circle(cx, geom.inner_y + geom.inner_h / 2, geom.inner_h * 0.12,
                         fill="none", stroke="#ffffff", stroke_width=2)
    # Áreas esquemáticas en los extremos.
    area_w = geom.inner_w * 0.10
    area_h = geom.inner_h * 0.5
    ay = geom.inner_y + (geom.inner_h - area_h) / 2
    body += p.rect(geom.inner_x, ay, area_w, area_h, fill="none",
                   stroke="#ffffff", stroke_width=2)
    body += p.rect(geom.inner_x + geom.inner_w - area_w, ay, area_w, area_h,
                   fill="none", stroke="#ffffff", stroke_width=2)
    return body
