"""PAPERTREND v2 (user's description and MultiCharts report, 2026-10-24; @NQ 5 min 2016-09-29 -> 2026-08-14: 535 trades,
+$167,378, PF 1.66, 58.9% win, max strategy DD -$25,177). The attached file was other code (PROPINTRA_PL rev2), so the rule
is rebuilt from the description, on our NQ 1-minute bars (Central time, close-stamped; RTH = bars 08:31-15:00 CT):
  bands = RTH open (open of the 08:31 bar) +/- 0.5 x ATR(14), ATR = mean of the previous 14 RTH session ranges (high - low);
  a 5-minute bar closing on a 15-minute mark (08:45, 09:00 ... 14:00 CT = 09:45-15:00 ET) beyond a band -> enter at the next
  bar's open; one trade a day; no target, no stop; flat at the 14:55 CT close (15:55 ET);
  filter 1 (skip): no trade the day after the widest RTH range of the last 7 sessions;
  filter 2 (gap): long only if the RTH open is above the prior RTH close (15:00 CT), short only if below.
Days: full sessions only (half days dropped); days whose prior-close -> open window holds a contract roll are dropped (the
continuous contract is not back-adjusted, so the 'gap' there is the roll spread; rolls as analysis/s_rank_gap_round2_test.py).
Costs: $7.25 per NQ round trip + 1 tick per market fill (entry and flatten). YM $5 / 1 pt tick $5, ES $5 / 0.25 tick.
Tests: the report's period; by year; pre-2022 (the author's design) vs 2022+ (their OOS) and 2023+ (ours); longs / shorts;
filter ablation (naked / skip / gap / both) with t of each filter's increment on the same days; band and ATR variants;
every-5-minute marks; placebos (random side on the same days, against the gap); the same rule on YM and ES; holding-to-close
vs exit at 12:00 / 13:00 CT; trade concentration; metrics / bootstrap / permutation / Monte Carlo at 1 MNQ; trials.
  python3 analysis/papertrend_test.py [SCRATCH_DIR] > analysis/outputs/papertrend_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
sys.argv = [sys.argv[0], SP]
import s_rank_gap_round2_test as SG

J0, JC, JF = jof(831), jof(1500), jof(1455)
NTRIAL = {"n": 0}


class Days:
    """One row per full RTH session: open, prior close, range, ATR, filters, roll flag."""
    def __init__(self, name, keep_rolls=False):
        S = SG.Sym(name); g = S.g; self.S, self.g, self.name = S, g, name
        out, info = SG.rolls_index(S); S.set_rolls(out)
        tr = g.trading; full = ~np.isnan(g.c[tr, JC]) & ~np.isnan(g.c[tr, JF])         # half days (12:15 CT close) dropped
        tr = tr[full]
        o = g.o[tr, J0]; c = g.c[tr, JC]
        hi = np.nanmax(g.h[tr, J0:JC + 1], axis=1); lo = np.nanmin(g.l[tr, J0:JC + 1], axis=1); rng = hi - lo
        pc = np.r_[np.nan, c[:-1]]
        F = pd.DataFrame(dict(row=tr, o=o, pc=pc, rng=rng), index=pd.DatetimeIndex(g.ts[tr]))
        F["atr"] = F.rng.rolling(14).mean().shift(1)
        trv = np.maximum(rng, np.maximum(np.abs(hi - pc), np.abs(lo - pc)))
        F["atrw"] = pd.Series(trv, index=F.index).ewm(alpha=1 / 14, adjust=False).mean().shift(1)
        F["skip"] = (F.rng.shift(1) >= F.rng.shift(1).rolling(7).max())
        F["gap"] = F.o - F.pc
        F["roll"] = S.has_roll(np.r_[0, tr[:-1]] * 1440 + JC, tr * 1440 + J0)
        self.F = F[(F.index >= "2016-10-01") & F.atr.notna() & (keep_rolls | ~F.roll) & F.pc.notna()].copy()


def run(D, k=0.5, skip=True, gap=True, step=15, first=jof(845), last=jof(1400), atr="atr", exit_j=JF, side_mode="rule",
        seed=1, count=True, stop_atr=None):
    if count: NTRIAL["n"] += 1
    g, S = D.g, D.S; F = D.F; rows = []; rnd = np.random.default_rng(seed)
    marks = np.arange(first, last + 1, step)
    for d, r in F.iterrows():
        if skip and r.skip: continue
        up, dn = r.o + k * r[atr], r.o - k * r[atr]; row = int(r.row); C = g.c[row]
        for j in marks:
            if j >= exit_j: break
            c = C[j]
            if np.isnan(c): continue
            side = 1 if c > up else -1 if c < dn else 0
            if side == 0: continue
            if gap and np.sign(r.gap) != side: continue            # only in the gap's direction; first qualifying mark
            if side_mode == "random": side = int(rnd.choice([-1, 1]))
            if side_mode == "against_gap" and np.sign(r.gap) == side: side = -side
            e = g.o[row, j + 1]
            if np.isnan(e): break
            x = g.c[row, exit_j]; kind = 2; xj = exit_j
            lows, highs = g.l[row, j + 1:exit_j + 1], g.h[row, j + 1:exit_j + 1]
            if stop_atr is not None:
                sp = e - side * stop_atr * r[atr]; hit = np.where((lows <= sp) if side > 0 else (highs >= sp))[0]
                if len(hit):
                    b = j + 1 + hit[0]; ob = g.o[row, b]
                    x = min(ob, sp) if side > 0 else max(ob, sp); kind = 0; xj = b
                    lows, highs = lows[:hit[0] + 1], highs[:hit[0] + 1]
            mae = (np.nanmin(lows) - e) if side > 0 else (e - np.nanmax(highs))
            gross = (x - e) * side * S.pv; net = gross - S.comm - 2 * S.tick * S.pv
            rows.append(dict(date=d, row=row, side=side, sig=j, j1=xj, kind=kind, entry=e, exit=x, gross=gross, net=net, mae=mae * S.pv - S.comm - S.tick * S.pv))
            break
    t = pd.DataFrame(rows)
    if len(t): t = t.set_index("date")
    return t


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(t, nm, w=46):
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    x = t.net; y = x.index.year; by = x.groupby(y).sum(); a, b, c = x[y < 2022], x[y >= 2022], x[y >= 2023]
    L, Sh = x[t.side > 0], x[t.side < 0]
    return (f"   {nm:<{w}} n={len(x):4d} ({len(x) / 9.9:4.0f}/yr) ${x.mean():5.0f} PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} "
            f"yrs+ {(by > 0).sum()}/{len(by)} | <22 ${a.mean():5.0f} t {tst(a):4.1f} | 22+ ${b.mean():5.0f} t {tst(b):4.1f} | 23+ t {tst(c):4.1f}"
            f" | L {len(L)} ${L.mean() if len(L) else 0:4.0f} S {len(Sh)} ${Sh.mean() if len(Sh) else 0:4.0f}")


def daily(D, t):
    x = t.net.groupby(t.index).sum(); return x.reindex(D.F.index, fill_value=0.0)


def incr(t_with, t_without, nm):
    """The filter's increment: P&L of the trades the filter removes (same rule otherwise)."""
    gone = t_without.loc[~t_without.index.isin(t_with.index)]
    return (f"   {nm:<46} removes {len(gone):4d} trades, ${gone.net.mean():5.0f} avg, t {tst(gone.net):4.1f}; "
            f"pre-2022 ${gone.net[gone.index.year < 2022].mean():5.0f} (t {tst(gone.net[gone.index.year < 2022]):4.1f}), "
            f"2022+ ${gone.net[gone.index.year >= 2022].mean():5.0f} (t {tst(gone.net[gone.index.year >= 2022]):4.1f})")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    NQ = Days("NQ"); base = run(NQ); base.to_csv("checks/candidates/papertrend/python_trades.csv")
    w = base[(base.index >= "2016-09-29") & (base.index <= "2026-08-14")]
    print(f"\n1. The report's period (2016-09-29 -> 2026-08-14), 1 NQ: {len(w)} trades (report 535), net ${w.net.sum():,.0f} "
          f"(report $167,378), PF {pf(w.net):.2f} (1.66), win {np.mean(w.net > 0):.1%} (58.9%), ${w.net.mean():.0f} a trade (~$313); "
          f"max DD ${-(w.net.cumsum() - w.net.cumsum().cummax()).min():,.0f} (report $25,177). Data ends {NQ.F.index[-1].date()}.")
    print("   by year, 1 NQ:", base.net.groupby(base.index.year).sum().round(0).astype(int).to_dict())
    print("   trades a year:", base.net.groupby(base.index.year).size().to_dict())

    print("\n2. Filter ablation (NQ; '<22' = the author's design years, '22+' their out-of-sample, 23+ ours):")
    naked, sk, gp = run(NQ, skip=False, gap=False), run(NQ, gap=False), run(NQ, skip=False)
    for t, nm in ((naked, "naked (no filters)"), (sk, "skip filter only"), (gp, "gap filter only"), (base, "both filters (the rule)")):
        print(line(t, nm))
    print("   same four as daily books (1 NQ, 2018+): " + "; ".join(
        f"{nm} ${daily(NQ, t)[NQ.F.index >= '2018-01-01'].sum() / 8.75:,.0f}/yr Sharpe "
        f"{(lambda x: x.mean() / x.std() * np.sqrt(252))(daily(NQ, t)[NQ.F.index >= '2018-01-01']):.2f} max DD "
        f"${(lambda e: -(e - e.cummax()).min())(daily(NQ, t)[NQ.F.index >= '2018-01-01'].cumsum()):,.0f}"
        for t, nm in ((naked, "naked"), (sk, "skip"), (gp, "gap"), (base, "both"))))
    print("   what each filter removes (a filter adds edge if the removed trades lose, out of sample too):")
    print(incr(gp, naked, "gap filter, on the naked rule")); print(incr(base, sk, "gap filter, after skip"))
    print(incr(sk, naked, "skip filter, on the naked rule")); print(incr(base, gp, "skip filter, after gap"))
    g_with = naked[np.sign(NQ.F.gap.reindex(naked.index)) == naked.side]; g_against = naked[np.sign(NQ.F.gap.reindex(naked.index)) != naked.side]
    print(line(g_with, "naked, with the gap")); print(line(g_against, "naked, against the gap"))

    print("\n3. Robustness of the rule (both filters):")
    for k in (0.3, 0.4, 0.6, 0.7, 0.8): print(line(run(NQ, k=k), f"band {k} ATR"))
    print(line(run(NQ, atr="atrw"), "Wilder true-range ATR(14)"))
    print(line(run(NQ, step=5), "every 5-minute close (not only 15-min marks)"))
    print(line(run(NQ, step=1), "every 1-minute close"))
    print(line(run(NQ, first=jof(845), last=jof(1200)), "entries to 12:00 CT only"))
    for ej, nm in ((jof(1200), "exit 12:00 CT"), (jof(1300), "exit 13:00 CT"), (jof(1400), "exit 14:00 CT"), (jof(1459), "exit 14:59 CT")):
        print(line(run(NQ, exit_j=ej), nm))
    for k in (0.3, 0.5, 0.7): print(line(run(NQ, k=k, skip=False, gap=False), f"naked, band {k} ATR"))
    print(line(run(NQ, step=5, skip=False, gap=False), "naked, every 5-minute close"))

    for m in (1.0, 1.5, 2.0, 3.0): print(line(run(NQ, stop_atr=m), f"disaster stop {m} ATR from entry"))
    print(line(run(Days("NQ", keep_rolls=True)), "roll-window days kept (gap = roll spread there)"))
    print(f"   extra slippage: 2 / 4 / 8 more ticks per round trip -> ${base.net.mean() - 10:.0f} / ${base.net.mean() - 20:.0f} / "
          f"${base.net.mean() - 40:.0f} a trade; break-even at {base.net.mean() / 5:.0f} extra ticks")
    for lag in (1, 2, 5):
        e = np.array([NQ.g.o[int(r.row), int(r.sig) + 1 + lag] for _, r in base.iterrows()]); n_ = (base.exit.values - e) * base.side.values * 20 - 17.25
        print(f"   entry {lag} min late (latency): ${np.nanmean(n_):.0f} a trade, t {np.nanmean(n_) / np.nanstd(n_) * np.sqrt(len(n_)):.1f}")
    import dual_thrust_test as DT
    dtd = DT.load(); dtt = DT.run(dtd, DT.setups(dtd), start="2017-01-01"); dtx = dtt.set_index("date").net.groupby(level=0).sum()
    pt = daily(NQ, base); dtx = dtx.reindex(pt.index, fill_value=0.0)
    both = (pt != 0) & (dtx != 0); same = (np.sign(pt[both]) == np.sign(dtx[both])).mean()
    print(f"   overlap with Dual Thrust v4 (open +/- 0.5 x prior range breakout, also flat 14:55): daily corr {np.corrcoef(pt, dtx)[0, 1]:+.2f}, "
          f"PT days on which DT also trades {both.sum() / (pt != 0).sum():.0%}, same-sign result on those {same:.0%}")

    print("\n4. Placebos (same days, same exits):")
    rs = [run(NQ, side_mode="random", seed=s, count=False).net for s in range(200)]
    m = np.array([x.mean() for x in rs]); tt = np.array([tst(x) for x in rs])
    print(f"   random side, 200 seeds: avg ${m.mean():.0f} (5-95% ${np.percentile(m, 5):.0f} .. ${np.percentile(m, 95):.0f}); "
          f"share >= the rule's ${base.net.mean():.0f}: {np.mean(m >= base.net.mean()):.1%}; t 95th pct {np.percentile(tt, 95):.1f}")
    print(line(run(NQ, side_mode="against_gap", gap=False), "naked breakouts, side flipped (fade)"))
    hold = []
    for d, r in NQ.F.iterrows():
        if r.skip: continue
        e, x = NQ.g.o[int(r.row), jof(846)], NQ.g.c[int(r.row), JF]
        s = np.sign(r.gap)
        if s and not np.isnan(e): hold.append(dict(date=d, side=s, net=(x - e) * s * 20 - 7.25 - 10))
    hold = pd.DataFrame(hold).set_index("date")
    print(line(hold, "no band: 08:45 -> 14:55 in the gap's direction"))

    print("\n5. The same rule on YM and ES (the author's null is on YM):")
    for nm in ("YM", "ES"):
        Dx = Days(nm)
        print(line(run(Dx), f"{nm} rule")); print(line(run(Dx, skip=False, gap=False), f"{nm} naked"))
        for k in (0.3, 0.7): print(line(run(Dx, k=k), f"{nm} rule, band {k}"))
        dn = daily(NQ, base); dx = daily(Dx, run(Dx)).reindex(dn.index, fill_value=0)
        both = (dn != 0) & (dx != 0)
        print(f"   {nm}: days both trade {both.sum()}, daily correlation on those days {np.corrcoef(dn[both], dx[both])[0, 1]:+.2f}; "
              f"NQ / {nm} ATR ratio in $ per contract {NQ.F.atr.mean() * 20 / (Dx.F.atr.mean() * Dx.S.pv):.1f}")
        ny = (base.net / (NQ.F.atr.reindex(base.index) * 20)); yy = run(Dx); yy = yy.net / (Dx.F.atr.reindex(yy.index) * Dx.S.pv)
        print(f"   in ATR units per trade: NQ {ny.mean():+.3f} (t {tst(ny):.1f}), {nm} {yy.mean():+.3f} (t {tst(yy):.1f})")

    print("\n6. Concentration (1 NQ, the rule):")
    s = base.net.sort_values(ascending=False)
    for k in (5, 10, 20): print(f"   without the best {k:2d} trades: ${s.iloc[k:].sum():>9,.0f} of ${s.sum():,.0f}, t {tst(s.iloc[k:]):.1f}")
    print(f"   worst trade ${base.net.min():,.0f}, worst open (MAE) ${base.mae.min():,.0f}; MAE < -$4,000 on {(base.mae < -4000).sum()} trades, "
          f"< -$8,000 on {(base.mae < -8000).sum()}")
    print("   by year (rule): " + " ".join(f"{y}: n {len(v)} ${v.sum():,.0f} t {tst(v):.1f}" for y, v in base.net.groupby(base.index.year)))

    print("\n7. Metrics, per 1 NQ (MNQ = /10):")
    dd = daily(NQ, base); dl = daily(NQ, base[base.side > 0]); ds = daily(NQ, base[base.side < 0])
    rows = {}
    for nm, x, tt in (("whole", dd, base.net), ("longs", dl, base.net[base.side > 0]), ("shorts", ds, base.net[base.side < 0])):
        for per, st in (("2018-26", "2018-01-01"), ("2023+", "2023-01-01")):
            rows[f"{nm} {per}"] = (x[x.index >= st], tt[tt.index >= st])
    print(M.table(rows))
    print("\n   2023+ bootstrap / permutation (daily, 1 NQ):")
    b_, p_ = R.report({"whole 2023+": dd[dd.index >= "2023-01-01"], "longs 2023+": dl[dl.index >= "2023-01-01"],
                       "shorts 2023+": ds[ds.index >= "2023-01-01"]}, limits=(5000, 10000, 20000))
    print(b_); print(p_)
    print("\n   Monte Carlo at 1 MNQ (2018+, Apex $2,000 trailing):")
    print(MC.report(base.net[base.index >= "2018-01-01"].values, daily=dd[dd.index >= "2018-01-01"].values, size=0.1, label="PAPERTREND 1 MNQ"))
    print(f"\n   trials counted here: {NTRIAL['n']}; t threshold at that count {M.t_threshold(NTRIAL['n']):.2f}; "
          f"deflated Sharpe (daily 2018+, N={NTRIAL['n']}) {M.deflated_sharpe(dd[dd.index >= '2018-01-01'].values, NTRIAL['n']):.2f}")
