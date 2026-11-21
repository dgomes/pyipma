import aiohttp

import pytest

from pyipma.api import IPMA_API


class StaticAPI:
    """Small API double for parser tests that only need response payloads."""

    def __init__(self, responses):
        self.responses = responses

    async def retrieve(self, url, **kwargs):
        response = self.responses[url]
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
async def live_api():
    """Use IPMA's live service so upstream incompatibilities fail tests."""
    async with aiohttp.ClientSession() as session:
        yield IPMA_API(session)


@pytest.fixture
def static_api():
    return StaticAPI
