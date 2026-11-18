from conftest import needs_ffmpeg

from clipfactory import media, sfx, voice


@needs_ffmpeg
def test_produce_line_by_line_offline(tmp_path):
    lines = ["¿Sabías que esto es una prueba?", "Segunda frase con más palabras aquí.", "Y cierre."]
    r = voice.produce(lines, tmp_path, provider="tono")
    spans = r["lines"]
    assert [s["style"] for s in spans] == ["gancho", "narracion", "cierre"]
    assert all(a["end"] <= b["start"] for a, b in zip(spans, spans[1:]))
    assert len(r["words"]) == sum(len(l.split()) for l in lines)
    assert abs(media.duration(r["audio"]) - spans[-1]["end"]) < 0.3


@needs_ffmpeg
def test_mix_with_sfx_and_music(tmp_path):
    r = voice.produce(["Hola mundo de prueba.", "Fin."], tmp_path, provider="tono")
    out = sfx.mix(r["audio"], [(0.0, "impacto"), (1.0, "whoosh"), (1.5, "tic")], tmp_path / "mix.wav", music=True)
    assert abs(media.duration(str(out)) - (media.duration(r["audio"]) + 0.6)) < 0.15
    assert media.has_audio(str(out))


def test_provider_chain_fallbacks(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "x")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert voice.provider_chain("auto") == ["elevenlabs", "edge"]
    monkeypatch.delenv("ELEVENLABS_API_KEY")
    assert voice.provider_chain("auto") == ["edge"]
    assert voice.provider_chain("tono") == ["tono"]
