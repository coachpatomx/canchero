"""Primitivas SVG puras: devuelven fragmentos de string SVG. Sin librerías (D3).

Todas deterministas; números formateados con precisión fija para reproducibilidad
byte a byte.
"""
from __future__ import annotations


def _n(x: float) -> str:
    """Formatea un número con 2 decimales fijos (determinismo)."""
    return f"{x:.2f}"


def esc(text: str) -> str:
    """Escapa caracteres especiales de XML en texto."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def rect(x, y, w, h, fill="none", stroke="#333", stroke_width=2, opacity=1.0, rx=0):
    return (
        f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" '
        f'rx="{_n(rx)}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{_n(stroke_width)}" opacity="{_n(opacity)}"/>'
    )


def line(x1, y1, x2, y2, stroke="#333", stroke_width=2, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}" '
        f'stroke="{stroke}" stroke-width="{_n(stroke_width)}"{d}/>'
    )


def circle(cx, cy, r, fill="#000", stroke="none", stroke_width=0):
    return (
        f'<circle cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{_n(stroke_width)}"/>'
    )


def polygon(points: list[tuple[float, float]], fill="#000", stroke="none"):
    pts = " ".join(f"{_n(px)},{_n(py)}" for px, py in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}"/>'


def text(x, y, content, size=18, fill="#111", anchor="start", weight="normal"):
    return (
        f'<text x="{_n(x)}" y="{_n(y)}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}" '
        f'font-family="sans-serif">{esc(content)}</text>'
    )


def cone(cx, cy, size=10, fill="#e67e22"):
    """Cono representado como triángulo."""
    return polygon(
        [(cx, cy - size), (cx - size * 0.7, cy + size), (cx + size * 0.7, cy + size)],
        fill=fill,
    )


def arrow(x1, y1, x2, y2, stroke="#c0392b", stroke_width=3):
    """Flecha de movimiento: línea con punta (triángulo) en el extremo."""
    import math

    ang = math.atan2(y2 - y1, x2 - x1)
    head = 10.0
    hx1 = x2 - head * math.cos(ang - math.pi / 6)
    hy1 = y2 - head * math.sin(ang - math.pi / 6)
    hx2 = x2 - head * math.cos(ang + math.pi / 6)
    hy2 = y2 - head * math.sin(ang + math.pi / 6)
    return (
        line(x1, y1, x2, y2, stroke=stroke, stroke_width=stroke_width)
        + polygon([(x2, y2), (hx1, hy1), (hx2, hy2)], fill=stroke)
    )


def svg_document(width: int, height: int, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">{body}</svg>'
    )
