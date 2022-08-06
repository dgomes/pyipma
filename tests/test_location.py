import json

import aiohttp
import pytest
from aioresponses import aioresponses
from mock import patch
from freezegun import freeze_time

from pyipma.api import IPMA_API
from pyipma.location import Location


def dump_json(data):
    return data

@freeze_time("2022-07-28")
async def test_location():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        location = await Location.get(api, 40.6517, -8.6573)
        print("Forecast for {}".format(location.name))
        print("Nearest station is {}".format(location.station))
        assert location.name == "Aveiro"
        assert location.station == "Aveiro (Universidade)"

        # 1210702 is the idEstacao for Aveiro (Universidade)
        assert location.id_station == 1210702

        with aioresponses() as mocked:
            mocked.get(
                "https://api.ipma.pt/open-data/observation/meteorology/stations/observations.json",
                status=200,
                payload=json.load(open("fixtures/observations.json")),
            )
            obs = await location.observation(api)
            assert obs.temperature == 17.7
            assert obs.humidity == 88.0

            # 1010500 is the globalIdLocal for Aveiro
            assert location.global_id_local == 1010500

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
            forecasts = await location.forecast(api)
            assert forecasts[0].temperature == 19.5
