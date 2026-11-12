"""Waldow, Schnaubelt, Krauss & Fischer (2021) 'Machine Learning in Futures Markets' (JRFM 14:119; papers/jrfm-14-00119.pdf),
rebuilt on the 9 futures we hold (6E BTC CL ES GC NG NQ YM ZN), 2018-2026. User upload 2026-11-12.

PRE-REGISTERED (written before the first run; one run, no tuning):
  Prices   Ve = VWAP of the 1-min bars closing 08:31-09:30 CT (paper: 09:30-10:30 EST), Vr = VWAP 09:32-10:31 CT; typical price
           (h+l+c)/3 x volume; a window with < 30 traded minutes = missing. Roll jumps removed by backward ratio adjustment (as the paper; the first run used difference
           adjustment, which shrank old CL / NG prices toward zero and blew up returns: a bug, not a result)
           (analysis/roll_adjust.py; NG / BTC monthly windows added here).
  Features R^l_t = Ve_t / Vr_{t-l} - 1, l in 1..20 and 40, 60, ..., 240 (31 features, paper eq. 1).
  Target   Y = 1 if R^1_{t+1} (= Ve_{t+1} / Vr_t - 1, the h = 1 trade) beats that day's cross-sectional median.
  Models   paper's: LR (L2, C from 100 log-spaced values 1e-4..1e5, 5-fold CV), RF (1000 trees, depth 20, sqrt features, seed 1),
           GBC (100 trees, depth 5; sklearn instead of lightgbm). Rolling: train 750 days, trade the next 250, refit; last
           training day dropped (its target is the first trading day). Plus two model-free rules the paper's feature importance
           points to: A1 short-term reversal, rank on -R^1; A2 the same on R^1 / its 20-day sd (our 9 markets differ in volatility).
  Trade    k = 1 (top / flop one of 9 = 11%, the paper's baseline is 10%), h = 1: long the top, short the bottom at Vr_t, out at
           Ve_{t+1}. Portfolio return = (long leg - short leg) / 2, in bp of notional. Costs per leg round trip: commission
           ($7.25 NQ, $5 others) + 1 tick a fill, as bp of notional at entry.
  Report   bp a day gross / net, t, Sharpe, by year, 2018-22 vs 2023+, long / short legs; control: equal-weight long all markets
           (MKT); placebo: random top / flop picks from the same days (1000 draws). NOT Apex-legal (overnight hold): personal only.
  tools/run_stamped.sh analysis/ml_futures_xs_test.py > analysis/outputs/ml_futures_xs_test_output.txt
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
import roll_adjust as RA

SYMS = ["6E", "BTC", "CL", "ES", "GC", "NG", "NQ", "YM", "ZN"]
SPEC = {"6E": (125000, 0.00005), "BTC": (5, 5), "CL": (1000, 0.01), "ES": (50, 0.25), "GC": (100, 0.1),
        "NG": (10000, 0.001), "NQ": (20, 0.25), "YM": (5, 1), "ZN": (1000, 1 / 64)}
COMM = {s: (7.25 if s == "NQ" else 5.0) for s in SYMS}
RA.WINDOWS.setdefault("NG", (tuple(range(1, 13)), 15, 31)); RA.WINDOWS.setdefault("BTC", (tuple(range(1, 13)), 15, 31))
CACHE = "scratch_data/ml_fut_vwap_ratio.pkl"
print(__doc__.split("\n")[0])


def vwap(g, a, b):
    j0, j1 = jof(a), jof(b) + 1
    tp = (g.h[:, j0:j1] + g.l[:, j0:j1] + g.c[:, j0:j1]) / 3; v = g.v[:, j0:j1]
    ok = ~np.isnan(tp) & (v > 0); n = ok.sum(1)
    with np.errstate(all="ignore"):
        x = np.where(ok, tp * v, 0).sum(1) / np.where(ok, v, 0).sum(1)
    x[n < 30] = np.nan
    return x


if os.path.exists(CACHE):
    VE, VR = pickle.load(open(CACHE, "rb"))
else:
    VE, VR = {}, {}
    for s in SYMS:
        g = Grid24() if s == "NQ" else Grid24(f"data/{s}_1min_20*.csv", night_pattern="")
        J = RA.roll_jumps(g, s); rows = np.arange(g.D) * 1440
        cf = pd.Series(g.c.ravel()).ffill().to_numpy()
        adj_e = np.ones(g.D); adj_r = np.ones(g.D)               # backward RATIO adjustment (the paper's): older prices x new / old
        for j, jump in J.items():
            prev = cf[j - 1]; fac = (prev + jump) / prev
            adj_e[rows + jof(930) < j] *= fac; adj_r[rows + jof(1031) < j] *= fac
        idx = pd.DatetimeIndex(g.ts)
        VE[s] = pd.Series(vwap(g, 831, 930) * adj_e, idx); VR[s] = pd.Series(vwap(g, 932, 1031) * adj_r, idx)
        print(f"   {s}: {len(J)} rolls removed", flush=True)
    pickle.dump((VE, VR), open(CACHE, "wb"))
VE = pd.DataFrame(VE); VR = pd.DataFrame(VR)
days = VE.index[(VE.notna().sum(1) >= 5) & (VE.index.dayofweek < 5) & (VE.index >= "2017-01-01")]
VE, VR = VE.loc[days], VR.loc[days]
LAGS = list(range(1, 21)) + list(range(40, 241, 20))
F = {l: VE / VR.shift(l) - 1 for l in LAGS}
FWD = VE.shift(-1) / VR - 1                                       # the h = 1 trade entered at Vr_t
bad = (FWD.abs() > 0.25).sum().sum(); print(f"   sanity: {bad} trade returns beyond +-25% (data errors if any)"); FWD = FWD.where(FWD.abs() <= 0.25)
cost_bp = pd.DataFrame({s: 1e4 * (COMM[s] + 2 * SPEC[s][0] * SPEC[s][1]) / (SPEC[s][0] * VR[s]) for s in SYMS})
print(f"\n   days {days[0].date()} .. {days[-1].date()} ({len(days)}); median round-trip cost bp: "
      + ", ".join(f"{s} {cost_bp[s].median():.1f}" for s in SYMS))


def picks_from(score):
    """score DataFrame (higher = long). Returns long / short symbol per day (NaN-safe, needs >= 5 markets with a score and a trade)."""
    sc = score.where(FWD.notna()); L, S = {}, {}
    for d, r in sc.iterrows():
        r = r.dropna()
        if len(r) >= 5: L[d] = r.idxmax(); S[d] = r.idxmin()
    return pd.Series(L), pd.Series(S)


def pnl(L, S):
    d = L.index
    lg = np.array([FWD.at[x, L[x]] for x in d]) * 1e4; sh = -np.array([FWD.at[x, S[x]] for x in d]) * 1e4
    cl = np.array([cost_bp.at[x, L[x]] for x in d]); cs = np.array([cost_bp.at[x, S[x]] for x in d])
    return pd.DataFrame(dict(long=lg, short=sh, gross=(lg + sh) / 2, net=(lg - cl + sh - cs) / 2, lsym=L.values, ssym=S.values), index=d)


def tt(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def report(nm, P, extra=""):
    y = P.index.year; n = P.net
    by = " ".join(f"{yy % 100:02d}:{n[y == yy].mean():+5.1f}" for yy in sorted(set(y)))
    print(f"   {nm:<26} n {len(P):4d} | gross {P.gross.mean():+5.1f} bp t {tt(P.gross):4.1f} | net {n.mean():+5.1f} bp t {tt(n):4.1f} "
          f"Sharpe {n.mean() / n.std() * np.sqrt(252):5.2f} | long {P.long.mean():+5.1f} short {P.short.mean():+5.1f} | "
          f"18-22 {n[y <= 2022].mean():+5.1f} (t {tt(n[y <= 2022]):4.1f}) 23+ {n[y >= 2023].mean():+5.1f} (t {tt(n[y >= 2023]):4.1f}){extra}")
    print(f"      by year (net bp): {by}")


# ---- model-free rules over the SAME days as the models' trading periods and over the whole sample
R1 = F[1]; sd = R1.rolling(20, min_periods=15).std().shift(1)
rules = {"A1 reversal raw": -R1, "A2 reversal / sd20": -R1 / sd}

# ---- rolling ML
from sklearn.linear_model import LogisticRegressionCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
X = np.stack([F[l].values for l in LAGS], axis=2)                   # (days, syms, 31)
Yv = FWD.values; med = np.nanmedian(np.where(np.isnan(X[:, :, 0]), np.nan, Yv), axis=1)
Y = (Yv > med[:, None]).astype(float); Y[np.isnan(Yv)] = np.nan
valid = ~np.isnan(X).any(2)
first = int(np.argmax(valid.sum(1) >= 5)); probs = {m: pd.DataFrame(np.nan, index=days, columns=SYMS) for m in ("LR", "RF", "GBC")}
t0 = first
while t0 + 750 < len(days):
    tr = np.arange(t0, t0 + 749); te = np.arange(t0 + 750, min(t0 + 1000, len(days)))
    m = valid[tr] & ~np.isnan(Y[tr]); Xtr = X[tr][m]; ytr = Y[tr][m]
    mods = {"LR": LogisticRegressionCV(Cs=np.logspace(-4, 5, 100), cv=5, max_iter=100, penalty="l2"),
            "RF": RandomForestClassifier(n_estimators=1000, max_depth=20, max_features="sqrt", random_state=1, n_jobs=-1),
            "GBC": GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=1)}
    for nm, mod in mods.items():
        mod.fit(Xtr, ytr)
        for i in te:
            ok = valid[i]
            if ok.sum(): probs[nm].iloc[i, np.flatnonzero(ok)] = mod.predict_proba(X[i][ok])[:, 1]
    print(f"   period train {days[tr[0]].date()}..{days[tr[-1]].date()} ({len(ytr)} rows) -> trade {days[te[0]].date()}..{days[te[-1]].date()}", flush=True)
    t0 += 250

trade_days = probs["RF"].dropna(how="all").index
print(f"\n== k = 1, h = 1, out-of-sample days {trade_days[0].date()} .. {trade_days[-1].date()} (bp a day of the long-short book)")
res = {}
for nm in ("LR", "RF", "GBC"):
    L, S = picks_from(probs[nm].loc[trade_days]); res[nm] = pnl(L, S); report(nm, res[nm])
for nm, sc in rules.items():
    L, S = picks_from(sc.loc[trade_days]); res[nm] = pnl(L, S); report(nm + " (same days)", res[nm])
mkt = (FWD.loc[trade_days] * 1e4 - cost_bp.loc[trade_days]).mean(1)
print(f"   {'MKT (long all, net)':<26} n {len(mkt):4d} | net {mkt.mean():+5.1f} bp t {tt(mkt):4.1f}")

print("\n== Model-free rules, whole sample 2018-2026 (thresholds none, nothing fitted)")
for nm, sc in rules.items():
    L, S = picks_from(sc.loc[sc.index >= "2018-01-01"]); report(nm, pnl(L, S))

print("\n== Placebo: random top / flop picks on the same days (1000 draws), net bp a day")
rng = np.random.default_rng(1); avail = FWD.loc[trade_days].notna().values; draws = []
F1 = FWD.loc[trade_days].values * 1e4; C1 = cost_bp.loc[trade_days].values
for _ in range(1000):
    tot = []
    for i in range(len(trade_days)):
        a = np.flatnonzero(avail[i])
        if len(a) < 5: continue
        l, s = rng.choice(a, 2, replace=False); tot.append((F1[i, l] - C1[i, l] - F1[i, s] - C1[i, s]) / 2)
    draws.append(np.mean(tot))
draws = np.array(draws)
for nm, P in res.items():
    print(f"   {nm:<26} net {P.net.mean():+5.1f} bp vs random p50 {np.median(draws):+5.1f}, p95 {np.percentile(draws, 95):+5.1f}: rank {np.mean(draws < P.net.mean()):.1%}")
print("\n== Which markets the best model picks (share of days)")
for nm in ("RF", "A2 reversal / sd20"):
    P = res[nm]; print(f"   {nm}: long " + ", ".join(f"{k} {v:.0%}" for k, v in P.lsym.value_counts(normalize=True).items())
                      + " | short " + ", ".join(f"{k} {v:.0%}" for k, v in P.ssym.value_counts(normalize=True).items()))

print("\n== Control added after the first look (disclosed): is the ML edge a volatility tilt? (long the highest 20-day sd, short the lowest)")
VOLS = sd                                                            # 20-day sd of R^1, lagged one day
for nm, sc in (("V long hi-vol / short lo-vol", VOLS), ("V reverse (long lo-vol)", -VOLS)):
    L, S = picks_from(sc.loc[trade_days]); P = pnl(L, S); report(nm + " (same days)", P)
    L, S = picks_from(sc.loc[sc.index >= "2018-01-01"]); report(nm + " 2018-26", pnl(L, S))
print("\n== Risk-scaled version of the models (each leg divided by its market's 20-day sd, x the median sd): vol tilt removed")
msd = np.nanmedian(sd.values)
for nm in ("RF", "GBC"):
    P = res[nm]; sl = np.array([sd.at[d, s] for d, s in zip(P.index, P.lsym)]); ss = np.array([sd.at[d, s] for d, s in zip(P.index, P.ssym)])
    cl = np.array([cost_bp.at[d, s] for d, s in zip(P.index, P.lsym)]); cs = np.array([cost_bp.at[d, s] for d, s in zip(P.index, P.ssym)])
    Q = pd.DataFrame(dict(long=(P.long - cl) / sl * msd, short=(P.short - cs) / ss * msd), index=P.index)
    Q["gross"] = (P.long / sl + P.short / ss) / 2 * msd; Q["net"] = (Q.long + Q.short) / 2; report(nm + " risk-scaled", Q)
