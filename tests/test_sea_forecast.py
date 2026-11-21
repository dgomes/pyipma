import datetime

import aiohttp
import pytest

from pyipma import IPMAException
from pyipma.api import IPMA_API
from pyipma.auxiliar import Sea_Location
from pyipma.sea_forecast import SeaForecasts, SeaForecast


SEA_MEASUREMENTS = {
    "wavePeriodMin": "min_swell_period", "wavePeriodMax": "max_swell_period",
    "waveHighMin": "min_swell_high", "waveHighMax": "max_swell_high",
    "totalSeaMin": "min_wave_high", "totalSeaMax": "max_wave_high",
    "sstMin": "min_temperature", "sstMax": "max_temperature",
}


def sea_payloads(value):
    return {
        f"http://api.ipma.pt/open-data/forecast/oceanography/daily/hp-daily-sea-forecast-day{day}.json": {
            "owner": "IPMA", "country": "PT",
            "forecastDate": f"2026-11-{23 - day}",
            "dataUpdate": "2026-11-21T06:00:00",
            "data": [dict.fromkeys(SEA_MEASUREMENTS, value) | {
                "globalIdLocal": "1160926", "longitude": "-9.0", "latitude": "39.0",
            }],
        }
        for day in range(3)
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, 0.0), ("0", 0.0), (-99, None), ("-99.0", None),
     (None, None), ("", None), ("2.5", 2.5)],
)
async def test_sea_measurements_and_chronological_order(static_api, value, expected):
    parser = SeaForecasts(static_api(sea_payloads(value)))
    parser.sea_locations.data = [Sea_Location(1160926, "Coast", 1, "AVR", 1, (39.0, -9.0))]

    forecasts = await parser.get(1160926)

    assert len(forecasts) == 3
    assert [f.forecastDate.day for f in forecasts] == [21, 22, 23]
    assert parser.owner == "IPMA"
    assert parser.country == "PT"
    for forecast in forecasts:
        assert forecast.wave_direction == ""
        assert forecast.coordinates == (-9.0, 39.0)
        for field, property_name in SEA_MEASUREMENTS.items():
            assert getattr(forecast, field) == expected
            assert getattr(forecast, property_name) == expected


async def test_sea_missing_measurements_and_direction(static_api):
    payloads = sea_payloads(1)
    for payload in payloads.values():
        for field in SEA_MEASUREMENTS:
            del payload["data"][0][field]
        payload["data"][0]["predWaveDir"] = "-99"
    parser = SeaForecasts(static_api(payloads))
    parser.sea_locations.data = [Sea_Location(1160926, "Coast", 1, "AVR", 1, (39.0, -9.0))]

    for forecast in await parser.get(1160926):
        assert forecast.wave_direction == ""
        assert all(getattr(forecast, field) is None for field in SEA_MEASUREMENTS)
    assert await parser.get(999) == []


async def test_sea_failure_does_not_store_partial_results(static_api):
    payloads = sea_payloads(1)
    payloads[list(payloads)[1]] = IPMAException("unavailable")
    parser = SeaForecasts(static_api(payloads))
    parser.sea_locations.data = [Sea_Location(1160926, "Coast", 1, "AVR", 1, (39.0, -9.0))]

    with pytest.raises(IPMAException, match="unavailable"):
        await parser.get(1160926)
    assert parser.data is None


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

        assert forecast_3days.owner == "IPMA"
        assert forecast_3days.country == "PT"
        assert forecast
        assert all(isinstance(day_forecast, SeaForecast) for day_forecast in forecast)
        assert_sea_forecast_properties(forecast[0])
