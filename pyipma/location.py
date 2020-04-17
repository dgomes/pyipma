"""Representation of a Weather Station from IPMA."""
import logging

from geopy import distance
from .observation import Observation
from .forecast import Forecast
from .sea_forecast import SeaForecast
from .entities import WeatherType
from .consts import (
    API_FORECAST_LOCATIONS,
    API_OBSERVATION_STATIONS,
    API_OBSERVATION_OBSERVATIONS,
    API_FORECAST_TEMPLATE,
    API_SEA_FORECAST,
    API_SEA_LOCATIONS
)

LOGGER = logging.getLogger(__name__)  # pylint: disable=invalid-name
LOGGER.setLevel(logging.DEBUG)


class ObservationStation:
    """Observation Station object as provided by the observation API."""

    def __init__(self, data):
        self._data = data

    @property
    def latitude(self):
        """Latitude."""
        return self._data["geometry"]["coordinates"][1]

    @property
    def longitude(self):
        """Longitude."""
        return self._data["geometry"]["coordinates"][0]

    @property
    def idEstacao(self):  # pylint: disable=invalid-name
        """Identification of Observation Station per IPMA."""
        return self._data["properties"]["idEstacao"]

    @property
    def localEstacao(self):  # pylint: disable=invalid-name
        """Name of Observation Station per IPMA."""
        return self._data["properties"]["localEstacao"]

    def __repr__(self):
        return self.localEstacao


class ForecastLocation:
    """Location object as provided by the forecast API."""

    def __init__(self, data):
        self._data = data

    @property
    def latitude(self):
        """Latitude."""
        return self._data["latitude"]

    @property
    def longitude(self):
        """Longitude."""
        return self._data["longitude"]

    @property
    def local(self):
        """Name of the Forecast location."""
        return self._data["local"]

    @property
    def globalIdLocal(self):  # pylint: disable=invalid-name
        """Identification of the Forecast location per IPMA."""
        return self._data["globalIdLocal"]


class Location:
    """Represents a Location (district)."""

    def __init__(self, distrit, observation_station, sea_station, weather_types):
        self._last_observation = None
        self.distrit = distrit
        self.observation_station = observation_station
        self.sea_station = sea_station
        self.weather_types = weather_types

    @classmethod
    def _filter_closest(cls, lat, lon, locations, order=0):
        """Helper to filter the closest station to a given location."""

        station_distance = [
            (s, distance.distance((lat, lon), (s.latitude, s.longitude)).km)
            for s in locations
        ]
        closest = sorted(station_distance, key=lambda x: x[1])[order][
            0
        ]  # first element of tuple

        return closest

    @classmethod
    async def get(cls, api, lat, lon, sea_stations=False, l_order=0, s_order=0, t_order=0):
        """Retrieve the nearest location and associated station."""

        raw_locations = await api.retrieve(url=API_FORECAST_LOCATIONS)
        locations = [ForecastLocation(r) for r in raw_locations]
        location = cls._filter_closest(lat, lon, locations, l_order)

        raw_observations_stations = await api.retrieve(url=API_OBSERVATION_STATIONS)
        stations = [ObservationStation(s) for s in raw_observations_stations]
        station = cls._filter_closest(lat, lon, stations, s_order)

        weather_type = await WeatherType.get(api)

        if sea_stations:
            raw_sea_stations = await api.retrieve(url=API_SEA_LOCATIONS)
            sea_stations = [ForecastLocation(t) for t in raw_sea_stations]
            sea_station = cls._filter_closest(lat, lon, sea_stations, t_order)

            t_loc = Location(location, station, sea_station, weather_type)

            sea_frcst = await t_loc.sea_forecast(api)

            if not sea_frcst:
                LOGGER.error(
                    "At %s but closest sea station %s seams offline",
                    location.local,
                    sea_station.local,
                )
                return await cls.get(api, lat, lon, sea_station, l_order, s_order, t_order + 1)
        else:
            t_loc = Location(location, station, None, weather_type)

        frcst = await t_loc.forecast(api)
        if not frcst:
            LOGGER.error("Can't get forecast for %s", location.local)
            return await cls.get(api, lat, lon, sea_station, l_order + 1, s_order, t_order)

        obs = await t_loc.observation(api)
        if not obs:
            LOGGER.error(
                "At %s but closest station %s seams offline",
                location.local,
                station.localEstacao,
            )
            return await cls.get(api, lat, lon, sea_station, l_order, s_order + 1, t_order)

        LOGGER.info(
            "Using %s as weather station for %s",
            station.localEstacao,
            location.local
        )

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

    @property
    def sea_station_name(self):
        """Sea station name"""
        if self.sea_station is None:
            return None
        else:
            return self.sea_station.local

    @property
    def sea_station_global_id_local(self):
        """Global identifier of the location as defined by IPMA."""
        if self.sea_station is None:
            return None
        else:
            return self.sea_station.globalIdLocal

    async def forecast(self, api):
        """Retrieve forecasts of location."""

        raw_forecasts = await api.retrieve(
            API_FORECAST_TEMPLATE.format(self.global_id_local)
        )

        forecasts = [
            Forecast(f["globalIdLocal"], f["dataPrev"], f, self.weather_types) for f in raw_forecasts
        ]

        return forecasts

    async def observation(self, api):
        """Retrieve observation of Estacao."""

        raw_observations = await api.retrieve(API_OBSERVATION_OBSERVATIONS)

        observation_dates = iter(sorted(raw_observations.keys(), reverse=True))
        _last_observation = next(observation_dates)

        while (
                not raw_observations[_last_observation][str(self.id_station)]
                or raw_observations[_last_observation][str(self.id_station)]["temperatura"]
                == -99
                or raw_observations[_last_observation][str(self.id_station)]["humidade"]
                == -99
        ):
            try:
                _last_observation = next(observation_dates)
            except StopIteration:
                LOGGER.error("Station has no observations!")
                return None

        return Observation(
            self.station,
            _last_observation,
            raw_observations[_last_observation][
                str(self.observation_station.idEstacao)
            ],
        )

    async def sea_forecast(self, api):
        """Retrieve today's sea forecast for closest sea location"""

        if self.sea_station is None:
            return "Sea stations disabled"

        raw_sea_forecasts = await api.retrieve(API_SEA_FORECAST)

        try:
            _matched_sea_frcst = next(item for item in raw_sea_forecasts['data']
                                      if item["globalIdLocal"] == self.sea_station_global_id_local)
        except StopIteration:
            LOGGER.error("Sea Station has no forecast for today!")
            return None

        return SeaForecast(
            self.sea_station_global_id_local,
            raw_sea_forecasts["forecastDate"],
            _matched_sea_frcst
        )