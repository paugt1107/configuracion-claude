"""Sincroniza un texto conocido con una locución grabada SIN modelos de IA ni red.

Detecta los silencios con ffmpeg (silencedetect) y reparte las palabras del texto por el tiempo de habla real,
respetando las pausas. Precisión típica: décimas de segundo, suficiente para subtítulos palabra a palabra.
"""

from __future__ import annotations

import re
import subprocess

from . import media


def speech_ranges(audio: str, noise_db: float = -35.0, min_silence: float = 0.22) -> list[tuple[float, float]]:
    total = media.duration(audio)
    r = subprocess.run(
        [
            media.require("ffmpeg"),
            "-hide_banner",
            "-i",
            audio,
            "-af",
            f"silencedetect=noise={noise_db}dB:d={min_silence}",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    ranges, cur = [], 0.0
    for i, s in enumerate(starts):
        s = max(0.0, s)
        if s - cur > 0.08:
            ranges.append((cur, s))
        cur = ends[i] if i < len(ends) else total
    if total - cur > 0.08:
        ranges.append((cur, total))
    return ranges or [(0.0, total)]


def _at(ranges, u, start=False):
    """Tiempo real para u segundos de habla acumulada. start=True: en un borde, salta al siguiente tramo."""
    for a, b in ranges:
        length = b - a
        if (u < length - 1e-9) if start else (u <= length + 1e-9):
            return a + u
        u -= length
    return ranges[-1][1]


def auto_ranges(text: str, audio: str) -> list[tuple[float, float]]:
    """Elige la sensibilidad cuyo nº de tramos se parece más al nº de frases/pausas del texto."""
    phrases = max(1, len(re.findall(r"[.,;:?!…]+", text)))
    best, best_diff = None, None
    for noise in (-35, -32, -30, -28, -26):
        for d in (0.22, 0.3):
            r = speech_ranges(audio, noise, d)
            diff = abs(len(r) - phrases * 0.75)
            if best_diff is None or diff < best_diff:
                best, best_diff = r, diff
    return best


def align_words(text: str, audio: str, **kw) -> list[dict]:
    words = text.split()
    ranges = speech_ranges(audio, **kw) if kw else auto_ranges(text, audio)
    speech = sum(b - a for a, b in ranges)
    weights = [len(w) + 1.5 for w in words]
    total_w = sum(weights)
    out, acc = [], 0.0
    for w, wt in zip(words, weights):
        s = _at(ranges, acc / total_w * speech, start=True)
        e = _at(ranges, (acc + wt * 0.9) / total_w * speech)
        seg_end = next((b for a, b in ranges if a - 1e-6 <= s < b), ranges[-1][1])
        e = min(e, seg_end)  # una palabra nunca se queda encendida durante una pausa
        out.append({"text": w, "start": round(s, 3), "end": round(max(e, s + 0.05), 3)})
        acc += wt
    return out
