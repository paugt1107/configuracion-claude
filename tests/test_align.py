import subprocess

from conftest import needs_ffmpeg

from clipfactory import align


@needs_ffmpeg
def test_words_skip_silence(tmp_path):
    a = tmp_path / "v.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=300:duration=3",
            "-af",
            "volume=enable='between(t,1,2)':volume=0",
            str(a),
        ],
        check=True,
    )
    w = align.align_words("aaaa bbbb cccc dddd eeee ffff", str(a))
    assert len(w) == 6
    # ninguna palabra puede ocupar el silencio (1.1 s - 1.9 s)
    assert all(x["end"] <= 1.1 or x["start"] >= 1.9 for x in w)
    assert any(x["start"] >= 1.9 for x in w)  # hay palabras tras la pausa
    assert all(x["start"] < x["end"] for x in w)
