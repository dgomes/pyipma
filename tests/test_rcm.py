import pytest

from pyipma.rcm import RCM_day, RCM


@pytest.mark.asyncio
async def test_rcm(static_api, load_fixture):
    api = static_api(
        {
            "http://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d0.json": load_fixture(
                "fixtures/rcm-d0.json"
            )
        }
    )
    rcms = RCM_day(api)

    d = await rcms.get(40.6405, -8.6538)

    assert len(d) == 278
    assert d[0] == RCM(dico="0105", rcm=2, coordinates=(40.6413, -8.6535))
    assert str(d[0]) == "Risco moderado para Aveiro"
