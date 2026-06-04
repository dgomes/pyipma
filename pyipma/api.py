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
            ) as response:
                try:
                    response.raise_for_status()
                except aiohttp.ClientResponseError as err:
                    body = await response.text()
                    message = (
                        f"Could not retrieve information from API: "
                        f"{url} returned HTTP {err.status}"
                    )
                    if body:
                        message = f"{message}: {body[:200]}"
                    raise IPMAException(message) from err

                if self._is_json_response(response):
                    return await response.json()
                return await response.text()
        except aiohttp.ClientError as err:
            raise IPMAException(f"Could not retrieve information from API: {url}") from err
        except asyncio.TimeoutError as err:
            raise IPMAException(f"Timed out retrieving information from API: {url}") from err
        except json.decoder.JSONDecodeError as err:
            raise IPMAException(f"Could not decode JSON from API: {url}") from err

    @classmethod
    def _is_json_response(cls, response):
        """Return True when the response has a JSON media type."""
        content_type = response.content_type or ""
        return content_type == "application/json" or content_type.endswith("+json")

    @classmethod
    def _to_number(cls, string):
        """Convert string to int or float."""
        num = ast.literal_eval(string)
        if isinstance(num, (int, float)):
            return num
        return string
