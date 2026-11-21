"""Representation of a Weather Forecast from IPMA."""
import datetime
import logging
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from typing import Any, Optional, TypeVar

from .api import IPMA_API
from ._parsing import number, text
from .auxiliar import Forecast_Location, Forecast_Locations, Weather_Type, Weather_Types

Number = TypeVar("Number", int, float)

LOGGER = logging.getLogger(__name__)


class TipoTemperatura(Enum):
    """Enumeration of types of Temperature."""

    MIN = "tMin"
    MED = "tMed"
    MAX = "tMax"


@dataclass
class Forecast:
    """Represents a Weather Forecast."""

    tMed: Optional[float]
    tMin: Optional[float]
    ffVento: Optional[float]
    idFfxVento: int | None
    dataUpdate: datetime.datetime
    tMax: Optional[float]
    iUv: Optional[float]
    intervaloHora: str | None
    idTipoTempo: Weather_Type
    hR: Optional[float]
    location: Forecast_Location
    probabilidadePrecipita: Optional[float]
    idPeriodo: int
    dataPrev: datetime.datetime
    ddVento: str
    utci: Optional[float] = None
    idIntensidadePrecipita: Optional[int] = None
    dirOndulacao: Optional[str] = None
    marTotal: Optional[float] = None
    ondulacao: Optional[float] = None
    periodOndulacao: Optional[float] = None
    periodoPico: Optional[float] = None
    tempAguaMar: Optional[float] = None

    @property
    def update_date(self) -> datetime.datetime:
        """Date when the forecast data was updated."""
        return self.dataUpdate

    @property
    def forecast_date(self) -> datetime.datetime:
        """Date for when this forecast is."""
        return self.dataPrev

    @property
    def forecasted_hours(self) -> int:
        """Number of hours for the forecast."""
        return self.idPeriodo

    @property
    def temperature(self) -> float | None:
        """Average Temperature."""
        if self.tMed is not None:
            return self.tMed
        # Create an average with MIN and MAX
        LOGGER.debug("Temperature not available, averaging Max and Min")
        if self.tMax is None or self.tMin is None:
            return None
        return round(
            (self.tMax - self.tMin) / 2 + self.tMin,
            1,
        )

    @property
    def max_temperature(self) -> float | None:
        """Maximum Temperature."""
        return self.tMax if self.tMax is not None else self.tMed

    @property
    def min_temperature(self) -> Optional[float]:
        """Minimum Temperature."""
        return self.tMin

    @property
    def feels_like_temperature(self) -> Optional[float]:
        """'Feels Like' Temperature."""
        return self.utci

    @property
    def humidity(self) -> Optional[float]:
        """Relative Humidity in %."""
        return self.hR

    @property
    def precipitation_probability(self) -> Optional[float]:
        """Probability of raining more then 0.3mm."""
        return self.probabilidadePrecipita

    @property
    def precipitation_intensity(self) -> Optional[int]:
        """Precipitation intensity class code (see Precipitation_Classes)."""
        return self.idIntensidadePrecipita

    @property
    def uv_index(self) -> Optional[float]:
        """Forecast ultraviolet index."""
        return self.iUv

    @property
    def wind_speed_class(self) -> int | None:
        """Wind speed class code (see Wind_Speed_Daily_Types)."""
        return self.idFfxVento

    @property
    def wave_direction(self) -> Optional[str]:
        """Forecast wave direction, when available for coastal locations."""
        return self.dirOndulacao

    @property
    def wave_height(self) -> Optional[float]:
        """Total significant wave height in meters."""
        return self.marTotal

    @property
    def swell_height(self) -> Optional[float]:
        """Swell height in meters."""
        return self.ondulacao

    @property
    def swell_period(self) -> Optional[float]:
        """Swell period in seconds."""
        return self.periodOndulacao

    @property
    def peak_period(self) -> Optional[float]:
        """Peak wave period in seconds."""
        return self.periodoPico

    @property
    def sea_temperature(self) -> Optional[float]:
        """Sea water temperature in degrees Celsius."""
        return self.tempAguaMar

    @property
    def wind_direction(self) -> str:
        """Wind direction."""
        return self.ddVento

    @property
    def wind_strength(self) -> Optional[float]:
        """Wind strenght."""
        return self.ffVento

    @property
    def weather_type(self) -> Weather_Type:
        """Weather type."""
        return self.idTipoTempo

    @property
    def weather_type_description(self) -> str:
        """Weather type description"""
        return self.idTipoTempo.en

    @property
    def weather_type_description_pt(self) -> str:
        """Weather type description in portuguese"""
        return self.idTipoTempo.pt

    def __str__(self) -> str:
        if self.humidity is None:
            return f"Forecast for {self.location} at {self.dataPrev}: \
                {self.temperature}°C, {self.weather_type_description}"
        return f"Forecast for {self.location} at {self.dataPrev}: \
            {self.temperature}°C, {self.humidity}%, {self.weather_type_description}"


