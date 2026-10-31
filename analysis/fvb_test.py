"""FVB 'First Valid Breakout' (user's fvb_final.py + submission, 2026-10-25; checks/candidates/fvb/). Port of the locked config
to our 1-minute grids (Central time, close-stamped; the author's files are ET, stamped at the bar's OPEN, back-adjusted):
an author bar opening at ET hh:mm = our bar closing at CT hh:mm - 59 min.  NQ / ES / YM:
  RTH = bars opening 09:30-16:14 ET (our 08:31-15:15 CT); premarket = 04:00-09:29 ET (03:01-08:30 CT); ATR = mean of the last
  14 RTH ranges (known the day before); skip if prior RTH range > 1.5 ATR or premarket range > 1.0 ATR.
  Levels: gap day (prior high < premarket low, or prior low > premarket high) -> premarket high (long) / low (short); otherwise
  prior high / low (long / short) plus premarket high / low. First bar opening 09:30-11:29 ET (closing 08:31-10:30 CT) that
  CLOSES beyond a level -> enter at the next bar's open; no shorts after a prior day with |close - open| / range >= 0.6.
  Stop = entry -/+ 0.18 x ATR (tick-rounded); no target; exit at the close of the bar opening 16:10 ET (15:11 CT).
  After a stop, one re-entry (max 2 a day) on a later bar, with the stopped level removed.
  VP2 (1.5x size near the pre-RTH volume-profile levels) is left out: the author calls it cosmetic (weighted R only).
Days whose prior-RTH-close -> today's close window holds a contract roll are dropped (our continuous contracts are not
back-adjusted; rolls as analysis/s_rank_gap_round2_test.py). GC / CL use the author's metal / energy session times.
Costs: ours $7.25 per NQ ($5 ES / YM) + 1 tick per market / stop fill; the author's $4.12 + 2 ticks shown alongside.
Stop fills: the author's model (at the stop) and gap-through (at the bar's open when it opens beyond the stop).
R = the trade's stop distance in $ (as the author); $ figures are per 1 contract.
  python3 analysis/fvb_test.py [SCRATCH_DIR] > analysis/outputs/fvb_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
sys.argv = [sys.argv[0], SP]
import s_rank_gap_round2_test as SG

SESS = {"idx": dict(rs=570, re=975, fc=970, ps=240, pe=570), "GC": dict(rs=510, re=810, fc=800, ps=240, pe=510),
        "CL": dict(rs=540, re=870, fc=860, ps=240, pe=540)}
NTRIAL = {"n": 0}


def col(et_open_min):
    """Our CT close-stamped column of the author's bar opening at et_open_min (minutes after midnight ET)."""
    return et_open_min - 59


class Frame:
    def __init__(self, name):
        S = SG.Sym(name); g = S.g; self.S, self.g, self.name = S, g, name
        out, _ = (SG.rolls_gc(S) if name == "GC" else SG.rolls_cl(S) if name == "CL" else SG.rolls_index(S)); S.set_rolls(out)
        s = SESS.get(name, SESS["idx"]); self.s = s
        a, b = col(s["rs"]), col(s["re"] - 1); pa, pb = col(s["ps"]), col(s["pe"] - 1)
        rows = []
        for r in g.trading:
            c = g.c[r, a:b + 1]; ok = ~np.isnan(c)
            if ok.sum() < 10: continue
            ph, pl = g.h[r, pa:pb + 1], g.l[r, pa:pb + 1]
            has = ~np.isnan(ph)
            rows.append(dict(row=r, h=np.nanmax(g.h[r, a:b + 1]), l=np.nanmin(g.l[r, a:b + 1]), o=g.o[r, a:b + 1][ok][0], c=c[ok][-1],
                             pmh=ph[has].max() if has.any() else np.nan, pml=pl[has].min() if has.any() else np.nan))
        F = pd.DataFrame(rows); F.index = pd.DatetimeIndex(g.ts[F.row])
        F["rng"] = F.h - F.l; F["br"] = (F.c - F.o).abs() / F.rng.replace(0, np.nan)
        F["atr"] = F.rng.rolling(14).mean().shift(1)
        F["pdh"], F["pdl"], F["prng"], F["pbr"] = F.h.shift(1), F.l.shift(1), F.rng.shift(1), F.br.shift(1)
        prow = F.row.shift(1).fillna(0).astype(int).to_numpy()
        F["roll"] = S.has_roll(prow * 1440 + b, F.row.to_numpy() * 1440 + b)
        self.nroll = int(F.roll[F.index >= "2018-01-01"].sum())
        self.F = F[(F.index >= "2017-06-01") & F.atr.notna() & F.pmh.notna() & F.pdh.notna() & ~F.roll].copy()
        self.a, self.b = a, b


