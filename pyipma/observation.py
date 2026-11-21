"""Representation of a Weather Observation from IPMA."""
import datetime
from dataclasses import dataclass

from .api import IPMA_API
from ._parsing import number

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
    """Hourly weather measurements from an IPMA station."""

    intensidadeVentoKM: float | None
    temperatura: float | None
    radiacao: float | None
    idDireccVento: int | None
    precAcumulada: float | None
    intensidadeVento: float | None
    humidade: float | None
    pressao: float | None
    timestamp: datetime.datetime
    idEstacao: int

    @property
    def temperature(self) -> float | None:
        """Temperatura do ar registada a 1.5 metros de altura, média da hora (ºC)."""
        return self.temperatura

    @property
    def radiation(self) -> float | None:
        """Radiação solar (kJ/m2)."""
        return self.radiacao

    @property
    def wind_intensity_km(self) -> float | None:
        """Intensidade do vento registada a 10 metros de altura (km/h)."""
        return self.intensidadeVentoKM

    @property
    def wind_intensity(self) -> float | None:
        """Intensidade do vento registada a 10 metros de altura (m/s)."""
        return self.intensidadeVento

    @property
    def wind_direction(self) -> str:
        """Predominant wind direction, or an empty string when unavailable."""
        if self.idDireccVento is None:
            return ""
        return WIND_DIRECTION_ID.get(self.idDireccVento, "")

    @property
    def accumulated_precipitation(self) -> float | None:
        """Precipitação registada a 1.5 metros de altura, valor acumulado da hora (mm)."""
        return self.precAcumulada

    @property
    def humidity(self) -> float | None:
        """Humidade relativa do ar registada a 1.5 metros de altura, média da hora (%)."""
        return self.humidade

    @property
    def pressure(self) -> float | None:
        """Pressão atmosférica, reduzida ao nível médio do mar (NMM), média da hora (hPa)."""
        return self.pressao

    def __str__(self) -> str:
        """Representation of a weather Observation in EN."""
        return f"Weather in {self.idEstacao} at {self.timestamp}: {self.temperature}°C, {self.humidity}%"


class Observations:
    """Retrieve station observations ordered from oldest to newest."""

    def __init__(
        self,
        api: IPMA_API,
    ) -> None:
        self.data: list[Observation] | None = None
        self.api = api

    async def get(self, idEstacao: int) -> list[Observation]:
        """Retrieve non-null observations for one station; missing stations return []."""
        raw = await self.api.retrieve(
            url="https://api.ipma.pt/open-data/observation/meteorology/stations/observations.json"
        )
        station_id = str(idEstacao)

        self.data = sorted(
            [
                Observation(
                    intensidadeVentoKM=self._number(r.get("intensidadeVentoKM")),
                    temperatura=self._number(r.get("temperatura")),
                    radiacao=self._number(r.get("radiacao")),
                    idDireccVento=int(direction)
                    if (direction := self._number(r.get("idDireccVento"))) is not None
                    else None,
                    precAcumulada=self._number(r.get("precAcumulada")),
                    intensidadeVento=self._number(r.get("intensidadeVento")),
                    humidade=self._number(r.get("humidade")),
                    pressao=self._number(r.get("pressao")),
                    timestamp=datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M"),
                    idEstacao=idEstacao,
                )
                for timestamp, stations in raw.items()
                if (r := stations.get(station_id)) is not None
            ],
            key=lambda d: d.timestamp,
        )

        return self.data

    @staticmethod
    def _number(value: float | str | None) -> float | None:
        """Normalize numeric measurements, preserving zero and treating -99 as missing."""
        return number(value, float)
