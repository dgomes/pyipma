"""API to IPMA."""
import logging
from collections import namedtuple
import aiohttp
import json
import ast

from .consts import \
    WIND_DIRECTION_ID, WIND_DIRECTION,\
    API_OBSERVATION_STATIONS, API_OBSERVATION_OBSERVATIONS
from .entities import Entities, ENTITY2APIURL

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class IPMA_API:
    """Interfaces to http://api.ipma.pt"""

    def __init__(self, websession):
        self.websession = websession
        self.weather_type = None
        self.wind_type = None

    async def retrieve(self, url, **kwargs):
        """Issue API requests."""
        try:
            async with self.websession.request('GET', url, headers={'Referer': 'http://www.ipma.pt'}, **kwargs) as res:
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
        num = ast.literal_eval(string)
        if isinstance(num, int) or isinstance(num, float):
            return num
        return string
    
    async def make(self, entity_name):
        """Load entity from url."""
        return Entities(entity_name, await self.retrieve(ENTITY2APIURL[entity_name]['url']), ENTITY2APIURL[entity_name]['key'])


    async def forecast(self, globalIdLocal):
        """Retrieve next 5 days forecast."""

        data = await self.retrieve(API_FORECAST + "{globalIdLocal}.json".
                                   format(globalIdLocal=globalIdLocal))

        if not self.weather_type:
            await self.weather_type_classe()

        if not self.wind_type:
            await self.wind_type_classe()

        _forecasts = []
        for forecast in data['data']:
            Forecast = namedtuple('Forecast', list(forecast.keys())+['description'])
            _description = self.weather_type[forecast['idWeatherType']]
            if forecast['classWindSpeed'] != -99.0:
                _description += ", com vento "+ self.wind_type[forecast['classWindSpeed']] +\
                                " de " + WIND_DIRECTION[forecast['predWindDir']]
            vals = [self._to_number(v) for v in forecast.values()] + [_description]
            _forecasts.append(Forecast(*vals))
        return _forecasts

    async def weather_type_classe(self):
        """Retrieve translation for weather type."""

        data = await self.retrieve(url=API_WEATHER_TYPE)

        self.weather_type = dict()

        for _type in data['data']:
            self.weather_type[_type['idWeatherType']] = _type['descIdWeatherTypePT']

        return self.weather_type

    async def wind_type_classe(self):
        """Retrieve translation for wind type."""

        data = await self.retrieve(url=API_WIND_SPEED_DAILY)

        self.wind_type = dict()

        for _type in data['data']:
            self.wind_type[int(_type['classWindSpeed'])] = _type['descClassWindSpeedDailyPT']

        return self.wind_type

    async def observations(self):
        """Retrieve current weather observation."""
        observations = []

        raw_stations = await self.retrieve(url=API_OBSERVATION_STATIONS,
                                           headers={'Referer': 'http://www.ipma.pt'})
        if not raw_stations:
            return observations 

        raw_observations = await self.retrieve(url=API_OBSERVATION_OBSERVATIONS,
                                               headers={'Referer': 'http://www.ipma.pt'})
        if not raw_observations:
            return observations 

        Station = namedtuple('ObservationStation', ['latitude', 'longitude', 'stationID',
                                                    'stationName', 'currentObs'])

        Observation = namedtuple('Observation', ['temperature', 'humidity',
                                                 'windspeed', 'winddirection',
                                                 'precipitation', 'pressure',
                                                 'description'])

        last_observation = sorted(raw_observations.keys())[-1]

        for station in raw_stations:
            _station = raw_observations[last_observation][str(station.get('properties').get('idEstacao'))]

            if _station is None:
                continue

            _observation = Observation(
                _station['temperatura'],
                _station['humidade'],
                _station['intensidadeVentoKM'] if _station['intensidadeVentoKM'] != -99.0 else None,
                WIND_DIRECTION[WIND_DIRECTION_ID[_station['idDireccVento']]],
                _station['precAcumulada'] if _station['precAcumulada'] != -99.0 else None,
                _station['pressao'] if _station['pressao'] != -99.0 else None,
                "{} @ {}".format(station.get('properties').get('localEstacao'), last_observation),
                )

            _station = Station(
                station.get('geometry').get('coordinates')[1],
                station.get('geometry').get('coordinates')[0],
                station.get('properties').get('idEstacao'),
                station.get('properties').get('localEstacao'),
                _observation)

            observations.append(_station)
        return observations
