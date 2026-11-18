from PIL import Image

from clipfactory import banco, buscador, dibujo


def _banco(tmp_path, monkeypatch):
    monkeypatch.setattr(banco, "BANCO", tmp_path / "banco")
    ind = {}
    for iid, tema, clip in [("of-1", "ciudad", {"ciudad": 0.6}), ("of-2", "perro", {"perro": 0.8}), ("lb-1", "noche", {"noche": 0.4, "ciudad": 0.2})]:
        p = banco.BANCO / "oficial" / f"{iid}.jpg"
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (900, 600), (40 + len(iid) * 20, 120, 200)).save(p)
        ind[iid] = {"archivo": f"oficial/{iid}.jpg", "fuente": "oficial", "categoria": "oficial", "tema": tema, "etiquetas": [tema], "clip": clip}
    banco.guardar(ind)
    return ind


def test_busca_ciudad_ordena_por_encaje(tmp_path, monkeypatch):
    _banco(tmp_path, monkeypatch)
    hits = [i for i, _, _ in buscador.encontrar("Ciudad")]
    assert hits[0] == "of-1" and "lb-1" in hits and "of-2" not in hits
    assert [i for i, _, _ in buscador.encontrar("perros")] == ["of-2"]  # plural


def test_preparar_deja_dibujos_y_galeria(tmp_path, monkeypatch):
    _banco(tmp_path, monkeypatch)
    out = buscador.preparar("ciudad", cuantas=5, animar=False)
    assert (out / "of-1.jpg").exists() and "Búsqueda: «ciudad»" in (out / "GALERIA.md").read_text()


def test_estilos_de_dibujo():
    im = Image.new("RGB", (320, 200), (200, 80, 40))
    for e in dibujo.ESTILOS:
        assert dibujo.dibujar(im, e, lado=320).size == (320, 200)
