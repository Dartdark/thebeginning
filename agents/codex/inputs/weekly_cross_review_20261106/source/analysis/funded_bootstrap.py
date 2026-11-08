"""Bootstrapped funded bench (2026-10-17). The funded bench (funded_lab / funded_sim) runs every start day of ONE history;
reshuffling just NFP's own results moved its 2-year blown rate 2% -> 16% (analysis/nfp_replacement_test.py). This runs the
same Apex PA simulator on many resampled histories:
  - circular block bootstrap of whole trading days (2018-2026), block length L (default 20 days), every strategy's day
    kept together, so cross-strategy correlation and volatility clustering inside a block are preserved
  - each history: one account started on day 0, horizon 500 trading days (2 years); the same history is used for every
    plan compared (paired), so differences between plans are not drawn from different luck
Output per plan: expected payouts within 1 / 2 years with 5-95% bands across histories, blown share, share with all 6
payouts within 2 years, median days to the 6th payout; pairwise: P(plan beats the base plan) on 2-year payouts.
Minute paths are compressed to the minutes where any strategy's open P&L changes (exact for the simulator's checks).
  from funded_bootstrap import Boot; B = Boot(lab); B.compare({...plans...}, n=1000)
  python3 analysis/funded_bootstrap.py [SCRATCH_DIR]     (plan check + block-length sensitivity + example decisions)
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import funded_sim as F

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PLAN = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
        "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}


def plan_lab(sp=SP):
    """The funded lab with the current plan's pieces (VB split by the single-print flag, CL fade as CLS)."""
    argv = sys.argv; sys.argv = ["x", sp]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    sys.argv = argv
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); S = pd.read_pickle(sp + "single_print_sessions.pkl")
    flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    return lab


