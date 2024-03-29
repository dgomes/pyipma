import datetime
import json

import aiohttp
from aioresponses import aioresponses
from freezegun import freeze_time

from pyipma.api import IPMA_API
from pyipma.forecast import Forecast_days


@freeze_time("2022-07-28")
async def test_forecast():
    async with aiohttp.ClientSession() as session:
        with aioresponses() as mocked:

            api = IPMA_API(session)

            mocked.get(
                "http://api.ipma.pt/public-data/forecast/aggregate/1010500.json",
                status=200,
                payload=json.load(open("fixtures/1010500.json")),
            )
            mocked.get(
                "https://api.ipma.pt/open-data/weather-type-classe.json",
                status=200,
                payload=json.load(open("fixtures/weather-type-classe.json")),
            )
            mocked.get(
                "http://api.ipma.pt/public-data/forecast/locations.json",
                status=200,
                payload=json.load(open("fixtures/locations.json")),
            )

            forecast_10days = Forecast_days(api)

            aveiro_forecast = await forecast_10days.get(1010500, 24)

            assert len(aveiro_forecast) == 10  # mocked days forecasted

            assert aveiro_forecast[0].dataPrev == datetime.datetime(
                2022, 7, 28, 0, 0, tzinfo=datetime.timezone.utc
            )
            assert aveiro_forecast[0].location.globalIdLocal == 1010500
            assert aveiro_forecast[1].idTipoTempo.desc() == "Céu pouco nublado"
