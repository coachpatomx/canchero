"""Genera un escudo tipo 'Fútbol Inclusivo Club América' como PNG, para usarlo
como marca de agua en la plantilla inclusiva. Uso interno/local.

Dibuja: anillo exterior azul marino, aro amarillo con texto curvo arriba
("FÚTBOL INCLUSIVO") y abajo ("CLUB AMÉRICA"), dos barras rojas con 19 / 16,
un balón central y las letras C (roja) A (roja) sobre un mapa de América.

Salida: app/interface/static/escudo-inclusivo.png
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
NAVY = (26, 42, 82)
YELLOW = (244, 206, 20)
RED = (214, 40, 40)
WHITE = (255, 255, 255)

OUT = os.path.join(os.path.dirname(__file__), "..", "app", "interface",
                   "static", "escudo-inclusivo.png")


def _font(size: int):
    """Intenta cargar una fuente bold del sistema; si no, la default."""
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/opt/kiro-ide/code-server/lib/vscode/node_modules/katex/dist/fonts/KaTeX_SansSerif-Bold.ttf",
        "/opt/kiro-ide/code-server/lib/vscode/node_modules/katex/dist/fonts/KaTeX_Main-Bold.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _draw_text_arc(draw, cx, cy, radius, text, font, fill, start_ang, end_ang,
                   flip=False):
    """Dibuja texto siguiendo un arco entre start_ang y end_ang (grados)."""
    n = len(text)
    if n == 0:
        return
    step = (end_ang - start_ang) / max(1, n - 1)
    box = 220  # lienzo por glifo (grande para no recortar al rotar)
    for i, ch in enumerate(text):
        ang = math.radians(start_ang + i * step)
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        # rotación de cada glifo tangente al círculo
        rot = -(start_ang + i * step) - 90
        if flip:
            rot += 180
        img_ch = Image.new("RGBA", (box, box), (0, 0, 0, 0))
        d = ImageDraw.Draw(img_ch)
        bbox = d.textbbox((0, 0), ch, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text((box / 2 - w / 2 - bbox[0], box / 2 - h / 2 - bbox[1]), ch,
               font=font, fill=fill)
        img_ch = img_ch.rotate(rot, resample=Image.BICUBIC, center=(box / 2, box / 2))
        base.alpha_composite(img_ch, (int(x) - box // 2, int(y) - box // 2))


base = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(base)
c = SIZE // 2

# Anillo exterior azul
draw.ellipse([20, 20, SIZE - 20, SIZE - 20], fill=NAVY)
# Aro amarillo
draw.ellipse([70, 70, SIZE - 70, SIZE - 70], fill=YELLOW)
# Círculo interior azul (centro)
draw.ellipse([250, 250, SIZE - 250, SIZE - 250], fill=NAVY)

# Barras rojas laterales (como el escudo real)
draw.rectangle([120, c - 30, 250, c - 8], fill=RED)
draw.rectangle([120, c + 8, 250, c + 30], fill=RED)
draw.rectangle([SIZE - 250, c - 30, SIZE - 120, c - 8], fill=RED)
draw.rectangle([SIZE - 250, c + 8, SIZE - 120, c + 30], fill=RED)

# Texto curvo (arriba normal, abajo invertido para que se lea derecho)
f_arc = _font(74)
# Sin acentos: la fuente de respaldo (KaTeX) no trae Ú/É y saldrían como cuadro.
_draw_text_arc(draw, c, c, 400, "FUTBOL INCLUSIVO", f_arc, NAVY,
               start_ang=200, end_ang=340)
_draw_text_arc(draw, c, c, 400, "CLUB AMERICA", f_arc, NAVY,
               start_ang=160, end_ang=20, flip=True)

# 19 / 16
f_year = _font(64)
draw.text((175, c - 32), "19", font=f_year, fill=NAVY)
draw.text((SIZE - 235, c - 32), "16", font=f_year, fill=NAVY)

# Balón central (círculo amarillo con gajos azules tipo balón)
draw.ellipse([310, 310, SIZE - 310, SIZE - 310], fill=YELLOW, outline=NAVY, width=10)
# algunos gajos (líneas radiales suaves) para dar aire a balón
for a in range(0, 360, 60):
    rad = math.radians(a)
    x1 = c + 120 * math.cos(rad)
    y1 = c + 120 * math.sin(rad)
    x2 = c + 195 * math.cos(rad)
    y2 = c + 195 * math.sin(rad)
    draw.line([x1, y1, x2, y2], fill=NAVY, width=6)

# Letras C y A grandes en rojo, centradas sobre el balón
f_ca = _font(320)


def _centered(ch, dx):
    bb = draw.textbbox((0, 0), ch, font=f_ca)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((c + dx - w / 2 - bb[0], c - h / 2 - bb[1]), ch, font=f_ca,
              fill=RED, stroke_width=12, stroke_fill=NAVY)


_centered("C", -120)
_centered("A", 120)

# Recortar a círculo (borde limpio)
mask = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(mask).ellipse([10, 10, SIZE - 10, SIZE - 10], fill=255)
base.putalpha(mask)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
base.save(os.path.abspath(OUT))
print("Escudo guardado en:", os.path.abspath(OUT))
