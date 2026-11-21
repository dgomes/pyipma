"""Representation of a Sea Forecast from IPMA."""
import datetime
from dataclasses import dataclass

from .api import IPMA_API
from ._parsing import number, text
from .auxiliar import Sea_Location, Sea_Locations


@dataclass
class SeaForecast:
    """Represents a Sea Forecast."""

    wavePeriodMin: float | None
    location: Sea_Location
    totalSeaMax: float | None
    waveHighMax: float | None
    waveHighMin: float | None
    wavePeriodMax: float | None
    totalSeaMin: float | None
    sstMax: float | None
    predWaveDir: str
    sstMin: float | None
    coordinates: tuple[float, float]
    forecastDate: datetime.datetime
    dataUpdate: datetime.datetime

    @property
    def min_swell_period(self) -> float | None:
        """Minimum daily peak period, associated with swell (seconds)."""
        return self.wavePeriodMin

    @property
    def max_swell_period(self) -> float | None:
        """Maximum daily peak period, associated with swell (seconds)."""
        return self.wavePeriodMax

    @property
    def min_swell_high(self) -> float | None:
        """Minimum daily swell high (meters)."""
        return self.waveHighMin

    @property
    def max_swell_high(self) -> float | None:
        """Maximum daily swell high (meters)."""
        return self.waveHighMax

    @property
    def wave_direction(self) -> str:
        """Predominant wave direction."""
        return self.predWaveDir

    @property
    def max_wave_high(self) -> float | None:
        """Maximum daily wave high (meters)."""
        return self.totalSeaMax

    @property
    def min_wave_high(self) -> float | None:
        """Minimum daily wave high (meters)."""
        return self.totalSeaMin

    @property
    def max_temperature(self) -> float | None:
        """Maximum sea surface temperature (ºC)."""
        return self.sstMax

    @property
    def min_temperature(self) -> float | None:
        """Minimum sea surface temperature (ºC)."""
        return self.sstMin

    def __str__(self) -> str:
        return (
            f"Sea forecast for {self.location} at {self.dataUpdate.strftime('%Y-%m-%d %H:%M')}: \n"
            f"Minimum sea temperature : {self.min_temperature}º \n"
            f"Maximum wave high : {self.max_wave_high}m \n"
            f"Predominant wave direction : {self.wave_direction}"
        )


class SeaForecasts:
    """Retrieve three daily sea forecasts ordered by forecast date."""

    def __init__(
        self,
        api: IPMA_API,
    ) -> None:
        """Initialize the sea forecast parser."""
        self.data: list[SeaForecast] | None = None
        self.api = api
        self.owner: str | None = None
        self.country: str | None = None

        self.sea_locations = Sea_Locations(api)

    async def get(self, globalIdLocal: int) -> list[SeaForecast]:
        forecasts: list[SeaForecast] = []
        for day in range(3):
            raw = await self.api.retrieve(
                url=f"http://api.ipma.pt/open-data/forecast/oceanography/daily/hp-daily-sea-forecast-day{day}.json"
            )
            self.owner = raw.get("owner")
            self.country = raw.get("country")
            forecast_date = datetime.datetime.strptime(raw["forecastDate"], "%Y-%m-%d")
            dataUpdate = datetime.datetime.strptime(
                raw["dataUpdate"], "%Y-%m-%dT%H:%M:%S"
            )
            forecasts += [
                SeaForecast(
                    wavePeriodMin=number(r.get("wavePeriodMin"), float),
                    location=await self.sea_locations.find(int(r["globalIdLocal"])),
                    totalSeaMax=number(r.get("totalSeaMax"), float),
                    waveHighMax=number(r.get("waveHighMax"), float),
                    waveHighMin=number(r.get("waveHighMin"), float),
                    wavePeriodMax=number(r.get("wavePeriodMax"), float),
                    totalSeaMin=number(r.get("totalSeaMin"), float),
                    sstMax=number(r.get("sstMax"), float),
                    predWaveDir=text(r.get("predWaveDir")) or "",
                    sstMin=number(r.get("sstMin"), float),
                    coordinates=(float(r["longitude"]), float(r["latitude"])),
                    forecastDate=forecast_date,
                    dataUpdate=dataUpdate,
                )
                for r in raw["data"]
                if int(r["globalIdLocal"]) == globalIdLocal
            ]

        self.data = sorted(
            forecasts,
            key=lambda d: d.forecastDate,
        )

        return self.data
