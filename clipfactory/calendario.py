"""STUDIO · Calendario de publicación: reparte los vídeos listos (APTO y sin publicar) en los huecos del calendario.

Huecos: canal-youtube/fuentes/juego.yaml → calendario (días, vídeos por día, horas; hora de España). Empieza el próximo
JUEVES (día fuerte del canal) o hoy si se pide. Escribe:
  canal-youtube/datos/calendario.md       tabla fecha/hora → vídeo, con su título y plataformas
  canal-youtube/datos/calendario.ics      para importarlo en el calendario del móvil (recordatorio 30 min antes)
  y añade "📅 Publicar: …" al principio de cada entregas/<ID>/publicacion.md
Uso: python3 -m clipfactory.calendario [--desde AAAA-MM-DD] [--hoy]
"""

from __future__ import annotations

import argparse
import datetime as dt
import re

import yaml

from . import rutas

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
ZONA = dt.timezone(dt.timedelta(hours=1))  # España en invierno (CET); en verano cambia a +2


def pendientes() -> list[dict]:
    """Vídeos con control APTO que no figuran como publicados en registro-videos.md, en orden de ID."""
    reg = (rutas.DATOS / "registro-videos.md").read_text(encoding="utf-8") if (rutas.DATOS / "registro-videos.md").exists() else ""
    publicados = set(re.findall(r"^\| (S\d+) \|[^\n]*\| publicado", reg, re.M | re.I))
    out = []
    for d in sorted(rutas.ENTREGAS.glob("S[0-9]*")):
        qa = d / "control-calidad.md"
        if d.name in publicados or not (d / f"{d.name}-final.mp4").exists() or not qa.exists():
            continue
        if "APTO" not in qa.read_text(encoding="utf-8").splitlines()[0]:
            continue
        g = rutas.GUIONES / f"{d.name}.yaml"
        spec = yaml.safe_load(g.read_text(encoding="utf-8")) if g.exists() else {}
        if spec.get("juego") == "ninguno":  # vídeos fuera del canal de GTA no entran en su calendario
            continue
        out.append({"id": d.name, "titulo": (spec.get("titulos") or [d.name])[0], "dir": d})
    return out


def huecos(cfg: dict, desde: dt.date, n: int) -> list[dt.datetime]:
    cal = cfg.get("calendario") or {}
    dias = [DIAS.index(x) for x in cal.get("dias", DIAS)]
    horas = [tuple(map(int, h.split(":"))) for h in cal.get("horas", ["20:30"])][: int(cal.get("por_dia", 1))]
    out, dia = [], desde
    ahora = dt.datetime.now(ZONA)
    while len(out) < n:
        if dia.weekday() in dias:
            for h, m in horas:
                t = dt.datetime(dia.year, dia.month, dia.day, h, m, tzinfo=ZONA)
                if t > ahora:
                    out.append(t)
        dia += dt.timedelta(days=1)
    return out[:n]


def proximo_jueves(hoy: dt.date) -> dt.date:
    return hoy + dt.timedelta(days=(3 - hoy.weekday()) % 7)


def _ics(eventos: list[tuple[dt.datetime, dict]]) -> str:
    sello = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lineas = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//sabiasque-gta6//calendario//ES"]
    for t, v in eventos:
        u = t.astimezone(dt.timezone.utc)
        lineas += [
            "BEGIN:VEVENT", f"UID:{v['id']}-{u:%Y%m%dT%H%M}@sabiasque", f"DTSTAMP:{sello}",
            f"DTSTART:{u:%Y%m%dT%H%M%SZ}", f"DTEND:{(u + dt.timedelta(minutes=15)):%Y%m%dT%H%M%SZ}",
            f"SUMMARY:Publicar {v['id']}: {v['titulo'][:60]}",
            f"DESCRIPTION:Archivos en entregas/{v['id']}/ (vídeo, portadas y publicacion.md). YouTube Shorts + TikTok + Reels. Etiqueta IA.",
            "BEGIN:VALARM", "TRIGGER:-PT30M", "ACTION:DISPLAY", "DESCRIPTION:Publicar vídeo", "END:VALARM", "END:VEVENT",
        ]  # fmt: skip
    return "\r\n".join(lineas + ["END:VCALENDAR"]) + "\r\n"


def planificar(desde: dt.date | None = None, hoy: bool = False) -> list[tuple[dt.datetime, dict]]:
    cfg = yaml.safe_load((rutas.FUENTES / "juego.yaml").read_text(encoding="utf-8")) or {}
    vids = pendientes()
    inicio = desde or (dt.date.today() if hoy else proximo_jueves(dt.date.today()))
    plan = list(zip(huecos(cfg, inicio, len(vids)), vids))
    filas = ["# Calendario de publicación", "",
             f"Generado {dt.datetime.now(ZONA):%d-%m %H:%M} (hora de España). Vídeos APTO sin publicar: {len(vids)}. "
             "Importa `calendario.ics` en el móvil para tener un aviso 30 min antes.", "",
             "| Cuándo | Vídeo | Título | Dónde |", "|---|---|---|---|"]  # fmt: skip
    for t, v in plan:
        cuando = f"{DIAS[t.weekday()].capitalize()} {t:%d-%m %H:%M}"
        filas.append(f"| {cuando} | {v['id']} | {v['titulo']} | YouTube Shorts · TikTok · Reels |")
        pub = v["dir"] / "publicacion.md"
        if pub.exists():
            txt = re.sub(r"^📅 Publicar:.*\n\n", "", pub.read_text(encoding="utf-8"))
            pub.write_text(f"📅 Publicar: {cuando} (hora de España) en YouTube Shorts, TikTok y Reels\n\n{txt}", encoding="utf-8")
    (rutas.DATOS / "calendario.md").write_text("\n".join(filas) + "\n", encoding="utf-8")
    (rutas.DATOS / "calendario.ics").write_text(_ics(plan), encoding="utf-8")
    return plan


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="clipfactory.calendario")
    ap.add_argument("--desde", help="AAAA-MM-DD (por defecto, el próximo jueves)")
    ap.add_argument("--hoy", action="store_true", help="empezar hoy en vez del próximo jueves")
    a = ap.parse_args(argv)
    plan = planificar(dt.date.fromisoformat(a.desde) if a.desde else None, a.hoy)
    for t, v in plan:
        print(f"{DIAS[t.weekday()]:>9} {t:%d-%m %H:%M}  {v['id']}  {v['titulo']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
