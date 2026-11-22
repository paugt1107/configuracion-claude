"""FERNANDA · Escenas 3D de verdad (three.js + Chromium) para que los vídeos no parezcan diapositivas.

Tarjeta del guion:  {kind: 3d, tipo: numero|texto|orbe|moneda|estrellas|billetes|mapa|versus|piedra|bombilla|corazon|foto, texto: "99",
                     titulo: "¿SABÍAS QUE…?", sub: "nota en Metacritic", color: gold|orange|cyan|magenta|white|green|red, n: 4}
  versus usa texto "GTA V|GTA VI". piedra = lápida romana con letras talladas que se encienden (texto "LUX").
  diorama = maqueta low-poly con etiquetas en secuencia: {tipo: diorama, preset: consola|discos|almacen|red|isla|mapa_pin|gallina|huevos|dino|nacer|podio|pila|trio|cesta,
    foto con notas (a pantalla completa en vertical): {tipo: foto, imagen|libre, foco: {x, y}, zoom: 1.8, notas: [{texto, x, y (0-1 sobre la foto), t}]} = zoom al detalle + anillo con etiqueta,
    cielo: dia|noche, n, progreso, etiquetas: [{titulo: "NACE", texto: "En una central", icono: "⚡"}, …]}.
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
# zona del mundo → sitio (igual que ZONAS en escena3d/mundo.js): varias frases pueden pasar en el mismo sitio
SITIO_DE_ZONA = {"dinos_noche": "dinos", "truco": "nido", "pone": "nido", "nace": "nido"}
TIPOS = {"numero", "texto", "orbe", "moneda", "estrellas", "billetes", "mapa", "versus", "piedra", "bombilla", "corazon", "foto", "diorama", "mundo"}


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


def _jpeg_url(im, calidad: int = 88) -> str:
    import base64
    import io

    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=calidad)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def foto_vertical(path: str | Path, foco: dict | None = None, punto: tuple | None = None, estilo: str = "cartoon", alto: int = 1280):
    """Recorte 9:16 de la foto alrededor del foco, pasado a dibujo. Devuelve (imagen PIL, (u, v) del punto en el recorte)."""
    from PIL import Image

    from . import dibujo

    im = Image.open(path).convert("RGB")
    W, H = im.size
    fx, fy = (foco or {}).get("x", 0.5), (foco or {}).get("y", 0.5)
    cw, ch = (H * 9 / 16, H) if W / H > 9 / 16 else (W, W * 16 / 9)
    x0 = min(max(0.0, fx * W - cw / 2), W - cw)
    y0 = min(max(0.0, fy * H - ch / 2), H - ch)
    rec = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((alto * 9 // 16, alto), Image.LANCZOS)
    if estilo:
        rec = dibujo.dibujar(rec, estilo, lado=alto)
    px, py = punto if punto and punto[0] is not None else (fx, fy)
    return rec, (round((px * W - x0) / cw, 4), round((py * H - y0) / ch, 4))


def preparar_mundo(s: dict) -> dict:
    """Fotos del mundo → dibujos animados como data URL (vallas 9:16 para entrar a pantalla completa y polaroids)."""
    from PIL import Image

    from . import dibujo

    fotos = {}
    for fid, f in (s.get("fotos") or {}).items():
        if not f.get("imagen") or not Path(f["imagen"]).exists():
            continue
        im, (u, v) = foto_vertical(f["imagen"], f.get("foco"), (f.get("x"), f.get("y")), f.get("estilo", "cartoon"))
        fotos[fid] = {"src": _jpeg_url(im), "x": u, "y": v, "nota": f.get("nota", "")}
    galeria = []
    for g in s.get("galeria") or []:
        if not g.get("imagen") or not Path(g["imagen"]).exists():
            continue
        im = Image.open(g["imagen"]).convert("RGB")
        im.thumbnail((900, 900))
        galeria.append({"src": _jpeg_url(dibujo.dibujar(im, g.get("estilo", "cartoon"), lado=900), 85), "pie": g.get("pie", "")})
    return {**s, "fotos": fotos, "galeria": galeria}


def _render(spec_json: Path, carpeta: Path, fps: int, n: int, trozos: int) -> None:
    """Renderiza los n fotogramas con `trozos` navegadores a la vez (cada uno un tramo seguido)."""
    trozos = max(1, min(trozos, n // 20 or 1))
    cortes = [round(i * n / trozos) for i in range(trozos + 1)]
    procs = [
        subprocess.Popen(["node", str(DIR / "render.mjs"), str(spec_json), str(carpeta), str(fps), str(a), str(b)], env=_env())
        for a, b in zip(cortes, cortes[1:])
    ]
    for p in procs:
        if p.wait(timeout=3600) != 0:
            for q in procs:
                q.kill()
            raise subprocess.CalledProcessError(p.returncode, "render.mjs")


def clip(spec: dict, dur: float, out: Path, fps: int = 30, crf: int = 19, trozos: int | None = None) -> Path:
    """Renderiza la escena a un mp4 1080x1920 de `dur` segundos."""
    fps = int(os.environ.get("ESCENA3D_FPS") or fps)  # pruebas rápidas: ESCENA3D_FPS=6
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
    if s.get("tipo") == "mundo":
        s = preparar_mundo(s)
    if s.get("tipo") not in TIPOS:
        raise ValueError(f"Escena 3D desconocida: {s.get('tipo')} (usa {sorted(TIPOS)})")
    with tempfile.TemporaryDirectory(prefix="e3d-") as tmp:
        tmp = Path(tmp)
        (tmp / "spec.json").write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
        n = max(1, round(float(dur) * fps))
        _render(tmp / "spec.json", tmp / "f", fps, n, trozos or (os.cpu_count() or 2))
        subprocess.run(
            [
                media.require("ffmpeg"), "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(tmp / "f" / "f%05d.jpg"),
                "-vf", "noise=alls=4:allf=t," + ("" if s.get("tipo") == "mundo" else "fade=t=in:st=0:d=0.12:color=white,") + "format=yuv420p",
                "-t", f"{dur}", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-r", str(fps), str(out),
            ],
            check=True,
        )  # fmt: skip
    return out
