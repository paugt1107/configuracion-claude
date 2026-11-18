"""Voz en off gratuita con edge-tts (voces neuronales de Microsoft) + marcas de tiempo por palabra.

Requiere: pip install edge-tts  (y acceso de red al servicio). Voces útiles:
  es-ES-AlvaroNeural, es-ES-ElviraNeural, es-MX-JorgeNeural, es-MX-DaliaNeural
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from .words import save_words


async def _synth(text: str, voice: str, rate: str, out_audio: Path) -> list[dict]:
    try:
        import edge_tts
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("Falta edge-tts: pip install edge-tts") from e
    try:
        comm = edge_tts.Communicate(text, voice=voice, rate=rate, boundary="WordBoundary")
    except TypeError:  # versiones antiguas
        comm = edge_tts.Communicate(text, voice=voice, rate=rate)
    words: list[dict] = []
    with open(out_audio, "wb") as fh:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                fh.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7
                words.append({"text": chunk["text"], "start": start, "end": start + chunk["duration"] / 1e7})
    return words


def synthesize(text: str, out_audio: str | Path, voice: str = "es-ES-AlvaroNeural", rate: str = "+8%") -> Path:
    out_audio = Path(out_audio)
    out_audio.parent.mkdir(parents=True, exist_ok=True)
    words = asyncio.run(_synth(text, voice, rate, out_audio))
    words_path = out_audio.with_suffix(".words.json")
    save_words(words, words_path)
    return words_path
