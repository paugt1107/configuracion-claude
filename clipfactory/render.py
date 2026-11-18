"""Render de un Short/TikTok vertical (1080x1920) desde un job YAML.

Capas: fondo desenfocado o recorte centrado → vídeo → gancho (primeros segundos) → crédito →
subtítulos palabra a palabra → audio (voz propia con el original atenuado por ducking) → -14 LUFS.
Antes de renderizar valida la política de la fuente (sources.check_segment).
"""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
from pathlib import Path

import yaml

from . import captions, media, sources
from .words import load_words, shift_window

W, H = 1080, 1920


def _filter_path(p: Path) -> str:
    return str(p).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def balanced_wrap(text: str, max_width: int = 18, max_lines: int = 3) -> str:
    """Reparte el texto en líneas de longitud parecida (evita palabras huérfanas)."""
    best, best_cost = None, None
    for width in range(8, max_width + 1):
        lines = textwrap.wrap(text, width=width)
        if not lines or len(lines) > max_lines:
            continue
        lens = [len(l) for l in lines]
        cost = (len(lines), max(lens) - min(lens)) if len(lines) > 1 else (1, 0)
        if best_cost is None or cost < best_cost:
            best, best_cost = lines, cost
    return "\n".join(best or textwrap.wrap(text, width=max_width))


def load_job(path: str | Path) -> dict:
    job = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    for k in ("id", "fuente", "inicio", "fin", "salida"):
        if k not in job:
            raise ValueError(f"El job {path} no tiene el campo obligatorio '{k}'.")
    return job


def build_command(job: dict, src: sources.Source, workdir: Path) -> list[str]:
    start, end = float(job["inicio"]), float(job["fin"])
    dur = end - start
    in_path = src.archivo or job.get("archivo_fuente")
    if not in_path or not Path(in_path).exists():
        raise FileNotFoundError(f"No encuentro el archivo de la fuente '{src.id}' ({in_path}). Descárgalo o indica 'archivo'.")
    voice = job.get("voz")
    if voice and not Path(voice).exists():
        raise FileNotFoundError(f"No existe la voz {voice}")
    commentary_s = media.duration(voice) if voice else 0.0
    sources.check_segment(src, start, end, commentary_s=min(commentary_s, dur))

    font = media.find_font()
    layout = job.get("layout", "blur")
    hook = (job.get("gancho") or "").strip()
    hook_s = float(job.get("gancho_segundos", 2.5))
    credit = (src.credito or "").strip() if src.tipo != "propia" else (job.get("credito") or "").strip()

    # Subtítulos
    sub_mode = job.get("subtitulos", "voz" if voice else "original")
    words: list[dict] = []
    if sub_mode == "voz" and job.get("palabras_voz"):
        words = [w for w in load_words(job["palabras_voz"]) if w["start"] < dur]
    elif sub_mode == "original" and job.get("palabras_original"):
        words = shift_window(load_words(job["palabras_original"]), start, end)
    ass_path = None
    if words:
        ass_path = workdir / "subs.ass"
        ass_path.write_text(captions.build_ass(words, font=job.get("fuente_subtitulos", "Inter")), encoding="utf-8")

    vf = []
    if layout == "crop":
        x = float(job.get("crop_x", 0.5))
        vf.append(f"[0:v]scale=-2:{H},crop={W}:{H}:(iw-{W})*{x:.3f}:0,setsar=1[base]")
    else:
        vf.append(
            f"[0:v]split=2[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"boxblur=28:4,eq=brightness=-0.12[bg];[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[base]"
        )
    last = "base"
    fontopt = f"fontfile='{_filter_path(Path(font))}':" if font else ""
    if hook:
        hf = workdir / "hook.txt"
        hf.write_text(balanced_wrap(hook.upper(), int(job.get("gancho_ancho", 18))), encoding="utf-8")
        vf.append(
            f"[{last}]drawtext={fontopt}textfile='{_filter_path(hf)}':fontsize={int(job.get('gancho_tamano', 84))}:"
            f"fontcolor=white:line_spacing=12:text_align=C:box=1:boxcolor=black@0.6:boxborderw=26:"
            f"x=(w-text_w)/2:y=h*0.27:enable='between(t,0,{hook_s})'[hk]"
        )
        last = "hk"
    if credit:
        cf = workdir / "credit.txt"
        cf.write_text(credit, encoding="utf-8")
        vf.append(
            f"[{last}]drawtext={fontopt}textfile='{_filter_path(cf)}':fontsize=38:fontcolor=white@0.9:"
            f"box=1:boxcolor=black@0.45:boxborderw=12:x=(w-text_w)/2:y=h*0.21[cr]"
        )
        last = "cr"
    if ass_path:
        vf.append(f"[{last}]subtitles='{_filter_path(ass_path)}'[sb]")
        last = "sb"
    vf.append(f"[{last}]fps=30,format=yuv420p[vout]")

    af = []
    src_audio = media.has_audio(in_path) and not job.get("silenciar_original", False)
    vol = float(job.get("volumen_original", 0.25 if voice else 1.0))
    if voice and src_audio:
        af.append(
            f"[0:a]volume={vol}[orig];[1:a]asplit=2[vo][key];[orig][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[duck];"
            f"[duck][vo]amix=inputs=2:duration=longest:normalize=0[mix];[mix]loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
        )
    elif voice:
        af.append("[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    elif src_audio:
        af.append(f"[0:a]volume={vol},loudnorm=I=-14:TP=-1.5:LRA=11[aout]")

    cmd = [media.require("ffmpeg"), "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{start}", "-to", f"{end}", "-i", in_path]
    if voice:
        cmd += ["-i", voice]
    cmd += ["-filter_complex", ";".join(vf + af), "-map", "[vout]"]
    if af:
        cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    cmd += [
        "-t",
        f"{dur}",
        "-c:v",
        "libx264",
        "-preset",
        job.get("preset", "veryfast"),
        "-crf",
        str(job.get("crf", 20)),
        "-movflags",
        "+faststart",
        str(job["salida"]),
    ]
    return cmd


def render(job_path: str | Path, registry: str | Path = sources.DEFAULT_REGISTRY, dry_run: bool = False) -> str:
    job = load_job(job_path)
    src = sources.get_source(job["fuente"], registry)
    Path(job["salida"]).parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="clipfactory-") as tmp:
        cmd = build_command(job, src, Path(tmp))
        if dry_run:
            return " ".join(cmd)
        subprocess.run(cmd, check=True)
    w, h = media.video_size(job["salida"])
    if (w, h) != (W, H):
        raise RuntimeError(f"Salida con tamaño inesperado {w}x{h}")
    return str(job["salida"])
