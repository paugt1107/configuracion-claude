"""Radar web de GTA VI (trabajador automático cada 30 min en GitHub Actions, sin tokens de Claude).

Fuentes (canal-youtube/fuentes/radar.yaml): Google News RSS por búsqueda, canales de YouTube por RSS (solo títulos),
subreddits por RSS, y búsqueda de YouTube Data API si hay YOUTUBE_API_KEY.
SOLO recopila títulos y enlaces para investigar. NO descarga vídeos ni imágenes de nadie (ver politica-fuentes.md).
Salida: canal-youtube/datos/radar/AAAA-MM-DD.md (acumulado del día) y ultimo.md (novedades de la última pasada).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

from . import rutas

UA = "Mozilla/5.0 (radar-gta; uso personal de investigacion)"
OUT = rutas.RADAR
CATEGORIES = [
    ("misión", r"misi[oó]n|mission|golpe|heist|atraco"),
    ("personaje", r"lucia|jason|cal hampton|boobie|dre'?quan|real dimez|raul bautista|brian heder|personaje|character"),
    ("secreto", r"secret|easter ?egg|oculto|escondid|hidden|detalle|curiosidad|sab[ií]as"),
    ("truco", r"truco|trick|tip|consejo|gu[ií]a|guide|c[oó]mo (conseguir|desbloquear|hacer)|how to|dinero|money|coche|car"),
    ("mapa", r"mapa|map|vice city|leonida|keys|grassrivers|port gellhorn|ambrosia|kalaga|ubicaci[oó]n|location"),
    ("polémica/bug", r"bug|glitch|error|crash|pol[eé]mic|cr[ií]tica|review|nota|metacritic|ventas|sales|r[eé]cord"),
]
CURIOSITY = r"sab[ií]as|nadie|secret|oculto|escondid|easter|detalle|curios|incre[ií]ble|primera vez|r[eé]cord|hidden|nobody"


def fetch(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_feed(data: bytes, source: str) -> list[dict]:
    """RSS 2.0 o Atom (YouTube, Reddit) → [{title, url, date, source}]."""
    root = ET.fromstring(data)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items = []
    for it in root.iter("item"):
        items.append(
            {
                "title": (it.findtext("title") or "").strip(),
                "url": (it.findtext("link") or "").strip(),
                "date": (it.findtext("pubDate") or "").strip(),
                "source": source,
            }
        )
    for e in root.findall("a:entry", ns):
        link = e.find("a:link", ns)
        items.append(
            {
                "title": (e.findtext("a:title", default="", namespaces=ns)).strip(),
                "url": link.get("href", "") if link is not None else "",
                "date": e.findtext("a:published", default="", namespaces=ns) or e.findtext("a:updated", default="", namespaces=ns),
                "source": source,
            }
        )
    return [i for i in items if i["title"] and i["url"]]


def classify(title: str) -> tuple[str, int]:
    t = title.lower()
    cats = [name for name, rx in CATEGORIES if re.search(rx, t)]
    score = len(cats) + (2 if re.search(CURIOSITY, t) else 0)
    return (", ".join(cats) or "general"), score


def item_id(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()[:16]


def resolve_channel(handle: str) -> str | None:
    html = fetch(f"https://www.youtube.com/{handle}").decode("utf-8", "ignore")
    m = re.search(r'"channelId":"(UC[\w-]{22})"', html) or re.search(r'itemprop="identifier" content="(UC[\w-]{22})"', html)
    return m.group(1) if m else None


def collect(cfg: dict, log=print) -> list[dict]:
    items: list[dict] = []
    for q in cfg.get("google_news", []):
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q, "hl": "es", "gl": "ES", "ceid": "ES:es"})
        try:
            items += parse_feed(fetch(url), f"Noticias: {q}")
        except Exception as e:  # una fuente caída no para el radar
            log(f"[aviso] Google News '{q}': {e}")
    for ch in cfg.get("youtube_canales", []):
        try:
            cid = ch.get("id") or resolve_channel(ch["handle"])
            if not cid:
                log(f"[aviso] no encuentro el canal {ch.get('handle')}")
                continue
            ch["id"] = cid
            feed = parse_feed(fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"), f"YouTube {ch.get('handle', cid)}")
            items += [i for i in feed if re.search(cfg.get("filtro_youtube", "gta"), i["title"], re.I)]
        except Exception as e:
            log(f"[aviso] canal {ch.get('handle')}: {e}")
    for sub in cfg.get("reddit", []):
        try:
            items += parse_feed(fetch(f"https://www.reddit.com/r/{sub}/top/.rss?t=day"), f"Reddit r/{sub}")
        except Exception as e:
            log(f"[aviso] reddit {sub}: {e}")
    return items


def update(items: list[dict], out_dir: Path = OUT, now: dt.datetime | None = None) -> list[dict]:
    """Deduplica contra lo ya visto, clasifica y escribe los informes. Devuelve las novedades."""
    now = now or dt.datetime.now(dt.timezone(dt.timedelta(hours=1)))
    out_dir.mkdir(parents=True, exist_ok=True)
    seen_p = out_dir / "vistos.json"
    seen = json.loads(seen_p.read_text()) if seen_p.exists() else []
    seen_set = set(seen)
    new = []
    for it in items:
        k = item_id(it["url"])
        if k in seen_set:
            continue
        seen_set.add(k)
        seen.append(k)
        cat, score = classify(it["title"])
        new.append({**it, "categoria": cat, "potencial": score})
    seen_p.write_text(json.dumps(seen[-3000:]))
    new.sort(key=lambda x: -x["potencial"])
    stamp = now.strftime("%H:%M")
    day = out_dir / f"{now:%Y-%m-%d}.md"
    if not day.exists():
        day.write_text(
            f"# Radar GTA VI · {now:%d-%m-%Y} (hora de España)\nSolo títulos y enlaces para investigar: no descargar ni reutilizar material ajeno sin permiso.\n\n"
            "| Hora | Potencial | Categoría | Título | Fuente |\n|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    with open(day, "a", encoding="utf-8") as fh:
        for i in new:
            title = i["title"].replace("|", "/")[:140]
            fh.write(f"| {stamp} | {'★' * min(i['potencial'], 5) or '·'} | {i['categoria']} | [{title}]({i['url']}) | {i['source']} |\n")
    if not new:  # sin novedades: se conserva la lista anterior
        return new
    top = new[:15]
    lines = [
        f"# Última pasada del radar: {now:%d-%m %H:%M}",
        f"{len(new)} novedades. Las 15 con más potencial para un '¿Sabías que…?':",
        "",
    ]
    lines += [
        f"- {'★' * min(i['potencial'], 5) or '·'} **{i['categoria']}** · [{i['title'][:120]}]({i['url']}) · {i['source']}" for i in top
    ]
    (out_dir / "ultimo.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return new


def run(cfg_path: str | Path = rutas.CONFIG_RADAR) -> int:
    p = Path(cfg_path)
    cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
    new = update(collect(cfg))
    p.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")  # guarda ids de canal resueltos
    print(f"{len(new)} novedades")
    return 0
