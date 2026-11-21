from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar

from geopy import distance

from pyipma.api import IPMA_API
from pyipma import IPMAException

LOGGER = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Located(Protocol):
    @property
    def coordinates(self) -> tuple[float, float]: ...


class Identified(Protocol):
    @property
    def id(self) -> int: ...


T = TypeVar("T")
LocationT = TypeVar("LocationT", bound=Located)
TypeT = TypeVar("TypeT", bound=Identified)


class AuxiliarParser(Generic[T]):
    def __init__(self, api: IPMA_API) -> None:
        self.data: list[T] | None = None
        self.owner: str | None = None
        self.country: str | None = None
        self.api = api
        self.endpoint: str

    def _data_to_obj_list(self, raw: Any) -> list[T]:
        raise NotImplementedError


class TypeParser(AuxiliarParser[TypeT]):
    async def get_type(self, id: int) -> TypeT:
        if not self.data:
            raw = await self.api.retrieve(url=self.endpoint)
            self.owner = raw.get("owner")
            self.country = raw.get("country")
            self.data = sorted(self._data_to_obj_list(raw), key=lambda d: abs(d.id))

        if id >= 0:
            return self.data[id]
        return self.data[-1]  # -99 is the last

    async def get(self, id: int) -> TypeT:
        return await self.get_type(id)


class LocationParser(AuxiliarParser[LocationT]):
    async def get_location(self, lon: float | None, lat: float | None) -> list[LocationT]:
        if not self.data:
            raw = await self.api.retrieve(url=self.endpoint)
            if raw is None:
                raise IPMAException(f"Could not retrieve location for {lon}, {lat}")
            if isinstance(raw, dict):
                self.owner = raw.get("owner")
                self.country = raw.get("country")
            self.data = self._data_to_obj_list(raw)
            if lon is not None and lat is not None:
                self.data = sorted(
                    self.data,
                    key=lambda d: distance.distance((lon, lat), d.coordinates).km,
                )
        return self.data

    async def get(self, lon: float | None, lat: float | None) -> list[LocationT]:
        return await self.get_location(lon, lat)


@dataclass
class District:
    globalIdLocal: int
    local: str
    idRegiao: int
    idDistrito: int
    idConcelho: int
    idAreaAviso: str
    coordinates: tuple[float, float]

    def __str__(self) -> str:
        return f"{self.local}({self.globalIdLocal})"


class Districts(LocationParser[District]):
    def __init__(self, api: IPMA_API) -> None:
        super().__init__(api)
        self.endpoint = "https://api.ipma.pt/open-data/distrits-islands.json"

    def _data_to_obj_list(self, raw: Any) -> list[District]:
        return [
            District(
                d["globalIdLocal"],
                d["local"],
                d["idRegiao"],
                d["idDistrito"],
                d["idConcelho"],
                d["idAreaAviso"],
                (float(d["latitude"]), float(d["longitude"])),
            )
            for d in raw["data"]
        ]


@dataclass
class Forecast_Location:
    globalIdLocal: int
    local: str
    idRegiao: int
    idDistrito: int
    idConcelho: int
    idAreaAviso: str
    coordinates: tuple[float, float]

    def __str__(self) -> str:
        return f"{self.local}({self.globalIdLocal})"


class Forecast_Locations(LocationParser[Forecast_Location]):
    def __init__(self, api: IPMA_API) -> None:
        super().__init__(api)
        self.endpoint = "http://api.ipma.pt/public-data/forecast/locations.json"

    def _data_to_obj_list(self, raw: Any) -> list[Forecast_Location]:
        return [
            Forecast_Location(
                int(d["globalIdLocal"]),
                d["local"],
                d["idRegiao"],
                d["idDistrito"],
                d["idConcelho"],
                d["idAreaAviso"],
                (float(d["latitude"]), float(d["longitude"])),
            )
            for d in raw
        ]

    async def find(self, globalIdLocal: int) -> Forecast_Location:
        if self.data is None:
            self.data = await self.get(None, None)
        return [l for l in self.data if l.globalIdLocal == globalIdLocal][0]


