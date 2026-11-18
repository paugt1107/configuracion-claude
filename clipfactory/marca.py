"""Imagen de marca del canal: banner de YouTube (2560x1440, texto en la zona segura 1546x423) y avatar (800x800, recorte circular)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from . import motion, props, rutas

NAVY, CHARCOAL = motion.NAVY, motion.CHARCOAL
ORANGE, CYAN, MAGENTA, WHITE = motion.ORANGE, motion.CYAN, motion.MAGENTA, motion.WHITE


def _bg(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(NAVY[i] * (1 - t) + CHARCOAL[i] * t) for i in range(3)))
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * 0.15, h * 0.55, w * 0.85, h * 1.4], fill=(120, 55, 15))
    gd.ellipse([w * -0.2, h * -0.6, w * 0.4, h * 0.4], fill=(90, 15, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(min(w, h) // 6))
    img = Image.blend(img, Image.composite(glow, img, glow.convert("L")), 0.6)
    # rejilla synthwave en el suelo
    d = ImageDraw.Draw(img)
    hz = int(h * 0.72)
    for i in range(-20, 21):
        d.line([(w / 2 + i * w * 0.02, hz), (w / 2 + i * w * 0.12, h)], fill=(70, 45, 110), width=2)
    for j in range(1, 10):
        y = hz + (h - hz) * (j / 9) ** 1.8
        d.line([(0, y), (w, y)], fill=(70, 45, 110), width=2)
    return img


def _text(img, xy, text, size, color, stroke=8, glow=True):
    d = ImageDraw.Draw(img)
    f = motion._font(size)
    if glow:
        layer = Image.new("RGB", img.size, (0, 0, 0))
        ImageDraw.Draw(layer).text(xy, text, font=f, fill=color, anchor="mm")
        b = layer.filter(ImageFilter.GaussianBlur(size // 6))
        img.paste(Image.composite(b, img, b.convert("L").point(lambda v: min(255, v * 2))))
        d = ImageDraw.Draw(img)
    d.text(xy, text, font=f, fill=color, anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0))


def banner(
    nombre: str = "¿SABÍAS QUE…?",
    acento: str = "GTA 6",
    lema: str = "Secretos · Trucos · Curiosidades — un Short nuevo cada día",
    out: Path | None = None,
) -> Path:
    W, H = 2560, 1440
    img = _bg(W, H)
    # zona segura: x 507-2053, y 508-931
    size, gap = 150, 50
    d = ImageDraw.Draw(img)
    while size > 70:  # nombre + acento en una línea dentro de la zona segura (1546 px)
        w1, w2 = d.textlength(nombre, font=motion._font(size)), d.textlength(acento, font=motion._font(size))
        if w1 + gap + w2 <= 1480:
            break
        size -= 6
    x0 = (W - (w1 + gap + w2)) / 2
    _text(img, (int(x0 + w1 / 2), 640), nombre, size, WHITE)
    _text(img, (int(x0 + w1 + gap + w2 / 2), 640), acento, size, ORANGE)
    _text(img, (W // 2, 830), lema, 54, CYAN, stroke=4, glow=False)
    for p in (
        {"tipo": "dinero", "x": 0.16, "y": 0.47, "tam": 260},
        {"tipo": "estrellas", "n": 5, "x": 0.5, "y": 0.27, "tam": 90},
        {"tipo": "pin", "x": 0.84, "y": 0.45, "tam": 230},
        {"tipo": "coche", "x": 0.5, "y": 0.86, "tam": 150},
    ):
        img = props.paste(img, p, ORANGE)
    out = out or rutas.ENTREGAS / "marca" / "banner-youtube-2560x1440.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    return out


def avatar(texto: str = "¿?", acento: str = "GTA 6", out: Path | None = None) -> Path:
    S = 800
    img = _bg(S, S)
    d = ImageDraw.Draw(img)
    d.ellipse([40, 40, S - 40, S - 40], outline=ORANGE, width=14)
    _text(img, (S // 2, 330), texto, 330, ORANGE)
    _text(img, (S // 2, 590), acento, 120, WHITE)
    img = props.paste(img, {"tipo": "estrellas", "n": 5, "x": 0.5, "y": 0.83, "tam": 48}, MAGENTA)
    out = out or rutas.ENTREGAS / "marca" / "avatar-800x800.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    return out
