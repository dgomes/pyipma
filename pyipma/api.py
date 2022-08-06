"""API to IPMA."""
import ast
import logging
import json
import aiohttp

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class IPMA_API:  # pylint: disable=invalid-name
    """Interfaces to http://api.ipma.pt service."""

    def __init__(self, websession):
        """Initializer API session."""
        self.websession = websession

    async def retrieve(self, url, **kwargs):
        """Issue API requests."""
        try:
            async with self.websession.request(
                "GET", url, headers={"Referer": "http://www.ipma.pt"}, **kwargs
            ) as res:
                if res.status != 200:
                    raise Exception("Could not retrieve information from API")
                if res.content_type == "application/json":
                    return await res.json()
                return await res.text()
        except aiohttp.ClientError as err:
            LOGGER.error(err)
        except json.decoder.JSONDecodeError as err:
            LOGGER.error(err)

    @classmethod
    def _to_number(cls, string):
        """Convert string to int or float."""
        num = ast.literal_eval(string)
        if isinstance(num, (int, float)):
            return num
        return string
