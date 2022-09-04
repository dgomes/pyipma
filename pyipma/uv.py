"""Representation of UV risk from IPMA."""
from dataclasses import dataclass
import datetime
from .api import IPMA_API


@dataclass
class UV:
    """Represents UV risk per region DICO."""

    idPeriodo: int
    intervaloHora: str
    data: datetime.datetime
    globalIdLocal: int
    iUv: float

    def __str__(self):
        def iUv2str(code):
            if code <= 2:
                return "Baixo", "Não é necessário proteção"
            if code <= 5:
                return "Moderado", "Óculos de Sol e protector solar"
            if code <= 7:
                return (
                    "Elevado",
                    "Utilizar óculos de Sol com filtro UV, chapéu, t-shirt e protector solar",
                )
            if code <= 10:
                return (
                    "Muito Elevado",
                    "Utilizar óculos de Sol com filtro UV, chapéu, t-shirt, guarda-sol, protector solar e evitar a exposição das crianças ao Sol",
                )
            return (
                "Extremo",
                "Evitar o mais possível a exposição ao Sol. Aproveite para descansar em casa.",
            )

        level, description = iUv2str(self.iUv)

        return f"{level} - {description}"


class UV_risks:
    """Represents a Risk of UV endpoint that retrieves UV objects."""

    def __init__(self, api: IPMA_API):
        self.api = api
        self.endpoint = f"https://api.ipma.pt/open-data/forecast/meteorology/uv/uv.json"

    async def get(self, globalIdLocal=None):
        """Retrive UV risk for globalIdLocal, or all."""
        raw = await self.api.retrieve(url=self.endpoint)

        data = [
            UV(
                idPeriodo=int(d["idPeriodo"]),
                intervaloHora=d["intervaloHora"],
                data=datetime.datetime.strptime(d["data"], "%Y-%m-%d"),
                globalIdLocal=d["globalIdLocal"],
                iUv=float(d["iUv"]),
            )
            for d in raw
            if globalIdLocal in [None, d["globalIdLocal"]]
        ]

        return sorted(
            data,
            key=lambda d: d.data,
        )
