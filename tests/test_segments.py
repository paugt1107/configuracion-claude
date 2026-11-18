from clipfactory import segments


def _words(text, start=0.0, step=0.4):
    out, t = [], start
    for w in text.split():
        out.append({"text": w, "start": t, "end": t + step * 0.9})
        t += step
    return out


def test_candidates_within_bounds_and_non_overlapping():
    text = (
        "¿Por qué nadie habla de este detalle? "
        + "Mira la esquina del mapa y fíjate bien en lo que pasa. " * 6
        + "Y entonces seguimos con otra cosa sin importancia. " * 8
    )
    words = _words(text)
    cands = segments.candidates(words, min_s=10, max_s=30, top=3)
    assert cands
    for c in cands:
        assert 10 <= c["duracion"] <= 30
    for i, a in enumerate(cands):
        for b in cands[i + 1 :]:
            assert a["fin"] <= b["inicio"] or a["inicio"] >= b["fin"]
    assert "pregunta" in " ".join(cands[0]["motivos"]) or "gancho" in " ".join(cands[0]["motivos"])


def test_weak_start_penalized():
    good = segments.score_window(segments.sentences(_words("Nadie vio este secreto en el tráiler.")))[0]
    weak = segments.score_window(segments.sentences(_words("Y luego pasó esto en el tráiler.")))[0]
    assert good > weak
