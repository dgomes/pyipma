import pytest
import aiohttp

from pyipma.api import IPMA_API
from pyipma.station import Station

@pytest.mark.asyncio
async def test_stations():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)
 
        station = await Station.get(api,  40.6517, -8.7873)
        print("Forecast for {}".format(station.local))
        print("Nearest station is {}".format(station.localEstacao))
        assert station.local == "Aveiro"
        assert station.localEstacao == "Aveiro (Universidade)"

        obs = await station.observation(api)
        assert obs.temperatura == 13.4
#        print(await station.observation())
#        print("Next days:")
#        for forecast in await station.forecast():
#            print(forecast)