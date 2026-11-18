"""Departamento de audio · DISEÑO SONORO. Efectos y música de fondo generados por código (sin derechos de autor).

whoosh (transición), impacto (golpe de graves para el gancho), tic (reloj), pad (cama musical tipo synthwave).
mix(): voz + efectos en los cambios de escena + música con ducking bajo la voz + -14 LUFS.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from . import media

SR = 48000
RECIPES = {
    "whoosh": ["-f", "lavfi", "-i", f"anoisesrc=color=pink:duration=0.5:sample_rate={SR}",
               "-af", "bandpass=f=1800:width_type=o:width=2,afade=t=in:d=0.3:curve=exp,afade=t=out:st=0.3:d=0.2,volume=0.6"],
    "impacto": ["-f", "lavfi", "-i", f"aevalsrc='0.9*exp(-5*t)*sin(2*PI*(48+30*exp(-8*t))*t)+0.25*exp(-35*t)*sin(2*PI*140*t)':d=1.1:s={SR}"],
    "tic": ["-f", "lavfi", "-i", f"aevalsrc='0.5*exp(-180*t)*sin(2*PI*2400*t)':d=0.08:s={SR}"],
}


def make(name: str, out: str | Path) -> Path:
    subprocess.run([media.require("ffmpeg"), "-y", "-loglevel", "error", *RECIPES[name], "-ac", "1", "-ar", str(SR), str(out)], check=True)
    return Path(out)


def pad(duration: float, out: str | Path) -> Path:
    """Cama musical: acorde La menor con pulso suave y filtro (ambiente synthwave), muy baja."""
    notes = [110.0, 164.81, 220.0, 261.63, 329.63]
    expr = "+".join(f"0.12*sin(2*PI*{f}*t)*(0.75+0.25*sin(2*PI*0.25*t+{i}))" for i, f in enumerate(notes))
    expr += "+0.10*sin(2*PI*55*t)*(0.5+0.5*sin(2*PI*2*t))"  # bajo con pulso a 120 bpm
    subprocess.run([media.require("ffmpeg"), "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"aevalsrc='{expr}':d={duration}:s={SR}",
                    "-af", "lowpass=f=1400,afade=t=in:d=1.2,afade=t=out:st=%.2f:d=1.5,volume=0.5" % max(0.0, duration - 1.5),
                    "-ac", "1", str(out)], check=True)
    return Path(out)


def mix(voice: str, cues: list[tuple[float, str]], out: str | Path, music: bool = True, tail: float = 0.6) -> Path:
    """cues: [(segundo, 'whoosh'|'impacto'|'tic'), ...]."""
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
        vol = {"whoosh": 0.35, "impacto": 0.8, "tic": 0.4}[kind]
        filters.append(f"[{i + 1}:a]adelay={ms}|{ms},volume={vol}[c{i}]")
        labels.append(f"[c{i}]")
    n = len(cues)
    if music:
        pad(dur, work / "pad.wav")
        inputs += ["-i", str(work / "pad.wav")]
        filters.append(f"[0:a]asplit=2[vo][key];[{n + 1}:a]volume=0.22[bed];[bed][key]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350[duck]")
        voice_lbl, extra = "[vo]", ["[duck]"]
    else:
        voice_lbl, extra = "[0:a]", []
    allin = voice_lbl + "".join(labels) + "".join(extra)
    filters.append(f"{allin}amix=inputs={1 + n + len(extra)}:duration=first:normalize=0,apad=pad_dur={tail},"
                   f"loudnorm=I=-14:TP=-1.5:LRA=9[out]")
    subprocess.run([media.require("ffmpeg"), "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
                    "-map", "[out]", "-ar", str(SR), "-ac", "2", "-t", f"{dur}", str(out)], check=True)
    return out
