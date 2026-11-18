"""IRENE · Control de calidad automático de cada vídeo producido → entregas/<ID>/control-calidad.md (APTO / REVISAR)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from . import hookscore_es, media, rutas


def _ffmpeg_stats(video: str) -> dict:
    r = subprocess.run(
        [
            media.require("ffmpeg"),
            "-hide_banner",
            "-i",
            video,
            "-vf",
            "blackdetect=d=0.5:pix_th=0.08",
            "-af",
            "ebur128,silencedetect=noise=-45dB:d=1.2",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    err = r.stderr
    lufs = re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", err, re.M)
    return {
        "negros": len(re.findall(r"black_start", err)),
        "silencios": len(re.findall(r"silence_start", err)),
        "lufs": float(lufs[-1]) if lufs else None,
    }


def comprobar(video: str | Path, spec: dict, lines: list[str], overlays: list[dict]) -> list[tuple[bool, str]]:
    n3d = sum(1 for e in spec.get("escenas") or [] if (e.get("tarjeta") or {}).get("kind") == "3d")
    video = str(video)
    w, h = media.video_size(video)
    dur = media.duration(video)
    st = _ffmpeg_stats(video)
    hook = hookscore_es.score(lines[0])
    words = sum(len(x.split()) for x in lines)
    checks = [
        ((w, h) == (1080, 1920), f"Formato vertical 1080x1920 ({w}x{h})"),
        (15 <= dur <= 60, f"Duración 15-60 s ({dur:.1f} s)"),
        (media.has_audio(video), "Tiene audio"),
        (st["lufs"] is not None and -16.5 <= st["lufs"] <= -12.0, f"Volumen ≈ -14 LUFS ({st['lufs']})"),
        (st["negros"] == 0, f"Sin pantallas negras ({st['negros']})"),
        (st["silencios"] == 0, f"Sin silencios largos ({st['silencios']})"),
        (hook["veredicto"] >= 55, f"Gancho ≥ 55 ({hook['veredicto']} {hook['banda']})"),
        (90 <= words <= 140, f"Guion 90-140 palabras ({words})"),
        (
            len(overlays) + n3d >= max(2, int(dur // 10)),
            f"Imágenes al nombrar cosas o escenas 3D ≥ 1 cada 10 s ({len(overlays)} + {n3d} 3D)",
        ),
        (len(spec.get("titulos", [])) >= 3, f"3 títulos propuestos ({len(spec.get('titulos', []))})"),
        (bool(spec.get("portada")), "Portada definida"),
        (bool(spec.get("fuentes")), "Fuentes citadas"),
    ]
    rep = gancho_repetido(lines[0], spec.get("id", ""))
    checks.append(
        (
            rep is None,
            "Gancho nuevo (no se parece a otro del canal)" if rep is None else f"Gancho demasiado parecido al de {rep[0]} ({rep[1]:.0%})",
        )
    )
    return checks


VACIAS = {
    "sabias",
    "que",
    "gta",
    "seis",
    "6",
    "el",
    "la",
    "los",
    "las",
    "de",
    "del",
    "en",
    "y",
    "a",
    "un",
    "una",
    "tu",
    "te",
    "es",
    "lo",
    "se",
    "por",
    "con",
    "no",
    "mas",
}


def _bolsa(t: str) -> set[str]:
    import unicodedata

    t = "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")
    return {w for w in re.findall(r"[a-z0-9]+", t) if w not in VACIAS and len(w) > 2}


def gancho_repetido(gancho: str, propio: str = "", umbral: float = 0.5) -> tuple[str, float] | None:
    """¿Se parece este gancho a otro ya escrito? (Jaccard de palabras con significado). Devuelve (ID, parecido) o None."""
    import yaml

    a = _bolsa(gancho)
    peor = None
    for g in sorted(rutas.GUIONES.glob("S[0-9]*.yaml")):
        if g.stem == propio:
            continue
        esc = (yaml.safe_load(g.read_text(encoding="utf-8")) or {}).get("escenas") or []
        if not esc:
            continue
        b = _bolsa(esc[0].get("texto", ""))
        if not a or not b:
            continue
        j = len(a & b) / len(a | b)
        if j >= umbral and (peor is None or j > peor[1]):
            peor = (g.stem, j)
    return peor


def informe(video, spec, lines, overlays, out: Path) -> bool:
    checks = comprobar(video, spec, lines, overlays)
    ok = all(c for c, _ in checks)
    body = [f"# Control de calidad {spec['id']} · {'✅ APTO' if ok else '⚠️ REVISAR'}", ""]
    body += [f"- {'✅' if c else '⚠️'} {msg}" for c, msg in checks]
    if overlays:
        body += ["", "Imágenes que aparecen: " + ", ".join(f"{o['palabra']} ({o['t']:.1f}s)" for o in overlays)]
    out.write_text("\n".join(body) + "\n", encoding="utf-8")
    return ok
