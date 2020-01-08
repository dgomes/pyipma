import pytest
import aiohttp

from pyipma.api import IPMA_API
from pyipma.entities import DistritIsland, WeatherType, WindSpeedDaily, Precipitation

@pytest.mark.asyncio
async def test_districts_islands():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)
        
        districts = await DistritIsland.get(api)

        assert len(districts) == 29
        assert len(districts[1010500]) == 8
        assert districts[1010500].local == "Aveiro"


@pytest.mark.asyncio
async def test_weather_types():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)
        weather_types = await WeatherType.get(api)

        assert len(weather_types) == 29
        assert len(weather_types[0]) == 3
        assert weather_types[0].descIdWeatherTypeEN == "No information"


@pytest.mark.asyncio
async def test_wind_speed():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)
        wind_speed = await WindSpeedDaily.get(api)

        assert len(wind_speed) == 5
        assert len(wind_speed["-99"]) == 3
        assert wind_speed["1"].descClassWindSpeedDailyEN == "Weak"

@pytest.mark.asyncio
async def test_wind_speed():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)
        precipitation = await Precipitation.get(api)

        assert len(precipitation) == 5
        assert len(precipitation["-99"]) == 3
        assert precipitation["1"].descClassPrecIntEN == "Weak"