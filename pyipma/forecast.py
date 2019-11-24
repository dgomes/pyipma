"""Representation of a Weather Forecast from IPMA."""
import logging
from enum import Enum
from collections import namedtuple

from .api import IPMA_API
from .consts import API_FORECAST_TEMPLATE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TipoTemperatura(Enum):
    MIN = "tMin"
    MED = "tMed"
    MAX = "tMax"

class Forecast:
    """Represents a Meteo Forecast."""
    def __init__(self, globalIdLocal, time, data):
        self._data = data
        self._time = time
        self._globalIdLocal = globalIdLocal

    @property
    def temperature(self, tipo=TipoTemperatura.MED):
        try:
            return self._data[tipo.value]
        except KeyError:
            # Create an average with MIN and MAX
            return round((float(self._data[TipoTemperatura.MAX.value]) - float(self._data[TipoTemperatura.MIN.value]))/2 + float(self._data[TipoTemperatura.MIN.value]), 1)
        

    @property
    def humidity(self):
        return self._data.get('hR')
            
    @property
    def rain_probability(self):
        return self._data['probabilidadePrecipita']

    @property
    def wind_strenght(self):
        return self._data['ffVento']

    @property
    def wind_direction(self):
        return self._data['ddVento']

    
    def __repr__(self):
        return f"Forecast for {self._globalIdLocal} at {self._time}: {self.temperatura}°C, {self.humidade}%"