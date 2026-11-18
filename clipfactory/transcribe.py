"""Transcripción local con faster-whisper (marcas de tiempo por palabra). pip install faster-whisper"""
from __future__ import annotations

from pathlib import Path

from .words import save_words, to_srt


def transcribe(media_path: str, out_base: str | Path, model: str = "small", language: str | None = "es") -> Path:
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("Falta faster-whisper: pip install faster-whisper") from e
    wm = WhisperModel(model, device="auto", compute_type="int8")
    segments, _info = wm.transcribe(media_path, language=language, word_timestamps=True, vad_filter=True)
    words = [{"text": w.word.strip(), "start": float(w.start), "end": float(w.end)}
             for seg in segments for w in (seg.words or []) if w.word.strip()]
    out_base = Path(out_base)
    words_path = out_base.with_suffix(".words.json")
    save_words(words, words_path)
    out_base.with_suffix(".srt").write_text(to_srt(words), encoding="utf-8")
    return words_path
