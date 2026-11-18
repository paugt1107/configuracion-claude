"""FERNANDA · Escenas 3D de verdad (three.js + Chromium) para que los vídeos no parezcan diapositivas.

Tarjeta del guion:  {kind: 3d, tipo: numero|texto|orbe|moneda|estrellas|billetes|mapa|versus|piedra|bombilla|corazon|foto, texto: "99",
                     titulo: "¿SABÍAS QUE…?", sub: "nota en Metacritic", color: gold|orange|cyan|magenta|white|green|red, n: 4}
  versus usa texto "GTA V|GTA VI". piedra = lápida romana con letras talladas que se encienden (texto "LUX").
  bombilla = se enciende; corazon = late y suelta cruces de curación; foto = imagen: media/oficial/x.jpg flotando en 3D
  sobre la misma foto desenfocada (si falta el archivo, usa `alt`: otra escena 3D). Renderiza fotograma a fotograma (tiempo exacto), ~0,3 s por fotograma.
Necesita node + playwright (en Actions se instalan solos). Si falta, la escena cae a una tarjeta plana equivalente.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import media

DIR = Path(__file__).with_name("escena3d")
TIPOS = {"numero", "texto", "orbe", "moneda", "estrellas", "billetes", "mapa", "versus", "piedra", "bombilla", "corazon", "foto"}


def disponible() -> bool:
    if not shutil.which("node"):
        return False
    r = subprocess.run(["node", "-e", "require('playwright')"], capture_output=True, env=_env())
    return r.returncode == 0


def _env() -> dict:
    env = dict(os.environ)
    try:
        root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        if root:
            env["NODE_PATH"] = os.pathsep.join(p for p in (env.get("NODE_PATH"), root) if p)
    except FileNotFoundError:
        pass
    return env


def plana(spec: dict) -> dict:
    """Tarjeta plana equivalente (si no hay navegador)."""
    tipo, txt = spec.get("tipo", "numero"), str(spec.get("texto", ""))
    base = {"titulo": spec.get("titulo", ""), "sub": spec.get("sub", ""), "color": spec.get("color", "orange"), "ty": 520}
    if tipo == "estrellas":
        return {**base, "kind": "busqueda", "n": spec.get("n", 3)}
    if tipo == "versus" and "|" in txt:
        a, b = txt.split("|", 1)
        return {**base, "kind": "split", "reloj": a, "reloj2": b, "sub": "", "sub2": "", "ty": 330}
    if tipo in ("moneda", "billetes"):
        return {**base, "kind": "dinero", "grande": txt or "$"}
    return {**base, "kind": "dato", "grande": txt or "?"}


def _data_urls(path: Path) -> tuple[str, str]:
    """Foto nítida (máx. 1400 px) y versión desenfocada/oscura para el fondo, como data URL."""
    import base64
    import io

    from PIL import Image, ImageEnhance, ImageFilter

    im = Image.open(path).convert("RGB")
    im.thumbnail((1400, 1400))
    k = 1920 / im.height
    bg = im.resize((max(1, int(im.width * k)), 1920)).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    out = []
    for x in (im, bg):
        buf = io.BytesIO()
        x.save(buf, "JPEG", quality=88)
        out.append("data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode())
    return out[0], out[1]


def clip(spec: dict, dur: float, out: Path, fps: int = 30, crf: int = 19) -> Path:
    """Renderiza la escena a un mp4 1080x1920 de `dur` segundos."""
    s = {k: v for k, v in spec.items() if k != "kind"}
    s["dur"] = float(dur)
    if s.get("tipo") == "foto" and s.get("banco") and not s.get("imagen"):  # foto del banco por etiqueta
        from . import banco

        fotos = sorted(banco.buscar(str(s["banco"])))
        if fotos:
            s["imagen"] = str(fotos[sum(map(ord, str(s.get("texto", "")) + str(dur))) % len(fotos)])
    if s.get("tipo") == "foto":
        if not s.get("imagen") or not Path(s["imagen"]).exists():
            alt = s.get("alt") or {"tipo": "versus", "texto": s.get("texto") or "GTA|VI"}
            s = {**{k: v for k, v in s.items() if k not in ("imagen", "alt")}, **alt}
        else:
            img = Path(s["imagen"])
            if s.get("dibujo"):  # convierte la foto en dibujo antes de animarla (gta | comic | neon | boceto)
                from . import dibujo

                img = dibujo.archivo(img, Path(tempfile.mkdtemp()) / "dibujo.jpg", "gta" if s["dibujo"] is True else str(s["dibujo"]))
            s["imagen"], s["fondo"] = _data_urls(img)
    if s.get("tipo") not in TIPOS:
        raise ValueError(f"Escena 3D desconocida: {s.get('tipo')} (usa {sorted(TIPOS)})")
    with tempfile.TemporaryDirectory(prefix="e3d-") as tmp:
        tmp = Path(tmp)
        (tmp / "spec.json").write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
        subprocess.run(
            ["node", str(DIR / "render.mjs"), str(tmp / "spec.json"), str(tmp / "f"), str(fps)], check=True, env=_env(), timeout=1800
        )
        subprocess.run(
            [
                media.require("ffmpeg"), "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(tmp / "f" / "f%05d.jpg"),
                "-vf", "noise=alls=4:allf=t,fade=t=in:st=0:d=0.12:color=white,format=yuv420p",
                "-t", f"{dur}", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-r", str(fps), str(out),
            ],
            check=True,
        )  # fmt: skip
    return out
