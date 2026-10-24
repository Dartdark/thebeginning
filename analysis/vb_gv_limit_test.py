"""VaultBreak NQ 'CircuitBreaker ApexLimit GVReader' + 'DailyATR GVWriter' (user's files, 2026-10-24) vs our Vault Break v1.
Rebuilt on the NQ 1-minute grid as 5-minute bars (close-stamped), sessions = calendar dates (Date <> Date[1]):
  DailyATR    = ALL-TIME average of each date's high - low (writer: RngSum / RngCnt, every date with bars, from the first
                loaded date = 2017-05 here; DailyATRLen 14 is only the minimum count). Variant 'roll14' = 14-date average.
  entry       5-min close > date open + 0.60 x DailyATR and > VWAP (from the date start), bar time 09:45-13:30, not
              10:55-11:59, max 3 ORDERS a day (an unfilled limit counts), flat; buy limit at close + 1 tick next bar.
  circuit     after 3 losing trades in a row (across days) the next signal is skipped, then the count restarts.
  exits       target limit entry + $1,000 (50 NQ pts; on MNQ the same code gives 500 pts); 'stop' = once a bar's low
              <= entry - 75 pts, sell limit at that bar's close next bar (re-placed every bar until filled: no stop
              order); VWAP exit: 2 closes in a row below VWAP -> limit at the close; from 15:50 -> limit at the close.
  Fills: limits at the price or better on touch (MultiCharts default); variant 'through' needs 1 tick through.
  Clock: 'ct' = times as written on an Exchange (CT) chart; 'et' = the chart on New York time (09:45 ET = 08:45 CT ...).
Costs: $7.25 per NQ round trip (limits: no slippage). Our VB v1 = the MultiCharts VB v1 list + 1 tick per market / stop fill.
  python3 analysis/vb_gv_limit_test.py > analysis/outputs/vb_gv_limit_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
import metrics as M, resampling as R, montecarlo as MC

PV, TICK, COMM = 20.0, 0.25, 7.25
NTRIAL = {"n": 0}


def bars5(g, shift=0):
    """5-minute bars per calendar row of the chart clock (shift minutes added to CT)."""
    k = 5; out = {}
    for c in "ohlcv":
        a = getattr(g, c).ravel()
        if shift: a = np.r_[np.full(shift, np.nan), a[:-shift]]
        x = np.r_[np.full(k - 1, np.nan), a, np.full((-(len(a) + k - 1)) % k, np.nan)].reshape(-1, k)
        with np.errstate(all="ignore"):
            y = {"h": np.nanmax(x, 1), "l": np.nanmin(x, 1), "v": np.nansum(x, 1),
                 "o": x[np.arange(len(x)), np.argmax(~np.isnan(x), 1)], "c": x[np.arange(len(x)), k - 1 - np.argmax(~np.isnan(x[:, ::-1]), 1)]}[c]
        out[c] = y[:g.D * 288]
    out["v"][np.isnan(out["c"])] = np.nan
    return out


def run(g, clock="ct", atr="alltime", mult=0.60, tp=50.0, sl=75.0, vw_bars=2, cb=True, blackout=True, max_tr=3,
        fill="touch", first=945, last=1330, flat=1550, start="2018-01-01", count=True):
    if count: NTRIAL["n"] += 1
    B = bars5(g, 60 if clock == "et" else 0); o, h, l, c, v = B["o"], B["h"], B["l"], B["c"], B["v"]
    N = len(c); idx = np.where(~np.isnan(c))[0]
    tm = (idx % 288) * 5; hhmm = (tm // 60) * 100 + tm % 60; row = idx // 288
    thr = TICK if fill == "through" else 0.0
    # date stats
    rows_u, first_i = np.unique(row, return_index=True)
    hi = np.maximum.reduceat(h[idx], first_i); lo = np.minimum.reduceat(l[idx], first_i); rng = hi - lo
    if atr == "alltime":
        cs = np.cumsum(np.where(rng > 0, rng, 0)); cn = np.cumsum(rng > 0)
        datr = np.where(cn >= 14, cs / np.maximum(cn, 1), 0)
    else:
        datr = pd.Series(np.where(rng > 0, rng, np.nan)).rolling(14, min_periods=14).mean().fillna(0).values
    atr_at = np.r_[0, datr[:-1]]                                  # known at the date's first bar
    ts = pd.DatetimeIndex(g.ts); st = ts.searchsorted(pd.Timestamp(start))
    trades = []; pos = 0; noise = np.nan; cum_pv = cum_v = 0.0; below = 0; dtr = 0; consec = 0; skip = False
    ent_lim = None; ex_lim = None; tp_px = 0.0; sl_px = 0.0; sl_b = False; eod = False; e = 0.0; e_i = 0; ri = -1
    for n, i in enumerate(idx):
        r = row[n]
        newday = r != (row[n - 1] if n else -1)
        # ---- orders working during this bar ----
        closed = None
        if pos == 0 and ent_lim is not None:
            if l[i] <= ent_lim - thr:
                e = min(o[i], ent_lim); pos = 1; e_i = i; tp_px = 0.0; sl_b = False; eod = False
            ent_lim = None
        elif pos == 1 and e_i != i:
            cand = [(p, k) for p, k in ((ex_lim, "limit_exit"), (tp_px if tp_px > 0 else None, "target"))
                    if p is not None and h[i] >= p + thr]
            xt = None
            if cand:                                              # both sell limits: the lower one is reached first
                p, k = min(cand); xt = (max(o[i], p), k)
            if xt is not None:
                x, kind = xt; net = (x - e) * PV - COMM; pos = 0; ex_lim = None; closed = net
                trades.append(dict(date=pd.Timestamp(g.ts[e_i // 288]).normalize(), entry_i=e_i, exit_i=i, entry=e, exit=x, kind=kind,
                                   net=net, mae=(np.nanmin(l[e_i:i + 1]) - e) * PV - COMM))
        # ---- bar close ----
        if newday:
            ri += 1; dtr = 0; below = 0; cum_pv = cum_v = 0.0
            if atr_at[ri] > 0: noise = o[i] + mult * atr_at[ri]
        if v[i] > 0: cum_pv += (h[i] + l[i] + c[i]) / 3 * v[i]; cum_v += v[i]
        vw = cum_pv / cum_v if cum_v > 0 else c[i]
        below = below + 1 if c[i] < vw else 0
        if closed is not None:
            if closed < 0: consec += 1
            else: consec = 0
            if cb and consec >= 3: skip = True
        t = hhmm[n]
        if pos == 1:
            if tp_px == 0: tp_px, sl_px = e + tp, e - sl
            if l[i] <= sl_px: sl_b = True
            if t >= flat: eod = True
        bl = blackout and 1055 <= t < 1200
        if (pos == 0 and r >= st and c[i] > noise and c[i] > vw and first <= t <= last and not bl and dtr < max_tr and atr_at[ri] > 0):
            if cb and skip: skip = False; consec = 0
            else: ent_lim = c[i] + TICK; dtr += 1
        ex_lim = c[i] if (pos == 1 and (below >= vw_bars or sl_b or eod)) else None
    return pd.DataFrame(trades)


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(t, nm, w=44):
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    t = t[t.date >= "2018-01-01"]; x = t.net.values; y = t.date.dt.year.values; by = pd.Series(x).groupby(y).sum()
    a, b = x[y < 2023], x[y >= 2023]
    return (f"   {nm:<{w}} n={len(x):4d} ${x.mean():5.0f} PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():4.0f} t {tst(a):4.1f} | 23+ ${b.mean():4.0f} t {tst(b):4.1f} | worst ${x.min():,.0f}")


def daily(t, days):
    return t.groupby("date").net.sum().reindex(days, fill_value=0.0)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= "2018-01-01"]
    vb = with_slippage(load_mc(g, REPORTS["VB"][0])); vb["date"] = pd.to_datetime(vb.date)
    base = run(g); base.to_csv("analysis/outputs/vb_gv_limit_trades.csv", index=False)
    print("\n1. Per 1 NQ, 2018 -> 2026-10:")
    print(line(vb, "our VB v1 (MultiCharts list, live)"))
    print(line(base, "new file as written (CT clock, touch fills)"))
    print("   exits:", base.kind.value_counts().to_dict(), f"| trades below -$1,500: {(base.net < -1500).sum()}, worst open ${base.mae.min():,.0f}")
    print("   by year new :", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   by year VB v1:", vb[vb.date >= "2018"].groupby(vb.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("\n2. Variants:")
    V = {"ET clock (chart on New York time)": dict(clock="et"), "fills 1 tick through": dict(fill="through"),
         "ET + through": dict(clock="et", fill="through"), "14-date ATR (not all-time)": dict(atr="roll14"),
         "14-date ATR, ET": dict(atr="roll14", clock="et"), "no circuit breaker": dict(cb=False), "no blackout": dict(blackout=False),
         "VWAP exit off": dict(vw_bars=999), "MNQ as coded (target 500 / 'stop' 750 pts)": dict(tp=500.0, sl=750.0),
         "noise 0.30": dict(mult=0.30), "noise 0.45": dict(mult=0.45), "noise 0.75": dict(mult=0.75)}
    out = {}
    for nm, kw in V.items():
        out[nm] = t = run(g, **kw); print(line(t, nm))
    a = base.groupby("date").net.sum(); b = vb[vb.date >= "2018"].groupby("date").net.sum()
    both = a.index.intersection(b.index)
    print(f"\n3. Overlap with VB v1: new trades on {len(a)} days, VB v1 on {len(b)}, both {len(both)}; daily corr "
          f"{np.corrcoef(daily(base, days), daily(vb, days))[0, 1]:+.2f}")
    print("\n4. Metrics per 1 NQ (daily):")
    rows = {}
    for nm, t in (("VB v1", vb), ("new", base), ("new ET", out["ET clock (chart on New York time)"])):
        dd = daily(t, days)
        for per, s in (("2018-26", "2018-01-01"), ("2023+", "2023-01-01")):
            rows[f"{nm} {per}"] = (dd[dd.index >= s], t[t.date >= s].set_index("date").net)
    print(M.table(rows))
    b_, p_ = R.report({"new 2023+": daily(base, days)[days >= "2023"], "VB v1 2023+": daily(vb, days)[days >= "2023"]}, limits=(5000, 10000, 20000))
    print(b_); print(p_)
    print("\n   Monte Carlo at 1 MNQ:")
    print(MC.report(base.net.values, daily=daily(base, days).values, size=0.1, label="new VB 1 MNQ"))
    print(MC.report(vb[vb.date >= "2018"].net.values, daily=daily(vb, days).values, size=0.1, label="VB v1 1 MNQ"))
    print(f"\n   trials {NTRIAL['n']}; t threshold {M.t_threshold(NTRIAL['n']):.2f}; deflated Sharpe (new) "
          f"{M.deflated_sharpe(daily(base, days).values, NTRIAL['n']):.2f}")