def levels(r):
    pmh, pml, pdh, pdl = r.pmh, r.pml, r.pdh, r.pdl
    pdh_in, pdl_in = pml < pdh < pmh, pml < pdl < pmh
    if pdh < pml or pdl > pmh:
        return [("pm_high", pmh, 1), ("pm_low", pml, -1)]
    lv = [("structural_pdh" if pdh_in else "pdh_break", pdh, 1), ("structural_pdl" if pdl_in else "pdl_break", pdl, -1)]
    if pmh != pdh: lv.append(("pm_high", pmh, 1))
    if pml != pdl: lv.append(("pm_low", pml, -1))
    return lv


def run(Fr, stop_frac=0.18, window=120, max_tr=2, max_pr=1.5, max_pm=1.0, strong_th=0.6, gap_fill=False, comm=None,
        count=True, exit_et=None, filters=True):
    if count: NTRIAL["n"] += 1
    g, S, s = Fr.g, Fr.S, Fr.s; tick, pv = S.tick, S.pv; comm = S.comm if comm is None else comm
    a, b = Fr.a, Fr.b; cut = col(s["rs"] + window)            # signal bars close before this column
    fcj = col(s["fc"] if exit_et is None else exit_et)
    rt = lambda x: np.round(x / tick) * tick
    rows = []
    for d, r in Fr.F.iterrows():
        atr = r.atr
        if filters and (r.prng / atr > max_pr or (r.pmh - r.pml) / atr > max_pm): continue
        if not r.pmh > r.pml: continue
        sd = rt(stop_frac * atr)
        if sd <= 0: continue
        strong = filters and r.pbr >= strong_th
        row = int(r.row); O, H, L, C = g.o[row], g.h[row], g.l[row], g.c[row]
        js = [j for j in range(a, b + 1) if not np.isnan(C[j])]
        active = levels(r); n_today = 0; k0 = 0
        while n_today < max_tr:
            found = None
            for ii in range(k0, len(js) - 1):
                j = js[ii]
                if j >= cut: break
                for nm, lv, sd_ in active:
                    if not ((sd_ == 1 and C[j] > lv) or (sd_ == -1 and C[j] < lv)): continue
                    if sd_ == -1 and strong: continue
                    found = (ii, nm, lv, sd_); break
                if found: break
            if not found: break
            ii, nm, lv, side = found
            e = rt(O[js[ii + 1]]); sp = rt(e - side * sd); kind = "eod"; x = C[js[-1]]; xi = len(js) - 1
            for kk in range(ii + 1, len(js)):
                k = js[kk]
                if (side == 1 and L[k] <= sp) or (side == -1 and H[k] >= sp):
                    x = (min(O[k], sp) if side == 1 else max(O[k], sp)) if gap_fill and kk > ii + 1 else sp
                    kind = "stop"; xi = kk; break
                if k >= fcj: x = C[k]; xi = kk; break
            pts = (x - e) * side; net = pts * pv - comm - 2 * tick * pv
            rows.append(dict(date=d, side=side, level=nm, n=n_today + 1, entry=e, exit=x, stop=sp, kind=kind, sd=sd, atr=atr,
                             pts=pts, net=net, r=net / (sd * pv), j0=js[ii + 1], j1=js[xi], row=row))
            n_today += 1
            if kind == "stop" and n_today < max_tr:
                k0 = xi + 1; active = [l for l in active if l[1] != lv]
            else: break
    t = pd.DataFrame(rows)
    return t.set_index("date") if len(t) else t


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(t, nm, w=44):
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    x = t.net; y = x.index.year; by = x.groupby(y).sum(); i, o, h = x[y <= 2023], x[(y >= 2024) & (y <= 2025)], x[y >= 2023]
    L, Sh = x[t.side > 0], x[t.side < 0]
    return (f"   {nm:<{w}} n={len(x):5d} ${x.mean():5.0f} R {t.r.mean():+.3f} PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} "
            f"yrs+ {(by > 0).sum()}/{len(by)} | IS18-23 PF {pf(i):4.2f} t {tst(i):4.1f} | OOS24-25 PF {pf(o):4.2f} t {tst(o):4.1f} | "
            f"23+ t {tst(h):4.1f} | L {len(L)} ${L.mean() if len(L) else 0:4.0f} S {len(Sh)} ${Sh.mean() if len(Sh) else 0:4.0f}")


