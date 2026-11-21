# Changelog

## 3.1.0 — 2026-11-21

**Python 3.14, Richer Forecasts, and Typed APIs**

Expand forecast data, improve parser reliability, and monitor compatibility
against IPMA's live services.

**Compatibility:** Python 3.14 or newer is now required. Users on Python 3.13
or older should stay on pyipma 3.0.10 until they upgrade Python.

* **Richer forecasts:** expose precipitation intensity, UV index, wind speed
  classes, and coastal conditions, including sea temperature, wave direction,
  wave and swell heights, and swell and peak periods.
* **More metadata:** expose fire-risk forecast, run, and update dates, and retain
  API owner and country information in auxiliary parsers and sea forecasts.
* **Typed APIs:** ship inline annotations and a `py.typed` marker, with strict
  mypy checks for the library and consumer examples, including optional values.
* **Consistent measurements:** normalize numeric strings and missing values
  across observations, weather and sea forecasts, UV risk, and fire risk while
  preserving zero. Fix the observation wind-speed `-99` sentinel check without
  discarding valid `99` values.
* **Unavailable data:** handle missing observation fields and unavailable or
  unknown wind directions; provide unavailable descriptions for missing UV and
  fire risk. Accept string location IDs in sea and UV forecasts.
* **Reliable retrieval:** filter forecast windows using UTC, validate forecast
  periods and fire-risk days explicitly, and avoid storing partial sea forecasts
  when retrieval fails.
* **Correct lookups and ordering:** resolve auxiliary classes by ID, preserve
  the legacy wind-class `get(0)` alias, sort cached locations for each coordinate
  query, and return warnings chronologically while parsing only the requested area.
* **Updated dependencies:** require `aiohttp>=3.14.5` and `geopy>=2.5.0`, refresh
  build and development dependency minimums, and align CI and mypy with Python 3.14.
* **Stronger validation:** expand live parsing and field-coverage checks across
  mainland Portugal, Madeira, and the Azores; add a daily Live API compatibility
  workflow with downloadable JUnit reports and regression tests for parser edge cases.

## Releases

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
