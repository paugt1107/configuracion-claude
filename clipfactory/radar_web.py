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
import os
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
    ("misión", r"misi[oó]n|miss[aã]o|mission|missione|golpe|heist|atraco|braquage|raub"),
    ("personaje", r"lucia|jason|cal hampton|boobie|dre'?quan|real dimez|raul bautista|brian heder|personaje|character"),
    (
        "secreto",
        r"secret|segredo|segreto|geheim|easter ?egg|oculto|escondid|hidden|cach[ée]|detalle|detail|curiosi|sab[ií]as|did you know|sabia que|saviez",
    ),
    (
        "truco",
        r"truco|trick|tip|astuce|trucco|tipp|consejo|gu[ií]a|guide|c[oó]mo (conseguir|desbloquear|hacer)|how to|dinero|dinheiro|money|argent|coche|car|carro|voiture",
    ),
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
    for loc in cfg.get("idiomas", [{"hl": "es", "gl": "ES"}]):
        hl, gl = loc["hl"], loc["gl"]
        for q in loc.get("busquedas") or cfg.get("google_news", []):
            url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
                {"q": q, "hl": hl, "gl": gl, "ceid": f"{gl}:{hl.split('-')[0]}"}
            )
            try:
                items += [{**i, "lang": hl} for i in parse_feed(fetch(url), f"Google {hl}-{gl}: {q}")]
            except Exception as e:  # una fuente caída no para el radar
                log(f"[aviso] Google News {hl}-{gl} '{q}': {e}")
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
    for q in cfg.get("bluesky", []):
        try:
            data = json.loads(
                fetch(
                    "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?"
                    + urllib.parse.urlencode({"q": q, "limit": 40, "sort": "top"})
                )
            )
            items += parse_bluesky(data, q)
        except Exception as e:
            log(f"[aviso] Bluesky '{q}': {e}")
    for inst, tag in [(m["instancia"], m["etiqueta"]) for m in cfg.get("mastodon", [])]:
        try:
            items += parse_mastodon(json.loads(fetch(f"https://{inst}/api/v1/timelines/tag/{tag}?limit=40")), f"Mastodon #{tag}")
        except Exception as e:
            log(f"[aviso] Mastodon {inst} #{tag}: {e}")
    token = os.environ.get("X_BEARER_TOKEN")
    if token:  # X/Twitter: solo con API de pago (recent search)
        for q in cfg.get("x", []):
            try:
                req = urllib.request.Request(
                    "https://api.x.com/2/tweets/search/recent?"
                    + urllib.parse.urlencode(
                        {"query": f"{q} -is:retweet", "max_results": 50, "tweet.fields": "lang,public_metrics,created_at"}
                    ),
                    headers={"Authorization": f"Bearer {token}", "User-Agent": UA},
                )
                with urllib.request.urlopen(req, timeout=20) as r:
                    items += parse_x(json.loads(r.read()), q)
            except Exception as e:
                log(f"[aviso] X '{q}': {e}")
    return items


def _clip_text(text: str, n: int = 140) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


def parse_bluesky(data: dict, q: str) -> list[dict]:
    out = []
    for p in data.get("posts", []):
        uri, handle = p.get("uri", ""), p.get("author", {}).get("handle", "")
        rkey = uri.rsplit("/", 1)[-1]
        txt = p.get("record", {}).get("text", "")
        likes = p.get("likeCount", 0) + 2 * p.get("repostCount", 0)
        if txt and rkey:
            out.append(
                {
                    "title": _clip_text(txt),
                    "url": f"https://bsky.app/profile/{handle}/post/{rkey}",
                    "date": p.get("indexedAt", ""),
                    "source": f"Bluesky ({likes}❤)",
                    "lang": (p.get("record", {}).get("langs") or ["?"])[0],
                    "eng": likes,
                }
            )
    return out


def parse_mastodon(data: list, source: str) -> list[dict]:
    out = []
    for s in data:
        txt = re.sub(r"<[^>]+>", " ", s.get("content", ""))
        if txt.strip():
            out.append(
                {
                    "title": _clip_text(txt),
                    "url": s.get("url", ""),
                    "date": s.get("created_at", ""),
                    "source": source,
                    "lang": s.get("language") or "?",
                    "eng": s.get("favourites_count", 0) + 2 * s.get("reblogs_count", 0),
                }
            )
    return [i for i in out if i["url"]]


