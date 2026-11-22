import pytest

from clipfactory import escena3d, motion


def test_plana_equivalente_se_puede_dibujar():
    for spec in [
        {"kind": "3d", "tipo": "numero", "texto": "99", "titulo": "NOTA"},
        {"kind": "3d", "tipo": "estrellas", "n": 4, "titulo": "BUSCA"},
        {"kind": "3d", "tipo": "versus", "texto": "GTA V|GTA VI"},
        {"kind": "3d", "tipo": "moneda"},
    ]:
        assert motion.card(escena3d.plana(spec)).size == (1080, 1920)


@pytest.mark.skipif(not escena3d.disponible(), reason="sin node+playwright")
def test_render_3d_corto(tmp_path):
    out = escena3d.clip({"tipo": "moneda", "titulo": "DINERO", "color": "gold"}, 0.3, tmp_path / "e.mp4", fps=10)
    assert out.exists() and out.stat().st_size > 1000


def test_foto_vertical_recorta_9_16_y_mueve_el_punto(tmp_path):
    from PIL import Image

    p = tmp_path / "f.jpg"
    Image.new("RGB", (1600, 900), (90, 140, 60)).save(p)
    im, (u, v) = escena3d.foto_vertical(p, {"x": 0.9, "y": 0.5}, (0.9, 0.3), estilo="", alto=640)
    assert im.size == (360, 640)
    assert 0 <= u <= 1 and abs(v - 0.3) < 1e-6 and u > 0.5  # foco pegado al borde derecho: el recorte se apoya en él


def test_unir_mundo_un_solo_clip_con_hitos():
    from clipfactory import short_job

    scenes = [{"kind": "3d", "tipo": "mundo", "zona": z, "dur": d} for z, d in [("intro", 3.0), ("dinos", 2.5), ("dinos_noche", 1.5)]]
    scenes.append({"kind": "dato", "grande": "?", "dur": 2.0})
    out = short_job.unir_mundo(scenes, {}, set(), [])
    assert len(out) == 2 and out[0]["hitos"] == [0.0, 3.0, 5.5] and out[0]["dur"] == 7.0
    assert [p["zona"] for p in out[0]["paradas"]] == ["intro", "dinos", "dinos_noche"]
    assert short_job._vuelos(out[0], 0.0) == [3.0 - 0.45]  # dinos → dinos_noche es el mismo sitio: sin whoosh


@pytest.mark.skipif(not escena3d.disponible(), reason="sin node+playwright")
def test_render_mundo_corto(tmp_path):
    spec = {"tipo": "mundo", "paradas": [{"zona": "intro"}, {"zona": "primeros", "etiquetas": [{"titulo": "A", "texto": "B"}]}], "hitos": [0, 0.4]}
    out = escena3d.clip(spec, 0.8, tmp_path / "m.mp4", fps=5, trozos=2)
    assert out.exists() and out.stat().st_size > 1000
