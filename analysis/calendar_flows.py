"""Calendar-flow effects on NQ/ES day sessions (2018-2026).

Month-end:
  - turn of the month (Ariel 1987; Lakonishok & Smidt 1988; McConnell & Xu 2008):
    returns concentrate from the last trading day through the first 3 days
  - month-end rebalancing (Etula et al. 2020 "Dash for Cash"; Harvey, Mazzoleni &
    Melone 2025): after a strong month for stocks, balanced funds sell equities in
    the last days of the month (and buy after a weak month); here the month-to-date
    index return stands in for stocks-vs-bonds
Options expiration (monthly options expire the third Friday; Thursday if that
Friday is a holiday):
  - expiration-week strength / week-after weakness
  - expiration-day pinning: dealer hedging dampens moves (intraday reversal)

calendar(g) returns one row per trading row with the flags; session_returns()
gives the 8:30-15:00 move and the 17:00 (previous evening) -> 15:00 move.
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
from grid24 import jof


# third Fridays on which the stock market was closed (options expired Thursday)
NYSE_CLOSED_THIRD_FRIDAYS = ["2019-04-19", "2022-04-15", "2025-04-18", "2026-06-19"]


def calendar(g):
    tr = g.trading
    ts = pd.DatetimeIndex(g.ts[tr])
    df = pd.DataFrame(dict(row=tr, date=ts))
    ym = ts.year * 100 + ts.month
    df["tdm"] = df.groupby(ym).cumcount() + 1                         # trading day of month (1 = first)
    df["tdm_end"] = df.groupby(ym)["tdm"].transform("max") - df["tdm"] + 1   # 1 = last
    # third Friday of the month (calendar), expiration = last trading day on or before it
    third_fri = []
    for y, m in zip(ts.year, ts.month):
        d1 = pd.Timestamp(y, m, 1)
        first_fri = d1 + pd.Timedelta(days=(4 - d1.dayofweek) % 7)
        third_fri.append(first_fri + pd.Timedelta(days=14))
    df["third_fri"] = third_fri
    closed = pd.to_datetime(NYSE_CLOSED_THIRD_FRIDAYS)
    eff = df.third_fri.where(~df.third_fri.isin(closed), df.third_fri - pd.Timedelta(days=1))
    ok = (df.date <= eff) & (eff <= df.date.max())       # skip a month whose expiration is past the data
    exp = df[ok].groupby(ym[ok]).date.max()
    df["opex"] = df.date.isin(exp.values)
    df["opex_date"] = pd.Series(ym).map(exp).values
    df["days_to_opex"] = [(np.busday_count(d.date(), o.date()) if pd.notna(o) else np.nan)
                          for d, o in zip(df.date, df.opex_date)]
    df["opex_week"] = (df.date >= df.opex_date - pd.Timedelta(days=4)) & (df.date <= df.opex_date)
    df["week_after"] = (df.date > df.opex_date) & (df.date <= df.opex_date + pd.Timedelta(days=7))
    df["quarterly"] = df.opex & ts.month.isin([3, 6, 9, 12])
    return df.set_index("row")


def session_returns(g, pv):
    """$ per contract: RTH 8:30 open -> 15:00 close, and Globex day 17:00 previous
    evening -> 15:00 (one Apex trading day), plus the month-to-date return to the
    previous close (for the rebalancing signal)."""
    tr = g.trading
    C = pd.DataFrame(g.c).ffill(axis=1).to_numpy()
    rth = (C[tr, jof(1500)] - g.o[tr, jof(831)]) * pv
    eve = C[tr - 1, jof(1700)]
    glob = (C[tr, jof(1500)] - eve) * pv
    cl = pd.Series(C[tr, jof(1500)], index=pd.DatetimeIndex(g.ts[tr]))
    ym = cl.index.year * 100 + cl.index.month
    prev_month_close = cl.groupby(ym).transform("first").shift(0)
    # month-to-date return known at the previous close: close(t-1) / last close of previous month - 1
    last_prev = cl.groupby(ym).last().shift(1)
    mtd = (cl.shift(1) / pd.Series(ym, index=cl.index).map(last_prev) - 1).to_numpy()
    return pd.DataFrame(dict(rth=rth, glob=glob, mtd=mtd), index=tr)
