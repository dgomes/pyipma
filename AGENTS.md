# Repository guidance

## Project and layout

pyipma is an asynchronous client for IPMA weather services. Python 3.14+ is
required; runtime and development dependencies are defined in `pyproject.toml`.

- `pyipma/api.py`: HTTP requests, timeouts, response decoding, and `IPMAException`.
- `pyipma/location.py`: coordinate-based discovery and high-level retrieval with fallback to nearby stations.
- `pyipma/auxiliar.py`: location, station, and classification lookups.
- `pyipma/forecast.py`, `observation.py`, `sea_forecast.py`, `rcm.py`, `uv.py`, and `warnings.py`: endpoint parsers and models.
- `tests/`: live API checks and static parser/error-handling tests; `tests/conftest.py` provides `live_api` and `static_api` fixtures.
- `tests/test_api_schema.py`: upstream field coverage for supported endpoints.
- `tests/typing/consumer.py`: checks of types exposed to library consumers.
- `.github/workflows/`: application checks, daily live API compatibility, and package publishing.

## Setup and validation

Use the existing `venv` if it runs Python 3.14+, or create a virtual environment
with a supported interpreter and install development dependencies:

```sh
python3.14 -m venv venv
venv/bin/python -m pip install -e ".[dev]"
```

Run checks appropriate to the change:

```sh
venv/bin/python -m mypy
venv/bin/python -m flake8 pyipma tests --count --select=E9,F63,F7,F82 --show-source --statistics
venv/bin/python -m pytest
```

Strict mypy covers the library and consumer examples. The full pytest suite
requires internet access and contacts live IPMA services. For focused work,
select relevant test files or individual tests. Report network or upstream
failures separately from local regressions; do not silently skip live tests or
weaken schema checks to get a passing run. Documentation-only edits usually need
consistency checks against the code and workflows rather than the live suite.

## Implementation conventions

- Keep HTTP access asynchronous through `IPMA_API` and reuse the caller-owned
  `aiohttp.ClientSession`.
- Preserve public names, including existing underscore/capitalization conventions
  and IPMA field names. Add descriptive properties consistently with existing models.
- Maintain concrete annotations and accurate optional return types. Keep the
  `py.typed` marker packaged and update consumer type checks for public API changes.
- Handle unavailable data explicitly. Forecast numeric parsing preserves zero
  and maps `-99` to `None`; use the existing conversion helper when adding fields.
- Preserve chronological ordering and nearby-station fallback behavior. Check
  coordinate ordering carefully: public `Location.get()` examples pass latitude,
  longitude positionally, despite its parameter names `lon` and `lat`.
- Add focused static tests for parser changes and error paths. For new upstream
  fields, update models, parsing, and the relevant live schema coverage together.
- Follow the surrounding style and avoid unrelated formatting changes.

## Documentation and releases

Keep README examples aligned with method signatures and missing-data behavior.
Maintain release history in `CHANGELOG.md`, linked from the README. Document
changes since the last release under an Unreleased entry in that file.
The package version is defined by `pyipma.__version__` and read dynamically by
setuptools; do not invent a release number for unreleased work. Package publishing
is configured for `v*` tags and created GitHub releases.
