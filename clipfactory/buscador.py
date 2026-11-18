"""TOMMY · Buscador del banco: "busca ciudad" → imágenes de ciudad convertidas en DIBUJO y animadas, listas para el vídeo.

  python3 -m clipfactory.buscador ciudad              → busca en el banco (temas y etiquetas que puso CLIP)
  python3 -m clipfactory.buscador ciudad --pedir 12   → si hay pocas, baja 12 nuevas de Openverse/Commons (licencia libre)
  … --estilo gta|comic|neon|boceto                    → estilo de dibujo (por defecto gta)

Deja el resultado en media/banco/busquedas/<palabra>/: dibujos (.jpg), clips 3D (.mp4) y GALERIA.md.
En GitHub: Actions → "Tommy · Busca imágenes" → Run workflow → escribe la palabra.
"""

from __future__ import annotations

import argparse
import shutil
import unicodedata
from pathlib import Path

from . import banco, dibujo

# palabra en español → (temas/etiquetas del banco que valen, búsqueda en inglés para bajar fotos nuevas)
DICCIONARIO: dict[str, tuple[list[str], str]] = {
    "ciudad": (["ciudad", "calle", "noche", "vice-city"], "city skyline"),
    "calle": (["calle", "ciudad"], "city street"),
    "noche": (["noche", "club", "cartel"], "city at night neon"),
    "playa": (["playa", "atardecer"], "beach palm trees"),
    "atardecer": (["atardecer", "playa"], "sunset palm trees"),
    "perro": (["perro"], "dog"),
    "gato": (["gato"], "cat"),
    "animal": (["animal", "perro", "gato", "ave", "caiman", "pez"], "wild animal"),
    "caiman": (["caiman", "pantano"], "alligator"),
    "cocodrilo": (["caiman", "pantano"], "alligator"),
    "flamenco": (["ave"], "flamingo"),
    "pajaro": (["ave"], "bird"),
    "tiburon": (["pez"], "shark"),
    "pantano": (["pantano", "caiman"], "swamp everglades"),
    "coche": (["coche", "deportivo"], "car"),
    "deportivo": (["deportivo", "coche"], "sports car"),
    "moto": (["moto"], "motorcycle"),
    "camion": (["camion"], "truck"),
    "barco": (["barco", "puerto"], "boat"),
    "yate": (["barco", "puerto"], "yacht"),
    "avion": (["avion"], "airplane"),
    "helicoptero": (["helicoptero"], "helicopter"),
    "policia": (["policia"], "police car"),
    "carcel": (["carcel"], "prison"),
    "atraco": (["criminal", "dinero", "arma"], "bank robbery"),
    "robo": (["criminal", "dinero"], "robbery"),
    "dinero": (["dinero"], "cash money"),
    "oro": (["joyas", "dinero"], "gold bars"),
    "joyas": (["joyas"], "jewelry diamonds"),
    "pistola": (["arma"], "handgun museum"),
    "arma": (["arma"], "gun museum"),
    "casa": (["casa", "interior"], "house"),
    "mansion": (["casa"], "mansion"),
    "piscina": (["casa", "fiesta"], "swimming pool"),
    "fiesta": (["fiesta", "club"], "party"),
    "discoteca": (["club", "fiesta"], "nightclub"),
    "club": (["club", "fiesta"], "nightclub"),
    "gasolinera": (["gasolinera"], "gas station"),
    "tienda": (["tienda"], "convenience store"),
    "comida": (["comida"], "fast food"),
    "movil": (["movil"], "smartphone"),
    "carretera": (["carretera"], "highway"),
    "puente": (["carretera"], "bridge"),
    "tormenta": (["tormenta"], "storm lightning"),
    "huracan": (["tormenta"], "hurricane"),
    "explosion": (["accion"], "explosion"),
    "persecucion": (["accion", "policia", "coche"], "car chase"),
    "lucia": (["lucia", "pareja"], ""),
    "jason": (["jason", "pareja"], ""),
    "miami": (["ciudad", "playa", "florida"], "Miami"),
    "florida": (["florida", "playa", "pantano"], "Florida"),
    "neon": (["cartel", "noche"], "neon sign"),
    "campo": (["campo"], "countryside"),
    # de todo
    "montana": (["montana"], "mountain landscape"),
    "bosque": (["bosque"], "forest"),
    "cascada": (["agua"], "waterfall"),
    "rio": (["agua"], "river"),
    "desierto": (["desierto"], "desert"),
    "volcan": (["volcan"], "volcano"),
    "espacio": (["espacio", "cohete"], "outer space galaxy"),
    "planeta": (["espacio"], "planet"),
    "luna": (["espacio"], "moon surface"),
    "astronauta": (["cohete", "espacio"], "astronaut"),
    "cohete": (["cohete"], "rocket launch"),
    "mar": (["mar", "pez"], "ocean"),
    "ballena": (["mar"], "whale"),
    "pulpo": (["mar"], "octopus"),
    "historia": (["historia", "monumento"], "ancient ruins"),
    "piramide": (["historia"], "egyptian pyramids"),
    "castillo": (["historia"], "medieval castle"),
    "misterio": (["misterio", "noche"], "abandoned foggy"),
    "abandonado": (["misterio"], "abandoned building"),
    "cementerio": (["misterio"], "old cemetery"),
    "ciencia": (["ciencia"], "laboratory science"),
    "dinosaurio": (["ciencia", "historia"], "dinosaur skeleton"),
    "robot": (["tecnologia"], "robot"),
    "ordenador": (["tecnologia"], "computer"),
    "videojuego": (["tecnologia"], "video game arcade"),
    "futbol": (["deporte", "estadio"], "football stadium"),
    "deporte": (["deporte", "estadio"], "sport"),
    "boxeo": (["deporte"], "boxing"),
    "formula1": (["deporte", "deportivo"], "formula 1 car"),
    "pizza": (["comida_rica", "comida"], "pizza"),
    "hamburguesa": (["comida_rica", "comida"], "hamburger"),
    "tren": (["tren"], "train"),
    "tanque": (["militar"], "military tank"),
    "guerra": (["militar"], "military"),
    "arte": (["arte"], "painting museum"),
    "musica": (["musica"], "concert musicians"),
    "persona": (["retrato", "personas"], "portrait"),
    "gente": (["personas", "retrato"], "crowd"),
    "torre": (["monumento", "ciudad"], "famous tower landmark"),
    "nueva york": (["ciudad", "monumento"], "New York skyline"),
    "tokio": (["ciudad", "noche"], "Tokyo street night"),
    "paris": (["monumento", "ciudad"], "Paris Eiffel Tower"),
    "madrid": (["ciudad"], "Madrid"),
    "bitcoin": (["dinero"], "bitcoin"),
}