def daily(Fr, t):
    x = t.net.groupby(t.index).sum(); idx = Fr.F.index[Fr.F.index >= "2018-01-01"]; return x.reindex(idx, fill_value=0.0)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    NQ = Frame("NQ"); base = run(NQ); base = base[base.index >= "2018-01-01"]
    import os; os.makedirs("checks/candidates/fvb", exist_ok=True); base.to_csv("checks/candidates/fvb/python_trades.csv")
    au = run(NQ, comm=4.12, count=False); au = au[(au.index >= "2018-01-01") & (au.index <= "2025-12-31")]
    print(f"\n1. NQ, the author's costs ($4.12 + 2 ticks), stop fills at the stop, 2018-2025 (submission: IS 1,534 trades PF 1.31 +355R, "
          f"OOS 507 PF 1.34 +126R, win ~26%; {NQ.nroll} roll days dropped here):")
    for nm, sel in (("IS 2018-23", au.index.year <= 2023), ("OOS 2024-25", au.index.year >= 2024)):
        x = au[sel]; print(f"   {nm}: {len(x)} trades, PF {pf(x.r):.2f}, {x.r.sum():+.0f}R, win {np.mean(x.r > 0):.1%}, "
                           f"t {tst(x.r):.1f}; $ per NQ {x.net.mean():.0f}")
    print("   exits:", base.kind.value_counts().to_dict(), "| levels:", base.level.value_counts().to_dict(), "| 2nd trades:", int((base.n == 2).sum()))

    print("\n2. NQ with our costs ($7.25 + 1 tick per fill), 2018-2026:")
    gf = run(NQ, gap_fill=True); gf = gf[gf.index >= "2018-01-01"]
    print(line(base, "the rule (stop fills at the stop)")); print(line(gf, "stop fills at the open on gap-through"))
    print(f"   gap-through cost: ${base.net.mean() - gf.net.mean():.2f} a trade; stops that opened through: "
          f"{((gf.exit != base.exit) & (gf.kind == 'stop')).sum()} of {(gf.kind == 'stop').sum()}")
    st = base[base.kind == "stop"]; worst = (st.pts / st.sd).min()
    print(f"   worst stop-out in R (at-stop model) {worst:.2f}; gap model worst {(gf.pts / gf.sd)[gf.kind == 'stop'].min():.2f}R")
    over = []
    for _, rr in st.iterrows():
        k = int(rr.j1); row = int(rr.row)
        ext = NQ.g.l[row, k] if rr.side > 0 else NQ.g.h[row, k]; over.append(abs(ext - rr.stop) / NQ.S.tick)
    over = np.array(over); half = base.net.copy(); half[base.kind == "stop"] -= over / 2 * NQ.S.tick * NQ.S.pv
    print(f"   fast markets: on the stop bar, price ran past the stop by median {np.median(over):.0f} ticks, 90th pct {np.percentile(over, 90):.0f}, "
          f"max {over.max():.0f}; if each stop filled halfway to that bar's extreme: ${half.mean():.0f} a trade, t {tst(half):.1f}")
    for tk in (2, 4, 8):
        y = base.net - tk * NQ.S.tick * NQ.S.pv * (base.kind == "stop")
        print(f"   {tk} more ticks on every stop fill: ${y.mean():.0f} a trade, t {tst(y):.1f}")
    print("   by year $ per NQ:", base.net.groupby(base.index.year).sum().round(0).astype(int).to_dict())
    print("   by year R:", base.r.groupby(base.index.year).sum().round(0).astype(int).to_dict())
    print(line(base[base.n == 1], "first trades only")); print(line(base[base.n == 2], "re-entries only"))
    for lv in base.level.unique(): print(line(base[base.level == lv], f"level {lv}"))

    sh = base[base.side < 0]; print(line(sh, "shorts only (longs / shorts split)"))
    print("   shorts by year $ per NQ:", sh.net.groupby(sh.index.year).sum().round(0).astype(int).to_dict())
    print("\n3. Fat tails (question 1):")
    r = base.r.sort_values(ascending=False)
    for k in (10, 25, 50, 100): print(f"   without the best {k:3d} trades: {r.iloc[k:].sum():+.0f}R of {r.sum():+.0f}R, t {tst(r.iloc[k:]):.1f}")
    for cap in (3, 5, 8):
        capped = np.minimum(base.pts / base.sd, cap) * base.sd * NQ.S.pv - NQ.S.comm - 2 * NQ.S.tick * NQ.S.pv
        print(f"   winners capped at {cap}R (as a target): ${capped.mean():.0f} a trade, t {tst(capped):.1f}")
    rw = base[base.r > 3]
    print(f"   trades > 3R: {len(rw)} ({len(rw) / len(base):.1%}), {rw.r.sum():+.0f}R; per year: {rw.groupby(rw.index.year).size().to_dict()}")
    big = base.r.groupby(base.index.year).apply(lambda v: v[v > 3].sum()); rest = base.r.groupby(base.index.year).apply(lambda v: v[v <= 3].sum())
    print("   per year, R from > 3R trades / from the rest:", {y: (round(big[y]), round(rest[y])) for y in big.index})

    print("\n4. Robustness:")
    for sf in (0.10, 0.15, 0.20, 0.25, 0.30): print(line(run(NQ, stop_frac=sf).loc["2018":], f"stop {sf:.2f} ATR"))
    for wnd in (60, 90, 180): print(line(run(NQ, window=wnd).loc["2018":], f"entry window {wnd} min"))
    print(line(run(NQ, max_tr=1).loc["2018":], "one trade a day"))
    print(line(run(NQ, filters=False).loc["2018":], "no filters (range / premarket / strong-day)"))
    print(line(run(NQ, max_pr=99).loc["2018":], "no prior-range filter")); print(line(run(NQ, max_pm=99).loc["2018":], "no premarket-range filter"))
    print(line(run(NQ, strong_th=9).loc["2018":], "shorts allowed after strong days"))
    for ex in (720, 840, 900, 959): print(line(run(NQ, exit_et=ex).loc["2018":], f"exit at {(ex - 60) // 60}:{(ex - 60) % 60:02d} CT"))

    print("\n5. Placebos:")
    rng = np.random.default_rng(1); ms = []
    for s in range(200):
        fl = rng.choice([-1, 1], len(base))
        ms.append(((base.exit - base.entry) * fl * 20 - 17.25).mean())
    ms = np.array(ms)
    print(f"   same entries and exit times, random side (stops not re-placed, so a proxy): avg ${ms.mean():.0f}, 95th pct ${np.percentile(ms, 95):.0f}; "
          f"the rule ${base.net.mean():.0f}")
    print("   (the same days and bars entered the other way, with the mirrored stop:)")
    g = NQ.g; fade = []
    for d, rr in base.iterrows():
        row, j0, side, e, sd = int(rr.row), int(rr.j0), -int(rr.side), rr.entry, rr.sd; sp = e - side * sd; x = g.c[row, NQ.b]; kind = "eod"
        for k in range(j0, NQ.b + 1):
            if np.isnan(g.c[row, k]): continue
            if (side == 1 and g.l[row, k] <= sp) or (side == -1 and g.h[row, k] >= sp): x = sp; break
            if k >= col(970): x = g.c[row, k]; break
        fade.append(dict(date=d, side=side, net=(x - e) * side * 20 - 17.25, r=0.0))
    fade = pd.DataFrame(fade).set_index("date"); print(line(fade, "reverse side, same stop distance"))

    print("\n6. Other markets (the author: works on ES / YM, fails on metals / energy):")
    others = {}
    for nm in ("ES", "YM", "GC", "CL"):
        Fx = Frame(nm); t = run(Fx).loc["2018":]; others[nm] = (Fx, t); print(line(t, f"{nm}"))
        print(line(run(Fx, gap_fill=True).loc["2018":], f"{nm} gap-through stops"))

    print("\n7. Metrics, per 1 NQ (MNQ = /10), gap-through stops:")
    dd, dl, ds = daily(NQ, gf), daily(NQ, gf[gf.side > 0]), daily(NQ, gf[gf.side < 0]); rows = {}
    for nm, x, tt in (("whole", dd, gf.net), ("longs", dl, gf.net[gf.side > 0]), ("shorts", ds, gf.net[gf.side < 0])):
        for per, st_ in (("2018-26", "2018-01-01"), ("2023+", "2023-01-01")):
            rows[f"{nm} {per}"] = (x[x.index >= st_], tt[tt.index >= st_])
    print(M.table(rows))
    b_, p_ = R.report({"whole 2023+": dd[dd.index >= "2023-01-01"], "longs 2023+": dl[dl.index >= "2023-01-01"],
                       "shorts 2023+": ds[ds.index >= "2023-01-01"]}, limits=(5000, 10000, 20000))
    print("\n   2023+ bootstrap / permutation (daily, 1 NQ):"); print(b_); print(p_)
    print("\n   Monte Carlo at 1 MNQ:"); print(MC.report(gf.net.values, daily=dd.values, size=0.1, label="FVB 1 MNQ"))
    from dual_thrust_test import load as dtl, run as dtr, setups as dts
    dtd = dtl(); dt = dtr(dtd, dts(dtd)).set_index("date").net.groupby(level=0).sum().reindex(dd.index, fill_value=0)
    pt = pd.read_csv("checks/candidates/papertrend/trades.csv", parse_dates=["date"]).set_index("date").net.groupby(level=0).sum().reindex(dd.index, fill_value=0)
    print(f"\n   daily corr with Dual Thrust {np.corrcoef(dd, dt)[0, 1]:+.2f}, with PAPERTREND {np.corrcoef(dd, pt)[0, 1]:+.2f}, "
          f"with ES FVB {np.corrcoef(dd, daily(*others['ES']).reindex(dd.index, fill_value=0))[0, 1]:+.2f}")
    print(f"\n   trials counted here: {NTRIAL['n']}; t threshold {M.t_threshold(NTRIAL['n']):.2f}; deflated Sharpe (N={NTRIAL['n']}) "
          f"{M.deflated_sharpe(dd.values, NTRIAL['n']):.2f}")
