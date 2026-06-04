import datetime

import aiohttp
import pytest
from aioresponses import aioresponses

from pyipma import IPMAException
from pyipma.api import IPMA_API
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


async def test_warnings_filters_green_and_area():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        with aioresponses() as mocked:
            mocked.get(
                "https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json",
                status=200,
                payload=WARNINGS_PAYLOAD,
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
