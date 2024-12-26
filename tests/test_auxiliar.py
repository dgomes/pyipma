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


@pytest.mark.asyncio
async def test_district():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        districts_islands = Districts(api)

        d = await districts_islands.get(40.6405, -8.6538)

        assert len(d) == 35
        assert d[0] == District(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535))


@pytest.mark.asyncio
async def test_forecast_location():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        forecast_locations = Forecast_Locations(api)

        d = await forecast_locations.get(40.5804, -8.4412)

        assert len(d) == 423
        assert d[0].globalIdLocal == 1010100
        assert d[0] == Forecast_Location(
            1010100, "Águeda", 1, 1, 1, "AVR", (40.5800, -8.4400)
        )


@pytest.mark.asyncio
async def test_sea_location():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        sea_locations = Sea_Locations(api)

        d = await sea_locations.get(40.6405, -8.6538)

        assert len(d) == 12
        assert d[0] == Sea_Location(
            1060526, "Figueira da Foz, Costa", 1, "CBR", 302, (40.1417, -8.8783)
        )


@pytest.mark.asyncio
async def test_station():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        stations = Stations(api)

        s = await stations.get(40.6405, -8.6538)

        assert len(s) == 216
        assert s[0] == Station(
            1210702, "Aveiro (Universidade)", (40.63529722, -8.65958333)
        )


@pytest.mark.asyncio
async def test_weather_type():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        weather_types = Weather_Types(api)

        w = await weather_types.get(0)

        assert w.desc() == w.pt
        assert w.en == "No information"

        w = await weather_types.get(-99)

        assert w.desc() == w.pt
        assert w.en == "--"


@pytest.mark.asyncio
async def test_wind_speed_daily():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        wind_speed_daily = Wind_Speed_Daily_Types(api)

        w = await wind_speed_daily.get(0)

        assert w.desc() == w.pt
        assert w.en == "Weak"

        w = await wind_speed_daily.get(-99)

        assert w.desc() == w.pt
        assert w.en == "--"


@pytest.mark.asyncio
async def test_precipitation():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        precipitation_classes = Precipitation_Classes(api)

        w = await precipitation_classes.get(0)

        assert w.desc() == w.pt
        assert w.en == "No precipitation"

        w = await precipitation_classes.get(-99)

        assert w.desc() == w.pt
        assert w.en == "--"
