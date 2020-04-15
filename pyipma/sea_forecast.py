"""Representation of a Sea Forecast from IPMA."""

import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class SeaForecast:
    """Represents a Sea Forecast"""

    def __init__(self, globalIdLocal, time, data):
        self._data = data
        self._time = time
        self._global_id_local = globalIdLocal

    @property
    def min_swell_period(self):
        """Minimum daily peak period, associated with swell (seconds)"""
        return self._data['wavePeriodMin']

    @property
    def max_swell_period(self):
        """Maximum daily peak period, associated with swell (seconds)"""
        return self._data['wavePeriodMax']

    @property
    def min_swell_high(self):
        """Minimum daily swell high (meters)"""
        return self._data['waveHighMin']

    @property
    def max_swell_high(self):
        """Maximum daily swell high (meters)"""
        return self._data['waveHighMax']

    @property
    def wave_direction(self):
        """Predominant wave direction"""
        return self._data['predWaveDir']

    @property
    def max_wave_high(self):
        """Maximum daily wave high (meters)"""
        return self._data['totalSeaMax']

    @property
    def min_wave_high(self):
        """Minimum daily wave high (meters)"""
        return self._data['totalSeaMin']

    @property
    def max_temperature(self):
        """Maximum sea surface temperature (ºC)"""
        return self._data['sstMin']

    @property
    def min_temperature(self):
        """Minimum sea surface temperature (ºC)"""
        return self._data['sstMin']

    def __repr__(self):
        return f"Sea forecast for {self._global_id_local} at {self._time}: \n" \
               f"Minimum sea temperature : {self.min_temperature}º \n" \
               f"Maximum wave high : {self.max_wave_high}m \n" \
               f"Predominant wave direction : {self.wave_direction}"
