"""Formato común de palabras con marca de tiempo: [{"text": str, "start": float, "end": float}, ...]."""
from __future__ import annotations

import json
from pathlib import Path


def load_words(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    words = data["words"] if isinstance(data, dict) else data
    out = []
    for w in words:
        text = str(w.get("text", w.get("word", ""))).strip()
        if not text:
            continue
        out.append({"text": text, "start": float(w["start"]), "end": float(w["end"])})
    out.sort(key=lambda w: w["start"])
    return out


def save_words(words: list[dict], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps({"words": words}, ensure_ascii=False, indent=1), encoding="utf-8")


def shift_window(words: list[dict], start: float, end: float) -> list[dict]:
    """Palabras dentro de [start, end], con tiempos relativos a start."""
    out = []
    for w in words:
        if w["end"] <= start or w["start"] >= end:
            continue
        out.append({"text": w["text"], "start": max(0.0, w["start"] - start), "end": min(end, w["end"]) - start})
    return out


def to_srt(words: list[dict], max_words: int = 7) -> str:
    def ts(t: float) -> str:
        ms = int(round(t * 1000))
        h, ms = divmod(ms, 3_600_000)
        m, ms = divmod(ms, 60_000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines, i = [], 1
    for k in range(0, len(words), max_words):
        chunk = words[k:k + max_words]
        lines.append(f"{i}\n{ts(chunk[0]['start'])} --> {ts(chunk[-1]['end'])}\n{' '.join(w['text'] for w in chunk)}\n")
        i += 1
    return "\n".join(lines)