class Boot:
    def __init__(self, lab, start="2018-01-01"):
        self.lab = lab; d = pd.DatetimeIndex(lab.g.ts[lab.tr]); self.days = np.where(d >= start)[0]

    def _histories(self, n, H, L, seed):
        rng = np.random.default_rng(seed); D = len(self.days); nb = int(np.ceil(H / L))
        st = rng.integers(0, D, (n, nb))
        idx = (st[:, :, None] + np.arange(L)) % D                       # circular blocks
        return self.days[idx.reshape(n, -1)[:, :H]]

    def run(self, plans, n=1000, H=500, L=20, seed=1, fmin=0.5, fmax=1.0, ref=1500.0):
        lab = self.lab; keys = sorted({k for p in plans.values() for k in p})
        Wall = np.stack([lab.W[k] for k in keys])                        # (K, D, 1440)
        chg = np.zeros(Wall.shape[2], bool); chg[-1] = True
        chg[1:] |= (np.abs(np.diff(Wall, axis=2)) > 0).any(axis=(0, 1)); chg[0] |= (Wall[:, :, 0] != 0).any()
        Wc = np.ascontiguousarray(Wall[:, :, chg]); Call = np.stack([lab.C[k] for k in keys])
        bases = {}
        for nm, p in plans.items():
            names, b = lab._base(p); B = np.zeros((len(keys), lab.D))
            for i, k in enumerate(names): B[keys.index(k)] = b[i]
            bases[nm] = B
        hist = self._histories(n, H, L, seed); res = {nm: np.zeros((n, 5)) for nm in plans}
        y1 = {nm: np.zeros(n) for nm in plans}
        for h in range(n):
            ix = hist[h]; W = np.ascontiguousarray(Wc[:, ix, :]); C = np.ascontiguousarray(Call[:, ix])
            for nm in plans:
                b = np.ascontiguousarray(bases[nm][:, ix])
                r = F.simulate_sized(W, C, b, horizon=H, starts=[0], fmin=fmin, fmax=fmax, ref=ref)
                res[nm][h] = [r["paid"][0], r["payouts"][0], r["days"][0], r["blown"][0], r["first"][0]]
                r1 = F.simulate_sized(W, C, b, horizon=min(250, H), starts=[0], fmin=fmin, fmax=fmax, ref=ref)
                y1[nm][h] = r1["paid"][0]
        return res, y1, chg.sum()

    def compare(self, plans, base=None, **kw):
        res, y1, nmin = self.run(plans, **kw); base = base or next(iter(plans))
        rows = {}
        for nm, r in res.items():
            paid, pay, days, blown = r[:, 0], r[:, 1], r[:, 2], r[:, 3]
            t6 = np.where(pay == 6, days, np.inf)
            rows[nm] = dict(y1=y1[nm].mean(), y1_p5=np.percentile(y1[nm], 5), y2=paid.mean(), y2_p5=np.percentile(paid, 5),
                            y2_p95=np.percentile(paid, 95), blown=blown.mean(), all6_2y=np.mean(pay == 6), days6=np.median(t6),
                            beats_base=np.mean(paid > res[base][:, 0]) + 0.5 * np.mean(paid == res[base][:, 0]),
                            diff_y2=(paid - res[base][:, 0]).mean(), diff_blown=blown.mean() - res[base][:, 3].mean())
        df = pd.DataFrame(rows).T
        fm = {c: "${:,.0f}".format for c in ("y1", "y1_p5", "y2", "y2_p5", "y2_p95", "diff_y2")}
        fm.update({c: "{:.1%}".format for c in ("blown", "all6_2y", "beats_base", "diff_blown")}); fm["days6"] = "{:.0f}".format
        return df, df.to_string(formatters=fm), nmin


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    lab = plan_lab(); B = Boot(lab)
    a, c = lab.score(PLAN, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(PLAN, 500, fmin=0.5, fmax=1.0, ref=1500.0)
    print(f"Single-history bench for reference: 1y ${a['expected']:,.0f} / 2y ${c['expected']:,.0f}, blown {a['blown']:.0%} / {c['blown']:.0%}")
    for L in (10, 20, 60):
        df, s, nmin = B.compare({"plan": PLAN}, n=600, L=L)
        print(f"\nBlock length {L} days, 600 histories ({nmin} decision minutes kept):\n{s}")
    nonfp = {k: v for k, v in PLAN.items() if k != "NFP_MC"}
    plans = {"plan": PLAN, "drop NFP": nonfp, "plan, VB 2 / 1": {**PLAN, "VB_N": 2}, "plan, cushion ref $1,000": PLAN}
    print("\nExample decisions (1,000 paired histories, L 20):")
    df, s, _ = B.compare({k: v for k, v in plans.items() if k != "plan, cushion ref $1,000"}, n=1000, L=20); print(s)


def add_moc_mes(lab, sp=SP):
    """ES MOC auction follow (>= 0.3 ATR 14:00 -> 14:50, follow 14:51 -> 15:00, stop 0.25 ATR) as per-MES daily paths."""
    import pickle
    from grid24 import jof
    import s_rank_es_round1_test as ER
    ge = pickle.load(open(sp + "ge.pkl", "rb")); tr = ge.trading[pd.DatetimeIndex(ge.ts[ge.trading]) >= "2018-01-01"]
    atr = ge.daily_atr(15)[tr]; cf = pd.Series(ge.c.ravel()).ffill().to_numpy(); P = lambda t: cf[tr * 1440 + jof(t)]
    full = ge.last_j[tr] >= jof(1500); mv = P(1450) - P(1400); m = full & (np.abs(mv) >= 0.3 * atr) & (mv != 0)
    t = ER.trades(ge, tr[m], np.sign(mv[m]).astype(int), jof(1451), jof(1500), 0.25 * atr[m])
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)
    W = np.zeros((len(dates), 1440)); Cd = np.zeros(len(dates))
    for r in t.itertuples():
        d = pd.Timestamp(r.date).normalize()
        if d not in pos.index: continue
        i = pos[d]; seg = ge.c[r.day, r.j0:r.j1 + 1]
        path = np.nan_to_num((seg - r.entry) * r.side * 50 - 5.0, nan=0.0) / 10
        path = pd.Series(path).replace(0, np.nan).ffill().fillna(0).to_numpy()
        W[i, r.j0:r.j1 + 1] = path; W[i, r.j1 + 1:] = r.net / 10; Cd[i] = r.net / 10
    lab.W["MOC_MES"] = W; lab.C["MOC_MES"] = Cd
    return lab


def decisions(B):
    nonfp = {k: v for k, v in PLAN.items() if k != "NFP_MC"}
    plans = {"plan (VB 3 / 1)": PLAN, "VB 2 / 1": {**PLAN, "VB_N": 2}, "VB 2 / 0": {**PLAN, "VB_N": 2, "VB_F": 0},
             "drop NFP": nonfp, "+ ES MOC 1 MES": {**PLAN, "MOC_MES": 1}, "+ ES MOC 2 MES": {**PLAN, "MOC_MES": 2},
             "VB 2 / 1 + ES MOC 2 MES": {**PLAN, "VB_N": 2, "MOC_MES": 2}, "NFP -> ES MOC 2 MES": {**nonfp, "MOC_MES": 2}}
    plans = {k: {kk: vv for kk, vv in v.items() if vv != 0} for k, v in plans.items()}
    df, s, _ = B.compare(plans, n=1000, L=20); print(s)
    for ref in (1000.0, 2000.0):
        d2, s2, _ = B.compare({"plan": PLAN, "VB 2 / 1": {**PLAN, "VB_N": 2}}, n=1000, L=20, ref=ref)
        print(f"\n   cushion ref ${ref:,.0f} (full size from that cushion):\n" + s2)
