import datetime

import aiohttp
import pytest
from pyipma.api import IPMA_API
from pyipma.forecast import Forecast, Forecast_days


async def test_forecast():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        forecast_10days = Forecast_days(api)

        aveiro_forecast = await forecast_10days.get(1010500)

        assert len(aveiro_forecast) == 10  # days forecasted

        assert aveiro_forecast[0].dataPrev >= (
            datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            - datetime.timedelta(days=1)
        )  # forecast start from today
        assert aveiro_forecast[0].location.globalIdLocal == 1010500
