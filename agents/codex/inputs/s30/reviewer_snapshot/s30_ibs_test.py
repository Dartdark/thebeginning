"""S30, cash-session IBS reversal (user's file, 2026-10-23; checks/candidates/s30_ibs/). Long only, multi-day holds (NOT Apex).
Rule: IBS = (15:00 close - session low) / (session high - session low) over 08:30-15:00 CT (26 15-min bars = 1-min bars
08:31-15:00); flat and IBS < 0.20 -> buy at the next bar's open (15:01); long and IBS > 0.80 -> sell at the next bar's open.
No stop / target. Sessions without a full 08:31-15:00 (half days) make no decision. NQ and ES (we have no RTY data).
Costs per contract round trip: NQ $7.25, ES $5.00, + 1 tick per market fill. Contract-switch jumps inside a hold are removed.
Controls: (a) holding the index for the same days (every day long, scaled to S30's time in market); (b) random entry days with
S30's own hold lengths (500 runs); (c) the short mirror (IBS > 0.80 short, cover < 0.20), as the author did.
  python3 analysis/s30_ibs_test.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from overnight_round import roll_minutes
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"NQ": ("g24.pkl", 20.0, 0.25, 7.25), "ES": ("ge.pkl", 50.0, 0.25, 5.0)}


def sessions(g, sym):
    tr = g.trading; rows = []
    jj = np.arange(jof(831), jof(1500) + 1)
    for r in tr:
        h, l, c = g.h[r, jj], g.l[r, jj], g.c[r, jj]
        full = np.isfinite(c).sum() >= 380 and np.isfinite(c[-1])
        nxt = g.o[r, jof(1501)] if np.isfinite(g.o[r, jof(1501)]) else np.nan
        rows.append(dict(r=r, date=pd.Timestamp(g.ts[r]), full=full, hi=np.nanmax(h) if full else np.nan, lo=np.nanmin(l) if full else np.nan,
                         c15=c[-1] if full else np.nan, nxt=nxt))
    S = pd.DataFrame(rows); S["ibs"] = (S.c15 - S.lo) / (S.hi - S.lo)
    return S


def run(g, S, pv, tick, comm, rolls, mirror=False):
    out = []; pos = 0; e_px = e_i = None
    for i, x in S.iterrows():
        if not x.full or not np.isfinite(x.ibs) or not np.isfinite(x.nxt) or x.hi <= x.lo: continue
        enter = (x.ibs < 0.2) if not mirror else (x.ibs > 0.8)
        leave = (x.ibs > 0.8) if not mirror else (x.ibs < 0.2)
        side = -1 if mirror else 1
        if pos == 0 and enter:
            pos = side; e_px = x.nxt + side * tick; e_i = i
        elif pos != 0 and leave:
            px = x.nxt - pos * tick; gross = (px - e_px) * pos
            m0, m1 = S.r[e_i] * 1440 + jof(1501), x.r * 1440 + jof(1501)
            for j in rolls[(rolls > m0) & (rolls <= m1)]:
                p = j - 1
                while not np.isfinite(g.c.ravel()[p]): p -= 1
                gross -= (g.c.ravel()[j] - g.c.ravel()[p]) * pos
            out.append(dict(date=S.date[e_i], exit_date=x.date, side=pos, net=gross * pv - comm, days=(x.date - S.date[e_i]).days, i0=e_i, i1=i))
            pos = 0
    return pd.DataFrame(out)


def line(t, nm):
    x = t.net; y = t.exit_date.dt.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / -x[x < 0].sum()
    a, b = x[y < 2023], x[y >= 2023]; ta = lambda q: q.mean() / q.std() * np.sqrt(len(q))
    return (f"   {nm:<30} n={len(x):4d} win {np.mean(x > 0):.0%} ${x.mean():6.0f} PF {pf:.2f} t {ta(x):4.1f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():5.0f} (t {ta(a):.1f}) | 23+ ${b.mean():5.0f} (t {ta(b):.1f}) | median hold {t.days.median():.0f} d")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    daily = {}
    for sym, (pk, pv, tick, comm) in SPEC.items():
        g = pickle.load(open(SP + pk, "rb")); S = sessions(g, sym); S = S[S.date >= "2017-12-01"].reset_index(drop=True)
        rolls = np.sort(roll_minutes(g, sym))
        t = run(g, S, pv, tick, comm, rolls); t = t[t.date >= "2018-01-01"].reset_index(drop=True)
        print(f"\n== {sym} (per full contract; 1 micro = 1/10) ==")
        print(line(t, "S30 long"))
        print("   by exit year:", t.groupby(t.exit_date.dt.year).net.sum().round(0).astype(int).to_dict())
        mi = run(g, S, pv, tick, comm, rolls, mirror=True); mi = mi[mi.date >= "2018-01-01"]
        print(line(mi, "short mirror (not traded)"))
        # (a) buy-and-hold for the same time in market: average 15:00-to-15:00 return per day held x S30's days held
        c = S.set_index("date").c15.where(S.set_index("date").full).ffill()
        d = c.diff().loc["2018-01-01":] * pv
        held_days = sum(t.i1 - t.i0); tot_days = len(d)
        print(f"   holding the index: ${d.sum():,.0f} over {tot_days} sessions; for S30's {held_days} sessions in the market ~${d.mean() * held_days:,.0f}"
              f" vs S30 ${t.net.sum():,.0f} (gross of costs for holding)")
        # (b) random entry sessions with S30's hold lengths
        rng = np.random.default_rng(1); L = (t.i1 - t.i0).values; ok = S.index[(S.date >= "2018-01-01") & S.full].values
        cvals = S.nxt.values; rs = []
        for _ in range(500):
            starts = rng.choice(ok[:-max(L) - 1], len(L), replace=False); tot = 0.0
            for s0, ln in zip(starts, L):
                e, x_ = cvals[s0], cvals[min(s0 + ln, len(cvals) - 1)]
                if np.isfinite(e) and np.isfinite(x_): tot += (x_ - e) * pv - comm - 2 * tick * pv
            rs.append(tot / len(L))
        print(f"   random entry sessions, same hold lengths (500 runs): ${np.mean(rs):.0f} a trade (95th pct ${np.percentile(rs, 95):.0f}) vs S30 ${t.net.mean():.0f}"
              f" -> p {np.mean(np.array(rs) >= t.net.mean()):.3f} (roll jumps not removed in the control)")
        # daily mark-to-market for metrics / correlation
        pos = pd.Series(0.0, index=S.date)
        for _, x in t.iterrows(): pos.iloc[x.i0 + 1:x.i1 + 1] = 1.0
        mtm = (pos * S.set_index("date").c15.ffill().diff().fillna(0) * pv).loc["2018-01-01":]
        alld = pd.bdate_range("2018-01-01", t.exit_date.max()); mtm = mtm.reindex(alld, fill_value=0.0)
        daily[sym] = mtm
        print(M.table({f"{sym} S30 (daily marked)": (mtm, t.net)}))
        bt, pm = R.report({f"{sym} 2023+": mtm[mtm.index >= "2023-01-01"]}, n=2000); print(bt)
        print(MC.report(t.net, mtm, size=0.1, label="1 micro"))
        t.to_csv(f"checks/candidates/s30_ibs/python_trades_{sym}.csv", index=False)
    both = (daily["NQ"] + daily["ES"].reindex(daily["NQ"].index, fill_value=0)) / 10
    e = both.cumsum(); print(f"\nNQ + ES at 1 micro each (daily marked): ${both.sum() / (len(both) / 252):,.0f} a year, max DD ${-(e - e.cummax()).min():,.0f}, "
                          f"corr NQ / ES {np.corrcoef(daily['NQ'], daily['ES'].reindex(daily['NQ'].index, fill_value=0))[0, 1]:.2f}")
    p = pd.read_csv("agents/tasks/plan_daily_pnl.csv", parse_dates=["date"]).set_index("date")
    bb = both.reindex(p.index, fill_value=0.0)
    print(f"   corr with the funded plan's daily P&L (1 micro each): {np.corrcoef(bb, p.sum(axis=1))[0, 1]:+.2f}")
    both.to_csv("checks/candidates/s30_ibs/daily_nq_es_per_micro.csv")
