"""S001 — GTA VI: hora de desbloqueo por país. Animatic de gráficos (14 escenas, ~45 s).
Ejecutar desde la raíz:  python3 canal-youtube/jobs/s001_motion.py [ruta-voz.mp3 ruta-palabras.json]
Si pasas voz + palabras (de `clipfactory voz` o de tu locución transcrita), los subtítulos se sincronizan con ella."""
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from clipfactory import motion  # noqa: E402

SCENES = [
    {"dur": 2.5, "kind": "clock", "reloj": "00:00", "color": "orange", "titulo": "NO A LA MISMA HORA", "ty": 520},
    {"dur": 2.5, "kind": "clock", "reloj": "19 NOV", "color": "cyan", "titulo": "CADA REGIÓN, SU 00:00", "ty": 520, "sub": "según varios medios"},
    {"dur": 3.5, "kind": "clock", "reloj": "?", "color": "magenta", "titulo": "¿QUIÉN JUEGA PRIMERO?", "ty": 520},
    {"dur": 3.0, "kind": "clock", "reloj": "00:00", "color": "magenta", "titulo": "NUEVA ZELANDA, PRIMERO", "ty": 520, "sub": "NUEVA ZELANDA"},
    {"dur": 3.5, "kind": "split", "reloj": "00:00", "sub": "NUEVA ZELANDA · DÍA 19", "reloj2": "12:00", "sub2": "ESPAÑA · AÚN ES DÍA 18", "color": "orange", "titulo": "AÚN ES DÍA 18", "ty": 330},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "cyan", "titulo": "ESPAÑA", "ty": 520, "sub": "= 23:00 UTC (día 18)"},
    {"dur": 3.5, "kind": "timeline", "titulo": "23:00 UTC = 00:00 ESPAÑA", "ty": 520},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "gold", "titulo": "MÉXICO (CENTRO)", "ty": 520},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "cyan", "titulo": "ARGENTINA", "ty": 520, "sub": "= 03:00 UTC"},
    {"dur": 3.5, "kind": "three", "relojes": [("00:00", "ESPAÑA · 23:00 UTC"), ("00:00", "MÉXICO · 06:00 UTC"), ("00:00", "ARGENTINA · 03:00 UTC")], "titulo": "MISMA HORA ≠ MISMO MOMENTO", "ty": 330, "tsize": 70},
    {"dur": 3.5, "kind": "bar", "titulo": "PRECARGA ≠ JUGAR ANTES", "ty": 520},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "orange", "titulo": "COMPRUEBA TU TIENDA", "ty": 520, "sub": "PlayStation / Xbox"},
    {"dur": 2.5, "kind": "clock", "reloj": "↓", "color": "gold", "titulo": "MÁS EN EL COMENTARIO FIJADO", "ty": 520, "tsize": 70},
    {"dur": 3.0, "kind": "clock", "reloj": "00:00", "color": "orange", "titulo": "¿A QUÉ HORA?", "ty": 520},
]
TEXTO = Path("canal-youtube/audio/S001-narracion.txt").read_text(encoding="utf-8").replace("\n", " ")
total = sum(s["dur"] for s in SCENES)
if len(sys.argv) >= 3:
    audio, words = sys.argv[1], json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))["words"]
else:
    audio, words = None, motion.estimate_words(TEXTO, total)
out = motion.build(SCENES, words, "salida/S001-animatic.mp4", audio)
print(out, f"{total:.1f}s", "con voz" if audio else "SIN voz (subtítulos con tiempos estimados)")
