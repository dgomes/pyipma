import aiohttp
from datetime import datetime

from pyipma.api import IPMA_API
from pyipma.auxiliar import District, Forecast_Location, Sea_Location, Station
from pyipma.location import Location
import pyipma.location as location_module
from pyipma.forecast import Forecast
from pyipma.rcm import RCM
from pyipma.uv import UV
from pyipma.warnings import Warning


def assert_location_properties(location):
    assert isinstance(location.name, str)
    assert isinstance(location.global_id_local, int)
    assert isinstance(location.station, str)
    assert isinstance(location.id_station, int)
    assert isinstance(location.station_latitude, float)
    assert isinstance(location.station_longitude, float)


def assert_forecast_properties(forecast):
    assert isinstance(forecast, Forecast)
    assert forecast.location is not None
    assert forecast.update_date is not None
    assert forecast.forecast_date is not None
    assert isinstance(forecast.forecasted_hours, int)
    assert isinstance(forecast.weather_type_description, str)
    assert isinstance(forecast.weather_type_description_pt, str)


async def test_location():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        location = await Location.get(api, 40.6517, -8.6573)
        assert_location_properties(location)

        obs = await location.observation(api)
        assert isinstance(obs.timestamp, datetime)
        assert isinstance(obs.temperature, float)
        assert isinstance(obs.humidity, float)

        forecasts = await location.forecast(api)
        assert forecasts
        assert_forecast_properties(forecasts[0])

        rcm = await location.fire_risk(api)
        assert isinstance(rcm, RCM)
        assert isinstance(rcm.dico, str)
        assert isinstance(rcm.rcm, int)
        assert isinstance(rcm.coordinates, tuple)

        uv = await location.uv_risk(api)
        assert isinstance(uv, UV)
        assert isinstance(uv.idPeriodo, int)
        assert isinstance(uv.intervaloHora, str)
        assert isinstance(uv.data, datetime)
        assert isinstance(uv.globalIdLocal, int)
        assert isinstance(uv.iUv, float)


async def test_location_sea_station_properties_and_warnings(static_api):
    location = Location(
        latitude=40.6413,
        longitude=-8.6535,
        forecast_locations=[
            Forecast_Location(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))
        ],
        observation_stations=[
            Station(1210702, "Aveiro (Universidade)", (40.63529722, -8.65958333))
        ],
        sea_stations=[
            Sea_Location(1060526, "Figueira da Foz, Costa", 1, "CBR", 302, (40.1417, -8.8783))
        ],
    )
    location.districts = [
        District(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))
    ]

    assert location.sea_station_name == "Figueira da Foz, Costa"
    assert location.sea_station_global_id_local == 1060526

    api = static_api(
        {
            "https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json": [
                {
                    "text": "Chuva forte",
                    "awarenessTypeName": "Precipitação",
                    "idAreaAviso": "AVR",
                    "startTime": "2026-06-04T06:00:00",
                    "awarenessLevelID": "yellow",
                    "endTime": "2026-06-04T18:00:00",
                }
            ]
        }
    )
    warnings = await location.warnings(api)

    assert warnings == [
        Warning(
            "Chuva forte",
            "Precipitação",
            "AVR",
            datetime(2026, 6, 4, 6, 0),
            "yellow",
            datetime(2026, 6, 4, 18, 0),
        )
    ]


def test_location_without_sea_stations_returns_none():
    location = Location(
        latitude=40.6413,
        longitude=-8.6535,
        forecast_locations=[
            Forecast_Location(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))
        ],
        observation_stations=[
            Station(1210702, "Aveiro (Universidade)", (40.63529722, -8.65958333))
        ],
        sea_stations=None,
    )

    assert location.sea_station_name is None
    assert location.sea_station_global_id_local is None


