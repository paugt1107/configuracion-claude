"""VALENTÍN · Qué BUSCA la gente (no solo qué publican los medios): autocompletado de Google y de YouTube.

Para cada semilla de canal-youtube/fuentes/juego.yaml ("GTA 6 como", "GTA 6 donde", …) pide las sugerencias que salen al
escribir en Google y en YouTube (España, México y EE. UU.), las junta, cuenta en cuántos sitios aparece cada una y las
clasifica por intención (guía, ubicación, truco, dinero, personaje…). Esas frases son TÍTULOS que la gente ya está
escribiendo: Pedro las usa para elegir temas y títulos. Sin claves ni coste.
Salida: canal-youtube/datos/demanda.md (top) y demanda.json (todo, con historial para ver qué sube).
"""

from __future__ import annotations

import datetime as dt
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

from . import rutas

URL = "https://suggestqueries.google.com/complete/search?client=firefox&hl={hl}&gl={gl}&q={q}{ds}"
MERCADOS = [("es", "es", "ES"), ("es", "es-419", "MX"), ("en", "en", "US")]
INTENCION = [
    ("guía", r"\b(como|cómo|how to|pasar|beat|guia|guía|walkthrough|tutorial)\b"),
    ("ubicación", r"\b(donde|dónde|where|ubicacion|ubicación|location|encontrar|find)\b"),
    ("truco", r"\b(truco|trucos|cheat|cheats|codigo|código|glitch|bug)\b"),
    ("dinero", r"\b(dinero|money|millon|rich|rapido|rápido|fast)\b"),
    ("secreto", r"\b(secreto|secret|easter egg|oculto|hidden|misterio)\b"),
    ("personaje", r"\b(lucia|lucía|jason|personaje|character|actor|actriz)\b"),
    ("historia", r"\b(final|ending|mision|misión|mission|historia|story|capitulo|chapter)\b"),
    ("lo mejor", r"\b(mejor|best|top|rapido|fastest|mas|más)\b"),
    ("online", r"\b(online|multijugador|multiplayer)\b"),
    ("mods", r"\b(mod|mods|pc)\b"),
]
SALIDA = rutas.DATOS / "demanda.md"
HIST = rutas.DATOS / "demanda.json"


def juego(cfg_path: Path = rutas.FUENTES / "juego.yaml") -> dict:
    return yaml.safe_load(Path(cfg_path).read_text(encoding="utf-8")) or {}


def sugerencias(q: str, hl: str, gl: str, youtube: bool) -> list[str]:
    url = URL.format(hl=hl, gl=gl, q=urllib.parse.quote(q), ds="&ds=yt" if youtube else "")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    return [s for s in data[1] if isinstance(s, str)]


def intencion(frase: str) -> str:
    for nombre, pat in INTENCION:
        if re.search(pat, frase, re.I):
            return nombre
    return "otros"


def recoger(cfg: dict | None = None, pausa: float = 0.4, log=print) -> dict[str, dict]:
    cfg = cfg or juego()
    j = cfg.get("corto", "GTA 6").lower()
    semillas = [(s.format(j=j), "es") for s in cfg.get("semillas_es", [])] + [(s.format(j=j), "en") for s in cfg.get("semillas_en", [])]
    frases: dict[str, dict] = {}
    for q, idioma in semillas:
        for lang, hl, gl in MERCADOS:
            if lang != idioma:
                continue
            for yt in (False, True):
                try:
                    res = sugerencias(q, hl, gl, yt)
                except Exception as e:
                    log(f"[demanda] {q} ({gl}, {'YouTube' if yt else 'Google'}): {e}")
                    continue
                for pos, s in enumerate(res):
                    f = frases.setdefault(s.lower().strip(), {"fuentes": set(), "mejor_pos": 99, "idioma": idioma})
                    f["fuentes"].add(f"{'yt' if yt else 'g'}-{gl}")
                    f["mejor_pos"] = min(f["mejor_pos"], pos)
                time.sleep(pausa)
    for f in frases.values():
        f["fuentes"] = sorted(f["fuentes"])
    return frases


def puntuar(frases: dict[str, dict], historial: dict) -> list[dict]:
    """Más fuentes y más arriba en la lista = más demanda. 'nueva' si no estaba en la pasada anterior."""
    previas = set(historial.get("ultima", []))
    out = []
    for frase, f in frases.items():
        p = len(f["fuentes"]) * 10 + (10 - min(f["mejor_pos"], 10)) + (8 if any(x.startswith("yt") for x in f["fuentes"]) else 0)
        out.append(
            {
                "frase": frase,
                "puntos": p,
                "intencion": intencion(frase),
                "idioma": f["idioma"],
                "fuentes": f["fuentes"],
                "nueva": frase not in previas,
            }
        )
    return sorted(out, key=lambda x: -x["puntos"])


def escribir(lista: list[dict], historial: dict, now: dt.datetime | None = None) -> Path:
    now = now or dt.datetime.now(dt.timezone(dt.timedelta(hours=1)))
    lines = [f"# Qué busca la gente · {now:%d-%m %H:%M}", "",
             "Autocompletado de Google y YouTube (ES, MX, US). Cada frase es algo que la gente YA escribe: úsala como tema y título.",
             "🆕 = no salía en la pasada anterior (está subiendo).", ""]  # fmt: skip
    por = {}
    for x in lista:
        por.setdefault(x["intencion"], []).append(x)
    orden = ["guía", "ubicación", "secreto", "truco", "dinero", "lo mejor", "historia", "personaje", "online", "mods", "otros"]
    for k in orden:
        if k not in por:
            continue
        lines += [f"## {k} ({len(por[k])})", ""]
        for x in por[k][:12]:
            yt = "▶" if any(f.startswith("yt") for f in x["fuentes"]) else " "
            lines.append(
                f"- {'🆕 ' if x['nueva'] else ''}**{x['frase']}** · {x['puntos']} pts {yt} `{x['idioma']}` · {len(x['fuentes'])} fuentes"
            )
        lines.append("")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text("\n".join(lines), encoding="utf-8")
    historial["ultima"] = [x["frase"] for x in lista]
    serie = historial.setdefault("serie", {})
    for x in lista[:200]:
        serie.setdefault(x["frase"], []).append([now.strftime("%Y-%m-%dT%H:%M"), x["puntos"]])
        serie[x["frase"]] = serie[x["frase"]][-48:]
    HIST.write_text(json.dumps(historial, ensure_ascii=False), encoding="utf-8")
    return SALIDA


def run() -> int:
    historial = json.loads(HIST.read_text(encoding="utf-8")) if HIST.exists() else {}
    frases = recoger()
    if not frases:
        print("[demanda] sin respuesta (¿sin red?): se conserva el informe anterior")
        return 0
    lista = puntuar(frases, historial)
    escribir(lista, historial)
    print(f"[demanda] {len(lista)} búsquedas; {sum(x['nueva'] for x in lista)} nuevas")
    return len(lista)


if __name__ == "__main__":
    raise SystemExit(0 if run() >= 0 else 1)
