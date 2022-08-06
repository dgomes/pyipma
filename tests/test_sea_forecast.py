import datetime

import aiohttp
import pytest

from pyipma.api import IPMA_API
from pyipma.sea_forecast import SeaForecast, SeaForecasts


async def test_observations():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        forecast_3days = SeaForecasts(api)

        aveiro_forecast = await forecast_3days.get(1160926)

        assert len(aveiro_forecast) == 3  # 3 days

        print(aveiro_forecast[0])
        assert aveiro_forecast[0].forecastDate >= (
            datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            - datetime.timedelta(days=1)
        )  # forecast start from today
        assert aveiro_forecast[0].location.globalIdLocal == 1160926
