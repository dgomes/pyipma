import logging
import aiohttp
from bs4 import BeautifulSoup

from .stations import STATIONS 

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Station:
    
    def __init__(self, html):
        data = dict()
        row = html.find_all('tr')
        units = [td.get_text() for td in row[1].find_all('td')]
        values = [td.get_text() for td in row[3].find_all('td')][1:]

        self._temperature = values[0]
        self._humidity = values[1]
        self._wind_speed = values[2]
        self._wind_direction = values[3]
        self._precipitation = values[4]
        self._pressure = values[5]

        self._unit_temperature = units[0]
        self._unit_humidity = units[1]
        self._unit_wind_speed = units[2]
        self._unit_wind_direction = units[3]
        self._unit_precipitation = units[4]
        self._unit_pressure = units[5]

    @property
    def temperature(self):
        """Temperature in Celsius."""
        return self._temperature

    @property
    def humidity(self):
        """Relative Humidity"""
        return self._humidity

    @property
    def wind_speed(self):
        return self._wind_speed

    @property
    def wind_direction(self):
        return self._wind_direction

    @property
    def precipitation(self):
        return self._precipitation

    @property
    def pressure(self):
        return self._pressure

    @property
    def temperature_unit(self):
        """Temperature in Celsius."""
        return self._unit_temperature

    @property
    def humidity_unit(self):
        """Relative Humidity"""
        return self._unit_humidity

    @property
    def wind_speed_unit(self):
        return self._unit_wind_speed

    @property
    def wind_direction_unit(self):
        return self._unit_wind_direction

    @property
    def precipitation_unit(self):
        return self._unit_precipitation

    @property
    def pressure_unit(self):
        return self._unit_pressure


class Agent:
    
    def __init__(self, location):
        self.location = location

    async def _get(self, url, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60, **kwargs) as resp:
                logger.debug(resp)
                return await resp.text(encoding='iso-8859-15')

    async def retrieve_station(self, stationID):
        for s in STATIONS:
            if stationID in s['name']:
                localID = s['localID']
                break
        r = await self._get(url="http://pda.ipma.pt/observacao.jsp", params={"selLocal": localID})
        observacao = BeautifulSoup(r, 'html.parser')
        s = Station(observacao.table)
        return s
