"""Representation of a Weather Station from IPMA."""
import logging
from collections import namedtuple
import aiohttp

from bs4 import BeautifulSoup
from geopy import distance

from .consts import STATIONS, API_DISTRITS, API_FORECAST, API_OBSERVATION

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Station:
    """Represents a Meteo Station (district)."""

    def __init__(self, websession):
        self.websession = websession

    async def retrieve(self, url, **kwargs):
        """Issue API requests."""
        try:
            async with self.websession.request('GET', url) as res:
                if res.status != 200:
                    raise Exception("Could not retrieve information from API")
                if res.content_type == 'application/json':
                    return await res.json()
                return await res.text()
        except aiohttp.ClientError as err:
            logging.error(err)

    @classmethod
    def _to_number(cls, string):
        """Convert string to int or float."""
        try:
            return int(string)
        except ValueError:
            try:
                return float(string)
            except ValueError:
                return string

    @classmethod
    async def get(cls, websession, lat, lon):
        """Retrieve the nearest station."""

        self = Station(websession)

        data = await self.retrieve(API_DISTRITS)

        current_location = (lat, lon)
        closest = None
        closest_distance = None

        for station in data['data']:
            station_loc = (float(station['latitude']),
                           float(station['longitude']))
            station_distance = distance.distance(current_location,
                                                 station_loc).km
            if not closest or station_distance < closest_distance:
                closest = station
                closest_distance = station_distance

        #self.idRegiao = closest['idRegiao']
        #self.idAreaAviso = closest['idAreaAviso']
        #self.idConselho = closest['idConcelho']
        self.globalIdLocal = closest['globalIdLocal']//100 * 100
        #self.idDistrito = closest['idDistrito']
        self.local = closest['local']
        logger.info("Using %s as weather station", self.local)
        self.latitude = closest['latitude']
        self.longitude = closest['longitude']

        return self

    async def forecast(self):
        """Retrieve next 5 days forecast."""

        data = await self.retrieve(API_FORECAST + "{globalIdLocal}.json".
                                   format(globalIdLocal=self.globalIdLocal))

        _forecasts = []
        for forecast in data['data']:
            Forecast = namedtuple('Forecast', forecast.keys())
            vals = [self._to_number(v) for v in forecast.values()]
            _forecasts.append(Forecast(*vals))
        return _forecasts

    async def observation(self):
        """Retrieve current weather observation."""
        from difflib import SequenceMatcher

        prev = 0
        for station in STATIONS:
            similar = SequenceMatcher(None, self.local, station['name']).ratio()
            if similar > prev:
                localID = station['localID']
                prev = similar

        data = await self.retrieve(url=API_OBSERVATION,
                                   params={"selLocal": localID})

        html = BeautifulSoup(data, 'html.parser')
        row = html.find_all('tr')

        Observation = namedtuple('Observation', ['temperature', 'humidity',
                                                 'windspeed', 'winddirection',
                                                 'precipitation', 'pressure'])
        units = [td.get_text() for td in row[1].find_all('td')]
        values = [self._to_number(td.get_text())
                  for td in row[3].find_all('td')][1:]
        _observation = Observation(*zip(values, units))

        return _observation
