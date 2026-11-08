"""Renderiza un diagrama de ejercicio desde datos estructurados (los que la IA
devuelve por bloque). Formas sencillas estilo pizarra táctica / easy2coach:

- jugadores = círculos numerados (equipo a=azul, b=rojo/amarillo)
- conos = triángulos naranjas
- porterías = mini-arcos (rectángulo abierto) orientados; soporta varias
- balón = círculo blanco
- zonas/figuras = rectángulo translúcido con etiqueta
- flechas: carrera (sólida), conducción (ondulada), pase (punteada)

Coordenadas de entrada en METROS (origen esquina inferior-izquierda). El dibujo
siempre sale APAISADO (horizontal), como las gráficas de easy2coach: el lado
mayor del espacio se mapea al eje X. La relación de aspecto se acota para que un
espacio muy alargado (p. ej. 12x30) no salga como "chorizo" vertical.

Determinista y offline.
"""
from __future__ import annotations

from . import svg_primitives as p
from .pitch import CANVAS_W, GRASS, GREEN, MARGIN

TEAM_A = "#1565c0"   # azul
TEAM_B = "#f4c20d"   # amarillo (como la plantilla América)
TEAM_C = "#2e7d32"   # verde (3er equipo / guías), por si acaso

# Relación alto/ancho del lienzo acotada al estilo de pizarra (apaisado).
_MIN_RATIO = 0.42
_MAX_RATIO = 0.66


def _orient_landscape(ancho_m: float, alto_m: float):
    """Devuelve (largo, corto, swapped) para dibujar siempre apaisado.

    El lado mayor va al eje X (horizontal). `swapped` indica si hubo que
    intercambiar los ejes respecto a las coords de entrada (ancho=X, alto=Y).
    """
    ancho_m = ancho_m if ancho_m and ancho_m > 0 else 40.0
    alto_m = alto_m if alto_m and alto_m > 0 else 30.0
    if alto_m > ancho_m:
        return alto_m, ancho_m, True
    return ancho_m, alto_m, False


def _scale_fns(largo_m: float, corto_m: float, swapped: bool):
    """Funciones de escala metros->píxel con aspecto acotado y orientación fija.

    El eje X siempre representa el lado LARGO del espacio; el eje Y el corto.
    Si las coords venían con el eje mayor en Y (swapped), las permutamos aquí
    para que el dibujo quede horizontal sin tocar los datos de la IA.
    """
    inner_w = CANVAS_W - 2 * MARGIN
    ratio = corto_m / largo_m
    ratio = max(_MIN_RATIO, min(_MAX_RATIO, ratio))
    inner_h = inner_w * ratio
    total_h = int(inner_h + 2 * MARGIN)

    def sx(mx, my):
        # valor sobre el eje LARGO (horizontal)
        v = my if swapped else mx
        return MARGIN + (v / largo_m) * inner_w

    def sy(mx, my):
        # valor sobre el eje CORTO (vertical), Y invertida (origen abajo)
        v = mx if swapped else my
        return MARGIN + (1 - (v / corto_m)) * inner_h

    return sx, sy, inner_w, inner_h, total_h


def _wavy(x1, y1, x2, y2, stroke, width=3):
    """Línea ondulada (conducción): varias curvas pequeñas a lo largo del trazo."""
    import math

    dx, dy = x2 - x1, y2 - y1
    length = max(1.0, math.hypot(dx, dy))
    segs = max(2, int(length / 14))
    amp = 5
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux  # normal
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


def _team_color(equipo: str) -> str:
    e = str(equipo or "a").lower()
    if e in ("a", "1", "azul", "blue"):
        return TEAM_A
    if e in ("c", "3", "verde", "green", "guia", "guía"):
        return TEAM_C
    return TEAM_B


def _goal_orient(gx_m, largo_m, corto_m, swapped, explicit):
    """Decide hacia dónde mira la portería. Usa 'lado' explícito si viene; si no,
    la coloca mirando hacia dentro según en qué extremo del campo esté."""
    if explicit in ("left", "right", "top", "bottom", "izq", "der", "arriba", "abajo"):
        return {"izq": "left", "der": "right", "arriba": "top", "abajo": "bottom"}.get(
            explicit, explicit)
    # auto: si está en la mitad izquierda del eje largo, mira a la derecha
    v = gx_m
    return "left" if v <= largo_m / 2 else "right"


