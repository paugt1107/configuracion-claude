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
