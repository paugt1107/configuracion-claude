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
