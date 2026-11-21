[![PyPI version](https://badge.fury.io/py/pyipma.svg)](https://badge.fury.io/py/pyipma)

# pyipma
Python library to retrieve information from [Instituto Português do Mar e Atmosfera](http://www.ipma.pt)

## Requirements
- aiohttp
- geopy

## Example

Coordinates are passed as latitude, longitude.

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

Forecasts expose `precipitation_intensity` (the API's `idIntensidadePrecipita`
class code), `uv_index`, and `wind_speed_class`. To resolve an intensity code
to an English or Portuguese description, use
`await Precipitation_Classes(api).get(forecast.precipitation_intensity)` from
`pyipma.auxiliar` when the code is not `None`. Class definitions are listed in
the [IPMA API documentation](https://api.ipma.pt/).

Coastal forecasts also expose `sea_temperature`, `wave_direction`, `wave_height`,
`swell_height`, `swell_period`, and `peak_period` when returned by IPMA. These
properties are `None` for periods or locations without marine data. The original
API field names remain available on the forecast object.

Forecast humidity, UV index, and feels-like temperature are numeric values;
missing values (`-99`) become `None`, and zero remains valid. Fire-risk objects
expose `forecast_date` and `run_date` as dates and `update_date` as a datetime.
Auxiliary parsers and `SeaForecasts` also retain the API's `owner` and `country`
metadata after retrieval.

## Running tests

Install the test dependencies in a virtual environment, then run pytest:

```sh
python3 -m venv venv
venv/bin/python -m pip install -e ".[test]"
venv/bin/python -m pytest
```

Tests call IPMA's live API and require internet access. Endpoint failures, response
schema changes, and parsing errors fail the suite so upstream changes are visible.
Live field-coverage tests also fail when supported endpoints add properties that
the library does not yet model. These checks cover the endpoints used by pyipma;
they do not discover unrelated IPMA services.

## Changelog

* 3.0.10 - Update aiohttp support and response handling
* 3.0.9 - Adjust forecast window for 24 hours periods
* 3.0.8 - Adds Weather Warnings
* 3.0.7 - Adds UV Index (@tokenize74)
* 3.0.6 - Bug Fixes
* 3.0.3 - Adds RCM (Fire Risk)
* 3.0.2 - Changes to fully support Home Assistant integration
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
