import datetime

import aiohttp

from pyipma.api import IPMA_API
from pyipma.sea_forecast import SeaForecasts, SeaForecast


def assert_sea_forecast_properties(forecast):
    assert isinstance(forecast, SeaForecast)
    assert forecast.location.globalIdLocal == 1160926
    assert isinstance(forecast.min_swell_period, float)
    assert isinstance(forecast.max_swell_period, float)
    assert isinstance(forecast.min_swell_high, float)
    assert isinstance(forecast.max_swell_high, float)
    assert isinstance(forecast.wave_direction, str)
    assert isinstance(forecast.max_wave_high, float)
    assert isinstance(forecast.min_wave_high, float)
    assert isinstance(forecast.min_temperature, float)
    assert isinstance(forecast.max_temperature, float)
    assert isinstance(forecast.coordinates, tuple)
    assert len(forecast.coordinates) == 2
    assert forecast.forecastDate is not None
    assert forecast.dataUpdate is not None


def test_max_temperature_returns_sst_max():
    forecast = SeaForecast(
        wavePeriodMin=1.0,
        location=None,
        totalSeaMax=2.0,
        waveHighMax=3.0,
        waveHighMin=1.0,
        wavePeriodMax=4.0,
        totalSeaMin=1.0,
        sstMax=19.0,
        predWaveDir="NW",
        sstMin=16.0,
        coordinates=(-9.0, 39.0),
        forecastDate=datetime.datetime(2026, 1, 1),
        dataUpdate=datetime.datetime(2026, 1, 1, 12, 0),
    )

    assert forecast.max_temperature == 19.0
    assert forecast.min_temperature == 16.0


async def test_observations():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        forecast_3days = SeaForecasts(api)

        forecast = await forecast_3days.get(1160926)

        assert forecast
        assert all(isinstance(day_forecast, SeaForecast) for day_forecast in forecast)
        assert_sea_forecast_properties(forecast[0])
