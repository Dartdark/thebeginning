"""IntradayMomentum_Signal_EN (user's MultiCharts file + report, 2026-10-25): Zarattini / Aziz / Barbon 'Beat the Market' noise area
on NQ / MNQ 30-minute RTH bars (CT), as the file's defaults run it:
  sigma(slot) = mean of |close(slot) / day open - 1| over the last 14 sessions (30-min slots, today excluded);
  UB = max(open, prior close) x (1 + sigma), LB = min(...) x (1 - sigma); VWAP from the 30-min bars ((H+L+C)/3 x volume);
  decisions at the 09:00 .. 14:30 closes: close > UB and > max(UB, VWAP) -> long next bar open (short mirror);
  exit when a 30-min close is beyond max(UB, VWAP) (StopMode 3) -> next bar open; ONE entry a day (MaxTradesPerDay 1);
  money stop $1,000 / target $500 on the WHOLE position at FixedQty 10 MNQ = 50 / 25 NQ points, intrabar on 1-minute bars
  (the Bar Magnifier the file makes mandatory); SetExitOnClose = out at the 15:00 close.
Per NQ (= 10 MNQ). Costs $7.25 + 1 tick per market / stop fill; the target is a limit (no slippage).
Variants: the paper's exits (no money stop / target), unlimited entries with reversal, LookBack 90 / VolMult 1.5, and the
paper's day filters NR4 / NR7 / Triangle (RTH daily ranges of completed days), each tested on the as-coded and the paper rule.
  python3 analysis/intraday_momentum_30m_test.py > analysis/outputs/intraday_momentum_30m_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R, montecarlo as MC

PV, TICK, COMM = 20.0, 0.25, 7.25
NTRIAL = {"n": 0}
g = pickle.load(open("scratch_data/g24.pkl", "rb"))
J0, J1 = jof(831), jof(1500)
tr = g.trading; tr = tr[~np.isnan(g.c[tr, J1]) & ~np.isnan(g.o[tr, J0])]
dts = pd.DatetimeIndex(g.ts[tr]); ND = len(tr)
ff = lambda a: np.array([pd.Series(r).ffill().bfill().to_numpy() for r in a])
O1, H1, L1, C1 = ff(g.o[tr, J0:J1 + 1]), ff(g.h[tr, J0:J1 + 1]), ff(g.l[tr, J0:J1 + 1]), ff(g.c[tr, J0:J1 + 1])
V1 = np.nan_to_num(g.v[tr, J0:J1 + 1])
# 30-minute bars: 13 per day, bar k covers minutes 30k .. 30k+29 (closes 09:00 .. 15:00)
O30 = O1[:, ::30]; C30 = C1[:, 29::30]
H30 = H1.reshape(ND, 13, 30).max(2); L30 = L1.reshape(ND, 13, 30).min(2); V30 = V1.reshape(ND, 13, 30).sum(2)
DO = O30[:, 0]; PC = np.r_[np.nan, C30[:-1, -1]]
VW = np.cumsum((H30 + L30 + C30) / 3 * V30, 1) / np.maximum(np.cumsum(V30, 1), 1)
mv = np.abs(C30 / DO[:, None] - 1)
dr = H30.max(1) - L30.min(1); dh, dl = H30.max(1), L30.min(1)
nr = lambda k: np.r_[np.zeros(k, bool), [dr[i - 1] < dr[i - k:i - 1].min() for i in range(k, ND)]]
NR4, NR7 = nr(4), nr(7)
INSIDE = np.r_[False, False, [(dh[i - 1] < dh[i - 2]) and (dl[i - 1] > dl[i - 2]) for i in range(2, ND)]]
PAT = {0: np.ones(ND, bool), 1: NR4, 2: NR7, 3: NR4 & INSIDE, 4: NR4 | NR7}


def run(look=14, vm=1.0, maxtr=1, sl=50.0, tp=25.0, pat=0, start="2018-01-01", count=True):
    if count: NTRIAL["n"] += 1
    sig = pd.DataFrame(mv).rolling(look).mean().shift(1).to_numpy()
    UB = np.fmax(DO, PC)[:, None] * (1 + vm * sig); LB = np.fmin(DO, PC)[:, None] * (1 - vm * sig)
    rows = []; s0 = dts.searchsorted(pd.Timestamp(start))
    for d in range(max(s0, look + 1), ND):
        if not PAT[pat][d] or np.isnan(sig[d]).any(): continue
        pos = 0; ent = 0; e = 0.0; m_in = 0
        pend = None                                                   # order for the next bar open: ('in', side) / ('out',)
        for b in range(13):
            # ---- bar b opens: pending market order fills at its first minute's open ----
            if pend is not None:
                if pend[0] == "out":
                    x = O1[d, 30 * b] - pos * TICK; rows.append((dts[d], pos, e, x, "trail", m_in, 30 * b)); pos = 0
                elif pend[0] in ("in", "rev"):
                    if pend[0] == "rev":
                        x = O1[d, 30 * b] - pos * TICK; rows.append((dts[d], pos, e, x, "reverse", m_in, 30 * b))
                    pos = pend[1]; e = O1[d, 30 * b] + pos * TICK; m_in = 30 * b
                pend = None
            # ---- money stop / target inside bar b, 1-minute path (Bar Magnifier) ----
            if pos != 0 and (sl or tp):
                for m in range(30 * b, 30 * b + 30):
                    stp = e - pos * sl if sl else None; tgt = e + pos * tp if tp else None
                    hit_s = sl and ((L1[d, m] <= stp) if pos > 0 else (H1[d, m] >= stp))
                    hit_t = tp and ((H1[d, m] >= tgt) if pos > 0 else (L1[d, m] <= tgt))
                    if hit_s:
                        x = (min(O1[d, m], stp) if pos > 0 else max(O1[d, m], stp)) - pos * TICK
                        rows.append((dts[d], pos, e, x, "money stop", m_in, m)); pos = 0; break
                    if hit_t:
                        x = tgt; rows.append((dts[d], pos, e, x, "target", m_in, m)); pos = 0; break
            if b == 12:                                               # 15:00 close: SetExitOnClose
                if pos != 0: rows.append((dts[d], pos, e, C30[d, 12] - pos * TICK, "close", m_in, 389)); pos = 0
                break
            # ---- bar b closes: decisions only at 09:00 .. 14:30 (b = 1 .. 12) for entries; trailing exit every close ----
            c = C30[d, b]; ub, lb, vw = UB[d, b], LB[d, b], VW[d, b]
            ls, ss = max(ub, vw), min(lb, vw)
            can = 1 <= b <= 12 and (maxtr <= 0 or ent < maxtr)
            longsig, shortsig = c > ub and c > ls, c < lb and c < ss
            if pos == 1:
                if shortsig and can: pend = ("rev", -1); ent += 1
                elif c < ls: pend = ("out",)
            elif pos == -1:
                if longsig and can: pend = ("rev", 1); ent += 1
                elif c > ss: pend = ("out",)
            else:
                if can and longsig: pend = ("in", 1); ent += 1
                elif can and shortsig: pend = ("in", -1); ent += 1
    t = pd.DataFrame(rows, columns=["date", "side", "entry", "exit", "kind", "m0", "m1"])
    t["net"] = (t.exit - t.entry) * t.side * PV - COMM
    return t


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(t, nm, w=48):
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); a, b = x[y < 2023], x[y >= 2023]
    return (f"   {nm:<{w}} n={len(x):4d} ${x.mean():4.0f} PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():4.0f} t {tst(a):4.1f} | 23+ ${b.mean():4.0f} t {tst(b):4.1f} | L ${x[t.side > 0].mean():4.0f} S ${x[t.side < 0].mean():4.0f}")


def daily(t):
    days = dts[dts >= "2018-01-01"]; return t.groupby("date").net.sum().reindex(days, fill_value=0.0)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    base = run(); base.to_csv("analysis/outputs/intraday_momentum_30m_trades.csv", index=False)
    print(f"\n1. As coded (10 MNQ = 1 NQ: money stop 50 / target 25 pts, 1 entry a day, StopMode 3), per NQ, 2018-01 -> {dts[-1].date()}:")
    print(line(base, "as coded"))
    print("   exits:", base.kind.value_counts().to_dict())
    print("   by year $:", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   2018-26 total at 10 MNQ (= 1 NQ):", f"${base.net.sum():,.0f}", "(the report's screenshot: ~$194k net, PF 1.24, win 65.9%; period and symbol not readable)")
    paper = run(sl=0, tp=0, maxtr=0)
    print("\n2. Exits and entries:")
    V = {"paper: no money stop / target, unlimited entries + reversals": dict(sl=0, tp=0, maxtr=0),
         "no money stop / target, 1 entry a day": dict(sl=0, tp=0), "money stop only (no target), 1 a day": dict(tp=0),
         "target 50 / stop 50": dict(tp=50.0), "target 100 / stop 50": dict(tp=100.0), "as coded, unlimited entries": dict(maxtr=0),
         "as coded, LookBack 90": dict(look=90), "as coded, VolMult 1.5": dict(vm=1.5), "paper, LookBack 90 (paper's SR 1.50)": dict(sl=0, tp=0, maxtr=0, look=90),
         "paper, VolMult 1.5": dict(sl=0, tp=0, maxtr=0, vm=1.5)}
    keep = {}
    for nm, kw in V.items(): keep[nm] = t = run(**kw); print(line(t, nm))
    print("\n3. The paper's day filters (completed RTH days, fixed before 09:00), on the as-coded rule and the paper rule:")
    for p, nm in ((1, "NR4"), (2, "NR7"), (3, "Triangle (NR4 + inside day)"), (4, "NR4 or NR7")):
        a = run(pat=p); b = run(pat=p, sl=0, tp=0, maxtr=0)
        print(line(a, f"as coded + {nm}")); print(line(b, f"paper + {nm}"))
        rest = base[~base.date.isin(a.date)]
        print(f"      {nm} days vs other days (as coded): ${a.net.mean():.0f} vs ${rest.net.mean():.0f} a trade, difference t "
              f"{(a.net.mean() - rest.net.mean()) / np.sqrt(a.net.var() / len(a) + rest.net.var() / len(rest)):.1f}; share of days {PAT[p][dts >= '2018'].mean():.0%}")
    print("\n4. Metrics per NQ (daily), Monte Carlo at the file's 10 MNQ:")
    rows = {}
    for nm, t in (("as coded", base), ("paper rule", paper)):
        x = daily(t)
        for per, s in (("2018-26", "2018-01-01"), ("2023+", "2023-01-01")):
            rows[f"{nm} {per}"] = (x[x.index >= s], t[t.date >= s].set_index("date").net)
        for sd, nn in ((1, "longs"), (-1, "shorts")):
            xx = daily(t[t.side == sd]); rows[f"{nm} {nn}"] = (xx, t[t.side == sd].set_index("date").net)
    print(M.table(rows))
    x = daily(base)
    b_, p_ = R.report({"as coded 2023+": x[x.index >= "2023-01-01"]}, limits=(5000, 10000, 20000)); print(b_); print(p_)
    print(MC.report(base.net.values, daily=x.values, size=1.0, label="as coded, 10 MNQ"))
    print(MC.report(base.net.values, daily=x.values, size=0.2, label="as coded, 2 MNQ"))
    pdp = pd.read_csv("agents/tasks/plan_daily_pnl.csv", index_col=0, parse_dates=True)
    xx = x.reindex(pdp.index, fill_value=0.0)
    print("   daily corr with the plan pieces:", pdp.corrwith(xx).round(2).to_dict())
    print(f"\n   trials {NTRIAL['n']}; t threshold {M.t_threshold(NTRIAL['n']):.2f}; deflated Sharpe (as coded) {M.deflated_sharpe(x.values, NTRIAL['n']):.2f}")
