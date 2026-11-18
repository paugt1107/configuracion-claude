"""Utilidades ffprobe/ffmpeg."""
from __future__ import annotations

import json
import shutil
import subprocess


def require(binary: str) -> str:
    path = shutil.which(binary)
    if not path:
        raise RuntimeError(f"No se encuentra '{binary}'. Instálalo (p. ej. 'sudo apt install ffmpeg' o 'brew install ffmpeg').")
    return path


def probe(path: str) -> dict:
    out = subprocess.run(
        [require("ffprobe"), "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def duration(path: str) -> float:
    return float(probe(path)["format"]["duration"])


def has_audio(path: str) -> bool:
    return any(s.get("codec_type") == "audio" for s in probe(path)["streams"])


def video_size(path: str) -> tuple[int, int]:
    for s in probe(path)["streams"]:
        if s.get("codec_type") == "video":
            return int(s["width"]), int(s["height"])
    raise RuntimeError(f"{path} no tiene pista de vídeo")


def find_font(preferred: tuple[str, ...] = ("Inter:bold", "DejaVu Sans:bold")) -> str | None:
    fc = shutil.which("fc-match")
    if not fc:
        return None
    for name in preferred:
        r = subprocess.run([fc, "-f", "%{file}", name], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return None
