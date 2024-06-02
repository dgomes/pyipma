import asyncio
import pprint
import aiohttp

from pyipma.api import IPMA_API
from pyipma.location import Location

LAT, LON =  37.1460511137383, -8.541564345359804    #Portimao
                    
#LAT, LON = 39.663396, -8.813334 Leiria
#LAT, LON = 41.221894, -8.541423 

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

async def main():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        location = await Location.get(api, LAT, LON, sea_stations=True)
        print("Forecast for {}".format(location.name))
        print("Nearest station is {}".format(location.station))
        print("Nearest sea station is {}".format(location.sea_station_name))

        obs = await location.observation(api)
        print("Current Weather based on observation: {}".format(obs))

        forecasts = await location.forecast(api, 1)
        print("Current Weather based on forecast data for the next hour: {}".format(forecasts[0]))
        print("UTCI if available: ", forecasts[0].utci)

        sea_forecasts = await location.sea_forecast(api)
        print("Sea forecast for today {}".format(sea_forecasts[0]))


asyncio.run(main())