def parse_x(data: dict, q: str) -> list[dict]:
    out = []
    for tw in data.get("data", []):
        m = tw.get("public_metrics", {})
        eng = m.get("like_count", 0) + 2 * m.get("retweet_count", 0)
        out.append(
            {
                "title": _clip_text(tw.get("text", "")),
                "url": f"https://x.com/i/web/status/{tw['id']}",
                "date": tw.get("created_at", ""),
                "source": f"X ({eng}❤)",
                "lang": tw.get("lang", "?"),
                "eng": eng,
            }
        )
    return out


HISTORIA = re.compile(
    r"modo historia|story mode|historia|story|misi[oó]n|missions?|cap[ií]tulo|chapter|final\b|ending|walkthrough|gu[ií]a|"
    r"duraci[oó]n|how long|horas|hours|campa[ñn]a|campaign|spoiler|personajes?|characters?|villano|villain|jefe final|boss",
    re.I,
)


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
        score += min(3, int(it.get("eng", 0)) // 200)  # interacción en redes
        new.append({**it, "categoria": cat, "potencial": score, "lang": it.get("lang", "es")})
    seen_p.write_text(json.dumps(seen[-3000:]))
    new.sort(key=lambda x: -x["potencial"])
    stamp = now.strftime("%H:%M")
    day = out_dir / f"{now:%Y-%m-%d}.md"
    if not day.exists():
        day.write_text(
            f"# Radar GTA VI · {now:%d-%m-%Y} (hora de España)\nSolo títulos y enlaces para investigar: no descargar ni reutilizar material ajeno sin permiso.\n\n"
            "| Hora | Potencial | Idioma | Categoría | Título | Fuente |\n|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    with open(day, "a", encoding="utf-8") as fh:
        for i in new:
            if i["potencial"] < 3:  # el archivo del día solo guarda lo que tiene potencial (antes crecía ~3,5 MB/día)
                continue
            title = i["title"].replace("|", "/")[:140]
            fh.write(
                f"| {stamp} | {'★' * min(i['potencial'], 5) or '·'} | {i['lang']} | {i['categoria']} | [{title}]({i['url']}) | {i['source']} |\n"
            )
    # MODO HISTORIA: todo lo que hable de misiones, capítulos, final, duración… va a historia.md (acumulado)
    hist = [i for i in new if HISTORIA.search(i["title"])]
    if hist:
        hp = out_dir / "historia.md"
        if not hp.exists():
            hp.write_text(
                "# Radar · MODO HISTORIA de GTA VI (Valentín)\nTitulares sobre misiones, capítulos, final, duración y personajes. "
                "⚠️ SPOILERS: no usarlos en título/portada/primeros 3 s hasta el 3-dic-2026. Resumen verificado: "
                "`canal-youtube/investigacion/modo-historia.md`.\n\n| Fecha | Idioma | Título | Fuente |\n|---|---|---|---|\n",
                encoding="utf-8",
            )
        with open(hp, "a", encoding="utf-8") as fh:
            for i in hist:
                fh.write(f"| {now:%d-%m %H:%M} | {i['lang']} | [{i['title'].replace('|', '/')[:140]}]({i['url']}) | {i['source']} |\n")
        lineas = hp.read_text(encoding="utf-8").splitlines()
        if len(lineas) > 205:  # solo los 200 titulares más recientes (lo que se lee tiene que ser corto)
            hp.write_text("\n".join(lineas[:5] + lineas[-200:]) + "\n", encoding="utf-8")
    for viejo in sorted(out_dir.glob("20??-??-??.md"))[:-2]:  # solo hoy y ayer
        viejo.unlink()
    if not new:  # sin novedades: se conserva la lista anterior
        return new
    top = new[:25]
    lines = [
        f"# Última pasada del radar: {now:%d-%m %H:%M}",
        f"{len(new)} novedades. Las 25 con más potencial para un '¿Sabías que…?':",
        "",
    ]
    lines += [
        f"- {'★' * min(i['potencial'], 5) or '·'} `{i['lang']}` **{i['categoria']}** · [{i['title'][:120]}]({i['url']}) · {i['source']}"
        for i in top
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
