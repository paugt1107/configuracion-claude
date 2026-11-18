"""Descarga SOLO fuentes registradas y autorizadas (yt-dlp). Nunca descarga una URL suelta."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from . import sources


def download(source_id: str, out_dir: str | Path = "media", registry: str | Path = sources.DEFAULT_REGISTRY) -> Path:
    src = sources.get_source(source_id, registry)  # valida la política
    if src.archivo and Path(src.archivo).exists():
        return Path(src.archivo)
    if not src.url:
        raise sources.PolicyError(f"La fuente '{source_id}' no tiene url ni archivo local.")
    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        raise RuntimeError("Falta yt-dlp: pip install yt-dlp")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{source_id}.mp4"
    subprocess.run([ytdlp, "--no-playlist", "-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4",
                    "-o", str(target), src.url], check=True)
    return target
