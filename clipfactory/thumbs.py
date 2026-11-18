"""Portadas (1080x1920) para Shorts/TikTok: 3 variantes por vídeo. Máx. 3 palabras grandes, que NO repitan el título."""

from __future__ import annotations

from pathlib import Path

from PIL import ImageDraw

from . import motion

VARIANTS = [("orange", 0.30), ("cyan", 0.30), ("magenta", 0.70)]  # (color, altura relativa del texto)


def _arrow(img, x, y, color):
    d = ImageDraw.Draw(img)
    d.line([(x, y), (x + 150, y + 150)], fill=color, width=26)
    d.polygon([(x + 190, y + 190), (x + 60, y + 170), (x + 170, y + 60)], fill=color)


def make_covers(portada: dict, out_dir: str | Path) -> list[Path]:
    """portada: {texto, kind(dato|imagen|personaje|clock), ...campos de la tarjeta}."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    texto = (portada.get("texto") or "").upper()
    outs = []
    for i, (color, ty) in enumerate(VARIANTS, 1):
        spec = {k: v for k, v in portada.items() if k not in {"texto", "titulo", "sub"}}
        spec.setdefault("kind", "dato")
        spec["color"] = color
        if spec["kind"] == "dato":
            spec.setdefault("grande", portada.get("grande", "?"))
        img = motion.card(spec)
        acc = motion.COLORS[color]
        y = int(motion.H * ty)
        size = 150
        d = ImageDraw.Draw(img)
        while size > 80 and d.textlength(texto, font=motion._font(size)) > 980:
            size -= 6
        motion._glow_text(img, (motion.W // 2, y), texto, size, motion.WHITE, spread=10, stroke=10)
        d = ImageDraw.Draw(img)
        d.text((motion.W // 2, y), texto, font=motion._font(size), fill=motion.WHITE, anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0))
        d.rectangle([140, y + size // 2 + 20, motion.W - 140, y + size // 2 + 34], fill=acc)
        if i == 2:
            _arrow(img, 120, int(motion.H * 0.42), acc)
        p = out_dir / f"portada-{i}.png"
        img.save(p, optimize=True)
        outs.append(p)
    return outs
