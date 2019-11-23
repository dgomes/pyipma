"""Representation of a Weather Station from IPMA."""
import logging
from collections import namedtuple
import aiohttp

from geopy import distance
from .api import IPMA_API
from .observation import Observation
from .consts import API_DISTRITS, API_OBSERVATION_STATIONS

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

class Station:
    """Represents a Meteo Station (district)."""

    def __init__(self, distrit, observation_station):
        self._last_observation = None
        self.distrit = distrit
        self.observation_station = observation_station

    @classmethod
    def _filter_closest(cls, lat, lon, stations):
        """Helper to filter the closest station to a given location."""
        current_location = (lat, lon)
        closest = None
        closest_distance = None

        #TODO: list compreension of stations, distance sorted by distance
        for station in stations:
            station_loc = (station.latitude, station.longitude)
            station_distance = distance.distance(current_location,
                                                 station_loc).km
            if not closest or station_distance < closest_distance:
                closest = station
                closest_distance = station_distance

        return closest 

    @classmethod
    async def get(cls, api, lat, lon):
        """Retrieve the nearest station."""
        
        distrits = await api.make('Distrit_Island')

        distrit = cls._filter_closest(lat, lon, distrits.values())

        raw_observation_stations = await api.retrieve(url=API_OBSERVATION_STATIONS)

        stations = [Observation_Station(s) for s in raw_observation_stations]

        station = cls._filter_closest(lat, lon, stations)


        logger.info("Using %s as weather station for %s", station.localEstacao, distrit.local)

        return Station(distrit, station)

    @property
    def local(self):
        """Location of the weather station."""
        return self.distrit.local

    @property
    def localEstacao(self):
        """Location of the weather station."""
        return self.observation_station.localEstacao

    @property
    def latitude(self):
        """Latitude of the weather station."""
        return self.observation_station.latitude

    @property
    def longitude(self):
        """Longitude of the weather station."""
        return self.observation_station.longitude

    @property
    def global_station_id(self):
        """Global identifier of the station as defined by IPMA."""
        return self.distrit.globalIdLocal

    async def forecast(self):
        """Retrieve next 5 days forecast."""

        _forecasts = await self.api.forecast(self.distrit.globalIdLocal)

        return _forecasts

    async def observation(self, api):
        """Retrieve current weather observation."""

        observation = await Observation.get(api, self.observation_station.idEstacao)

        return observation
