import asyncio
import aiohttp

from pyipma.api import IPMA_API
from pyipma.location import Location

async def main():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        location = await Location.get(api,  40.6517, -8.6573)
        print("Forecast for {}".format(location.name))
        print("Nearest station is {}".format(location.station))

        obs = await location.observation(api)
        print("Current weather is {}".format(obs))

        forecasts = await location.forecast(api)
        print("Forecast for tomorrow {}".format(forecasts[0]))

asyncio.get_event_loop().run_until_complete(main())
