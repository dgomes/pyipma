import json

import pytest


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
def load_fixture():
    def _load_fixture(path):
        with open(path) as fixture:
            return json.load(fixture)

    return _load_fixture


@pytest.fixture
def static_api():
    return StaticAPI
