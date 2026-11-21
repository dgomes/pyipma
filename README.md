[![PyPI version](https://badge.fury.io/py/pyipma.svg)](https://badge.fury.io/py/pyipma)

# pyipma
Asynchronous Python library to retrieve weather information from
[Instituto Português do Mar e Atmosfera (IPMA)](https://www.ipma.pt).

Supports weather observations, forecasts at 1-, 3-, and 24-hour intervals,
three-day sea forecasts, weather warnings, UV risk, and fire risk (RCM).
Locations and nearby stations are selected from geographic coordinates.

## Installation

Requires Python 3.10 or newer. Runtime dependencies are `aiohttp>=3.14` and
`geopy`, installed automatically with the package:

```sh
python -m pip install pyipma
```

## Example

Pass coordinates to `Location.get()` positionally as latitude, longitude.
Create and close the `aiohttp.ClientSession` in your application.

```python
import asyncio
import aiohttp

from pyipma.api import IPMA_API
from pyipma.location import Location

async def main() -> None:
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        location = await Location.get(api, 40.6517, -8.6573, sea_stations=True)
        print(f"Forecast for {location.name}")
        print(f"Nearest station is {location.station}")
        print(f"Nearest sea station is {location.sea_station_name}")

        obs = await location.observation(api)
        if obs is not None:
            print(f"Latest observation: {obs}")

        forecasts = await location.forecast(api, period=24)
        for forecast in forecasts:
            print(f"Forecast for {forecast.forecast_date}: {forecast}")

        sea_forecasts = await location.sea_forecast(api)
        for sea_forecast in sea_forecasts:
            print(f"Sea forecast for {sea_forecast.forecastDate}: {sea_forecast}")

        print("Weather warnings:", await location.warnings(api))
        print("UV risk:", await location.uv_risk(api))
        print("Fire risk today:", await location.fire_risk(api, day=0))

asyncio.run(main())
```

`location.forecast(api, period=...)` accepts `1`, `3`, or `24` (the default),
and returns forecasts sorted by date. The first daily forecast can be for today;
use `forecast_date` to identify the day. `location.sea_forecast(api)` returns a
date-sorted list for today and the next two days and requires
`sea_stations=True` when creating the location.

The location methods try up to ten nearby locations or stations for weather
forecasts, observations, and sea forecasts. If retrieval fails, forecast methods
return an empty list; observation and risk methods return `None`. Warnings return
a list (which can be empty), or `None` if retrieval fails or no warning area is
available. Check these results before indexing or accessing model properties.

`IPMA_API` uses a ten-second request timeout by default. Its `timeout` argument
accepts seconds, an `aiohttp.ClientTimeout`, or `None` to use the session's
timeout. Low-level request failures raise `pyipma.IPMAException`.

## Forecast data

Forecasts expose `precipitation_intensity` (the API's `idIntensidadePrecipita`
class code), `uv_index`, and `wind_speed_class`. To resolve an intensity code
to an English or Portuguese description, use
`await Precipitation_Classes(api).get(forecast.precipitation_intensity)` from
`pyipma.auxiliar` when the code is not `None`. Class definitions are listed in
the [IPMA API documentation](https://api.ipma.pt/).

Coastal entries in `Forecast` also expose `sea_temperature`, `wave_direction`, `wave_height`,
`swell_height`, `swell_period`, and `peak_period` when returned by IPMA. These
properties are `None` for periods or locations without marine data. The original
API field names remain available on the forecast object. The separate
`SeaForecast` model returned by `location.sea_forecast()` exposes daily minimum
and maximum sea temperatures, wave heights, and swell periods, plus wave direction.

Forecast humidity, UV index, and feels-like temperature are numeric values;
missing values (`-99`) become `None`, and zero remains valid. Fire-risk objects
expose `forecast_date` and `run_date` as dates and `update_date` as a datetime.
Auxiliary parsers and `SeaForecasts` also retain the API's `owner` and `country`
metadata after retrieval.

## Type checking

The library ships inline type annotations and a `py.typed` marker for downstream
type checkers. Parsed models and parser methods expose concrete return types,
including `None` for unavailable values. The low-level `IPMA_API.retrieve()`
method returns dynamic JSON or text; use the parsers for typed results.

Install development dependencies and run the strict type checks:

```sh
venv/bin/python -m pip install -e ".[dev]"
venv/bin/python -m mypy
```

These checks cover the library and consumer examples in `tests/typing` and run
in CI alongside the live API tests.

## Running tests

Install the test dependencies in a virtual environment, then run pytest:

```sh
python3 -m venv venv
venv/bin/python -m pip install -e ".[test]"
venv/bin/python -m pytest
```

The suite includes static parser and error-handling tests as well as tests that
call IPMA's live API and require internet access. Endpoint failures, response
schema changes, and parsing errors fail the suite so upstream changes are visible.
Live field-coverage tests also fail when supported endpoints add properties that
the library does not yet model. These checks cover the endpoints used by pyipma;
they do not discover unrelated IPMA services.

The **Live API compatibility** GitHub Actions workflow runs this suite daily at
08:23 UTC and can also be started from the Actions tab using **Run workflow**.
It checks the current library against live IPMA responses, including field
coverage and parsing compatibility. API outages also fail the run. Each run
uploads a JUnit test report as the `live-api-test-results` artifact for diagnosis.
Scheduled runs use the repository's default branch.

## Changelog

### Unreleased

* Expose precipitation intensity, UV index, wind speed class, and coastal fields on forecasts.
* Normalize numeric forecast values, preserve zero, and treat missing values as `None`.
* Expose fire-risk forecast, run, and update dates, and retain API owner/country metadata.
* Ship inline type annotations and `py.typed`, with strict mypy checks for the library and consumer examples.
* Expand live API parsing and field-coverage checks across mainland Portugal, Madeira, and the Azores.
* Add the daily Live API compatibility workflow and downloadable JUnit reports.

### Releases

* 3.0.10 - Update aiohttp support and HTTP/JSON error handling, fix sea forecasts, and modernize packaging and CI
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
Values are obtained from [IPMA](https://api.ipma.pt/).


## Contributors
@abmantis
@joaocps

## Copyright

(C) 2018,2019,2020 Diogo Gomes <diogogomes@gmail.com> 
