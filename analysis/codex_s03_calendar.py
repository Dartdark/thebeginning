"""Deterministic cash-session calendar for the registered S03 reconstruction.

Known calendar dates only: never inspect today's future prices to decide
whether its earlier entries were eligible. Existing repo early-close guard
is reused, with NYSE full holidays/Good Friday and mourning dates explicit.
"""
from functools import lru_cache

import pandas as pd
from pandas.tseries.holiday import (AbstractHolidayCalendar, Holiday,
    USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay,
    USLaborDay, USThanksgivingDay, nearest_workday, sunday_to_monday)

try:
    from replica import is_early_close
except ImportError:
    from analysis.replica import is_early_close


class _CashHolidays(AbstractHolidayCalendar):
    rules = [Holiday("New Year", month=1, day=1, observance=sunday_to_monday),
        USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay,
        Holiday("Juneteenth", month=6, day=19, observance=nearest_workday,
                start_date=pd.Timestamp("2022-06-19")),
        Holiday("Independence Day", month=7, day=4, observance=nearest_workday),
        USLaborDay, USThanksgivingDay,
        Holiday("Christmas", month=12, day=25, observance=nearest_workday)]


@lru_cache(maxsize=32)
def _holidays(year):
    return set(_CashHolidays().holidays(f"{year}-01-01", f"{year}-12-31").normalize())


def calendar_status(date):
    d = pd.Timestamp(date).normalize()
    if d.dayofweek >= 5:
        kind, close, reason = "weekend", None, "weekend"
    elif d in (pd.Timestamp("2018-12-05"), pd.Timestamp("2025-01-09")):
        kind, close, reason = "holiday", None, "national mourning"
    elif d in _holidays(d.year):
        kind, close, reason = "holiday", None, "cash exchange holiday"
    elif is_early_close(d):
        kind, close, reason = "early", 12 * 60, "existing repo early-close calendar"
    else:
        kind, close, reason = "normal", 15 * 60, "normal cash session"
    return dict(kind=kind, cash_close_j=close, reason=reason)


def synthetic_checks():
    assert calendar_status("2021-12-31")["kind"] == "normal"  # NYSE stayed open before Saturday New Year
    assert calendar_status("2023-01-02")["kind"] == "holiday"
    assert calendar_status("2024-03-29")["kind"] == "holiday"  # Good Friday
    assert calendar_status("2021-06-18")["kind"] == "normal"  # no NYSE Juneteenth observance yet
    assert calendar_status("2022-06-20")["kind"] == "holiday"
    assert calendar_status("2025-01-09")["kind"] == "holiday"
    assert calendar_status("2024-11-29")["kind"] == "early"
    assert calendar_status("2025-07-03")["cash_close_j"] == 720
    assert calendar_status("2026-10-24")["kind"] == "weekend"
    return 9


if __name__ == "__main__":
    print("Calendar synthetic checks:", synthetic_checks())
