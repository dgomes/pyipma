import datetime

import pytest

from pyipma.uv import UV_risks, UV


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
