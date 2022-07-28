import datetime

import aiohttp
import pytest
from pyipma.api import IPMA_API
from pyipma.observation import Observation, Observations


async def test_observations():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        obs = Observations(api)

        aveiro_obs = await obs.get(1210702)

        assert len(aveiro_obs) == 24  # hourly observations for the last day

        assert aveiro_obs[0].idEstacao == 1210702
