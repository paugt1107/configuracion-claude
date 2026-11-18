from clipfactory import misterio

LINEAS = [
    "¿Sabías que Lucía esconde un secreto?",
    "Viene del latín.",
    "Pero aquí viene lo raro…",
    "Significa luz.",
    "Y casi nadie lo sabe.",
    "Ojo, que hay más.",
    "Rockstar no lo ha confirmado.",
    "¿Tú qué crees?",
]


def test_estilos_pausas_sin_seguidas_y_maximo_tres():
    st = misterio.estilos(LINEAS)
    assert st[0] == "gancho" and st[-1] == "cierre"
    sus = [i for i, s in enumerate(st) if s == "suspense"]
    assert 2 in sus and len(sus) <= 3
    assert all(b - a > 1 for a, b in zip(sus, sus[1:]))


def test_pausa_forzada_y_vetada():
    esc = [{} for _ in LINEAS]
    esc[2] = {"pausa": False}
    esc[4] = {"pausa": True}
    st = misterio.estilos(LINEAS, esc)
    assert st[2] != "suspense" and st[4] == "suspense"


def test_plan_y_filtro():
    st = misterio.estilos(LINEAS)
    spans, words, t = [], [], 0.2
    for linea in LINEAS:
        ws = linea.split()
        spans.append({"text": linea, "start": t, "end": t + 0.3 * len(ws)})
        words += [{"text": w, "start": t + 0.3 * k, "end": t + 0.3 * k + 0.25} for k, w in enumerate(ws)]
        t += 0.3 * len(ws) + 0.6
    p = misterio.plan(spans, words, st, t)
    assert p["silencios"] and p["empujes"] and any(k == "riser" for _, k in p["cues"])
    f = misterio.filtro(p)
    assert f.startswith("scale=") and "crop=1080:1920" in f and "eq=brightness" in f
