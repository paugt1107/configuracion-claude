"""Recorte de personajes (quitar fondo) con rembg (open source, U²-Net) para escenas tipo 'personaje'.

Uso previsto en GitHub Actions (descarga el modelo la primera vez). Solo imágenes OFICIALES (p. ej. descargas de la
web de Rockstar) o capturas propias, siempre con crédito. Ver politica-fuentes.md.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

import yaml
from PIL import Image

from . import rutas


def cutout(src: str | Path, dst: str | Path) -> Path:
    from rembg import remove  # pip install "rembg[cpu]"

    im = Image.open(src).convert("RGBA")
    out = remove(im)
    bbox = out.split()[3].point(lambda v: 255 if v > 20 else 0).getbbox()
    if bbox:
        out = out.crop(bbox)
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst)
    return dst


def fetch_official(cfg_path: str | Path = rutas.CONFIG_IMAGENES, out_dir: str | Path = rutas.OFICIAL) -> list[Path]:
    """Descarga las imágenes listadas (url + nombre + credito). Solo fuentes oficiales o con permiso."""
    cfg = yaml.safe_load(Path(cfg_path).read_text(encoding="utf-8")) or {}
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    got = []
    for it in cfg.get("imagenes") or []:
        dst = out_dir / it["nombre"]
        if dst.exists() or not it.get("url"):
            continue
        req = urllib.request.Request(it["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            dst.write_bytes(r.read())
        got.append(dst)
    return got


def process_all(src_dir: str | Path = rutas.OFICIAL, dst_dir: str | Path = rutas.RECORTES) -> list[Path]:
    done = []
    for p in sorted(Path(src_dir).glob("*")):
        if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        dst = Path(dst_dir) / (p.stem + ".png")
        if not dst.exists():
            done.append(cutout(p, dst))
    return done
