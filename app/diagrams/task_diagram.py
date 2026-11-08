"""render_task_diagram: dibuja una tarea sobre media cancha (SVG).

Jugadores (equipo A/B) en cuadrícula determinista, conos, balón, zonas y
marcadores adaptados (vallas, guía). Leyenda bilingüe.
"""
from __future__ import annotations

from dataclasses import dataclass

from periodization_engine import I18nText

from . import svg_primitives as p
from .pitch import draw_pitch, pitch_geometry

TEAM_A = "#1565c0"
TEAM_B = "#c62828"
BALL = "#fafafa"

# Etiquetas bilingües de marcadores adaptados (D6).
_MARKER_LABELS = {
    "side_boards": I18nText("Vallas laterales", "Side boards"),
    "guide": I18nText("Guía / llamador", "Guide / caller"),
    "zones": I18nText("Zonas (def/medio/ataque)", "Zones (def/mid/att)"),
}


@dataclass(frozen=True)
class SvgDiagram:
    svg: str
    width: int
    height: int
    title: I18nText


def _grid_positions(n: int, x0, y0, w, h):
    """Posiciones deterministas en cuadrícula dentro de un rectángulo."""
    if n <= 0:
        return []
    import math

    cols = max(1, math.ceil(math.sqrt(n)))
    rows = max(1, math.ceil(n / cols))
    pts = []
    for i in range(n):
        r = i // cols
        c = i % cols
        px = x0 + w * (c + 1) / (cols + 1)
        py = y0 + h * (r + 1) / (rows + 1)
        pts.append((px, py))
    return pts


def render_task_diagram(exercise, fmt, lang: str = "es") -> SvgDiagram:
    half = True
    geom = pitch_geometry(fmt.field_length_m, fmt.field_width_m, half=half)
    body = draw_pitch(geom, half=half)

    spec = exercise.diagram_spec
    ix, iy, iw, ih = geom.inner_x, geom.inner_y, geom.inner_w, geom.inner_h

    if spec is None:
        label = "sin datos de tarea" if lang == "es" else "no task data"
        body += p.text(ix + 10, iy + 30, label, size=20, fill="#fff")
        doc = p.svg_document(geom.width, geom.height, body)
        return SvgDiagram(doc, geom.width, geom.height,
                          I18nText("Tarea", "Task"))

    # Marcadores adaptados primero (capa de fondo).
    markers = spec.adapted_markers
    if "side_boards" in markers:
        body += p.rect(ix, iy, iw, 6, fill="#fdd835", stroke="none")
        body += p.rect(ix, iy + ih - 6, iw, 6, fill="#fdd835", stroke="none")
    if "zones" in markers:
        for k in (1, 2):
            zx = ix + iw * k / 3
            body += p.line(zx, iy, zx, iy + ih, stroke="#ffffff",
                           stroke_width=1, dash="6,6")
    if "guide" in markers:
        body += p.circle(ix + iw + 4, iy + ih / 2, 8, fill="#8e24aa")
        body += p.text(ix + iw - 60, iy + ih / 2,
                       "Guía" if lang == "es" else "Guide", size=14, fill="#fff")

    # Zonas de contenido (claves de momentos C1).
    zone_x = {"final_third": 0.66, "middle": 0.33, "build_up": 0.0}
    for z in spec.zones:
        fx = zone_x.get(z, 0.0)
        body += p.rect(ix + iw * fx, iy, iw / 3, ih, fill="#ffffff",
                       stroke="none", opacity=0.12)

    # Jugadores: A a la izquierda, B a la derecha.
    half_w = iw / 2
    for (px, py) in _grid_positions(spec.players_a, ix, iy, half_w, ih):
        body += p.circle(px, py, 14, fill=TEAM_A, stroke="#fff", stroke_width=2)
    for (px, py) in _grid_positions(spec.players_b, ix + half_w, iy, half_w, ih):
        body += p.circle(px, py, 14, fill=TEAM_B, stroke="#fff", stroke_width=2)

    # Conos repartidos en el borde superior del espacio.
    for i in range(spec.cones):
        cx = ix + iw * (i + 1) / (spec.cones + 1)
        body += p.cone(cx, iy + 14)

    # Balón(es) al centro.
    for i in range(spec.balls):
        body += p.circle(ix + iw / 2 + i * 20, iy + ih / 2, 8,
                         fill=BALL, stroke="#111", stroke_width=2)

    # Leyenda bilingüe de marcadores adaptados.
    ly = geom.height - 14
    legend = []
    for mk in markers:
        lab = _MARKER_LABELS.get(mk)
        if lab:
            legend.append(lab.es if lang == "es" else lab.en)
    if legend:
        body += p.text(ix, ly, " · ".join(legend), size=14, fill="#111")

    title = exercise.name
    body = (
        p.text(ix, iy - 12,
               (title.es if lang == "es" else title.en), size=20, weight="bold")
        + body
    )

    doc = p.svg_document(geom.width, geom.height, body)
    return SvgDiagram(doc, geom.width, geom.height, title)
