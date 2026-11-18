from clipfactory import trends


def test_multiple_uses_channel_median():
    assert trends.multiple(1000, [100, 100, 100, 100]) == 10.0
    assert trends.multiple(1000, [100, 100, 100]) is None  # < 4 vídeos


def test_rank_flags_alarm():
    vids = [{"id": "a", "views": 5000, "channel_id": "c1", "title": "A", "channel": "C1", "url": "u"},
            {"id": "b", "views": 900_000, "channel_id": "c2", "title": "B", "channel": "C2", "url": "u"}]
    hist = {"c1": [400, 500, 450, 520], "c2": [800_000, 900_000, 1_000_000, 950_000]}
    ranked = trends.rank(vids, hist, alarm=10)
    assert ranked[0]["id"] == "a" and ranked[0]["alarma"] is True  # 10.5x aunque tenga menos vistas
    assert ranked[1]["alarma"] is False
    md = trends.report_markdown("gta 6", ranked)
    assert "ALARMA" in md and "| 1 |" in md
