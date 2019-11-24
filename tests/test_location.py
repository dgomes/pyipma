import pytest
import aiohttp
from mock import patch

from pyipma.api import IPMA_API
from pyipma.location import Location

async def dump_json(data):
    return data

@pytest.mark.asyncio
async def test_location():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        location = await Location.get(api,  40.6517, -8.6573)
        print("Forecast for {}".format(location.name))
        print("Nearest station is {}".format(location.station))
        assert location.name == "Aveiro"
        assert location.station == "Aveiro (Universidade)"

        #1210702 is the idEstacao for Aveiro (Universidade)
        assert location.id_station == 1210702
        with patch.object(api, "retrieve", return_value=dump_json({"data": {
            str(location.id_station): {"temperatura": 10, "humidade": 80}
            }})): 
            obs = await location.observation(api)
            assert obs.temperatura == 10
            assert obs.humidade == 80
        
        #1010500 is the globalIdLocal for Aveiro
        assert location.global_id_local == 1010500
        with patch.object(api, "retrieve", return_value=dump_json([
            {"globalIdLocal": location.global_id_local, "dataPrev": "2019-11-23T00:00:00", "tMed": 9}
        ])):
            forecasts = await location.forecast(api)
            assert forecasts[0].temperature == 9.0

        
