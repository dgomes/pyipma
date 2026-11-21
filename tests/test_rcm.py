import pytest
from datetime import date, datetime

from pyipma.rcm import RCM_day, RCM


@pytest.mark.parametrize("day", [0, 1])
async def test_rcm(live_api, day):
    risks = await RCM_day(live_api, day).get(40.6405, -8.6538)

    assert risks
    for risk in risks:
        assert isinstance(risk, RCM)
        assert isinstance(risk.dico, str)
        assert isinstance(risk.forecast_date, date)
        assert isinstance(risk.run_date, date)
        assert isinstance(risk.update_date, datetime)
        assert risk.rcm in range(1, 6)
        assert isinstance(risk.coordinates, tuple)
        assert len(risk.coordinates) == 2
        assert all(isinstance(value, float) for value in risk.coordinates)
        assert str(risk)