def norm(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t.lower().strip()) if unicodedata.category(c) != "Mn")


def _entrada(palabra: str) -> tuple[list[str], str]:
    p = norm(palabra)
    if p in DICCIONARIO:
        return DICCIONARIO[p]
    if p.endswith("s") and p[:-1] in DICCIONARIO:  # plurales: coches → coche
        return DICCIONARIO[p[:-1]]
    return [p], palabra


def encontrar(palabra: str, ind: dict | None = None) -> list[tuple[str, dict, float]]:
    """Imágenes del banco para la palabra, de la que mejor encaja a la que menos (puntuación CLIP + etiquetas)."""
    ind = ind if ind is not None else banco.cargar()
    temas, _ = _entrada(palabra)
    res = []
    for iid, v in ind.items():
        clip = v.get("clip") or {}
        p = 0.0
        # el primer tema de la lista es lo que se pidió; los demás, parientes (ciudad → calle, noche…)
        peso = {t: (1.0 if k == 0 else 0.5) for k, t in enumerate(temas)}
        if v.get("tema") in peso:
            p += 3 * peso[v["tema"]]
        p += sum(peso[t] for t in temas if t in v.get("etiquetas", []))
        p += sum(clip.get(t, 0) * 4 * peso[t] for t in temas)
        if norm(palabra) in norm(v.get("consulta", "") + " " + v.get("alt", "")):
            p += 1.5
        if p > 0:
            res.append((iid, v, p))
    return sorted(res, key=lambda x: -x[2])


