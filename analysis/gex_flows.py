"""Dealer gamma (GEX) and dark-pool index (DIX) from SqueezeMetrics (data/DIX.csv:
date, S&P 500 close, DIX, GEX in $ of S&P delta change per 1% move), tested on
NQ/ES day sessions.

Research: Baltussen, Da, Lammers & Martens (2021, JFE) - intraday momentum is
driven by short-gamma hedging; Barbon, Beckmeyer, Buraschi & Moerke (SSRN 3925725) -
end-of-day momentum when dealer gamma is negative, reversal when positive;
Ni, Pearson, Poteshman & White (2021, RFS); SqueezeMetrics, "Gamma Exposure" (2017).

GEX and DIX are published after the close, so day d uses the values of the
previous trading day. GEX grows with the market, so it is ranked within the
previous 252 days (gex_rank 0..1); gex_neg marks negative GEX.
"""
import numpy as np
import pandas as pd


def load_dix(path="data/DIX.csv"):
    d = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    d["gex_rank"] = d["gex"].rolling(252, min_periods=120).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)
    d["dix_rank"] = d["dix"].rolling(252, min_periods=120).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)
    d["gex_neg"] = d["gex"] < 0
    return d


def features_for(g, d=None):
    """Previous trading day's GEX/DIX features for each trading row of grid g."""
    d = load_dix() if d is None else d
    dates = pd.DatetimeIndex(g.ts[g.trading])
    f = d[["gex", "gex_rank", "gex_neg", "dix", "dix_rank"]].shift(1)       # known before day d
    f = f.reindex(dates, method="ffill")
    f.index = g.trading
    return f
