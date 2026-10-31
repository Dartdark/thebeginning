"""VWAP Drift Continuation (user's PowerLanguage file + write-up, 2026-10-25; checks/candidates/vwap_drift/). Final settings from
the write-up: EntryMode 2 (enter on the context bar), no new entries from 14:00 CT, MaxSLusd 2550, ADX(14) >= 20, SL 3 x ATR,
TP 1.5 x ATR long / 1.9 x ATR short, max 3 trades and 1 loss a day. Rebuild on our 24-hour 1-minute grids (CT, close-stamped):
  Data1 = clock-aligned 15-minute bars, Data2 = 60-minute bars. Session VWAP from the 15-minute bars closing 08:45-16:30,
  reset at midnight, typical price x volume. At each 60-minute close (a 15-minute bar closing on the hour): anchor = session
  VWAP now, previous anchor = VWAP at the previous hourly update the same day (first update: equal -> no slope);
  drift = 60-min close vs 6 hours earlier. Long context: 60-min close > VWAP, VWAP rising, drift >= +0.15%; short mirror.
  justArmed is set at every hourly update where the context holds (the code does not require a change), so the rule enters
  at any hourly close 08:30 <= time < 14:00 while flat and the context holds, if ADX(14) on the 15-minute bars >= 20.
  Entry: the next 15-minute bar's open. Stop pts = 3 x ATR(12) of 15-minute bars (simple average true range), clamped to
  25-150 pts; target 1.5 / 1.9 x ATR. Stop live from the entry minute (the money-management backstop), target from the next
  15-minute bar. Flat at the 16:00 close (SetExitOnClose; FlatTime 1555 on 15-minute bars); Apex needs 15:59 -> also 15:30.
  Fills on 1-minute bars (like the Bar Magnifier): a stop the minute opens beyond fills at the open; stop and target in one
  minute = stop.
Per 1 MNQ ($2 a point). Costs: ours ($0.725 + 1 tick per market / stop fill), the author's ($1.50 + $3 a side).
Windows: the author's IS 2020-07 .. 2023, OOS 2024 .. 2026-07, and our untouched pre-period 2018-01 .. 2020-06.
  python3 analysis/vwap_drift_test.py [SCRATCH_DIR] > analysis/outputs/vwap_drift_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from numba import njit
import metrics as M, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
NTR = {"n": 0}


def load(name):
    g = pickle.load(open(SP + name + ".pkl", "rb"))
    O, H, L, C, Vv = (getattr(g, k).ravel() for k in ("o", "h", "l", "c", "v"))
    return g, O, H, L, C, np.nan_to_num(Vv)


def bars(O, H, L, C, V, k):
    n = len(C) // k * k
    o, h, l, c, v = (x[:n].reshape(-1, k) for x in (O, H, L, C, V))
    ok = ~np.isnan(c).all(1)
    with np.errstate(all="ignore"):
        hh, ll = np.nanmax(h, 1), np.nanmin(l, 1)
    first = np.argmax(~np.isnan(o), 1); last = k - 1 - np.argmax(~np.isnan(c[:, ::-1]), 1)
    oo = o[np.arange(len(o)), first]; cc = c[np.arange(len(c)), last]
    end = np.arange(len(c)) * k + k - 1                                   # flat index of the bar's last minute slot
    s = np.where(ok)[0]
    return dict(o=oo[s], h=hh[s], l=ll[s], c=cc[s], v=v.sum(1)[s], end=end[s])


def adx_wilder(h, l, c, n=14):
    up = np.r_[0, np.diff(h)]; dn = np.r_[0, -np.diff(l)]
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    pc = np.r_[c[0], c[:-1]]; tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    a = 1.0 / n
    atr = pd.Series(tr).ewm(alpha=a, adjust=False).mean(); p = pd.Series(pdm).ewm(alpha=a, adjust=False).mean()
    m = pd.Series(mdm).ewm(alpha=a, adjust=False).mean()
    pdi, mdi = 100 * p / atr, 100 * m / atr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=a, adjust=False).mean().to_numpy(), tr


@njit(cache=True)
def walk(O, H, L, C, start, side, sp, tp, tp_from, flat_idx):
    n = len(start); out = np.full((n, 4), np.nan)
    for t in range(n):
        k = start[t]
        while k < len(O) and np.isnan(O[k]): k += 1
        e = O[k]; s = side[t]; stop = e - s * sp[t]; tgt = e + s * tp[t]
        j = k; xp = np.nan; kind = -1
        while j <= flat_idx[t]:
            if np.isnan(O[j]):
                j += 1; continue
            if (s > 0 and L[j] <= stop) or (s < 0 and H[j] >= stop):
                xp = min(O[j], stop) if s > 0 else max(O[j], stop)
                if j == k: xp = stop
                kind = 0; break
            if j >= tp_from[t] and ((s > 0 and H[j] >= tgt) or (s < 0 and L[j] <= tgt)):
                xp = max(O[j], tgt) if s > 0 else min(O[j], tgt); kind = 1; break
            j += 1
        if kind < 0:
            jj = flat_idx[t]
            while jj > k and np.isnan(C[jj]): jj -= 1
            xp = C[jj]; kind = 2; j = jj
        out[t, 0] = e; out[t, 1] = xp; out[t, 2] = kind; out[t, 3] = j
    return out


def run(name, pv=2.0, tick=0.25, comm=0.725, slip_ticks=1, side_cost=None, sess_end=1400, flat=1600, drift_th=0.15, adx_th=20.0,
        sl_atr=3.0, tpl=1.5, tps=1.9, min_sp=25.0, max_sp=150.0, entry_mode=2, max_tr=3, max_loss=1, cache={}, count=True):
    if count: NTR["n"] += 1
    if name not in cache:
        g, O, H, L, C, V = load(name)
        B15 = bars(O, H, L, C, V, 15); B60 = bars(O, H, L, C, V, 60)
        cache[name] = (g, O, H, L, C, V, B15, B60)
    g, O, H, L, C, V, B15, B60 = cache[name]
    ts = pd.DatetimeIndex(np.asarray(g.ts)[B15["end"] // 1440]); mod = B15["end"] % 1440 + 1          # close minute of day
    hhmm = (mod // 60) * 100 + mod % 60
    day = B15["end"] // 1440
    tp_ = (B15["h"] + B15["l"] + B15["c"]) / 3
    inv = (hhmm > 830) & (hhmm <= 1630)
    pv_cum = pd.Series(np.where(inv, tp_ * B15["v"], 0)).groupby(day).cumsum().to_numpy()
    v_cum = pd.Series(np.where(inv, B15["v"], 0)).groupby(day).cumsum().to_numpy()
    vwap = np.where(v_cum > 0, pv_cum / np.maximum(v_cum, 1), 0)
    adx, tr = adx_wilder(B15["h"], B15["l"], B15["c"])
    atr = pd.Series(tr).rolling(12).mean().to_numpy()
    # hourly updates: the 15-min bar whose close is a 60-min bar close
    i60 = np.searchsorted(B15["end"], B60["end"]); ok = (i60 < len(B15["end"])) & (B15["end"][np.minimum(i60, len(B15["end"]) - 1)] == B60["end"])
    upd = np.zeros(len(B15["c"]), bool); upd[i60[ok]] = True
    c60 = np.full(len(B15["c"]), np.nan); c60[i60[ok]] = B60["c"][ok]
    c60_6 = np.full(len(B15["c"]), np.nan); c60_6[i60[ok]] = pd.Series(B60["c"]).shift(6).to_numpy()[ok]
    rows = []
    prev_anchor = {}; ntr = {}; nloss = {}
    for i in np.where(upd)[0]:
        d = day[i]
        if vwap[i] <= 0: continue
        pa = prev_anchor.get(d, vwap[i]); prev_anchor[d] = vwap[i]
        drift = (c60[i] - c60_6[i]) / c60_6[i] * 100
        side = 0
        if c60[i] > vwap[i] and vwap[i] > pa and drift >= drift_th: side = 1
        elif c60[i] < vwap[i] and vwap[i] < pa and drift <= -drift_th: side = -1
        if side == 0 or not (830 <= hhmm[i] < sess_end) or not (adx[i] >= adx_th) or np.isnan(atr[i]): continue
        rows.append((i, d, side))
    S = pd.DataFrame(rows, columns=["i", "d", "side"])
    S["sp"] = np.clip(sl_atr * atr[S.i], min_sp, max_sp); S["tp"] = np.where(S.side > 0, tpl, tps) * atr[S.i]
    S["start"] = B15["end"][S.i] + 1; S["tp_from"] = S.start + 15
    S["flat_idx"] = S.d * 1440 + (flat // 100 * 60 + flat % 100) - 1
    W = walk(O, H, L, C, S.start.to_numpy(np.int64), S.side.to_numpy(np.int64), S.sp.to_numpy(float), S.tp.to_numpy(float),
             S.tp_from.to_numpy(np.int64), S.flat_idx.to_numpy(np.int64))
    S["e"], S["x"], S["kind"], S["xj"] = W.T
    # sequential rules: one position at a time, max trades / losses a day (an entry needs the previous trade closed)
    keep = []; busy_until = -1; cnt = {}; los = {}
    for r in S.itertuples():
        if r.start <= busy_until: continue
        if cnt.get(r.d, 0) >= max_tr or los.get(r.d, 0) >= max_loss: continue
        keep.append(r.Index); cnt[r.d] = cnt.get(r.d, 0) + 1
        g_ = (r.x - r.e) * r.side
        if g_ < 0: los[r.d] = los.get(r.d, 0) + 1
        busy_until = r.xj
    T = S.loc[keep].copy()
    T["date"] = pd.DatetimeIndex(np.asarray(g.ts)[T.d])
    T["gross"] = (T.x - T.e) * T.side * pv
    fills = 1 + (T.kind != 1).astype(int)
    T["net"] = T.gross - (comm + fills * slip_ticks * tick * pv if side_cost is None else 2 * side_cost)
    return T.set_index("date")


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def win(T, a, b):
    return T[(T.index >= a) & (T.index <= b)]


def line(T, nm, w=40):
    if len(T) < 5: return f"   {nm:<{w}} n={len(T)}"
    x = T.net; L, S_ = x[T.side > 0], x[T.side < 0]
    pre, is_, oos = win(T, "2018-01-01", "2020-06-30").net, win(T, "2020-07-01", "2023-12-31").net, win(T, "2024-01-01", "2026-12-31").net
    return (f"   {nm:<{w}} n={len(x):5d} ${x.mean():6.2f}/MNQ PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} | pre 18-20H1 PF {pf(pre):4.2f} "
            f"t {tst(pre):4.1f} | IS 20-23 PF {pf(is_):4.2f} t {tst(is_):4.1f} | OOS 24-26 PF {pf(oos):4.2f} t {tst(oos):4.1f} | "
            f"L {len(L)} ${L.mean():5.2f} S {len(S_)} ${S_.mean():5.2f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    T = run("g24"); T = T[T.index >= "2018-01-01"]      # one evaluation window for trade AND daily stats (fix 2026-10-25, Codex review finding 4)
    a = win(T, "2020-07-02", "2026-07-24")
    print(f"\n1. NQ data, per 1 MNQ, our costs. The author's window 2020-07-02 .. 2026-07-24: {len(a)} trades (author 1,677), "
          f"PF {pf(a.net):.2f} (author 1.22), win {np.mean(a.net > 0):.1%} (59.7%); author's costs: PF {pf(win(run('g24', side_cost=4.5, count=False), '2020-07-02', '2026-07-24').net):.2f}")
    print(line(T, "rule (our costs)"))
    print(line(run("g24", side_cost=4.5), "author's costs ($1.50 + $3 a side)"))
    print("   by year $ per MNQ:", T.net.groupby(T.index.year).sum().round(0).astype(int).to_dict())
    print("   longs by year:", T.net[T.side > 0].groupby(T.index[T.side > 0].year).sum().round(0).astype(int).to_dict())
    print("   shorts by year:", T.net[T.side < 0].groupby(T.index[T.side < 0].year).sum().round(0).astype(int).to_dict())
    print("   exits:", T.kind.map({0: "stop", 1: "target", 2: "flat"}).value_counts().to_dict())
    print("\n2. Settings the author tuned on IS / OOS (the pre-2020 window was never seen):")
    for nm, kw in (("entries to 15:00 (before the cutoff)", dict(sess_end=1500)), ("no ADX gate", dict(adx_th=0)),
                   ("ADX >= 25", dict(adx_th=25)), ("drift 0.10%", dict(drift_th=0.10)), ("drift 0.25%", dict(drift_th=0.25)),
                   ("SL 2 ATR", dict(sl_atr=2.0)), ("SL 4 ATR", dict(sl_atr=4.0)), ("TP 1.0 / 1.0 ATR", dict(tpl=1.0, tps=1.0)),
                   ("TP 2.5 / 2.5 ATR", dict(tpl=2.5, tps=2.5)), ("flat 15:30 (Apex-safe)", dict(flat=1530))):
        print(line(run("g24", **kw), nm))
    print("\n3. ES, the same parameters (per 1 MES, $5 a point; our ES costs $0.50 + 1 tick):")
    TE = run("ge", pv=5.0, comm=0.5, min_sp=25 / 3.5, max_sp=150 / 3.5)
    print(line(TE, "ES rule (per 1 MES)"))
    print("   ES longs by year:", TE.net[TE.side > 0].groupby(TE.index[TE.side > 0].year).sum().round(0).astype(int).to_dict())
    print("   ES shorts by year:", TE.net[TE.side < 0].groupby(TE.index[TE.side < 0].year).sum().round(0).astype(int).to_dict())
    print("\n4. Long / short and market drift: the RTH move (08:30 -> 15:00) on signal days by side, NQ:")
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(f"   NQ 2024-26 average RTH day {np.nanmean([(g.c[r, 900] - g.o[r, 511]) for r in g.trading if g.dates[r] >= 20240101]):+.1f} pts; "
          f"long trades 2024-26 ${T.net[(T.side > 0) & (T.index >= '2024-01-01')].mean():.2f}, shorts ${T.net[(T.side < 0) & (T.index >= '2024-01-01')].mean():.2f}")
    print("\n5. Metrics (per 1 MNQ, our costs) and Monte Carlo at 3 MNQ:")
    days = pd.DatetimeIndex(np.asarray(g.ts)[g.trading]); days = days[days >= "2018-01-01"]
    dd = T.net.groupby(T.index).sum().reindex(days, fill_value=0.0)
    print(M.table({"whole 2018-26": (dd, T.net), "longs": (T.net[T.side > 0].groupby(T.index[T.side > 0]).sum().reindex(days, fill_value=0), T.net[T.side > 0]),
                   "shorts": (T.net[T.side < 0].groupby(T.index[T.side < 0]).sum().reindex(days, fill_value=0), T.net[T.side < 0]),
                   "2023+": (dd[dd.index >= "2023-01-01"], T.net[T.index >= "2023-01-01"])}))
    print(MC.report(T.net.values, daily=dd.values, size=3.0, label="VWAP drift 3 MNQ"))
    import io, contextlib, runpy
    with contextlib.redirect_stdout(io.StringIO()):
        gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
    P = gg["P"]; s = dd.reindex(P.index, fill_value=0)
    print(f"   daily corr with our 17-piece personal book {np.corrcoef(s, P.sum(axis=1))[0, 1]:+.2f}; with Dual Thrust {np.corrcoef(s, P['DualThrust'])[0, 1]:+.2f}, "
          f"Vault Break {np.corrcoef(s, P['VaultBreak'])[0, 1]:+.2f}")
    print(f"\n   variants run here: {NTR['n']}; t threshold at that count {M.t_threshold(NTR['n']):.2f}")
