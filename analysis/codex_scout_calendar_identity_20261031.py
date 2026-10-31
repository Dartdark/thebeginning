"""Date-only audit of SSRN6818821's calendar descriptions. NO price reads/returns.

Weekday calendars are provisional, not certified NYSE/CME holiday calendars.
This audits a prose coincidence claim, not the paper's code or economic result.
"""
import calendar
import datetime as dt
import json
from pathlib import Path


def audit():
    rows = []
    for year in range(2018, 2023):
        for month in (3, 6, 9, 12):
            fridays = [dt.date(year, month, day) for day in range(1, calendar.monthrange(year, month)[1] + 1)
                       if dt.date(year, month, day).weekday() == 4]
            qend = dt.date(year, month, calendar.monthrange(year, month)[1])
            while qend.weekday() > 4:
                qend -= dt.timedelta(days=1)
            rows.append({"year": year, "month": month, "third_friday": fridays[2].isoformat(),
                         "last_friday": fridays[-1].isoformat(),
                         "provisional_weekday_quarter_end": qend.isoformat(),
                         "qend_is_third_friday": qend == fridays[2],
                         "last_friday_is_third_friday": fridays[-1] == fridays[2]})
    return {"scope": "calendar arithmetic only; no outcomes or strategy definition", "years": [2018, 2022],
            "quarter_rows": len(rows),
            "provisional_quarter_end_third_friday_coincidences": sum(r["qend_is_third_friday"] for r in rows),
            "june_last_friday_third_friday_coincidences": sum(r["last_friday_is_third_friday"] for r in rows if r["month"] == 6),
            "limitations": "Weekday endpoints only, not holiday-adjusted official calendars. Does not inspect author code, refute overlap with daily LETF, or measure alpha.",
            "rows": rows}


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "outputs/codex_scout_calendar_identity_20261031"
    out.mkdir(parents=True, exist_ok=True)
    (out / "calendar_audit.json").write_text(json.dumps(audit(), indent=2) + "\n")
    print(json.dumps({k: v for k, v in audit().items() if k != "rows"}, indent=2))
