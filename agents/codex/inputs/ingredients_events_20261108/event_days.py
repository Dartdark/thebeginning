"""Scheduled-event days on NQ/ES (2018-2026), from papers cited in "151 Trading
Strategies":
  - Lucca & Moench (2015), The Pre-FOMC Announcement Drift: stock index returns
    are unusually high in the hours before scheduled FOMC announcements
  - Savor & Wilson (2013); Ai & Bansal (2018): returns on macro announcement days
    are higher than on other days

FOMC_DATES are the scheduled announcement days (13:00 CT statement), written from
the Fed's calendar; check_fomc() confirms each against the 13:00-13:10 CT
volatility spike in the 1-minute data. Macro release days (8:30 ET = 7:30 CT:
CPI, payrolls, PPI, retail sales, ...) are detected from the 7:30 CT bar's range
(known before the 8:30 CT open, so usable for day-session trades).
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
from grid24 import jof

FOMC_DATES = """
2018-01-31 2018-03-21 2018-05-02 2018-06-13 2018-08-01 2018-09-26 2018-11-08 2018-12-19
2019-01-30 2019-03-20 2019-05-01 2019-06-19 2019-07-31 2019-09-18 2019-10-30 2019-12-11
2020-01-29 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05 2020-12-16
2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15
2022-01-26 2022-03-16 2022-05-04 2022-06-15 2022-07-27 2022-09-21 2022-11-02 2022-12-14
2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01 2023-12-13
2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18
2025-01-29 2025-03-19 2025-05-07 2025-06-18 2025-07-30 2025-09-17 2025-10-29 2025-12-10
2026-01-28 2026-03-18 2026-04-29 2026-06-17 2026-07-29 2026-09-16
""".split()


def rows_of(g, dates):
    idx = pd.Series(np.arange(len(g.dates)), index=g.dates)
    d = pd.to_datetime(pd.Series(dates)).dt.strftime("%Y%m%d").astype(int)
    return idx.reindex(d).dropna().astype(int).to_numpy()


def bar_range(g, rows, start, end):
    """High-low range from the bar closing after `start` to the bar closing at `end` (CT)."""
    a, b = jof(start) + 1, jof(end)
    with np.errstate(all="ignore"):
        return np.nanmax(g.h[rows, a:b + 1], 1) - np.nanmin(g.l[rows, a:b + 1], 1)


def check_fomc(g):
    """Ratio of the 13:00-13:10 CT range on each FOMC date to its median on
    other trading days (a real announcement day is several times larger)."""
    f = rows_of(g, FOMC_DATES)
    other = np.setdiff1d(g.trading, f)
    base = np.nanmedian(bar_range(g, other, 1300, 1310))
    return pd.Series(bar_range(g, f, 1300, 1310) / base, index=g.ts[f])


def release_days(g, mult=3.0, lookback=20):
    """Trading rows whose 7:30-7:35 CT range is > mult x its median over the
    previous `lookback` days (an 8:30 ET data release)."""
    tr = g.trading
    r = pd.Series(bar_range(g, tr, 730, 735))
    base = r.rolling(lookback).median().shift(1)
    return tr[(r > mult * base).to_numpy()]
