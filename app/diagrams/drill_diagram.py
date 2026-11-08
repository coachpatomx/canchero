"""Renderiza un diagrama de ejercicio desde datos estructurados (los que la IA
devuelve por bloque). Formas sencillas estilo pizarra táctica:

- jugadores = círculos numerados (equipo a=azul, b=rojo)
- conos = triángulos naranjas
- porterías = rectángulo con postes
- balón = círculo blanco
- zonas = rectángulo translúcido con etiqueta
- flechas: carrera (línea sólida), conducción (línea ondulada), pase (punteada)

Coordenadas de entrada en METROS (origen esquina inferior-izquierda). Se
escalan al lienzo SVG. Determinista y offline.
"""
from __future__ import annotations

from . import svg_primitives as p
from .pitch import CANVAS_W, GRASS, GREEN, MARGIN

TEAM_A = "#1565c0"
TEAM_B = "#c62828"


def _scale_fns(ancho_m: float, alto_m: float):
    ancho_m = ancho_m if ancho_m and ancho_m > 0 else 40.0
    alto_m = alto_m if alto_m and alto_m > 0 else 30.0
    inner_w = CANVAS_W - 2 * MARGIN
    inner_h = inner_w * (alto_m / ancho_m)
    total_h = int(inner_h + 2 * MARGIN)

    def sx(mx):
        return MARGIN + (mx / ancho_m) * inner_w

    def sy(my):  # invertir Y: en metros el origen está abajo
        return MARGIN + (1 - (my / alto_m)) * inner_h

    return sx, sy, inner_w, inner_h, total_h


def _wavy(x1, y1, x2, y2, stroke, width=3):
    """Línea ondulada (conducción): varias curvas pequeñas a lo largo del trazo."""
    import math

    dx, dy = x2 - x1, y2 - y1
    length = max(1.0, math.hypot(dx, dy))
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux  # normal
    segs = max(2, int(length / 14))
    amp = 5
    d = f"M {x1:.1f} {y1:.1f}"
    for i in range(1, segs + 1):
        t = i / segs
        px = x1 + dx * t
        py = y1 + dy * t
        side = amp if i % 2 else -amp
        cx = px + nx * side
        cy = py + ny * side
        d += f" Q {cx:.1f} {cy:.1f} {px:.1f} {py:.1f}"
    head = p.arrow(x1 + dx * 0.78, y1 + dy * 0.78, x2, y2, stroke=stroke, stroke_width=width)
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}"/>' + head


