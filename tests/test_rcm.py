import aiohttp
import json
import pytest
from aioresponses import aioresponses

from pyipma.api import IPMA_API
from pyipma.rcm import RCM_day, RCM

@pytest.mark.asyncio
async def test_rcm():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)


        with aioresponses() as mocked:
            mocked.get(
                "http://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d0.json",
                status=200,
                payload=json.load(open("fixtures/rcm-d0.json")),
            )
            rcms = RCM_day(api)

            d = await rcms.get(40.6405, -8.6538)

            assert len(d) == 278
            assert d[0] == RCM(dico='0105', rcm=2, coordinates=(40.6413, -8.6535))
            assert str(d[0]) == "Risco moderado para Aveiro"
