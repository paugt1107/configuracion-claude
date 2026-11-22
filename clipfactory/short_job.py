"""Producción completa de un Short desde un guion YAML (canal-youtube/guiones/<ID>.yaml):
voz IA frase a frase → escenas sincronizadas → efectos + música → vídeo 1080x1920 → 3 portadas → publicacion.md.
Todo queda en entregas/<ID>/. Ver canal-youtube/guiones/PLANTILLA.yaml.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from . import calidad, hookscore_es, misterio, motion, musica, rutas, sfx, thumbs, visuales, voice

TAGS_BASE = ["#gta6", "#gtavi", "#gta6espanol", "#sabiasque", "#shorts"]


def _foto_libre(consulta: str, usadas: set):
    """Mejor foto libre para la consulta (Commons, y Openverse si falla). None si no hay ninguna nueva."""
    from . import libres

    try:
        r = libres.buscar(consulta)
        if not r:
            for p, cred, *_ in libres.openverse(consulta, 3, libres.CARPETA):
                r = (p, cred)
                break
    except Exception:
        r = None
    if r and r[1] not in usadas:  # misma foto con otro nombre de archivo = mismo crédito
        usadas.add(r[1])
        return r
    return None


def title_checks(title: str, cover_text: str, gta: bool = True) -> list[str]:
    notes = []
    if len(title) > 60:
        notes.append(f"{len(title)} caracteres (>60, se corta)")
    if len(title) > 40:
        notes.append("en móvil se ven ~40 caracteres: lo importante al principio")
    if gta and not re.search(r"gta ?(6|vi)", title, re.I):
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
        out.append(f"- **{t}** — {'; '.join(title_checks(t, cover, spec.get('juego') != 'ninguno'))}")
    if spec.get("juego") == "ninguno":
        tags = [*spec.get("hashtags", []), "#sabiasque", "#shorts"]
    else:
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
    con_misterio = spec.get("misterio", True)
    estilos = misterio.estilos(lines, escenas) if con_misterio else None
    v = voice.produce(lines, work, provider=provider, styles=estilos)
    spans = v["lines"]
    starts = [0.0] + [s["start"] - 0.08 for s in spans[1:]]
    end = spans[-1]["end"] + 0.6
    scenes, creditos_fotos, usadas = [], [], set()
    for i, e in enumerate(escenas):
        sc = dict(e.get("tarjeta") or {"kind": "dato", "grande": "?"})
        if sc.get("libre"):  # foto libre de internet (Commons/Openverse), con crédito
            for q in ([sc["libre"]] if isinstance(sc["libre"], str) else sc["libre"]):
                r = _foto_libre(q, usadas)
                if r:
                    sc["imagen"] = str(r[0])
                    creditos_fotos.append(r[1])
                    break
        sc["dur"] = round((starts[i + 1] if i + 1 < len(starts) else end) - starts[i], 3)
        scenes.append(sc)
    cues = [(0.0, "impacto")] + [(s - 0.12, "whoosh") for s in starts[1:]] + [(starts[-1], "impacto")]
    cam = misterio.plan(spans, v["words"], estilos or voice.styles_for(len(lines)), end) if con_misterio else None
    if cam:
        cues += cam["cues"]
    tema = musica.pista(spec) if spec.get("musica", True) else None
    if tema:
        spec = {**spec, "creditos": "\n".join(filter(None, [spec.get("creditos", ""), tema[1]]))}
    mixed = sfx.mix(
        v["audio"], cues, work / "mezcla.wav", music=spec.get("musica", True) is not False,
        silencios=cam["silencios"] if cam else None, pista=tema[0] if tema else None,
    )  # fmt: skip
    plan = visuales.planificar(visuales.detectar(v["words"])) if spec.get("imagenes_auto", True) else []
    # en las escenas 3D manda la animación: sin pegatinas encima (menos ruido en pantalla)
    zonas3d = [(starts[i], starts[i] + sc["dur"]) for i, sc in enumerate(scenes) if sc.get("kind") == "3d"]
    plan = [p for p in plan if not any(a <= p["t"] < b for a, b in zonas3d)]
    overlays, creditos_libres = visuales.preparar(plan, work / "pops")
    video = motion.build(
        scenes,
        v["words"],
        out_dir / f"{sid}-final.mp4",
        str(mixed),
        premixed=True,
        overlays=overlays,
        camara=misterio.filtro(cam) if cam else None,
    )
    creditos_libres = [*creditos_libres, *creditos_fotos]
    if creditos_libres:
        spec = {**spec, "creditos": "\n".join(filter(None, [spec.get("creditos", ""), *("Imagen: " + c for c in creditos_libres)]))}
    if spec.get("portada"):
        thumbs.make_covers(spec["portada"], out_dir)
    (out_dir / "publicacion.md").write_text(publication(spec, lines, v["provider"]), encoding="utf-8")
    calidad.informe(video, spec, lines, overlays, out_dir / "control-calidad.md")
    return video
