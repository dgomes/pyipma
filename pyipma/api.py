"""API to IPMA."""
import ast
import asyncio
import logging
import json
import aiohttp

from . import IPMAException

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

DEFAULT_TIMEOUT = 10


class IPMA_API:  # pylint: disable=invalid-name
    """Interfaces to http://api.ipma.pt service."""

    def __init__(self, websession, timeout=DEFAULT_TIMEOUT):
        """Initializer API session."""
        self.websession = websession
        self.timeout = timeout

    async def retrieve(self, url, **kwargs):
        """Issue API requests."""
        headers = {"Referer": "http://www.ipma.pt"}
        headers.update(kwargs.pop("headers", {}) or {})

        if self.timeout is not None and "timeout" not in kwargs:
            if isinstance(self.timeout, aiohttp.ClientTimeout):
                kwargs["timeout"] = self.timeout
            else:
                kwargs["timeout"] = aiohttp.ClientTimeout(total=self.timeout)

        try:
            async with self.websession.request(
                "GET", url, headers=headers, **kwargs
            ) as res:
                if res.status != 200:
                    body = await res.text()
                    raise IPMAException(
                        f"Could not retrieve information from API: "
                        f"{url} returned HTTP {res.status}: {body[:200]}"
                    )
                if res.content_type == "application/json":
                    return await res.json()
                return await res.text()
        except aiohttp.ClientError as err:
            raise IPMAException(f"Could not retrieve information from API: {url}") from err
        except asyncio.TimeoutError as err:
            raise IPMAException(f"Timed out retrieving information from API: {url}") from err
        except json.decoder.JSONDecodeError as err:
            raise IPMAException(f"Could not decode JSON from API: {url}") from err

    @classmethod
    def _to_number(cls, string):
        """Convert string to int or float."""
        num = ast.literal_eval(string)
        if isinstance(num, (int, float)):
            return num
        return string
