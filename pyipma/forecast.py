"""Representation of a Weather Forecast from IPMA."""
import logging
from enum import Enum

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class TipoTemperatura(Enum):
    """Enumeration of types of Temperature."""
    MIN = "tMin"
    MED = "tMed"
    MAX = "tMax"

class Forecast:
    """Represents a Meteo Forecast."""
    def __init__(self, globalIdLocal, time, data):
        self._data = data
        self._time = time
        self._global_id_local = globalIdLocal

    def _temperature(self, tipo=TipoTemperatura.MED):
        """Temperature in Celcius."""
        try:
            return float(self._data[tipo.value])
        except KeyError:
            # Create an average with MIN and MAX
            return round((
                float(self._data[TipoTemperatura.MAX.value])
                - float(self._data[TipoTemperatura.MIN.value])
                )/2 + float(self._data[TipoTemperatura.MIN.value]), 1)

    @property
    def update_date(self):
        """Date when the forecast data was updated."""
        return self._data['dataUpdate']

    @property
    def forecast_date(self):
        """Date for when this forecast is."""
        return self._data['dataPrev']

    @property
    def forecasted_hours(self):
        """Number of hours for the forecast."""
        return self._data['idPeriodo']

    @property
    def temperature(self):
        """Average Temperature."""
        return self._temperature()

    @property
    def max_temperature(self):
        """Maximum Temperature."""
        return self._temperature(TipoTemperatura.MAX)

    @property
    def min_temperature(self):
        """Minimum Temperature."""
        return self._temperature(TipoTemperatura.MIN)

    @property
    def feels_like_temperature(self):
        """'Feels Like' Temperature."""
        return self._data["utci"]

    @property
    def humidity(self):
        """Relative Humidity in %."""
        return self._data.get('hR')

    @property
    def precipitation_probability(self):
        """Probability of raining more then 0.3mm."""
        return self._data['probabilidadePrecipita']

    @property
    def wind_strength(self):
        """Wind Strength."""
        return self._data.get('ffVento')

    @property
    def wind_direction(self):
        """Wind direction."""
        return self._data['ddVento']

    @property
    def weather_type(self):
        """Weather type."""
        return self._data['idTipoTempo']

    def __repr__(self):
        return f"Forecast for {self._global_id_local} at {self._time}: \
            {self.temperature}°C, {self.humidity}%"
