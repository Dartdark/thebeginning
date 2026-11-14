"""KAMA_TrendFollowing (user's Jesse strategy, 2026-11-14; pre-registered checks/candidates/kama_trend/PREREG.md): BTC spot + NQ, ingredient
breakdown, random-side placebo; NQ trades saved for the data sweep. Reuses the EMBIA_V3 harness (bars, Wilder ATR / ADX, 1-min walk, costs).
  tools/run_stamped.sh analysis/kama_trend_test.py > analysis/outputs/kama_trend_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
src = open("analysis/embia_v3_test.py").read().split("RES = {}")[0]; exec(compile(src, "embia_head", "exec"))
print(__doc__.split("\n")[0])


def kama(c, er_n=10, fast=2, slow=30):
    out = np.full(len(c), np.nan); fsc, ssc = 2 / (fast + 1), 2 / (slow + 1)
    for i in range(er_n, len(c)):
        ch = abs(c[i] - c[i - er_n]); vol = np.sum(np.abs(np.diff(c[i - er_n:i + 1])))
        sc = ((ch / vol if vol > 0 else 0) * (fsc - ssc) + ssc) ** 2
        out[i] = c[i - 1] + sc * (c[i] - c[i - 1]) if np.isnan(out[i - 1]) else out[i - 1] + sc * (c[i] - out[i - 1])
    return out


def kbars(m, tf):
    b = bars(m, tf); c = b.c.values; b["kama"] = kama(c)
    pc = np.r_[np.nan, c[:-1]]; tr = np.nanmax(np.c_[b.h - b.l, np.abs(b.h - pc), np.abs(b.l - pc)], axis=1)
    rng_ = b.h.rolling(14).max() - b.l.rolling(14).min()
    b["chop"] = 100 * np.log10(pd.Series(tr, index=b.index).rolling(14).sum() / rng_) / np.log10(14)
    mid = b.c.rolling(20).mean(); sd = b.c.rolling(20).std(ddof=0); b["bbw"] = (4 * sd) / mid
    return b


def ksignals(m, tf, drop=None):
    b = kbars(m, tf); H = kbars(m, "4h")[["kama"]].rename(columns={"kama": "H_kama"})
    b = pd.merge_asof(b, H, left_index=True, right_index=True, direction="backward")
    def on(k): return drop != k
    L_ = np.ones(len(b), bool); S_ = np.ones(len(b), bool)
    if on("kama"): L_ &= b.c > b.kama; S_ &= b.c < b.kama
    if on("adx"): L_ &= b.adx > 50; S_ &= b.adx > 50
    if on("ltkama"): L_ &= b.c > b.H_kama; S_ &= b.c < b.H_kama
    if on("chop"): L_ &= b.chop < 50; S_ &= b.chop < 50
    if on("bbw"): L_ &= b.bbw * 100 < 7; S_ &= b.bbw * 100 < 7
    ok = b[["kama", "H_kama", "adx", "chop", "bbw", "atr"]].notna().all(axis=1)
    side = np.where(L_ & ok, 1, np.where(S_ & ok, -1, 0)); return b, side


def ksim(m, tf, cost_fn, drop=None, flat=None, no_entry=None, rng=None):
    """one position at a time; cooldown = 10 base bars after the last position CLOSED (the code's last_trade_index)."""
    b, side = ksignals(m, tf, drop); bt = b.index.values; tsm = m.index.values; o, h, l, c = (m[k].values for k in ("o", "h", "l", "c"))
    atrv = b.atr.values; out = []; busy_t = np.datetime64("1970-01-01"); last_close_bar = -10 ** 9; n = len(o)
    for k in np.flatnonzero(side != 0):
        if bt[k] <= busy_t: continue
        if drop != "cooldown" and k - last_close_bar < 10: continue
        i = np.searchsorted(tsm, bt[k], side="right")
        if i >= n - 1 or (no_entry is not None and no_entry[i]) or tsm[i] - tsm[i - 1] > np.timedelta64(10, "m"): continue
        s = int(side[k]) if rng is None else int(rng.choice([-1, 1]))
        e = o[i]; sp = e - s * 2.5 * atrv[k]; tp = e + s * 2.5 * atrv[k]; ex = None
        for j in range(i, n):
            if (l[j] <= sp) if s > 0 else (h[j] >= sp): ex = (min(o[j], sp) if s > 0 else max(o[j], sp)) if j > i else sp; why = "stop"; break
            if (h[j] >= tp) if s > 0 else (l[j] <= tp): ex = tp; why = "tgt"; break
            if flat is not None and flat[j]: ex = c[j]; why = "flat"; break
        if ex is None: break
        out.append((pd.Timestamp(tsm[i]), s, e, ex, why, cost_fn(e, ex, s, why), j - i)); busy_t = tsm[j]
        last_close_bar = np.searchsorted(bt, tsm[j], side="left")              # the base bar in which the position closed
    return pd.DataFrame(out, columns=["ts", "side", "entry", "exit", "why", "net", "mins"])


RES = {}
for mk, M, cost, extra in (("BTC spot", BTC, btc_cost, {}), ("NQ as coded (holds overnight)", NQ, nq_cost, {}),
                           ("NQ Apex (flat 15:55, no entries 15:00-17:00)", NQ, nq_cost, dict(flat=apex_flat, no_entry=apex_noentry))):
    print(f"\n################ {mk}")
    for tf in ("1h", "15min"):
        T = ksim(M, tf, cost, **extra); T = T[T.ts >= "2018-01-01"]
        print(line(T, f"{tf} {'PRIMARY' if tf == '1h' else 'secondary'}")); print(by_year(T))
        print(f"      exits " + ", ".join(f"{k} {v}" for k, v in T.why.value_counts().items()) + f"; median hold {T.mins.median():.0f} min; {len(T) / 8.85:.0f} trades a year")
        RES[(mk, tf)] = T
    rng = np.random.default_rng(1); base = RES[(mk, "1h")].net.mean()
    pl = np.array([ksim(M, "1h", cost, rng=rng, **extra).pipe(lambda P: P[P.ts >= "2018-01-01"].net.mean()) for _ in range(40)])
    print(f"   random side, same entries (40 runs): mean ${pl.mean():.1f}, p95 ${np.percentile(pl, 95):.1f} -> real ${base:.1f}: p {np.mean(pl >= base):.3f}")
    print("   ingredient breakdown (1h, one condition removed at a time):")
    for k in ("kama", "adx", "ltkama", "chop", "bbw", "cooldown"):
        T = ksim(M, "1h", cost, drop=k, **extra); print(line(T[T.ts >= "2018-01-01"], f"without {k}"))
T = RES[("NQ as coded (holds overnight)", "1h")]
T.assign(date=T.ts.dt.normalize(), entry_date=T.ts.dt.normalize())[["date", "entry_date", "net", "side"]].to_csv("checks/candidates/kama_trend/trades_nq.csv", index=False)
