"""TOMMY · Imágenes que aparecen JUSTO cuando la voz nombra algo (estilo edición de TikTok).

1. detectar(): busca en las palabras de la locución (con tiempos) entidades conocidas: países → bandera, dinero → bolsa,
   policía → estrellas, coche, mapa/lugares, móvil/redes, récord/ventas → trofeo, Lucía/Jason → recorte, lugares reales → foto libre.
2. planificar(): elige qué mostrar y cuándo (sin saturar: separación mínima y sin repetir lo mismo seguido).
3. preparar(): convierte cada visual en un PNG listo para superponer (pop-in de ~1,3 s en el centro de la pantalla).
Las reglas extra del canal se añaden en canal-youtube/fuentes/visuales.yaml.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFilter

from . import motion, props, rutas

DEFAULTS: list[tuple[str, dict]] = [
    (r"\bespana\b|\bespanol(es|a)?\b", {"bandera": "es"}),
    (r"\bmexico\b|\bmexican", {"bandera": "mx"}),
    (r"\bargentin", {"bandera": "ar"}),
    (r"nueva zelanda", {"bandera": "nz"}),
    (r"estados unidos|\bee ?uu\b|\beeuu\b|\busa\b|americano", {"bandera": "us"}),
    (r"\bdinero\b|\bdolares?\b|\bmillon(es)?\b|\bpasta\b|\bfortuna\b|\bpresupuesto\b", {"prop": "dinero"}),
    (r"\bbilletes?\b|\bprecio\b|\bcuesta\b|\bpagar\b|\bcobra", {"prop": "billetes"}),
    (r"\bpolic[ií]a\b|\bpoli\b|\bbusqueda\b|\bestrellas?\b|\bpersecuci", {"prop": "estrellas", "n": 4}),
    (r"\bsirenas?\b|\bpatrulla\b|\barresto\b|\bdetenid", {"prop": "sirena"}),
    (r"\bcoches?\b|\bvehiculos?\b|\bcarros?\b|\bdeportivo\b|\bconducir\b", {"prop": "coche"}),
    (r"\bmapa\b|\bubicacion\b|\blugar\b|\bvice city\b|\bleonida\b|\bdonde\b", {"prop": "pin"}),
    (r"\bmovil\b|\btelefono\b|\bredes\b|\binternet\b|\btiktok\b|\binstagram\b|\bapp\b", {"prop": "movil"}),
    (r"\brecord\b|\bventas\b|\bpremio\b|\bnumero uno\b|\bel mejor\b|\btrofeo\b", {"prop": "trofeo"}),
    (r"\bhoras?\b|\bminutos\b|\bduracion\b|\bdura\b|\btiempo\b|\bmilisegundos\b", {"prop": "reloj"}),
    (r"\bconsolas?\b|\bmando\b|\bjugadores?\b|\bpartida\b", {"prop": "mando"}),
    (r"\bnota\b|\bresenas?\b|\bcriticas?\b|\bpuntuacion\b|\bcalificacion\b", {"prop": "nota"}),
    (r"\bmetacritic\b", {"chip": "METACRITIC", "color": "gold"}),
    (r"\bzelda\b|\bocarina\b", {"chip": "ZELDA", "color": "cyan"}),
    (r"\bps ?(cinco|5)\b|\bplaystation\b", {"chip": "PS5", "color": "cyan"}),
    (r"\bxbox\b", {"chip": "XBOX", "color": "cyan"}),
    (r"\bpc\b|\bordenador\b", {"chip": "PC", "color": "white"}),
    (r"\bfps\b|\bfotogramas\b|imagenes por segundo", {"chip": "FPS", "color": "orange"}),
    (r"\bprocesador\b|\bcpu\b", {"chip": "CPU", "color": "magenta"}),
    (r"\brockstar\b", {"chip": "ROCKSTAR", "color": "gold"}),
    (r"\bred dead\b", {"chip": "RED DEAD 2", "color": "magenta"}),
    (r"\bgta (cuatro|4|iv)\b", {"chip": "GTA IV", "color": "white"}),
    (r"\bgta (cinco|5|v)\b", {"chip": "GTA V", "color": "white"}),
    (r"new york times|\bperiodico\b|\bentrevista\b", {"chip": "PRENSA", "color": "white"}),
    (r"\btrailer\b", {"chip": "TRÁILER", "color": "magenta"}),
    (r"\bcomentarios?\b|\bcomenta\b", {"chip": "COMENTA", "color": "orange"}),
    (r"\blucia\b", {"recorte": "media/recortes/lucia.png", "alt": {"prop": "estrellas", "n": 2}}),
    (r"\bjason\b", {"recorte": "media/recortes/jason.png", "alt": {"prop": "estrellas", "n": 2}}),
]


def norm(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def reglas(path: Path = rutas.FUENTES / "visuales.yaml") -> list[tuple[str, dict]]:
    extra = []
    if Path(path).exists():
        cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        extra = [(r["patron"], r["visual"]) for r in cfg.get("extra") or []]
    return extra + DEFAULTS  # las del canal tienen prioridad


def detectar(words: list[dict], rules: list[tuple[str, dict]] | None = None) -> list[dict]:
    """Devuelve [{t, visual, palabra}] buscando cada regla en ventanas de 1-3 palabras."""
    rules = rules or reglas()
    toks = [norm(re.sub(r"[^\w\s$]", "", w["text"])) for w in words]
    hits, used = [], set()
    for i in range(len(words)):
        for n in (1, 2, 3):
            if i + n > len(words) or any(j in used for j in range(i, i + n)):
                continue
            frag = " ".join(toks[i : i + n])
            rest = " ".join(toks[i + 1 : i + n])
            for pat, vis in rules:
                # la imagen sale en la PRIMERA palabra que la nombra (no antes)
                if re.search(pat, frag) and not (n > 1 and re.search(pat, rest)):
                    hits.append({"t": words[i]["start"], "visual": vis, "palabra": " ".join(w["text"] for w in words[i : i + n])})
                    used.update(range(i, i + n))
                    break
            else:
                continue
            break
    return hits


def planificar(hits: list[dict], dur: float = 1.3, gap: float = 1.6, repeat_gap: float = 6.0, skip_start: float = 0.8) -> list[dict]:
    plan, last_t, last_seen = [], -99.0, {}
    for h in sorted(hits, key=lambda x: x["t"]):
        key = str(sorted(h["visual"].items()))
        if h["t"] < skip_start or h["t"] - last_t < gap or h["t"] - last_seen.get(key, -99) < repeat_gap:
            continue
        plan.append({**h, "dur": dur})
        last_t, last_seen[key] = h["t"], h["t"]
    return plan


def _marco(im: Image.Image, maxw: int = 640, maxh: int = 520, borde: int = 12) -> Image.Image:
    """Foto con borde blanco, esquinas redondeadas y sombra (estilo pegatina)."""
    im = im.convert("RGB")
    k = min(maxw / im.width, maxh / im.height)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    w, h = im.width + 2 * borde, im.height + 2 * borde
    card = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 26, w + 20, h + 26], 26, fill=(0, 0, 0, 150))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    ImageDraw.Draw(card).rounded_rectangle([20, 20, w + 20, h + 20], 26, fill=(255, 255, 255, 255))
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], 18, fill=255)
    card.paste(im, (20 + borde, 20 + borde), mask)
    return card


def _render(vis: dict, creditos: list[str]) -> Image.Image | None:
    if "recorte" in vis:
        if Path(vis["recorte"]).exists():
            fig = Image.open(vis["recorte"]).convert("RGBA")
            k = 620 / fig.height
            return fig.resize((int(fig.width * k), 620), Image.LANCZOS)
        vis = vis.get("alt") or {}
    if "imagen" in vis and Path(vis["imagen"]).exists():
        return _marco(Image.open(vis["imagen"]))
    if "libre" in vis:
        try:
            from . import libres

            r = libres.buscar(vis["libre"])
        except Exception:  # sin red / sin resultado: se omite
            r = None
        if r:
            creditos.append(r[1])
            return _marco(Image.open(r[0]))
        return None
    if "chip" in vis:
        acc = motion.COLORS.get(vis.get("color", "orange"), motion.ORANGE)
        f = motion._font(120)
        txt = vis["chip"]
        tw = int(ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(txt, font=f))
        w, h = min(900, tw + 120), 200
        canvas = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([30, 38, w + 30, h + 38], 34, fill=(0, 0, 0, 160))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle([30, 30, w + 30, h + 30], 34, fill=(15, 15, 22, 240), outline=acc + (255,), width=10)
        txt, sz = motion._fit(d, txt, 120, w - 60)
        d.multiline_text((30 + w / 2, 30 + h / 2), txt, font=motion._font(sz), fill=acc, anchor="mm", align="center")
        return canvas.rotate(-4, resample=Image.BICUBIC, expand=True)
    if "bandera" in vis:
        fl = motion.flag(vis["bandera"], 480)
        canvas = Image.new("RGBA", (fl.width + 40, fl.height + 40), (0, 0, 0, 0))
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([20, 26, fl.width + 20, fl.height + 26], 20, fill=(0, 0, 0, 140))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        canvas.alpha_composite(fl, (20, 20))
        return canvas
    if "prop" in vis:
        im = props.draw(vis["prop"], 360, int(vis.get("n", 3)))
        if im.width > 700:
            im = im.resize((700, int(im.height * 700 / im.width)), Image.LANCZOS)
        glow = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
        halo = Image.new("RGBA", im.size, (255, 194, 75, 0))
        halo.putalpha(im.split()[3])
        glow.alpha_composite(halo, (40, 40))
        glow = glow.filter(ImageFilter.GaussianBlur(18))
        glow.alpha_composite(im, (40, 40))
        return glow
    return None


def preparar(plan: list[dict], workdir: Path) -> tuple[list[dict], list[str]]:
    """PNG por visual. Devuelve (overlays [{png, t, dur}], créditos de imágenes libres)."""
    workdir.mkdir(parents=True, exist_ok=True)
    overlays, creditos = [], []
    for i, p in enumerate(plan):
        im = _render(p["visual"], creditos)
        if im is None:
            continue
        png = workdir / f"pop{i:02d}.png"
        im.save(png)
        overlays.append({"png": str(png), "t": round(p["t"], 3), "dur": p["dur"], "palabra": p["palabra"]})
    return overlays, creditos
