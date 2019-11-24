"""Serviços auxiliares."""
from collections import UserDict, namedtuple

from .consts import API_DISTRITS, API_WEATHER_TYPE, API_WIND_SPEED_DAILY, API_PRECIPITATION

class Entities(UserDict): # pylint: disable=too-many-ancestors
    """Generic base class for IPMA auxiliar services."""
    def __init__(self, entity_name, data, key):
        super().__init__()
        self._data = {}

        if len(data) < 1:
            raise Exception(f"No {self.__class__.__name__} data")
        data_type = namedtuple(entity_name, list(data["data"][0].keys()))
        for entry in data["data"]:
            self._data[entry[key]] = data_type._make(entry.values())

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def get(self, api): # pylint: disable=arguments-differ
        raise NotImplementedError()


class DistritIsland(Entities): # pylint: disable=too-many-ancestors
    """Object based representation of IPMA open API district_islands.json."""
    def __init__(self, data):
        super().__init__(self.__class__.__name__, data, 'globalIdLocal')

    @classmethod
    async def get(cls, api):
        raw = await api.retrieve(API_DISTRITS)

        return cls(raw)

class WeatherType(Entities): # pylint: disable=too-many-ancestors
    """Object based representation of IPMA open API weather-type-classe.json."""
    def __init__(self, data):
        super().__init__(self.__class__.__name__, data, 'idWeatherType')

    @classmethod
    async def get(cls, api):
        raw = await api.retrieve(API_WEATHER_TYPE)

        return cls(raw)

class WindSpeedDaily(Entities): # pylint: disable=too-many-ancestors
    """Object based representation of IPMA open API wind-speed-daily-classe.json."""
    def __init__(self, data):
        super().__init__(self.__class__.__name__, data, 'classWindSpeed')

    @classmethod
    async def get(cls, api):
        raw = await api.retrieve(API_WIND_SPEED_DAILY)

        return cls(raw)

class Precipitation(Entities): # pylint: disable=too-many-ancestors
    """Object based representation of IPMA open API precipitation_classe.json."""
    def __init__(self, data):
        super().__init__(self.__class__.__name__, data, 'classPrecInt')

    @classmethod
    async def get(cls, api):
        raw = await api.retrieve(API_PRECIPITATION)

        return cls(raw)
