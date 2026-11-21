from datetime import datetime

import pytest

from pyipma import IPMAException
from pyipma.observation import Observation, Observations

ENDPOINT = "https://api.ipma.pt/open-data/observation/meteorology/stations/observations.json"
MEASUREMENTS = {
    "intensidadeVentoKM": "wind_intensity_km",
    "temperatura": "temperature",
    "radiacao": "radiation",
    "precAcumulada": "accumulated_precipitation",
    "intensidadeVento": "wind_intensity",
    "humidade": "humidity",
    "pressao": "pressure",
}


@pytest.mark.parametrize(
    ("value", "expected"),
    [(-99, None), ("-99", None), ("-99.0", None), (None, None), ("", None),
     (0, 0.0), ("0", 0.0), (99, 99.0), ("12.5", 12.5)],
)
async def test_observation_normalizes_measurements(static_api, value, expected):
    row = dict.fromkeys(MEASUREMENTS, value)
    row["idDireccVento"] = 1
    parser = Observations(static_api({ENDPOINT: {"2026-11-21T10:00": {"123": row}}}))

    observations = await parser.get(123)

    assert parser.data is observations
    assert len(observations) == 1
    for field, property_name in MEASUREMENTS.items():
        assert getattr(observations[0], field) == expected
        assert getattr(observations[0], property_name) == expected
    assert observations[0].wind_direction == "N"


@pytest.mark.parametrize(
    ("code", "expected"),
    [(0, ""), (1, "N"), (2, "NE"), (3, "E"), (4, "SE"), (5, "S"),
     (6, "SW"), (7, "W"), (8, "NW"), (9, "N"), ("2", "NE"),
     (-99, ""), ("-99", ""), (None, ""), ("", ""), (42, "")],
)
async def test_observation_wind_direction(static_api, code, expected):
    api = static_api({ENDPOINT: {"2026-11-21T10:00": {"123": {"idDireccVento": code}}}})

    observation, = await Observations(api).get(123)

    assert observation.wind_direction == expected


async def test_observations_filter_station_and_sort_timestamps(static_api):
    api = static_api({ENDPOINT: {
        "2026-11-21T12:00": {"123": {"temperatura": 12}, "456": {"temperatura": 99}},
        "2026-11-21T09:00": {"123": None},
        "2026-11-21T10:00": {"123": {}},
        "2026-11-21T11:00": {"456": {"temperatura": 99}},
    }})

    observations = await Observations(api).get(123)

    assert [item.timestamp for item in observations] == [
        datetime(2026, 11, 21, 10), datetime(2026, 11, 21, 12),
    ]
    assert all(item.idEstacao == 123 for item in observations)
    assert observations[0].timestamp.tzinfo is None
    assert observations[0].idDireccVento is None
    assert observations[0].wind_direction == ""
    assert all(getattr(observations[0], field) is None for field in MEASUREMENTS)
    assert observations[1].temperature == 12.0


async def test_observations_missing_station_clears_previous_result(static_api):
    parser = Observations(static_api({ENDPOINT: {"2026-11-21T10:00": {"123": {}}}}))
    assert await parser.get(123)

    assert await parser.get(456) == []
    assert parser.data == []


async def test_observations_propagate_api_errors(static_api):
    parser = Observations(static_api({ENDPOINT: IPMAException("unavailable")}))

    with pytest.raises(IPMAException, match="unavailable"):
        await parser.get(123)


async def test_observations_reject_invalid_measurements(static_api):
    api = static_api({ENDPOINT: {"2026-11-21T10:00": {"123": {"temperatura": "invalid"}}}})

    with pytest.raises(ValueError):
        await Observations(api).get(123)


async def test_observations(live_api):
    observations = await Observations(live_api).get(1210702)

    assert observations
    assert [item.timestamp for item in observations] == sorted(
        item.timestamp for item in observations
    )
    for observation in observations:
        assert isinstance(observation, Observation)
        assert observation.idEstacao == 1210702
        assert isinstance(observation.timestamp, datetime)
        for value in (
            observation.temperature,
            observation.radiation,
            observation.wind_intensity_km,
            observation.wind_intensity,
            observation.accumulated_precipitation,
            observation.humidity,
            observation.pressure,
        ):
            assert value is None or isinstance(value, (int, float))
        assert isinstance(observation.wind_direction, str)
        assert str(observation).startswith("Weather in 1210702")
