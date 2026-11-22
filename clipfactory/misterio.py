"""DIRECTOR DE SUSPENSE · pausas dramáticas, zooms y golpes de cámara para que cada vídeo tenga misterio.

Cómo funciona (todo automático; el guion puede forzarlo con `pausa: true` o desactivarlo con `misterio: false`):

1. estilos()  → decide qué frases son de SUSPENSE: las que preparan una revelación ("Pero…", "Ojo…", "Lo raro es que…",
   "nadie", "secreto", frases con "…", preguntas a mitad de vídeo). Como mucho 3 por vídeo y nunca dos seguidas.
   La voz las dice más lenta y grave (estilo "suspense" de voice.py) y deja una PAUSA de ~0,85 s detrás.
2. plan()     → con los tiempos reales de la locución, coloca:
     · EMPUJE: acercamiento MUY lento (1,00 → 1,03) y oscurecimiento leve durante la frase de suspense y su pausa.
     · GOLPE:  pequeño acento de cámara (≤ 4 %, subida suave y caída lenta, nada de tirones) en la REVELACIÓN, en la 1.ª
               palabra del gancho y, como mucho, en UN dato más. Máximo MAX_GOLPES por vídeo: la cámara de verdad la
               mueve el travelling 3D; estos golpes solo subrayan 2-3 momentos clave.
     · SILENCIO: la música cae casi a cero en la pausa (el silencio da más tensión que cualquier efecto).
     · SONIDO: dron grave bajo la frase de suspense, latido al empezar la pausa, riser que sube hasta la revelación
               y un impacto en la revelación.
3. filtro()   → traduce el plan a un filtro de ffmpeg (escala + recorte por fotograma + brillo), que motion.build aplica al
   vídeo base ANTES de las imágenes de Tommy y los subtítulos (así los subtítulos no se mueven ni pierden nitidez).
"""

from __future__ import annotations

import re

W, H = 1080, 1920

# Frases que preparan una revelación (al principio de la frase o en cualquier parte)
INICIO = re.compile(
    r"^\s*(pero|ojo|y aqu[ií]|aqu[ií] viene|lo raro|lo curioso|lo mejor|lo peor|ahora bien|sin embargo|en realidad|"
    r"y lo m[aá]s|atento|f[ií]jate|espera)\b",
    re.I,
)
CLAVE = re.compile(r"\b(nadie|secreto|escond|ocult|misterio|nunca|casi nadie|no sab[ií]as|truco|de verdad|realmente)\w*", re.I)
NUMERO = re.compile(r"^\d|^(un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|veinte|treinta|cien|mil|mill[oó]n)", re.I)

MAX_PAUSAS = 3
GOLPE_REVELACION, GOLPE_GANCHO, GOLPE_DATO = 0.04, 0.03, 0.025
EMPUJE = 0.03
OSCURO = -0.05
SEPARACION_GOLPES = 8.0
MAX_GOLPES = 3


def _es_suspense(texto: str) -> int:
    """Puntuación de 'suspense' de una frase (0 = ninguna)."""
    t = texto.strip()
    p = 0
    if INICIO.search(t):
        p += 3
    if CLAVE.search(t):
        p += 2
    if t.endswith("…") or t.endswith("..."):
        p += 3
    if t.endswith("?"):
        p += 1
    return p


def estilos(lines: list[str], escenas: list[dict] | None = None, max_pausas: int = MAX_PAUSAS) -> list[str]:
    """Estilo de voz de cada frase: gancho (1.ª), cierre (última), suspense (las mejores candidatas) y narración."""
    n = len(lines)
    out = ["gancho"] + ["narracion"] * max(0, n - 2) + (["cierre"] if n > 1 else [])
    escenas = escenas or [{} for _ in lines]
    if n < 4:
        return out
    forzadas = {i for i, e in enumerate(escenas) if e.get("pausa") is True and 0 < i < n - 1}
    vetadas = {i for i, e in enumerate(escenas) if e.get("pausa") is False}
    cands = sorted(
        ((i, _es_suspense(lines[i])) for i in range(1, n - 1) if i not in vetadas and i not in forzadas),
        key=lambda x: (-x[1], x[0]),
    )
    elegidas = set(forzadas)
    for i, p in cands:
        if len(elegidas) >= max_pausas or p < 3:
            break
        if any(abs(i - j) <= 1 for j in elegidas):  # nunca dos pausas seguidas
            continue
        elegidas.add(i)
    for i in elegidas:
        out[i] = "suspense"
    return out


