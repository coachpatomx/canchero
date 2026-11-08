"""render_organization_diagram: cancha completa con zonas, vista global de la
sesión (todas las tareas resumidas)."""
from __future__ import annotations

from periodization_engine import I18nText

from . import svg_primitives as p
from .pitch import draw_pitch, pitch_geometry
from .task_diagram import SvgDiagram


def render_organization_diagram(tasks, fmt, lang: str = "es") -> SvgDiagram:
    geom = pitch_geometry(fmt.field_length_m, fmt.field_width_m, half=False)
    body = draw_pitch(geom, half=False)
    ix, iy, iw, ih = geom.inner_x, geom.inner_y, geom.inner_w, geom.inner_h

    # Divide la cancha en tantas estaciones como tareas (hasta 4) con etiqueta.
    n = max(1, min(len(tasks), 4))
    for i in range(n):
        zx = ix + iw * i / n
        body += p.rect(zx, iy, iw / n, ih, fill="#ffffff", stroke="#fff",
                       stroke_width=1, opacity=0.08)
        if i < len(tasks):
            name = tasks[i].name
            label = name.es if lang == "es" else name.en
            body += p.text(zx + 8, iy + 24, f"{i+1}. {label}", size=14, fill="#fff")

    title = I18nText("Organización de la sesión", "Session organization")
    body = p.text(ix, iy - 12, title.es if lang == "es" else title.en,
                  size=20, weight="bold") + body
    doc = p.svg_document(geom.width, geom.height, body)
    return SvgDiagram(doc, geom.width, geom.height, title)
