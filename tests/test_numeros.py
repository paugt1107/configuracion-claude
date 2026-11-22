from clipfactory import numeros


def _w(txt):
    return [{"text": t, "start": i, "end": i + 0.5} for i, t in enumerate(txt.split())]


def _txt(txt):
    return " ".join(w["text"] for w in numeros.a_cifras(_w(txt)))


def test_cifras_en_subtitulos():
    assert _txt("¿Sabías que GTA seis ocupa doscientos doce gigas?") == "¿Sabías que GTA 6 ocupa 212 gigas?"
    assert _txt("unos cuarenta y siete minutos.") == "unos 47 minutos."
    assert _txt("más de cincuenta y ocho por ciento") == "más de 58 %"
    assert _txt("en dos mil veintiséis") == "en 2026"
    assert _txt("tiene un coche y una moto") == "tiene un coche y una moto"
    assert _txt("trescientos sesenta y cuatro gigas") == "364 gigas"
    assert _txt("ciento catorce reseñas") == "114 reseñas"
    assert _txt("un millón de copias") == "1 millón de copias"


def test_tiempos_unidos():
    w = numeros.a_cifras(_w("son cuarenta y cinco DVD"))
    assert w[1]["text"] == "45" and w[1]["start"] == 1 and w[1]["end"] == 3.5


def test_palabras_clave_para_subtitulos():
    from clipfactory import captions

    w = [{"text": t, "start": i * 0.4, "end": i * 0.4 + 0.3} for i, t in enumerate(["¿Sabías", "que", "Sheffield", "halló", "300", "millones?", "Nunca", "fue", "casual."])]
    claves = [x["text"] for k, x in enumerate(w) if captions.es_clave(w, k)]
    assert "Sheffield" in claves and "300" in claves and "Nunca" in claves
    assert "Sabías" not in claves and "fue" not in claves


def test_millones_redondos_se_leen_con_palabra():
    ws = [{"text": t, "start": i, "end": i + 0.5} for i, t in enumerate(["hace", "trescientos", "millones", "de", "años"])]
    assert [w["text"] for w in numeros.a_cifras(ws)] == ["hace", "300 millones", "de", "años"]


def test_miles_con_punto_pero_anios_sin_punto():
    assert _txt("unos tres mil quinientos años") == "unos 3.500 años"
    assert _txt("en dos mil diez") == "en 2010"