def plan(spans: list[dict], words: list[dict], styles: list[str], total: float) -> dict:
    """Plan de cámara y sonido a partir de los tiempos reales. spans = voz.lines ({text,start,end,style})."""
    golpes: list[tuple[float, float]] = []
    empujes: list[tuple[float, float]] = []
    silencios: list[tuple[float, float]] = []
    cues: list[tuple[float, str]] = []
    revelaciones: list[float] = []
    for i, (sp, st) in enumerate(zip(spans, styles)):
        if st != "suspense" or i + 1 >= len(spans):
            continue
        a, fin_voz, reve = sp["start"], sp["end"], spans[i + 1]["start"]
        empujes.append((a, reve))
        silencios.append((fin_voz, reve))
        revelaciones.append(reve)
        golpes.append((reve, GOLPE_REVELACION))
        cues += [(a, "dron"), (fin_voz + 0.02, "latido"), (max(fin_voz, reve - 0.8), "riser"), (reve, "impacto")]
    if words:
        golpes.append((words[0]["start"], GOLPE_GANCHO))
    # golpes suaves en datos y nombres propios, sin pisar las revelaciones ni amontonarse
    ultimo = words[0]["start"] if words else -99.0  # el primer dato, lejos del golpe del gancho
    from . import captions, numeros

    cifras = numeros.a_cifras(words)  # "trescientos millones" → "300 millones": también cuentan como dato
    for k, w in enumerate(cifras):
        if k == 0 or not captions.es_clave(cifras, k) or w["start"] - ultimo < SEPARACION_GOLPES:
            continue
        if any(abs(w["start"] - r) < 1.2 for r in revelaciones) or any(a <= w["start"] < b for a, b in empujes):
            continue
        if len(golpes) >= MAX_GOLPES:
            break
        golpes.append((w["start"], GOLPE_DATO))
        ultimo = w["start"]
    return {"golpes": sorted(golpes), "empujes": empujes, "silencios": silencios, "cues": cues, "total": total}


def _zoom_expr(p: dict) -> str:
    """Z(t): 1 + golpes (subida suave de 0,18 s y caída lenta, sin tirones) + empujes (rampa lenta que vuelve suave)."""
    partes = [
        f"{f:.3f}*clip((t-{t0 - 0.06:.3f})/0.18,0,1)*exp(-max(t-{t0 + 0.12:.3f},0)*2.2)*gte(t,{t0 - 0.06:.3f})" for t0, f in p["golpes"]
    ]
    partes += [
        f"{EMPUJE}*clip((t-{a:.3f})/{max(b - a, 0.1):.3f},0,1)*clip(({b + 0.6:.3f}-t)/0.6,0,1)*gte(t,{a:.3f})" for a, b in p["empujes"]
    ]
    return "1+" + "+".join(partes) if partes else "1"


def _brillo_expr(p: dict) -> str:
    if not p["empujes"]:
        return "0"
    return f"{OSCURO}*min(1," + "+".join(f"clip((t-{a:.3f})/0.5,0,1)*clip(({b + 0.4:.3f}-t)/0.4,0,1)" for a, b in p["empujes"]) + ")"


def filtro(p: dict) -> str | None:
    """Filtro ffmpeg de cámara para el vídeo base (1080x1920). None si no hay nada que hacer."""
    if not p["golpes"] and not p["empujes"]:
        return None
    z = _zoom_expr(p)
    return (
        f"scale=w='trunc({W // 2}*({z}))*2':h='trunc({H // 2}*({z}))*2':eval=frame:flags=bicubic,"
        f"crop={W}:{H},"
        f"eq=brightness='{_brillo_expr(p)}':eval=frame"
    )
