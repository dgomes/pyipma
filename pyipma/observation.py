"""Representation of a Weather Observation from IPMA."""
import datetime
import logging
from dataclasses import dataclass

from typing import Optional

from .api import IPMA_API

LOGGER = logging.getLogger(__name__)

WIND_DIRECTION_ID = {
    0: "",
    1: "N",
    2: "NE",
    3: "E",
    4: "SE",
    5: "S",
    6: "SW",
    7: "W",
    8: "NW",
    9: "N",
}


@dataclass
class Observation:
    """Represents a Meteo Station (district)."""

    intensidadeVentoKM: Optional[float]
    temperatura: Optional[float]
    radiacao: Optional[float]
    idDireccVento: int
    precAcumulada: Optional[float]
    intensidadeVento: Optional[float]
    humidade: Optional[float]
    pressao: Optional[float]
    timestamp: datetime.datetime
    idEstacao: int

    @property
    def temperature(self):
        """Temperatura do ar registada a 1.5 metros de altura, média da hora (ºC)."""
        return self.temperatura

    @property
    def radiation(self):
        """Radiação solar (kJ/m2)."""
        return self.radiacao

    @property
    def wind_intensity_km(self):
        """Intensidade do vento registada a 10 metros de altura (km/h)."""
        return self.intensidadeVentoKM

    @property
    def wind_intensity(self):
        """Intensidade do vento registada a 10 metros de altura (m/s)."""
        return self.intensidadeVento

    @property
    def wind_direction(self):
        """Rumo predominante do vento registado a 10 metros de altura."""
        return WIND_DIRECTION_ID[self.idDireccVento]

    @property
    def accumulated_precipitation(self):
        """Precipitação registada a 1.5 metros de altura, valor acumulado da hora (mm)."""
        return self.precAcumulada

    @property
    def humidity(self):
        """Humidade relativa do ar registada a 1.5 metros de altura, média da hora (%)."""
        return self.humidade

    @property
    def pressure(self):
        """Pressão atmosférica, reduzida ao nível médio do mar (NMM), média da hora (hPa)."""
        return self.pressao

    def __str__(self):
        """Representation of a weather Observation in EN."""
        return f"Weather in {self.idEstacao} at {self.timestamp}: {self.temperature}°C, {self.humidity}%"


class Observations:
    """Represents a Meteo Station endpoint that retrieves Observation objects."""

    def __init__(
        self,
        api: IPMA_API,
    ):
        self.data = None
        self.api = api

    async def get(self, idEstacao):
        """Retrieve observations from IPMA."""
        raw = await self.api.retrieve(
            url="https://api.ipma.pt/open-data/observation/meteorology/stations/observations.json"
        )
        idEstacao = str(idEstacao)

        self.data = sorted(
            [
                Observation(
                    r["intensidadeVentoKM"] if r["intensidadeVentoKM"] != -99 else None,
                    r["temperatura"] if r["temperatura"] != -99 else None,
                    r["radiacao"] if r["radiacao"] != -99 else None,
                    r["idDireccVento"],
                    r["precAcumulada"] if r["precAcumulada"] != -99 else None,
                    r["intensidadeVento"] if r["intensidadeVento"] != 99 else None,
                    r["humidade"] if r["humidade"] != -99 else None,
                    r["pressao"] if r["pressao"] != -99 else None,
                    datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M"),
                    int(estacao),
                )
                for timestamp in raw
                for estacao, r in raw[timestamp].items()
                if r is not None and estacao == idEstacao
            ],
            key=lambda d: d.timestamp,
        )

        return self.data
