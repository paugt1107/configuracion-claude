"""Candidatos a clip a partir de una transcripción con marcas de tiempo por palabra.

Heurística (inspirada en los clippers open source revisados: cortes en límites de frase y pausas,
momentos autónomos de 15-60 s). La herramienta PROPONE; el agente `editor` elige y el `guionista`
escribe el gancho. No sustituye al criterio humano.
"""

from __future__ import annotations

import re

HOOK_WORDS = {
    # español
    "nadie",
    "nunca",
    "secreto",
    "oculto",
    "por qué",
    "cómo",
    "nadie sabe",
    "primera vez",
    "increíble",
    "mira",
    "ojo",
    "atención",
    "error",
    "truco",
    "imposible",
    "real",
    "verdad",
    "mentira",
    "récord",
    "el mejor",
    "el peor",
    "lo que",
    "no sabías",
    "fíjate",
    "cuidado",
    # inglés (fuentes en inglés)
    "nobody",
    "never",
    "secret",
    "hidden",
    "why",
    "how",
    "first time",
    "insane",
    "look",
    "mistake",
    "trick",
    "impossible",
    "truth",
    "record",
    "best",
    "worst",
    "you didn't know",
}
WEAK_STARTS = {"y", "pero", "entonces", "pues", "o", "así", "and", "but", "so", "then", "or", "because", "porque"}
END_PUNCT = (".", "?", "!", "…")


def sentences(words: list[dict], gap: float = 0.7) -> list[list[dict]]:
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if w["text"].endswith(END_PUNCT) or (nxt and nxt["start"] - w["end"] > gap) or nxt is None:
            out.append(cur)
            cur = []
    return out


def _text(ws: list[dict]) -> str:
    return " ".join(w["text"] for w in ws)


def score_window(sents: list[list[dict]]) -> tuple[float, list[str]]:
    first = _text(sents[0]).lower()
    full = " ".join(_text(s) for s in sents).lower()
    start, end = sents[0][0]["start"], sents[-1][-1]["end"]
    dur = max(end - start, 0.1)
    n_words = sum(len(s) for s in sents)
    reasons, score = [], 0.0
    hooks = [h for h in HOOK_WORDS if re.search(rf"\b{re.escape(h)}\b", first)]
    if hooks:
        score += 2.0 + 0.5 * min(len(hooks), 3)
        reasons.append(f"gancho en la 1.ª frase ({', '.join(sorted(hooks)[:3])})")
    if "?" in first or first.startswith(("¿", "qué", "por qué", "cómo", "what", "why", "how")):
        score += 1.5
        reasons.append("abre con pregunta")
    if re.search(r"\d", first):
        score += 1.0
        reasons.append("número/dato en la 1.ª frase")
    first_word = re.sub(r"[^\wáéíóúñü]", "", sents[0][0]["text"].lower())
    if first_word in WEAK_STARTS:
        score -= 2.0
        reasons.append("empieza con conector (depende de contexto previo)")
    if sents[-1][-1]["text"].endswith(END_PUNCT):
        score += 1.0
        reasons.append("termina en frase completa")
    wps = n_words / dur
    if wps >= 2.3:
        score += 1.0
        reasons.append(f"ritmo alto ({wps:.1f} pal/s)")
    elif wps < 1.4:
        score -= 1.0
        reasons.append(f"ritmo lento ({wps:.1f} pal/s)")
    if "!" in full:
        score += 0.5
    return score, reasons


def candidates(words: list[dict], min_s: float = 20.0, max_s: float = 55.0, top: int = 5) -> list[dict]:
    sents = sentences(words)
    found = []
    for i in range(len(sents)):
        for j in range(i, len(sents)):
            start, end = sents[i][0]["start"], sents[j][-1]["end"]
            dur = end - start
            if dur > max_s:
                break
            if dur >= min_s:
                sc, why = score_window(sents[i : j + 1])
                found.append(
                    {
                        "inicio": round(max(0.0, start - 0.15), 2),
                        "fin": round(end + 0.25, 2),
                        "duracion": round(dur, 1),
                        "puntuacion": round(sc, 2),
                        "primera_frase": _text(sents[i]),
                        "ultima_frase": _text(sents[j]),
                        "motivos": why,
                    }
                )
    found.sort(key=lambda c: (-c["puntuacion"], c["inicio"]))
    chosen: list[dict] = []
    for c in found:
        if all(c["fin"] <= o["inicio"] or c["inicio"] >= o["fin"] for o in chosen):
            chosen.append(c)
        if len(chosen) >= top:
            break
    return chosen
