"""Representation of a Weather Observation from IPMA."""
import logging
from collections import namedtuple

from .api import IPMA_API
from .consts import API_OBSERVATION_OBSERVATIONS, WIND_DIRECTION_ID

LOGGER = logging.getLogger(__name__)


class Observation:
    """Represents a Meteo Station (district)."""

    def __init__(self, station, last_observation, data):
        self._data = data
        self._station = station
        self._last_observation = last_observation

    @property
    def temperature(self):
        if self._data["temperatura"] == -99:
            LOGGER.warning("No temperature available.")
            return None
        return self._data["temperatura"]

    @property
    def radiation(self):
        return self._data["radiacao"]

    @property
    def wind_intensity_km(self):
        if self._data["intensidadeVentoKM"] == -99:
            LOGGER.warning("No wind intensity available.")
            return None
        return self._data["intensidadeVentoKM"]

    @property
    def wind_intensity(self):
        return self._data["intensidadeVento"]

    @property
    def wind_direction(self):
        return WIND_DIRECTION_ID[self._data["idDireccVento"]]

    @property
    def accumulated_precipitation(self):
        if self._data["precAcumulada"] == -99:
            LOGGER.warning("No Accumulated Precipitation available")
            return None
        return self._data["precAcumulada"]

    @property
    def humidity(self):
        if self._data["humidade"] == -99:
            LOGGER.warning("No Humidity available")
            return None
        return self._data["humidade"]

    @property
    def pressure(self):
        if self._data["pressao"] == -99:
            LOGGER.warning("No Pressure available")
            return None
        return self._data["pressao"]

    def __repr__(self):
        return f"Weather in {self._station} at {self._last_observation}: {self.temperature}°C, {self.humidity}%"
