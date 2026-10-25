"""MNQ_Portfolio_SharedCap_v2 (user's MultiCharts .NET file + report, 2026-10-25; checks/candidates/mnq_sharedcap/). Three legs
in one signal on a 1-minute @MNQ chart (Central time, close-stamped):
  NA   noise area: sigma(m) = mean |close(m) / RTH open - 1| over the last 14 sessions at minute m (08:31 .. 15:00);
       UB = max(open, prior 15:00 close) x (1 + sigma), LB = min(...) x (1 - sigma); VWAP = sum(close x vol) / sum(vol) from
       08:31. Every minute: exit a long if close < max(UB, VWAP) (short mirror). At :00 / :30 closes 09:00-14:30: close > UB
       -> long (reversing a short), close < LB -> short; not on Mondays or the holiday windows. Flat at the 15:00 close. 2 MNQ.
  ON   overnight gap fade: at the 08:31 bar, z = (open - prior close) / prior close against the last 20 such returns
       (population sd); z >= 1 -> short 3 MNQ at the 08:31 close, out at the 12:00 close.
  TOTM 3rd RTH session of the month and the prior close > its 50-session mean -> long 3 MNQ at the 08:31 close, out at the
       15:01 close.
  Shared cap: when realized + open P&L of all legs <= -$750, flatten everything and stop for the day.
  Fills at the signal bar's close (the code's MarketThisBar).
The point the code misses: one MultiCharts signal holds ONE net position. A SellShort while long (or a Buy while short)
reverses the WHOLE position, and the exit orders of a leg that MultiCharts already closed are ignored. So the report is
not the three legs' sum. This script builds (a) each leg alone, (b) the intended sum with the shared cap, (c) the netted
book MultiCharts would hold (one position; every entry first closes any opposite position, like Buy / SellShort do).
Costs per MNQ: ours $0.725 + 1 tick ($0.50) per market fill; Apex real $1.04 + 1 tick; the report's $0.37 + its slippage.
  python3 analysis/mnq_sharedcap_test.py [SCRATCH_DIR] > analysis/outputs/mnq_sharedcap_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
g = pickle.load(open(SP + "g24.pkl", "rb"))
J0, J1 = jof(831), jof(1500)
tr = g.trading; tr = tr[~np.isnan(g.c[tr, J1]) & ~np.isnan(g.o[tr, J0])]
dts = pd.DatetimeIndex(g.ts[tr])
C = np.array([pd.Series(g.c[r, J0:J1 + 1]).ffill().bfill().to_numpy() for r in tr]); V = np.nan_to_num(g.v[tr, J0:J1 + 1])
O0 = g.o[tr, J0]; C1501 = np.where(np.isnan(g.c[tr, J1 + 1]), C[:, -1], g.c[tr, J1 + 1])
PV = 2.0; TICK = 0.25
PC = np.r_[np.nan, C[:-1, -1]]
sig = pd.DataFrame(np.abs(C / O0[:, None] - 1)).rolling(14).mean().shift(1).to_numpy()
UB = np.fmax(O0, PC)[:, None] * (1 + sig); LB = np.fmin(O0, PC)[:, None] * (1 - sig)
VW = np.cumsum(C * V, 1) / np.maximum(np.cumsum(V, 1), 1)
onr = (O0 - PC) / PC; s_ = pd.Series(onr)
z = ((s_ - s_.rolling(20).mean().shift(1)) / s_.rolling(20).std(ddof=0).shift(1)).to_numpy()
ma50 = pd.Series(C[:, -1]).rolling(50).mean().shift(1).to_numpy()
rank = pd.Series(1, index=dts).groupby([dts.year, dts.month]).cumsum().to_numpy()
mins = 831 + np.arange(390); mins = (mins // 100 * 60 + mins % 100)
hhmm = np.array([(510 + 1 + k) // 60 * 100 + (510 + 1 + k) % 60 for k in range(390)])        # 08:31 .. 15:00
HALF = ((hhmm % 100 == 0) | (hhmm % 100 == 30)) & (hhmm >= 900) & (hhmm <= 1430)
I1200 = int(np.where(hhmm == 1200)[0][0])


def holiday(d):
    mo, dy = d.month, d.day
    return (mo == 12 and dy >= 23) or (mo == 1 and dy <= 2) or (mo == 7 and 2 <= dy <= 5) or (mo == 11 and 20 <= dy <= 29)


def day_paths(d, na_q=2, on_q=3, tm_q=3, block_mon=True, hol=True):
    """Per-minute event lists for each leg: list of (minute index, signed qty change, price)."""
    ev = {"NA": [], "ON": [], "TOTM": []}
    if np.isfinite(z[d]) and z[d] >= 1 and on_q: ev["ON"] += [(0, -on_q, C[d, 0]), (I1200, on_q, C[d, I1200])]
    if rank[d] == 3 and np.isfinite(ma50[d]) and PC[d] > ma50[d] and tm_q: ev["TOTM"] += [(0, tm_q, C[d, 0]), (390, -tm_q, C1501[d])]
    if np.isnan(sig[d]).any() or not np.isfinite(PC[d]) or not na_q: return ev
    pos = 0; ok_day = not (block_mon and dts[d].dayofweek == 0) and not (hol and holiday(dts[d]))
    for m in range(390):
        c = C[d, m]
        if pos == 1 and c < max(UB[d, m], VW[d, m]): ev["NA"].append((m, -na_q, c)); pos = 0
        elif pos == -1 and c > min(LB[d, m], VW[d, m]): ev["NA"].append((m, na_q, c)); pos = 0
        if HALF[m] and ok_day:
            if c > UB[d, m] and pos != 1:
                ev["NA"].append((m, na_q * (2 if pos == -1 else 1), c)); pos = 1
            elif c < LB[d, m] and pos != -1:
                ev["NA"].append((m, -na_q * (2 if pos == 1 else 1), c)); pos = -1
    if pos: ev["NA"].append((389, -pos * na_q, C[d, 389]))
    return ev


def realize(events, d, cost_per_fill, cap=None):
    """P&L of a list of (minute, dq, price) events for one book; optional shared cap on realized + open (minute marks)."""
    events = sorted(events, key=lambda e: e[0]); pos = 0; cash = 0.0; fills = 0; out = []
    ei = 0; capped = False
    for m in range(391):
        while ei < len(events) and events[ei][0] == m and not capped:
            _, dq, px = events[ei]; cash -= dq * px * PV; fills += abs(dq); pos += dq; ei += 1
        if capped: break
        px_m = C[d, min(m, 389)] if m < 390 else C1501[d]
        mtm = cash + pos * px_m * PV - fills * cost_per_fill
        if cap is not None and mtm <= -cap:           # latch even when flat (fix 2026-10-25, Codex review finding 2)
            if pos: cash += pos * px_m * PV; fills += abs(pos); pos = 0
            capped = True
    if pos: cash += pos * C1501[d] * PV; fills += abs(pos)
    return cash - fills * cost_per_fill, fills


def netted(ev):
    """MultiCharts one-position netting: an entry against an open opposite position first closes ALL of it; an exit for a
    leg whose contracts MultiCharts no longer holds does nothing. Legs' own exits reduce only what is still held for them.
    Fix 2026-10-25 (Codex review finding 1): events are classified by the leg's OWN intended position, so an exit order of a
    leg that another leg's entry already closed is ignored instead of opening a new position (was: held == 0 -> entry)."""
    allev = sorted([(m, leg, dq, px) for leg, L in ev.items() for (m, dq, px) in L], key=lambda e: (e[0], e[1]))
    net = 0; held = {k: 0 for k in ev}; own = {k: 0 for k in ev}; out = []
    for m, leg, dq, px in allev:
        new_own = own[leg] + dq
        if own[leg] == 0 or np.sign(new_own) == -np.sign(own[leg]) or np.sign(dq) == np.sign(own[leg]):
            q = new_own if own[leg] != 0 and np.sign(new_own) == -np.sign(own[leg]) else dq      # entry (a reversal = entry of new_own)
            if net != 0 and np.sign(net) != np.sign(q):                       # opposite position held: closed in full
                out.append((m, -net, px)); held = {k: 0 for k in held}; net = 0
            out.append((m, q, px)); net += q; held[leg] += q
        else:                                                                 # exit order for this leg
            q = -held[leg]
            if q != 0: out.append((m, q, px)); net += q; held[leg] = 0
        own[leg] = new_own
    return out

