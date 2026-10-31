"""Gold 3-Candle Reversal, long only, H4 (user's file Gold_Reversal_Target_Vol_Margin.txt, 2026-10-24), rebuilt on our GC
1-minute bars (CT, close-stamped), roll gaps back-adjusted (rolls from s_rank_gap_round2_test.rolls_gc).
H4 bars follow the CME session from 17:00 CT: 17-21, 21-01, 01-05, 05-09, 09-13, 13-16.
Rule (as MultiCharts runs it, no IOG): at an H4 close, flat and no working order: candle 2 (bar[1]) bearish with low < bar[2]
low, candle 3 (this bar) bullish and closing above bar[2] low -> buy stop at candle 3 high (input default), stop = min(low[1],
low), target = entry + 1 x risk. The order works until an H4 bar CLOSES with low <= stop (cancel; the order stays live
inside that bar). Exits are placed at the close of the fill bar, so they work from the next bar (no stop in the fill bar).
Sizing input only matters for us as a filter: risk > $10,000 per contract (100 points) is skipped.
Costs: $7.25 per GC round trip + 1 tick ($10) per stop fill (entry, stop); the target limit has no slippage.
Variants: 'apex' = flat at 15:55 CT (Apex: flat by 15:59) and the working order cancelled there; the other input settings;
targets 1.5 / 2; a mirrored short version and a random-entry placebo.
  python3 analysis/gold_h4_reversal_test.py > analysis/outputs/gold_h4_reversal_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
sys.argv = [sys.argv[0], "scratch_data/"]
import s_rank_gap_round2_test as SG
import metrics as M, resampling as R, montecarlo as MC

PV, TICK, COMM = 100.0, 0.10, 7.25
NTRIAL = {"n": 0}


def load():
    S = SG.Sym("GC"); out, info = SG.rolls_gc(S); S.set_rolls(out)
    O, H, L, C = S.O.copy(), S.H.copy(), S.L.copy(), S.C.copy()
    j, _, _ = S.jumps(); adj = np.zeros(S.N)
    for b in sorted(out): adj[:b] += j[b]                  # back-adjust: older prices carry the later roll gaps
    O, H, L, C = O + adj, H + adj, L + adj, C + adj
    ok = np.where(~np.isnan(C))[0]; row, hm = ok // 1440, ok % 1440
    end = np.where(hm <= 60, row * 1440 + 60, np.where(hm <= 300, row * 1440 + 300, np.where(hm <= 540, row * 1440 + 540,
          np.where(hm <= 780, row * 1440 + 780, np.where(hm <= 960, row * 1440 + 960, np.where(hm <= 1260, row * 1440 + 1260,
          (row + 1) * 1440 + 60))))))
    ends, start = np.unique(end, return_index=True); stop_ = np.r_[start[1:], len(ok)]
    bars = pd.DataFrame(dict(end=ends, a=start, b=stop_))
    bars["o"] = O[ok[start]]; bars["c"] = C[ok[stop_ - 1]]
    bars["h"] = np.maximum.reduceat(H[ok], start); bars["l"] = np.minimum.reduceat(L[ok], start)
    return dict(S=S, ok=ok, O=O[ok], H=H[ok], L=L[ok], C=C[ok], bars=bars, ts=S.TS)


def run(D, entry_high=True, stop_lowest=True, rr=1.0, apex=False, side=1, max_risk=100.0, rand=None, count=True):
    """side 1 = the rule; side -1 = mirrored short. rand = rng: enter at a random H4 close instead of the pattern."""
    if count: NTRIAL["n"] += 1
    B = D["bars"]; o, h, l, c = B.o.values, B.h.values, B.l.values, B.c.values
    mO, mH, mL, mC, ok = D["O"], D["H"], D["L"], D["C"], D["ok"]
    mhm = ok % 1440; flatm = (mhm == 955) if apex else np.zeros(len(ok), bool)
    rows = []; k = 2; nb = len(B); pend = False
    while k < nb - 1:
        # bar k just closed, flat. pending cancel check, then scan
        if pend and (l[k] <= sp if side > 0 else h[k] >= sp): pend = False
        if not pend:
            if rand is not None:
                setup = rand.random() < 0.08
            elif side > 0:
                setup = c[k - 1] < o[k - 1] and l[k - 1] < l[k - 2] and c[k] > o[k] and c[k] > l[k - 2]
            else:
                setup = c[k - 1] > o[k - 1] and h[k - 1] > h[k - 2] and c[k] < o[k] and c[k] < h[k - 2]
            if setup:
                if side > 0:
                    e = h[k] if entry_high else h[k - 1]; sp = min(l[k - 1], l[k]) if stop_lowest else l[k - 1]
                else:
                    e = l[k] if entry_high else l[k - 1]; sp = max(h[k - 1], h[k]) if stop_lowest else h[k - 1]
                risk = (e - sp) * side
                if 0 < risk <= max_risk:
                    tp = e + side * rr * risk; pend = True; setk = k
        if not pend: k += 1; continue
        # working order through bar k+1 (minute path); cancelled only at a bar close
        filled = False; k += 1
        while k < nb:
            a, b = B.a.values[k], B.b.values[k]; m = np.arange(a, b)
            if apex:
                fm = np.where(flatm[m])[0]
                if len(fm): m = m[:fm[0]]                       # nothing fills after 15:55
            hit = np.where(mH[m] >= e if side > 0 else mL[m] <= e)[0]
            if len(hit):
                fi = m[hit[0]]; ef = max(mO[fi], e) if side > 0 else min(mO[fi], e); filled = True; break
            if apex and len(np.where(flatm[np.arange(a, b)])[0]): pend = False; break   # cancel at the daily flat
            if (l[k] <= sp) if side > 0 else (h[k] >= sp): pend = False; break
            k += 1
        if not filled:
            if k >= nb: break
            pend = False; continue                               # bar k closed with the cancel: rescan on bar k
        pend = False; fk = k
        # in the fill bar: no exits unless apex flat; from the next bar: stop / target
        x = None; xi = None; kind = None
        mm = np.arange(fi, B.b.values[fk])
        if apex:
            f = np.where(flatm[mm])[0]
            if len(f): xi = mm[f[0]]; x = mC[xi] - side * TICK; kind = "flat"
        kk = fk + 1
        while x is None and kk < nb:
            m = np.arange(B.a.values[kk], B.b.values[kk])
            sl = (mL[m] <= sp) if side > 0 else (mH[m] >= sp); tg = (mH[m] >= tp) if side > 0 else (mL[m] <= tp)
            fl = flatm[m]; ev = np.where(sl | tg | fl)[0]
            if len(ev):
                i = m[ev[0]]; xi = i
                if sl[ev[0]]: x = (min(mO[i], sp) if side > 0 else max(mO[i], sp)) - side * TICK; kind = "stop"
                elif tg[ev[0]]: x = max(mO[i], tp) if side > 0 else min(mO[i], tp); kind = "target"
                else: x = mC[i] - side * TICK; kind = "flat"
                break
            kk += 1
        if x is None: break
        gross = (x - ef) * side * PV; slip_e = TICK * PV
        net = gross - COMM - slip_e
        ts = D["ts"]
        rows.append(dict(entry_time=ts[ok[fi] // 1440] + pd.Timedelta(minutes=int(ok[fi] % 1440)),
                         exit_time=ts[ok[xi] // 1440] + pd.Timedelta(minutes=int(ok[xi] % 1440)),
                         side=side, entry=ef, stop=sp, target=tp, exit=x, kind=kind, risk_pts=risk, net=net,
                         bars_waited=fk - setk, roll=bool(D["S"].has_roll(ok[fi], ok[xi]))))
        k = bars_end(B, xi)                                      # the exit bar's close: rescan there
    t = pd.DataFrame(rows)
    if len(t): t["date"] = pd.to_datetime(t.exit_time.dt.date)
    return t


def bars_end(B, mi):
    return int(np.searchsorted(B.b.values, mi, side="right"))


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(t, nm, w=40):
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    t = t[t.date >= "2018-01-01"]; x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    a, b = x[y < 2023], x[y >= 2023]; hold = (t.exit_time - t.entry_time).dt.total_seconds() / 3600
    return (f"   {nm:<{w}} n={len(x):4d} ({len(x) / 8.8:3.0f}/yr) ${x.mean():5.0f} PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} "
            f"yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${a.mean():5.0f} t {tst(a):4.1f} | 23+ ${b.mean():5.0f} t {tst(b):4.1f} | hold med {hold.median():.0f}h"
            f" | in R {(x / (t.risk_pts * PV)).mean():+.3f}")


def daily(t, days):
    return t.groupby("date").net.sum().reindex(days, fill_value=0.0)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    D = load(); days = pd.DatetimeIndex(D["S"].days)
    print(f"H4 bars {len(D['bars'])}, data {D['ts'][D['ok'][0] // 1440].date()} -> {D['ts'][D['ok'][-1] // 1440].date()}")
    base = run(D); base.to_csv("analysis/outputs/gold_h4_reversal_trades.csv", index=False)
    ap = run(D, apex=True); ap.to_csv("analysis/outputs/gold_h4_reversal_apex_trades.csv", index=False)
    print("\n1. The rule (per 1 GC; MGC = /10), 2018-01 -> 2026:")
    print(line(base, "as coded (multi-day holds)")); print(line(ap, "Apex: flat 15:55 CT, order cancelled"))
    print("   by year (as coded):", base[base.date >= "2018"].groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   by year (Apex)    :", ap[ap.date >= "2018"].groupby(ap.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   exits (as coded):", base.kind.value_counts().to_dict(), "| trades across a roll:", int(base.roll.sum()))
    print(f"   median risk {base.risk_pts.median():.1f} pts (${base.risk_pts.median() * PV:,.0f} per GC), 90th pct {base.risk_pts.quantile(.9):.1f}")

    print("\n2. Other input settings and targets (as coded):")
    for eh, sl in ((True, False), (False, True), (False, False)):
        print(line(run(D, entry_high=eh, stop_lowest=sl), f"entry {'c3' if eh else 'c2'} high, stop {'lowest' if sl else 'c2 low'}"))
    for rr in (0.5, 1.5, 2.0, 3.0): print(line(run(D, rr=rr), f"target {rr} R"))
    for rr in (1.5, 2.0): print(line(run(D, rr=rr, apex=True), f"Apex, target {rr} R"))

    print("\n3. Placebos:")
    print(line(run(D, side=-1), "mirrored short pattern"))
    pl = [run(D, rand=np.random.default_rng(s), count=False) for s in range(40)]
    m = np.array([p[p.date >= "2018"].net.mean() for p in pl])
    print(f"   random H4 close -> same entry / stop / target build, 40 seeds: avg ${m.mean():.0f} (5-95% {np.percentile(m, 5):.0f} .. "
          f"{np.percentile(m, 95):.0f}); share >= rule ${base[base.date >= '2018'].net.mean():.0f}: {np.mean(m >= base[base.date >= '2018'].net.mean()):.0%}")
    bh = D["bars"]; print(f"   buy and hold GC 2018 -> end, per contract: ${(bh.c.iloc[-1] - bh.c[bh.end // 1440 >= np.searchsorted(D['ts'], pd.Timestamp('2018-01-01'))].iloc[0]) * PV:,.0f}")

    print("\n4. Metrics per 1 GC (daily, booked on the exit day):")
    rows = {}
    for nm, t in (("as coded", base), ("Apex", ap)):
        dd = daily(t, days)
        for per, st in (("2018-26", "2018-01-01"), ("2023+", "2023-01-01")):
            rows[f"{nm} {per}"] = (dd[dd.index >= st], t[t.date >= st].set_index("date").net)
    print(M.table(rows))
    for nm, t in (("as coded", base), ("Apex", ap)):
        dd = daily(t, days)
        b_, p_ = R.report({f"{nm} 2023+": dd[dd.index >= "2023-01-01"]}, limits=(10000, 20000, 40000)); print(b_); print(p_)
    print("\n   Monte Carlo, Apex variant at 1 MGC (2018+, $2,000 trailing):")
    print(MC.report(ap[ap.date >= "2018"].net.values, daily=daily(ap, days)[days >= "2018"].values, size=0.1, label="Gold H4 Apex 1 MGC"))
    print("   Monte Carlo, as coded at 1 MGC:")
    print(MC.report(base[base.date >= "2018"].net.values, daily=daily(base, days)[days >= "2018"].values, size=0.1, label="Gold H4 1 MGC"))
    dd = daily(base, days); dd = dd[dd.index >= "2018"]
    print(f"\n   trials {NTRIAL['n']}; t threshold {M.t_threshold(NTRIAL['n']):.2f}; deflated Sharpe (as coded) {M.deflated_sharpe(dd.values, NTRIAL['n']):.2f}")
    daily(base, days).to_csv("analysis/outputs/gold_h4_reversal_daily_per_gc.csv")
