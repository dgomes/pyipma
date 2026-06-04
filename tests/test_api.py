import asyncio

import aiohttp
import pytest
from aioresponses import aioresponses

from pyipma import IPMAException
from pyipma.api import IPMA_API


async def test_retrieve_raises_api_exception_for_http_error():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)
        url = "https://api.ipma.pt/example.json"

        with aioresponses() as mocked:
            mocked.get(url, status=503, body="maintenance")

            with pytest.raises(IPMAException, match="HTTP 503"):
                await api.retrieve(url)


async def test_retrieve_raises_api_exception_for_connection_error():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)
        url = "https://api.ipma.pt/example.json"

        with aioresponses() as mocked:
            mocked.get(url, exception=aiohttp.ClientConnectionError("boom"))

            with pytest.raises(IPMAException, match=url):
                await api.retrieve(url)


async def test_retrieve_raises_api_exception_for_timeout():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)
        url = "https://api.ipma.pt/example.json"

        with aioresponses() as mocked:
            mocked.get(url, exception=asyncio.TimeoutError())

            with pytest.raises(IPMAException, match="Timed out"):
                await api.retrieve(url)


async def test_retrieve_raises_api_exception_for_invalid_json():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)
        url = "https://api.ipma.pt/example.json"

        with aioresponses() as mocked:
            mocked.get(
                url,
                status=200,
                body="{",
                headers={"Content-Type": "application/json"},
            )

            with pytest.raises(IPMAException, match="decode JSON"):
                await api.retrieve(url)


async def test_retrieve_returns_text_response():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)
        url = "https://api.ipma.pt/example.txt"

        with aioresponses() as mocked:
            mocked.get(
                url,
                status=200,
                body="plain response",
                headers={"Content-Type": "text/plain"},
            )

            assert await api.retrieve(url) == "plain response"


async def test_retrieve_accepts_client_timeout_instance():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session, timeout=aiohttp.ClientTimeout(total=1))
        url = "https://api.ipma.pt/example.json"

        with aioresponses() as mocked:
            mocked.get(url, status=200, payload={"ok": True})

            assert await api.retrieve(url) == {"ok": True}


def test_to_number_converts_numeric_strings():
    assert IPMA_API._to_number("1") == 1
    assert IPMA_API._to_number("1.5") == 1.5
    assert IPMA_API._to_number("'text'") == "'text'"
