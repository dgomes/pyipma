"""Detect live API fields that pyipma would otherwise silently discard."""

from dataclasses import fields
from datetime import date, datetime

import pytest

from pyipma.auxiliar import (
    District, Districts, Forecast_Location, Forecast_Locations,
    Precipitation_Class, Precipitation_Classes, Sea_Location, Sea_Locations,
    Station, Stations, Weather_Type, Weather_Types,
    Wind_Speed_Daily_Type, Wind_Speed_Daily_Types,
)
from pyipma.forecast import Forecast, Forecast_days
from pyipma.observation import Observation, Observations
from pyipma.rcm import RCM, RCM_day
from pyipma.sea_forecast import SeaForecast, SeaForecasts
from pyipma.uv import UV, UV_risks
from pyipma.warnings import Warning, Warnings


class RecordingAPI:
    """Record responses from actual requests for comparison with parsed objects."""

    def __init__(self, api):
        self.api = api
        self.responses = {}

    async def retrieve(self, url, **kwargs):
        response = await self.api.retrieve(url, **kwargs)
        self.responses[url] = response
        return response


def assert_modeled_fields(rows, model, aliases=()):
    modeled = {field.name for field in fields(model)} | set(aliases)
    received = set().union(*(row.keys() for row in rows))
    assert received <= modeled, f"Unhandled {model.__name__} API fields: {received - modeled}"


@pytest.mark.parametrize(
    ("parser_type", "model", "aliases"),
    [
        (Districts, District, {"latitude", "longitude"}),
        (Forecast_Locations, Forecast_Location, {"latitude", "longitude"}),
        (Sea_Locations, Sea_Location, {"latitude", "longitude"}),
        (Weather_Types, Weather_Type,
         {"idWeatherType", "descWeatherTypeEN", "descWeatherTypePT"}),
        (Wind_Speed_Daily_Types, Wind_Speed_Daily_Type,
         {"classWindSpeed", "descClassWindSpeedDailyEN", "descClassWindSpeedDailyPT"}),
        (Precipitation_Classes, Precipitation_Class,
         {"classPrecInt", "descClassPrecIntEN", "descClassPrecIntPT"}),
    ],
)
async def test_auxiliary_fields(live_api, parser_type, model, aliases):
    api = RecordingAPI(live_api)
    parser = parser_type(api)
    if parser_type in (Districts, Forecast_Locations, Sea_Locations):
        assert await parser.get(None, None)
    else:
        assert isinstance(await parser.get(0), model)
    raw = api.responses[parser.endpoint]
    if isinstance(raw, dict):
        assert set(raw) <= {"owner", "country", "data"}
        assert parser.owner == raw["owner"]
        assert parser.country == raw["country"]
        raw = raw["data"]
    assert_modeled_fields(raw, model, aliases)


async def test_station_fields(live_api):
    api = RecordingAPI(live_api)
    parser = Stations(api)
    assert await parser.get(None, None)
    raw = api.responses[parser.endpoint]
    for feature in raw:
        assert set(feature) <= {"type", "geometry", "properties"}
        assert set(feature["geometry"]) <= {"type", "coordinates"}
    assert_modeled_fields([feature["properties"] for feature in raw], Station)


@pytest.mark.parametrize("period", [1, 3, 24])
@pytest.mark.parametrize("location_id", [1010500, 1030300, 1110600, 2310300, 3470100])
async def test_forecast_fields(live_api, period, location_id):
    api = RecordingAPI(live_api)
    forecasts = await Forecast_days(api).get(location_id, period)
    raw = api.responses[f"http://api.ipma.pt/public-data/forecast/aggregate/{location_id}.json"]
    assert_modeled_fields(raw, Forecast, {"globalIdLocal"})
    by_date = {(row["dataPrev"], row["idPeriodo"]): row for row in raw}
    assert forecasts
    for forecast in forecasts:
        row = by_date[(forecast.dataPrev.replace(tzinfo=None).isoformat(), period)]
        assert forecast.location.globalIdLocal == row["globalIdLocal"]
        for key in (
            "idIntensidadePrecipita", "iUv", "hR", "utci", "marTotal", "ondulacao",
            "periodOndulacao", "periodoPico", "tempAguaMar",
        ):
            value = row.get(key)
            expected = None if value in (None, "", -99, "-99", "-99.0") else float(value)
            assert getattr(forecast, key) == expected
        direction = row.get("dirOndulacao")
        assert forecast.wave_direction == (
            None if direction in (None, "", -99, "-99") else direction
        )
        for name, key in (
            ("wave_height", "marTotal"), ("swell_height", "ondulacao"),
            ("swell_period", "periodOndulacao"), ("peak_period", "periodoPico"),
            ("sea_temperature", "tempAguaMar"),
        ):
            assert getattr(forecast, name) == getattr(forecast, key)


async def test_observation_fields(live_api):
    api = RecordingAPI(live_api)
    assert await Observations(api).get(1210702)
    raw = next(iter(api.responses.values()))
    assert_modeled_fields(
        [row for stations in raw.values() for row in stations.values() if row is not None],
        Observation,
    )


async def test_sea_forecast_fields(live_api):
    api = RecordingAPI(live_api)
    parser = SeaForecasts(api)
    assert await parser.get(1160926)
    for url, raw in api.responses.items():
        if "hp-daily-sea-forecast" not in url:
            continue
        assert set(raw) <= {"owner", "country", "forecastDate", "dataUpdate", "data"}
        assert parser.owner == raw["owner"]
        assert parser.country == raw["country"]
        assert_modeled_fields(raw["data"], SeaForecast, {"globalIdLocal", "latitude", "longitude"})


@pytest.mark.parametrize("day", [0, 1])
async def test_fire_risk_fields(live_api, day):
    api = RecordingAPI(live_api)
    parser = RCM_day(api, day)
    risks = await parser.get(None, None)
    raw = api.responses[parser.endpoint]
    assert set(raw) <= {"dataPrev", "dataRun", "fileDate", "local"}
    assert risks
    for risk in risks:
        assert risk.forecast_date == date.fromisoformat(raw["dataPrev"])
        assert risk.run_date == date.fromisoformat(raw["dataRun"])
        assert risk.update_date == datetime.fromisoformat(raw["fileDate"])
    assert_modeled_fields(raw["local"].values(), RCM, {"latitude", "longitude", "data"})
    assert_modeled_fields([row["data"] for row in raw["local"].values()], RCM)


async def test_uv_fields(live_api):
    api = RecordingAPI(live_api)
    parser = UV_risks(api)
    assert await parser.get()
    assert_modeled_fields(api.responses[parser.endpoint], UV)


async def test_warning_fields(live_api):
    api = RecordingAPI(live_api)
    parser = Warnings(api)
    await parser.get("AVR")
    assert_modeled_fields(api.responses[parser.endpoint], Warning)
