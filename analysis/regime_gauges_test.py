"""Regime gauges side by side (user, 2026-10-25): the macro cycle checklist of the user's PDF 'application_1' (Expansion / Peak /
Recession / Recovery + growth x inflation quadrants) vs a daily volatility / trend gauge, as sizing rules on our 17-piece
personal book (analysis/personal_portfolio.py, 1 micro each, 2018-2026).

PRE-REGISTERED (written before any result was looked at; nothing below is tuned):
  Momentum cluster = VaultBreak, DualThrust, RelativeStrength (the pieces named in the 2026-10-25 plan review).
  Design half 2018-2022, holdout 2023-2026. A rule passes only if it raises return / max drawdown AND does not lower
  Sharpe, in BOTH halves.
  Macro gauge, monthly, from data up to the prior month end. FRED is not reachable from this container, so the checklist
  uses market stand-ins (data/macro_proxies_daily.csv, Yahoo): yield curve = 10-year (TNX) - 3-month (IRX); Fed policy =
  6-month change in the 3-month bill; credit = HYG / IEF ratio; growth = copper (HG=F); inflation = TIP / IEF ratio.
  The PDF's unemployment, core PCE, ISM and balance-sheet rows are left out. Votes (one per indicator):
    curve:  <= 0.25 -> Peak; 3-month change >= +0.5 with bills falling -> Recession; >= 1.5 -> Recovery; else Expansion
    Fed:    6-month bill change <= -0.5 -> Recession; >= +0.25 -> Expansion, or Peak if bills are within 0.25 of their
            3-year high; flat and bills < 0.5 -> Recovery; flat otherwise -> Peak if bills > 3.0 else Expansion
    credit: HYG/IEF 3-month change < -5% -> Recession; -5% .. -1% -> Peak; > +3% with the 12-month change < 0 ->
            Recovery; else Expansion
    growth: copper 6-month change < -10% -> Recession; 6-month > 0 but 3-month < 0 -> Peak; 6-month < 0 but 3-month > 0
            -> Recovery; else Expansion
    inflation (TIP/IEF 6-month change): > +2% -> Peak; < -2% -> Recession; 0 .. 2% -> Expansion; -2% .. 0 -> Recovery
  Regime = most votes; 'transition' when the top regime has <= 2 of the 5 votes (the PDF: 3 or fewer of 7).
  Quadrant: growth = sign of copper's 6-month change, inflation = sign of TIP/IEF's 6-month change.
    M1 (the PDF's own rule): transition month -> whole book at half size.
    M2: Peak or Recession month -> momentum cluster at half size.
    M3: Stagflation or Deflationary-bust quadrant -> momentum cluster at half size.
  Volatility / trend gauge, daily, from the prior session's close:
    V1: VIX prior close < 15 -> momentum cluster at half size.
    V2: trend-day rate (share of the last 20 NQ RTH sessions with |close - open| / range >= 0.6) in the bottom third of its
        own trailing 252-session values -> momentum cluster at half size.
    V3: V1 or V2.
  Also reported (descriptive, not rules): each piece's average $ a day by macro regime and by VIX bucket.
  python3 analysis/regime_gauges_test.py [SCRATCH_DIR] > analysis/outputs/regime_gauges_test_output.txt
"""
import sys, io, pickle, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MOM = ["VaultBreak", "DualThrust", "RelativeStrength"]
REG = ["Expansion", "Peak", "Recession", "Recovery"]

with contextlib.redirect_stdout(io.StringIO()):
    gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
P = gg["P"].copy(); days = P.index

# ---------------- macro gauge (monthly, prior month end) ----------------
X = pd.read_csv("data/macro_proxies_daily.csv", parse_dates=["date"]).set_index("date").ffill()
m = X.resample("ME").last()
curve = m.TNX - m.IRX; bills = m.IRX; hyg = m.HYG / m.IEF; cu = m["HG=F"]; inf = m.TIP / m.IEF
ch = lambda s, k: s / s.shift(k) - 1


def votes(i):
    v = []
    c, dc, db6 = curve.iloc[i], curve.iloc[i] - curve.iloc[i - 3], bills.iloc[i] - bills.iloc[i - 6]
    v.append("Peak" if c <= 0.25 else "Recession" if (dc >= 0.5 and bills.iloc[i] < bills.iloc[i - 3]) else "Recovery" if c >= 1.5 else "Expansion")
    hi3 = bills.iloc[max(0, i - 36):i + 1].max()
    if db6 <= -0.5: v.append("Recession")
    elif db6 >= 0.25: v.append("Peak" if bills.iloc[i] >= hi3 - 0.25 else "Expansion")
    elif bills.iloc[i] < 0.5: v.append("Recovery")
    else: v.append("Peak" if bills.iloc[i] > 3.0 else "Expansion")
    h3, h12 = ch(hyg, 3).iloc[i], ch(hyg, 12).iloc[i]
    v.append("Recession" if h3 < -0.05 else "Peak" if h3 < -0.01 else "Recovery" if (h3 > 0.03 and h12 < 0) else "Expansion")
    c6, c3 = ch(cu, 6).iloc[i], ch(cu, 3).iloc[i]
    v.append("Recession" if c6 < -0.10 else "Peak" if (c6 > 0 and c3 < 0) else "Recovery" if (c6 < 0 and c3 > 0) else "Expansion")
    i6 = ch(inf, 6).iloc[i]
    v.append("Peak" if i6 > 0.02 else "Recession" if i6 < -0.02 else "Expansion" if i6 >= 0 else "Recovery")
    return v