async def test_location_get_can_include_sea_stations(monkeypatch):
    class FakeForecastLocations:
        def __init__(self, api):
            pass

        async def get(self, lon, lat):
            return [
                Forecast_Location(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))
            ]

    class FakeStations:
        def __init__(self, api):
            pass

        async def get(self, lon, lat):
            return [Station(1210702, "Aveiro (Universidade)", (40.63529722, -8.65958333))]

    class FakeSeaLocations:
        def __init__(self, api):
            pass

        async def get(self, lon, lat):
            return [
                Sea_Location(
                    1060526,
                    "Figueira da Foz, Costa",
                    1,
                    "CBR",
                    302,
                    (40.1417, -8.8783),
                )
            ]

    monkeypatch.setattr(location_module, "Forecast_Locations", FakeForecastLocations)
    monkeypatch.setattr(location_module, "Stations", FakeStations)
    monkeypatch.setattr(location_module, "Sea_Locations", FakeSeaLocations)

    location = await Location.get(None, 40.6517, -8.6573, sea_stations=True)

    assert location.sea_station_name == "Figueira da Foz, Costa"


async def test_location_forecast_returns_empty_after_endpoint_error(monkeypatch):
    class FakeForecastDays:
        def __init__(self, api):
            pass

        async def get(self, global_id_local, period):
            raise RuntimeError("boom")

    monkeypatch.setattr(location_module, "Forecast_days", FakeForecastDays)
    location = Location(
        40.6413,
        -8.6535,
        [Forecast_Location(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))],
        [Station(1210702, "Aveiro (Universidade)", (40.63529722, -8.65958333))],
        None,
    )

    assert await location.forecast(None) == []


async def test_location_observation_returns_none_after_endpoint_error(monkeypatch):
    class FakeObservations:
        def __init__(self, api):
            pass

        async def get(self, station_id):
            raise RuntimeError("boom")

    monkeypatch.setattr(location_module, "Observations", FakeObservations)
    location = Location(
        40.6413,
        -8.6535,
        [Forecast_Location(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))],
        [Station(1210702, "Aveiro (Universidade)", (40.63529722, -8.65958333))],
        None,
    )

    assert await location.observation(None) is None


async def test_location_sea_forecast_uses_first_valid_location(monkeypatch):
    class FakeSeaForecasts:
        def __init__(self, api):
            pass

        async def get(self, global_id_local):
            return ["forecast"]

    monkeypatch.setattr(location_module, "SeaForecasts", FakeSeaForecasts)
    location = Location(
        40.6413,
        -8.6535,
        [Forecast_Location(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))],
        [Station(1210702, "Aveiro (Universidade)", (40.63529722, -8.65958333))],
        [Sea_Location(1060526, "Figueira da Foz, Costa", 1, "CBR", 302, (40.1417, -8.8783))],
    )

    assert await location.sea_forecast(None) == ["forecast"]


async def test_location_risk_methods_return_none_after_endpoint_errors(monkeypatch):
    class FakeRCMDay:
        def __init__(self, api, day):
            pass

        async def get(self, lon, lat):
            raise RuntimeError("boom")

    class FakeUVRisks:
        def __init__(self, api):
            pass

        async def get(self, global_id_local):
            raise RuntimeError("boom")

    monkeypatch.setattr(location_module, "RCM_day", FakeRCMDay)
    monkeypatch.setattr(location_module, "UV_risks", FakeUVRisks)
    location = Location(
        40.6413,
        -8.6535,
        [Forecast_Location(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))],
        [Station(1210702, "Aveiro (Universidade)", (40.63529722, -8.65958333))],
        None,
    )
    location.districts = [
        District(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))
    ]

    assert await location.fire_risk(None) is None
    assert await location.uv_risk(None) is None


async def test_location_warnings_returns_none_after_endpoint_error(monkeypatch):
    class FakeWarnings:
        def __init__(self, api):
            pass

        async def get(self, area_id):
            raise RuntimeError("boom")

    monkeypatch.setattr(location_module, "Warnings", FakeWarnings)
    location = Location(
        40.6413,
        -8.6535,
        [Forecast_Location(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))],
        [Station(1210702, "Aveiro (Universidade)", (40.63529722, -8.65958333))],
        None,
    )
    location.districts = [
        District(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))
    ]

    assert await location.warnings(None) is None
