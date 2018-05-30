"""Representation of a Weather Station from IPMA."""
import logging
from collections import namedtuple
import aiohttp

from geopy import distance
from .api import IPMA_API

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Station:
    """Represents a Meteo Station (district)."""

    def __init__(self, websession):
        self.api = IPMA_API(websession)

    def _filter_closest(self, lat, lon, stations):
        """Helper to filter the closest station to a given location."""
        current_location = (lat, lon)
        closest = None
        closest_distance = None

        for station in stations:
            station_loc = (station.latitude, station.longitude)
            station_distance = distance.distance(current_location,
                                                 station_loc).km
            if not closest or station_distance < closest_distance:
                closest = station
                closest_distance = station_distance

        return closest 

    @classmethod
    async def get(cls, websession, lat, lon):
        """Retrieve the nearest station."""

        self = Station(websession)
        
        stations = await self.api.stations()

        self.station = self._filter_closest(lat, lon, stations)

        logger.info("Using %s as weather station", self.station.local)

        return self

    @property
    def local(self):
        """Location of the weather station."""
        return self.station.local

    async def forecast(self):
        """Retrieve next 5 days forecast."""

        _forecasts = await self.api.forecast(self.station.globalIdLocal)

        return _forecasts

    async def observation(self):
        """Retrieve current weather observation."""

        observations = await self.api.observations()

        closest = self._filter_closest(self.station.latitude,
                                       self.station.longitude,
                                       observations)

        return closest.currentObs 
