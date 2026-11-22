"""TOMMY · Convierte cualquier foto en DIBUJO (estilo ilustración de GTA: colores planos, tinta negra, tramado).

Estilos:
  gta     → ilustración tipo pantalla de carga: colores planos (cel), contorno de tinta, contraste alto,
            sombras con trama de puntos y gradación Vice City (luces cálidas, sombras magenta/turquesa).
  neon    → noche: fondo oscuro, contornos que brillan en rosa/turquesa (para misterio y escenas nocturnas).
  boceto  → lápiz sobre papel (para "cómo se hizo", datos o teorías).
  comic   → viñeta de cómic: colores muy saturados, tinta gruesa y trama grande.
  cartoon → dibujos animados: zonas de color limpias y luminosas (sin trama), contorno negro grueso y suave,
            sombras en un solo tono y brillo cálido (para insertos a pantalla completa y cuadros del mundo 3D).

Todo con PIL + numpy (sin modelos ni internet): rápido y siempre igual (el mismo archivo da el mismo dibujo).
Uso:  python3 -m clipfactory.dibujo <entrada.jpg> <salida.jpg> [gta|neon|boceto|comic]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ESTILOS = ("gta", "neon", "boceto", "comic", "cartoon")


# ---------------------------------------------------------------- piezas
def _gris(im: Image.Image) -> np.ndarray:
    return np.asarray(im.convert("L"), dtype=np.float32) / 255.0


def _blur(a: np.ndarray, r: float) -> np.ndarray:
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255.0


def tinta(im: Image.Image, grosor: float = 1.0, tau: float = 0.982, eps: float = -0.004, phi: float = 140.0) -> np.ndarray:
    """Líneas de tinta con XDoG (diferencia de gaussianas extendida): 0 = tinta, 1 = papel.
    D = G(s) − τ·G(1,6·s); papel donde D ≥ ε, y una caída suave (tanh) hacia la tinta donde D < ε.
    Saca siluetas, ventanas y caras sin el ruido fino."""
    g = _gris(im)
    s = 0.9 * grosor
    d = _blur(g, s) - tau * _blur(g, s * 1.6)
    lineas = np.where(d >= eps, 1.0, 1.0 + np.tanh(phi * (d - eps)))
    lineas = np.clip(lineas, 0, 1)
    img = Image.fromarray((lineas * 255).astype(np.uint8))
    if grosor >= 1:  # engorda el trazo para que se lea en el móvil
        img = img.filter(ImageFilter.MinFilter(3))
    return np.asarray(img, dtype=np.float32) / 255.0


def planos(im: Image.Image, colores: int = 14, pasadas: int = 2) -> Image.Image:
    """Colores planos tipo cel: suaviza conservando bordes (mediana) y reduce la paleta."""
    x = im.convert("RGB")
    for _ in range(pasadas):
        x = x.filter(ImageFilter.MedianFilter(5))
    x = x.filter(ImageFilter.SMOOTH_MORE)
    return x.quantize(colors=colores, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")


def trama(im: Image.Image, paso: int = 7, fuerza: float = 0.35, solo_sombras: float = 0.42) -> Image.Image:
    """Trama de puntos (halftone) en las sombras, como en los carteles impresos."""
    a = np.asarray(im, dtype=np.float32) / 255.0
    lum = a.mean(axis=2)
    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w]
    # rejilla girada 45° para que no parezca un patrón de pantalla
    u = ((xx + yy) % paso) - paso / 2
    v = ((xx - yy) % paso) - paso / 2
    radio = np.clip((solo_sombras - lum) / solo_sombras, 0, 1) * (paso / 2)
    punto = (u * u + v * v) < (radio * radio)
    a[punto] *= 1 - fuerza
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def gradacion(im: Image.Image, luces=(1.06, 0.98, 0.88), sombras=(0.95, 0.85, 1.12)) -> Image.Image:
    """Tinta de color: luces cálidas y sombras magenta/turquesa (atardecer de Vice City)."""
    a = np.asarray(im, dtype=np.float32) / 255.0
    lum = a.mean(axis=2, keepdims=True)
    mezcla = lum * np.array(luces) + (1 - lum) * np.array(sombras)
    return Image.fromarray((np.clip(a * mezcla, 0, 1) * 255).astype(np.uint8))


def vineta(im: Image.Image, fuerza: float = 0.28) -> Image.Image:
    a = np.asarray(im, dtype=np.float32) / 255.0
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a *= (1 - fuerza * np.clip(d - 0.55, 0, 1))[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def _poner_tinta(base: Image.Image, lineas: np.ndarray, color=(18, 12, 24)) -> Image.Image:
    a = np.asarray(base, dtype=np.float32)
    m = lineas[..., None]
    out = a * m + np.array(color, dtype=np.float32) * (1 - m)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def _caja(integral, y0, x0, y1, x1):
    return integral[y1, x1] - integral[y0, x1] - integral[y1, x0] + integral[y0, x0]


def kuwahara(im: Image.Image, r: int = 5) -> Image.Image:
    """Filtro de Kuwahara: suaviza en manchas de color planas conservando los bordes (aspecto de pintura/animación).
    Para cada píxel elige, de sus 4 cuadrantes (r x r), el de menor varianza de luminancia y toma su color medio."""
    a = np.asarray(im.convert("RGB"), dtype=np.float64) / 255.0
    h, w, _ = a.shape
    lum = a.mean(axis=2)
    pad = lambda x: np.pad(x, ((r, r + 1), (r, r + 1)) + ((0, 0),) * (x.ndim - 2), mode="edge")

    def integral(x):
        s = np.cumsum(np.cumsum(pad(x), 0), 1)
        return np.pad(s, ((1, 0), (1, 0)) + ((0, 0),) * (x.ndim - 2))

    S, S2, SC = integral(lum), integral(lum * lum), integral(a)
    yy, xx = np.mgrid[0:h, 0:w]
    best_v = np.full((h, w), np.inf)
    out = np.zeros_like(a)
    n = (r + 1) ** 2
    for dy, dx in ((0, 0), (0, r), (r, 0), (r, r)):  # cuadrantes: arriba-izq, arriba-dcha, abajo-izq, abajo-dcha
        y0, x0 = yy + dy, xx + dx
        y1, x1 = y0 + r + 1, x0 + r + 1
        m = _caja(S, y0, x0, y1, x1) / n
        v = _caja(S2, y0, x0, y1, x1) / n - m * m
        c = _caja(SC, y0, x0, y1, x1) / n
        mejor = v < best_v
        best_v = np.where(mejor, v, best_v)
        out[mejor] = c[mejor]
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def cartoon(im: Image.Image) -> Image.Image:
    """Dibujo animado: manchas de color limpias (Kuwahara + paleta corta), colores vivos y contorno oscuro suave."""
    x = kuwahara(im, 4)
    x = kuwahara(x, 3)
    x = ImageEnhance.Color(ImageEnhance.Contrast(x).enhance(1.10)).enhance(1.6)
    q = x.quantize(colors=18, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    q = q.filter(ImageFilter.ModeFilter(5))
    a = np.asarray(q, dtype=np.float32) / 255.0
    lum = a.mean(axis=2, keepdims=True)
    a = np.clip(a * (0.88 + 0.32 * lum) + 0.035, 0, 1)  # luces luminosas y sombras más hondas (aspecto animado)
    base = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.SMOOTH)
    lineas = tinta(x, grosor=1.7, tau=0.99, eps=-0.012, phi=45.0)  # solo bordes fuertes (sobre la imagen ya suavizada)
    lin = Image.fromarray((lineas * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    return _poner_tinta(base, np.asarray(lin, dtype=np.float32) / 255.0, color=(24, 16, 32))


# ---------------------------------------------------------------- estilos
def dibujar(im: Image.Image, estilo: str = "gta", lado: int = 1400) -> Image.Image:
    if estilo not in ESTILOS:
        raise ValueError(f"Estilo desconocido: {estilo} (usa {', '.join(ESTILOS)})")
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((lado, lado), Image.LANCZOS)
    if estilo == "gta":
        base = planos(ImageEnhance.Contrast(im).enhance(1.15), colores=16)
        base = ImageEnhance.Color(base).enhance(1.45)
        base = gradacion(trama(base, paso=6, fuerza=0.30))
        out = _poner_tinta(base, tinta(im, grosor=1.0))
        return vineta(out)
    if estilo == "comic":
        base = planos(ImageEnhance.Contrast(im).enhance(1.3), colores=10, pasadas=3)
        base = trama(ImageEnhance.Color(base).enhance(1.8), paso=9, fuerza=0.45, solo_sombras=0.5)
        return _poner_tinta(base, tinta(im, grosor=1.6), color=(5, 5, 10))
    if estilo == "cartoon":
        return cartoon(im)
    if estilo == "neon":
        oscuro = ImageEnhance.Brightness(planos(im, colores=12)).enhance(0.35)
        lineas = 1 - tinta(im, grosor=1.0)  # 1 = línea
        brillo = Image.fromarray((lineas * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
        a = np.asarray(oscuro, dtype=np.float32)
        h = np.asarray(brillo, dtype=np.float32)[..., None] / 255.0
        ln = lineas[..., None]
        rosa, cian = np.array([255, 70, 170]), np.array([60, 230, 220])
        mezcla = np.linspace(0, 1, a.shape[1])[None, :, None]  # de rosa (izq) a turquesa (dcha)
        neon = rosa * (1 - mezcla) + cian * mezcla
        out = a + neon * h * 0.9 + 255 * ln * 0.55
        return vineta(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), 0.4)
    # boceto: lápiz sobre papel
    g = _gris(im)
    lapiz = np.clip(g / np.maximum(_blur(1 - g, 8) * -1 + 1, 0.05), 0, 1)  # color dodge del negativo desenfocado
    lapiz = lapiz**2.2 * tinta(im, grosor=0.6) ** 0.6
    papel = np.array([243, 236, 222], dtype=np.float32)
    out = papel * lapiz[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def archivo(src: str | Path, dst: str | Path, estilo: str = "gta") -> Path:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dibujar(Image.open(src), estilo).save(dst, "JPEG", quality=88)
    return dst


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        raise SystemExit(__doc__)
    print(archivo(a[0], a[1], a[2] if len(a) > 2 else "gta"))
