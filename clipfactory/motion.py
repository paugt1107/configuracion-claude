"""Animatic de gráficos en movimiento (sin fuente de vídeo ajena): tarjetas neón 1080x1920 + zoom suave + subtítulos.

Sirve para Shorts originales (cuenta atrás, horarios, datos) donde no hay gameplay. Cada escena es una tarjeta PNG
dibujada con PIL (brillo neón) que ffmpeg anima con zoom lento y entrada con fundido; después se concatenan y se
queman los subtítulos palabra a palabra.

Uso (desde Python): build(escenas, palabras, salida). Ver canal-youtube/jobs/s001_motion.py
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import captions, media

W, H = 1080, 1920
NAVY, CHARCOAL = (11, 22, 48), (20, 22, 28)
ORANGE, CYAN, MAGENTA, WHITE, GOLD = (255, 122, 26), (25, 211, 255), (255, 46, 147), (255, 255, 255), (255, 194, 75)
COLORS = {"orange": ORANGE, "cyan": CYAN, "magenta": MAGENTA, "white": WHITE, "gold": GOLD}
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


def _font(size: int) -> ImageFont.FreeTypeFont:
    path = media.find_font() or FONT_BOLD
    return ImageFont.truetype(path, size)


def _bg(accent=ORANGE) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    px = ImageDraw.Draw(img)
    for y in range(H):  # degradado vertical navy -> carbón
        t = y / H
        px.line([(0, y), (W, y)], fill=tuple(int(NAVY[i] * (1 - t) + CHARCOAL[i] * t) for i in range(3)))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-200, 1250, W + 200, 2400], fill=tuple(int(c * 0.55) for c in accent))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    return Image.blend(img, Image.composite(glow, img, glow.convert("L")), 0.55)


def _glow_text(img, xy, text, size, color, anchor="mm", spread=22, stroke=0):
    layer = Image.new("RGB", img.size, (0, 0, 0))
    ImageDraw.Draw(layer).text(xy, text, font=_font(size), fill=color, anchor=anchor)
    blur = layer.filter(ImageFilter.GaussianBlur(spread))
    img.paste(Image.composite(blur, img, blur.convert("L").point(lambda v: min(255, v * 2))), (0, 0))
    ImageDraw.Draw(img).text(xy, text, font=_font(size), fill=WHITE if color != WHITE else WHITE, anchor=anchor,
                             stroke_width=stroke, stroke_fill=color)
    ImageDraw.Draw(img).text(xy, text, font=_font(size), fill=color, anchor=anchor)


def _fit(d, text, size, maxw):
    """Reduce el tamaño o parte el texto en 2 líneas para que quepa en maxw px."""
    def width(txt, sz):
        return max(d.textlength(line, font=_font(sz)) for line in txt.split("\n"))

    s = size
    while s > 40 and width(text, s) > maxw:
        s -= 4
    if width(text, s) <= maxw or "\n" in text:
        return text, s
    words = text.split()
    best = (text, 56)
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        if width(a, size) <= maxw and width(b, size) <= maxw:
            return a + "\n" + b, size
        best = (a + "\n" + b, 56)
    return best


def _label(img, xy, text, size, color=WHITE, anchor="mm", box=True, maxw=900):
    d = ImageDraw.Draw(img)
    text, size = _fit(d, text, size, maxw)
    f = _font(size)
    kw = {"align": "center", "spacing": 14} if "\n" in text else {}
    if box:
        x0, y0, x1, y1 = d.multiline_textbbox(xy, text, font=f, anchor=anchor, **kw)
        pad = 24
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).rounded_rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad], 22, fill=(0, 0, 0, 150))
        img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"))
        d = ImageDraw.Draw(img)
    d.multiline_text(xy, text, font=f, fill=color, anchor=anchor, **kw)


# ---------- Banderas dibujadas (simplificadas, sin escudos) ----------
def _star(draw, cx, cy, r, fill, outline=None, ow=0):
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill, outline=outline, width=ow)


def flag(code: str, w: int = 480) -> Image.Image:
    """Bandera RGBA de ancho w. Códigos: nz, es, mx, ar. Dibujo a 3x y reducción (bordes suaves)."""
    k = 3
    ratios = {"nz": 0.5, "es": 2 / 3, "mx": 4 / 7, "ar": 5 / 8}
    h = int(w * ratios[code])
    W2, H2 = w * k, h * k
    im = Image.new("RGB", (W2, H2), (255, 255, 255))
    d = ImageDraw.Draw(im)
    if code == "es":
        d.rectangle([0, 0, W2, H2 // 4], fill=(170, 21, 27))
        d.rectangle([0, H2 // 4, W2, H2 * 3 // 4], fill=(241, 191, 0))
        d.rectangle([0, H2 * 3 // 4, W2, H2], fill=(170, 21, 27))
    elif code == "mx":
        t3 = W2 // 3
        d.rectangle([0, 0, t3, H2], fill=(0, 104, 71))
        d.rectangle([2 * t3, 0, W2, H2], fill=(206, 17, 38))
        cx, cy, r = W2 // 2, H2 // 2, H2 // 7
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(140, 100, 40))
        d.ellipse([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], fill=(110, 140, 70))
    elif code == "ar":
        d.rectangle([0, 0, W2, H2], fill=(116, 172, 223))
        d.rectangle([0, H2 // 3, W2, H2 * 2 // 3], fill=(255, 255, 255))
        import math
        cx, cy, r = W2 // 2, H2 // 2, H2 // 10
        for i in range(16):
            a = i * math.pi / 8
            d.polygon([(cx + (r * 1.0) * math.cos(a - .09), cy + (r * 1.0) * math.sin(a - .09)),
                       (cx + (r * 1.75) * math.cos(a), cy + (r * 1.75) * math.sin(a)),
                       (cx + (r * 1.0) * math.cos(a + .09), cy + (r * 1.0) * math.sin(a + .09))], fill=(246, 180, 14))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(246, 180, 14))
    elif code == "nz":
        d.rectangle([0, 0, W2, H2], fill=(0, 36, 125))
        cw, ch = W2 // 2, H2 // 2  # cantón (Union Jack simplificada)
        d.rectangle([0, 0, cw, ch], fill=(1, 33, 105))
        d.line([(0, 0), (cw, ch)], fill=(255, 255, 255), width=int(ch * 0.2))
        d.line([(0, ch), (cw, 0)], fill=(255, 255, 255), width=int(ch * 0.2))
        d.line([(0, 0), (cw, ch)], fill=(200, 16, 46), width=int(ch * 0.07))
        d.line([(0, ch), (cw, 0)], fill=(200, 16, 46), width=int(ch * 0.07))
        d.rectangle([cw // 2 - ch * 0.17, 0, cw // 2 + ch * 0.17, ch], fill=(255, 255, 255))
        d.rectangle([0, ch // 2 - ch * 0.17, cw, ch // 2 + ch * 0.17], fill=(255, 255, 255))
        d.rectangle([cw // 2 - ch * 0.09, 0, cw // 2 + ch * 0.09, ch], fill=(200, 16, 46))
        d.rectangle([0, ch // 2 - ch * 0.09, cw, ch // 2 + ch * 0.09], fill=(200, 16, 46))
        for fx, fy, fr in ((0.775, 0.22, 0.095), (0.775, 0.80, 0.11), (0.655, 0.50, 0.085), (0.89, 0.43, 0.085)):
            _star(d, W2 * fx, H2 * fy, H2 * fr * 1.28, (255, 255, 255))
            _star(d, W2 * fx, H2 * fy, H2 * fr, (200, 16, 46))
    im = im.resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], int(h * 0.07), fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def _paste_flag(img, code, cx, cy, w):
    fl = flag(code, w)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([cx - w // 2 - 8, cy - fl.height // 2 - 8, cx + w // 2 + 8, cy + fl.height // 2 + 8], 18, fill=(255, 255, 255, 40))
    base = Image.alpha_composite(img.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(14)))
    base.alpha_composite(fl, (cx - fl.width // 2, cy - fl.height // 2))
    img.paste(base.convert("RGB"))


def card(spec: dict) -> Image.Image:
    """spec: {fondo, reloj, reloj_color, titulo, sub, extra:[(texto, color)], barra, kind}"""
    accent = COLORS.get(spec.get("color", "orange"), ORANGE)
    img = _bg(accent)
    kind = spec.get("kind", "clock")
    d = ImageDraw.Draw(img)
    if kind == "clock" and spec.get("bandera"):
        _paste_flag(img, spec["bandera"], W // 2, 700, 520)
        _glow_text(img, (W // 2, 1010), spec["reloj"], 250, accent)
        if spec.get("sub"):
            _label(img, (W // 2, 1190), spec["sub"], 46, CYAN, box=False)
    elif kind == "clock":
        _glow_text(img, (W // 2, 800), spec["reloj"], 300, accent)
        if spec.get("sub"):
            _label(img, (W // 2, 1010), spec["sub"], 52, CYAN)
    elif kind == "three":
        for i, row in enumerate(spec["relojes"]):
            t, tag = row[0], row[1]
            y = 520 + i * 250
            if len(row) > 2:
                _paste_flag(img, row[2], 190, y, 220)
            _glow_text(img, (W // 2 + (110 if len(row) > 2 else 0), y), t, 170, CYAN, spread=16)
            _label(img, (W // 2 + (110 if len(row) > 2 else 0), y + 118), tag, 40, WHITE, box=False)
    elif kind == "split":
        d.line([(120, 880), (W - 120, 880)], fill=(60, 80, 130), width=4)
        ox = 130 if spec.get("bandera") else 0
        if spec.get("bandera"):
            _paste_flag(img, spec["bandera"], 190, 640, 220)
            _paste_flag(img, spec["bandera2"], 190, 1010, 220)
        _glow_text(img, (W // 2 + ox, 640), spec["reloj"], 210, accent)
        _label(img, (W // 2 + ox, 780), spec["sub"], 44, CYAN, box=False)
        _glow_text(img, (W // 2 + ox, 1010), spec["reloj2"], 210, GOLD)
        _label(img, (W // 2 + ox, 1150), spec["sub2"], 44, GOLD, box=False)
    elif kind == "timeline":
        y = 960
        d.line([(110, y), (W - 110, y)], fill=(80, 105, 160), width=8)
        for i in range(9):
            x = 110 + i * (W - 220) / 8
            d.line([(x, y - 20), (x, y + 20)], fill=(80, 105, 160), width=5)
        for x, lab, col in ((300, "23:00 UTC\nDÍA 18", CYAN), (780, "00:00\nESPAÑA · DÍA 19", ORANGE)):
            d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=col)
            _label(img, (x, y - 140), lab, 46, col, box=False)
        d.line([(335, y - 60), (745, y - 60)], fill=GOLD, width=6)
    elif kind == "bar":
        d.rounded_rectangle([140, 760, W - 140, 860], 40, outline=(80, 105, 160), width=6)
        d.rounded_rectangle([150, 770, W - 150, 850], 32, fill=(70, 220, 130))
        _label(img, (W // 2, 810), "100%", 52, NAVY, box=False)
        _glow_text(img, (W // 2, 1050), "🔒" if False else "BLOQUEADO", 120, MAGENTA, spread=14)
    if spec.get("titulo"):
        _label(img, (W // 2, spec.get("ty", 500)), spec["titulo"], spec.get("tsize", 84), WHITE)
    if spec.get("pie"):
        _label(img, (W // 2, 1300), spec["pie"], 50, accent, box=False)
    return img


def _clip(png: Path, dur: float, out: Path, i: int):
    n = max(1, int(dur * 30))
    zoom = "zoompan=z='1+0.06*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=%d:s=%dx%d:fps=30" % (n, n, W, H)
    subprocess.run([media.require("ffmpeg"), "-y", "-loglevel", "error", "-loop", "1", "-i", str(png), "-vf",
                    f"scale=2160:3840,{zoom},fade=t=in:st=0:d=0.12,format=yuv420p", "-t", f"{dur}", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "19", str(out)], check=True)


def estimate_words(text: str, total_s: float, lead: float = 0.2) -> list[dict]:
    toks = text.split()
    weights = [len(t) + 2 for t in toks]
    scale = (total_s - lead - 0.3) / sum(weights)
    t, out = lead, []
    for tok, w in zip(toks, weights):
        out.append({"text": tok, "start": round(t, 3), "end": round(t + w * scale * 0.92, 3)})
        t += w * scale
    return out


def build(scenes: list[dict], words: list[dict], out: str | Path, audio: str | None = None) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="motion-") as tmp:
        tmp = Path(tmp)
        lst = []
        for i, sc in enumerate(scenes):
            png, clip = tmp / f"s{i:02d}.png", tmp / f"s{i:02d}.mp4"
            card(sc).save(png)
            _clip(png, float(sc["dur"]), clip, i)
            lst.append(f"file '{clip}'")
        (tmp / "list.txt").write_text("\n".join(lst), encoding="utf-8")
        base = tmp / "base.mp4"
        subprocess.run([media.require("ffmpeg"), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                        "-c", "copy", str(base)], check=True)
        ass = tmp / "subs.ass"
        ass.write_text(captions.build_ass(words), encoding="utf-8")
        esc = str(ass).replace(":", r"\:")
        cmd = [media.require("ffmpeg"), "-y", "-loglevel", "error", "-i", str(base)]
        if audio:
            cmd += ["-i", audio]
        cmd += ["-vf", f"subtitles='{esc}'", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
        # voz: quita graves de ambiente, reduce ruido de fondo y normaliza a -14 LUFS (estándar de Shorts/TikTok)
        cmd += (["-af", "highpass=f=80,afftdn=nf=-25,loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
                 "-ar", "48000", "-shortest"] if audio else ["-an"]) + [str(out)]
        subprocess.run(cmd, check=True)
    return out
