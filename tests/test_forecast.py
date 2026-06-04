import datetime
import json

import aiohttp
from aioresponses import aioresponses
from freezegun import freeze_time

from pyipma.api import IPMA_API
from pyipma.auxiliar import Forecast_Location, Weather_Type
from pyipma.forecast import Forecast, Forecast_days


@freeze_time("2022-07-28")
async def test_forecast():
    async with aiohttp.ClientSession() as session:
        with aioresponses() as mocked:

            api = IPMA_API(session)

            mocked.get(
                "http://api.ipma.pt/public-data/forecast/aggregate/1010500.json",
                status=200,
                payload=json.load(open("fixtures/1010500.json")),
            )
            mocked.get(
                "https://api.ipma.pt/open-data/weather-type-classe.json",
                status=200,
                payload=json.load(open("fixtures/weather-type-classe.json")),
            )
            mocked.get(
                "http://api.ipma.pt/public-data/forecast/locations.json",
                status=200,
                payload=json.load(open("fixtures/locations.json")),
            )

            forecast_10days = Forecast_days(api)

            aveiro_forecast = await forecast_10days.get(1010500, 24)

            assert len(aveiro_forecast) == 10  # mocked days forecasted

            assert aveiro_forecast[0].dataPrev == datetime.datetime(
                2022, 7, 28, 0, 0, tzinfo=datetime.timezone.utc
            )
            assert aveiro_forecast[0].location.globalIdLocal == 1010500
            assert aveiro_forecast[1].idTipoTempo.desc() == "Céu pouco nublado"


def test_forecast_properties_and_string_without_humidity():
    weather_type = Weather_Type(2, "Partly cloudy", "Céu pouco nublado")
    location = Forecast_Location(
        1010500,
        "Aveiro",
        1,
        1,
        5,
        "AVR",
        (40.6413, -8.6535),
    )
    forecast = Forecast(
        tMed=None,
        tMin=10.0,
        ffVento=3.5,
        idFfxVento=1,
        dataUpdate=datetime.datetime(2022, 7, 28, 6, 0),
        tMax=20.0,
        iUv=5.0,
        intervaloHora="00h-24h",
        idTipoTempo=weather_type,
        hR=None,
        location=location,
        probabilidadePrecipita=25.0,
        idPeriodo=24,
        dataPrev=datetime.datetime(2022, 7, 29, tzinfo=datetime.timezone.utc),
        ddVento="NW",
        utci=18.0,
    )

    assert forecast.update_date == forecast.dataUpdate
    assert forecast.forecast_date == forecast.dataPrev
    assert forecast.forecasted_hours == 24
    assert forecast.temperature == 15.0
    assert forecast.max_temperature == 20.0
    assert forecast.min_temperature == 10.0
    assert forecast.feels_like_temperature == 18.0
    assert forecast.humidity is None
    assert forecast.precipitation_probability == 25.0
    assert forecast.wind_direction == "NW"
    assert forecast.wind_strength == 3.5
    assert forecast.weather_type == weather_type
    assert forecast.weather_type_description == "Partly cloudy"
    assert forecast.weather_type_description_pt == "Céu pouco nublado"
    assert "Partly cloudy" in str(forecast)


def test_forecast_string_with_humidity_and_max_temperature_fallback():
    forecast = Forecast(
        tMed=12.0,
        tMin=None,
        ffVento=None,
        idFfxVento=1,
        dataUpdate=datetime.datetime(2022, 7, 28, 6, 0),
        tMax=None,
        iUv=None,
        intervaloHora="00h-24h",
        idTipoTempo=Weather_Type(0, "No information", "Sem informação"),
        hR=80.0,
        location=Forecast_Location(1010500, "Aveiro", 1, 1, 5, "AVR", (40.6413, -8.6535)),
        probabilidadePrecipita=None,
        idPeriodo=24,
        dataPrev=datetime.datetime(2022, 7, 29, tzinfo=datetime.timezone.utc),
        ddVento="",
    )

    assert forecast.temperature == 12.0
    assert forecast.max_temperature == 12.0
    assert "80.0%" in str(forecast)
