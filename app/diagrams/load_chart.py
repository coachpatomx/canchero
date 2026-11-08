"""render_load_chart: gráfica de líneas de volumen e intensidad por microciclo
(secundario, RF-5). SVG puro."""
from __future__ import annotations

from dataclasses import dataclass

from periodization_engine import I18nText, LoadCurve

from . import svg_primitives as p

W = 900
H = 360
PAD = 50
VOL = "#1565c0"
INT = "#c62828"


@dataclass(frozen=True)
class SvgChart:
    svg: str
    width: int
    height: int
    title: I18nText


def _points_path(values, n, color):
    if n <= 1:
        xs = [PAD]
    else:
        xs = [PAD + (W - 2 * PAD) * i / (n - 1) for i in range(n)]
    segs = ""
    prev = None
    for x, v in zip(xs, values):
        y = H - PAD - (H - 2 * PAD) * (v / 100.0)
        segs += p.circle(x, y, 4, fill=color)
        if prev is not None:
            segs += p.line(prev[0], prev[1], x, y, stroke=color, stroke_width=3)
        prev = (x, y)
    return segs


def render_load_chart(curve: LoadCurve, lang: str = "es") -> SvgChart:
    pts = list(curve.points)
    n = len(pts)
    body = p.rect(0, 0, W, H, fill="#ffffff", stroke="none")
    # Ejes.
    body += p.line(PAD, H - PAD, W - PAD, H - PAD, stroke="#333", stroke_width=2)
    body += p.line(PAD, PAD, PAD, H - PAD, stroke="#333", stroke_width=2)
    # Líneas de referencia 0/50/100%.
    for pct in (0, 50, 100):
        y = H - PAD - (H - 2 * PAD) * (pct / 100.0)
        body += p.line(PAD, y, W - PAD, y, stroke="#ddd", stroke_width=1)
        body += p.text(10, y + 4, f"{pct}%", size=12, fill="#555")

    body += _points_path([pt.volume_pct for pt in pts], n, VOL)
    body += _points_path([pt.intensity_pct for pt in pts], n, INT)

    # Leyenda bilingüe.
    vol_lab = "Volumen" if lang == "es" else "Volume"
    int_lab = "Intensidad" if lang == "es" else "Intensity"
    body += p.circle(W - 220, 30, 6, fill=VOL)
    body += p.text(W - 205, 35, vol_lab, size=14)
    body += p.circle(W - 120, 30, 6, fill=INT)
    body += p.text(W - 105, 35, int_lab, size=14)

    title = I18nText("Curva de carga", "Load curve")
    body = p.text(PAD, 30, title.es if lang == "es" else title.en,
                  size=20, weight="bold") + body
    doc = p.svg_document(W, H, body)
    return SvgChart(doc, W, H, title)
