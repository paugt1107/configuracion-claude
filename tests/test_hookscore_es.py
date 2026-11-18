from clipfactory import hookscore_es as hs


def test_spanish_address_and_curiosity_are_detected():
    weak = hs.score("Hola chicos bienvenidos a un nuevo video increíble")
    strong = hs.score("Si haces esto en la primera hora de GTA 6, pierdes 10 minutos")
    assert strong["veredicto"] > weak["veredicto"] + 15
    assert strong["propiedades"]["TE_HABLA"] > 26
    assert weak["banda"] == "DÉBIL"


def test_brevity_band():
    assert hs.brevity("Nadie vio este detalle en Vice City") == 100
    assert hs.brevity("uno dos") < 100
