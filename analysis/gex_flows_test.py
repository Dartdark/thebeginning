"""GEX/DIX tests (2026-10-12): regime checks (part 1), funded-bench candidates (commented gex2),
price-only stand-ins for the GEX filter (commented gex3). Expects pickled grids from a scratch
run; kept as the record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
import gex_flows as GX
d = GX.load_dix()
print("GEX < 0 share of days 2018-2026:", d.loc["2018":, "gex_neg"].mean().round(2))
for name, f, pv in (("NQ", "g24.pkl", 20), ("ES", "ge.pkl", 50)):
    g = pickle.load(open(f"/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/{f}","rb"))
    tr = g.trading; F = GX.features_for(g, d)
    C = pd.DataFrame(g.c[tr]).ffill(axis=1).to_numpy(); H = g.h[tr]; L = g.l[tr]
    op = g.o[tr, jof(831)]
    yr = pd.DatetimeIndex(g.ts[tr]).year; keep = (yr >= 2018) & F.gex_rank.notna().to_numpy()
    with np.errstate(all="ignore"):
        rng = (np.nanmax(H[:, jof(831):jof(1500)+1], 1) - np.nanmin(L[:, jof(831):jof(1500)+1], 1)) / op * 100
    r1 = C[:, jof(930)] - op; r2 = C[:, jof(1500)] - C[:, jof(930)]
    ra = C[:, jof(1430)] - op; rl = C[:, jof(1500)] - C[:, jof(1430)]
    grp = pd.cut(F.gex_rank, [-0.01, 0.2, 0.4, 0.6, 0.8, 1.01], labels=["Q1 low", "Q2", "Q3", "Q4", "Q5 high"])
    neg = F.gex_neg.to_numpy(dtype=bool)
    print(f"\n{name} 2018-2026: by previous day's GEX rank (vs past year)")
    print(f"  {'group':<9}{'days':>6}{'RTH range %':>13}{'corr(1st hr, rest)':>20}{'follow 1st hr $':>17}{'corr(to 14:30, last 30m)':>27}{'follow to 14:30 $':>19}")
    groups = [(lab, keep & (grp == lab).to_numpy()) for lab in grp.cat.categories] + [("GEX < 0", keep & neg)]
    for lab, m in groups:
        ok = m & ~np.isnan(r1) & ~np.isnan(r2)
        fol = np.sign(r1[ok]) * r2[ok] * pv; fol2 = np.sign(ra[ok]) * rl[ok] * pv
        print(f"  {lab:<9}{ok.sum():>6}{np.nanmean(rng[ok]):>13.2f}{np.corrcoef(r1[ok], r2[ok])[0,1]:>20.2f}{fol.mean():>12.0f} t={fol.mean()/fol.std()*np.sqrt(ok.sum()):4.1f}{np.corrcoef(ra[ok], rl[ok])[0,1]:>22.2f}{fol2.mean():>12.0f} t={fol2.mean()/fol2.std()*np.sqrt(ok.sum()):4.1f}")
    # DIX: next-day RTH long by DIX rank
    print(f"  DIX (dark-pool buying) rank -> next day long 8:30->15:00:")
    dg = pd.cut(F.dix_rank, [-0.01, 0.2, 0.8, 1.01], labels=["low", "mid", "high"])
    day = (C[:, jof(1500)] - op) * pv
    for lab in dg.cat.categories:
        m = keep & (dg == lab).to_numpy() & ~np.isnan(day)
        print(f"    DIX {lab:<5} n={m.sum():4d} avg ${day[m].mean():6.0f} t={day[m].mean()/day[m].std()*np.sqrt(m.sum()):4.1f}")
# strategies by regime
g = pickle.load(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/g24.pkl","rb"))
F = GX.features_for(g, d)
print("\nYour strategies (MultiCharts lists, per NQ after $7.25) by previous day's GEX rank")
for k, f in (("Vault Break", "VB v1"), ("Overnight Bias", "ONB v2"), ("Overnight Drift", "OND v1"), ("Expiration Open Short", "EOS v1")):
    t = load_mc(g, f"mc_reports/Backtesting Strategy Performance Report {f}.xlsx")
    t = t[pd.DatetimeIndex(t.date).year >= 2018]
    fr = F.reindex(t.day.to_numpy())
    grp = pd.cut(fr.gex_rank.to_numpy(), [-0.01, 0.33, 0.67, 1.01], labels=["low", "mid", "high"])
    out = []
    for lab in ("low", "mid", "high"):
        x = t.net.to_numpy()[grp == lab]
        w, l = x[x > 0].sum(), -x[x < 0].sum()
        out.append(f"{lab}: n={len(x)} ${x.mean():.0f} PF {w/l:.2f}")
    x = t.net.to_numpy()[fr.gex_neg.to_numpy(dtype=bool)]
    out.append(f"GEX<0: n={len(x)} ${x.mean():.0f}")
    print(f"  {k:<22}" + " | ".join(out))
# ===== gex2
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# from grid import execute
# from grid24 import jof
# from portfolio import load_mc
# import gex_flows as GX, intraday_research as IR
# g = pickle.load(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/g24.pkl","rb"))
# lab = pickle.load(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/lab.pkl","rb"))
# F = GX.features_for(g); atr = g.daily_atr(15); tr = g.trading
# C = pd.DataFrame(g.c).ffill(axis=1).to_numpy()
# def summ(t, name):
#     t2 = t[pd.DatetimeIndex(t.date).year >= 2018].copy(); t2["slips"] = 1 + (t2["kind"] != 1); t2["net"] -= t2["slips"] * 5
#     s = IR.summary(t2); by = t2.groupby(pd.DatetimeIndex(t2.date).year).net.mean().round().to_dict()
#     print(f"{name:<52} n={s['trades']:4d} win {s['win']} avg ${s['avg']:5.0f} PF {s['pf']:.2f} t={s['t_stat']:4.1f} yrs+ {s['years_pos']}  {by}")
# ond = lab_ond = load_mc(g, "mc_reports/Backtesting Strategy Performance Report OND v1.xlsx"); ond = ond[ond.j0 <= jof(30)]
# gr = F.gex_rank.reindex(ond.day.to_numpy()).to_numpy()
# for cut in (0.33, 0.5):
#     t = ond[gr < cut]; summ(t, f"Overnight Drift, GEX rank < {cut}"); lab.add(f"OND_G{int(cut*100)}", t, stop_pts=0.3 * atr)
# summ(ond, "Overnight Drift, all (reference)")
# onb = load_mc(g, "mc_reports/Backtesting Strategy Performance Report ONB v2.xlsx")
# neg = F.gex_neg.reindex(onb.day.to_numpy()).to_numpy(dtype=bool)
# t = onb[~neg]; summ(t, "Overnight Bias, skip GEX < 0"); lab.add("ONB_NN", t, stop_pts=0.3 * atr)
# # gamma last 30 minutes: follow 8:30->14:30 move when GEX<0, fade it when gex_rank > 0.8
# rows = []
# for d in tr:
#     if d not in F.index or pd.isna(F.gex_rank.get(d)): continue
#     mv = C[d, jof(1430)] - g.o[d, jof(831)]
#     if np.isnan(mv) or mv == 0: continue
#     if F.gex_neg[d]: side = int(np.sign(mv))
#     elif F.gex_rank[d] > 0.8: side = -int(np.sign(mv))
#     else: continue
#     rows.append((d, jof(1430), side, 0.1 * atr[d], np.inf, jof(1500)))
# s = pd.DataFrame(rows, columns=["day", "dj", "side", "stop", "target", "exit_j"])
# t = execute(g, s, max_trades=1); summ(t, "Gamma last 30 min (follow GEX<0, fade GEX top 20%)"); lab.add("G30", t, stop_pts=0.1 * atr)
# for lab_, m in (("  follow part", t.side.to_numpy() == np.sign(1)), ):
#     pass
# # DIX high -> long RTH with stop
# dr = F.dix_rank
# rows = [(d, jof(830), 1, 0.3 * atr[d], np.inf, jof(1500)) for d in tr if d in dr.index and dr[d] > 0.8]
# t = execute(g, pd.DataFrame(rows, columns=["day", "dj", "side", "stop", "target", "exit_j"]), max_trades=1)
# summ(t, "DIX top 20% -> long 8:30-15:00, stop 0.3 ATR"); lab.add("DIXL", t, stop_pts=0.3 * atr)
# lab.add("OND_MC", ond, stop_pts=0.3 * atr)
# base = {"VB": 3, "ONB": ("risk", 300), "OND_MC": ("risk", 500), "EOS": ("risk", 500)}
# plans = {"Current funded set (VB3, ONB$300, OND$500, EOS$500)": base}
# for k in ("OND_G33", "OND_G50"):
#     for rk in (500, 800):
#         p = dict(base); p.pop("OND_MC"); p[k] = ("risk", rk); plans[f"  OND -> {k} ${rk}"] = p
# p = dict(base); p.pop("ONB"); p["ONB_NN"] = ("risk", 300); plans["  ONB skips GEX<0"] = p
# for k, risks in (("G30", (150, 300)), ("DIXL", (150, 300))):
#     for rk in risks:
#         p = dict(base); p[k] = ("risk", rk); plans[f"  + {k} ${rk}"] = p
# print(lab.corr(["VB", "ONB", "OND_MC", "EOS", "G30", "DIXL"]).round(2).to_string())
# print(lab.table(plans))
# pickle.dump(lab, open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/lab.pkl","wb"), protocol=4)
# ===== gex3
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# from grid24 import jof
# from portfolio import load_mc
# import gex_flows as GX, intraday_research as IR
# g = pickle.load(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/g24.pkl","rb"))
# lab = pickle.load(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/lab.pkl","rb"))
# F = GX.features_for(g); atr = g.daily_atr(15); tr = g.trading
# C = pd.DataFrame(g.c).ffill(axis=1).to_numpy()
# cl = pd.Series(C[tr, jof(1500)], index=tr)                   # RTH close
# prev = cl.shift(1)                                           # known before day d
# atrp = pd.Series(atr[tr], index=tr) / prev                   # ATR as % of price
# proxies = {
#     "ATR% in top 11% of past year": atrp > atrp.rolling(252).quantile(0.89),
#     "prev close < 50-day average": prev < cl.rolling(50).mean().shift(1),
#     "prev close < 100-day average": prev < cl.rolling(100).mean().shift(1),
#     "prev close < 20-day average and ATR% top 25%": (prev < cl.rolling(20).mean().shift(1)) & (atrp > atrp.rolling(252).quantile(0.75)),
#     "drawdown from 60-day high > 8%": prev / cl.rolling(60).max().shift(1) - 1 < -0.08,
#     "drawdown from 60-day high > 5%": prev / cl.rolling(60).max().shift(1) - 1 < -0.05,
# }
# neg = F.gex_neg.astype(bool)
# onb = load_mc(g, "mc_reports/Backtesting Strategy Performance Report ONB v2.xlsx")
# y = pd.DatetimeIndex(onb.date).year
# base = {"VB": 3, "ONB": ("risk", 300), "OND_MC": ("risk", 500), "EOS": ("risk", 500)}
# plans = {"Current funded set": base}
# p = dict(base); p.pop("ONB"); p["ONB_NN"] = ("risk", 300); plans["ONB skips GEX<0 (needs daily GEX)"] = p
# yrs = pd.DatetimeIndex(g.ts[tr]).year >= 2018
# print("share of days flagged (2018+) and overlap with GEX<0:")
# for name, m in proxies.items():
#     m = m.reindex(tr).fillna(False).astype(bool)
#     both = (m & neg.reindex(tr).fillna(False)).to_numpy()[yrs].sum(); nn = neg.reindex(tr).fillna(False).to_numpy()[yrs].sum()
#     skip = m.reindex(onb.day.to_numpy()).to_numpy(dtype=bool)
#     kept = onb[~skip]; dropped = onb[skip]
#     k2 = kept[pd.DatetimeIndex(kept.date).year >= 2018]
#     print(f"  {name:<45} flags {m.to_numpy()[yrs].mean():4.0%} of days, catches {both/nn:4.0%} of GEX<0 days | ONB kept n={len(k2)} ${k2.net.mean():.0f} t={k2.net.mean()/k2.net.std()*np.sqrt(len(k2)):.1f}; skipped trades avg ${dropped.net.mean():.0f}")
#     key = "ONB_P" + str(len(plans)); lab.add(key, kept, stop_pts=0.3 * atr)
#     p = dict(base); p.pop("ONB"); p[key] = ("risk", 300); plans[f"ONB skips: {name}"] = p
# print(lab.table(plans)); print(lab.table(plans, horizon=500))
