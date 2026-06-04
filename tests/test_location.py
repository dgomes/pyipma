import aiohttp
from datetime import datetime

from pyipma.api import IPMA_API
from pyipma.location import Location
from pyipma.forecast import Forecast
from pyipma.rcm import RCM
from pyipma.uv import UV


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
