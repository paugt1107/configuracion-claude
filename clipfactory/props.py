"""Objetos gráficos originales de "estilo GTA" dibujados por código (sin material de Rockstar).

Tipos: dinero (bolsa con $), billetes (fajos), estrellas (nivel de búsqueda), sirena, pin (mapa), movil, coche, trofeo,
reloj (horas/tiempo), mando (consola), nota (calificación), bombilla (luz/idea).
Uso en una tarjeta del guion:  props: [{tipo: dinero, x: 0.8, y: 0.3, tam: 260}, {tipo: estrellas, n: 4, y: 0.25}]
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

GREEN, DARK_GREEN, GOLD, WHITE, RED, BLUE = (60, 190, 90), (30, 110, 55), (255, 194, 75), (255, 255, 255), (235, 40, 60), (40, 110, 255)
BROWN, GREY = (150, 105, 60), (90, 95, 110)


def _star(d, cx, cy, r, fill, outline=None, width=0):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline, width=width)


def draw(tipo: str, tam: int = 240, n: int = 3) -> Image.Image:
    """Devuelve una imagen RGBA cuadrada (o apaisada para estrellas/coche) con el objeto, dibujada a 3x y reducida."""
    k = 3
    s = tam * k
    w = s * (5 if tipo == "estrellas" else 2 if tipo == "coche" else 1)
    im = Image.new("RGBA", (w, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tipo == "dinero":
        d.ellipse([s * 0.12, s * 0.30, s * 0.88, s * 0.95], fill=BROWN, outline=(90, 60, 30), width=s // 40)
        d.polygon(
            [(s * 0.36, s * 0.32), (s * 0.30, s * 0.10), (s * 0.70, s * 0.10), (s * 0.64, s * 0.32)], fill=BROWN, outline=(90, 60, 30)
        )
        d.rectangle([s * 0.32, s * 0.27, s * 0.68, s * 0.34], fill=GOLD)
        d.text((s * 0.5, s * 0.64), "$", fill=GOLD, anchor="mm", font=_font(int(s * 0.42)))
    elif tipo == "billetes":
        for i in range(4):
            y = s * (0.62 - i * 0.12)
            d.rounded_rectangle(
                [s * 0.08, y, s * 0.92, y + s * 0.26],
                radius=s // 30,
                fill=GREEN if i % 2 else DARK_GREEN,
                outline=(20, 70, 35),
                width=s // 80,
            )
        d.rectangle([s * 0.42, s * 0.26, s * 0.58, s * 0.88], fill=(235, 225, 190))
        d.text((s * 0.5, s * 0.40), "$", fill=DARK_GREEN, anchor="mm", font=_font(int(s * 0.22)))
    elif tipo == "estrellas":
        for i in range(5):
            cx = s * (0.5 + i)
            _star(d, cx, s * 0.5, s * 0.42, WHITE if i < n else (255, 255, 255, 60), outline=(0, 0, 0), width=s // 30)
    elif tipo == "sirena":
        d.rounded_rectangle([s * 0.10, s * 0.45, s * 0.90, s * 0.75], radius=s // 12, fill=(30, 30, 40))
        d.pieslice([s * 0.15, s * 0.20, s * 0.50, s * 0.70], 180, 360, fill=RED)
        d.pieslice([s * 0.50, s * 0.20, s * 0.85, s * 0.70], 180, 360, fill=BLUE)
    elif tipo == "pin":
        d.ellipse([s * 0.22, s * 0.08, s * 0.78, s * 0.64], fill=RED)
        d.polygon([(s * 0.26, s * 0.46), (s * 0.74, s * 0.46), (s * 0.5, s * 0.95)], fill=RED)
        d.ellipse([s * 0.38, s * 0.24, s * 0.62, s * 0.48], fill=WHITE)
    elif tipo == "movil":
        d.rounded_rectangle([s * 0.28, s * 0.05, s * 0.72, s * 0.95], radius=s // 12, fill=(25, 25, 32), outline=GREY, width=s // 50)
        d.rounded_rectangle([s * 0.32, s * 0.12, s * 0.68, s * 0.84], radius=s // 30, fill=(25, 211, 255))
        for i in range(3):
            d.rounded_rectangle([s * 0.36, s * (0.2 + i * 0.2), s * 0.64, s * (0.32 + i * 0.2)], radius=s // 40, fill=(11, 22, 48))
    elif tipo == "coche":
        d.polygon(
            [
                (s * 0.1, s * 0.62),
                (s * 0.35, s * 0.62),
                (s * 0.6, s * 0.32),
                (s * 1.3, s * 0.32),
                (s * 1.6, s * 0.55),
                (s * 1.9, s * 0.6),
                (s * 1.9, s * 0.78),
                (s * 0.1, s * 0.78),
            ],
            fill=(255, 122, 26),
            outline=(120, 50, 10),
        )
        d.polygon([(s * 0.7, s * 0.38), (s * 1.0, s * 0.38), (s * 1.0, s * 0.56), (s * 0.55, s * 0.56)], fill=(160, 220, 255))
        d.polygon([(s * 1.05, s * 0.38), (s * 1.28, s * 0.38), (s * 1.5, s * 0.56), (s * 1.05, s * 0.56)], fill=(160, 220, 255))
        for cx in (0.45, 1.5):
            d.ellipse([s * (cx - 0.16), s * 0.62, s * (cx + 0.16), s * 0.94], fill=(20, 20, 25))
            d.ellipse([s * (cx - 0.07), s * 0.71, s * (cx + 0.07), s * 0.85], fill=GREY)
    elif tipo == "trofeo":
        d.pieslice([s * 0.22, s * -0.15, s * 0.78, s * 0.62], 0, 180, fill=GOLD)
        d.arc([s * 0.08, s * 0.10, s * 0.36, s * 0.40], 90, 270, fill=GOLD, width=s // 25)
        d.arc([s * 0.64, s * 0.10, s * 0.92, s * 0.40], 270, 90, fill=GOLD, width=s // 25)
        d.rectangle([s * 0.44, s * 0.6, s * 0.56, s * 0.78], fill=GOLD)
        d.rectangle([s * 0.28, s * 0.78, s * 0.72, s * 0.9], fill=GOLD)
    elif tipo == "reloj":
        d.ellipse([s * 0.08, s * 0.08, s * 0.92, s * 0.92], fill=WHITE, outline=GOLD, width=s // 18)
        for i in range(12):
            a = i * math.pi / 6
            r1, r2 = s * 0.33, s * 0.38
            d.line([(s / 2 + r1 * math.cos(a), s / 2 + r1 * math.sin(a)), (s / 2 + r2 * math.cos(a), s / 2 + r2 * math.sin(a))], fill=(30, 30, 35), width=s // 50)
        d.line([(s / 2, s / 2), (s / 2, s * 0.22)], fill=(30, 30, 35), width=s // 28)
        d.line([(s / 2, s / 2), (s * 0.72, s * 0.6)], fill=RED, width=s // 40)
        d.ellipse([s * 0.46, s * 0.46, s * 0.54, s * 0.54], fill=(30, 30, 35))
    elif tipo == "mando":
        d.rounded_rectangle([s * 0.08, s * 0.3, s * 0.92, s * 0.72], s // 8, fill=(35, 38, 48), outline=WHITE, width=s // 60)
        d.ellipse([s * 0.04, s * 0.45, s * 0.34, s * 0.88], fill=(35, 38, 48))
        d.ellipse([s * 0.66, s * 0.45, s * 0.96, s * 0.88], fill=(35, 38, 48))
        d.rectangle([s * 0.2, s * 0.44, s * 0.24, s * 0.58], fill=WHITE)
        d.rectangle([s * 0.15, s * 0.49, s * 0.29, s * 0.53], fill=WHITE)
        for (cx, cy), c in zip([(0.74, 0.42), (0.8, 0.5), (0.74, 0.58), (0.68, 0.5)], [GREEN, RED, BLUE, GOLD]):
            d.ellipse([s * (cx - 0.035), s * (cy - 0.035), s * (cx + 0.035), s * (cy + 0.035)], fill=c)
    elif tipo == "nota":
        d.rounded_rectangle([s * 0.1, s * 0.1, s * 0.9, s * 0.9], s // 10, fill=GREEN, outline=WHITE, width=s // 30)
        for i in range(5):
            _star(d, s * (0.22 + i * 0.14), s * 0.5, s * 0.07, GOLD)
    elif tipo == "bombilla":
        for i in range(5):
            a = math.pi * (1.1 + i * 0.2)
            d.line([(s / 2 + s * 0.36 * math.cos(a), s * 0.4 + s * 0.36 * math.sin(a)), (s / 2 + s * 0.47 * math.cos(a), s * 0.4 + s * 0.47 * math.sin(a))], fill=GOLD, width=s // 28)
        d.ellipse([s * 0.24, s * 0.14, s * 0.76, s * 0.66], fill=GOLD)
        d.polygon([(s * 0.36, s * 0.58), (s * 0.64, s * 0.58), (s * 0.6, s * 0.76), (s * 0.4, s * 0.76)], fill=GOLD)
        d.polygon([(s * 0.52, s * 0.24), (s * 0.4, s * 0.44), (s * 0.5, s * 0.44), (s * 0.46, s * 0.6), (s * 0.6, s * 0.38), (s * 0.5, s * 0.38)], fill=(255, 236, 190))
        for k in range(3):
            d.rounded_rectangle([s * (0.4 + k * 0.02), s * (0.79 + k * 0.06), s * (0.6 - k * 0.02), s * (0.83 + k * 0.06)], s // 60, fill=(200, 200, 205))
    else:
        raise ValueError(f"Objeto desconocido: {tipo}")
    return im.resize((w // k, s // k), Image.LANCZOS)


def _font(size):
    from .motion import _font as f

    return f(size)


def paste(img: Image.Image, p: dict, accent=(255, 122, 26)) -> Image.Image:
    """Pega un objeto con sombra/brillo. p: {tipo, x (0-1), y (0-1), tam, n}."""
    obj = draw(p["tipo"], int(p.get("tam", 240)), int(p.get("n", 3)))
    cx, cy = int(img.width * float(p.get("x", 0.5))), int(img.height * float(p.get("y", 0.5)))
    base = img.convert("RGBA")
    glow = Image.new("RGBA", obj.size, accent + (0,))
    glow.putalpha(obj.split()[3].point(lambda v: int(v * 0.8)))
    glow = glow.filter(ImageFilter.GaussianBlur(max(6, obj.height // 12)))
    pos = (cx - obj.width // 2, cy - obj.height // 2)
    base.alpha_composite(glow, pos)
    base.alpha_composite(obj, pos)
    return base.convert("RGB")
