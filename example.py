import asyncio
import aiohttp

from pyipma import Station, IPMA_API

async def main():
    async with aiohttp.ClientSession() as session:
        station = await Station.get(session,  40.6517, -8.7873)
        print("Nearest station is {}".format(station.local))
        print("Current Weather:")
        print(await station.observation())
        print("Next days:")
        for forecast in await station.forecast():
            print(forecast)

        api = IPMA_API(session)
        types = await api.weather_type_classe()
        for t in types.items():
            print(t)

        types = await api.wind_type_classe()
        for t in types.items():
            print(t)

        station = await Station.get(session,  40.52855833, -7.278675)
        print("Nearest station is {}".format(station.local))
        print("Current Weather:")
        print(await station.observation())
        import pprint
        pprint.pprint(station.__dict__)

        station = await Station.get(session,  38.0153, -7.8627)
        print("Nearest station is {}".format(station.local))
        print("Current Weather:")
        print(await station.observation())

asyncio.get_event_loop().run_until_complete(main())


