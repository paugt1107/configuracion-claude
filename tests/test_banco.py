from PIL import Image

from clipfactory import banco, rutas


def test_galeria_y_personajes(tmp_path, monkeypatch):
    monkeypatch.setattr(banco, "BANCO", tmp_path / "banco")
    monkeypatch.setattr(rutas, "OFICIAL", tmp_path / "oficial")
    ind = {}
    for iid, et in [("of-1", ["lucia"]), ("of-2", ["jason"]), ("of-3", ["lucia", "jason"]), ("lb-1", ["florida"])]:
        p = banco.BANCO / "oficial" / f"{iid}.jpg"
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (1200, 700), (200, 100, 50)).save(p)
        ind[iid] = {"archivo": f"oficial/{iid}.jpg", "fuente": "oficial" if iid.startswith("of") else "libre",
                    "categoria": "oficial" if iid.startswith("of") else "florida", "etiquetas": et, "w": 1200, "h": 700}
    assert sorted(banco.personajes(ind)) == ["jason.jpg", "lucia-jason.jpg", "lucia.jpg"]
    g = banco.galeria(ind).read_text()
    assert "[florida](temas/florida/GALERIA.md)" in g and (banco.BANCO / "temas" / "florida" / "lb-1.jpg").exists()


def test_etiquetas_por_texto():
    assert banco._etiquetas_texto("GTA_VI_Jason_Duval_03", "", "https://www.rockstargames.com/VI/places") == ["jason"]
    assert "vice-city" in banco._etiquetas_texto("vice_city_beach")


def test_libres_reparto_y_dibujo_cartoon(tmp_path, monkeypatch):
    from clipfactory import dibujo, libres

    monkeypatch.setattr(banco, "BANCO", tmp_path / "banco")
    vistas = []

    def falso(q, n, carpeta):
        vistas.append(q)
        p = carpeta / f"{libres.slug(q)}.jpg"
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (2400, 1600), (120, 160, 90)).save(p)
        return [(p, f"{q} — autor — CC0 — url", 2400, 1600)]

    monkeypatch.setattr(libres, "openverse", falso)
    monkeypatch.setattr(libres, "buscar_varias", lambda q, n, c: [])
    cfg = {"libres": {"n": 6, "huevos": ["egg"], "gallinas": ["hen"], "otros": ["x"]}}
    ind = {}
    banco.descargar_libres(cfg, ind, 99, ["huevos", "gallinas"], parte=1, partes=2, n=2, lado=1280)
    assert vistas == ["egg"]  # gallinas (0) es de la parte 0; huevos (1) de la parte 1; "otros" no se pidió
    (v,) = ind.values()
    assert max(v["w"], v["h"]) == 1280 and v["categoria"] == "huevos"
    assert banco.dibujar(ind, "cartoon", ["huevos"]) == 1
    assert v["dibujo"].startswith("dibujos/cartoon/")
    g = banco.galeria(ind).read_text()
    assert "[huevos](temas/huevos/GALERIA.md)" in g
    assert dibujo.dibujar(Image.new("RGB", (300, 200), (200, 50, 50)), "cartoon").size == (300, 200)
