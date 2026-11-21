"""Static checks for the types exposed to library consumers."""

from typing_extensions import assert_type

from pyipma.api import IPMA_API
from pyipma.auxiliar import (
    District, Districts, Forecast_Location, Forecast_Locations,
    Precipitation_Class, Precipitation_Classes, Sea_Location, Sea_Locations,
    Station, Stations, Weather_Type, Weather_Types,
    Wind_Speed_Daily_Type, Wind_Speed_Daily_Types,
)
from pyipma.forecast import Forecast, Forecast_days
from pyipma.location import Location
from pyipma.observation import Observation, Observations
from pyipma.rcm import RCM, RCM_day
from pyipma.sea_forecast import SeaForecast, SeaForecasts
from pyipma.uv import UV, UV_risks
from pyipma.warnings import Warning, Warnings


async def check_public_api(api: IPMA_API) -> None:
    assert_type(await Districts(api).get(None, None), list[District])
    assert_type(await Forecast_Locations(api).get(None, None), list[Forecast_Location])
    assert_type(await Forecast_Locations(api).find(1010500), Forecast_Location)
    assert_type(await Sea_Locations(api).get(None, None), list[Sea_Location])
    assert_type(await Sea_Locations(api).find(1160926), Sea_Location)
    assert_type(await Stations(api).get(None, None), list[Station])
    assert_type(await Weather_Types(api).get(0), Weather_Type)
    assert_type(await Wind_Speed_Daily_Types(api).get(0), Wind_Speed_Daily_Type)
    assert_type(await Precipitation_Classes(api).get(0), Precipitation_Class)

    forecasts = await Forecast_days(api).get(1010500)
    assert_type(forecasts, list[Forecast])
    assert_type(forecasts[0].temperature, float | None)
    assert_type(forecasts[0].precipitation_intensity, int | None)
    assert_type(forecasts[0].sea_temperature, float | None)
    assert_type(forecasts[0].weather_type, Weather_Type)
    sea_forecasts = await SeaForecasts(api).get(1160926)
    assert_type(sea_forecasts, list[SeaForecast])
    assert_type(sea_forecasts[0].location, Sea_Location)
    assert_type(sea_forecasts[0].max_temperature, float | None)
    assert_type(await Observations(api).get(1210702), list[Observation])
    assert_type(await RCM_day(api).get(None, None), list[RCM])
    assert_type(await UV_risks(api).get(), list[UV])
    assert_type(await Warnings(api).get("AVR"), list[Warning])

    location = await Location.get(api, 40.6517, -8.6573)
    assert_type(location, Location)
    assert_type(await location.forecast(api), list[Forecast])
    assert_type(await location.observation(api), Observation | None)
    assert_type(await location.sea_forecast(api), list[SeaForecast])
    assert_type(await location.fire_risk(api), RCM | None)
    assert_type(await location.uv_risk(api), UV | None)
    assert_type(await location.warnings(api), list[Warning] | None)
