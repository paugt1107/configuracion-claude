"""TOMMY · Banco de imágenes del canal: descarga, etiqueta, anima en 3D y hace una galería.

Fuentes (canal-youtube/fuentes/banco.yaml): capturas y artes OFICIALES de Rockstar + fotos LIBRES de Wikimedia Commons.
Resultado en media/banco/:
  oficial/<id>.jpg, libres/<categoria>/<id>.jpg   imágenes (máx. 1920 px)
  animadas/<id>.mp4                               clip 3D de 3 s listo para meter en un vídeo (1080x1920)
  miniaturas/<id>.jpg                             para la galería
  indice.json                                     {id: {archivo, fuente, credito, categoria, etiquetas, w, h, clip}}
  GALERIA.md                                      galería navegable en GitHub
Uso:  python3 -m clipfactory.banco [descargar|etiquetar|animar|galeria|todo] [--max N]
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import yaml
from PIL import Image

from .. import rutas

BANCO = rutas.MEDIA / "banco"
INDICE = BANCO / "indice.json"
CONFIG = rutas.FUENTES / "banco.yaml"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
CREDITO_OFICIAL = "Imagen oficial: Rockstar Games (Grand Theft Auto VI)"

# Etiquetas por texto (nombre de archivo, alt, página)
TEXTO_ETIQUETAS = {
    "jason": r"jason|duval",
    "lucia": r"lucia|caminos",
    "vice-city": r"vice.?city",
    "leonida": r"leonida",
    "keys": r"\bkeys\b|leonida.?keys",
    "grassrivers": r"grass.?rivers",
    "port-gellhorn": r"gellhorn",
    "ambrosia": r"ambrosia",
    "mount-kalaga": r"kalaga",
    "personaje": r"people|character|personaj|cal-hampton|boobie|dre|real-dimez|raul|brian",
    "mapa": r"\bmap\b|mapa",
    "logo": r"logo",
}
# Etiquetas por contenido (CLIP): etiqueta → descripción en inglés
# TEMAS por contenido (CLIP). tema → descripción en inglés. El primero que mejor encaja es la CARPETA de la imagen
# (media/banco/temas/<tema>/); los 3 mejores quedan como etiquetas. Cambiar la lista sube CLIP_VERSION y se re-etiqueta.
CLIP_VERSION = 2
CLIP_ETIQUETAS = {
    # personajes
    "lucia": "a photo of a young latina woman with brown hair and bangs",
    "jason": "a photo of a man with long dark hair and a beard",
    "pareja": "a man and a woman together in a car",
    "personas": "a group of people",
    "policia": "police officers or a police car with lights",
    "criminal": "a masked robber holding a gun",
    # animales
    "perro": "a dog",
    "gato": "a cat",
    "caiman": "an alligator or crocodile",
    "ave": "a bird or a flamingo",
    "animal": "a wild animal",
    "pez": "fish or sea animals underwater",
    # vehículos
    "coche": "a car on the road",
    "deportivo": "a fancy sports car",
    "moto": "a motorcycle",
    "camion": "a truck or a van",
    "barco": "a boat or a yacht on the water",
    "avion": "an airplane",
    "helicoptero": "a helicopter",
    # lugares
    "ciudad": "a city skyline with skyscrapers",
    "calle": "a city street with shops",
    "playa": "a beach with sand and ocean",
    "pantano": "a swamp with tall grass and water",
    "campo": "the countryside with fields and trees",
    "carretera": "a highway or a bridge",
    "gasolinera": "a gas station",
    "tienda": "a store or supermarket",
    "club": "a nightclub with lights",
    "casa": "a house or a mansion",
    "interior": "the inside of a room",
    "carcel": "a prison",
    "puerto": "a port or a marina",
    # objetos
    "dinero": "a lot of cash money",
    "arma": "a gun",
    "joyas": "jewelry and diamonds",
    "movil": "a smartphone screen",
    "comida": "food or drinks",
    "cartel": "a neon sign",
    # ambiente
    "noche": "a city at night with neon lights",
    "atardecer": "a sunset",
    "tormenta": "a storm or a hurricane",
    "fiesta": "people partying",
    "accion": "an explosion or a car chase",
}


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.rockstargames.com/"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


GRUPOS = ("oficial", "trailers", "libres")


def _grupo(v: dict) -> str:
    return "trailers" if v.get("categoria") == "trailer" else "oficial" if v.get("fuente") == "oficial" else "libres"


def cargar() -> dict:
    """Une indice-oficial/trailers/libres.json (cada máquina escribe el suyo, así pueden ir en paralelo)."""
    ind = {}
    for p in [INDICE, *(BANCO / f"indice-{g}.json" for g in GRUPOS)]:
        if p.exists():
            ind.update(json.loads(p.read_text(encoding="utf-8")))
    return ind


def guardar(ind: dict, grupos: tuple[str, ...] = GRUPOS) -> None:
    BANCO.mkdir(parents=True, exist_ok=True)
    for g in grupos:
        sub = {k: v for k, v in ind.items() if _grupo(v) == g}
        (BANCO / f"indice-{g}.json").write_text(json.dumps(sub, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    INDICE.unlink(missing_ok=True)


def _ahash(im: Image.Image) -> str:
    g = im.convert("L").resize((16, 16))
    px = list(g.getdata())
    avg = sum(px) / len(px)
    return "".join("1" if p > avg else "0" for p in px)


def _cerca(a: str, b: str) -> bool:
    return sum(x != y for x, y in zip(a, b)) <= 12


def _guardar_imagen(data: bytes, dst: Path) -> tuple[int, int] | None:
    im = Image.open(io.BytesIO(data))
    im.load()
    if im.width < 700 or im.height < 400:
        return None
    im = im.convert("RGB")
    im.thumbnail((1920, 1920), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "JPEG", quality=86, optimize=True)
    return im.width, im.height


def _etiquetas_texto(*textos: str) -> list[str]:
    t = " ".join(textos).lower()
    return sorted(k for k, pat in TEXTO_ETIQUETAS.items() if re.search(pat, t))


def _limpia(url: str) -> str:
    """Quita parámetros de tamaño para pedir la imagen original."""
    return re.sub(r"\?.*$", "", url)


def descargar_oficial(cfg: dict, ind: dict, maximo: int) -> int:
    paginas = (cfg.get("oficial") or {}).get("paginas") or []
    if not paginas:
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        lista = Path(tmp) / "urls.json"
        subprocess.run(["node", str(Path(__file__).with_name("scrape.mjs")), str(lista), *paginas], check=False, timeout=1800)
        items = json.loads(lista.read_text()) if lista.exists() else []
    print(f"[banco] oficial: {len(items)} URLs candidatas")

    # primero las que parecen capturas/artes grandes; las miniaturas y logos al final
    def prioridad(it):
        u = it["url"].lower()
        return (
            0 if re.search(r"screenshot|artwork|wallpaper|people|places|/vi/", u + it.get("pagina", "").lower()) else 1,
            1 if re.search(r"thumb|small|_s\.|w=\d{2,3}\b|width=\d{2,3}\b|icon", u) else 0,
        )

    items.sort(key=prioridad)
    for it in items[:8]:
        print("[banco] ejemplo:", it["url"][:160])
    hashes = {v["hash"]: k for k, v in ind.items() if v.get("hash")}
    nuevas = 0
    vistos = set()
    for it in items:
        if nuevas >= maximo:
            break
        url = _limpia(it["url"])
        if url in vistos or any(v.get("url") == url for v in ind.values()):
            continue
        vistos.add(url)
        try:
            data = _get(url)
        except Exception:
            try:
                data = _get(it["url"])
            except Exception as e:
                print(f"[banco] no baja {url[:90]}: {e}")
                continue
        try:
            im = Image.open(io.BytesIO(data))
            im.load()
        except Exception:
            continue
        h = _ahash(im)
        dup = next((k for hh, k in hashes.items() if k in ind and _cerca(h, hh)), None)
        if dup and ind[dup]["w"] >= im.width:
            continue
        iid = "of-" + hashlib.sha1(url.encode()).hexdigest()[:10]
        dst = BANCO / "oficial" / f"{iid}.jpg"
        wh = _guardar_imagen(data, dst)
        if not wh:
            continue
        if dup:  # misma imagen en peor calidad: se sustituye
            (BANCO / ind[dup]["archivo"]).unlink(missing_ok=True)
            ind.pop(dup)
            hashes = {hh: k for hh, k in hashes.items() if k != dup}
        nombre = Path(url).stem
        ind[iid] = {
            "archivo": str(dst.relative_to(BANCO)),
            "fuente": "oficial",
            "url": url,
            "pagina": it.get("pagina", ""),
            "credito": CREDITO_OFICIAL,
            "categoria": "oficial",
            "etiquetas": _etiquetas_texto(nombre, it.get("alt", ""), it.get("pagina", "")),
            "alt": it.get("alt", ""),
            "w": wh[0],
            "h": wh[1],
            "hash": h,
        }
        hashes[h] = iid
        nuevas += 1
        if nuevas % 25 == 0:
            guardar(ind, ("oficial",))
            print(f"[banco] oficial: {nuevas} guardadas…")
    print(f"[banco] oficial: {nuevas} nuevas")
    return nuevas


def descargar_libres(cfg: dict, ind: dict, maximo: int) -> int:
    from .. import libres

    lib = dict(cfg.get("libres") or {})
    n = int(lib.pop("n", 3))
    nuevas = 0
    for cat, consultas in lib.items():
        for q in consultas or []:
            if nuevas >= maximo:
                return nuevas
            res = []
            for nombre, fn in (("Openverse", libres.openverse), ("Commons", libres.buscar_varias)):
                try:
                    res += fn(q, n, BANCO / "libres" / cat)
                except Exception as e:
                    print(f"[banco] {nombre} '{q}': {e}")
            for path, credit, w, h in res:
                iid = "lb-" + hashlib.sha1(path.name.encode()).hexdigest()[:10]
                if iid in ind:
                    continue
                ind[iid] = {
                    "archivo": str(path.relative_to(BANCO)),
                    "fuente": "libre",
                    "credito": credit,
                    "categoria": cat,
                    "consulta": q,
                    "etiquetas": sorted({cat, *libres.slug(q).split("-")[:3]}),
                    "w": w,
                    "h": h,
                }
                nuevas += 1
    print(f"[banco] libres: {nuevas} nuevas")
    return nuevas


def trailers(cfg: dict, ind: dict, maximo: int, por_video: int = 400) -> int:
    """Fotogramas de los vídeos OFICIALES de Rockstar (cambios de plano), sin negros ni rótulos, sin duplicados.
    Acepta URLs de vídeo o búsquedas "ytsearchN:…" (solo se bajan los subidos por Rockstar Games)."""
    import shutil

    urls = list((cfg.get("oficial") or {}).get("trailers") or [])
    urls += _videos_rockstar((cfg.get("oficial") or {}).get("paginas_video") or [])
    if not urls or not shutil.which("yt-dlp"):
        print("[banco] tráileres: sin URLs o sin yt-dlp")
        return 0
    hashes = {v["hash"]: k for k, v in ind.items() if v.get("hash")}
    nuevas = 0
    for url in urls:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            if re.search(r"\.(m3u8|mp4|webm)(\?|$)", url):  # fichero/stream directo del CDN de Rockstar
                cmd = ["ffmpeg", "-loglevel", "error", "-y", "-headers", "Referer: https://www.rockstargames.com/\r\n",
                       "-i", url, "-t", "600", "-c", "copy", str(tmp / f"rs{hashlib.sha1(url.encode()).hexdigest()[:8]}.mp4")]  # fmt: skip
            else:
                filtro = [] if "rockstargames.com" in url else ["--match-filter", "uploader *= 'Rockstar Games' & duration < 900"]
                cmd = ["yt-dlp", "-q", "--no-warnings", "-f", "bv*[height<=2160][ext=mp4]/bv*[height<=2160]/best/b",
                       *filtro, "-o", str(tmp / "%(id)s.%(ext)s"), url]  # fmt: skip
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            vids = [v for v in tmp.glob("*.*") if v.suffix in (".mp4", ".webm", ".mkv") and v.stat().st_size > 100_000]
            if not vids:
                print(f"[banco] vídeo {url}: no se pudo bajar ({(r.stderr or '').strip()[:200]})")
                continue
            for vid in vids:
                if nuevas >= maximo:
                    break
                nuevas += _fotogramas(vid, ind, hashes, min(por_video, maximo - nuevas))
    print(f"[banco] tráileres: {nuevas} fotogramas nuevos")
    return nuevas


def _videos_rockstar(paginas: list[str]) -> list[str]:
    """Vídeos OFICIALES alojados en rockstargames.com (no depende de YouTube, que bloquea a los servidores)."""
    if not paginas:
        return []
    import os

    with tempfile.TemporaryDirectory() as tmp:
        lista = Path(tmp) / "videos.json"
        env = {**os.environ, "SCRAPE_VIDEOS": "1"}
        subprocess.run(["node", str(Path(__file__).with_name("scrape.mjs")), str(lista), *paginas], check=False, timeout=1800, env=env)
        items = json.loads(lista.read_text()) if lista.exists() else []
    urls = list(dict.fromkeys(it["url"] for it in items))
    # primero las páginas de vídeo (yt-dlp tiene extractor de Rockstar), luego los streams sueltos
    urls.sort(key=lambda u: 0 if "/videos/video/" in u else 1 if ".m3u8" in u else 2)
    print(f"[banco] vídeos de rockstargames.com: {len(urls)}")
    for u in urls[:10]:
        print("[banco] vídeo:", u[:150])
    return urls[:60]


def _fotogramas(vid: Path, ind: dict, hashes: dict, tope: int) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-i", str(vid), "-vf", "select='gt(scene,0.22)',scale='min(1920,iw)':-2",
             "-vsync", "vfr", "-q:v", "3", str(out / "%04d.jpg")],
            check=False,
            timeout=1800,
        )  # fmt: skip
        frames = sorted(out.glob("*.jpg"))
        print(f"[banco] {vid.name}: {len(frames)} cambios de plano")
        hechos = 0
        for f in frames:
            if hechos >= tope:
                break
            im = Image.open(f)
            g = im.convert("L").resize((64, 36))
            px = list(g.getdata())
            media_l = sum(px) / len(px)
            var = sum((x - media_l) ** 2 for x in px) / len(px)
            if media_l < 28 or var < 250:  # negro, fundido o rótulo plano
                continue
            h = _ahash(im)
            if any(_cerca(h, hh) for hh in hashes):
                continue
            iid = f"tr-{vid.stem[:8]}-{f.stem}"
            dst = BANCO / "oficial" / f"{iid}.jpg"
            wh = _guardar_imagen(f.read_bytes(), dst)
            if not wh:
                continue
            ind[iid] = {
                "archivo": str(dst.relative_to(BANCO)),
                "fuente": "oficial",
                "url": f"https://www.youtube.com/watch?v={vid.stem}",
                "credito": "Fotograma de un vídeo oficial de Grand Theft Auto VI (Rockstar Games)",
                "categoria": "trailer",
                "etiquetas": [],
                "w": wh[0],
                "h": wh[1],
                "hash": h,
            }
            hashes[h] = iid
            hechos += 1
    return hechos


def etiquetar(ind: dict) -> int:
    """Añade etiquetas por CONTENIDO con CLIP (si está instalado). Sobre todo para saber dónde salen Lucía y Jason."""
    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
    except ImportError:
        print("[banco] CLIP no instalado: solo etiquetas por texto")
        return 0
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    keys = list(CLIP_ETIQUETAS)
    txt = proc(text=[CLIP_ETIQUETAS[k] for k in keys], return_tensors="pt", padding=True)
    hechos = 0
    for v in ind.values():
        if v.get("clip") and v.get("clip_v") == CLIP_VERSION:
            continue
        im = Image.open(BANCO / v["archivo"]).convert("RGB")
        with torch.no_grad():  # forward completo: estable entre versiones de transformers
            px = proc(images=im, return_tensors="pt")["pixel_values"]
            p = (
                model(input_ids=txt["input_ids"], attention_mask=txt["attention_mask"], pixel_values=px)
                .logits_per_image.softmax(dim=-1)[0]
                .tolist()
            )
        top = sorted(zip(keys, p), key=lambda x: -x[1])
        auto = [k for k, s in top[:3] if s >= 0.10]
        v["clip"] = {k: round(s, 3) for k, s in top[:5]}
        v["clip_v"] = CLIP_VERSION
        v["tema"] = top[0][0]
        v["etiquetas"] = sorted(set(v.get("etiquetas", [])) | set(auto))
        hechos += 1
    print(f"[banco] etiquetadas con CLIP: {hechos}")
    return hechos


def personajes(ind: dict) -> list[str]:
    """Copia la mejor foto oficial de Lucía, de Jason y de los dos a media/oficial/ (para recortes y escenas 'foto')."""
    rutas.OFICIAL.mkdir(parents=True, exist_ok=True)
    hechos = []

    def score(v, k):
        return (v.get("clip") or {}).get(k, 0) + (0.5 if k in _etiquetas_texto(v.get("url", ""), v.get("alt", "")) else 0)

    ofi = [v for v in ind.values() if v["fuente"] == "oficial"]
    for nombre, quiere, evita in [("lucia", "lucia", "jason"), ("jason", "jason", "lucia")]:
        cands = sorted((v for v in ofi if quiere in v["etiquetas"] and evita not in v["etiquetas"]), key=lambda v: -score(v, quiere))
        if cands:
            dst = rutas.OFICIAL / f"{nombre}.jpg"
            if not dst.exists():
                dst.write_bytes((BANCO / cands[0]["archivo"]).read_bytes())
                hechos.append(dst.name)
    pares = sorted(
        (v for v in ofi if {"lucia", "jason"} <= set(v["etiquetas"]) or "pareja" in v["etiquetas"]), key=lambda v: -score(v, "pareja")
    )
    if pares and not (rutas.OFICIAL / "lucia-jason.jpg").exists():
        (rutas.OFICIAL / "lucia-jason.jpg").write_bytes((BANCO / pares[0]["archivo"]).read_bytes())
        hechos.append("lucia-jason.jpg")
    print(f"[banco] personajes: {hechos}")
    return hechos


def animar(ind: dict, maximo: int, dur: float = 3.0, parte: int = 0, partes: int = 1) -> int:
    """Clip 3D de cada imagen (alterna estilos) en media/banco/animadas/. Con partes>1 cada máquina hace su trozo."""
    from .. import escena3d

    estilos = ["inclinada", "lleno", "inclinada", "lleno", "giro"]
    hechos = 0
    for i, (iid, v) in enumerate(sorted(ind.items())):
        if hechos >= maximo:
            break
        if i % partes != parte:
            continue
        out = BANCO / "animadas" / f"{iid}.mp4"
        if out.exists():
            v["animada"] = str(out.relative_to(BANCO))
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            escena3d.clip(
                {"tipo": "foto", "imagen": str(BANCO / v["archivo"]), "estilo": estilos[i % len(estilos)], "color": "gold"},
                dur,
                out,
                crf=26,
            )
            v["animada"] = str(out.relative_to(BANCO))
            hechos += 1
        except Exception as e:
            print(f"[banco] no se anima {iid}: {e}")
    print(f"[banco] animadas: {hechos}")
    return hechos


def _tema(v: dict) -> str:
    return v.get("tema") or {"trailer": "trailer", "oficial": "oficial"}.get(v.get("categoria", ""), v.get("categoria", "otros"))


def _tabla(items: list, raiz: str = "") -> list[str]:
    """Tabla de 4 columnas con miniatura → imagen, ▶ → clip 3D. `raiz` = prefijo relativo hasta media/banco/."""
    lines, row = ["| | | | |", "|---|---|---|---|"], []
    for iid, v in items:
        clip = f" · [▶ 3D]({raiz}{v['animada']})" if v.get("animada") else ""
        et = ", ".join(v.get("etiquetas", [])[:4])
        src = "🎬 oficial" if v["fuente"] == "oficial" else "📷 libre"
        row.append(f"[![{iid}]({raiz}miniaturas/{iid}.jpg)]({raiz}{v['archivo']})<br>`{iid}` {src}{clip}<br><sub>{et}</sub>")
        if len(row) == 4:
            lines.append("| " + " | ".join(row) + " |")
            row = []
    if row:
        lines.append("| " + " | ".join(row + [""] * (4 - len(row))) + " |")
    return lines


def galeria(ind: dict) -> Path:
    """Miniaturas + carpetas por TEMA (media/banco/temas/<tema>/: imagen, clip 3D y GALERIA.md) + índice general."""
    import shutil

    mini = BANCO / "miniaturas"
    mini.mkdir(parents=True, exist_ok=True)
    por_tema: dict[str, list] = {}
    for iid, v in sorted(ind.items()):
        clip = BANCO / "animadas" / f"{iid}.mp4"
        if clip.exists():
            v["animada"] = str(clip.relative_to(BANCO))
        m = mini / f"{iid}.jpg"
        if not m.exists():
            im = Image.open(BANCO / v["archivo"]).convert("RGB")
            im.thumbnail((360, 360))
            im.save(m, "JPEG", quality=78)
        por_tema.setdefault(_tema(v), []).append((iid, v))
    # carpetas por tema (git guarda una sola copia de cada archivo idéntico: no ocupa el doble)
    temas_dir = BANCO / "temas"
    if temas_dir.exists():
        shutil.rmtree(temas_dir)
    for tema, items in por_tema.items():
        d = temas_dir / tema
        d.mkdir(parents=True, exist_ok=True)
        for iid, v in items:
            shutil.copy2(BANCO / v["archivo"], d / f"{iid}.jpg")
            if v.get("animada"):
                shutil.copy2(BANCO / v["animada"], d / f"{iid}.mp4")
        (d / "GALERIA.md").write_text(
            "\n".join([f"# Tema: {tema} ({len(items)})", "", "[← todas las carpetas](../../GALERIA.md)", "", *_tabla(items, "../../")])
            + "\n",
            encoding="utf-8",
        )
    n_anim = sum(1 for v in ind.values() if v.get("animada"))
    lines = [
        "# Banco de imágenes de TOMMY",
        "",
        f"**{len(ind)} imágenes** · **{n_anim} animadas en 3D** · **{len(por_tema)} carpetas por tema**. "
        "Cada carpeta (`media/banco/temas/<tema>/`) tiene las fotos (.jpg) y sus clips 3D (.mp4, 1080x1920, 3 s) listos para editar.",
        "",
        "En un guion: `{kind: 3d, tipo: foto, banco: <tema>, estilo: lleno|inclinada|giro}` o `imagen: media/banco/temas/<tema>/<id>.jpg`.",
        "Créditos: 🎬 oficiales → «Rockstar Games»; 📷 libres → autor y licencia en `indice-libres.json` (van solos a publicacion.md).",
        "",
        "| Carpeta | Imágenes | Clips 3D | Muestra |",
        "|---|---|---|---|",
    ]
    for tema, items in sorted(por_tema.items(), key=lambda x: -len(x[1])):
        muestra = " ".join(f"![{i}](miniaturas/{i}.jpg)" for i, _ in items[:3])
        anim = sum(1 for _, v in items if v.get("animada"))
        lines.append(f"| [{tema}](temas/{tema}/GALERIA.md) | {len(items)} | {anim} | {muestra} |")
    out = BANCO / "GALERIA.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def buscar(etiqueta: str, fuente: str | None = None) -> list[Path]:
    """Imágenes del banco con esa etiqueta (para Tommy y para los guiones)."""
    ind = cargar()
    return [
        BANCO / v["archivo"]
        for v in ind.values()
        if (etiqueta in v.get("etiquetas", []) or etiqueta == v.get("tema")) and (fuente is None or v["fuente"] == fuente)
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="clipfactory.banco")
    ap.add_argument("paso", choices=["oficial", "libres", "trailers", "descargar", "etiquetar", "animar", "galeria", "todo"])
    ap.add_argument("--max", type=int, default=1000)
    ap.add_argument("--parte", type=int, default=0)
    ap.add_argument("--partes", type=int, default=1)
    a = ap.parse_args(argv)
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    ind = cargar()
    if a.paso in ("oficial", "descargar", "todo"):
        descargar_oficial(cfg, ind, a.max)
        guardar(ind, ("oficial",))
    if a.paso in ("libres", "descargar", "todo"):
        descargar_libres(cfg, ind, a.max)
        guardar(ind, ("libres",))
    if a.paso in ("trailers", "todo"):
        trailers(cfg, ind, a.max)
        guardar(ind, ("trailers",))
    if a.paso in ("oficial", "libres", "trailers"):
        return 0
    if a.paso in ("etiquetar", "todo"):
        etiquetar(ind)
        guardar(ind)
        personajes(ind)
    if a.paso in ("animar", "todo"):
        animar(ind, a.max, parte=a.parte, partes=a.partes)
        if a.partes > 1:  # en paralelo no se toca el índice (lo rehace el paso final)
            return 0
        guardar(ind)
    galeria(ind)
    guardar(ind)
    print(f"[banco] total {len(ind)} imágenes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
