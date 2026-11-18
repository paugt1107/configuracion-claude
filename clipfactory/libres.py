"""Imágenes con licencia libre de Wikimedia Commons (CC0, dominio público, CC BY, CC BY-SA) para lugares y objetos REALES
(p. ej. Miami para "vida real vs GTA"). Siempre con atribución: autor, licencia y enlace (se añade a publicacion.md)."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from . import rutas

API = "https://commons.wikimedia.org/w/api.php"
UA = "clipfactory/0.2 (canal de curiosidades; uso con atribucion)"
OK_LICENSES = re.compile(r"^(cc0|public domain|pd|cc by(-sa)? [\d.]+)", re.I)
CARPETA = rutas.MEDIA / "libres"


def _abrir(url: str, timeout: int = 60) -> bytes:
    """GET con pausa entre llamadas y reintentos si Commons pide calma (HTTP 429/503)."""
    import time
    import urllib.error

    for intento in range(6):
        time.sleep(1.2)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or intento == 5:
                raise
            espera = int(e.headers.get("Retry-After") or 0) or 10 * 2**intento
            time.sleep(min(espera, 120))
    raise RuntimeError("sin respuesta")


def _get(params: dict) -> dict:
    return json.loads(_abrir(API + "?" + urllib.parse.urlencode(params), timeout=30))


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def creditos() -> dict:
    p = CARPETA / "creditos.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def buscar(consulta: str) -> tuple[Path, str] | None:
    """Descarga (una vez) la mejor imagen libre para la consulta. Devuelve (ruta, crédito) o None."""
    CARPETA.mkdir(parents=True, exist_ok=True)
    dst = CARPETA / f"{slug(consulta)}.jpg"
    cred = creditos()
    if dst.exists() and dst.name in cred:
        return dst, cred[dst.name]
    data = _get(
        {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {consulta}",
            "gsrnamespace": 6,
            "gsrlimit": 8,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": 1280,
        }
    )
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "")
        if not OK_LICENSES.match(lic) or not ii.get("thumburl"):
            continue
        artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "desconocido")).strip()
        dst.write_bytes(_abrir(ii["thumburl"]))
        credit = f"{p.get('title', '').replace('File:', '')} — {artist} — {lic} — {ii.get('descriptionurl', '')}"
        cred[dst.name] = credit
        (CARPETA / "creditos.json").write_text(json.dumps(cred, ensure_ascii=False, indent=1), encoding="utf-8")
        return dst, credit
    return None


def buscar_varias(consulta: str, n: int, carpeta: Path) -> list[tuple[Path, str, int, int]]:
    """Hasta n imágenes libres (grandes) para la consulta en `carpeta`. Devuelve [(ruta, crédito, ancho, alto)]."""
    carpeta.mkdir(parents=True, exist_ok=True)
    data = _get(
        {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {consulta}",
            "gsrnamespace": 6,
            "gsrlimit": max(10, n * 4),
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|size",
            "iiurlwidth": 1920,
        }
    )
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    out = []
    for p in pages:
        if len(out) >= n:
            break
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "")
        if not OK_LICENSES.match(lic) or not ii.get("thumburl") or ii.get("width", 0) < 900:
            continue
        dst = carpeta / f"{slug(consulta)}-{len(out) + 1}.jpg"
        artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "desconocido")).strip()
        credit = f"{p.get('title', '').replace('File:', '')} — {artist} — {lic} — {ii.get('descriptionurl', '')}"
        if not dst.exists():
            dst.write_bytes(_abrir(ii["thumburl"]))
        from PIL import Image

        with Image.open(dst) as im:
            w, h = im.size
        out.append((dst, credit, w, h))
    return out


def openverse(consulta: str, n: int, carpeta: Path) -> list[tuple[Path, str, int, int]]:
    """Fotos libres de Openverse (Flickr y otros; licencias que permiten uso comercial y modificación)."""
    carpeta.mkdir(parents=True, exist_ok=True)
    q = urllib.parse.urlencode({"q": consulta, "license_type": "commercial,modification", "page_size": max(10, n * 3), "mature": "false"})
    data = json.loads(_abrir("https://api.openverse.org/v1/images/?" + q, timeout=30))
    out = []
    for r in data.get("results", []):
        if len(out) >= n:
            break
        if (r.get("width") or 0) < 900 or not r.get("url"):
            continue
        lic = f"CC {r.get('license', '').upper()} {r.get('license_version', '')}".replace("CC CC0", "CC0").replace(
            "CC PDM", "Dominio público"
        )
        credit = f"{r.get('title', '')} — {r.get('creator', 'desconocido')} — {lic.strip()} — {r.get('foreign_landing_url', '')}"
        dst = carpeta / f"{slug(consulta)}-ov{len(out) + 1}.jpg"
        try:
            if not dst.exists():
                dst.write_bytes(_abrir(r["url"]))
            from PIL import Image

            with Image.open(dst) as im:
                im.thumbnail((1920, 1920))
                im.convert("RGB").save(dst, "JPEG", quality=86)
                w, h = im.size
        except Exception:
            dst.unlink(missing_ok=True)
            continue
        out.append((dst, credit, w, h))
    return out
