"""CL forced flows, round 2: the testable parts of the user's AI chat on crude-oil forced flows (2026-10-14).

The chat (pasted 2026-10-14) lists: the monthly contract roll, margin-call / stop-run cascades after EIA, commercial
producer hedging at round numbers, USO / index-fund roll windows, options-expiry pinning, and a "golden hour" from
the 9:00 ET pit open to the 11:30 ET "London fix / European close". Already tested here (not repeated): the GSCI / BCOM
roll windows and the business-day 1-4 roll short (analysis/s_rank_cl_round1_test.py, cl_forced_flows_test.py), EIA
follow / fade / pre-release drift, settlement 13:30 CT, options-expiry pinning (none on CL). Not testable with 1-minute
OHLCV: DOM icebergs, CVD / footprint delta, calendar-spread z-scores (needs the second month). New tests:
  A. The Platts Market-on-Close window, 16:00-16:30 London (where physical crude cargoes and Brent / Dubai are
     benchmarked; the chat's "London fix" for oil): 10:00-10:30 CT normally, 11:00-11:30 CT in the 3-4 DST-mismatch
     weeks a year (natural experiment: a window-driven effect moves with the London clock). Measures: the window's
     move, the 30 minutes before, after (window end -> 13:29); trades: follow the pre-window move into the window,
     follow / fade the window to 13:29.
  B. EIA stop-run sweep fade (chat setup 2): on EIA days, if a 1-minute bar between 9:32 and 9:45 CT trades beyond the
     8:00 -> 9:29 range and closes back inside it, fade at the next open; stop 3 ticks beyond the sweep extreme;
     target the pre-release midpoint; out 11:00 CT. Placebo: the same rule on non-EIA days.
  C. Producer / refiner hedging at round numbers (chat setup 3): first intraday touch (8:00-12:30 CT) of a $5 level
     from below -> short at the level (resting limit: filled when price trades 1 tick through), stop 12 ticks, target
     3R or 13:29; mirror long at $5 levels touched from above; also $1 levels. Placebo: levels offset by half a step.
  D. USO roll window (chat setup 1): USO's 4-day roll about two weeks before expiry (last trade - 10 .. - 7 business
     days): short the front 8:00 -> 13:29 and 9:30 -> 10:30 CT ("into the European close") vs other days.
Per CL, $7.25 + 1 tick per market / stop fill (no tick on limit fills). Design 2018-22, holdout 2023-26, picks by
design t; advance = t >= 2.5 and positive in both periods; full metrics for anything that advances.
  python3 analysis/cl_forced_flows_round2_test.py [SCRATCH_DIR]
"""
import sys, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from grid24 import jof
from cl_forced_flows_test import load
from forced_groups_round4_test import ct_of
from s_rank_cl_round1_test import Eng, tstat, line
import metrics as M, resampling as R

PV, TICK, COMM = 1000.0, 0.01, 7.25
SPLIT = pd.Timestamp("2023-01-01")
SURV = []


