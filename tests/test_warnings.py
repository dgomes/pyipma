import datetime

import pytest

from pyipma import IPMAException
from pyipma.warnings import Warning, Warnings


WARNINGS_PAYLOAD = [
    {
        "text": "Chuva forte",
        "awarenessTypeName": "Precipitação",
        "idAreaAviso": "AVR",
        "startTime": "2026-06-04T06:00:00",
        "awarenessLevelID": "yellow",
        "endTime": "2026-06-04T18:00:00",
    },
    {
        "text": "Sem avisos",
        "awarenessTypeName": "Sem aviso",
        "idAreaAviso": "AVR",
        "startTime": "2026-06-04T00:00:00",
        "awarenessLevelID": "green",
        "endTime": "2026-06-04T23:59:00",
    },
    {
        "text": "Vento forte",
        "awarenessTypeName": "Vento",
        "idAreaAviso": "LSB",
        "startTime": "2026-06-04T08:00:00",
        "awarenessLevelID": "orange",
        "endTime": "2026-06-04T20:00:00",
    },
]


async def test_live_warnings(live_api):
    warnings = await Warnings(live_api).get("AVR")

    assert isinstance(warnings, list)
    for warning in warnings:
        assert isinstance(warning, Warning)
        assert warning.idAreaAviso == "AVR"
        assert warning.awarenessLevelID in {"yellow", "orange", "red"}
        assert isinstance(warning.text, str)
        assert isinstance(warning.awarenessTypeName, str)
        assert isinstance(warning.startTime, datetime.datetime)
        assert isinstance(warning.endTime, datetime.datetime)


async def test_warnings_filters_green_and_area(static_api):
    api = static_api(
        {
            "https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json": WARNINGS_PAYLOAD
        }
    )

    warnings = await Warnings(api).get("AVR")

    assert warnings == [
        Warning(
            "Chuva forte",
            "Precipitação",
            "AVR",
            datetime.datetime(2026, 6, 4, 6, 0),
            "yellow",
            datetime.datetime(2026, 6, 4, 18, 0),
        )
    ]
    assert (
        str(warnings[0])
        == "Chuva forte - Precipitação - 2026-06-04 06:00:00 - 2026-06-04 18:00:00"
    )


async def test_warnings_raises_when_api_returns_none():
    class EmptyAPI:
        async def retrieve(self, url):
            return None

    with pytest.raises(IPMAException, match="Could not retrieve warnings"):
        await Warnings(EmptyAPI()).get("AVR")


async def test_warnings_sort_and_ignore_unrelated_invalid_dates(static_api):
    first = WARNINGS_PAYLOAD[0]
    later = first | {"startTime": "2026-06-04T12:00:00"}
    earlier_end = first | {"endTime": "2026-06-04T12:00:00"}
    unrelated = WARNINGS_PAYLOAD[2] | {"startTime": "invalid"}
    green = WARNINGS_PAYLOAD[1] | {"endTime": "invalid"}
    parser = Warnings(static_api({
        "https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json":
        [later, unrelated, first, green, earlier_end],
    }))

    warnings = await parser.get("AVR")

    assert parser.data is warnings
    assert [(w.startTime.hour, w.endTime.hour) for w in warnings] == [(6, 12), (6, 18), (12, 18)]
    assert await parser.get("missing") == []


async def test_warnings_reject_invalid_dates_in_selected_area(static_api):
    parser = Warnings(static_api({
        "https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json":
        [WARNINGS_PAYLOAD[0] | {"startTime": "invalid"}],
    }))
    with pytest.raises(ValueError):
        await parser.get("AVR")
