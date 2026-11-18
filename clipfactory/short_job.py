"""Producción completa de un Short desde un guion YAML (canal-youtube/guiones/<ID>.yaml):
voz IA frase a frase → escenas sincronizadas → efectos + música → vídeo 1080x1920 → 3 portadas → publicacion.md.
Todo queda en entregas/<ID>/. Ver canal-youtube/guiones/PLANTILLA.yaml.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from . import hookscore_es, motion, rutas, sfx, thumbs, voice

TAGS_BASE = ["#gta6", "#gtavi", "#gta6espanol", "#sabiasque", "#shorts"]


def title_checks(title: str, cover_text: str) -> list[str]:
    notes = []
    if len(title) > 60:
        notes.append(f"{len(title)} caracteres (>60, se corta)")
    if len(title) > 40:
        notes.append("en móvil se ven ~40 caracteres: lo importante al principio")
    if not re.search(r"gta ?(6|vi)", title, re.I):
        notes.append("falta 'GTA 6' (lo que busca la gente)")
    shared = {w for w in re.findall(r"\w{4,}", cover_text.lower())} & {w for w in re.findall(r"\w{4,}", title.lower())}
    if shared:
        notes.append(f"la portada repite palabras del título: {', '.join(sorted(shared))}")
    return notes or ["ok"]


def publication(spec: dict, lines: list[str], provider: str) -> str:
    cover = (spec.get("portada") or {}).get("texto", "")
    hook = hookscore_es.score(lines[0])
    out = [
        f"# Publicación {spec['id']}",
        "",
        f"Gancho (frase 1): «{lines[0]}» → {hook['veredicto']} {hook['banda']} ({hook['mejora']})",
        "",
        "## Títulos (elige uno)",
    ]
    for t in spec.get("titulos", []):
        out.append(f"- **{t}** — {'; '.join(title_checks(t, cover))}")
    tags = TAGS_BASE + spec.get("hashtags", [])
    fuentes = spec.get("fuentes", [])
    desc = spec.get("descripcion", "").strip()
    out += [
        "",
        "## Descripción YouTube (copiar)",
        "```",
        desc,
        "",
        "Fuentes:" if fuentes else "",
        *[f"- {f}" for f in fuentes],
        *([spec["creditos"]] if spec.get("creditos") else []),
        "Voz generada con IA.",
        " ".join(tags[:5]),
        "```",
        "",
        "## TikTok (copiar)",
        "```",
        f"{lines[0]} {' '.join(tags[:5])}",
        "```",
        "",
        "## Instagram Reels (copiar)",
        "```",
        f"{lines[0]}\n\n{desc[:180]}\n\n{' '.join(tags[:5])} #reels",
        "```",
        "",
        "## Comentario fijado",
        spec.get("comentario", "¿Lo sabías? Te leo 👇"),
        "",
        "## Al subir",
        "- Marca **contenido alterado o sintético** si la plataforma lo pide (voz IA).",
        "- Portada: `portada-1.png` / `-2` / `-3` (elige la que más destaque en pequeño).",
        f"- Voz: {provider}. Revisa el vídeo entero antes de publicar.",
    ]
    return "\n".join(out) + "\n"


def produce(spec_path: str | Path, provider: str = "auto", out_root: str | Path = rutas.ENTREGAS) -> Path:
    spec = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))
    sid = spec["id"]
    escenas = spec["escenas"]
    lines = [e["texto"].strip() for e in escenas]
    out_dir = Path(out_root) / sid
    out_dir.mkdir(parents=True, exist_ok=True)
    work = rutas.TRABAJO / f"{sid}-voz"
    v = voice.produce(lines, work, provider=provider)
    spans = v["lines"]
    starts = [0.0] + [s["start"] - 0.08 for s in spans[1:]]
    end = spans[-1]["end"] + 0.6
    scenes = []
    for i, e in enumerate(escenas):
        sc = dict(e.get("tarjeta") or {"kind": "dato", "grande": "?"})
        sc["dur"] = round((starts[i + 1] if i + 1 < len(starts) else end) - starts[i], 3)
        scenes.append(sc)
    cues = [(0.0, "impacto")] + [(s - 0.12, "whoosh") for s in starts[1:]] + [(starts[-1], "impacto")]
    mixed = sfx.mix(v["audio"], cues, work / "mezcla.wav", music=spec.get("musica", True))
    video = motion.build(scenes, v["words"], out_dir / f"{sid}-final.mp4", str(mixed), premixed=True)
    if spec.get("portada"):
        thumbs.make_covers(spec["portada"], out_dir)
    (out_dir / "publicacion.md").write_text(publication(spec, lines, v["provider"]), encoding="utf-8")
    return video
