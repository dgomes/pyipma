import pytest
from datetime import date, datetime

from pyipma.rcm import RCM_day, RCM


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, 0), ("3", 3), (-99, None), ("-99.0", None), (None, None), ("", None)],
)
async def test_fire_risk_normalizes_class_codes(static_api, value, expected):
    payload = {
        "dataPrev": "2026-11-21", "dataRun": "2026-11-20", "fileDate": "2026-11-21T06:00:00",
        "local": {"unknown": {"dico": "unknown", "latitude": "40.0", "longitude": "-8.0", "data": {"rcm": value}}},
    }
    parser = RCM_day(static_api({"http://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d0.json": payload}))

    risk, = await parser.get(None, None)

    assert risk.rcm == expected
    assert risk.coordinates == (40.0, -8.0)
    assert risk.forecast_date == date(2026, 11, 21)
    assert risk.run_date == date(2026, 11, 20)
    assert risk.update_date == datetime(2026, 11, 21, 6)
    assert str(risk).endswith("para unknown")
    if expected is None or expected == 0:
        assert str(risk).startswith("Risco indisponível")


@pytest.mark.parametrize("day", [-1, 2])
def test_fire_risk_rejects_unsupported_days(day):
    with pytest.raises(ValueError, match="Fire risk day"):
        RCM_day(None, day)


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
