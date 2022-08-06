"""Representation of a Weather Station from IPMA."""
import logging

from .auxiliar import (
    Forecast_Location,
    Forecast_Locations,
    Sea_Location,
    Sea_Locations,
    Station,
    Stations,
)
from .forecast import Forecast_days
from .observation import Observations
from .sea_forecast import SeaForecasts

LOGGER = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Location:
    """Represents a Location (district)."""

    def __init__(
        self,
        forecast_locations: list[Forecast_Location],
        observation_stations: list[Station],
        sea_stations: list[Sea_Location],
    ):
        self.forecast_locations = forecast_locations
        self.observation_stations = observation_stations
        self.sea_stations = sea_stations

    @classmethod
    async def get(cls, api, lon, lat, sea_stations=False):
        """Retrieve the nearest location and associated station."""

        forecast_locations = Forecast_Locations(api)
        near_locations = await forecast_locations.get(lon, lat)

        stations = Stations(api)
        near_stations = await stations.get(lon, lat)

        near_sea_locations = None
        if sea_stations:
            sea_locations = Sea_Locations(api)
            near_sea_locations = await sea_locations.get(lon, lat)

        LOGGER.info(
            "Using %s as weather station for %s",
            near_stations[0].localEstacao,
            near_locations[0].local,
        )

        return Location(near_locations, near_stations, near_sea_locations)

    @property
    def name(self):
        """Location name."""
        return self.forecast_locations[0].local

    @property
    def global_id_local(self):
        """Global identifier of the location as defined by IPMA."""
        return self.forecast_locations[0].globalIdLocal

    @property
    def station(self):
        """Name of the weather station."""
        return self.observation_stations[0].localEstacao

    @property
    def id_station(self):
        """Global identifier of the location as defined by IPMA."""
        return self.observation_stations[0].idEstacao

    @property
    def station_latitude(self):
        """Weather station latitude."""
        return self.observation_stations[0].coordinates[1]

    @property
    def station_longitude(self):
        """Weather station longitude."""
        return self.observation_stations[0].coordinates[0]

    @property
    def sea_station_name(self):
        """Sea station name."""
        if self.sea_stations is not None:
            return self.sea_stations[0].local
        return None

    @property
    def sea_station_global_id_local(self):
        """Global identifier of the location as defined by IPMA."""
        if self.sea_stations is not None:
            return self.sea_stations[0].globalIdLocal
        return None

    async def forecast(self, api, period=24):
        """Retrieve forecasts of location."""
        forecast_days = Forecast_days(api)
        forecasts = []

        for forecast_location in self.forecast_locations[:10]:
            try:
                forecasts = await forecast_days.get(
                    forecast_location.globalIdLocal, period
                )
                break
            except Exception as err:
                LOGGER.warning(
                    "Could not retrieve forecast for %s: %s", forecast_location, err
                )

        return forecasts

    async def observation(self, api):
        """Retrieve observation of Estacao."""
        obs = Observations(api)
        observations = []
        for station in self.observation_stations[:10]:
            try:
                observations = await obs.get(station.idEstacao)
                break
            except Exception as err:
                LOGGER.warning(
                    "Could not retrieve obsertation for %s: %s", station, err
                )

        return observations[0] if len(observations) else None

    async def sea_forecast(self, api):
        """Retrieve today's sea forecast for closest sea location"""
        forecast_3days = SeaForecasts(api)
        forecasts = []

        for sea_location in self.sea_stations[:10]:
            try:
                forecasts = await forecast_3days.get(sea_location.globalIdLocal)
                break
            except Exception as err:
                LOGGER.warning(
                    "Could not retrieve forecast for %s: %s", sea_location, err
                )

        return forecasts
