import logging
from dataclasses import dataclass

from geopy import distance

from pyipma.api import IPMA_API

LOGGER = logging.getLogger(__name__)  # pylint: disable=invalid-name


class AuxiliarParser:
    def __init__(self, api: IPMA_API, type="location"):
        _TYPES = {"location": self.get_location, "type": self.get_type}
        self.data = None
        self.api = api
        self.get = _TYPES[type]

    async def get_type(self, id):
        if not self.data:
            raw = await self.api.retrieve(url=self.endpoint)

            self.data = sorted(self._data_to_obj_list(raw), key=lambda d: abs(d.id))

        if id >= 0:
            return self.data[id]
        else:
            return self.data[-1]  # -99 is the last

    async def get_location(self, lon, lat):
        if not self.data:
            raw = await self.api.retrieve(url=self.endpoint)

            self.data = self._data_to_obj_list(raw)

            if (lon, lat) != (None, None):
                self.data = sorted(
                    self.data,
                    key=lambda d: distance.distance((lon, lat), d.coordinates).km,
                )

        return self.data


@dataclass
class District:
    globalIdLocal: int
    local: str
    idRegiao: int
    idDistrito: int
    idConcelho: int
    idAreaAviso: str
    coordinates: tuple[float, float]

    def __str__(self):
        return f"{self.local}({self.globalIdLocal})"


class Districts(AuxiliarParser):
    def __init__(self, api: IPMA_API):
        super().__init__(api)
        self.endpoint = "https://api.ipma.pt/open-data/distrits-islands.json"

    def _data_to_obj_list(self, raw):
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

    def __str__(self):
        return f"{self.local}({self.globalIdLocal})"


class Forecast_Locations(AuxiliarParser):
    def __init__(self, api: IPMA_API):
        super().__init__(api)
        self.endpoint = "http://api.ipma.pt/public-data/forecast/locations.json"

    def _data_to_obj_list(self, raw):
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

    async def find(self, globalIdLocal):
        if self.data is None:
            await self.get(None, None)
        return [l for l in self.data if l.globalIdLocal == globalIdLocal][0]


@dataclass
class Sea_Location:
    globalIdLocal: int
    local: str
    idRegiao: int
    idAreaAviso: str
    idLocal: int
    coordinates: tuple[float, float]

    def __str__(self):
        return f"{self.local}({self.globalIdLocal})"


class Sea_Locations(AuxiliarParser):
    def __init__(self, api: IPMA_API):
        super().__init__(api)
        self.endpoint = "https://api.ipma.pt/open-data/sea-locations.json"

    def _data_to_obj_list(self, raw):
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

    async def find(self, globalIdLocal):
        if self.data is None:
            await self.get(None, None)
        return [l for l in self.data if l.globalIdLocal == globalIdLocal][0]


@dataclass
class Station:
    idEstacao: int
    localEstacao: str
    coordinates: tuple[float, float]

    def __str__(self):
        return f"{self.localEstacao}({self.idEstacao})"


class Stations(AuxiliarParser):
    def __init__(self, api: IPMA_API):
        super().__init__(api)
        self.endpoint = "https://api.ipma.pt/open-data/observation/meteorology/stations/stations.json"

    def _data_to_obj_list(self, raw):
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

    def desc(self, lang="pt"):
        if lang == "pt":
            return self.pt
        return self.en

    def __str__(self):
        return self.desc()


class Weather_Types(AuxiliarParser):
    def __init__(self, api: IPMA_API):
        super().__init__(api, "type")
        self.endpoint = "https://api.ipma.pt/open-data/weather-type-classe.json"
        self.order = lambda d: abs(d.id)

    def _data_to_obj_list(self, raw):
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

    def desc(self, lang="pt"):
        if lang == "pt":
            return self.pt
        return self.en


class Wind_Speed_Daily_Types(AuxiliarParser):
    def __init__(self, api: IPMA_API):
        super().__init__(api, "type")
        self.endpoint = "https://api.ipma.pt/open-data/wind-speed-daily-classe.json"
        self.order = lambda d: abs(d.id)

    def _data_to_obj_list(self, raw):
        return [
            Weather_Type(
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

    def desc(self, lang="pt"):
        if lang == "pt":
            return self.pt
        return self.en


class Precipitation_Classes(AuxiliarParser):
    def __init__(self, api: IPMA_API):
        super().__init__(api, "type")
        self.endpoint = "https://api.ipma.pt/open-data/precipitation-classe.json"
        self.order = lambda d: abs(d.id)

    def _data_to_obj_list(self, raw):
        return [
            Weather_Type(
                id=int(w["classPrecInt"]),
                en=w["descClassPrecIntEN"],
                pt=w["descClassPrecIntPT"],
            )
            for w in raw["data"]
        ]
