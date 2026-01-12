import aiohttp
import json
import pytest
from aioresponses import aioresponses
import datetime

from pyipma.api import IPMA_API
from pyipma.uv import UV_risks, UV

@pytest.mark.asyncio
async def test_low_uv():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        with aioresponses() as mocked:
            mocked.get(
                "https://api.ipma.pt/open-data/forecast/meteorology/uv/uv.json",
                status=200,
                payload=json.load(open("fixtures/uv.json")),
            )
            uv = UV_risks(api)

            d = await uv.get(1090821)

            assert len(d) == 3
            assert d[0] == UV(
                idPeriodo=2,
                intervaloHora="12h-14h",
                data=datetime.datetime(2022, 9, 4, 0, 0),
                globalIdLocal=1090821,
                iUv=1.2,
            )
            assert (
                str(d[0])
                == "Baixo - Não é necessário proteção"
            )

@pytest.mark.asyncio
async def test_medium_uv():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        with aioresponses() as mocked:
            mocked.get(
                "https://api.ipma.pt/open-data/forecast/meteorology/uv/uv.json",
                status=200,
                payload=json.load(open("fixtures/uv.json")),
            )
            uv = UV_risks(api)

            d = await uv.get(3480200)

            assert len(d) == 3
            assert d[1] == UV(
                idPeriodo=1,
                intervaloHora="14h-15h",
                data=datetime.datetime(2022, 9, 5, 0, 0),
                globalIdLocal=3480200,
                iUv=4.1,
            )
            assert (
                str(d[1])
                == "Moderado - Óculos de Sol e protector solar"
            )

@pytest.mark.asyncio
async def test_high_uv():
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

@pytest.mark.asyncio
async def test_veryhigh_uv():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        with aioresponses() as mocked:
            mocked.get(
                "https://api.ipma.pt/open-data/forecast/meteorology/uv/uv.json",
                status=200,
                payload=json.load(open("fixtures/uv.json")),
            )
            uv = UV_risks(api)

            d = await uv.get(2320100)

            assert len(d) == 3
            assert d[0] == UV(
                idPeriodo=3,
                intervaloHora="13h-16h",
                data=datetime.datetime(2022, 9, 4, 0, 0),
                globalIdLocal=2320100,
                iUv=7.5,
            )
            assert (
                str(d[0])
                == "Muito Elevado - Utilizar óculos de Sol com filtro UV, chapéu, t-shirt, guarda-sol, protector solar e evitar a exposição das crianças ao Sol"
            )

@pytest.mark.asyncio
async def test_extreme_uv():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        with aioresponses() as mocked:
            mocked.get(
                "https://api.ipma.pt/open-data/forecast/meteorology/uv/uv.json",
                status=200,
                payload=json.load(open("fixtures/uv.json")),
            )
            uv = UV_risks(api)

            d = await uv.get(2310300)

            assert len(d) == 3
            assert d[2] == UV(
                idPeriodo=4,
                intervaloHora="12h-16h",
                data=datetime.datetime(2022, 9, 6, 0, 0),
                globalIdLocal=2310300,
                iUv=10.3,
            )
            assert (
                str(d[2])
                == "Extremo - Evitar o mais possível a exposição ao Sol. Aproveite para descansar em casa."
            )


