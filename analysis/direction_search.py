"""Search for a new daily direction signal for NQ (2026-10-12), independent of Overnight Bias.

Every feature is known by the 8:30 CT open (except the 'first 15 minutes' family, known at 8:45).
Target: NQ 8:30 open -> 15:00 close in $ per NQ (8:45 -> 15:00 for the 8:45 features).
Score of a feature: trade its sign (or its top/bottom third, thresholds from the design years only)
every day; $ per day, t-stat, years positive; design 2018-2022, holdout 2023-2026.
Overlap with Overnight Bias: agreement of the signal with ONB's bias (open in top / bottom third
of the 23:00-8:30 range) on days both are non-zero, and correlation of the daily P&L.
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
PV = 20.0
tr = g.trading; dts = pd.DatetimeIndex(g.ts[tr])
erow = pd.Series(np.arange(es.D), index=pd.DatetimeIndex(es.ts))


def at(G, rows, j, f="c"):
    return getattr(G, f)[rows, j]


def first_valid(a):            # first non-nan along axis 1
    i = np.argmax(~np.isnan(a), 1); return a[np.arange(len(a)), i]


def last_valid(a):
    i = a.shape[1] - 1 - np.argmax(~np.isnan(a[:, ::-1]), 1); return a[np.arange(len(a)), i]


def session(G, rows, prev_from=None, j_from=0, j_to=510):
    """OHLCV pieces of the window [prev row prev_from..23:59] + [row j_from..j_to]."""
    parts = []
    if prev_from is not None: parts.append(slice(prev_from, 1440, rows - 1))
    out = {}
    for k in ("o", "h", "l", "c", "v"):
        A = getattr(G, k)
        seg = A[rows, j_from:j_to + 1]
        if prev_from is not None: seg = np.concatenate([A[rows - 1, prev_from:], seg], 1)
        out[k] = seg
    return out


def feats(G, rows, prev_rth_rows):
    o830 = at(G, rows, 511, "o"); c1500 = at(G, rows, 900)
    pc = at(G, prev_rth_rows, 900)                                   # previous RTH 15:00 close
    on = session(G, rows, prev_from=1020, j_to=510)                  # 17:00 prev evening -> 8:30
    asia = session(G, rows, prev_from=1020, j_to=120)                # 17:00 -> 02:00
    eu = session(G, rows, j_from=121, j_to=510)                      # 02:00 -> 8:30
    F = {}
    F["gap"] = o830 - pc
    F["asia_ret"] = last_valid(asia["c"]) - first_valid(asia["o"])
    F["europe_ret"] = last_valid(eu["c"]) - first_valid(eu["o"])
    sv = np.nansum(on["v"] * np.sign(on["c"] - on["o"]), 1); tv = np.nansum(on["v"], 1)
    F["on_flow"] = sv / tv                                           # signed-volume imbalance
    path = np.nansum(np.abs(np.diff(on["c"], axis=1)), 1)
    F["on_eff"] = F["gap"] / path                                    # trend efficiency (signed)
    hi, lo = np.nanmax(on["h"], 1), np.nanmin(on["l"], 1)
    jhi = np.nanargmax(np.nan_to_num(on["h"], nan=-1e9), 1); jlo = np.nanargmax(np.nan_to_num(-on["l"], nan=-1e9), 1)
    F["on_hi_later"] = np.sign(jhi - jlo).astype(float)              # +1 if the ON high came after the low
    # previous RTH day
    ph, pl = np.nanmax(G.h[prev_rth_rows, 510:901], 1), np.nanmin(G.l[prev_rth_rows, 510:901], 1)
    F["prev_clv"] = (pc - pl) / (ph - pl) - 0.5
    F["prev_rth_ret"] = pc - at(G, prev_rth_rows, 511, "o")
    F["prev_last_hour"] = pc - at(G, prev_rth_rows, 840)
    F["prev_post_close"] = at(G, rows - 0, 0) * 0 + (last_valid(G.c[prev_rth_rows, 900:960]) - pc)  # 15:00-16:00
    return F, o830, c1500


prev = np.r_[tr[0] - 1, tr[:-1]]
F, o830, c1500 = feats(g, tr, prev)
y830 = (c1500 - o830) * PV
o845 = g.o[tr, 526]; y845 = (c1500 - o845) * PV
F["first15"] = g.c[tr, 525] - o830                                   # 8:30-8:45 (traded from 8:45)
# ES versions and NQ-ES relative strength (in % to compare)
er = erow.reindex(dts).to_numpy(); okE = ~np.isnan(er); er = np.nan_to_num(er).astype(int)
eprev = erow.reindex(pd.DatetimeIndex(g.ts[prev])).to_numpy(); eprev = np.nan_to_num(eprev).astype(int)
FE, eo830, _ = feats(es, er, eprev)
for k in ("gap", "europe_ret", "asia_ret", "on_flow"):
    F["es_" + k] = np.where(okE, FE[k], np.nan)
F["nq_minus_es_gap%"] = F["gap"] / o830 - np.where(okE, FE["gap"] / eo830, np.nan)
F["nq_minus_es_prevday%"] = F["prev_rth_ret"] / o830 - np.where(okE, FE["prev_rth_ret"] / eo830, np.nan)
# multi-day momentum (RTH closes)
cl = pd.Series(at(g, tr, 900))
for n in (2, 5, 10, 20, 60):
    F[f"mom{n}"] = (cl.shift(1) - cl.shift(1 + n)).to_numpy()
F["ma50_dist"] = (cl.shift(1) - cl.shift(1).rolling(50).mean()).to_numpy()
# VIX (previous close)
vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE")["CLOSE"]
vx = vix.reindex(dts - pd.Timedelta(days=1), method="ffill").to_numpy()   # last close before the day
vxs = pd.Series(vx)
F["vix_chg"] = (vxs - vxs.shift(1)).to_numpy()
F["vix_vs_ma20"] = (vxs / vxs.rolling(20).mean() - 1).to_numpy()
# ONB bias for overlap
onh = np.fmax(np.nanmax(g.h[tr - 1, 1380:], 1), np.nanmax(g.h[tr, :511], 1))
onl = np.fmin(np.nanmin(g.l[tr - 1, 1380:], 1), np.nanmin(g.l[tr, :511], 1))
pos = (o830 - onl) / (onh - onl); onb = np.where(pos >= 2 / 3, 1, np.where(pos <= 1 / 3, -1, 0))

D = pd.DataFrame(F, index=dts); D["y830"] = y830; D["y845"] = y845; D["onb"] = onb
D = D[(D.index.year >= 2018) & ~np.isnan(D.y830) & ~np.isnan(D.y845)]
des = D.index.year <= 2022


def score(sig, y):
    p = sig * y; p = p[sig != 0]
    if len(p) < 50: return None
    yrs = p.groupby(p.index.year).sum()
    return p.mean(), p.mean() / p.std() * np.sqrt(len(p)), (yrs > 0).mean(), len(p)


rows = []
for k in [c for c in D.columns if c not in ("y830", "y845", "onb")]:
    x = D[k]; y = D.y845 if k == "first15" else D.y830
    lo, hi = x[des].quantile([1 / 3, 2 / 3])
    for mode in ("sign", "tercile"):
        for flip in (1, -1):
            s = np.sign(x) if mode == "sign" else pd.Series(np.where(x >= hi, 1, np.where(x <= lo, -1, 0)), index=x.index)
            s = (s * flip).fillna(0)
            a, b = score(s[des], y[des]), score(s[~des], y[~des])
            if a is None or b is None or a[0] <= 0: continue          # direction picked on the design years
            both = (s != 0) & (D.onb != 0)
            agree = (np.sign(s[both]) == D.onb[both]).mean()
            pc_ = np.corrcoef((s * y).fillna(0), (D.onb * D.y830).fillna(0))[0, 1]
            rows.append(dict(feature=k, mode=mode, dir="follow" if flip > 0 else "fade",
                             des_avg=a[0], des_t=a[1], des_yrs=a[2], hold_avg=b[0], hold_t=b[1], hold_yrs=b[2],
                             n_per_yr=(a[3] + b[3]) / 8.8, agree_onb=agree, corr_onb=pc_))
R = pd.DataFrame(rows).sort_values("des_t", ascending=False)
if __name__ == "__main__":
    print(__doc__.split("\n")[0]); print(f"features x modes scored: {len(R)} (direction chosen on 2018-22)")
    pd.set_option("display.width", 250)
    print(R.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
    D.to_pickle(SP + "dirfeat.pkl")
