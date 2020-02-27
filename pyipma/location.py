"""Representation of a Weather Station from IPMA."""
import logging

from geopy import distance
from .observation import Observation
from .forecast import Forecast
from .consts import API_FORECAST_LOCATIONS, API_OBSERVATION_STATIONS,\
    API_OBSERVATION_OBSERVATIONS, API_FORECAST_TEMPLATE

LOGGER = logging.getLogger(__name__) # pylint: disable=invalid-name
LOGGER.setLevel(logging.DEBUG)

class ObservationStation:
    """Observation Station object as provided by the observation API."""
    def __init__(self, data):
        self._data = data

    @property
    def latitude(self):
        """Latitude."""
        return self._data['geometry']['coordinates'][1]

    @property
    def longitude(self):
        """Longitude."""
        return self._data['geometry']['coordinates'][0]

    @property
    def idEstacao(self): # pylint: disable=invalid-name
        """Identification of Observation Station per IPMA."""
        return self._data['properties']['idEstacao']

    @property
    def localEstacao(self): # pylint: disable=invalid-name
        """Name of Observation Station per IPMA."""
        return self._data['properties']['localEstacao']

    def __repr__(self):
        return self.localEstacao

class ForecastLocation:
    """Location object as provided by the forecast API."""
    def __init__(self, data):
        self._data = data

    @property
    def latitude(self):
        """Latitude."""
        return self._data['latitude']

    @property
    def longitude(self):
        """Longitude."""
        return self._data['longitude']

    @property
    def local(self):
        """Name of the Forecast location."""
        return self._data['local']

    @property
    def globalIdLocal(self): # pylint: disable=invalid-name
        """Identification of the Forecast location per IPMA."""
        return self._data['globalIdLocal']

class Location:
    """Represents a Location (district)."""

    def __init__(self, distrit, observation_station):
        self._last_observation = None
        self.distrit = distrit
        self.observation_station = observation_station

    @classmethod
    def _filter_closest(cls, lat, lon, locations, order=0):
        """Helper to filter the closest station to a given location."""

        station_distance = [(s, distance.distance((lat, lon), (s.latitude, s.longitude)).km)
                            for s in locations]
        closest = sorted(station_distance, key=lambda x: x[1])[order][0] #first element of tuple

        return closest

    @classmethod
    async def get(cls, api, lat, lon, l_order=0, s_order=0):
        """Retrieve the nearest location and associated station."""

        raw_locations = await api.retrieve(url=API_FORECAST_LOCATIONS)
        locations = [ForecastLocation(r) for r in raw_locations]
        location = cls._filter_closest(lat, lon, locations, l_order)

        raw_observations_stations = await api.retrieve(url=API_OBSERVATION_STATIONS)
        stations = [ObservationStation(s) for s in raw_observations_stations]
        station = cls._filter_closest(lat, lon, stations, s_order)

        t_loc = Location(location, station)

        frcst = await t_loc.forecast(api)
        if not frcst:
            LOGGER.error("Can't get forecast for %s", location.local)
            return await cls.get( api, lat, lon, l_order+1, s_order)

        obs = await t_loc.observation(api)
        if not obs or obs.temperature == -99 or obs.humidity == -99:
            LOGGER.error("At %s but closest station %s seams offline", location.local, station.localEstacao)
            return await cls.get( api, lat, lon, l_order, s_order+1)

        LOGGER.info("Using %s as weather station for %s", station.localEstacao, location.local)

        return t_loc

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

    @property
    def station_latitude(self):
        """Weather station latitude."""
        return self.observation_station.latitude

    @property
    def station_longitude(self):
        """Weather station longitude."""
        return self.observation_station.longitude

    async def forecast(self, api):
        """Retrieve forecasts of location."""

        raw_forecasts = await api.retrieve(API_FORECAST_TEMPLATE.format(self.global_id_local))

        forecasts = [Forecast(f['globalIdLocal'], f['dataPrev'], f) for f in raw_forecasts]

        return forecasts

    async def observation(self, api):
        """Retrieve observation of Estacao."""

        raw_observations = await api.retrieve(API_OBSERVATION_OBSERVATIONS)
        
        observation_dates = iter(sorted(raw_observations.keys(), reverse=True))
        _last_observation = next(observation_dates)

        while not raw_observations[_last_observation][str(self.id_station)]:
            try:
                _last_observation = next(observation_dates)

            except StopIteration:
                LOGGER.error("Station has no observations!")
                return None

        return Observation(self.station,
                           _last_observation,
                           raw_observations[_last_observation][
                               str(self.observation_station.idEstacao)])