@dataclass
class Sea_Location:
    globalIdLocal: int
    local: str
    idRegiao: int
    idAreaAviso: str
    idLocal: int
    coordinates: tuple[float, float]

    def __str__(self) -> str:
        return f"{self.local}({self.globalIdLocal})"


class Sea_Locations(LocationParser[Sea_Location]):
    def __init__(self, api: IPMA_API) -> None:
        super().__init__(api)
        self.endpoint = "https://api.ipma.pt/open-data/sea-locations.json"

    def _data_to_obj_list(self, raw: Any) -> list[Sea_Location]:
        return [
            Sea_Location(
                d["globalIdLocal"],
                d["local"],
                d["idRegiao"],
                d["idAreaAviso"],
                d["idLocal"],
                (float(d["latitude"]), float(d["longitude"])),
            )
            for d in raw
        ]

    async def find(self, globalIdLocal: int) -> Sea_Location:
        if self.data is None:
            self.data = await self.get(None, None)
        return [l for l in self.data if l.globalIdLocal == globalIdLocal][0]


@dataclass
class Station:
    idEstacao: int
    localEstacao: str
    coordinates: tuple[float, float]

    def __str__(self) -> str:
        return f"{self.localEstacao}({self.idEstacao})"


class Stations(LocationParser[Station]):
    def __init__(self, api: IPMA_API) -> None:
        super().__init__(api)
        self.endpoint = "https://api.ipma.pt/open-data/observation/meteorology/stations/stations.json"

    def _data_to_obj_list(self, raw: Any) -> list[Station]:
        return [
            Station(
                s["properties"]["idEstacao"],
                s["properties"]["localEstacao"],
                (s["geometry"]["coordinates"][1], s["geometry"]["coordinates"][0]),
            )
            for s in raw
        ]


@dataclass
class Weather_Type:
    id: int
    en: str
    pt: str

    def desc(self, lang: str = "pt") -> str:
        if lang == "pt":
            return self.pt
        return self.en

    def __str__(self) -> str:
        return self.desc()


class Weather_Types(TypeParser[Weather_Type]):
    def __init__(self, api: IPMA_API) -> None:
        super().__init__(api)
        self.endpoint = "https://api.ipma.pt/open-data/weather-type-classe.json"

    def _data_to_obj_list(self, raw: Any) -> list[Weather_Type]:
        return [
            Weather_Type(
                id=w["idWeatherType"],
                en=w["descWeatherTypeEN"],
                pt=w["descWeatherTypePT"],
            )
            for w in raw["data"]
        ]


@dataclass
class Wind_Speed_Daily_Type:
    id: int
    en: str
    pt: str

    def desc(self, lang: str = "pt") -> str:
        if lang == "pt":
            return self.pt
        return self.en


class Wind_Speed_Daily_Types(TypeParser[Wind_Speed_Daily_Type]):
    def __init__(self, api: IPMA_API) -> None:
        super().__init__(api)
        self.endpoint = "https://api.ipma.pt/open-data/wind-speed-daily-classe.json"

    def _data_to_obj_list(self, raw: Any) -> list[Wind_Speed_Daily_Type]:
        return [
            Wind_Speed_Daily_Type(
                id=int(w["classWindSpeed"]),
                en=w["descClassWindSpeedDailyEN"],
                pt=w["descClassWindSpeedDailyPT"],
            )
            for w in raw["data"]
        ]


@dataclass
class Precipitation_Class:
    id: int
    en: str
    pt: str

    def desc(self, lang: str = "pt") -> str:
        if lang == "pt":
            return self.pt
        return self.en


class Precipitation_Classes(TypeParser[Precipitation_Class]):
    def __init__(self, api: IPMA_API) -> None:
        super().__init__(api)
        self.endpoint = "https://api.ipma.pt/open-data/precipitation-classe.json"

    def _data_to_obj_list(self, raw: Any) -> list[Precipitation_Class]:
        return [
            Precipitation_Class(
                id=int(w["classPrecInt"]),
                en=w["descClassPrecIntEN"],
                pt=w["descClassPrecIntPT"],
            )
            for w in raw["data"]
        ]
