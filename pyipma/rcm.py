"""Representation of a Fire Risk from IPMA."""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from .api import IPMA_API
from .auxiliar import LocationParser
from .dico_codes import DICO


@dataclass
class RCM:
    """Represents fire risk per region DICO."""

    dico: str
    rcm: int
    coordinates: tuple[float, float]
    dataPrev: date | None = None
    dataRun: date | None = None
    fileDate: datetime | None = None

    @property
    def forecast_date(self) -> date | None:
        """Date for which the fire risk is forecast."""
        return self.dataPrev

    @property
    def run_date(self) -> date | None:
        """Date of the model run."""
        return self.dataRun

    @property
    def update_date(self) -> datetime | None:
        """Date and time when IPMA updated the file."""
        return self.fileDate

    def __str__(self) -> str:
        RCM_str = {
            1: "Risco reduzido",
            2: "Risco moderado",
            3: "Risco elevado",
            4: "Risco muito elevado",
            5: "Risco máximo",
        }

        return f"{RCM_str[self.rcm]} para {DICO[self.dico][0]}"


class RCM_day(LocationParser[RCM]):
    """Represents a Risk of Fire endpoint that retrieves RCM objects."""

    def __init__(self, api: IPMA_API, day: int = 0) -> None:
        assert day in [0, 1]
        super().__init__(api)
        self.endpoint = (
            f"http://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d{day}.json"
        )

    def _data_to_obj_list(self, raw: Any) -> list[RCM]:
        forecast_date = date.fromisoformat(raw["dataPrev"])
        run_date = date.fromisoformat(raw["dataRun"])
        update_date = datetime.fromisoformat(raw["fileDate"])
        return [
            RCM(
                d["dico"],
                d["data"]["rcm"],
                (float(d["latitude"]), float(d["longitude"])),
                dataPrev=forecast_date,
                dataRun=run_date,
                fileDate=update_date,
            )
            for dico, d in raw["local"].items()
        ]
