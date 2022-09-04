import aiohttp
import json
import pytest
from aioresponses import aioresponses
import datetime

from pyipma.api import IPMA_API
from pyipma.uv import UV_risks, UV


@pytest.mark.asyncio
async def test_uv():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        with aioresponses() as mocked:
            mocked.get(
                "https://api.ipma.pt/open-data/forecast/meteorology/uv/uv.json",
                status=200,
                payload=json.load(open("fixtures/uv.json")),
            )
            uv = UV_risks(api)

            d = await uv.get(1010500)

            assert len(d) == 6
            assert d[0] == UV(
                idPeriodo=0,
                intervaloHora="14h-14h",
                data=datetime.datetime(2022, 9, 4, 0, 0),
                globalIdLocal=1010500,
                iUv=5.9,
            )
            assert (
                str(d[0])
                == "Elevado - Utilizar óculos de Sol com filtro UV, chapéu, t-shirt e protector solar"
            )
