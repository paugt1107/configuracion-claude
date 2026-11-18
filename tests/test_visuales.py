from clipfactory import visuales


def _w(text, step=0.5):
    return [{"text": w, "start": i * step, "end": i * step + 0.4} for i, w in enumerate(text.split())]


def test_detecta_en_la_palabra_exacta():
    hits = visuales.detectar(_w("Hola, en España hay mucho dinero y en Nueva Zelanda juegan antes"))
    by = {h["palabra"]: h["t"] for h in hits}
    assert by["España"] == 1.0 and by["dinero"] == 2.5 and by["Nueva Zelanda"] == 4.0


def test_planificar_no_satura():
    hits = [{"t": t, "visual": {"prop": "dinero"}, "palabra": "x"} for t in (1, 1.5, 2, 9)] + [
        {"t": 3.5, "visual": {"bandera": "es"}, "palabra": "y"}
    ]
    plan = visuales.planificar(hits)
    assert [p["t"] for p in plan] == [1, 3.5, 9]


def test_preparar_offline(tmp_path):
    plan = [
        {"t": 1, "dur": 1.3, "palabra": "a", "visual": {"prop": "trofeo"}},
        {"t": 3, "dur": 1.3, "palabra": "b", "visual": {"bandera": "us"}},
        {"t": 5, "dur": 1.3, "palabra": "c", "visual": {"recorte": "no-existe.png", "alt": {"prop": "estrellas", "n": 2}}},
    ]
    ovs, cred = visuales.preparar(plan, tmp_path)
    assert len(ovs) == 3 and cred == []
