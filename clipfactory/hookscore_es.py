"""Puntuación de ganchos EN ESPAÑOL (heurística, misma lógica que yt-script/hookscore.py, que solo entiende inglés).

Cinco propiedades 0-100; veredicto = 60 % media + 40 % la más débil (un gancho se rompe por su punto flojo).
Calibrado para ganchos de Shorts/TikTok: 6-14 palabras habladas. Una nota baja = revisa; una alta NO es promesa.
    python3 -m clipfactory.hookscore_es "gancho"            # uno
    python3 -m clipfactory.hookscore_es --archivo ganchos.txt  # uno por línea, ordenados
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata

VAGUE = {
    "increible",
    "brutal",
    "locura",
    "epico",
    "alucinante",
    "impresionante",
    "mejor",
    "peor",
    "secreto",
    "definitivo",
    "loco",
    "tremendo",
    "bestial",
    "flipante",
    "top",
}
FILLER = {
    "hola",
    "chicos",
    "bienvenidos",
    "hoy",
    "video",
    "suscribete",
    "canal",
    "basicamente",
    "literalmente",
    "simplemente",
    "bueno",
    "pues",
    "vale",
}
NAMED = {"gta", "lucia", "jason", "vice", "leonida", "rockstar", "miami", "florida", "cayos", "keys", "ps5", "xbox"}
CONCRETE = re.compile(r"\b\d[\d.,]*\s?(%|k|m|x|s|h|€|\$)?|\b\d+\s?(segundos?|minutos?|horas?|dias?|semanas?|meses|años?)\b", re.I)
YOU = re.compile(
    r"\b(tu|tus|te|ti|contigo|tienes|haces|sabias|sabes|puedes|viste|has|juegas|pierdes|perderas|"
    r"mira|fijate|para|imagina|elige|haz|evita|necesitas|quieres|vas)\b",
    re.I,
)
STAKE = re.compile(
    r"\b(perder|pierdes|perderas|error|errores|cuesta|costar|arruina|riesgo|antes|nunca|evita|deja|"
    r"muere|falla|fallar|desperdicias|tirar|prohibido|cuidado|ojo|ban|baneado|multa)\b",
    re.I,
)
CURIOSITY = re.compile(
    r"\b(por que|porque|como|que|cual|hasta|pero|nadie|casi|excepto|razon|realmente|esconde|"
    r"escondido|oculto|aqui|esto|esta|mira|fijate|parece|nunca|nadie)\b",
    re.I,
)
CLOSED = re.compile(r"\b(porque|ya que|lo que significa|asi que)\b", re.I)


def norm(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def words(t: str) -> list[str]:
    return re.findall(r"[a-z0-9%$€.]+", norm(t))


def specificity(t: str) -> int:
    w = words(t)
    if not w:
        return 0
    s = 34 + len(CONCRETE.findall(norm(t))) * 22 - sum(x in VAGUE for x in w) * 16 - sum(x in FILLER for x in w) * 5
    s += min(24, 8 * sum(x in NAMED for x in w))
    s += min(12, 6 * sum(1 for x in t.split()[1:] if x[:1].isupper() and norm(x).strip(".,!?¿¡") not in NAMED))
    return max(0, min(100, s))


def address(t: str) -> int:
    n = len(YOU.findall(norm(t)))
    first = 30 if YOU.search(" ".join(norm(t).split()[:6])) else 0
    return max(0, min(100, 26 + n * 20 + first))


def stakes(t: str) -> int:
    return max(0, min(100, 22 + len(STAKE.findall(norm(t))) * 26 + (14 if CONCRETE.search(norm(t)) else 0)))


def curiosity(t: str) -> int:
    n = len(CURIOSITY.findall(norm(t)))
    q = 18 if t.strip().endswith("?") or t.strip().startswith("¿") else 0
    closed = -18 if CLOSED.search(norm(t)) else 0
    return max(0, min(100, 24 + n * 17 + q + closed))


def brevity(t: str) -> int:
    n = len(words(t))
    if n == 0:
        return 0
    if 6 <= n <= 14:
        return 100
    if n < 6:
        return max(30, 100 - (6 - n) * 14)
    return max(10, 100 - (n - 14) * 9)


PROPS = [("ESPECIFICIDAD", specificity), ("TE_HABLA", address), ("EN_JUEGO", stakes), ("CURIOSIDAD", curiosity), ("BREVEDAD", brevity)]
FIX = {
    "ESPECIFICIDAD": "cambia un adjetivo por un número, un nombre o un lugar",
    "TE_HABLA": "háblale de tú en las 6 primeras palabras",
    "EN_JUEGO": "di qué pierde si no lo ve (tiempo, dinero, la misión)",
    "CURIOSIDAD": "quita la mitad que ya responde la pregunta; deja un hueco",
    "BREVEDAD": "6-14 palabras: léelo en voz alta en menos de 3 s",
}


def score(t: str) -> dict:
    parts = {n: fn(t) for n, fn in PROPS}
    vals = list(parts.values())
    verdict = round(0.6 * sum(vals) / len(vals) + 0.4 * min(vals))
    weakest = min(parts, key=parts.get)
    return {
        "gancho": t.strip(),
        "propiedades": parts,
        "veredicto": verdict,
        "banda": "FUERTE" if verdict >= 72 else "VALE" if verdict >= 55 else "DÉBIL",
        "mejora": f"{weakest}: {FIX[weakest]}",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("gancho", nargs="?")
    p.add_argument("--archivo")
    a = p.parse_args(argv)
    if a.archivo:
        with open(a.archivo, encoding="utf-8") as fh:
            hooks = [line for line in fh.read().splitlines() if line.strip()]
    else:
        hooks = [a.gancho or ""]
    for r in sorted((score(h) for h in hooks if h.strip()), key=lambda r: -r["veredicto"]):
        props = " ".join(f"{k[:4]}={v}" for k, v in r["propiedades"].items())
        print(f"{r['veredicto']:3d} {r['banda']:6} | {r['gancho']}\n      {props} | mejora → {r['mejora']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
