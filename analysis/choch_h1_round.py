"""Hourly 2-bar CHoCH, one bounded round (pre-registration: checks/candidates/choch_h1/PREREG.md, commit 92b2706).
Signal engine = Codex's frozen `codex_choch4h.signals` (copied verbatim below, radius 2) on CT clock-hour bars of our own
24-hour data (g24 / ge). Variants B0 (2R target), V1 (no target, out 15:58), V2 (break-even at +1R, out 15:58),
V3 (B0 on the Overnight Bias side only), V4 (B0 on ES).
  python3 analysis/choch_h1_round.py [SCRATCH_DIR] [design | holdout]
design  : 2018-2022 only, gates, writes analysis/outputs/choch_h1_round/design.json
holdout : 2023-2026 only for the variants that passed the design gate (refuses otherwise)
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid import _walk
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "design"
OUT = "analysis/outputs/choch_h1_round"
# targets fill only on a 1-point trade-through (NQ and ES both: 4 ticks)
SPEC = {"NQ": dict(pv=20.0, comm=7.25, tick=0.25, through=1.0), "ES": dict(pv=50.0, comm=5.0, tick=0.25, through=1.0)}


def signals(bars, radius):
    """Codex codex_choch4h.signals (codex/work), verbatim. Pivot values become usable only on their confirmation bar."""
    history, highs, lows, out = [], [], [], []
    trend, previous = 0, None
    consumed = set()
    for b in bars:
        if not b['valid']:
            history, highs, lows, trend, previous = [], [], [], 0, None
            continue
        history.append(b)
        changed = False
        if len(history) >= 2 * radius + 1:
            window = history[-(2 * radius + 1):]
            pivot = window[radius]
            others = window[:radius] + window[radius + 1:]
            if all(pivot['high'] > x['high'] for x in others):
                highs.append((pivot['end'], pivot['high']))
                changed = True
            if all(pivot['low'] < x['low'] for x in others):
                lows.append((pivot['end'], pivot['low']))
                changed = True
        if changed and len(highs) >= 2 and len(lows) >= 2:
            if highs[-1][1] > highs[-2][1] and lows[-1][1] > lows[-2][1]:
                trend = 1
            elif highs[-1][1] < highs[-2][1] and lows[-1][1] < lows[-2][1]:
                trend = -1
        side = 0
        if previous is not None and highs and lows:
            if trend == 1 and previous >= lows[-1][1] and b['close'] < lows[-1][1]:
                side, stop, broken = -1, highs[-1][1], lows[-1][0]
            elif trend == -1 and previous <= highs[-1][1] and b['close'] > highs[-1][1]:
                side, stop, broken = 1, lows[-1][1], highs[-1][0]
            if side and (side, broken) not in consumed:
                out.append(dict(signal=b['end'], close=b['close'], side=side,
                                stop=stop, broken_pivot=broken, radius=radius))
                consumed.add((side, broken))
                trend = side
        previous = b['close']
    return pd.DataFrame(out, columns=['signal', 'close', 'side', 'stop', 'broken_pivot', 'radius'])


def hourly_bars(g):
    """CT clock-hour bars over the CME session from 1-minute columns (column j closes at 00:00 + j min). An hour with
    no minute at all inside the expected session is a data hole (resets the structure); outside it is skipped."""
    h, l, c = g.h.ravel(), g.l.ravel(), g.c.ravel()
    dow = pd.DatetimeIndex(g.ts).dayofweek.to_numpy()
    bars = []
    for end in range(60, len(c), 60):
        row, m = divmod(end, 1440)
        if m == 0: row, m = row - 1, 1440                 # the hour closing at midnight belongs to the previous date
        d = dow[row]
        session = not ((960 < m <= 1020) or d == 5 or (d == 4 and m > 960) or (d == 6 and m <= 1020))
        seg = c[end - 59:end + 1]
        have = ~np.isnan(seg)
        if not have.any():
            if session: bars.append(dict(end=end, valid=False))
            continue
        last = end - 59 + int(np.flatnonzero(have)[-1])
        bars.append(dict(end=end, valid=True, high=float(np.nanmax(h[end - 59:end + 1])),
                         low=float(np.nanmin(l[end - 59:end + 1])), close=float(c[last])))
    return bars


def onb_side(g, row):
    """Overnight Bias: 08:30 open vs the 23:00 (previous date) -> 08:30 range: top third +1, bottom third -1, else 0."""
    hi = np.nanmax(np.r_[g.h[row - 1, 1381:], g.h[row, :511]]); lo = np.nanmin(np.r_[g.l[row - 1, 1381:], g.l[row, :511]])
    op = g.o[row, 511]
    if not np.isfinite(op) or not np.isfinite(hi) or hi <= lo: return 0
    pos = (op - lo) / (hi - lo)
    return 1 if pos >= 2 / 3 else (-1 if pos <= 1 / 3 else 0)


def ledger(g, ev, spec, mode, onb=False, years=(2018, 2022)):
    o, h, l, c = (getattr(g, k).ravel() for k in "ohlc")
    normal = set(g.trading.tolist())
    rows, blocked = [], -1
    for e in ev.to_dict("records"):
        s = int(e["signal"]); row, m = divmod(s, 1440)
        if row not in normal or not (540 <= m <= 840): continue                    # signal closes 09:00-14:00 CT
        yr = int(str(g.dates[row])[:4])
        if not (years[0] <= yr <= years[1]): continue
        if np.isnan(g.c[row, 900:915]).all(): continue                              # early close (no 15:00-15:15 bars): skip
        deadline = row * 1440 + 958                                                 # flatten at the OPEN of 15:58
        j0 = s + 2
        while j0 < deadline and np.isnan(o[j0]) and j0 < s + 7: j0 += 1         # next print within 5 minutes
        if j0 <= blocked or j0 >= deadline or np.isnan(o[j0]): continue
        side, stop = int(e["side"]), float(e["stop"])
        if onb and onb_side(g, row) != side: continue
        entry = float(o[j0]); risk = side * (entry - stop)
        if risk <= 0: continue
        far = entry + side * 1e9
        if mode == "B0":
            end, px, kind, _ = _walk(o, h, l, c, j0, deadline - 1, side, stop, entry + side * 2 * risk, spec["through"])
        elif mode == "V1":
            end, px, kind, _ = _walk(o, h, l, c, j0, deadline - 1, side, stop, far, spec["through"])
        else:   # V2: walk to a +1R touch (no trade-through needed to MOVE a stop), then stop at entry from the next bar
            end, px, kind, _ = _walk(o, h, l, c, j0, deadline - 1, side, stop, entry + side * risk, 0.0)
            if kind == 1:
                if end + 1 <= deadline - 1:
                    end, px, kind, _ = _walk(o, h, l, c, end + 1, deadline - 1, side, entry, far, spec["through"])
                else: kind = 2
        if kind == 2:                                                               # time exit at the 15:58 open
            px = o[deadline] if np.isfinite(o[deadline]) else c[deadline - 1]; end = deadline
        slip = spec["tick"] * (1 + (kind != 1))                                     # entry + stop / time exit
        net = (side * (px - entry) - slip) * spec["pv"] - spec["comm"]
        blocked = int(end)
        rows.append(dict(date=int(g.dates[row]), year=yr, side=side, entry_t=m, entry=entry, stop=stop, risk=risk,
                         exit=float(px), kind=int(kind), net=net))
    return pd.DataFrame(rows)


def summarize(t, label, days):
    d = t.groupby("date").net.sum().reindex(days, fill_value=0.0)
    p = M.perf(d.values, t.net.values)
    tt = t.net.mean() / t.net.std() * np.sqrt(len(t)) if len(t) > 1 else np.nan
    yrs = t.groupby("year").net.sum()
    out = dict(name=label, trades=len(t), net=round(t.net.sum()), per_trade=round(t.net.mean(), 1), t=round(tt, 2),
               pf=round(p["profit_factor"], 2), win=round(p["win"], 3), sharpe=round(p["sharpe"], 2), sortino=round(p["sortino"], 2),
               calmar=round(p["calmar"], 2), ulcer=round(p["ulcer"], 2), max_dd=round(p["max_dd"]),
               years_pos=int((yrs > 0).sum()), by_year={int(k): round(v) for k, v in yrs.items()})
    for sd, nm in ((1, "long"), (-1, "short")):
        x = t[t.side == sd].net
        out[nm] = dict(n=len(x), net=round(x.sum()), t=round(x.mean() / x.std() * np.sqrt(len(x)), 2) if len(x) > 1 else None,
                       pf=round(x[x > 0].sum() / -x[x < 0].sum(), 2) if (x < 0).any() else None)
    return out


def gate(s):
    return s["trades"] >= 100 and s["net"] > 0 and s["t"] >= 2.0 and s["pf"] >= 1.25 and s["years_pos"] >= 4


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    g = pickle.load(open(SP + "g24.pkl", "rb")); ge = pickle.load(open(SP + "ge.pkl", "rb"))
    evn = signals(hourly_bars(g), 2); eve = signals(hourly_bars(ge), 2)
    print(f"raw hourly signals: NQ {len(evn)}, ES {len(eve)}")
    runs = {"B0": (g, evn, SPEC["NQ"], "B0", False), "V1": (g, evn, SPEC["NQ"], "V1", False),
            "V2": (g, evn, SPEC["NQ"], "V2", False), "V3": (g, evn, SPEC["NQ"], "B0", True),
            "V4": (ge, eve, SPEC["ES"], "B0", False)}
    if MODE == "design":
        res = {}
        for k, (gg, ev, sp, md, onb) in runs.items():
            t = ledger(gg, ev, sp, md, onb, (2018, 2022)); t.to_csv(f"{OUT}/{k}_design_trades.csv", index=False)
            days = [int(x) for x in gg.dates[gg.trading] if 20180101 <= x <= 20221231]
            s = summarize(t, k, days); s["pass"] = bool(gate(s)); res[k] = s
            print(f"{k}: n {s['trades']}  net ${s['net']:,} per NQ  avg ${s['per_trade']}  t {s['t']}  PF {s['pf']}  win {s['win']}  "
                  f"Sharpe {s['sharpe']}  Sortino {s['sortino']}  Calmar {s['calmar']}  Ulcer {s['ulcer']}  maxDD ${s['max_dd']:,}  "
                  f"yrs+ {s['years_pos']}/5  {s['by_year']}  L {s['long']}  S {s['short']}  PASS {s['pass']}")
        json.dump(res, open(f"{OUT}/design.json", "w"), indent=1)
    else:
        res = json.load(open(f"{OUT}/design.json"))
        ok = [k for k, v in res.items() if v["pass"]]
        if not ok: sys.exit("no design survivor: holdout stays closed (PREREG)")
        for k in ok:
            gg, ev, sp, md, onb = runs[k]
            t = ledger(gg, ev, sp, md, onb, (2023, 2026)); t.to_csv(f"{OUT}/{k}_holdout_trades.csv", index=False)
            days = [int(x) for x in gg.dates[gg.trading] if x >= 20230101]
            print("HOLDOUT", summarize(t, k, days))
