import datetime
import pytest

from pyipma.auxiliar import Forecast_Location, Weather_Type
from pyipma.forecast import Forecast, Forecast_days


@pytest.mark.parametrize("period", [1, 3, 24])
async def test_forecast(live_api, period):
    forecasts = await Forecast_days(live_api).get(1010500, period)

    assert forecasts
    assert [item.forecast_date for item in forecasts] == sorted(
        item.forecast_date for item in forecasts
    )
    for forecast in forecasts:
        assert isinstance(forecast, Forecast)
        assert forecast.location.globalIdLocal == 1010500
        assert forecast.forecasted_hours == period
        assert isinstance(forecast.forecast_date, datetime.datetime)
        assert forecast.forecast_date.tzinfo == datetime.timezone.utc
        assert isinstance(forecast.update_date, datetime.datetime)
        assert isinstance(forecast.weather_type, Weather_Type)
        assert isinstance(forecast.weather_type_description, str)
        assert isinstance(forecast.temperature, float)
        assert forecast.precipitation_intensity is None or isinstance(
            forecast.precipitation_intensity, int
        )
        assert forecast.wind_speed_class is None or isinstance(forecast.wind_speed_class, int)
        for value in (forecast.uv_index, forecast.humidity, forecast.feels_like_temperature):
            assert value is None or isinstance(value, float)


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
        idIntensidadePrecipita=2,
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
    assert forecast.precipitation_intensity == 2
    assert forecast.uv_index == 5.0
    assert forecast.wind_speed_class == 1
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

    forecast.tMed = 0.0
    forecast.tMax = 0.0
    assert forecast.temperature == 0.0
    assert forecast.max_temperature == 0.0
