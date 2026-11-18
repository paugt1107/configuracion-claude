"""CLI: python3 -m clipfactory <comando> ...  (ver `python3 -m clipfactory -h`)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import rutas, sources


def _cmd_fuentes(a):
    reg = sources.load_registry(a.registro)
    bad = 0
    for sid, src in reg.items():
        try:
            sources.validate(src)
            lim = src.fragment_limit
            print(f"OK   {sid:28} {src.tipo:8} máx {'∞' if lim is None else f'{lim:.0f}s'}  {src.credito}")
        except sources.PolicyError as e:
            bad += 1
            print(f"MAL  {sid:28} {e}")
    return 1 if bad else 0


def _cmd_descargar(a):
    from .download import download

    print(download(a.fuente, a.dir, a.registro))


def _cmd_transcribir(a):
    from .transcribe import transcribe

    print(transcribe(a.media, a.salida, model=a.modelo, language=a.idioma))


def _cmd_candidatos(a):
    from .segments import candidates
    from .words import load_words

    cands = candidates(load_words(a.palabras), a.min, a.max, a.top)
    if a.salida:
        Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
        Path(a.salida).write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
    for i, c in enumerate(cands, 1):
        print(f"{i}. [{c['inicio']:.1f}-{c['fin']:.1f}s, {c['duracion']}s] {c['puntuacion']:+.1f}  «{c['primera_frase'][:90]}»")
        print(f"   motivos: {', '.join(c['motivos']) or '—'}")


def _cmd_voz(a):
    from .tts import synthesize

    text = Path(a.archivo).read_text(encoding="utf-8") if a.archivo else a.texto
    if not text:
        sys.exit("Indica el texto o --archivo")
    print(synthesize(text, a.salida, voice=a.voz, rate=a.velocidad))


def _cmd_narrar(a):
    from .voice import produce

    lines = [l.strip() for l in Path(a.guion).read_text(encoding="utf-8").splitlines() if l.strip()]
    r = produce(lines, a.salida, provider=a.proveedor)
    print(f"{r['audio']} · {len(r['lines'])} frases · proveedor {r['provider']}")


def _cmd_voces(a):
    from .voice import samples

    for p in samples(a.texto, a.salida):
        print(p)


def _cmd_producir(a):
    from .short_job import produce

    print(produce(a.guion, provider=a.proveedor))


def _cmd_portadas(a):
    import yaml

    from .thumbs import make_covers

    spec = yaml.safe_load(Path(a.guion).read_text(encoding="utf-8"))
    for p in make_covers(spec["portada"], rutas.ENTREGAS / spec["id"]):
        print(p)


def _cmd_recortar(a):
    from .recorte import cutout

    print(cutout(a.imagen, a.salida))


def _cmd_render(a):
    from .render import render

    print(render(a.job, a.registro, dry_run=a.dry_run))


def _cmd_radar(a):
    from . import trends

    ranked = trends.scan(a.consulta, days=a.dias, region=a.region, lang=a.idioma, alarm=a.umbral)
    print(trends.save(a.consulta, ranked, alarm=a.umbral))


def _cmd_subir(a):
    if not a.confirmo:
        sys.exit("Subida bloqueada: añade --confirmo después de revisar el vídeo. Se sube como privado salvo que indiques otra cosa.")
    from .upload_youtube import upload

    desc = Path(a.descripcion).read_text(encoding="utf-8") if a.descripcion and Path(a.descripcion).exists() else (a.descripcion or "")
    vid = upload(
        a.video,
        a.titulo,
        desc,
        tags=[t.strip() for t in (a.etiquetas or "").split(",") if t.strip()],
        privacy=a.privacidad,
        publish_at=a.programar,
        synthetic=a.sintetico,
    )
    print(f"Subido: https://youtu.be/{vid} ({a.privacidad if not a.programar else 'programado ' + a.programar})")


def main(argv=None):
    p = argparse.ArgumentParser(prog="clipfactory", description="Fábrica de Shorts/TikToks con política de fuentes.")
    p.add_argument("--registro", default=str(sources.DEFAULT_REGISTRY), help="registro de fuentes YAML")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("fuentes", help="valida el registro de fuentes")
    s.set_defaults(f=_cmd_fuentes)
    s = sub.add_parser("descargar", help="descarga una fuente registrada")
    s.add_argument("fuente")
    s.add_argument("--dir", default=str(rutas.MEDIA))
    s.set_defaults(f=_cmd_descargar)
    s = sub.add_parser("transcribir", help="transcribe con faster-whisper")
    s.add_argument("media")
    s.add_argument("--salida", required=True)
    s.add_argument("--modelo", default="small")
    s.add_argument("--idioma", default="es")
    s.set_defaults(f=_cmd_transcribir)
    s = sub.add_parser("candidatos", help="propone momentos de 20-55 s")
    s.add_argument("palabras")
    s.add_argument("--min", type=float, default=20)
    s.add_argument("--max", type=float, default=55)
    s.add_argument("--top", type=int, default=5)
    s.add_argument("--salida")
    s.set_defaults(f=_cmd_candidatos)
    s = sub.add_parser("voz", help="voz en off con edge-tts + palabras")
    s.add_argument("texto", nargs="?")
    s.add_argument("--archivo")
    s.add_argument("--salida", required=True)
    s.add_argument("--voz", default="es-ES-AlvaroNeural")
    s.add_argument("--velocidad", default="+8%")
    s.set_defaults(f=_cmd_voz)
    s = sub.add_parser("narrar", help="locución IA frase a frase (+ tiempos)")
    s.add_argument("guion")
    s.add_argument("--salida", required=True)
    s.add_argument("--proveedor", default="auto", help="auto|edge|openai|elevenlabs|tono")
    s.set_defaults(f=_cmd_narrar)
    s = sub.add_parser("voces", help="muestras de voces gratuitas")
    s.add_argument("--texto", default="¿Sabías que hay gente que juega GTA seis doce horas antes que tú?")
    s.add_argument("--salida", default=str(rutas.ENTREGAS / "voces"))
    s.set_defaults(f=_cmd_voces)
    s = sub.add_parser("producir", help="Short completo desde guion YAML (voz IA, vídeo, portadas, publicación)")
    s.add_argument("guion")
    s.add_argument("--proveedor", default="auto")
    s.set_defaults(f=_cmd_producir)
    s = sub.add_parser("portadas", help="3 portadas desde el guion YAML")
    s.add_argument("guion")
    s.set_defaults(f=_cmd_portadas)
    s = sub.add_parser("recortar", help="quita el fondo de una imagen (rembg)")
    s.add_argument("imagen")
    s.add_argument("--salida", required=True)
    s.set_defaults(f=_cmd_recortar)
    s = sub.add_parser("render", help="renderiza un job YAML a 1080x1920")
    s.add_argument("job")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(f=_cmd_render)
    s = sub.add_parser("radar", help="radar de tendencias (YOUTUBE_API_KEY)")
    s.add_argument("consulta")
    s.add_argument("--dias", type=int, default=7)
    s.add_argument("--region", default="ES")
    s.add_argument("--idioma", default="es")
    s.add_argument("--umbral", type=float, default=10.0)
    s.set_defaults(f=_cmd_radar)
    s = sub.add_parser("subir", help="sube a YouTube (OAuth). Privado por defecto")
    s.add_argument("video")
    s.add_argument("--titulo", required=True)
    s.add_argument("--descripcion", default="")
    s.add_argument("--etiquetas", default="")
    s.add_argument("--privacidad", default="private")
    s.add_argument("--programar", help="RFC3339, p. ej. 2026-11-20T18:00:00+01:00")
    s.add_argument("--sintetico", action="store_true", help="declara contenido sintético realista")
    s.add_argument("--confirmo", action="store_true")
    s.set_defaults(f=_cmd_subir)

    a = p.parse_args(argv)
    try:
        rc = a.f(a)
    except sources.PolicyError as e:
        print(f"POLÍTICA: {e}", file=sys.stderr)
        return 2
    except (FileNotFoundError, RuntimeError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return rc or 0


if __name__ == "__main__":
    sys.exit(main())
