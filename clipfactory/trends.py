"""Radar de tendencias con la API oficial YouTube Data v3 (requiere YOUTUBE_API_KEY).

Busca Shorts recientes de un tema, calcula para cada vídeo el múltiplo de vistas sobre la MEDIANA del
propio canal (no tamaño del canal) y marca ALARMA si el múltiplo >= umbral (10x por defecto).
Coste aproximado de cuota: 100 (search) + ~3 por canal.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import statistics
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://www.googleapis.com/youtube/v3/"


def _get(endpoint: str, **params) -> dict:
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("Define YOUTUBE_API_KEY (clave de la YouTube Data API v3).")
    params["key"] = key
    with urllib.request.urlopen(API + endpoint + "?" + urllib.parse.urlencode(params), timeout=30) as r:
        return json.loads(r.read().decode())


def multiple(views: int, channel_views: list[int]) -> float | None:
    """Múltiplo sobre la mediana del canal; None si hay menos de 4 vídeos (mediana poco fiable)."""
    vals = [v for v in channel_views if v is not None]
    if len(vals) < 4:
        return None
    med = statistics.median(vals)
    return round(views / med, 2) if med > 0 else None


def rank(videos: list[dict], channel_history: dict[str, list[int]], alarm: float = 10.0) -> list[dict]:
    out = []
    for v in videos:
        m = multiple(v["views"], channel_history.get(v["channel_id"], []))
        out.append({**v, "multiplo": m, "alarma": bool(m and m >= alarm)})
    out.sort(key=lambda x: (x["multiplo"] is None, -(x["multiplo"] or 0), -x["views"]))
    return out


def _video_stats(ids: list[str]) -> dict[str, dict]:
    out = {}
    for i in range(0, len(ids), 50):
        data = _get("videos", part="statistics,snippet,contentDetails", id=",".join(ids[i:i + 50]))
        for it in data.get("items", []):
            out[it["id"]] = it
    return out


def scan(query: str, days: int = 7, region: str = "ES", lang: str = "es", max_results: int = 50, alarm: float = 10.0) -> list[dict]:
    after = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    found = _get("search", part="snippet", q=query, type="video", videoDuration="short", order="viewCount",
                 publishedAfter=after, regionCode=region, relevanceLanguage=lang, maxResults=max_results)
    ids = [it["id"]["videoId"] for it in found.get("items", [])]
    stats = _video_stats(ids)
    videos, chans = [], set()
    for vid, it in stats.items():
        chans.add(it["snippet"]["channelId"])
        videos.append({"id": vid, "url": f"https://www.youtube.com/shorts/{vid}", "title": it["snippet"]["title"],
                       "channel": it["snippet"]["channelTitle"], "channel_id": it["snippet"]["channelId"],
                       "published": it["snippet"]["publishedAt"], "views": int(it["statistics"].get("viewCount", 0))})
    history: dict[str, list[int]] = {}
    for ch in chans:
        info = _get("channels", part="contentDetails", id=ch)
        items = info.get("items") or []
        if not items:
            continue
        uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        pl = _get("playlistItems", part="contentDetails", playlistId=uploads, maxResults=20)
        vids = [p["contentDetails"]["videoId"] for p in pl.get("items", [])]
        history[ch] = [int(s["statistics"].get("viewCount", 0)) for s in _video_stats(vids).values()]
    return rank(videos, history, alarm)


def report_markdown(query: str, ranked: list[dict], alarm: float = 10.0) -> str:
    today = dt.date.today().isoformat()
    lines = [f"# Radar de tendencias: \"{query}\" ({today})", "", f"Múltiplo = vistas / mediana de los últimos vídeos del canal. ALARMA si >= {alarm:g}x.", "",
             "| # | Múltiplo | Vistas | Título | Canal | Enlace |", "|---|---|---|---|---|---|"]
    for i, v in enumerate(ranked[:25], 1):
        m = f"{v['multiplo']:g}x" if v["multiplo"] is not None else "s/d"
        flag = " 🚨" if v["alarma"] else ""
        title = v["title"].replace("|", "/")
        lines.append(f"| {i} | {m}{flag} | {v['views']:,} | {title} | {v['channel']} | {v['url']} |")
    lines += ["", "Nota: el múltiplo describe el rendimiento, no explica por qué funcionó. Los datos de otros canales se usan solo para análisis; no se descargan ni resuben sus vídeos."]
    return "\n".join(lines) + "\n"


def save(query: str, ranked: list[dict], out_dir: str | Path = "canal-youtube/data/trends", alarm: float = 10.0,
         alerts_file: str | Path = "canal-youtube/data/alertas.md") -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    slug = "".join(c if c.isalnum() else "-" for c in query.lower()).strip("-")
    (out_dir / f"{today}-{slug}.json").write_text(json.dumps(ranked, ensure_ascii=False, indent=1), encoding="utf-8")
    md = out_dir / f"{today}-{slug}.md"
    md.write_text(report_markdown(query, ranked, alarm), encoding="utf-8")
    alarms = [v for v in ranked if v["alarma"]]
    if alarms and Path(alerts_file).exists():
        with open(alerts_file, "a", encoding="utf-8") as fh:
            for v in alarms:
                fh.write(f"\n- [{today}] ALARMA {v['multiplo']:g}x · {v['title']} · {v['channel']} · {v['url']} (radar: {query})")
    return md
