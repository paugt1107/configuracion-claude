"""Departamento de audio · LOCUCIÓN IA. Convierte un guion (una frase por línea) en una locución profesional.

- Sintetiza FRASE A FRASE: la primera con estilo "gancho" (más energía), el resto "narración", la última "cierre".
  Así cada frase tiene tiempos exactos (escenas sincronizadas) y pausas controladas.
- Proveedores (auto = el mejor disponible):
    elevenlabs  ELEVENLABS_API_KEY (+ ELEVENLABS_VOICE_ID). Máxima calidad. Tiempos por carácter.
    openai      OPENAI_API_KEY. gpt-4o-mini-tts con instrucciones de estilo. Tiempos por pausas.
    edge        Gratis, sin clave (voces neuronales de Microsoft). Tiempos por palabra. Necesita red.
    tono        Solo para tests sin red (pitidos).
- Postproducción: filtro de graves, presencia, compresor, de-esser y -14 LUFS.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path

from . import align, media

EDGE_VOICE = os.environ.get("TTS_VOICE", "es-ES-AlvaroNeural")
EDGE_STYLE = {"gancho": ("+14%", "+3Hz"), "narracion": ("+9%", "+0Hz"), "cierre": ("+4%", "+2Hz")}
OPENAI_VOICE = os.environ.get("OPENAI_TTS_VOICE", "ash")
OPENAI_INSTR = {
    "gancho": "Eres el narrador de un canal de curiosidades de videojuegos en YouTube Shorts. Español de España, claro. "
    "Arranca con mucha energía y sorpresa, como contando un secreto que engancha. Ritmo rápido, sin sonar gritón.",
    "narracion": "Narrador de curiosidades de videojuegos en Shorts. Español de España claro, ritmo ágil, entusiasta y cercano; "
    "enfatiza nombres propios, horas y números. Pausas cortas.",
    "cierre": "Cierra con intriga y una ligera sonrisa en la voz, dejando la pregunta en el aire.",
}
ELEVEN_VOICE = os.environ.get("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # cámbiala por una voz española de la Voice Library
ELEVEN_SETTINGS = {"gancho": (0.30, 0.55), "narracion": (0.40, 0.40), "cierre": (0.45, 0.35)}  # (stability, style)
GAP = {"gancho": 0.28, "narracion": 0.14, "cierre": 0.0}
POST = "highpass=f=70,equalizer=f=3200:width_type=o:width=1.2:g=2.5,deesser=i=0.4,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2"


def pick_provider(name: str = "auto") -> str:
    if name != "auto":
        return name
    if os.environ.get("ELEVENLABS_API_KEY"):
        return "elevenlabs"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "edge"


def styles_for(n: int) -> list[str]:
    return ["gancho"] + ["narracion"] * max(0, n - 2) + (["cierre"] if n > 1 else [])


# ---------------- proveedores: devuelven palabras con tiempos o None ----------------
async def _edge(text, style, out):
    import edge_tts

    rate, pitch = EDGE_STYLE[style]
    try:
        comm = edge_tts.Communicate(text, voice=EDGE_VOICE, rate=rate, pitch=pitch, boundary="WordBoundary")
    except TypeError:
        comm = edge_tts.Communicate(text, voice=EDGE_VOICE, rate=rate, pitch=pitch)
    words = []
    with open(out, "wb") as fh:
        async for ch in comm.stream():
            if ch["type"] == "audio":
                fh.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7
                words.append({"text": ch["text"], "start": s, "end": s + ch["duration"] / 1e7})
    return words or None


def _openai(text, style, out):
    body = json.dumps(
        {
            "model": os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
            "voice": OPENAI_VOICE,
            "input": text,
            "instructions": OPENAI_INSTR[style],
            "response_format": "mp3",
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        Path(out).write_bytes(r.read())
    return None


def _eleven(text, style, out):
    stab, sty = ELEVEN_SETTINGS[style]
    body = json.dumps(
        {
            "text": text,
            "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
            "voice_settings": {"stability": stab, "similarity_boost": 0.8, "style": sty, "use_speaker_boost": True},
        }
    ).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE}/with-timestamps?output_format=mp3_44100_128",
        data=body,
        method="POST",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    Path(out).write_bytes(base64.b64decode(data["audio_base64"]))
    al = data.get("alignment") or {}
    chars, st, en = al.get("characters", []), al.get("character_start_times_seconds", []), al.get("character_end_times_seconds", [])
    words, cur, cs, pe = [], "", None, 0.0
    for c, s, e in zip(chars, st, en):
        if c.isspace():
            if cur:
                words.append({"text": cur, "start": cs, "end": pe})
            cur, cs = "", None
        else:
            cur, cs, pe = cur + c, (s if cs is None else cs), e
    if cur:
        words.append({"text": cur, "start": cs, "end": pe})
    return words or None


def _tono(text, style, out):
    dur = max(0.6, len(text.split()) * 0.33)
    subprocess.run(
        [
            media.require("ffmpeg"),
            "-y",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=220:duration={dur}",
            "-af",
            "volume=0.3",
            str(out),
        ],
        check=True,
    )
    return None


def synth_line(provider, text, style, out):
    if provider == "edge":
        return asyncio.run(_edge(text, style, out))
    return {"openai": _openai, "elevenlabs": _eleven, "tono": _tono}[provider](text, style, out)


# ---------------- producción completa ----------------
def provider_chain(provider: str = "auto") -> list[str]:
    """Orden de intento: el elegido y, si falla (cuota agotada, red, clave mala), los siguientes disponibles."""
    first = pick_provider(provider)
    if first == "tono":
        return ["tono"]
    rest = [p for p in ("elevenlabs", "openai", "edge") if p != first and (p == "edge" or os.environ.get(KEYS[p]))]
    return [first, *rest]


KEYS = {"elevenlabs": "ELEVENLABS_API_KEY", "openai": "OPENAI_API_KEY"}


def produce(lines: list[str], out_dir: str | Path, provider: str = "auto", lead: float = 0.15, log=print) -> dict:
    """Locución completa con respaldo automático de proveedor. Toda la pieza usa UNA sola voz (sin mezclar)."""
    errors = []
    for prov in provider_chain(provider):
        try:
            return _produce(lines, out_dir, prov, lead)
        except Exception as e:  # noqa: BLE001 - se informa y se pasa al siguiente proveedor
            errors.append(f"{prov}: {e}")
            log(f"[voz] {prov} falló ({e}); probando el siguiente proveedor")
    raise RuntimeError("Ningún proveedor de voz funcionó: " + " | ".join(errors))


def _produce(lines: list[str], out_dir: str | Path, provider: str, lead: float) -> dict:
    """Devuelve {"audio": wav postproducido, "words": [...], "lines": [{"text","start","end"}], "provider": str}."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    styles = styles_for(len(lines))
    words_all, spans, parts, t = [], [], [], lead
    with tempfile.TemporaryDirectory(prefix="voz-") as tmp:
        tmp = Path(tmp)
        sil = tmp / "lead.wav"
        subprocess.run(
            [
                media.require("ffmpeg"),
                "-y",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=48000:cl=mono",
                "-t",
                str(lead),
                str(sil),
            ],
            check=True,
        )
        parts.append(sil)
        for i, (text, style) in enumerate(zip(lines, styles)):
            raw = tmp / f"l{i:02d}.mp3"
            ws = synth_line(provider, text, style, raw)
            wav = tmp / f"l{i:02d}.wav"
            gap = GAP[style]
            # recorta silencios del principio/fin de cada frase y añade la pausa deseada
            subprocess.run(
                [
                    media.require("ffmpeg"),
                    "-y",
                    "-loglevel",
                    "error",
                    "-i",
                    str(raw),
                    "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                    f"apad=pad_dur={gap}",
                    "-ar",
                    "48000",
                    "-ac",
                    "1",
                    str(wav),
                ],
                check=True,
            )
            dur = media.duration(str(wav))
            speech = dur - gap
            if not ws:
                ws = align.align_words(text, str(wav))
            else:  # reescala tiempos del proveedor a la frase recortada
                k = speech / max(ws[-1]["end"] - ws[0]["start"], 0.01)
                off = ws[0]["start"]
                ws = [{"text": w["text"], "start": (w["start"] - off) * k, "end": (w["end"] - off) * k} for w in ws]
            words_all += [{"text": w["text"], "start": round(t + w["start"], 3), "end": round(t + w["end"], 3)} for w in ws]
            spans.append({"text": text, "start": round(t, 3), "end": round(t + speech, 3), "style": style})
            parts.append(wav)
            t += dur
        lst = tmp / "list.txt"
        lst.write_text("\n".join(f"file '{p}'" for p in parts), encoding="utf-8")
        raw_all = tmp / "voz.wav"
        subprocess.run(
            [media.require("ffmpeg"), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(raw_all)],
            check=True,
        )
        final = out_dir / "voz.wav"
        subprocess.run(
            [media.require("ffmpeg"), "-y", "-loglevel", "error", "-i", str(raw_all), "-af", POST, "-ar", "48000", str(final)], check=True
        )
    (out_dir / "voz.words.json").write_text(json.dumps({"words": words_all}, ensure_ascii=False, indent=1), encoding="utf-8")
    (out_dir / "voz.lines.json").write_text(
        json.dumps({"provider": provider, "lines": spans}, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return {"audio": str(final), "words": words_all, "lines": spans, "provider": provider}


SAMPLE_VOICES = [
    "es-ES-AlvaroNeural",
    "es-ES-ElviraNeural",
    "es-ES-XimenaNeural",
    "es-MX-JorgeNeural",
    "es-MX-DaliaNeural",
    "es-US-AlonsoNeural",
]


def samples(text: str, out_dir: str | Path) -> list[Path]:
    """Muestras de voces gratuitas con la misma frase, para elegir la voz del canal."""
    global EDGE_VOICE
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    res = []
    for v in SAMPLE_VOICES:
        EDGE_VOICE = v
        p = out_dir / f"{v}.mp3"
        asyncio.run(_edge(text, "gancho", p))
        res.append(p)
    return res
