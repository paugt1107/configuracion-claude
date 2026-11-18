import yaml

from clipfactory import media, short_job, thumbs
from conftest import needs_ffmpeg


def test_title_checks():
    assert short_job.title_checks("GTA 6: hora de desbloqueo", "12 HORAS ANTES") == ["ok"]
    notes = short_job.title_checks("Un título larguísimo que no dice el juego y se pasa de los sesenta caracteres", "TÍTULO")
    assert any("falta 'GTA 6'" in n for n in notes) and any(">60" in n for n in notes)


def test_covers(tmp_path):
    outs = thumbs.make_covers({"texto": "NADIE LO VIO", "kind": "clock", "reloj": "00:00", "bandera": "es"}, tmp_path)
    assert len(outs) == 3 and all(p.exists() for p in outs)


@needs_ffmpeg
def test_produce_from_yaml_offline(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    spec = {"id": "T1", "titulos": ["GTA 6: prueba"], "portada": {"texto": "PRUEBA", "kind": "dato", "grande": "1"},
            "escenas": [{"texto": "¿Sabías que esto es una prueba?", "tarjeta": {"kind": "dato", "grande": "1"}},
                        {"texto": "Y esto el cierre.", "tarjeta": {"kind": "lista", "items": ["a", "b"]}}]}
    (tmp_path / "g.yaml").write_text(yaml.safe_dump(spec, allow_unicode=True), encoding="utf-8")
    video = short_job.produce(tmp_path / "g.yaml", provider="tono", out_root=tmp_path / "entregas")
    assert media.video_size(str(video)) == (1080, 1920) and media.has_audio(str(video))
    d = tmp_path / "entregas" / "T1"
    assert (d / "portada-1.png").exists() and "Títulos" in (d / "publicacion.md").read_text()
