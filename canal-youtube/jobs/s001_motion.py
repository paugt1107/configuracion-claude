"""S001 — ¿Sabías que…? GTA VI: hora de desbloqueo por país. 14 escenas = 14 frases del guion.

  python3 canal-youtube/jobs/s001_motion.py --ia [--proveedor auto|edge|openai|elevenlabs|tono]   # voz IA + efectos + música (automático)
  python3 canal-youtube/jobs/s001_motion.py                                                        # animatic sin voz
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, ".")
from clipfactory import motion, sfx, voice  # noqa: E402

SCENES = [
    {"dur": 2.5, "kind": "clock", "reloj": "00:00", "color": "orange", "titulo": "12 HORAS ANTES QUE TÚ", "ty": 520},
    {"dur": 2.5, "kind": "clock", "reloj": "19 NOV", "color": "cyan", "titulo": "CADA REGIÓN, SU 00:00", "ty": 520, "sub": "según varios medios"},
    {"dur": 3.5, "kind": "clock", "reloj": "?", "color": "magenta", "titulo": "¿QUIÉN JUEGA PRIMERO?", "ty": 520},
    {"dur": 3.0, "kind": "clock", "reloj": "00:00", "color": "magenta", "titulo": "NUEVA ZELANDA, PRIMERO", "ty": 380, "bandera": "nz"},
    {"dur": 3.5, "kind": "split", "reloj": "00:00", "sub": "NUEVA ZELANDA · DÍA 19", "reloj2": "12:00", "sub2": "ESPAÑA · AÚN ES DÍA 18", "bandera": "nz", "bandera2": "es", "color": "orange", "titulo": "AÚN ES DÍA 18", "ty": 330},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "cyan", "titulo": "ESPAÑA", "ty": 380, "sub": "= 23:00 UTC (día 18)", "bandera": "es"},
    {"dur": 3.5, "kind": "timeline", "titulo": "23:00 UTC = 00:00 ESPAÑA", "ty": 520},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "gold", "titulo": "MÉXICO (CENTRO)", "ty": 380, "sub": "= 06:00 UTC (día 19)", "bandera": "mx"},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "cyan", "titulo": "ARGENTINA", "ty": 380, "sub": "= 03:00 UTC", "bandera": "ar"},
    {"dur": 3.5, "kind": "three", "relojes": [("00:00", "ESPAÑA · 23:00 UTC", "es"), ("00:00", "MÉXICO · 06:00 UTC", "mx"), ("00:00", "ARGENTINA · 03:00 UTC", "ar")], "titulo": "MISMA HORA ≠ MISMO MOMENTO", "ty": 330, "tsize": 70},
    {"dur": 3.5, "kind": "bar", "titulo": "PRECARGA ≠ JUGAR ANTES", "ty": 520},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "orange", "titulo": "COMPRUEBA TU TIENDA", "ty": 520, "sub": "PlayStation / Xbox"},
    {"dur": 2.5, "kind": "clock", "reloj": "↓", "color": "gold", "titulo": "¿DESDE QUÉ PAÍS JUEGAS?", "ty": 520, "tsize": 70},
    {"dur": 3.0, "kind": "clock", "reloj": "00:00", "color": "magenta", "titulo": "EN NUEVA ZELANDA YA JUEGAN", "ty": 380, "bandera": "nz"},
]
LINES = [l.strip() for l in Path("canal-youtube/audio/S001-narracion.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
assert len(LINES) == len(SCENES), f"{len(LINES)} frases vs {len(SCENES)} escenas"

ap = argparse.ArgumentParser()
ap.add_argument("--ia", action="store_true")
ap.add_argument("--proveedor", default="auto")
ap.add_argument("--salida", default="entregas/S001/S001-final-ia.mp4")
a = ap.parse_args()

if a.ia:
    work = Path("salida/S001-voz")
    v = voice.produce(LINES, work, provider=a.proveedor)
    spans = v["lines"]
    end = spans[-1]["end"] + 0.6
    starts = [0.0] + [s["start"] - 0.08 for s in spans[1:]]
    for i, s in enumerate(SCENES):
        s["dur"] = round((starts[i + 1] if i + 1 < len(starts) else end) - starts[i], 3)
    cues = [(0.0, "impacto")] + [(st - 0.12, "whoosh") for st in starts[1:]] + [(starts[-1], "impacto")]
    mixed = sfx.mix(v["audio"], cues, work / "mezcla.wav", music=True)
    out = motion.build(SCENES, v["words"], a.salida, str(mixed), premixed=True)
    print(out, f"{sum(s['dur'] for s in SCENES):.1f}s", "voz:", v["provider"])
else:
    total = sum(s["dur"] for s in SCENES)
    out = motion.build(SCENES, motion.estimate_words(" ".join(LINES), total), "salida/S001-animatic.mp4")
    print(out, f"{total:.1f}s sin voz")
