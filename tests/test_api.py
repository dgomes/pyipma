import asyncio
import json

import aiohttp
import pytest

from pyipma import IPMAException
from pyipma.api import IPMA_API


class FixtureResponse:
    def __init__(self, status=200, body="", content_type="text/plain", payload=None):
        self.status = status
        self.body = body
        self.content_type = content_type
        self.payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(
                request_info=None,
                history=(),
                status=self.status,
            )

    async def text(self):
        return self.body

    async def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class FixtureSession:
    def __init__(self, response):
        self.response = response
        self.kwargs = None

    def request(self, method, url, **kwargs):
        self.kwargs = kwargs
        return self.response


class RaisingSession:
    def __init__(self, exception):
        self.exception = exception

    def request(self, method, url, **kwargs):
        raise self.exception


async def test_retrieve_raises_api_exception_for_http_error():
    api = IPMA_API(
        FixtureSession(FixtureResponse(status=503, body="maintenance")),
    )

    with pytest.raises(IPMAException, match="HTTP 503"):
        await api.retrieve("https://api.ipma.pt/example.json")


async def test_retrieve_raises_api_exception_for_connection_error():
    api = IPMA_API(RaisingSession(aiohttp.ClientConnectionError("boom")))

    with pytest.raises(IPMAException, match="example.json"):
        await api.retrieve("https://api.ipma.pt/example.json")


async def test_retrieve_raises_api_exception_for_timeout():
    api = IPMA_API(RaisingSession(asyncio.TimeoutError()))

    with pytest.raises(IPMAException, match="Timed out"):
        await api.retrieve("https://api.ipma.pt/example.json")


async def test_retrieve_raises_api_exception_for_invalid_json():
    api = IPMA_API(
        FixtureSession(
            FixtureResponse(
                content_type="application/json",
                payload=json.JSONDecodeError("invalid", "{", 0),
            ),
        ),
    )

    with pytest.raises(IPMAException, match="decode JSON"):
        await api.retrieve("https://api.ipma.pt/example.json")


async def test_retrieve_returns_text_response():
    api = IPMA_API(
        FixtureSession(FixtureResponse(body="plain response")),
    )

    assert await api.retrieve("https://api.ipma.pt/example.txt") == "plain response"


async def test_retrieve_accepts_client_timeout_instance():
    session = FixtureSession(
        FixtureResponse(content_type="application/json", payload={"ok": True}),
    )
    timeout = aiohttp.ClientTimeout(total=1)
    api = IPMA_API(session, timeout=timeout)

    assert await api.retrieve("https://api.ipma.pt/example.json") == {"ok": True}
    assert session.kwargs["timeout"] is timeout


async def test_retrieve_returns_json_response_from_api():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        response = await api.retrieve(
            "https://api.ipma.pt/open-data/weather-type-classe.json"
        )

        assert "data" in response


async def test_retrieve_accepts_json_suffix_media_type():
    api = IPMA_API(
        FixtureSession(
            FixtureResponse(
                content_type="application/vnd.ipma+json",
                payload={"ok": True},
            ),
        ),
    )

    assert await api.retrieve("https://api.ipma.pt/example") == {"ok": True}


def test_to_number_converts_numeric_strings():
    assert IPMA_API._to_number("1") == 1
    assert IPMA_API._to_number("1.5") == 1.5
    assert IPMA_API._to_number("'text'") == "'text'"
