"""Representation of a Weather Forecast from IPMA."""
import datetime
import logging
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from .api import IPMA_API
from .auxiliar import Forecast_Location, Forecast_Locations, Weather_Type, Weather_Types

LOGGER = logging.getLogger(__name__)


class TipoTemperatura(Enum):
    """Enumeration of types of Temperature."""

    MIN = "tMin"
    MED = "tMed"
    MAX = "tMax"


@dataclass
class Forecast:
    """Represents a Weather Forecast."""

    tMed: float | None
    tMin: float | None
    ffVento: float | None
    idFfxVento: int
    dataUpdate: datetime.datetime
    tMax: float | None
    iUv: float | None
    intervaloHora: str
    idTipoTempo: Weather_Type
    hR: float | None
    location: Forecast_Location
    probabilidadePrecipita: float | None
    idPeriodo: int
    dataPrev: datetime.datetime
    ddVento: str
    utci: float | None = None

    @property
    def update_date(self):
        """Date when the forecast data was updated."""
        return self.dataUpdate

    @property
    def forecast_date(self):
        """Date for when this forecast is."""
        return self.dataPrev

    @property
    def forecasted_hours(self):
        """Number of hours for the forecast."""
        return self.idPeriodo

    @property
    def temperature(self):
        """Average Temperature."""
        if self.tMed:
            return self.tMed
        # Create an average with MIN and MAX
        LOGGER.debug("Temperature not available, averaging Max and Min")
        return round(
            (self.tMax - self.tMin) / 2 + self.tMin,
            1,
        )

    @property
    def max_temperature(self):
        """Maximum Temperature."""
        return self.tMax if self.tMax else self.tMed

    @property
    def min_temperature(self):
        """Minimum Temperature."""
        return self.tMin

    @property
    def feels_like_temperature(self):
        """'Feels Like' Temperature."""
        return self.utci

    @property
    def humidity(self):
        """Relative Humidity in %."""
        return self.hR

    @property
    def precipitation_probability(self):
        """Probability of raining more then 0.3mm."""
        return self.probabilidadePrecipita

    @property
    def wind_direction(self):
        """Wind direction."""
        return self.ddVento

    @property
    def wind_strength(self):
        """Wind strenght."""
        return self.ffVento

    @property
    def weather_type(self):
        """Weather type."""
        return self.idTipoTempo

    @property
    def weather_type_description(self):
        """Weather type description"""
        return self.idTipoTempo.en

    @property
    def weather_type_description_pt(self):
        """Weather type description in portuguese"""
        return self.idTipoTempo.pt

    def __str__(self):
        if self.humidity is None:
            return f"Forecast for {self.location} at {self.dataPrev}: \
                {self.temperature}°C, {self.weather_type_description}"
        return f"Forecast for {self.location} at {self.dataPrev}: \
            {self.temperature}°C, {self.humidity}%, {self.weather_type_description}"


class Forecast_days:
    """Represents Forecast endpoint that retrieves 10 days objects."""

    def __init__(self, api: IPMA_API):
        """Initialize Forecast_days."""
        self.data = None
        self.api = api

        self.weather_type = Weather_Types(api)
        self.forecast_locations = Forecast_Locations(api)

    async def get(self, globalIdLocal, period: int = 24):
        """Retrieve forecasts from IPMA.
        periodo: 1: 3days, 3: 5days, 24: 10days
        """
        assert period in [1, 3, 24], "Forecast period must be 1h, 3h or 24h"
        raw = await self.api.retrieve(
            url=f"http://api.ipma.pt/public-data/forecast/aggregate/{globalIdLocal}.json"
        )
        self.data = sorted(
            [
                Forecast(
                    tMed=float(r["tMed"]) if r.get("tMed") else None,
                    tMin=float(r["tMin"]) if r.get("tMin") else None,
                    ffVento=float(r["ffVento"]) if r.get("ffVento") else None,
                    idFfxVento=r.get("idFfxVento"),
                    dataUpdate=datetime.datetime.strptime(
                        r["dataUpdate"], "%Y-%m-%dT%H:%M:%S"
                    ),
                    tMax=float(r["tMax"]) if r.get("tMax") else None,
                    iUv=r.get("iUv"),
                    intervaloHora=r.get("intervaloHora"),
                    idTipoTempo=await self.weather_type.get(int(r["idTipoTempo"])),
                    hR=r.get("hR"),
                    location=await self.forecast_locations.find(
                        int(r["globalIdLocal"])
                    ),
                    probabilidadePrecipita=float(r["probabilidadePrecipita"])
                    if r["probabilidadePrecipita"] != -99
                    else None,
                    idPeriodo=r["idPeriodo"],
                    dataPrev=datetime.datetime.strptime(
                        r["dataPrev"], "%Y-%m-%dT%H:%M:%S"
                    ).replace(tzinfo=datetime.timezone.utc),
                    ddVento=r["ddVento"],
                    utci=r.get("utci"),
                )
                for r in raw
                if r["idPeriodo"] == period
                and datetime.datetime.strptime(r["dataPrev"], "%Y-%m-%dT%H:%M:%S")
                > (datetime.datetime.now() - timedelta(hours=1))
            ],
            key=lambda d: d.dataPrev,
        )

        return self.data
