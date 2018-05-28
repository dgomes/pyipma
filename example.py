import asyncio
import aiohttp

from pyipma import Station 

async def main():
    async with aiohttp.ClientSession() as session:
        station = await Station.get(session, 40.614,-8.642)
        print("Nearest station if {}".format(station.local))
        print("Current Weather:")
        print(await station.observation())
        print("Next days:")
        for forecast in await station.forecast():
            print(forecast)

asyncio.get_event_loop().run_until_complete(main())


