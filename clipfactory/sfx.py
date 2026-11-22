"""Departamento de audio · DISEÑO SONORO. Efectos y música de fondo generados por código (sin derechos de autor).

whoosh (transición), impacto (golpe de graves para el gancho), tic (reloj), pad (cama musical tipo synthwave).
mix(): voz + efectos + música con ducking suave bajo la voz + normalización a -14 LUFS en DOS pasadas (lineal, sin
"bombeo") y limitador a -1,5 dBTP. Reglas para que no se cuele nada: los efectos van muy por debajo de la voz (VOLUMEN),
cada efecto lleva fundidos de entrada/salida (sin clics), la música baja y sube con rampas (nunca escalones) y la cola
de la música se funde antes del final.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from . import media

SR = 48000
RECIPES = {
    "whoosh": [
        "-f",
        "lavfi",
        "-i",
        f"anoisesrc=color=pink:duration=0.5:sample_rate={SR}",
        "-af",
        "bandpass=f=1100:width_type=o:width=1.6,lowpass=f=4000,afade=t=in:d=0.32:curve=exp,afade=t=out:st=0.32:d=0.18,volume=0.6",
    ],
    "impacto": [
        "-f",
        "lavfi",
        "-i",
        f"aevalsrc='0.9*exp(-5*t)*sin(2*PI*(48+30*exp(-8*t))*t)+0.25*exp(-35*t)*sin(2*PI*140*t)':d=1.1:s={SR}",
        "-af",
        "afade=t=in:d=0.004,afade=t=out:st=0.8:d=0.3",
    ],
    "tic": ["-f", "lavfi", "-i", f"aevalsrc='0.5*exp(-180*t)*sin(2*PI*2400*t)':d=0.08:s={SR}"],
    # MISTERIO ----------------------------------------------------------------------------------------------
    # latido: dos golpes graves (lub-dub) para la pausa dramática
    "latido": [
        "-f",
        "lavfi",
        "-i",
        f"aevalsrc='0.9*exp(-28*t)*sin(2*PI*55*t)+0.7*exp(-28*(t-0.22))*gte(t,0.22)*sin(2*PI*50*(t-0.22))':d=0.75:s={SR}",
    ],
    # riser: tono que sube y se abre durante la pausa, corta justo en la revelación
    "riser": [
        "-f",
        "lavfi",
        "-i",
        f"aevalsrc='0.22*(t/0.8)^2*(sin(2*PI*(180*t+420*t*t))+0.4*sin(2*PI*(363*t+840*t*t)))':d=0.8:s={SR}",
        "-af",
        "lowpass=f=2500,afade=t=out:st=0.74:d=0.06",
    ],
    # dron: zumbido grave de suspense (debajo de la voz en la frase misteriosa)
    "dron": [
        "-f",
        "lavfi",
        "-i",
        f"aevalsrc='0.18*sin(t*PI/2.4)*(sin(2*PI*41*t)+0.5*sin(2*PI*61.5*t)+0.25*sin(2*PI*82*t+sin(2*PI*0.5*t)))':d=2.4:s={SR}",
    ],
}


def make(name: str, out: str | Path) -> Path:
    subprocess.run([media.require("ffmpeg"), "-y", "-loglevel", "error", *RECIPES[name], "-ac", "1", "-ar", str(SR), str(out)], check=True)
    return Path(out)


def pad(duration: float, out: str | Path) -> Path:
    """Cama musical: acorde La menor con pulso suave y filtro (ambiente synthwave), muy baja."""
    notes = [110.0, 164.81, 220.0, 261.63, 329.63]
    expr = "+".join(f"0.12*sin(2*PI*{f}*t)*(0.75+0.25*sin(2*PI*0.25*t+{i}))" for i, f in enumerate(notes))
    expr += "+0.10*sin(2*PI*55*t)*(0.5+0.5*sin(2*PI*2*t))"  # bajo con pulso a 120 bpm
    subprocess.run(
        [
            media.require("ffmpeg"),
            "-y",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"aevalsrc='{expr}':d={duration}:s={SR}",
            "-af",
            f"lowpass=f=1400,afade=t=in:d=1.2,afade=t=out:st={max(0.0, duration - 1.5):.2f}:d=1.5,volume=0.5",
            "-ac",
            "1",
            str(out),
        ],
        check=True,
    )
    return Path(out)


# volumen de cada efecto (la voz va a 1): sutiles, para acompañar y no tapar
VOLUMEN = {"whoosh": 0.10, "impacto": 0.30, "tic": 0.15, "latido": 0.30, "riser": 0.16, "dron": 0.22}


def _volumen_cama(silencios: list[tuple[float, float]] | None, base: float = 0.22, rampa: float = 0.25) -> str:
    """Expresión de volumen de la música: normal, y muy baja (15 %) dentro de cada pausa dramática, con rampas suaves
    de entrada y salida (un escalón de volumen se oye como un corte)."""
    if not silencios:
        return f"{base}"
    dentro = "+".join(f"clip((t-{a:.2f})/{rampa},0,1)*clip(({b + rampa:.2f}-t)/{rampa},0,1)" for a, b in silencios)
    return f"{base}*(1-0.85*min(1,{dentro}))"


def loudnorm_2p(src: str | Path, out: str | Path, objetivo: float = -14.0, pico: float = -1.5) -> Path:
    """Normaliza en dos pasadas (medir y aplicar ganancia lineal): el volumen no "respira" como con loudnorm dinámico."""
    import json
    import re

    ff = media.require("ffmpeg")
    r = subprocess.run(
        [ff, "-hide_banner", "-i", str(src), "-af", f"loudnorm=I={objetivo}:TP={pico}:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    m = json.loads(re.findall(r"\{[^{}]*\}", r.stderr)[-1])
    filtro = (
        f"loudnorm=I={objetivo}:TP={pico}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
        f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
        f"alimiter=limit={10 ** (pico / 20):.3f}:attack=3:release=60:level=disabled"
    )
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(src), "-af", filtro, "-ar", str(SR), str(out)], check=True)
    return Path(out)


def mix(
    voice: str,
    cues: list[tuple[float, str]],
    out: str | Path,
    music: bool = True,
    tail: float = 0.6,
    silencios: list[tuple[float, float]] | None = None,
    pista: str | Path | None = None,
) -> Path:
    """cues: [(segundo, 'whoosh'|'impacto'|'tic'|'latido'|'riser'|'dron'), ...].
    silencios: tramos [(desde, hasta)] en los que la música CAE casi a cero (la pausa dramática se nota más en silencio)."""
    out = Path(out)
    work = out.parent / (out.stem + "_sfx")
    work.mkdir(parents=True, exist_ok=True)
    dur = media.duration(voice) + tail
    inputs = ["-i", voice]
    filters, labels = [], []
    for kind in sorted({c[1] for c in cues}):
        make(kind, work / f"{kind}.wav")
    for i, (t, kind) in enumerate(cues):
        inputs += ["-i", str(work / f"{kind}.wav")]
        ms = int(max(0.0, t) * 1000)
        vol = VOLUMEN[kind]
        filters.append(f"[{i + 1}:a]adelay={ms}|{ms},volume={vol}[c{i}]")
        labels.append(f"[c{i}]")
    n = len(cues)
    if music:
        if pista:  # música real: en bucle, recortada, con fundidos (empieza en un punto con energía: segundo 6)
            inputs += ["-stream_loop", "-1", "-ss", "6", "-t", f"{dur}", "-i", str(pista)]
        else:
            pad(dur, work / "pad.wav")
            inputs += ["-i", str(work / "pad.wav")]
        filters.append(
            f"[0:a]asplit=2[vo][key];[{n + 1}:a]aformat=sample_rates={SR}:channel_layouts=mono,highpass=f=60,"
            f"volume='{_volumen_cama(silencios, 0.20 if pista else 0.22)}':eval=frame,"
            f"afade=t=in:d=0.8,afade=t=out:st={max(0.0, dur - 2.0):.2f}:d=1.9[bed];"
            "[bed][key]sidechaincompress=threshold=0.04:ratio=4:attack=40:release=450:knee=4[duck]"
        )
        voice_lbl, extra = "[vo]", ["[duck]"]
    else:
        voice_lbl, extra = "[0:a]", []
    allin = voice_lbl + "".join(labels) + "".join(extra)
    filters.append(f"{allin}amix=inputs={1 + n + len(extra)}:duration=first:normalize=0,apad=pad_dur={tail}[out]")
    bruto = work / "mezcla-bruta.wav"
    subprocess.run(
        [
            media.require("ffmpeg"),
            "-y",
            "-loglevel",
            "error",
            *inputs,
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-ar",
            str(SR),
            "-ac",
            "2",
            "-t",
            f"{dur}",
            str(bruto),
        ],
        check=True,
    )
    return loudnorm_2p(bruto, out)
