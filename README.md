[![PyPI version](https://badge.fury.io/py/pyipma.svg)](https://badge.fury.io/py/pyipma)

# pyipma
Python library to retrieve information from Instituto Português do Mar e Atmosfera

## Requirements
- aiohttp
- BeautifulSoup4
- geopy

## Example

```python
import asyncio
import aiohttp

from pyipma import Station 

async def main():
    async with aiohttp.ClientSession() as session:
        station = await Station.get(session, 40.61,-8.64)
        print("Nearest station if {}".format(station.local))
        print(await station.forecast())
        print(await station.observation())

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

```

## Credits
Values are obtained from [IPMA](http://api.ipma.pt)

## Copyright

(C) 2018 Diogo Gomes <diogogomes@gmail.com> 
