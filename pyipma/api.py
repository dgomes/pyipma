"""API to IPMA."""
import logging
from collections import namedtuple
import aiohttp

from .consts import API_DISTRITS, API_FORECAST, API_XML_OBSERVATION

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class IPMA_API:
    """Interfaces to http://api.ipma.pt"""

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

    async def stations(self):
        """Retrieve stations."""

        data = await self.retrieve(API_DISTRITS)

        Station = namedtuple('Station', ['latitude', 'longitude',
                                         'idAreaAviso', 'idConselho',
                                         'idDistrito', 'idRegiao',
                                         'globalIdLocal', 'local'])

        _stations = []

        for station in data['data']:
        
            _station = Station(
                self._to_number(station['latitude']),
                self._to_number(station['longitude']),
                station['idAreaAviso'],
                station['idConcelho'],
                station['idDistrito'],
                station['idRegiao'],
                station['globalIdLocal']//100 * 100,
                station['local'],
                )

            _stations.append(_station)

        return _stations 

    async def forecast(self, globalIdLocal):
        """Retrieve next 5 days forecast."""

        data = await self.retrieve(API_FORECAST + "{globalIdLocal}.json".
                                   format(globalIdLocal=globalIdLocal))

        _forecasts = []
        for forecast in data['data']:
            Forecast = namedtuple('Forecast', forecast.keys())
            vals = [self._to_number(v) for v in forecast.values()]
            _forecasts.append(Forecast(*vals))
        return _forecasts

    async def observations(self):
        """Retrieve current weather observation."""

        data = await self.retrieve(url=API_XML_OBSERVATION,
                                   headers={'Referer': 'http://www.ipma.pt'})

        import xml.etree.ElementTree as ET
        tree = ET.fromstring(data)

        Station = namedtuple('ObservationStation', ['latitude', 'longitude', 'stationID',
                                         'stationName', 'currentObs'])

        Observation = namedtuple('Observation', ['temperature', 'humidity',
                                                 'windspeed', 'winddirection',
                                                 'precipitation', 'pressure'])
        _observations = [] 

        for station in tree.iter('station'):
            obs = station.find('currentObs')
            _observation = Observation(
                self._to_number(obs.find('temp').text),
                self._to_number(obs.find('humidity').text),
                obs.find('wind').find('windDirectionResume').text,
                self._to_number(obs.find('wind').find('windSpeed').text),
                self._to_number(obs.find('prec').text),
                self._to_number(obs.find('pres').text),
                )
            
            _station = Station(
                station.get('lat'),
                station.get('lon'),
                station.get('stationID'),
                station.get('stationName'),
                _observation)

            _observations.append(_station)

        return _observations
