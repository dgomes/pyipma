from datetime import datetime

from pyipma.observation import Observation, Observations


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
