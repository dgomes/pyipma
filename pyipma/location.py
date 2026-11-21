"""Representation of a Weather Station from IPMA."""
from __future__ import annotations
import logging

from .api import IPMA_API
from .auxiliar import (
    District,
    Districts,
    Forecast_Location,
    Forecast_Locations,
    Sea_Location,
    Sea_Locations,
    Station,
    Stations,
)
from .forecast import Forecast, Forecast_days
from .observation import Observation, Observations
from .sea_forecast import SeaForecast, SeaForecasts
from .rcm import RCM, RCM_day
from .uv import UV, UV_risks
from .warnings import Warning, Warnings

LOGGER = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Location:
    """Represents a Location (district)."""

    def __init__(
        self,
        latitude: float,
        longitude: float,
        forecast_locations: list[Forecast_Location],
        observation_stations: list[Station],
        sea_stations: list[Sea_Location] | None,
    ) -> None:
        self.coordinates = (longitude, latitude)
        self.forecast_locations = forecast_locations
        self.observation_stations = observation_stations
        self.sea_stations = sea_stations
        self.districts: list[District] | None = None

    @classmethod
    async def get(
        cls, api: IPMA_API, lon: float, lat: float, sea_stations: bool = False,
    ) -> Location:
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

        return Location(lat, lon, near_locations, near_stations, near_sea_locations)

    @property
    def name(self) -> str:
        """Location name."""
        return self.forecast_locations[0].local

    @property
    def global_id_local(self) -> int:
        """Global identifier of the location as defined by IPMA."""
        return self.forecast_locations[0].globalIdLocal

    @property
    def station(self) -> str:
        """Name of the weather station."""
        return self.observation_stations[0].localEstacao

    @property
    def id_station(self) -> int:
        """Global identifier of the location as defined by IPMA."""
        return self.observation_stations[0].idEstacao

    @property
    def station_latitude(self) -> float:
        """Weather station latitude."""
        return self.observation_stations[0].coordinates[1]

    @property
    def station_longitude(self) -> float:
        """Weather station longitude."""
        return self.observation_stations[0].coordinates[0]

    @property
    def sea_station_name(self) -> str | None:
        """Sea station name."""
        if self.sea_stations is not None:
            return self.sea_stations[0].local
        return None

    @property
    def sea_station_global_id_local(self) -> int | None:
        """Global identifier of the location as defined by IPMA."""
        if self.sea_stations is not None:
            return self.sea_stations[0].globalIdLocal
        return None

    async def get_districts(self, api: IPMA_API) -> list[District]:
        if self.districts is None:
            self.districts = await Districts(api).get(*self.coordinates)

        return self.districts

    async def forecast(self, api: IPMA_API, period: int = 24) -> list[Forecast]:
        """Retrieve forecasts of location."""
        forecast_days = Forecast_days(api)
        forecasts: list[Forecast] = []

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

    async def observation(self, api: IPMA_API) -> Observation | None:
        """Retrieve observation of Estacao."""
        obs = Observations(api)
        for station in self.observation_stations[:10]:
            try:
                LOGGER.debug("Get Observation for %s", station.idEstacao)
                observations = await obs.get(station.idEstacao)
                if len(observations) and observations[-1] is not None:
                    return observations[-1]
            except Exception as err:
                LOGGER.warning(
                    "Could not retrieve obsertation for %s: %s", station, err
                )
        LOGGER.error("Could not retrieve a valid observation for %s", self.name)
        return None

    async def sea_forecast(self, api: IPMA_API) -> list[SeaForecast]:
        """Retrieve today's sea forecast for closest sea location."""
        forecast_3days = SeaForecasts(api)
        forecasts: list[SeaForecast] = []

        for sea_location in (self.sea_stations or [])[:10]:
            try:
                forecasts = await forecast_3days.get(sea_location.globalIdLocal)
                break
            except Exception as err:
                LOGGER.warning(
                    "Could not retrieve forecast for %s: %s", sea_location, err
                )

        return forecasts

    async def fire_risk(self, api: IPMA_API, day: int = 0) -> RCM | None:
        """Retrieve Fire Risk (RCM) for DICO region closest to the current location."""
        rcms = RCM_day(api, day)
        risk = None

        try:
            risks = await rcms.get(*self.coordinates)
            if risks:
                risk = risks[0]
        except Exception as err:
            LOGGER.warning(
                "Could not retrieve RCM for %s: %s",
                "today" if day == 0 else "tomorrow",
                err,
            )

        return risk

    async def uv_risk(self, api: IPMA_API) -> UV | None:
        """Retrieve UV Risk for the current location."""
        uvs = UV_risks(api)
        district_id = None

        try:
            districts = await self.get_districts(api)
            district_id = districts[0].globalIdLocal
            if district_id:
                result = await uvs.get(district_id)
                if result:
                    return result[0]
        except Exception as err:
            LOGGER.warning(
                "Could not retrieve UV for %s: %s",
                district_id,
                err,
            )

        return None

    async def warnings(self, api: IPMA_API) -> list[Warning] | None:
        """Retrieve Warnings for the current location."""

        warnings = Warnings(api)
        area_id: str | None = None

        try:
            districts = await self.get_districts(api)
            area_id = districts[0].idAreaAviso

            if area_id:
                return await warnings.get(area_id)

        except Exception as err:
            LOGGER.warning(
                "Could not retrieve Warnings for %s: %s",
                area_id,
                err,
            )

        return None
