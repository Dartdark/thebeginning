"""IBS Mean Reversion ES v5 (user upload 2026-11-12: forum post + MultiCharts file IBS_MeanReversion_ES.txt, Kakushadze & Serur 2018 sec.
4.4; report 12/2016-11/2026: 301 trades, $174,987, PF 1.53, 67.8% wins, max DD $45,823 per ES). Long only, multi-day (NOT Apex-legal).
Rule as coded: the day = Globex session 17:00-16:00 CT. At the first bar >= 14:59 CT: IBS = (close - session low) / (session high -
session low) so far; ATR(10) = (today's true range so far + the last 9 full-session true ranges) / 10.
  long:  IBS > 0.8 -> sell next bar at market; else held >= 5 sessions -> sell next bar at market.
  flat:  IBS < 0.2 -> buy next bar at market; stop 2.5 x ATR below the entry (active from the bar after the entry bar).
Our rebuild on back-adjusted 1-min data (data/ES_1min_*.csv, 24h; contract-switch jumps removed). Costs: ours $5 + 1 tick ($12.50) per
fill = $30 a round trip per ES ($37.25 / NQ: $7.25 + 2 ticks); his $2.50 + $4.00 per fill = $13.
Sections: reproduction vs his report, his split (2016-21 / 2022+) and ours (2018-22 / 2023+), by year, exits, metrics, beta controls
(holding ES on the same days; random entries with his holds), ingredient breakdown (one part changed at a time), bootstrap +
permutation on 2023+, Monte Carlo at 1 ES / 1 MES.
  tools/run_stamped.sh analysis/ibs_globex_test.py > analysis/outputs/ibs_globex_test_output.txt
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as MT, resampling as RS, montecarlo as MC
from overnight_round import roll_minutes

SPEC = {"ES": (50.0, 0.25, 5.0, "scratch_data/ge.pkl", "data/ES_1min_20*.csv", None),
        "NQ": (20.0, 0.25, 7.25, "scratch_data/g24.pkl", "data/NQ_1min_20*.csv", "data/NQ_1min_ON_20*.csv")}


def minutes(sym):
    pv, tick, comm, gp, f1, f2 = SPEC[sym]
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f1)) + (sorted(glob.glob(f2)) if f2 else [])], ignore_index=True)
    d = d.drop_duplicates(["date", "time"])
    ts = pd.to_datetime(d.date.astype(str), format="%Y%m%d") + pd.to_timedelta(d.time // 100 * 60 + d.time % 100, unit="m")
    d = d.assign(ts=ts).sort_values("ts").reset_index(drop=True)
    g = pickle.load(open(gp, "rb")); rl = roll_minutes(g, sym)
    rts = pd.DatetimeIndex(g.ts[rl // 1440]) + pd.to_timedelta(rl % 1440, unit="m")
    pos = np.searchsorted(d.ts.to_numpy(), rts.to_numpy()); pos = pos[(pos > 0) & (pos < len(d))]
    gap = np.zeros(len(d)); gap[pos] = d.open.to_numpy()[pos] - d.close.to_numpy()[pos - 1]   # new contract open - old contract close
    adj = np.cumsum(gap[::-1])[::-1] - gap                                                    # sum of the gaps AFTER each minute
    for c in ("open", "high", "low", "close"): d[c] = d[c] + adj                              # back-adjusted to the latest contract
    d["hm"] = d.ts.dt.hour * 100 + d.ts.dt.minute
    d["sess"] = (d.ts + pd.Timedelta(hours=7) - pd.Timedelta(minutes=1)).dt.normalize()
    return d, len(pos)


def sessions(d, rth=False, dec=1459):
    """per session: first index, decision index (first bar >= dec), hi/lo up to it, full hi/lo, last close."""
    s = d.sess.to_numpy(); hm = d.hm.to_numpy(); n = len(d)
    starts = np.r_[0, np.flatnonzero(s[1:] != s[:-1]) + 1]; ends = np.r_[starts[1:], n]
    h, l, c = d.high.to_numpy(), d.low.to_numpy(), d.close.to_numpy(); rows = []
    for a, b in zip(starts, ends):
        hh = hm[a:b]; k = np.flatnonzero((hh >= dec) & (hh < 1700))
        di = a + k[0] if len(k) else -1
        if rth: w = np.flatnonzero((hh > 830) & (hh <= dec)) + a
        else: w = np.arange(a, di + 1) if di >= 0 else np.arange(a, b)
        rows.append((a, b, di, h[w].max() if len(w) and di >= 0 else np.nan, l[w].min() if len(w) and di >= 0 else np.nan,
                     h[a:b].max(), l[a:b].min(), c[b - 1], s[a]))
    S = pd.DataFrame(rows, columns="a b di hi lo fh fl last sess".split())
    S["ok"] = (S.di >= 0) & (S.b - S.a > 300)
    return S


def run(d, S, sym="ES", ent=0.2, ex=0.8, hold=5, stop=2.5, atrn=10, costs="ours", exit_rule="ibs", rand=None, side=1):
    pv, tick, comm = SPEC[sym][:3]
    fee = (2 * comm + 2 * tick * pv) if costs == "ours" else 13.0 if costs == "his" else 0.0
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(o)
    prevc = np.r_[np.nan, S["last"].to_numpy()[:-1]]
    ftr = np.maximum(S.fh, prevc) - np.minimum(S.fl, prevc)
    rows = []; pos = 0; e_i = e_px = e_atr = 0; days = 0; trh = []
    rng = np.random.default_rng(rand) if rand is not None else None
    for k in range(len(S)):
        if pos: days += 1
        r = S.iloc[k]
        if k > 0 and np.isfinite(ftr[k - 1]): trh.append(ftr[k - 1])
        if not r.ok: continue
        di = int(r.di); a = int(r.a)
        if pos:                                              # stop from max(entry bar + 1, session start) to the decision bar
            j0 = max(e_i + 1, a); stp = e_px - side * stop * e_atr if stop else None
            if stp is not None and di >= j0:
                hit = (l[j0:di + 1] <= stp) if side > 0 else (h[j0:di + 1] >= stp)
                if hit.any():
                    j = j0 + int(np.argmax(hit)); px = min(stp, o[j]) if side > 0 else max(stp, o[j])
                    rows.append((d.ts.iat[e_i], d.ts.iat[j], e_px, px, side * (px - e_px) * pv - fee, "stop", days)); pos = 0
        rngd = r.hi - r.lo; ibs = (c[di] - r.lo) / rngd if rngd > 0 else 0.5
        today = max(r.hi, prevc[k]) - min(r.lo, prevc[k]) if np.isfinite(prevc[k]) else np.nan
        atr = (today + sum(trh[-(atrn - 1):])) / atrn if len(trh) >= atrn - 1 and np.isfinite(today) else 0.0
        if di + 1 >= n: break
        if pos:
            why = None
            if exit_rule == "ibs" and ((ibs > ex) if side > 0 else (ibs < 1 - ex)): why = "ibs"
            elif exit_rule == "prevhigh" and c[di] > S.hi.iat[k - 1 if k else 0]: why = "ibs"
            elif hold and days >= hold: why = "time"
            if why:
                px = o[di + 1]; rows.append((d.ts.iat[e_i], d.ts.iat[di + 1], e_px, px, side * (px - e_px) * pv - fee, why, days)); pos = 0
                continue                                     # MarketPosition is still 1 on this bar: no re-entry
        if not pos and atr > 0:
            go = (ibs < ent) if side > 0 else (ibs > 1 - ent)
            if rng is not None: go = rng.random() < rand_p
            if go:
                pos = 1; e_i = di + 1; e_px = o[e_i]; e_atr = atr; days = 0
    return pd.DataFrame(rows, columns=["entry_ts", "exit_ts", "entry", "exit", "net", "why", "days"])


rand_p = 0.0


def line(t, lab):
    if len(t) < 3: return f"   {lab:<40} n {len(t)}"
    x = t.net; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum()); tt = x.mean() / x.std() * np.sqrt(len(x))
    return f"   {lab:<40} n {len(t):4d} win {np.mean(x > 0):5.1%} ${x.mean():8,.0f} total ${x.sum():10,.0f} PF {pf:4.2f} t {tt:5.2f}"


def daily_marked(d, t, pv, days_idx):
    """daily P&L marked at each session's last close (entry / exit fills and costs on their days)."""
    c = d.close.to_numpy(); s = d.sess.to_numpy(); last = pd.Series(c).groupby(s).last()
    out = pd.Series(0.0, index=days_idx)
    for r in t.itertuples():
        e = pd.Timestamp(r.entry_ts); x = pd.Timestamp(r.exit_ts)
        se = (e + pd.Timedelta(hours=7) - pd.Timedelta(minutes=1)).normalize(); sx = (x + pd.Timedelta(hours=7) - pd.Timedelta(minutes=1)).normalize()
        lv = last[(last.index >= se) & (last.index < sx)]; prev = r.entry
        for dd, v in lv.items(): out[dd] = out.get(dd, 0) + (v - prev) * pv; prev = v
        out[sx] = out.get(sx, 0) + (r.exit - prev) * pv + (r.net - (r.exit - r.entry) * pv)
    return out.sort_index()


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    d, nr = minutes("ES"); S = sessions(d); pv = 50.0
    print(f"ES 1-min {d.ts.min()} .. {d.ts.max()}, {len(S)} sessions, {nr} contract switches removed")
    T = run(d, S); T_his = run(d, S, costs="his"); y = pd.DatetimeIndex(T.entry_ts).year
    print("\n== Reproduction (his report: Dec 2016 - Nov 2026, 301 trades, $174,987, PF 1.53, 67.77% wins; IS 161 / $50,170 / PF 1.41; OOS 168 / $128,516 / PF 1.59)")
    print(line(T_his, "his costs ($13 a round trip), all")); yh = pd.DatetimeIndex(T_his.entry_ts).year
    print(line(T_his[yh <= 2021], "his costs, his IS 2016-21")); print(line(T_his[yh >= 2022], "his costs, his OOS 2022+"))
    print(line(T, "OUR costs ($30), all")); print(line(T[y <= 2021], "our costs, his IS 2016-21")); print(line(T[y >= 2022], "our costs, his OOS 2022+"))
    print(line(T[(y >= 2018) & (y <= 2022)], "our costs, design 2018-22")); print(line(T[y >= 2023], "our costs, holdout 2023+"))
    print("   by year: " + "  ".join(f"{k} ${g.net.sum():,.0f} ({len(g)}, PF {g.net[g.net > 0].sum() / max(1, -g.net[g.net < 0].sum()):.2f})" for k, g in T.groupby(y)))
    print("   exits: " + "  ".join(f"{k}: {len(g)} trades ${g.net.sum():,.0f} (avg ${g.net.mean():,.0f}, worst ${g.net.min():,.0f})" for k, g in T.groupby("why")))
    print(f"   avg win ${T.net[T.net > 0].mean():,.0f}, avg loss ${T.net[T.net < 0].mean():,.0f}, worst ${T.net.min():,.0f}, avg hold {T.days.mean():.1f} sessions")

    days_idx = pd.DatetimeIndex(sorted(set(S.sess[S.ok]))); days_idx = days_idx[days_idx >= "2018-01-01"]
    T18 = T[y >= 2018]; D = daily_marked(d, T18, pv, days_idx).reindex(days_idx, fill_value=0.0)
    print("\n== Standard metrics (2018-26, daily marked to the session close, 1 ES, capital 150K)")
    for lab, dd, tt in (("all", D, T18), ("2018-22", D[D.index.year <= 2022], T18[pd.DatetimeIndex(T18.entry_ts).year <= 2022]), ("2023+", D[D.index.year >= 2023], T18[pd.DatetimeIndex(T18.entry_ts).year >= 2023])):
        p = MT.perf(dd, tt.net, capital=150_000)
        print(f"   {lab:<8} Sharpe {p['sharpe']:.2f} Sortino {p['sortino']:.2f} PF {p['profit_factor']:.2f} Calmar {p['calmar']:.2f} Ulcer {p['ulcer']:.2f} maxDD ${p['max_dd']:,.0f} annual ${p['annual']:,.0f}")
    print("   longs only (the rule is long only); shorts = the mirror, in the breakdown below")

    print("\n== Beta controls (2018-26, our costs)")
    c = d.close.to_numpy(); last = pd.Series(c).groupby(d.sess.to_numpy()).last(); bh = last.diff().reindex(days_idx).fillna(0) * pv
    inm = (D != 0).mean(); print(f"   ES held every session: ${bh.sum():,.0f}; x its time in market ({inm:.0%} of sessions with P&L) = ${bh.sum() * inm:,.0f}; IBS rule ${T18.net.sum():,.0f}")
    hold_days = T18.days.to_numpy(); okk = np.flatnonzero((S.ok & (S.sess >= "2018-01-01")).to_numpy()); o = d.open.to_numpy(); rng = np.random.default_rng(1); res = []
    DI = S.di.to_numpy().astype(int)
    for _ in range(300):                                    # random decision sessions (only sessions with a decision bar), his hold lengths
        tot = 0.0; p = 0
        for hd in rng.permutation(hold_days):
            p = p + int(rng.integers(1, 6))
            if p + int(hd) >= len(okk): break
            e = o[DI[okk[p]] + 1]; x = o[DI[okk[p + int(hd)]] + 1]; tot += (x - e) * pv - 30.0; p = p + int(hd)
        res.append(tot)
    res = np.array(res); print(f"   random entry days with the same hold lengths, 300 runs: mean ${res.mean():,.0f}, p95 ${np.percentile(res, 95):,.0f}; p(random >= rule) {np.mean(res >= T18.net.sum()):.3f}")

    print("\n== Ingredient breakdown (one part changed at a time; our costs; whole 2016-26 / design 2018-22 / 2023+)")
    def ab(lab, t):
        yy = pd.DatetimeIndex(t.entry_ts).year
        print(line(t, lab) + f" | 18-22 ${t.net[(yy >= 2018) & (yy <= 2022)].sum():9,.0f} | 23+ ${t.net[yy >= 2023].sum():9,.0f}")
    ab("v5 as posted", T)
    ab("no emergency stop", run(d, S, stop=0)); ab("stop 2.0 ATR", run(d, S, stop=2.0)); ab("stop 3.5 ATR", run(d, S, stop=3.5))
    ab("no time stop", run(d, S, hold=0)); ab("time stop 3", run(d, S, hold=3)); ab("time stop 10", run(d, S, hold=10))
    ab("entry IBS < 0.10", run(d, S, ent=0.1)); ab("entry IBS < 0.30", run(d, S, ent=0.3))
    ab("exit IBS > 0.7", run(d, S, ex=0.7)); ab("exit IBS > 0.9", run(d, S, ex=0.9)); ab("exit close > prev high", run(d, S, exit_rule="prevhigh"))
    ab("short mirror", run(d, S, side=-1))
    S_rth = sessions(d, rth=True); ab("RTH range 08:30-14:59 (S30-like)", run(d, S_rth))
    ab("decision 15:14 (near the close)", run(d, sessions(d, dec=1514)))
    dn, _ = minutes("NQ"); Sn = sessions(dn); Tn = run(dn, Sn, sym="NQ"); ab("same rule on NQ (per NQ)", Tn)

    print("\n== Bootstrap + drawdown permutation, 2023+ holdout (1 ES daily, capital 150K)")
    B, P = RS.report({"IBS v5 ES": D[D.index.year >= 2023]}, n=3000, capital=150_000, limits=(10000, 20000, 40000)); print(B); print(P)
    print("\n== Monte Carlo at trading size (1 ES and 1 MES = x0.1; no trailing limit: personal account)")
    for size in (1.0, 0.1): print(MC.report(T18.net, D, size=size, label="IBS v5", trail=1e12))
    T18.assign(date=pd.DatetimeIndex(T18.exit_ts).normalize().strftime("%Y-%m-%d"),
               entry_date=(pd.DatetimeIndex(T18.entry_ts) + pd.Timedelta(hours=7) - pd.Timedelta(minutes=1)).normalize().strftime("%Y-%m-%d"))[["date", "entry_date", "entry_ts", "exit_ts", "entry", "exit", "why", "days", "net"]].to_csv("checks/candidates/ibs_globex/trades.csv", index=False)
    D.to_csv("checks/candidates/ibs_globex/daily.csv", header=["net"])
