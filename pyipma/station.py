import asyncio
import logging
import json
import aiohttp

from collections import namedtuple
from bs4 import BeautifulSoup
from geopy import distance

from .consts import STATIONS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Station:
    """Represents a Meteo Station (district)."""

    async def retrieve(self, url, **kwargs):
        try:
            async with self.websession.request('GET', url) as res:
                if res.content_type == 'application/json':
                    return await res.json()
                else:
                    return await res.text()
        except aiohttp.client_exceptions as err:
            logging.error(error)

    @classmethod
    async def get(cls, websession, lat, lon):
        """Retrieve the nearest station."""
       
        self = Station()
        self.websession = websession

        data = await self.retrieve("http://api.ipma.pt/open-data/distrits-islands.json")

        me = (lat, lon)
        closest = None

        for station in data['data']:
            station_loc = (float(station['latitude']), float(station['longitude']))
            station_distance = distance.distance(me, station_loc).km 
            if not closest or station_distance < closest_distance:
                closest = station
                closest_distance = station_distance

        self.idRegiao = closest['idRegiao']
        self.idAreaAviso = closest['idAreaAviso']
        self.idConselho = closest['idConcelho']
        self.globalIdLocal = closest['globalIdLocal']
        self.latitude = closest['latitude']
        self.idDistrito = closest['idDistrito']
        self.local = closest['local']
        self.longitude = closest['longitude']

        return self

    async def forecast(self):
        
        data = await self.retrieve("http://api.ipma.pt/open-data/forecast/meteorology/cities/daily/{globalIdLocal}.json".format(globalIdLocal=self.globalIdLocal))

        _forecasts = []
        Forecast = namedtuple('Forecast', data['data'][0].keys())
        for f in data['data']:
            _forecasts.append(Forecast(*f.values()))
        return _forecasts

    async def observation(self):
        for s in STATIONS:
            if self.local in s['name']:
                localID = s['localID']
                break
        
        data = await self.retrieve(url="http://pda.ipma.pt/observacao.jsp", params={"selLocal": localID})
        
        html = BeautifulSoup(data, 'html.parser')
        row = html.find_all('tr')

        Observation = namedtuple('Observation', ['temperature', 'humidity', 'windspeed', 'winddirection', 'precipitation', 'pressure'])
        units = [td.get_text() for td in row[1].find_all('td')]
        values = [td.get_text() for td in row[3].find_all('td')][1:]
        _observation = Observation(*zip(values, units))
        return _observation

async def main():
    async with aiohttp.ClientSession() as session:
        station = await Station.get(session, 40.6147336,-8.6424433)
        print("Nearest station if {}".format(station.local))
        print(await station.forecast())
        print(await station.observation())

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
