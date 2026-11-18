from clipfactory import motion


def test_estimate_words_fits_duration_and_is_monotonic():
    w = motion.estimate_words("GTA seis sale mañana pero no a la misma hora", 10.0)
    assert len(w) == 9
    assert all(a["end"] <= b["start"] + 1e-6 or a["start"] < b["start"] for a, b in zip(w, w[1:]))
    assert w[-1]["end"] <= 10.0


def test_card_is_vertical_and_long_titles_fit():
    img = motion.card({"kind": "clock", "reloj": "00:00", "titulo": "UN TÍTULO MUCHO MÁS LARGO QUE CABE EN DOS LÍNEAS DE PANTALLA"})
    assert img.size == (1080, 1920)
