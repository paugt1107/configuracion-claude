from clipfactory import demanda


def test_intencion_y_puntos(tmp_path, monkeypatch):
    monkeypatch.setattr(demanda, "SALIDA", tmp_path / "demanda.md")
    monkeypatch.setattr(demanda, "HIST", tmp_path / "demanda.json")
    assert demanda.intencion("gta 6 donde esta el coche secreto") == "ubicación"
    assert demanda.intencion("gta 6 como ganar dinero") == "guía"
    frases = {
        "gta 6 como ganar dinero": {"fuentes": ["g-ES", "yt-ES", "yt-MX"], "mejor_pos": 0, "idioma": "es"},
        "gta 6 lucia actriz": {"fuentes": ["g-ES"], "mejor_pos": 5, "idioma": "es"},
    }
    lista = demanda.puntuar(frases, {"ultima": ["gta 6 lucia actriz"]})
    assert lista[0]["frase"] == "gta 6 como ganar dinero" and lista[0]["nueva"] and not lista[1]["nueva"]
    md = demanda.escribir(lista, {}).read_text()
    assert "🆕 **gta 6 como ganar dinero**" in md and "## personaje" in md
