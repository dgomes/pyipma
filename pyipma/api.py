"""API to IPMA."""
import logging
from collections import namedtuple
import aiohttp

from .consts import API_DISTRITS, API_FORECAST, API_WEATHER_TYPE,\
    API_WIND_TYPE, WIND_DIRECTION_ID, WIND_DIRECTION,\
    API_OBSERVATION_STATIONS, API_OBSERVATION_OBSERVATIONS

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
            if float(string) - int(string) == 0:
                return int(string)
            return float(string)
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

        data = await self.retrieve(url=API_WIND_TYPE)

        self.wind_type = dict()

        for _type in data['data']:
            self.wind_type[int(_type['classWindSpeed'])] = _type['descClassWindSpeedDailyPT']

        return self.wind_type

    async def observations(self):
        """Retrieve current weather observation."""

        raw_stations = await self.retrieve(url=API_OBSERVATION_STATIONS,
                                           headers={'Referer': 'http://www.ipma.pt'})

        raw_observations = await self.retrieve(url=API_OBSERVATION_OBSERVATIONS,
                                               headers={'Referer': 'http://www.ipma.pt'})

        Station = namedtuple('ObservationStation', ['latitude', 'longitude', 'stationID',
                                                    'stationName', 'currentObs'])

        Observation = namedtuple('Observation', ['temperature', 'humidity',
                                                 'windspeed', 'winddirection',
                                                 'precipitation', 'pressure',
                                                 'description'])
        observations = []
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
