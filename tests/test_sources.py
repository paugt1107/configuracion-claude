import pytest

from clipfactory import sources
from clipfactory.sources import PolicyError, Source


def test_rejects_unknown_type():
    with pytest.raises(PolicyError):
        sources.validate(Source(id="x", tipo="filtracion", url="u"))


def test_permission_requires_proof_and_credit():
    with pytest.raises(PolicyError):
        sources.validate(Source(id="x", tipo="permiso", url="u", credito="Clip: @a"))
    with pytest.raises(PolicyError):
        sources.validate(Source(id="x", tipo="permiso", url="u", permiso="mail.png"))
    sources.validate(Source(id="x", tipo="permiso", url="u", permiso="mail.png", credito="Clip: @a"))


def test_official_fragment_limit_and_commentary():
    src = Source(id="t", tipo="oficial", url="u", credito="Tráiler oficial")
    sources.check_segment(src, 10, 22, commentary_s=8)
    with pytest.raises(PolicyError):
        sources.check_segment(src, 10, 30, commentary_s=20)  # 20 s > 15 s
    with pytest.raises(PolicyError):
        sources.check_segment(src, 10, 20, commentary_s=2)  # comentario < 50 %


def test_own_footage_has_no_limit():
    src = Source(id="p", tipo="propia", archivo="a.mp4")
    sources.check_segment(src, 0, 600)


def test_registry_loads_example():
    reg = sources.load_registry()
    assert "ejemplo-propia" in reg
    for s in reg.values():
        sources.validate(s)


def test_unregistered_source_is_refused():
    with pytest.raises(PolicyError):
        sources.get_source("no-existe")
