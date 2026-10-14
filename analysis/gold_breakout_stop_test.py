"""Gold Asian-range breakout: tighter stops, 0.5 x and 0.25 x the Asian range (user's question, 2026-10-14).

Same trade as analysis/gold_breakout_filter_test.py (range 20:00 -> 00:00 CT, OCO stops, out 10:00 CT, one a day, 1 GC,
$7.25 + 1 tick a fill), stop = 1.0 / 0.5 / 0.25 x range width, with and without filter B (fills before 02:00 CT only).
A tighter stop means more MGC for the same $ risk, so the fair comparison is R = net / $ risked (stop x $100 per GC),
plus the funded bench risk-sized (same $ risk per trade) and at fixed 1 MGC.
Note: the stop is measured from the fill. Stop-outs inside the entry minute are filled at the stop (1-minute bars can't
see the order inside the minute), so very tight stops are slightly optimistic.
  python3 analysis/gold_breakout_stop_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import asian_breakout_test as AB
import gold_asian_breakout_gc_test as GT
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPLIT = pd.Timestamp("2023-01-01")


def streaks(net):
    s = "".join("L" if v < 0 else "W" for v in net)
    return max(len(z) for z in s.split("W")), net.rolling(20).sum().min()


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    gc = GT.load_gc()
    days = pd.DatetimeIndex(gc.ts[gc.trading]); days = days[days.year >= 2018]
    dl = lambda x: x.groupby(x.date).net.sum().reindex(days, fill_value=0.0)
    V = {}
    for frac in (1.0, 0.5, 0.25):
        t = AB.run(gc, "GC", frac=frac); t = t[t.date >= pd.Timestamp("2018-01-01")].reset_index(drop=True)
        t["Rr"] = t.net / (frac * t.width * 100.0); t["hour"] = (t.t0 % 1440) // 60; t["frac"] = frac
        V[f"stop {frac} x"] = t; V[f"stop {frac} x + B"] = t[t.hour < 2].reset_index(drop=True)
    print("\n1. Per GC; R = net / $ risked (stop distance x $100)")
    hold = {}
    for nm, t in V.items():
        y = t.date.dt.year; ls, w20 = streaks(t.Rr)
        print(f"   {nm:<16} n {len(t):4d} win {np.mean(t.net > 0):.0%} ${t.net.mean():5.0f} PF {t.net[t.net > 0].sum() / -t.net[t.net < 0].sum():.2f}"
              f" | {t.Rr.mean():+.3f} R t {t.Rr.mean() / t.Rr.std() * np.sqrt(len(t)):.1f} | 2018-22 {t.Rr[y < 2023].mean():+.3f} 2023-26 {t.Rr[y >= 2023].mean():+.3f}"
              f" | yrs+ (R) {(t.Rr.groupby(y).sum() > 0).sum()}/{y.nunique()} | stopped {np.mean(t.kind == 0):.0%} | longest losing run {ls}, worst 20 trades {w20:+.1f} R")
        hold[nm + " 2023+"] = dl(t)[days >= SPLIT]
    print("\n2. Standard metrics per GC (whole, longs, shorts)")
    for nm, t in V.items():
        print(M.table({nm: (dl(t), t.net), "  longs": (dl(t[t.side > 0]), t.net[t.side > 0]), "  shorts": (dl(t[t.side < 0]), t.net[t.side < 0])}))
    b_, p_ = R.report(hold, n=3000); print(b_); print(p_)

    print("\n3. Funded bench (plan + gold on MGC), same $ risk per trade and fixed 1 MGC")
    g = pickle.load(open(SP + "g24.pkl", "rb")); lab = pickle.load(open(SP + "lab.pkl", "rb"))
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); dpos = pd.Series(np.arange(lab.D), index=dts2)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    from speed_to_13k import run as speed, fmt
    cands = {"current plan": plan}
    for i, (nm, t) in enumerate(V.items()):
        key = f"G{i}"; GT.add_to_lab(lab, key, t, gc)
        st_arr = np.full(lab.D, 1e12)
        for r in t.itertuples():
            if r.date in dpos.index: st_arr[dpos[r.date]] = r.frac * r.width * 5.0       # MGC $10 / pt vs lab's $2 / pt
        lab.stop[key] = st_arr
        cands[f"+ {nm}, 1 MGC"] = {**plan, key: 1}
        for risk in (75, 100, 150):
            cands[f"+ {nm}, risk ${risk}"] = {**plan, key: ("risk", risk)}
    sp = {}
    for nm, p in cands.items():
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<34} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        sp[nm] = speed(lab, p, **CS)
    print(fmt(pd.DataFrame(sp).T))
