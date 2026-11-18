import datetime as dt

from clipfactory import radar_web as rw

RSS = b"""<?xml version="1.0"?><rss><channel>
<item><title>GTA 6: el secreto oculto en la primera mision de Lucia</title><link>https://x.com/a</link><pubDate>Thu</pubDate></item>
<item><title>Ventas record de GTA 6</title><link>https://x.com/b</link></item>
</channel></rss>"""
ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>GTA 6 todas las misiones</title><link href="https://youtube.com/watch?v=1"/><published>2026-11-19</published></entry>
</feed>"""


def test_parse_rss_and_atom():
    a = rw.parse_feed(RSS, "n")
    b = rw.parse_feed(ATOM, "yt")
    assert [i["url"] for i in a] == ["https://x.com/a", "https://x.com/b"]
    assert b[0]["title"] == "GTA 6 todas las misiones"


def test_classify_scores_curiosities_higher():
    c1, s1 = rw.classify("GTA 6: el secreto oculto en la primera misión de Lucia")
    c2, s2 = rw.classify("Ventas de GTA 6")
    assert "secreto" in c1 and "misión" in c1 and "personaje" in c1
    assert s1 > s2


def test_update_dedupes_and_writes(tmp_path):
    now = dt.datetime(2026, 11, 19, 10, 30)
    items = rw.parse_feed(RSS, "n")
    new1 = rw.update(items, tmp_path, now)
    new2 = rw.update(items, tmp_path, now)
    assert len(new1) == 2 and new2 == []
    assert "secreto" in (tmp_path / "ultimo.md").read_text()
    assert (tmp_path / "2026-11-19.md").read_text().count("| 10:30 |") == 2