def render_drill(diagram: dict, title: str = "") -> str:
    """Devuelve un SVG (string) del diagrama del ejercicio."""
    ancho = float(diagram.get("ancho_m") or 40)
    alto = float(diagram.get("alto_m") or 30)
    sx, sy, iw, ih, total_h = _scale_fns(ancho, alto)

    body = p.rect(0, 0, CANVAS_W, total_h, fill=GRASS, stroke="none")
    body += p.rect(MARGIN, MARGIN, iw, ih, fill=GREEN, stroke="#ffffff", stroke_width=3)

    cx = MARGIN + iw / 2
    cy = MARGIN + ih / 2
    line = "#ffffff"
    lw = 2

    # El tipo de cancha depende del tamaño del espacio del ejercicio:
    # - grande (campo completo, ~>= 60 m de largo o fase de juego) -> cancha completa
    # - mediano -> media cancha (área + círculo parcial)
    # - reducido/pequeño -> solo el rectángulo de trabajo con una rejilla sutil
    if ancho >= 60:
        # cancha completa
        body += p.line(cx, MARGIN, cx, MARGIN + ih, stroke=line, stroke_width=lw)
        body += p.circle(cx, cy, min(iw, ih) * 0.14, fill="none", stroke=line, stroke_width=lw)
        body += p.circle(cx, cy, 3, fill=line, stroke="none")
        area_w, area_h = iw * 0.09, ih * 0.55
        ay = MARGIN + (ih - area_h) / 2
        small_w, small_h = iw * 0.035, ih * 0.28
        sy_ = MARGIN + (ih - small_h) / 2
        body += p.rect(MARGIN, ay, area_w, area_h, fill="none", stroke=line, stroke_width=lw)
        body += p.rect(MARGIN, sy_, small_w, small_h, fill="none", stroke=line, stroke_width=lw)
        body += p.circle(MARGIN + iw * 0.11, cy, 3, fill=line, stroke="none")
        body += p.rect(MARGIN + iw - area_w, ay, area_w, area_h, fill="none", stroke=line, stroke_width=lw)
        body += p.rect(MARGIN + iw - small_w, sy_, small_w, small_h, fill="none", stroke=line, stroke_width=lw)
        body += p.circle(MARGIN + iw - iw * 0.11, cy, 3, fill=line, stroke="none")
    elif ancho >= 35:
        # media cancha: un área a la derecha (zona de finalización) + semicírculo
        area_w, area_h = iw * 0.16, ih * 0.6
        ay = MARGIN + (ih - area_h) / 2
        body += p.rect(MARGIN + iw - area_w, ay, area_w, area_h, fill="none", stroke=line, stroke_width=lw)
        body += p.circle(MARGIN + iw - area_w, cy, 3, fill=line, stroke="none")
    else:
        # espacio reducido: rejilla sutil para dar referencia de dimensiones
        for k in (1, 2):
            body += p.line(MARGIN + iw * k / 3, MARGIN, MARGIN + iw * k / 3, MARGIN + ih,
                           stroke=line, stroke_width=1, dash="4,8")
            body += p.line(MARGIN, MARGIN + ih * k / 3, MARGIN + iw, MARGIN + ih * k / 3,
                           stroke=line, stroke_width=1, dash="4,8")

    # etiqueta de dimensiones reales del espacio
    body += p.text(MARGIN + 6, MARGIN + ih - 8, f"{int(ancho)}x{int(alto)} m",
                   size=13, fill="#eafbe9")

    # zonas (fondo)
    for z in diagram.get("zonas", []) or []:
        try:
            zx, zy = sx(float(z["x"])), sy(float(z["y"]) + float(z.get("h", 0)))
            zw = (float(z.get("w", 0)) / ancho) * iw
            zh = (float(z.get("h", 0)) / alto) * ih
            body += p.rect(zx, zy, zw, zh, fill="#ffffff", stroke="none", opacity=0.14)
            if z.get("etiqueta"):
                body += p.text(zx + 4, zy + 16, str(z["etiqueta"]), size=13, fill="#fff")
        except (KeyError, ValueError, TypeError):
            continue

    # flechas (sobre el campo, debajo de jugadores)
    arrow_color = {"carrera": "#ffffff", "conduccion": "#ffd54f", "pase": "#c0392b"}
    for a in diagram.get("flechas", []) or []:
        try:
            x1, y1 = sx(float(a["x1"])), sy(float(a["y1"]))
            x2, y2 = sx(float(a["x2"])), sy(float(a["y2"]))
            tipo = str(a.get("tipo", "pase"))
            color = arrow_color.get(tipo, "#c0392b")
            if tipo == "conduccion":
                body += _wavy(x1, y1, x2, y2, color)
            elif tipo == "pase":
                body += p.line(x1, y1, x2, y2, stroke=color, stroke_width=3, dash="7,6")
                body += p.arrow(x1 + (x2 - x1) * 0.8, y1 + (y2 - y1) * 0.8, x2, y2,
                                stroke=color, stroke_width=3)
            else:  # carrera
                body += p.arrow(x1, y1, x2, y2, stroke=color, stroke_width=3)
        except (KeyError, ValueError, TypeError):
            continue

    # porterías
    for g in diagram.get("porterias", []) or []:
        try:
            gx, gy = sx(float(g["x"])), sy(float(g["y"]))
            body += p.rect(gx - 4, gy - 22, 8, 44, fill="none", stroke="#ffffff", stroke_width=3)
        except (KeyError, ValueError, TypeError):
            continue

    # conos (triángulos)
    for c in diagram.get("conos", []) or []:
        try:
            body += p.cone(sx(float(c["x"])), sy(float(c["y"])), size=9)
        except (KeyError, ValueError, TypeError):
            continue

    # jugadores (círculos numerados)
    for pl in diagram.get("jugadores", []) or []:
        try:
            px, py = sx(float(pl["x"])), sy(float(pl["y"]))
            color = TEAM_A if str(pl.get("equipo", "a")) == "a" else TEAM_B
            body += p.circle(px, py, 13, fill=color, stroke="#fff", stroke_width=2)
            num = pl.get("num")
            if num is not None:
                body += p.text(px, py + 4, str(num), size=13, fill="#fff", anchor="middle")
        except (KeyError, ValueError, TypeError):
            continue

    # balones
    for b in diagram.get("balones", []) or []:
        try:
            body += p.circle(sx(float(b["x"])), sy(float(b["y"])), 7,
                             fill="#fafafa", stroke="#111", stroke_width=2)
        except (KeyError, ValueError, TypeError):
            continue

    # leyenda breve
    legend = ("<tspan>● azul/rojo = jugadores</tspan>")
    body += p.text(MARGIN, total_h - 10,
                   "▲ cono   → carrera   ⇢ pase   ∿ conducción", size=13, fill="#eee")
    if title:
        body = p.text(MARGIN, MARGIN - 12, title, size=18, weight="bold") + body

    return p.svg_document(CANVAS_W, total_h, body)


def has_drill_data(diagram) -> bool:
    """True si el dict trae suficientes datos para dibujar algo útil."""
    if not isinstance(diagram, dict):
        return False
    return any(diagram.get(k) for k in ("jugadores", "conos", "porterias", "flechas", "zonas"))
