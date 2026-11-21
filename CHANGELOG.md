# Changelog

Release notes summarize user-visible changes from the Git history. Historical
dates follow repository tags where available, or version-bump commits otherwise.
Early entries without a matching tag or version bump retain the original README's
version labels and omit dates.

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

## [3.0.10](https://github.com/dgomes/pyipma/tree/v3.0.10) — 2026-06-04

* Fix `SeaForecast.max_temperature` to return the maximum sea surface temperature
  (`sstMax`) instead of the minimum.
* Improve HTTP, connection, timeout, and JSON error handling through `IPMAException`.
* Support modern aiohttp timeout configuration, JSON media types, and request headers.
* Move packaging configuration to `pyproject.toml`; require Python 3.10+ and aiohttp 3.14+.
* Expand live API tests and modernize build, test, and publishing workflows.

## [3.0.9](https://github.com/dgomes/pyipma/tree/3.0.9) — 2025-02-10

* Keep daily forecasts within the previous 24 hours so today's forecast remains
  available. Retain the one-hour cutoff for 1- and 3-hour forecasts.

## [3.0.8](https://github.com/dgomes/pyipma/tree/3.0.8) — 2024-12-26

* Add weather warnings through `Warning`, `Warnings`, and `Location.warnings()`.
* Resolve warnings through the location's district warning-area ID and exclude green alerts.
* Update station coverage in location tests.

## [3.0.7](https://github.com/dgomes/pyipma/tree/3.0.7) — 2023-09-13

* Fix UV risk lookup to use the district's global location ID rather than the
  nearest forecast location ID ([#13](https://github.com/dgomes/pyipma/pull/13)).
* Cache district lookups on `Location` and return `None` when UV risk is unavailable.

## [3.0.6](https://github.com/dgomes/pyipma/tree/3.0.6) — 2023-02-10

* Return the newest station observation instead of the oldest observation in the
  chronologically ordered response.

## [3.0.5](https://github.com/dgomes/pyipma/tree/3.0.5) — 2022-09-22

* Continue searching nearby stations when an observation response is empty or null.
* Return `None` and log the failure if no nearby station supplies an observation.

## [3.0.4](https://github.com/dgomes/pyipma/tree/3.0.4) — 2022-09-12

* Expose `IPMAException` from the package root for consistent error handling.

## [3.0.3](https://github.com/dgomes/pyipma/tree/3.0.3) — 2022-09-12

* Add fire-risk forecasts (RCM), including lookup by nearby DICO region and
  `Location.fire_risk()` for today or tomorrow.
* Add UV risk models and `Location.uv_risk()`.
* Raise an explicit exception when auxiliary location retrieval returns no response.

## [3.0.2](https://github.com/dgomes/pyipma/tree/3.0.2) — 2022-08-06

* Continue Home Assistant integration compatibility work and Python 3.9 support.

## 3.0.1 — 2022-08-06

* Restore Python 3.9-compatible optional annotations and add test fixtures.
  This version is recorded in the
  [version-bump commit](https://github.com/dgomes/pyipma/commit/ec63509).

## [3.0.0](https://github.com/dgomes/pyipma/tree/3.0.0) — 2022-08-06

* Rewrite the backend around dataclass models and endpoint parsers while retaining
  the high-level location interface.
* Support 1-, 3-, and 24-hour forecast selection through `Location.forecast()`.
* Update forecast temperatures, wind strength, station coordinates, and UTC
  forecast timestamps for Home Assistant 2022.08 compatibility.
* Adapt weather descriptions to renamed IPMA API fields.

## [2.1.5](https://github.com/dgomes/pyipma/tree/2.1.5) — 2020-12-20

* Improve logging and format the code with Black.
* Omit humidity from forecast descriptions when humidity is unavailable.

## 2.1.0 — 2020-11-29

* Add sea forecasts associated with the closest sea station, with optional sea
  station discovery through `sea_stations=True`.
* Retrieve weather classification descriptions dynamically from IPMA.
* Handle malformed JSON responses more defensively.

## 2.0.5 — 2020-02-29

* Search earlier observations when the latest sample lacks temperature or humidity.
* Normalize missing observation measurements to `None`.

## 2.0.4 — 2020-02-27

* Skip observation stations reporting `-99` for temperature or humidity.

## 2.0.3 — 2020-02-09

* Try the next closest observation station when the nearest station is offline.
* Update the observation station URL to IPMA's open-data endpoint.

## 2.0.2 — 2020-01-20

* Expose observation station latitude and longitude
  ([#7](https://github.com/dgomes/pyipma/pull/7)).

## 2.0.1

* Maintenance fixes recorded in the original README changelog.

## 2.0.0 — 2019-11-23

* Begin the major refactor separating location discovery, observations, forecasts,
  and API access; subsequent integration work adds English method names and
  handles stations without data.

## 1.2.1 — 2019-02-06

* Fix package installation with pip and expose the package version from `pyipma`.

## 1.2.0

* Correct wind direction mapping.
* Expose station coordinates and global location identifiers.

## 1.1.6

* Interpret IPMA's `-99` sentinel as unavailable data.

## 1.1.5

* Cache the last observation.

## 1.1.4 — 2018-10-29

* Switch to the updated IPMA observation API.

## Earlier development — 2018

* Establish the initial package and weather retrieval API.
* Add weather descriptions, wind information, examples, and station-selection improvements.
