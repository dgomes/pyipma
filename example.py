import asyncio
import aiohttp

from pyipma.api import IPMA_API
from pyipma.location import Location


async def main():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        location = await Location.get(api, 40.6517, -8.6573, sea_stations=False)
        print("Forecast for {}".format(location.name))
        print("Nearest station is {}".format(location.station))
        print("Nearest sea station is {}".format(location.sea_station_name))

        obs = await location.observation(api)
        print("Current weather is {}".format(obs))

        forecasts = await location.forecast(api)
        print("Forecast for tomorrow {}".format(forecasts[0]))
        print("UTCI if available: ", forecasts[0].utci)

        sea_forecasts = await location.sea_forecast(api)
        print("Sea forecast for today {}".format(sea_forecasts[0]))


asyncio.run(main())
