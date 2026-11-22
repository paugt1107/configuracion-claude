"""Números en palabras → cifras, SOLO para los subtítulos (la voz los necesita en palabras para pronunciarlos bien).

"GTA seis" → "GTA 6", "doscientos doce gigas" → "212 gigas", "cuarenta y siete minutos" → "47 minutos",
"cincuenta y ocho por ciento" → "58 %", "dos mil veintiséis" → "2026". Trabaja sobre la lista de palabras con tiempos:
une las palabras del número en una sola (desde el inicio de la primera hasta el final de la última).
"""

from __future__ import annotations

import re
import unicodedata

UNIDADES = {
    "cero": 0, "uno": 1, "un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8,
    "nueve": 9, "diez": 10, "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15, "dieciseis": 16,
    "diecisiete": 17, "dieciocho": 18, "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintiun": 21, "veintiuna": 21,
    "veintidos": 22, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25, "veintiseis": 26, "veintisiete": 27,
    "veintiocho": 28, "veintinueve": 29,
}  # fmt: skip
DECENAS = {"treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90}
CENTENAS = {
    "cien": 100, "ciento": 100, "doscientos": 200, "doscientas": 200, "trescientos": 300, "trescientas": 300,
    "cuatrocientos": 400, "cuatrocientas": 400, "quinientos": 500, "quinientas": 500, "seiscientos": 600, "seiscientas": 600,
    "setecientos": 700, "setecientas": 700, "ochocientos": 800, "ochocientas": 800, "novecientos": 900, "novecientas": 900,
}  # fmt: skip
SUELTOS_NO = {"un", "una", "uno"}  # "un coche" no es "1 coche"


def _n(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def _limpio(t: str) -> tuple[str, str, str]:
    """(signos delante, palabra, signos detrás)."""
    m = re.match(r"^(\W*)(.*?)(\W*)$", t, re.S)
    return m.group(1), m.group(2), m.group(3)


def leer(tokens: list[str]) -> tuple[int, int] | None:
    """Lee un número desde el principio de tokens (ya normalizados). Devuelve (valor, cuántos tokens usa) o None."""
    total, actual, i, usado = 0, 0, 0, 0
    while i < len(tokens):
        w = tokens[i]
        if w in UNIDADES and (actual % 10 == 0 or actual >= 100 and actual % 100 == 0):
            if actual % 100 >= 10 and w in UNIDADES and UNIDADES[w] >= 10:
                break
            actual += UNIDADES[w]
        elif w in DECENAS and actual % 100 == 0:
            actual += DECENAS[w]
            if i + 2 < len(tokens) and tokens[i + 1] == "y" and tokens[i + 2] in UNIDADES and UNIDADES[tokens[i + 2]] < 10:
                actual += UNIDADES[tokens[i + 2]]
                i += 2
        elif w in CENTENAS and actual == 0:
            actual += CENTENAS[w]
        elif w == "mil":
            total += (actual or 1) * 1000
            actual = 0
        elif w in ("millon", "millones"):
            total += (actual or 1) * 1_000_000
            actual = 0
        else:
            break
        i += 1
        usado = i
    if not usado:
        return None
    return total + actual, usado


def a_cifras(words: list[dict]) -> list[dict]:
    """Une y convierte números escritos con palabras en la lista de palabras de los subtítulos."""
    out, i = [], 0
    norm = [_n(_limpio(w["text"])[1]) for w in words]
    while i < len(words):
        r = leer(norm[i:])
        if r and not (r[1] == 1 and norm[i] in SUELTOS_NO):
            valor, k = r
            delante = _limpio(words[i]["text"])[0]
            detras = _limpio(words[i + k - 1]["text"])[2]
            if valor >= 1_000_000 and valor % 1_000_000 == 0:  # "300 millones" se lee mejor que "300.000.000"
                m = valor // 1_000_000
                txt = f"{m:,}".replace(",", ".") + (" millón" if m == 1 else " millones")
            else:
                txt = f"{valor:,}".replace(",", ".") if valor >= 10000 else str(valor)
            fin = i + k
            if fin + 1 < len(words) and norm[fin] == "por" and norm[fin + 1] == "ciento":  # 58 por ciento → 58 %
                txt += " %"
                detras = _limpio(words[fin + 1]["text"])[2]
                fin += 2
            out.append({"text": f"{delante}{txt}{detras}", "start": words[i]["start"], "end": words[fin - 1]["end"]})
            i = fin
        else:
            out.append(words[i])
            i += 1
    return out
