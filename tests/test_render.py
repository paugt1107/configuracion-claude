import json

import pytest
import yaml

from clipfactory import media, render, sources
from conftest import needs_ffmpeg


def _registry(tmp_path, video, tipo="propia", **extra):
    reg = tmp_path / "fuentes.yaml"
    entry = {"id": "f1", "tipo": tipo, "archivo": str(video), "credito": "Clip: @prueba", **extra}
    reg.write_text(yaml.safe_dump({"fuentes": [entry]}), encoding="utf-8")
    return reg


def _job(tmp_path, **kw):
    job = {"id": "T1", "fuente": "f1", "inicio": 1.0, "fin": 6.0, "salida": str(tmp_path / "out.mp4"),
           "gancho": "Nadie vio este detalle del tráiler", "layout": "blur", **kw}
    p = tmp_path / "job.yaml"
    p.write_text(yaml.safe_dump(job, allow_unicode=True), encoding="utf-8")
    return p


@needs_ffmpeg
def test_render_vertical_with_voice_and_captions(tmp_path, synthetic_video, synthetic_voice):
    words = tmp_path / "voz.words.json"
    words.write_text(json.dumps({"words": [{"text": t, "start": i * 0.5, "end": i * 0.5 + 0.4}
                                           for i, t in enumerate("esto es una prueba de subtítulos".split())]}), encoding="utf-8")
    reg = _registry(tmp_path, synthetic_video)
    job = _job(tmp_path, voz=str(synthetic_voice), palabras_voz=str(words), subtitulos="voz")
    out = render.render(job, reg)
    assert media.video_size(out) == (1080, 1920)
    assert 4.5 <= media.duration(out) <= 5.6
    assert media.has_audio(out)


@needs_ffmpeg
def test_render_crop_layout_without_voice(tmp_path, synthetic_video):
    reg = _registry(tmp_path, synthetic_video)
    out = render.render(_job(tmp_path, layout="crop", crop_x=0.3), reg)
    assert media.video_size(out) == (1080, 1920)


@needs_ffmpeg
def test_render_refuses_official_clip_without_commentary(tmp_path, synthetic_video):
    reg = _registry(tmp_path, synthetic_video, tipo="oficial")
    with pytest.raises(sources.PolicyError):
        render.render(_job(tmp_path), reg)


def test_balanced_wrap_avoids_orphans():
    out = render.balanced_wrap("EL DETALLE DEL TRÁILER QUE NADIE VIO", 18).split("\n")
    assert len(out) <= 3
    assert min(len(l) for l in out) >= 8
