from clipfactory import captions

WORDS = [{"text": t, "start": i * 0.4, "end": i * 0.4 + 0.35} for i, t in enumerate("GTA VI sale mañana. Pero ojo con la hora".split())]


def test_chunks_respect_max_and_sentence_end():
    chunks = captions.chunk_words(WORDS, max_words=3)
    assert all(len(c) <= 3 for c in chunks)
    assert chunks[0][-1]["text"] in {"sale", "mañana."}
    assert any(c[-1]["text"] == "mañana." for c in chunks)


def test_ass_has_one_event_per_word_and_highlight():
    ass = captions.build_ass(WORDS)
    events = [l for l in ass.splitlines() if l.startswith("Dialogue:")]
    assert len(events) == len(WORDS)
    assert "PlayResY: 1920" in ass
    assert "\\c&H001A7AFF" in ass  # naranja #FF7A1A en BGR


def test_margin_inside_safe_zone():
    ass = captions.build_ass(WORDS)
    style = [l for l in ass.splitlines() if l.startswith("Style: Cap")][0]
    margin_v = int(style.split(",")[-2])
    assert margin_v >= int(1920 * 0.25)


def test_braces_are_escaped():
    ass = captions.build_ass([{"text": "{hack}", "start": 0, "end": 1}])
    assert "{hack}" not in ass and "HACK" in ass.upper()
