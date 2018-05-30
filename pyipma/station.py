"""Representation of a Weather Station from IPMA."""
import logging
from collections import namedtuple
import aiohttp

from geopy import distance

from .consts import API_DISTRITS, API_FORECAST, API_XML_OBSERVATION

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Station:
    """Represents a Meteo Station (district)."""

    def __init__(self, websession):
        self.websession = websession

    async def retrieve(self, url, **kwargs):
        """Issue API requests."""
        try:
            async with self.websession.request('GET', url, **kwargs) as res:
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

        self.idAreaAviso = closest['idAreaAviso']
        self.idConselho = closest['idConcelho']
        self.idDistrito = closest['idDistrito']
        self.idRegiao = closest['idRegiao']
        self.globalIdLocal = closest['globalIdLocal']//100 * 100
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

        data = await self.retrieve(url=API_XML_OBSERVATION,
                                   headers={'Referer': 'http://www.ipma.pt'})

        import xml.etree.ElementTree as ET
        tree = ET.fromstring(data)
        current_location = (self.latitude, self.longitude)
        closest = None
        closest_distance = None

        for station in tree.iter('station'):
            station_loc = (float(station.get('lat')),
                           float(station.get('lon')))
            station_distance = distance.distance(current_location,
                                                 station_loc).km
            if not closest or station_distance < closest_distance:
                closest = station
                closest_distance = station_distance

        Observation = namedtuple('Observation', ['temperature', 'humidity',
                                                 'windspeed', 'winddirection',
                                                 'precipitation', 'pressure'])

        obs = closest.find('currentObs')
        _observation = Observation(
            self._to_number(obs.find('temp').text),
            self._to_number(obs.find('humidity').text),
            obs.find('wind').find('windDirectionResume').text,
            self._to_number(obs.find('wind').find('windSpeed').text),
            self._to_number(obs.find('prec').text),
            self._to_number(obs.find('pres').text),
            )
        return _observation
