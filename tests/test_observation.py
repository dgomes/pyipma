import datetime
import json

import aiohttp
import pytest
from aioresponses import aioresponses

from pyipma.api import IPMA_API
from pyipma.observation import Observation, Observations


async def test_observations():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        with aioresponses() as mocked:
            mocked.get(
                "https://api.ipma.pt/open-data/observation/meteorology/stations/observations.json",
                status=200,
                payload=json.load(open("fixtures/observations.json")),
            )

            obs = Observations(api)

            aveiro_obs = await obs.get(1210702)

            assert len(aveiro_obs) == 24  # hourly observations for the last day

            assert aveiro_obs[0].idEstacao == 1210702

            assert aveiro_obs[0].temperature == 17.7
            assert aveiro_obs[0].radiation == 0.0
            assert aveiro_obs[0].wind_intensity_km == 10.8
            assert aveiro_obs[0].wind_intensity == 3.0
            assert aveiro_obs[0].wind_direction == "N"
            assert aveiro_obs[0].accumulated_precipitation == 0.0
            assert aveiro_obs[0].humidity == 88.0
            assert aveiro_obs[0].pressure == 1018.0
            assert str(aveiro_obs[0]).startswith("Weather in 1210702")
