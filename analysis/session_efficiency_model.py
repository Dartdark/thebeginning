"""Exact Python port of the user's SessEffForecast (5-min model, coefficients from
multi_strategy/session_efficiency/Function_SessEffForecast.txt; fitted on NQ 2010-07..2018-12, so 2019+ is out of sample),
run on NQ 2018-2026, then used as a filter / tilt on the plan's strategies (2026-10-14).
Session 8:30-15:00 CT, 5-min buckets (close of the last 1-min bar in each bucket), complete sessions = >= 90% of buckets.
Forecast for session t uses sessions up to t-1 only (as the indicator after the close).
  1. check: corr(forecast, actual ER) and actual ER by band (the README: 5-min 0.121 / 0.136 / 0.145 out of sample)
  2. plan strategies by band (2019-2026): low vs high band $ per trade, t, and both halves (2019-22 / 2023-26)
  python3 analysis/session_efficiency_model.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
INTER, CUTLO, CUTHI, CALA, CALB = 0.000107620570529, 0.477917151462, 0.532012637845, 0.02157359493, 0.2016862049
MU = [0.00082456060537, 0.122390125235, 0.249194580466, 0.895842964709, 0.335596906718, 0.0141822257896, 1.03189946834,
      0.492603404553, 0.347151219858, 0.122440023432, 0.122422239427, 0.122519058667, -0.0643720089027, 0.500821652972, 0.500724987917]
SD = [0.000443497121115, 0.0938066659082, 0.187206341725, 0.210564842396, 0.109267801864, 0.034399556477, 1.60871277324,
      0.307380075419, 0.249786857976, 0.020293359557, 0.0937879068968, 0.093774282362, 0.376595809335, 0.221093426595, 0.157882678877]
CF = [0.00599441202498, -0.164916507718, -0.0245938579242, 0.0663399080669, 0.0604975801856, -0.109860639535, -0.152085356195,
      -0.0159369304158, -0.0850669348154, -0.0899385694023, -0.0838981297647, 0.00536973272424, 0.0235918789158, 0.0683918204237, -0.126260904277]


def sessions(g):
    tr = g.trading; idx = pd.DatetimeIndex(g.ts[tr])
    C = pd.DataFrame(g.c[tr, jof(831):jof(1500) + 1]).ffill(axis=1).to_numpy()       # minutes closing 8:31 .. 15:00
    has = np.isfinite(g.c[tr, jof(831):jof(1500) + 1])
    b = C[:, 4::5]; nb = has.reshape(len(tr), 78, 5).any(2).sum(1)                  # bucket closes (8:35 .. 15:00)
    hi = np.nanmax(g.h[tr, jof(831):jof(1500) + 1], 1); lo = np.nanmin(g.l[tr, jof(831):jof(1500) + 1], 1)
    ok = (nb >= 0.9 * 78) & np.isfinite(b).all(1)
    path = np.abs(np.diff(b, axis=1)).sum(1); er = np.abs(b[:, -1] - b[:, 0]) / path
    lr = np.diff(np.log(b), axis=1); rv = lr.std(1)                                  # population std (ddof 0)
    return pd.DataFrame({"C": b[:, -1], "H": hi, "L": lo, "ER": er, "RV": rv}, index=idx)[ok]


def forecast(S):
    rows = []; ER = S.ER.to_numpy(); C = S.C.to_numpy(); H = S.H.to_numpy(); L = S.L.to_numpy(); RV = S.RV.to_numpy()
    chop = np.zeros(len(S)); run = np.zeros(len(S))
    for t in range(len(S)):
        n = min(t + 1, 252)
        if n >= 60: chop[t] = float(ER[t] < np.median(ER[t - n + 1:t + 1]))
        run[t] = (run[t - 1] + 1 if t > 0 else 1) if chop[t] == 1 else 0
    for t in range(len(S)):                                       # features at the close of session t -> forecast for t+1
        if t + 1 < 65 or t + 1 >= len(S): continue
        dc = lambda k: C[t - k]; de = lambda k: ER[t - k]
        eff = lambda n: abs(dc(0) - dc(n)) / sum(abs(dc(k) - dc(k + 1)) for k in range(n))
        x5 = np.array([np.log(dc(k) / dc(k + 5)) for k in range(60)]); x1 = np.array([np.log(dc(k) / dc(k + 1)) for k in range(60)])
        vr = x5.var(ddof=1) / (5 * x1.var(ddof=1))
        fb = np.mean([((H[t - k] > H[t - k - 1]) or (L[t - k] < L[t - k - 1])) and L[t - k - 1] <= C[t - k] <= H[t - k - 1] for k in range(20)])
        r5 = np.array([np.log(dc(k) / dc(k + 1)) for k in range(5)]); r20 = np.array([np.log(dc(k) / dc(k + 1)) for k in range(20)])
        f = [RV[t], de(0), eff(20), vr, fb, (dc(0) - np.mean([dc(k) for k in range(50)])) / dc(0), run[t], eff(5), eff(10),
             np.mean([de(k) for k in range(20)]), de(1), de(2), r5.std(ddof=1) / r20.std(ddof=1) - 1,
             np.mean(chop[t - 4:t + 1]), np.mean(chop[t - 9:t + 1])]
        lin = INTER + sum(c * (v - m) / s for c, v, m, s in zip(CF, f, MU, SD)); p = 1 / (1 + np.exp(-lin))
        rows.append((S.index[t + 1], p, CALA + CALB * p, 1 if p <= CUTLO else (3 if p > CUTHI else 2)))
    return pd.DataFrame(rows, columns=["d", "p", "expER", "band"]).set_index("d")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); S = sessions(g); Fc = forecast(S).join(S.ER)
    Fc = Fc[Fc.index >= "2019-01-01"]
    print(f"sessions {len(S)}; forecasts 2019+ {len(Fc)}; band shares {Fc.band.value_counts(normalize=True).sort_index().round(2).to_dict()}")
    print(f"1. corr(forecast p, actual ER) {Fc.p.corr(Fc.ER):+.3f} (2019-22 {Fc.p[Fc.index.year < 2023].corr(Fc.ER[Fc.index.year < 2023]):+.3f}, 2023-26 {Fc.p[Fc.index.year >= 2023].corr(Fc.ER[Fc.index.year >= 2023]):+.3f})")
    print("   actual ER by band:", Fc.groupby("band").ER.mean().round(3).to_dict(), "(README out of sample: 0.121 / 0.136 / 0.145)")
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/plan_agreement_test.py", run_name="__main__")
    T = ns["T"]; T = T[T.date >= "2019-01-01"]
    # Sunday-evening entries (Bridge Monday) belong to Monday's session
    T["sess"] = T.date + pd.to_timedelta((T.date.dt.dayofweek == 6).astype(int), unit="D")
    T["band"] = T.sess.map(Fc.band)
    print("\n2. plan strategies by the forecast band (2019-2026, $ per trade per NQ)")
    for s in ["VB", "ONB_ML", "MON", "EOS", "LDF", "NFP", "BRIDGE", "VCS"]:
        x = T[(T.strat == s) & T.band.notna()]
        if len(x) < 20: continue
        lo, mid, hi = (x.net[x.band == b] for b in (1, 2, 3))
        t_ = (hi.mean() - lo.mean()) / np.sqrt(hi.var() / max(len(hi), 1) + lo.var() / max(len(lo), 1)) if len(hi) > 2 and len(lo) > 2 else np.nan
        y = x.sess.dt.year
        h1 = x[y < 2023]; h2 = x[y >= 2023]
        d1 = h1.net[h1.band == 3].mean() - h1.net[h1.band == 1].mean(); d2 = h2.net[h2.band == 3].mean() - h2.net[h2.band == 1].mean()
        print(f"   {s:<7} low ${lo.mean():6.0f} (n {len(lo):3d}) | mid ${mid.mean():6.0f} (n {len(mid):3d}) | high ${hi.mean():6.0f} (n {len(hi):3d})"
              f" | high - low t {t_:+.2f} | 2019-22 {d1:+6.0f}, 2023-26 {d2:+6.0f}")
    Fc.to_pickle(SP + "sess_eff_forecast.pkl")
