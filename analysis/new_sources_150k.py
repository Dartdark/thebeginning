"""New, uncorrelated trade sources as small add-ons to the 150K plan (user 2026-11-08, 'like Twin cap1'). PRE-REGISTERED (header
committed before the first run; 5 trials). Each piece at 2 contracts (MNQ; gold: MGC), per-day worst point + close (the worst applied
from the day's start: conservative for the floor). Costs: $7.25 + 1 tick per fill per full contract.
  1 green-day overnight long: RTH 08:30 -> 15:00 up -> long at the 17:00 reopen (Mon-Thu), out 08:30 CT next morning, stop 0.5 x
    daily ATR15 (prior day). Overnight Tick trades after DOWN days, so the two never overlap.
  2 60-min double top (short) / bottom (long), WATCHLIST #30 rules (chart_patterns_test), exit after 4 bars / 14:59 / 1 ATR stop.
  3 gold Asian range on MGC: WATCHLIST #6 'filter B' (range 20:00-00:00 CT, orders cancelled 02:00, stop 1 x range, out 12:00 CT).
  4 Vol-Control Sell Flow (lab VCS_MC, MC trades), dropped from the plan in October.
  5 turn of the month: long NQ 08:30 open -> 15:00 close on the last trading day of a month and the first 3 of the next, stop 0.5 x ATR.
Benches: 150K evaluation set + piece (corrected engine; paired band, 60-day blocks); funded 150K plan x 1.5 (full from $3,000) +
piece, 600 paired bootstrap histories; daily correlation with the plan pieces. Twin cap1 2 MNQ (already adopted) shown for reference.
  tools/run_stamped.sh analysis/new_sources_150k.py > analysis/outputs/new_sources_150k_output.txt
"""
import sys, io, runpy, contextlib, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30
from plan_150k_test import evaluation, R150
from grid24 import jof
from candlestick_patterns_test import rth_bars
from chart_patterns_test import pivots_signals
import asian_breakout_test as AB
from gold_asian_breakout_gc_test import load_gc
import twin_continuation_test as tc
from twin_continuation_bench import grids
import funded_sim150 as F

PV, TICK, COMM = 20.0, 0.25, 7.25


def daypaths(D, items):
    """items: list of (trading index, worst $, net $) per 1 full contract -> per-micro (W, R) arrays (D, 1440)."""
    W = np.zeros((D, 1440)); R = np.zeros((D, 1440)); wd = np.zeros(D); cd = np.zeros(D)
    for i, w, n in items:
        if i is None: continue
        wd[i] = min(wd[i], cd[i] + min(w, n)); cd[i] += n
    W[:] = np.minimum(wd, cd)[:, None] / 10; R[:, -1] = cd / 10
    return W, R


