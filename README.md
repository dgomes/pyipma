[![PyPI version](https://badge.fury.io/py/pyipma.svg)](https://badge.fury.io/py/pyipma)

# pyipma
Python library to retrieve information from [Instituto Português do Mar e Atmosfera](http://www.ipma.pt)

## Requirements
- aiohttp
- geopy

## Example

```python
import asyncio
import aiohttp

from pyipma.api import IPMA_API
from pyipma.location import Location

async def main():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        location = await Location.get(api,  40.6517, -8.6573, sea_stations=True)
        print("Forecast for {}".format(location.name))
        print("Nearest station is {}".format(location.station))
        print("Nearest sea station is {}".format(location.sea_station_name))

        obs = await location.observation(api)
        print("Current weather is {}".format(obs))

        forecasts = await location.forecast(api)
        print("Forecast for tomorrow {}".format(forecasts[0]))
        
        sea_forecast = await location.sea_forecast(api)
        print("Sea forecast for today {}".format(sea_forecast))

asyncio.get_event_loop().run_until_complete(main())
```

## Changelog

* 3.0.0 - Backend fully rewritten, but keeping backward compatibility at interface level
* 2.1.5 - Better logging and code formated with black
* 2.1.0 - Sea Forecast
* 2.0.5 - Look for previous observations when no temperature/humidity available
* 2.0.4 - Ignore Observation stations with temperature/humidity -99
* 2.0.3 - Searches next closest station when offline
* 2.0.2 - Adds Station Lat/Lon
* 2.0.1 - fixes
* 2.0.0 - Major refactor
* 1.2.1 - Fix pip
* 1.2.0 - Wind direction corrected 
* 1.1.6 - Interpret -99 and unavailable
* 1.1.5 - Cache values
* 1.1.4 - New API
* ...

## Credits
Values are obtained from [IPMA](http://api.ipma.pt)


## Contributors
@abmantis
@joaocps

## Copyright

(C) 2018,2019,2020 Diogo Gomes <diogogomes@gmail.com> 
