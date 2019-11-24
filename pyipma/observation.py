"""Representation of a Weather Observation from IPMA."""
import logging
from collections import namedtuple

from .api import IPMA_API
from .consts import API_OBSERVATION_OBSERVATIONS, WIND_DIRECTION_ID

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Observation:
    """Represents a Meteo Station (district)."""
    def __init__(self, estacao, last_observation, data):
        self._data = data
        self._estacao = estacao
        self._last_observation = last_observation

    @property
    def intensidade_vento_km(self):
        return self._data['intensidadeVentoKM']

    @property
    def temperatura(self):
        return self._data['temperatura']

    @property
    def radiacao(self):
        return self._data['radiacao']

    @property
    def direccao_vento(self):
        return WIND_DIRECTION_ID[self._data['idDireccVento']]
    
    @property
    def precipitacao_acumulada(self):
        return self._data['precAcumulada']

    @property
    def intensidade_vento(self):
        return self._data['intensidadeVento']
    
    @property
    def humidade(self):
        return self._data['humidade']

    @property
    def pressao(self):
        return self._data['pressao']

    def __repr__(self):
        return f"Weather in {self._estacao} at {self._last_observation}: {self.temperatura}°C, {self.humidade}%"