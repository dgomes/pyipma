import datetime

import pytest

from pyipma.uv import UV_risks, UV


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, 0.0), ("0", 0.0), (-99, None), ("-99.0", None),
     (None, None), ("", None), ("5.9", 5.9)],
)
async def test_uv_normalizes_values_and_location_ids(static_api, value, expected):
    rows = [{
        "idPeriodo": "24", "intervaloHora": "12h-14h", "data": f"2026-11-{day}",
        "globalIdLocal": "1010500", "iUv": value,
    } for day in (23, 21, 22)]
    rows.append(rows[0] | {"globalIdLocal": 999, "iUv": "invalid"})
    parser = UV_risks(static_api({"https://api.ipma.pt/open-data/forecast/meteorology/uv/uv.json": rows}))

    risks = await parser.get(1010500)

    assert [r.data.day for r in risks] == [21, 22, 23]
    for risk in risks:
        assert risk.globalIdLocal == 1010500
        assert risk.iUv == expected
        assert (str(risk) == "Sem informação") == (expected is None)
    assert await parser.get(123) == []


async def test_uv_missing_index(static_api):
    row = {"idPeriodo": 24, "intervaloHora": "12h-14h", "data": "2026-11-21", "globalIdLocal": 1010500}
    parser = UV_risks(static_api({"https://api.ipma.pt/open-data/forecast/meteorology/uv/uv.json": [row]}))
    risk, = await parser.get()
    assert risk.iUv is None
    assert str(risk) == "Sem informação"


async def test_uv_risks(live_api):
    risks = await UV_risks(live_api).get()

    assert risks
    for risk in risks:
        assert isinstance(risk, UV)
        assert isinstance(risk.idPeriodo, int)
        assert isinstance(risk.intervaloHora, str)
        assert isinstance(risk.data, datetime.datetime)
        assert isinstance(risk.globalIdLocal, int)
        assert isinstance(risk.iUv, float)
        assert str(risk)

    aveiro_risks = await UV_risks(live_api).get(1010500)
    assert aveiro_risks
    assert all(risk.globalIdLocal == 1010500 for risk in aveiro_risks)
    assert [risk.data for risk in aveiro_risks] == sorted(
        risk.data for risk in aveiro_risks
    )


@pytest.mark.parametrize(
    ("index", "level"),
    [(1.2, "Baixo"), (4.1, "Moderado"), (5.9, "Elevado"),
     (7.5, "Muito Elevado"), (10.3, "Extremo")],
)
def test_uv_risk_description(index, level):
    risk = UV(0, "12h-14h", datetime.datetime(2026, 1, 1), 1010500, index)
    assert str(risk).startswith(f"{level} - ")
