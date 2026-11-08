"""GC USA -> Asia continuation + protective stop in Asia-ATR units (user, 2026-11-01: "test the ATR stop").

Pre-registered BEFORE any result (2026-11-01): ONE value, SL_ATR_Mult = 1.0, i.e. stop = entry - 1.0 x the Asia ATR fixed at
the decision (median High-Low of the last 21 Asia sessions; the code's SetStopLoss per contract, active from the entry bar).
Why 1.0: a night that runs a whole typical Asia range against the entry is the tail event the 2023+ drawdown is made of
(-$17.8k on 2026-04-02 at 1 GC), while ordinary noise stays inside it. Adopt only if it improves return / max DD at 1 GC in
2018-22 AND 2023+ on the New York clock (the version matching the user's report) and does not reverse on the CT clock.
Other multipliers (0.5 / 0.75 / 1.5 / 2.0) are printed as a labelled sensitivity, never as a choice.

Trades: checks/candidates/gc_asia_continuation/python_trades_shift{-60,0}.csv (analysis/gc_asia_continuation_test.py).
Stop fill: first 1-minute bar from the entry bar on whose low <= stop, at min(that minute's open, stop) (gaps fill worse);
costs unchanged ($7.25 + 1 tick per market / stop fill = $27.25 per GC).
  python3 analysis/gc_asia_atr_stop_test.py [SCRATCH_DIR]
"""
import sys, os, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from cl_forced_flows_test import load
import gc_asia_continuation_test as G
import metrics as M, resampling as R, montecarlo as MC

PRE = 1.0
SENS = (0.5, 0.75, 1.5, 2.0)


def with_stop(T, g, mult):
    O, L = g.o.ravel(), g.l.ravel()
    pts, hit = [], []
    for r in T.itertuples():
        stop = r.entry - mult * r.atr
        seg = L[int(r.e):int(r.x)]
        j = np.where(seg <= stop)[0]
        if len(j):
            k = int(r.e) + j[0]; o = O[k]
            px = min(o if np.isfinite(o) else stop, stop)
            pts.append(px - r.entry); hit.append(True)
        else:
            pts.append(r.pts); hit.append(False)
    out = T.copy(); out["pts_s"] = pts; out["stopped"] = hit
    out["net_s"] = out.pts_s * G.PV - G.COST
    out["netA_s"] = out.net_s * out.qty_atr
    return out


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    g = load("GC")
    for shift in (-60, 0):
        T = pd.read_csv(f"checks/candidates/gc_asia_continuation/python_trades_shift{shift}.csv", parse_dates=["date", "asia_date"])
        clock = "New York clock (report match)" if shift == -60 else "CT clock (as coded)"
        print(f"\n==================== {clock}: {len(T)} trades")
        rows = []
        for mult in (None, PRE) + SENS:
            S = T.assign(net_s=T.net1, netA_s=T.netA, stopped=False) if mult is None else with_stop(T, g, mult)
            lab = "no stop (base)" if mult is None else (f"{mult:.2f} x ATR  << PRE-REGISTERED" if mult == PRE else f"{mult:.2f} x ATR (sensitivity)")
            for p in ("2018-22", "2023+"):
                u = S[S.period == p]; a = G.stats(u.net_s, ""); b = G.stats(u.netA_s, "")
                rows.append(dict(stop=lab, period=p, n=a["n"], stopped=f"{u.stopped.mean():.0%}", avg=a["avg"], pf=a["pf"], t=a["t"],
                                 maxdd=a["maxdd"], ret_dd=a["ret_dd"], worst=u.net_s.min(), atr_net=b["net"], atr_pf=b["pf"], atr_dd=b["maxdd"],
                                 atr_ret_dd=b["ret_dd"]))
        print("1 GC: avg / pf / t / maxdd / ret_dd / worst night;  ATR-sized (the code's sizing): net / pf / maxdd / ret_dd")
        print(pd.DataFrame(rows).round(2).to_string(index=False))
        if shift == -60:
            S = with_stop(T, g, PRE)
            print("\nWorst 8 nights 2023+ (1 GC), base -> with the 1.0 x ATR stop:")
            w = S[S.period == "2023+"].nsmallest(8, "net1")[["asia_date", "net1", "net_s", "stopped", "atr"]]
            print(w.round(1).to_string(index=False))
            print("\nStopped trades: how they would have ended without the stop (1 GC):",
                  f"{S.stopped.sum()} trades, stop result ${S[S.stopped].net_s.sum():,.0f} vs time exit ${S[S.stopped].net1.sum():,.0f}")
            days = pd.bdate_range("2018-01-01", S.asia_date.max())
            dly = S.groupby(S.asia_date).net_s.sum().reindex(days, fill_value=0.0)
            print("\n== 1.0 x ATR stop: standard metrics per GC (long only, so longs = whole)")
            print(M.table({"whole": (dly, S.net_s), "2018-22": (dly[dly.index < "2023-01-01"], S[S.period == "2018-22"].net_s),
                           "2023+": (dly[dly.index >= "2023-01-01"], S[S.period == "2023+"].net_s)}, capital=50_000.0))
            b_, p_ = R.report({"1.0 ATR stop 2023+": dly[dly.index >= "2023-01-01"]}); print(b_); print(p_)
            print(MC.report(S.net_s.values, daily=dly.values, size=0.1, label="1.0 ATR stop, 1 MGC"))
            print(MC.report(S.net_s.values, daily=dly.values, size=0.2, label="1.0 ATR stop, 2 MGC"))