def pedir(palabra: str, n: int) -> int:
    """Baja n fotos NUEVAS con licencia libre para la palabra y las mete en el banco (categoría 'pedidas')."""
    import hashlib

    from . import libres

    _, consulta = _entrada(palabra)
    if not consulta:
        print(f"[buscador] '{palabra}': solo imágenes oficiales (no se buscan fotos libres)")
        return 0
    ind = banco.cargar()
    carpeta = banco.BANCO / "libres" / "pedidas"
    res = []
    for nombre, fn in (("Openverse", libres.openverse), ("Commons", libres.buscar_varias)):
        try:
            res += fn(consulta, n, carpeta)
        except Exception as e:
            print(f"[buscador] {nombre}: {e}")
    nuevas = 0
    temas, _ = _entrada(palabra)
    for path, credit, w, h in res:
        iid = "lb-" + hashlib.sha1(path.name.encode()).hexdigest()[:10]
        if iid in ind:
            continue
        ind[iid] = {"archivo": str(path.relative_to(banco.BANCO)), "fuente": "libre", "credito": credit, "categoria": "pedidas",
                    "consulta": consulta, "tema": temas[0], "etiquetas": sorted(set(temas)), "w": w, "h": h}  # fmt: skip
        nuevas += 1
    banco.guardar(ind, ("libres-pedidas",))
    print(f"[buscador] '{palabra}' → {nuevas} fotos nuevas ('{consulta}')")
    return nuevas


def preparar(palabra: str, cuantas: int = 12, estilo: str = "gta", animar: bool = True) -> Path:
    """Dibujos + clips 3D de las mejores imágenes para la palabra en media/banco/busquedas/<palabra>/."""
    ind = banco.cargar()
    hits = encontrar(palabra, ind)[:cuantas]
    out = banco.BANCO / "busquedas" / norm(palabra).replace(" ", "-")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    filas = []
    for iid, v, p in hits:
        dib = banco.dibujo_de(iid, v, estilo)
        shutil.copy2(dib, out / f"{iid}.jpg")
        clip = ""
        if animar:
            from . import escena3d

            mp4 = out / f"{iid}.mp4"
            try:
                escena3d.clip(
                    {"tipo": "foto", "imagen": str(dib), "estilo": ("lleno", "inclinada", "giro")[len(filas) % 3]}, 3.0, mp4, crf=26
                )
                clip = f" · [▶ clip 3D]({iid}.mp4)"
            except Exception as e:
                print(f"[buscador] sin clip para {iid}: {e}")
        fuente = "🎬 oficial" if v["fuente"] == "oficial" else "📷 libre"
        filas.append(
            f"| [![{iid}]({iid}.jpg)]({iid}.jpg) | `{iid}` {fuente}{clip}<br>encaje {p:.1f} · {', '.join(v.get('etiquetas', [])[:4])}<br><sub>{v.get('credito', '')[:120]}</sub> |"
        )
    (out / "GALERIA.md").write_text(
        "\n".join(
            [
                f"# Búsqueda: «{palabra}» · estilo {estilo}",
                "",
                f"{len(hits)} resultados (dibujo + clip 3D de 3 s, 1080x1920). En un guion: "
                f"`{{kind: 3d, tipo: foto, imagen: media/banco/busquedas/{out.name}/<id>.jpg}}`",
                "",
                "| Dibujo | Datos |",
                "|---|---|",
                *filas,
            ]
        )
        + "\n",  # fmt: skip
        encoding="utf-8",
    )
    print(f"[buscador] '{palabra}': {len(hits)} resultados → {out}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="clipfactory.buscador", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("palabras", nargs="+", help="una o varias palabras (cada una es una búsqueda): ciudad perro coche")
    ap.add_argument("--cuantas", type=int, default=12)
    ap.add_argument("--estilo", default="gta", choices=dibujo.ESTILOS)
    ap.add_argument("--pedir", type=int, default=0, help="bajar N fotos nuevas por palabra si hay menos de --cuantas en el banco")
    ap.add_argument("--sin-clips", action="store_true")
    a = ap.parse_args(argv)
    for palabra in a.palabras:
        if a.pedir and len(encontrar(palabra)) < a.cuantas:
            pedir(palabra, a.pedir)
        preparar(palabra, a.cuantas, a.estilo, animar=not a.sin_clips)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
