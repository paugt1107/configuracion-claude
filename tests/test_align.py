import subprocess

from clipfactory import align
from conftest import needs_ffmpeg


@needs_ffmpeg
def test_words_skip_silence(tmp_path):
    a = tmp_path / "v.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=300:duration=3",
                    "-af", "volume=enable='between(t,1,2)':volume=0", str(a)], check=True)
    w = align.align_words("aaaa bbbb cccc dddd eeee ffff", str(a))
    assert len(w) == 6
    assert w[2]["end"] <= 1.1          # primeras 3 palabras antes del silencio
    assert w[3]["start"] >= 1.9        # el resto después del silencio
    assert all(x["start"] < x["end"] for x in w)