def run(cost=0.725 + 0.5, cap=750.0, start="2018-01-01", **kw):
    rows = []
    for d in range(len(tr)):
        if dts[d] < pd.Timestamp(start): continue
        ev = day_paths(d, **kw)
        r = {"date": dts[d]}
        for leg in ev: r[leg], r[leg + "_n"] = realize(ev[leg], d, cost)
        allev = [e for L in ev.values() for e in L]
        r["sum"], _ = realize(allev, d, cost)
        r["sum_cap"], _ = realize(allev, d, cost, cap=cap)
        r["net_cap"], _ = realize(netted(ev), d, cost, cap=cap)
        rows.append(r)
    return pd.DataFrame(rows).set_index("date")


def line(x, nm, w=34):
    t = x[x != 0]; by = x.groupby(x.index.year).sum(); e = x.cumsum()
    return (f"   {nm:<{w}} ${x.sum() / (len(x) / 252):>8,.0f}/yr  days {len(t):4d}  ${t.mean():6.1f}/day  t {t.mean() / t.std() * np.sqrt(len(t)):4.1f}  "
            f"Sharpe {x.mean() / x.std() * np.sqrt(252):4.2f}  maxDD ${-(e - e.cummax()).min():>6,.0f}  worst day ${x.min():>6,.0f}  yrs+ {(by > 0).sum()}/{len(by)} | "
            f"2018-21 ${x[x.index.year < 2022].sum() / max(1, (x.index.year < 2022).sum() / 252):>7,.0f}/yr  2022+ ${x[x.index.year >= 2022].sum() / ((x.index.year >= 2022).sum() / 252):>7,.0f}/yr")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    rep = pd.read_excel("mc_reports/MNQ_Portfolio_SharedCap_v2.xlsx", sheet_name="List of Trades", header=2)
    en = rep[rep.Type.astype(str).str.startswith("Entry")]; ex = rep[rep.Type.astype(str).str.startswith("Exit")]
    print(f"\n1. The report (02/2022 - 07/2026): net ${en['Profit ($)'].sum():,.0f}, {len(en)} trades; entries by signal "
          f"{en.Signal.value_counts().to_dict()}, exits by signal {ex.Signal.value_counts().to_dict()}")
    cross = ex[~ex.Signal.isin(["NA_LongX", "NA_ShortX", "ON_Exit", "TOTM_Exit"])].Signal.value_counts().to_dict()
    mism = sum(1 for (a, b) in zip(en.Signal.values, ex.Signal.values) if not (b.startswith(a.split("_")[0]) or (a.startswith("NA") and b.startswith("NA"))))
    print(f"   exits made by ANOTHER leg's entry order (MultiCharts nets them into one position): {mism} of {len(en)} trades")
    for nm, c in (("ours ($0.725 + 1 tick a fill)", 0.725 + 0.5), ("Apex real ($1.04 + 1 tick)", 1.04 + 0.5), ("report ($0.37, no slip)", 0.37)):
        R = run(cost=c)
        print(f"\n2. 2018-2026, costs {nm}, per day (NA 2 MNQ, ON 3, TOTM 3):")
        for col, label in (("NA", "NA alone"), ("ON", "ON alone"), ("TOTM", "TOTM alone"), ("sum", "three legs, no cap"),
                           ("sum_cap", "three legs + $750 shared cap"), ("net_cap", "netted (one MC position) + cap")):
            print(line(R[col], label))
        if c == 0.725 + 0.5: RO = R
        if c == 0.37:
            w = R[(R.index >= "2022-02-22") & (R.index <= "2026-07-24")]
            print(f"   report window 2022-02-22 .. 2026-07-24: netted + cap ${w.net_cap.sum():,.0f} (report ${en['Profit ($)'].sum():,.0f}); "
                  f"three legs + cap ${w.sum_cap.sum():,.0f}")
    R = RO
    print("\n3. Overlap: days with ON short and NA long at the same time, TOTM long with ON short (legs fighting in one position):")
    n_on_tm = int(((R.ON != 0) & (R.TOTM != 0)).sum()); print(f"   ON + TOTM same day: {n_on_tm}; ON days {int((R.ON != 0).sum())}, TOTM days {int((R.TOTM != 0).sum())}")
    print("\n4. Robustness of each leg (ours):")
    for nm, kw in (("NA without the Monday block", dict(block_mon=False)), ("NA without the holiday blackout", dict(hol=False)),
                   ("NA neither", dict(block_mon=False, hol=False))):
        print(line(run(**kw).NA, nm))
    y = R.NA; mon = R.index.dayofweek == 0
    print(f"   NA on Mondays if traded: {line(run(block_mon=False).NA[mon], 'Mondays only')}")
    print("\n5. Metrics, three legs + cap (ours), and Monte Carlo at the user's size:")
    x = R.sum_cap
    print(M.table({"three legs + cap 2018-26": (x, None), "2023+": (x[x.index >= "2023-01-01"], None),
                   "NA": (R.NA, None), "ON": (R.ON, None), "TOTM": (R.TOTM, None)}))
    print(MC.report(x[x != 0].values, daily=x.values, size=1.0, label="three legs + cap (NA 2, ON 3, TOTM 3 MNQ)"))
    import io, contextlib, runpy
    with contextlib.redirect_stdout(io.StringIO()):
        gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
    P = gg["P"]; tot = P.sum(axis=1)
    for leg, q in (("NA", 2), ("ON", 3), ("TOTM", 3)):
        s = (R[leg] / q).reindex(P.index, fill_value=0)
        print(f"   {leg} (1 MNQ) daily corr with our 17-piece personal book {np.corrcoef(s, tot)[0, 1]:+.2f}; "
              f"with Overnight Bias {np.corrcoef(s, P['OvernightBiasML'])[0, 1]:+.2f}, Vault Break {np.corrcoef(s, P['VaultBreak'])[0, 1]:+.2f}")
    R.to_csv(SP + "mnq_sharedcap_daily.csv")
