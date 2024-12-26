"""Representation of Warnings from IPMA."""
from dataclasses import dataclass
from datetime import datetime

from . import IPMAException
from .api import IPMA_API
from .auxiliar import AuxiliarParser


@dataclass
class Warning:
    """Represents a Warning for a given Area."""

    text: str
    awarenessTypeName: str
    idAreaAviso: str
    startTime: datetime
    awarenessLevelID: str
    endTime: datetime

    def __str__(self):
        return f"{self.text} - {self.awarenessTypeName} - {self.startTime} - {self.endTime}"


class Warnings:
    """Represents a Warnings end point that returns Warning objects."""

    def __init__(self, api: IPMA_API):
        self.api = api
        self.endpoint = (
            f"https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json"
        )

    def _data_to_obj_list(self, raw):
        # awarenessLevelID: cor / nível do aviso (e.g. "green", "yellow", "orange", "red", só existem avisos para níveis diferentes de "green", ou seja, "yellow", "orange", "red")

        return [
            Warning(
                w["text"],
                w["awarenessTypeName"],
                w["idAreaAviso"],
                datetime.strptime(w["startTime"], "%Y-%m-%dT%H:%M:%S"),
                w["awarenessLevelID"],
                datetime.strptime(w["endTime"], "%Y-%m-%dT%H:%M:%S"),
            )
            for w in raw
            if w["awarenessLevelID"] != "green"
        ]

    async def get(self, area: str):
        """Retrieve warnings for a given area."""
        raw = await self.api.retrieve(url=self.endpoint)

        if raw is None:
            raise IPMAException(f"Could not retrieve warnings")

        self.data = [w for w in self._data_to_obj_list(raw) if w.idAreaAviso == area]

        return self.data
