"""Tune the combine and funded sizing for the whole pipeline (net $ per account slot), not each phase alone (2026-10-14).

Pipeline (analysis/account_pipeline_test.py): challenge ($50 a try) -> funded PA ($85 activation) -> 6 payouts or
blown -> next challenge; one slot, every start month 2018-01 .. 2023-10, 3-year windows, real day order.
  1. Combine sizing grid: VB 4 / 6 / 8 / 10 MNQ x ONB ADX30 risk $700 / $1,100 / $1,500 x Bridge Monday 1 / 2 / 3 MNQ
     x EOS off / $500 (72 sets), funded plan as now.
  2. Funded sizing grid with the chosen combine: full size at a cushion of $1,000 / $1,500 / $2,000 / $2,500 x whole
     plan scale 0.75 / 1.0 / 1.25.
Scored at the backtest edge AND with 25% of every strategy's average daily profit removed (volatility unchanged),
because the live edge will likely be smaller; the pick must be good on both (best average of the two ranks).
  python3 analysis/pipeline_tuning_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from account_pipeline_test import pa_timeline, slot, PLAN
from portfolio import paths, challenge
from time_clusters_test import trades as plan_trades
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
H = 750; ACT = 85.0


def haircut(Wk, Ck, alpha):
    traded = Ck != 0; mu = Ck[traded].mean() if traded.any() else 0.0
    sh = np.where(traded, alpha * mu, 0.0)
    return Wk - sh[:, None], Ck - sh


def pipeline(chal, PA, starts, D):
    out = []
    for s0 in starts:
        tend = min(D, s0 + H); fl, c = slot(s0, tend, chal, PA, ACT)
        cash = np.zeros(tend - s0 + 1)
        for d, v in fl.items(): cash[d - s0] += v
        cum = np.cumsum(cash)
        out.append(dict(net12=cum[min(len(cum) - 1, 252)], net36=cum[-1], worst=cum.min(), **c))
    return pd.DataFrame(out)


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    T = plan_trades(g); atr = g.daily_atr(15); tr = g.trading; D = len(tr); dates = pd.DatetimeIndex(g.ts[tr])
    P = {}
    for nm in ("VB", "ONB_ADX30", "MON_BR", "EOS"):
        w, r = paths(g, T[nm]); P[nm] = (w[tr] / 10, r[tr] / 10)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    PH = {}
    for nm, p in P.items():
        cl = p[1][:, -1]; wh, ch = haircut(p[0], cl, 0.25); PH[nm] = (wh, p[1] - (cl - ch)[:, None])
    starts = [int(np.argmax(dates >= pd.Timestamp(y, m, 1))) for y in range(2018, 2024) for m in range(1, 13) if pd.Timestamp(y, m, 1) <= pd.Timestamp("2023-10-01")]

    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    names, b0 = lab._base(PLAN)
    Wf = np.stack([lab.W[k] for k in names]); Cf = np.stack([lab.C[k] for k in names])
    Wh = Wf.copy(); Ch = Cf.copy()
    for k in range(len(names)): Wh[k], Ch[k] = haircut(Wf[k], Cf[k], 0.25)

    def make_PA(W, C, b, ref):
        cache = {}
        def PA(s, h):
            if (s, h) not in cache: cache[(s, h)] = pa_timeline(W, C, np.ascontiguousarray(b), s, h, 0.5, 1.0, ref)
            return cache[(s, h)]
        return PA
    PA0, PAh = make_PA(Wf, Cf, b0, 1500.0), make_PA(Wh, Ch, b0, 1500.0)

    print("\n1. Combine sizing (funded plan as now); per slot, medians over 70 start months")
    rows = []
    for vb, onb, bm, eos in itertools.product((4, 6, 8, 10), (700, 1100, 1500), (1, 2, 3), (0, 500)):
        r_ = {}
        for tag, PP, PAx in (("edge", P, PA0), ("75%", PH, PAh)):
            parts = [(PP["VB"], vb), (PP["ONB_ADX30"], rk(onb, 0.25)), (PP["MON_BR"], bm)] + ([(PP["EOS"], rk(eos, 0.30))] if eos else [])
            W0 = sum(p[0] * q for p, q in parts); R0 = sum(p[1] * q for p, q in parts)
            chal = [challenge(W0, R0, np.arange(s, min(s + 21, D))) for s in range(D)]
            pr = np.mean([c[0] == "pass" for c in chal if c is not None])
            df = pipeline(chal, PAx, starts, D)
            r_[tag] = (pr, df.net12.median(), df.net36.median(), df.net36.mean(), df.challenges.median())
        rows.append(dict(VB=vb, ONB=onb, BrMon=bm, EOS=eos, pass_edge=r_["edge"][0], net12_edge=r_["edge"][1], net36_edge=r_["edge"][2],
                         pass_75=r_["75%"][0], net12_75=r_["75%"][1], net36_75=r_["75%"][2], challenges_36=r_["edge"][4]))
    G = pd.DataFrame(rows)
    G["rank"] = (G.net36_edge.rank(ascending=False) + G.net36_75.rank(ascending=False)) / 2
    fm = {c: "${:,.0f}".format for c in ("net12_edge", "net36_edge", "net12_75", "net36_75")}
    fm.update({"pass_edge": "{:.1%}".format, "pass_75": "{:.1%}".format})
    print(G.sort_values("rank").head(15).to_string(index=False, formatters=fm))
    cur = G[(G.VB == 8) & (G.ONB == 1100) & (G.BrMon == 2) & (G.EOS == 500)]
    print("   current combine:"); print(cur.to_string(index=False, formatters=fm))
    print("   by VB size (median over the other settings): " + str(G.groupby("VB")[["pass_edge", "net36_edge", "net36_75"]].median().round(3).to_dict()))
    best = G.sort_values("rank").iloc[0]

    print(f"\n2. Funded sizing with the best combine (VB {best.VB}, ONB ${best.ONB}, Bridge Monday {best.BrMon}, EOS {'$' + str(best.EOS) if best.EOS else 'off'})")
    def chal_for(PP):
        parts = [(PP["VB"], int(best.VB)), (PP["ONB_ADX30"], rk(int(best.ONB), 0.25)), (PP["MON_BR"], int(best.BrMon))] + ([(PP["EOS"], rk(int(best.EOS), 0.30))] if best.EOS else [])
        W0 = sum(p[0] * q for p, q in parts); R0 = sum(p[1] * q for p, q in parts)
        return [challenge(W0, R0, np.arange(s, min(s + 21, D))) for s in range(D)]
    ch0, chh = chal_for(P), chal_for(PH)
    rows = []
    for ref, sc in itertools.product((1000, 1500, 2000, 2500), (0.75, 1.0, 1.25)):
        r_ = {}
        for tag, chx, W, C in (("edge", ch0, Wf, Cf), ("75%", chh, Wh, Ch)):
            df = pipeline(chx, make_PA(W, C, b0 * sc, float(ref)), starts, D)
            r_[tag] = (df.net12.median(), df.net36.median(), df.blown.mean(), df.full.mean())
        rows.append(dict(ref=ref, scale=sc, net12_edge=r_["edge"][0], net36_edge=r_["edge"][1], blown_edge=r_["edge"][2], full_edge=r_["edge"][3],
                         net12_75=r_["75%"][0], net36_75=r_["75%"][1], blown_75=r_["75%"][2], full_75=r_["75%"][3]))
    F2 = pd.DataFrame(rows)
    F2["rank"] = (F2.net36_edge.rank(ascending=False) + F2.net36_75.rank(ascending=False)) / 2
    fm2 = {c: "${:,.0f}".format for c in ("net12_edge", "net36_edge", "net12_75", "net36_75")}
    print(F2.sort_values("rank").to_string(index=False, formatters=fm2, float_format=lambda v: f"{v:.2f}"))
    pickle.dump(dict(G=G, F2=F2), open(SP + "pipeline_tuning.pkl", "wb"))
