"""Representation of a Weather Station from IPMA."""
import logging
from collections import namedtuple
import aiohttp

from geopy import distance
from .api import IPMA_API
from .observation import Observation
from .forecast import Forecast
from .consts import API_FORECAST_LOCATIONS, API_OBSERVATION_STATIONS, API_OBSERVATION_OBSERVATIONS, API_FORECAST_TEMPLATE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Observation_Station:
    def __init__(self, data):
        self._data = data
    
    @property
    def latitude(self):
        return self._data['geometry']['coordinates'][1]

    @property
    def longitude(self):
        return self._data['geometry']['coordinates'][0]
    
    @property
    def idEstacao(self):
        return self._data['properties']['idEstacao']
    
    @property
    def localEstacao(self):
        return self._data['properties']['localEstacao']
    
    def __repr__(self):
        return self.localEstacao

class Forecast_Location:
    def __init__(self, data):
        self._data = data

    @property
    def latitude(self):
        return self._data['latitude']

    @property
    def longitude(self):
        return self._data['longitude']

    @property
    def local(self):
        return self._data['local']
    
    @property
    def globalIdLocal(self):
        return self._data['globalIdLocal']

class Location:
    """Represents a Location (district)."""

    def __init__(self, distrit, observation_station):
        self._last_observation = None
        self.distrit = distrit
        self.observation_station = observation_station

    @classmethod
    def _filter_closest(cls, lat, lon, locations):
        """Helper to filter the closest station to a given location."""

        l = [(s, distance.distance((lat, lon), (s.latitude, s.longitude)).km) for s in locations]
        closest = sorted(l, key=lambda x: x[1])[0][0] #first element of tuple that is first in the sorted list 

        return closest 

    @classmethod
    async def get(cls, api, lat, lon):
        """Retrieve the nearest location and associated station."""
        
        raw_locations = await api.retrieve(url=API_FORECAST_LOCATIONS)
        locations = [Forecast_Location(r) for r in raw_locations]
        location = cls._filter_closest(lat, lon, locations)

        raw_observation_stations = await api.retrieve(url=API_OBSERVATION_STATIONS)
        stations = [Observation_Station(s) for s in raw_observation_stations]
        station = cls._filter_closest(lat, lon, stations)

        logger.info("Using %s as weather station for %s", station.localEstacao, location.local)

        return Location(location, station)

    @property
    def name(self):
        """Location name."""
        return self.distrit.local

    @property
    def global_id_local(self):
        """Global identifier of the location as defined by IPMA."""
        return self.distrit.globalIdLocal

    @property
    def station(self):
        """Name of the weather station."""
        return str(self.observation_station)

    @property
    def id_station(self):
        """Global identifier of the location as defined by IPMA."""
        return self.observation_station.idEstacao

    async def forecast(self, api):
        """Retrieve forecasts of location."""
        
        raw_forecasts = await api.retrieve(API_FORECAST_TEMPLATE.format(self.global_id_local))
        
        forecasts = [Forecast(f['globalIdLocal'],  f['dataPrev'], f) for f in raw_forecasts]

        return forecasts

    async def observation(self, api):
        """Retrieve observation of Estacao."""
        
        raw_observations = await api.retrieve(API_OBSERVATION_OBSERVATIONS)
        
        observation_dates = iter(sorted(raw_observations.keys(), reverse=True))
        _last_observation = next(observation_dates)

        while not raw_observations[_last_observation][str(self.observation_station.idEstacao)]:
            _last_observation = next(observation_dates[last])

        return Observation(self.station, _last_observation, raw_observations[_last_observation][str(self.observation_station.idEstacao)])