rows = []
for i in range(36, len(m)):
    v = votes(i); cnt = pd.Series(v).value_counts(); top = cnt.index[0]
    g_up, i_up = ch(cu, 6).iloc[i] > 0, ch(inf, 6).iloc[i] > 0
    quad = {(True, False): "Goldilocks", (True, True): "Reflation", (False, False): "Deflationary bust", (False, True): "Stagflation"}[(g_up, i_up)]
    rows.append(dict(month=m.index[i], regime=top if cnt.iloc[0] >= 3 else "transition", top=top, nvotes=int(cnt.iloc[0]), quad=quad))
MR = pd.DataFrame(rows).set_index("month")
# a month's label applies to the NEXT month's trading days (known at the prior month end)
lab = MR.shift(1).reindex(pd.date_range(MR.index[0], days[-1] + pd.offsets.MonthEnd(0), freq="ME")).ffill()
dm = days.to_period("M").to_timestamp("M")
regime = pd.Series(lab.regime.reindex(dm).to_numpy(), index=days); quad = pd.Series(lab.quad.reindex(dm).to_numpy(), index=days)

# ---------------- vol / trend gauge (daily, prior close) ----------------
vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE
vix_prev = vix.shift(1).reindex(days, method="ffill")
g = pickle.load(open(SP + "g24.pkl", "rb")); J0, J1 = jof(831), jof(1500)
tr = g.trading; o, c = g.o[tr, J0], g.c[tr, J1]
with np.errstate(all="ignore"):
    hi, lo = np.nanmax(g.h[tr, J0:J1 + 1], 1), np.nanmin(g.l[tr, J0:J1 + 1], 1)
trend = pd.Series(np.abs(c - o) / (hi - lo) >= 0.6, index=pd.DatetimeIndex(g.ts[tr])).astype(float)
rate = trend.rolling(20).mean().shift(1)                                  # known before the session
pct = rate.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean() if len(w) > 1 else np.nan, raw=True)
low_trend = (pct < 1 / 3).reindex(days).fillna(False)
quiet = (vix_prev < 15).fillna(False)


def book(scale_all=None, scale_mom=None):
    Q = P.copy()
    if scale_all is not None: Q = Q.mul(np.where(scale_all, 0.5, 1.0), axis=0)
    if scale_mom is not None:
        for k in MOM: Q[k] = Q[k] * np.where(scale_mom, 0.5, 1.0)
    return Q.sum(axis=1)


def stats(x):
    e = x.cumsum(); dd = -(e - e.cummax()).min(); yr = x.sum() / (len(x) / 252)
    return yr, x.mean() / x.std() * np.sqrt(252), dd, yr / dd if dd else np.nan


RULES = {"base (no gauge)": dict(),
         "M1 macro transition -> book x0.5": dict(scale_all=(regime == "transition").to_numpy()),
         "M2 macro Peak/Recession -> momentum x0.5": dict(scale_mom=regime.isin(["Peak", "Recession"]).to_numpy()),
         "M3 stagflation/bust quadrant -> momentum x0.5": dict(scale_mom=quad.isin(["Stagflation", "Deflationary bust"]).to_numpy()),
         "V1 VIX < 15 -> momentum x0.5": dict(scale_mom=quiet.to_numpy()),
         "V2 low trend-day rate -> momentum x0.5": dict(scale_mom=low_trend.to_numpy()),
         "V3 V1 or V2 -> momentum x0.5": dict(scale_mom=(quiet | low_trend).to_numpy())}

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    print("\n1. Macro gauge, months by label (2018-2026):", regime.groupby(regime.index.to_period("M")).first().value_counts().to_dict(),
          "| quadrants:", quad.groupby(quad.index.to_period("M")).first().value_counts().to_dict())
    print("   label by year (most common):", {y: s.value_counts().index[0] for y, s in regime.groupby(regime.index.year)})
    print(f"   vol gauge: VIX<15 on {quiet.mean():.0%} of days; low trend-day rate on {low_trend.mean():.0%}; either {(quiet | low_trend).mean():.0%}")
    print("\n2. Rules on the 17-piece book ($ a year, Sharpe, max DD, return/DD), design 2018-22 | holdout 2023-26 | pass?")
    base = {}
    for nm, kw in RULES.items():
        x = book(**kw); out = []
        for a, b in (("2018-01-01", "2022-12-31"), ("2023-01-01", "2026-12-31")):
            out.append(stats(x[(x.index >= a) & (x.index <= b)]))
        if nm.startswith("base"): base = out
        ok = all(o_[3] > b_[3] and o_[1] >= b_[1] - 1e-9 for o_, b_ in zip(out, base)) if not nm.startswith("base") else None
        print(f"   {nm:<46} " + " | ".join(f"${o_[0]:>7,.0f} Sh {o_[1]:.2f} DD ${o_[2]:>6,.0f} R/DD {o_[3]:4.1f}" for o_ in out)
              + ("" if ok is None else f" | {'PASS' if ok else 'fail'}"))
    print("\n3. Descriptive: average $ a day per piece by macro regime (2018-2026):")
    print(P.groupby(regime).mean().T.round(1).to_string())
    print("\n   by quadrant:"); print(P.groupby(quad).mean().T.round(1).to_string())
    print("\n   by trend-day-rate tercile (low / mid / high, prior 20 sessions vs the trailing year):")
    terc = pd.cut(pct.reindex(days), [-0.01, 1 / 3, 2 / 3, 1.01], labels=["low", "mid", "high"])
    print(P.groupby(terc).mean().T.round(1).to_string())
    print("\n   days per label:", regime.value_counts().to_dict(), "| trend terciles:", terc.value_counts().to_dict())
