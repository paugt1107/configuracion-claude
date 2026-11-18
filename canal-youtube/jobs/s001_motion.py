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
    {"dur": 3.0, "kind": "clock", "reloj": "00:00", "color": "magenta", "titulo": "NUEVA ZELANDA, PRIMERO", "ty": 380, "bandera": "nz"},
    {"dur": 3.5, "kind": "split", "reloj": "00:00", "sub": "NUEVA ZELANDA · DÍA 19", "reloj2": "12:00", "sub2": "ESPAÑA · AÚN ES DÍA 18", "bandera": "nz", "bandera2": "es", "color": "orange", "titulo": "AÚN ES DÍA 18", "ty": 330},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "cyan", "titulo": "ESPAÑA", "ty": 380, "sub": "= 23:00 UTC (día 18)", "bandera": "es"},
    {"dur": 3.5, "kind": "timeline", "titulo": "23:00 UTC = 00:00 ESPAÑA", "ty": 520},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "gold", "titulo": "MÉXICO (CENTRO)", "ty": 380, "sub": "= 06:00 UTC (día 19)", "bandera": "mx"},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "cyan", "titulo": "ARGENTINA", "ty": 380, "sub": "= 03:00 UTC", "bandera": "ar"},
    {"dur": 3.5, "kind": "three", "relojes": [("00:00", "ESPAÑA · 23:00 UTC", "es"), ("00:00", "MÉXICO · 06:00 UTC", "mx"), ("00:00", "ARGENTINA · 03:00 UTC", "ar")], "titulo": "MISMA HORA ≠ MISMO MOMENTO", "ty": 330, "tsize": 70},
    {"dur": 3.5, "kind": "bar", "titulo": "PRECARGA ≠ JUGAR ANTES", "ty": 520},
    {"dur": 3.5, "kind": "clock", "reloj": "00:00", "color": "orange", "titulo": "COMPRUEBA TU TIENDA", "ty": 520, "sub": "PlayStation / Xbox"},
    {"dur": 2.5, "kind": "clock", "reloj": "↓", "color": "gold", "titulo": "MÁS EN EL COMENTARIO FIJADO", "ty": 520, "tsize": 70},
    {"dur": 3.0, "kind": "clock", "reloj": "00:00", "color": "orange", "titulo": "¿A QUÉ HORA?", "ty": 520},
]
TEXTO = Path("canal-youtube/audio/S001-narracion.txt").read_text(encoding="utf-8").replace("\n", " ")
total = sum(s["dur"] for s in SCENES)
audio, words = None, None
args = sys.argv[1:]
if args:
    audio = args[0]
    from clipfactory import align, media
    if len(args) > 1:
        words = json.loads(Path(args[1]).read_text(encoding="utf-8"))["words"]
    else:
        words = align.align_words(TEXTO, audio)  # sincroniza el texto con tu voz sin red ni IA
    # cada escena = una línea del guion: cambia de escena cuando empiezas a decir su frase
    lines = [l for l in Path("canal-youtube/audio/S001-narracion.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(lines) == len(SCENES):
        idx, starts = 0, []
        for l in lines:
            starts.append(0.0 if not starts else words[idx]["start"] - 0.1)
            idx += len(l.split())
        end = media.duration(audio) + 0.4
        for i, s in enumerate(SCENES):
            s["dur"] = round((starts[i + 1] if i + 1 < len(starts) else end) - starts[i], 3)
    else:  # si no cuadra, reparto proporcional
        k = (media.duration(audio) + 0.4) / total
        for s in SCENES:
            s["dur"] = round(s["dur"] * k, 3)
    total = sum(s["dur"] for s in SCENES)
    print("escenas (s):", [s["dur"] for s in SCENES])
else:
    words = motion.estimate_words(TEXTO, total)
out = motion.build(SCENES, words, "salida/S001-animatic.mp4" if not audio else "entregas/S001/S001-final.mp4", audio)
print(out, f"{total:.1f}s", "con tu voz" if audio else "SIN voz (subtítulos estimados)")
