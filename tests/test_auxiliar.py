import aiohttp
import pytest

from pyipma.api import IPMA_API
from pyipma.auxiliar import (
    District,
    Districts,
    Forecast_Location,
    Forecast_Locations,
    Precipitation_Class,
    Precipitation_Classes,
    Sea_Location,
    Sea_Locations,
    Station,
    Stations,
    Weather_Type,
    Weather_Types,
    Wind_Speed_Daily_Type,
    Wind_Speed_Daily_Types,
)


def assert_location_properties(location):
    assert isinstance(location.globalIdLocal, int)
    assert isinstance(location.local, str)
    assert isinstance(location.idRegiao, int)
    assert isinstance(location.idAreaAviso, str)
    assert isinstance(location.coordinates, tuple)
    assert len(location.coordinates) == 2
    assert all(isinstance(coordinate, float) for coordinate in location.coordinates)


def assert_type_properties(type_object):
    assert isinstance(type_object.id, int)
    assert isinstance(type_object.en, str)
    assert isinstance(type_object.pt, str)
    assert type_object.desc() == type_object.pt
    assert type_object.desc("en") == type_object.en


@pytest.mark.asyncio
async def test_district():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        districts_islands = Districts(api)
        districts = await districts_islands.get(40.6405, -8.6538)

        assert districts
        assert isinstance(districts[0], District)
        assert_location_properties(districts[0])


@pytest.mark.asyncio
async def test_forecast_location():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        forecast_locations = Forecast_Locations(api)
        locations = await forecast_locations.get(40.5804, -8.4412)

        assert locations
        assert isinstance(locations[0], Forecast_Location)
        assert_location_properties(locations[0])


@pytest.mark.asyncio
async def test_sea_location():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        sea_locations = Sea_Locations(api)
        locations = await sea_locations.get(40.6405, -8.6538)

        assert locations
        assert isinstance(locations[0], Sea_Location)
        assert_location_properties(locations[0])


@pytest.mark.asyncio
async def test_station():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        stations = Stations(api)
        station_list = await stations.get(40.6405, -8.6538)

        assert station_list
        assert isinstance(station_list[0], Station)
        assert isinstance(station_list[0].idEstacao, int)
        assert isinstance(station_list[0].localEstacao, str)
        assert isinstance(station_list[0].coordinates, tuple)
        assert len(station_list[0].coordinates) == 2


@pytest.mark.asyncio
async def test_weather_type():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        weather_types = Weather_Types(api)

        weather_type = await weather_types.get(0)
        missing_weather_type = await weather_types.get(-99)

        assert isinstance(weather_type, Weather_Type)
        assert isinstance(missing_weather_type, Weather_Type)
        assert_type_properties(weather_type)
        assert_type_properties(missing_weather_type)


@pytest.mark.asyncio
async def test_wind_speed_daily():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        wind_speed_daily = Wind_Speed_Daily_Types(api)

        wind_type = await wind_speed_daily.get(0)
        missing_wind_type = await wind_speed_daily.get(-99)

        assert_type_properties(wind_type)
        assert_type_properties(missing_wind_type)


@pytest.mark.asyncio
async def test_precipitation():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        precipitation_classes = Precipitation_Classes(api)

        precipitation_type = await precipitation_classes.get(0)
        missing_precipitation_type = await precipitation_classes.get(-99)

        assert_type_properties(precipitation_type)
        assert_type_properties(missing_precipitation_type)