def render_drill(diagram: dict, title: str = "") -> str:
    """Devuelve un SVG (string) del diagrama del ejercicio (siempre apaisado)."""
    ancho = float(diagram.get("ancho_m") or 40)
    alto = float(diagram.get("alto_m") or 30)
    largo_m, corto_m, swapped = _orient_landscape(ancho, alto)
    sx, sy, iw, ih, total_h = _scale_fns(largo_m, corto_m, swapped)

    body = p.rect(0, 0, CANVAS_W, total_h, fill=GRASS, stroke="none")
    body += p.rect(MARGIN, MARGIN, iw, ih, fill=GREEN, stroke="#ffffff", stroke_width=3)

    cx = MARGIN + iw / 2
    cy = MARGIN + ih / 2
    line = "#ffffff"
    lw = 2

    # El tipo de cancha depende del tamaño (lado largo) del espacio:
    # - grande (>= 60 m) -> cancha completa (línea media, círculo, 2 áreas)
    # - mediano (>= 35 m) -> media cancha (un área de finalización)
    # - reducido (< 35 m) -> rejilla sutil de referencia
    if largo_m >= 60:
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
    elif largo_m >= 35:
        area_w, area_h = iw * 0.16, ih * 0.6
        ay = MARGIN + (ih - area_h) / 2
        body += p.rect(MARGIN + iw - area_w, ay, area_w, area_h, fill="none", stroke=line, stroke_width=lw)
        body += p.circle(MARGIN + iw - area_w, cy, 3, fill=line, stroke="none")
    else:
        for k in (1, 2):
            body += p.line(MARGIN + iw * k / 3, MARGIN, MARGIN + iw * k / 3, MARGIN + ih,
                           stroke=line, stroke_width=1, dash="4,8")
            body += p.line(MARGIN, MARGIN + ih * k / 3, MARGIN + iw, MARGIN + ih * k / 3,
                           stroke=line, stroke_width=1, dash="4,8")

    # etiqueta de dimensiones reales del espacio (ancho x alto originales)
    body += p.text(MARGIN + 6, MARGIN + ih - 8, f"{int(ancho)}x{int(alto)} m",
                   size=13, fill="#eafbe9")

    # ---- zonas / figuras (fondo translúcido con etiqueta) ----
    for z in diagram.get("zonas", []) or []:
        try:
            zx0 = float(z["x"])
            zy0 = float(z["y"])
            zw_m = float(z.get("w", 0))
            zh_m = float(z.get("h", 0))
            # esquinas en metros -> píxel (respetando orientación)
            x_a = sx(zx0, zy0)
            x_b = sx(zx0 + zw_m, zy0 + zh_m)
            y_a = sy(zx0, zy0)
            y_b = sy(zx0 + zw_m, zy0 + zh_m)
            zx, zw = min(x_a, x_b), abs(x_b - x_a)
            zy, zh = min(y_a, y_b), abs(y_b - y_a)
            body += p.rect(zx, zy, zw, zh, fill="#ffffff", stroke="#ffffff",
                           stroke_width=1, opacity=0.14)
            if z.get("etiqueta"):
                body += p.text(zx + 4, zy + 16, str(z["etiqueta"]), size=13, fill="#fff")
        except (KeyError, ValueError, TypeError):
            continue

    # ---- flechas (sobre el campo, debajo de jugadores) ----
    arrow_color = {"carrera": "#ffffff", "conduccion": "#ffd54f", "pase": "#c0392b"}
    for a in diagram.get("flechas", []) or []:
        try:
            x1, y1 = sx(float(a["x1"]), float(a["y1"])), sy(float(a["x1"]), float(a["y1"]))
            x2, y2 = sx(float(a["x2"]), float(a["y2"])), sy(float(a["x2"]), float(a["y2"]))
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

    # ---- porterías (varias, orientadas; mini-arcos estilo pizarra) ----
    goal_len = max(28.0, min(ih * 0.4, 70.0))
    for g in diagram.get("porterias", []) or []:
        try:
            gx_m, gy_m = float(g["x"]), float(g["y"])
            gx, gy = sx(gx_m, gy_m), sy(gx_m, gy_m)
            long_val = gy_m if swapped else gx_m
            orient = _goal_orient(long_val, largo_m, corto_m, swapped,
                                  str(g.get("lado", "")).lower())
            body += p.goal(gx, gy, orient=orient, length=goal_len, depth=14)
        except (KeyError, ValueError, TypeError):
            continue

    # ---- conos (triángulos) ----
    for c in diagram.get("conos", []) or []:
        try:
            body += p.cone(sx(float(c["x"]), float(c["y"])),
                           sy(float(c["x"]), float(c["y"])), size=9)
        except (KeyError, ValueError, TypeError):
            continue

    # ---- jugadores (círculos numerados) ----
    for pl in diagram.get("jugadores", []) or []:
        try:
            px, py = sx(float(pl["x"]), float(pl["y"])), sy(float(pl["x"]), float(pl["y"]))
            color = _team_color(pl.get("equipo", "a"))
            txt = "#fff" if color != TEAM_B else "#222"  # amarillo lleva texto oscuro
            body += p.circle(px, py, 13, fill=color, stroke="#fff", stroke_width=2)
            num = pl.get("num")
            if num is not None:
                body += p.text(px, py + 4, str(num), size=13, fill=txt, anchor="middle")
        except (KeyError, ValueError, TypeError):
            continue

    # ---- balones ----
    for b in diagram.get("balones", []) or []:
        try:
            body += p.circle(sx(float(b["x"]), float(b["y"])),
                             sy(float(b["x"]), float(b["y"])), 7,
                             fill="#fafafa", stroke="#111", stroke_width=2)
        except (KeyError, ValueError, TypeError):
            continue

    # leyenda breve
    body += p.text(MARGIN, total_h - 10,
                   "▲ cono   → carrera   ⇢ pase   ∿ conducción   ⊓ portería",
                   size=13, fill="#eee")
    if title:
        body = p.text(MARGIN, MARGIN - 12, title, size=18, weight="bold") + body

    return p.svg_document(CANVAS_W, total_h, body)


def has_drill_data(diagram) -> bool:
    """True si el dict trae suficientes datos para dibujar algo útil."""
    if not isinstance(diagram, dict):
        return False
    return any(diagram.get(k) for k in ("jugadores", "conos", "porterias", "flechas", "zonas"))
