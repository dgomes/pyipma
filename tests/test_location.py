import aiohttp
import pytest
from mock import patch
from pyipma.api import IPMA_API
from pyipma.location import Location


def dump_json(data):
    return data


@pytest.mark.asyncio
async def test_location():
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        location = await Location.get(api, 40.6517, -8.6573)
        print("Forecast for {}".format(location.name))
        print("Nearest station is {}".format(location.station))
        assert location.name == "Aveiro"
        assert location.station == "Aveiro (Universidade)"

        # 1210702 is the idEstacao for Aveiro (Universidade)
        assert location.id_station == 1210702
        with patch.object(
            api,
            "retrieve",
            return_value=dump_json(
                {
                    "2022-07-27T15:00": {
                        "1210702": {
                            "intensidadeVentoKM": 20.9,
                            "temperatura": 19.0,
                            "radiacao": 141.4,
                            "idDireccVento": 9,
                            "precAcumulada": 0.0,
                            "intensidadeVento": 5.8,
                            "humidade": 81.0,
                            "pressao": 1017.1,
                        },
                    }
                }
            ),
        ):
            obs = await location.observation(api)
            assert obs.temperature == 19.0
            assert obs.humidity == 81.0

        # 1010500 is the globalIdLocal for Aveiro
        assert location.global_id_local == 1010500

        forecasts = await location.forecast(api)
        assert forecasts[0].temperature == 19.8
