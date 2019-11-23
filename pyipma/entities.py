"""Serviços auxiliares."""
from collections import UserDict, namedtuple

from .consts import API_DISTRITS, API_WEATHER_TYPE, API_WIND_SPEED_DAILY, API_PRECIPITATION

ENTITY2APIURL = {
    "Distrit_Island": {'url': API_DISTRITS, 'key': 'globalIdLocal'},
    "Weather_Type": {'url': API_WEATHER_TYPE, 'key': 'idWeatherType'},
    "Wind_Speed_Daily": {'url': API_WIND_SPEED_DAILY, 'key': 'classWindSpeed'},
    "Precipitation": {'url': API_PRECIPITATION, 'key': 'classPrecInt'},
}

class Entities(UserDict):
    def __init__(self, entity_name, data, key):
        self._data = {}

        if len(data) < 1:
            raise Exception(f"No {self.__class__.name} data")
        Data = namedtuple(entity_name, list(data["data"][0].keys()))
        for entry in data["data"]:
            self._data[entry[key]] = Data._make(entry.values())
        
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



