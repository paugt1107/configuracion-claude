"""Subtítulos ASS palabra a palabra (palabra activa resaltada) para vídeo vertical 1080x1920.

Zona segura: se evita el 20 % superior y el 25 % inferior (UI de Shorts/TikTok).
"""
from __future__ import annotations

PUNCT_END = (".", "?", "!", "…", ":", ";")


def _ass_time(t: float) -> str:
    cs = int(round(max(0.0, t) * 100))
    h, cs = divmod(cs, 360_000)
    m, cs = divmod(cs, 6_000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _hex_to_ass(color: str) -> str:
    c = color.lstrip("#")
    r, g, b = c[0:2], c[2:4], c[4:6]
    return f"&H00{b}{g}{r}".upper()


def _escape(text: str) -> str:
    return text.replace("\\", "").replace("{", "(").replace("}", ")")


def chunk_words(words: list[dict], max_words: int = 3, max_gap: float = 0.6) -> list[list[dict]]:
    """Agrupa palabras en bloques cortos: corta por número, pausa larga o fin de frase."""
    chunks: list[list[dict]] = []
    cur: list[dict] = []
    for w in words:
        if cur and (len(cur) >= max_words or w["start"] - cur[-1]["end"] > max_gap or cur[-1]["text"].endswith(PUNCT_END)):
            chunks.append(cur)
            cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


def build_ass(
    words: list[dict],
    width: int = 1080,
    height: int = 1920,
    font: str = "Inter",
    size: int = 88,
    base_color: str = "#FFFFFF",
    active_color: str = "#FF7A1A",
    margin_v: int | None = None,
    uppercase: bool = True,
    max_words: int = 3,
    pop: bool = True,
) -> str:
    if margin_v is None:
        margin_v = int(height * 0.30)  # por encima del 25 % inferior reservado a la UI
    base, active = _hex_to_ass(base_color), _hex_to_ass(active_color)
    header = (
        "[Script Info]\nScriptType: v4.00+\nWrapStyle: 0\nScaledBorderAndShadow: yes\n"
        f"PlayResX: {width}\nPlayResY: {height}\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Cap,{font},{size},{base},{active},&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,2,2,90,90,{margin_v},1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    events = []
    for chunk in chunk_words(words, max_words=max_words):
        texts = [_escape(w["text"].upper() if uppercase else w["text"]) for w in chunk]
        for i, w in enumerate(chunk):
            start = w["start"]
            end = chunk[i + 1]["start"] if i + 1 < len(chunk) else max(w["end"], start + 0.05)
            on = (f"{{\\c{active}\\fscx122\\fscy122\\t(0,110,\\fscx100\\fscy100)}}" if pop else f"{{\\c{active}}}")
            parts = [f"{on}{t}{{\\c{base}\\fscx100\\fscy100}}" if j == i else t for j, t in enumerate(texts)]
            events.append(f"Dialogue: 0,{_ass_time(start)},{_ass_time(end)},Cap,,0,0,0,,{' '.join(parts)}")
    return header + "\n".join(events) + "\n"