def path_exit(g, segs, side, e, stop):
    """segs: list of (row, j0, j1); returns (exit px, worst adverse px move) walking 1-min bars; stop at entry -/+ stop."""
    worst = 0.0; st = e - side * stop
    for r, a, b in segs:
        o, h, l, c = g.o[r, a:b + 1], g.h[r, a:b + 1], g.l[r, a:b + 1], g.c[r, a:b + 1]
        for m in range(len(c)):
            if np.isnan(c[m]): continue
            adv = (l[m] - e) if side > 0 else (e - h[m]); worst = min(worst, adv)
            if (l[m] <= st) if side > 0 else (h[m] >= st):
                return (min(o[m], st) if side > 0 else max(o[m], st)), worst
            last = c[m]
    return last, worst


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = list(g.trading); D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year; pos = {r: i for i, r in enumerate(trr)}; dts = pd.DatetimeIndex(g.ts[trr])
    J0, J1, J17 = jof(831), jof(1500), jof(1701)
    op, cl = g.o[trr, J0], g.c[trr, J1]
    pieces, nets = {}, {}
    # 1 green-day overnight long
    it = []
    for k in range(len(trr) - 1):
        r, r2 = trr[k], trr[k + 1]
        if not (cl[k] > op[k]) or dts[k].dayofweek == 4 or np.isnan(g.o[r, J17]) or dts[k].year < 2018: continue
        a = atr[r - 1] if r > 0 else np.nan
        if not np.isfinite(a): continue
        e = g.o[r, J17] + TICK; segs = [(r, J17, 1439)] + [(x, 0, 1439) for x in range(r + 1, r2)] + [(r2, 0, jof(830))]
        x, w = path_exit(g, segs, 1, e, 0.5 * a); x -= TICK
        it.append((k + 1, w * PV - COMM, (x - e) * PV - COMM))
    pieces["1 green-day overnight"] = daypaths(D, it); nets["1 green-day overnight"] = np.array([n for _, _, n in it])
    # 2 double top / bottom 60-min
    B = rth_bars(g, 60); S = pivots_signals(B); a60 = (B.h - B.l).rolling(14, min_periods=10).mean().to_numpy(); it = []
    for nm, s in (("DTOP", -1), ("DBOT", 1)):
        for i in np.nonzero(S[nm][0])[0]:
            r, j = int(B.row[i]), int(B.j[i])
            if r not in pos or pd.Timestamp(g.ts[r]) < pd.Timestamp("2018-01-01") or j >= jof(1430) or np.isnan(a60[i]): continue
            j0, j1 = j + 1, min(j + 240, jof(1459)); oo = g.o[r, j0:j1 + 1]; ok_ = ~np.isnan(oo)
            if not ok_.any(): continue
            e = oo[ok_][0] + s * TICK; x, w = path_exit(g, [(r, j0, j1)], s, e, a60[i]); x -= s * TICK
            it.append((pos[r], w * PV - COMM, (x - e) * s * PV - COMM))
    pieces["2 double top / bottom"] = daypaths(D, it); nets["2 double top / bottom"] = np.array([n for _, _, n in it])
    # 3 gold Asian range on MGC (per full GC, then /10 = MGC)
    gc = load_gc(); AB.SPEC["GC"] = (100.0, 0.10, 7.25); t = AB.run(gc, "GC", 2000, 200, 1200, 1.0, False)
    t = t[t.date >= "2018-01-01"]; H, L = gc.h.ravel(), gc.l.ravel(); dpos = pd.Series(np.arange(D), index=dts); it = []
    for r in t.itertuples():
        if r.date not in dpos.index: continue
        adv = (np.nanmin(L[r.t0:r.t1 + 1]) - r.entry) if r.side > 0 else (r.entry - np.nanmax(H[r.t0:r.t1 + 1]))
        it.append((int(dpos[r.date]), adv * 100.0 - 7.25, r.net))
    pieces["3 gold Asian range (MGC)"] = daypaths(D, it); nets["3 gold Asian range (MGC)"] = np.array([n for _, _, n in it])
    # 5 turn of the month
    mon = dts.month.to_numpy(); last = np.r_[mon[1:] != mon[:-1], False]; first = np.r_[False, mon[1:] != mon[:-1]]
    tom = np.zeros(D, bool)
    for k in range(D):
        if last[k]: tom[k] = True
        if first[k]: tom[k:k + 3] = True
    it = []
    for k in np.nonzero(tom & (yr >= 2018))[0]:
        r = trr[k]; a = atr[r - 1] if r > 0 else np.nan
        if np.isnan(op[k]) or not np.isfinite(a): continue
        e = g.o[r, J0] + TICK; x, w = path_exit(g, [(r, J0, J1)], 1, e, 0.5 * a); x -= TICK
        it.append((k, w * PV - COMM, (x - e) * PV - COMM))
    pieces["5 turn of the month"] = daypaths(D, it); nets["5 turn of the month"] = np.array([n for _, _, n in it])
    # lab (funded) + VCS + Twin reference
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    assert list(lab.tr) == trr
    pieces["4 Vol-Control Sell"] = (lab.W["VCS_MC"], np.concatenate([np.zeros((D, 1439)), lab.C["VCS_MC"][:, None]], axis=1))
    nets["4 Vol-Control Sell"] = lab.C["VCS_MC"][lab.C["VCS_MC"] != 0] * 10
    Bf = tc.flatten(g); TT = tc.simulate(Bf, max_stop_mult=1.0, v21=True); TT = TT[TT.date >= "2018-01-01"]; Wt, Rt = grids(g, Bf, TT)
    pieces["(ref) Twin cap1"] = (Wt[trr] / 10, Rt[trr] / 10); nets["(ref) Twin cap1"] = TT.net.to_numpy()
    print("\nPieces per full contract, 2018+:")
    for nm, x in nets.items():
        print(f"   {nm:<28} n {len(x):5d} ${x.mean():6.0f} t {x.mean() / x.std(ddof=1) * np.sqrt(len(x)):5.2f} worst ${x.min():,.0f}")
    dates = dts; Sp = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = Sp.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag; lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    Cplan = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR_MC")}, index=dates)[yr >= 2018]
    for nm, (W, R) in pieces.items():
        c = Cplan.corrwith(pd.Series(R[:, -1], index=dates)[yr >= 2018]); print(f"   corr {nm:<28} max {c.abs().max():.2f} ({c.abs().idxmax()})")
    # evaluation
    P = {}
    for k, t_ in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                  "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t_); P[k] = (w[trr] / 10, rr[trr] / 10)
    risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    base = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
    Wb = sum(P[k][0] * v for k, v in base.items()); Rb = sum(P[k][1] * v for k, v in base.items()); ok = yr >= 2018
    def ev(Wx, Rx):
        res = [evaluation(Wb + Wx, Rb + Rx, s, D, R150) for s in range(D)]
        return np.array([x[0] if x else "" for x in res]), ok & np.array([x is not None for x in res])
    o0, v0 = ev(0 * Wb, 0 * Rb); print(f"\n150K evaluation set alone: pass {(o0 == 'pass')[v0].mean():.1%}")
    for nm, (W, R) in pieces.items():
        o, v = ev(2 * W, 2 * R); ps = o == "pass"; d = (ps.astype(float) - (o0 == "pass").astype(float))[v & v0]
        rng = np.random.default_rng(1); nb = int(np.ceil(len(d) / 60)); st = rng.integers(0, len(d), (2000, nb))
        mm = d[((st[:, :, None] + np.arange(60)) % len(d)).reshape(2000, -1)[:, :len(d)]].mean(axis=1)
        print(f"   + {nm:<28} 2 units: pass {ps[v].mean():5.1%} (18-22 {ps[v & (yr < 2023)].mean():5.1%}, 23+ {ps[v & (yr >= 2023)].mean():5.1%})"
              f" | vs set {d.mean():+.1%} ({np.percentile(mm, 5):+.1%} / {np.percentile(mm, 95):+.1%})", flush=True)
    # funded
    for nm, (W, R) in pieces.items(): lab.W["X_" + nm] = W; lab.C["X_" + nm] = R[:, -1]
    PLAN = {"VB_N": 2, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda p, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in p.items()}
    V = {"plan x 1.5": sc(PLAN, 1.5)}
    for nm in pieces: V["+ " + nm] = {**sc(PLAN, 1.5), "X_" + nm: 2}
    keys = sorted({k for p in V.values() for k in p}); Wall = np.stack([lab.W[k] for k in keys]); Call = np.stack([lab.C[k] for k in keys])
    bases = {}
    for nm, p in V.items():
        names, b = lab._base(p); Bm = np.zeros((len(keys), lab.D))
        for i, k in enumerate(names): Bm[keys.index(k)] = b[i]
        bases[nm] = Bm
    chg = np.zeros(Wall.shape[2], bool); chg[-1] = True; chg[1:] |= (np.abs(np.diff(Wall, axis=2)) > 0).any(axis=(0, 1)); chg[0] |= (Wall[:, :, 0] != 0).any()
    Wc = np.ascontiguousarray(Wall[:, :, chg]); days = np.where(dates >= "2018-01-01")[0]; rng = np.random.default_rng(1); n, H, L_ = 600, 500, 20
    stb = rng.integers(0, len(days), (n, H // L_)); hist = days[((stb[:, :, None] + np.arange(L_)) % len(days)).reshape(n, -1)[:, :H]]
    Rr = {nm: np.zeros((n, 3)) for nm in V}
    for h in range(n):
        ix = hist[h]; Wh = np.ascontiguousarray(Wc[:, ix]); Ch = np.ascontiguousarray(Call[:, ix])
        for nm, Bm in bases.items():
            r = F.simulate_sized(Wh, Ch, np.ascontiguousarray(Bm[:, ix]), horizon=H, starts=[0], fmin=0.5, fmax=1.0, ref=3000.0)
            Rr[nm][h] = [r["paid"][0], r["blown"][0], r["payouts"][0] == 6]
    b0 = Rr["plan x 1.5"][:, 0]; print("\nFunded 150K plan x 1.5 + piece at 2 units, 600 paired bootstrap histories, 2 years:")
    for nm, r in Rr.items():
        print(f"   {nm:<30} 2y ${r[:, 0].mean():>7,.0f}  blown {r[:, 1].mean():5.1%}  all 6 {r[:, 2].mean():5.1%}  beats plan {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}  diff ${(r[:, 0] - b0).mean():+6,.0f}")