def show(x, nm, test=True):
    x = pd.Series(x).dropna(); s = line(x, nm, test=False); print(s)
    if test and len(x) >= 20:
        y = x.index.year; a, b = x[y < 2023].mean(), x[y >= 2023].mean(); t = tstat(x)
        if t >= 2.5 and a > 0 and b > 0: SURV.append((nm, x)); print("      <-- advances")


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    print(__doc__.split("\n")[0])
    cl = load("CL"); E = Eng(cl); ts = pd.DatetimeIndex(cl.ts); atr_all = cl.daily_atr(15)
    tr = cl.trading[ts[cl.trading] >= "2018-01-01"]; idx = ts[tr]; D = len(tr); atr = atr_all[tr]; base = tr * 1440
    full = cl.last_j[tr] >= jof(1500); cf = E.cf
    P = lambda t: cf[base + jof(t)]
    days = idx; dl = lambda x: x.groupby(x.index.normalize()).sum().reindex(days, fill_value=0.0)

    # ---------------- A. Platts window ----------------
    print("\nA. Platts Market-on-Close window (16:00-16:30 London)")
    w0 = ct_of(idx, 16, 0, "Europe/London"); mism = w0 != 1000
    print(f"   window start in CT: {pd.Series(w0).value_counts().to_dict()}")
    J0 = jof(w0); pick = lambda j: cf[base + j]
    win = (pick(J0 + 30) - pick(J0)) * PV; pre = (pick(J0) - pick(J0 - 30)) * PV; post = (P(1329) - pick(J0 + 30)) * PV
    for nm, s in (("window 30 min", win), ("30 min before", pre), ("after: window end -> 13:29", post)):
        s = pd.Series(s, index=idx)[full]
        print(line(s, f"   {nm}, all full days ($ per CL, before costs)", test=False))
    print("   natural experiment, mismatch days: the London-clock window vs the usual 10:00-10:30 CT")
    for nm, jj in (("London clock (11:00-11:30 CT)", J0), ("CT clock (10:00-10:30 CT)", np.full(D, jof(1000)))):
        s = pd.Series((pick(jj + 30) - pick(jj)) * PV, index=idx)[full & mism]
        print(f"      {nm}: avg ${s.mean():.0f}, |move| median ${s.abs().median():.0f}, t {tstat(s):.1f}, n {len(s)}")
    vol = pd.Series(np.abs(win), index=idx)[full]; base_vol = pd.Series(np.abs((pick(J0 - 60) - pick(J0 - 90)) * PV), index=idx)[full]
    print(f"   |window move| median ${vol.median():.0f} vs the half hour 90-60 min before ${base_vol.median():.0f}")
    sg_pre = np.sign(pick(J0) - pick(J0 - 30)); sg_win = np.sign(pick(J0 + 30) - pick(J0))
    for nm, side, e, x in (("follow the 30 min before into the window", sg_pre, J0 + 1, J0 + 30),
                           ("follow the window to 13:29", sg_win, J0 + 31, np.full(D, jof(1329))),
                           ("fade the window to 13:29", -sg_win, J0 + 31, np.full(D, jof(1329)))):
        for th in (0.0, 0.15):
            mv_ = np.abs(pick(J0) - pick(J0 - 30)) if "before" in nm else np.abs(pick(J0 + 30) - pick(J0))
            m = full & (mv_ >= th * atr)
            net, _ = E.run(base + e, base + x, np.where(m, side, 0), idx)
            show(net, f"{nm}, |move| >= {th} ATR")

    # ---------------- B. EIA sweep fade ----------------
    print("\nB. EIA stop-run sweep fade (9:32-9:45 CT, back inside the 8:00-9:29 range)")
    hol = USFederalHolidayCalendar().holidays("2017-12-01", "2026-12-31")
    wk = idx.to_period("W"); hol_wk = set(pd.DatetimeIndex(hol[hol.dayofweek <= 1]).to_period("W"))
    eia = (((idx.dayofweek == 2) & ~wk.isin(hol_wk)) | ((idx.dayofweek == 3) & wk.isin(hol_wk))) & full
    H, L, O, C = cl.h, cl.l, cl.o, cl.c
    def sweep(rows_mask, tgt_mode):
        out = {}
        for i in np.where(rows_mask)[0]:
            d = tr[i]; rh = np.nanmax(H[d, jof(801):jof(929) + 1]); rl = np.nanmin(L[d, jof(801):jof(929) + 1])
            if not np.isfinite(rh): continue
            mid = (rh + rl) / 2
            for j in range(jof(932), jof(945) + 1):
                if np.isnan(C[d, j]): continue
                s = 0
                if L[d, j] < rl and C[d, j] > rl: s, ext = 1, L[d, j]
                elif H[d, j] > rh and C[d, j] < rh: s, ext = -1, H[d, j]
                if s == 0: continue
                e = O[d, j + 1] + s * TICK
                if np.isnan(e): break
                sp = ext - s * 3 * TICK; tp = mid if tgt_mode == "mid" else None
                px = None
                for k in range(j + 1, jof(1100) + 1):
                    if np.isnan(H[d, k]): continue
                    if (L[d, k] <= sp) if s > 0 else (H[d, k] >= sp):
                        px = (min(O[d, k], sp) if s > 0 else max(O[d, k], sp)) - s * TICK; break
                    if tp is not None and ((H[d, k] >= tp) if s > 0 else (L[d, k] <= tp)) and (tp - e) * s > 0:
                        px = tp; break
                if px is None: px = cf[d * 1440 + jof(1100)] - s * TICK
                out[idx[i]] = (px - e) * s * PV - COMM
                break
        return pd.Series(out, dtype=float)
    for tm in ("mid", "time"):
        show(sweep(eia, tm), f"EIA days, target {'pre-release midpoint' if tm == 'mid' else 'none (out 11:00)'}")
        show(sweep(full & ~eia, tm), f"   placebo: non-EIA days, same rule", test=False)

    # ---------------- C. round numbers ----------------
    print("\nC. Round-number hedging walls (first touch 8:00-12:30 CT)")
    def round_trade(step, offset, side_mode):
        out = {}
        for i in np.where(full)[0]:
            d = tr[i]; o8 = O[d, jof(801)]
            if np.isnan(o8): continue
            if side_mode == "short":
                lvl = np.floor((o8 - offset) / step) * step + step + offset         # first level above the 8:00 open
            else:
                lvl = np.ceil((o8 - offset) / step) * step - step + offset          # first level below
            for j in range(jof(801), jof(1230) + 1):
                if np.isnan(H[d, j]): continue
                hit = (H[d, j] >= lvl + TICK) if side_mode == "short" else (L[d, j] <= lvl - TICK)
                if not hit: continue
                s = -1 if side_mode == "short" else 1
                e = lvl; sp = lvl - s * 12 * TICK; tp = lvl + s * 36 * TICK; px = None
                for k in range(j, jof(1329) + 1):
                    if np.isnan(H[d, k]): continue
                    if (L[d, k] <= sp) if s > 0 else (H[d, k] >= sp):
                        px = (sp if k == j else (min(O[d, k], sp) if s > 0 else max(O[d, k], sp))) - s * TICK; break
                    if k > j and ((H[d, k] >= tp) if s > 0 else (L[d, k] <= tp)): px = tp; break
                if px is None: px = cf[d * 1440 + jof(1329)] - s * TICK
                out[idx[i]] = (px - e) * s * PV - COMM
                break
        return pd.Series(out, dtype=float)
    for step in (5.0, 1.0):
        for sm in ("short", "long"):
            show(round_trade(step, 0.0, sm), f"${step:.0f} levels, {sm} at the first touch ({'from below' if sm == 'short' else 'from above'})")
            show(round_trade(step, step / 2, sm), f"   placebo: levels offset by ${step / 2:.2f}", test=False)

    # ---------------- D. USO roll window ----------------
    print("\nD. USO roll window (last trade - 10 .. - 7 business days): short the front")
    bd = pd.DatetimeIndex(sorted(set(idx[cl.last_j[tr] >= jof(1329)])))
    ltd = []
    for m in pd.period_range("2018-01", "2026-11", freq="M"):
        k = bd.searchsorted(pd.Timestamp(m.year, m.month, 25), side="right") - 1
        if 3 <= k < len(bd): ltd.append(bd[k - 3])
    uso = set()
    for Lt in ltd:
        k = bd.searchsorted(Lt)
        for q in range(7, 11):
            if k - q >= 0: uso.add(bd[k - q])
    is_uso = idx.isin(list(uso)) & full
    for nm, a, b in (("8:00 -> 13:29", 801, 1329), ("9:30 -> 10:30 ('into the European close')", 931, 1030)):
        net, _ = E.run(base + jof(a), base + jof(b), np.where(is_uso, -1, 0), idx)
        show(net, f"USO roll days, short {nm}")
        net2, _ = E.run(base + jof(a), base + jof(b), np.where(full & ~is_uso, -1, 0), idx)
        show(net2, f"   placebo: other days, short {nm}", test=False)

    print(f"\nAdvancing: {len(SURV)}")
    for nm, x in SURV:
        print(f"\n== {nm}")
        print(M.table({nm[:40]: (dl(x), x)}))
        b_, p_ = R.report({nm[:40] + ", 2023+": dl(x)[days >= SPLIT]}, n=3000); print(b_); print(p_)
