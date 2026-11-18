"""SONIDO · Música REAL y gratis para la cama musical: temas de Kevin MacLeod (incompetech.com), licencia CC BY 4.0.

Se elige por AMBIENTE (misterio, accion, epico, tension, tranquilo, retro) — el guion puede pedirlo con `musica: misterio`;
con `musica: true` se elige solo según el formato (guía → accion, sabías-que → misterio). El crédito obligatorio se añade
SOLO a la descripción (publicacion.md). Si no se puede bajar, se usa la cama sintetizada de sfx.pad (nunca falla).
Los archivos se guardan en media/musica/ (en Actions, con caché).
"""

from __future__ import annotations

import hashlib
import re
import urllib.parse
import urllib.request
from pathlib import Path

from . import rutas

CARPETA = rutas.MEDIA / "musica"
BASE = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/{}.mp3"
CATALOGO: dict[str, list[str]] = {
    "misterio": ["Investigations", "The Complex", "Cipher", "Darkling", "Spy Glass"],
    "accion": ["Hitman", "Volatile Reaction", "Mistake the Getaway", "Movement Proposition"],
    "tension": ["Sneaky Snitch", "Crypto", "Night Vigil", "Dark Fog"],
    "epico": ["Five Armies", "Heroic Age", "Strength of the Titans"],
    "tranquilo": ["Wallpaper", "Carefree", "Local Forecast - Elevator"],
    "retro": ["Ouroboros", "Cyborg Ninja", "Voltaic"],
}
POR_FORMATO = {"guia": "accion", "sabias-que": "misterio", "secreto": "tension", "historia": "epico"}


def credito(titulo: str) -> str:
    return f'Música: "{titulo}" Kevin MacLeod (incompetech.com) · Licencia Creative Commons: By Attribution 4.0 · http://creativecommons.org/licenses/by/4.0/'


def ambiente(spec: dict) -> str | None:
    m = spec.get("musica", True)
    if m is False:
        return None
    if isinstance(m, str) and m in CATALOGO:
        return m
    return POR_FORMATO.get(spec.get("formato", ""), "misterio")


def elegir(amb: str, semilla: str) -> list[str]:
    """Temas del ambiente, empezando por uno distinto según el vídeo (para que no suene siempre igual)."""
    lista = CATALOGO[amb]
    k = int(hashlib.sha1(semilla.encode()).hexdigest(), 16) % len(lista)
    return lista[k:] + lista[:k]


def bajar(titulo: str) -> Path | None:
    CARPETA.mkdir(parents=True, exist_ok=True)
    dst = CARPETA / (re.sub(r"[^a-z0-9]+", "-", titulo.lower()).strip("-") + ".mp3")
    if dst.exists() and dst.stat().st_size > 100_000:
        return dst
    try:
        req = urllib.request.Request(BASE.format(urllib.parse.quote(titulo)), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        if len(data) < 100_000 or not (data[:3] == b"ID3" or data[:2] == b"\xff\xfb"):
            return None
        dst.write_bytes(data)
        return dst
    except Exception:
        return None


def pista(spec: dict) -> tuple[Path, str] | None:
    """(archivo mp3, crédito) para este guion, o None (→ cama sintetizada)."""
    amb = ambiente(spec)
    if not amb:
        return None
    for titulo in elegir(amb, str(spec.get("id", ""))):
        p = bajar(titulo)
        if p:
            return p, credito(titulo)
    return None
