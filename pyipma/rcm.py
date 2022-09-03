"""Representation of a Fire Risk from IPMA."""
from dataclasses import dataclass

from .api import IPMA_API
from .auxiliar import AuxiliarParser
from .dico_codes import DICO


@dataclass
class RCM:
    """Represents fire risk per region DICO."""

    dico: str
    rcm: int
    coordinates: tuple[float, float]

    def __str__(self):
        RCM_str = {
            1: "Risco reduzido",
            2: "Risco moderado",
            3: "Risco elevado",
            4: "Risco muito elevado",
            5: "Risco máximo",
        }

        return f"{RCM_str[self.rcm]} para {DICO[self.dico][0]}"


class RCM_day(AuxiliarParser):
    """Represents a Risk of Fire endpoint that retrieves RCM objects."""

    def __init__(self, api: IPMA_API, day: int = 0):
        assert day in [0, 1]
        super().__init__(api)
        self.endpoint = (
            f"http://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d{day}.json"
        )

    def _data_to_obj_list(self, raw):
        return [
            RCM(
                d["dico"],
                d["data"]["rcm"],
                (float(d["latitude"]), float(d["longitude"])),
            )
            for dico, d in raw["local"].items()
        ]