class Forecast_days:
    """Represents Forecast endpoint that retrieves 10 days objects."""

    def __init__(self, api: IPMA_API) -> None:
        """Initialize Forecast_days."""
        self.data: list[Forecast] | None = None
        self.api = api

        self.weather_type = Weather_Types(api)
        self.forecast_locations = Forecast_Locations(api)

    async def get(self, globalIdLocal: int, period: int = 24) -> list[Forecast]:
        """Retrieve forecasts from IPMA.
        periodo: 1: 3days, 3: 5days, 24: 10days
        """
        if period not in (1, 3, 24):
            raise ValueError("Forecast period must be 1h, 3h or 24h")
        raw = await self.api.retrieve(
            url=f"http://api.ipma.pt/public-data/forecast/aggregate/{globalIdLocal}.json"
        )
        cutoff = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - (
            timedelta(days=1) if period == 24 else timedelta(hours=1)
        )
        self.data = sorted(
            [
                Forecast(
                    tMed=self._number(r.get("tMed"), float),
                    tMin=self._number(r.get("tMin"), float),
                    ffVento=self._number(r.get("ffVento"), float),
                    idFfxVento=self._number(r.get("idFfxVento"), int),
                    dataUpdate=datetime.datetime.strptime(
                        r["dataUpdate"], "%Y-%m-%dT%H:%M:%S"
                    ),
                    tMax=self._number(r.get("tMax"), float),
                    iUv=self._number(r.get("iUv"), float),
                    intervaloHora=r.get("intervaloHora"),
                    idTipoTempo=await self.weather_type.get(int(r["idTipoTempo"])),
                    hR=self._number(r.get("hR"), float),
                    location=await self.forecast_locations.find(
                        int(r["globalIdLocal"])
                    ),
                    probabilidadePrecipita=self._number(r.get("probabilidadePrecipita"), float),
                    idPeriodo=int(r["idPeriodo"]),
                    dataPrev=datetime.datetime.strptime(
                        r["dataPrev"], "%Y-%m-%dT%H:%M:%S"
                    ).replace(tzinfo=datetime.timezone.utc),
                    ddVento=text(r.get("ddVento")) or "",
                    utci=self._number(r.get("utci"), float),
                    idIntensidadePrecipita=self._number(
                        r.get("idIntensidadePrecipita"), int
                    ),
                    dirOndulacao=text(r.get("dirOndulacao")),
                    marTotal=self._number(r.get("marTotal"), float),
                    ondulacao=self._number(r.get("ondulacao"), float),
                    periodOndulacao=self._number(r.get("periodOndulacao"), float),
                    periodoPico=self._number(r.get("periodoPico"), float),
                    tempAguaMar=self._number(r.get("tempAguaMar"), float),
                )
                for r in raw
                if int(r["idPeriodo"]) == period
                and datetime.datetime.strptime(r["dataPrev"], "%Y-%m-%dT%H:%M:%S") > cutoff
            ],
            key=lambda d: d.dataPrev,
        )

        return self.data

    @staticmethod
    def _number(value: Any, number_type: type[Number]) -> Number | None:
        """Convert API numbers, preserving zero and treating -99 as missing."""
        return number(value, number_type)
