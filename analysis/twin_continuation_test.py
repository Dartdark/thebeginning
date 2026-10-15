"""Twin Continuation (user's MultiCharts code, 2026-10-15): Swing Breakout (6h fractal swing levels, stop entries) + Morning
Momentum (10-min oscillator cross, 8:40-9:30 CT), one position at a time, NQ 1-minute, 24h session (17:00-16:00 CT).

Port of the PowerLanguage logic, minute by minute on our NQ 1-min grid (2017-12 .. 2026-10, CT, close-stamped):
  BO  session clock from 17:00; 15-min bars and 6-hour candles (17-23, 23-05, 05-11, 11-16) aligned to it; Wilder ATR(14) on
      15-min bars; swing high = 6h candle high >= the 3 candles before and after (confirmed at the 3rd candle after's close),
      'open' until any 1-min high reaches it; swing low mirror. At each 15-min close while flat and ATR ready: arm a buy stop at
      the open swing high (stop = last swing low) and/or a sell stop at the open swing low (stop = last swing high), if the
      previous session's range <= 2 x the 50-session average and the 15-min bar closes before 15:30. Orders live until the next
      15-min close (re-armed each 15 min) or a trade. Exits: stop at the swing level, target entry +/- 2 x ATR (limit, touch),
      market if the stop is already through the entry, at the close of the 15:45 bar. Positions can be held overnight.
  MO  10-min buckets by clock (all hours), EMA21 pivot of closes, RMA(14) true range, raw = (C - pivot) / (3 x ATR) x 100,
      osc = EMA3(raw); cross above +100 -> long, below -100 -> short, on a full 10-min bucket ending 8:40..9:30 CT, first
      qualifying signal per date, while flat, not on half days, after 60 buckets. Market entry next 1-min open; stop 75 pts;
      out at the 14:51 open.
Costs (CLAUDE.md): $7.25 + 1 tick per market / stop fill (limit target: no slip). The user's research costs ($5 + $1 a trade)
are shown alongside. Same-bar stop and target: stop first.
Tests: whole / BO / MO, longs and shorts, by year, 2018-22 vs 2023-26, standard metrics + bootstrap / permutation (2023+),
random-side placebo (same entry time, exits mirrored), correlation with the plan.
  python3 analysis/twin_continuation_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25


def flatten(g):
    o, h, l, c = (a.ravel() for a in (g.o, g.h, g.l, g.c)); ok = ~np.isnan(c)
    idx = np.where(ok)[0]
    row, j = idx // 1440, idx % 1440                                   # j = close minute of day
    start = (idx - 1)                                                   # global start minute
    sm = (j - 1 - 1020) % 1440                                          # minutes since 17:00 (bar start)
    sess = (start - 1020) // 1440
    return dict(o=o[idx], h=h[idx], l=l[idx], c=c[idx], row=row, j=j, sm=sm, sess=sess,
                date=g.dates[row], dow=pd.DatetimeIndex(g.ts[row]).dayofweek.to_numpy())


def half_day(d):
    m, dd = (d // 100) % 100, d % 100
    dts = pd.to_datetime(d.astype(str)); dow = dts.dayofweek.to_numpy()
    return ((m == 7) & (dd == 3)) | ((m == 12) & (dd == 24)) | ((m == 11) & (dow == 4) & (dd >= 23) & (dd <= 29))


def simulate(B, use_bo=True, use_mo=True, placebo_rng=None, max_stop_mult=0.0, mo_target=0.0, pv=PV, tick=TICK, comm=COMM, mo_stop=75.0, mo_stop_atr=0.0):
    n = len(B["c"]); o, h, l, c, sm, sess, j, date = (B[k] for k in ("o", "h", "l", "c", "sm", "sess", "j", "date"))
    halfd = half_day(date)
    # ---- precompute bucket boundaries (last existing bar of each 15m bucket / 6h candle / 10m bucket)
    k15 = sess * 100 + sm // 15; kc = sess * 10 + np.minimum(sm // 360, 3)
    k10 = B["row"] * 1000 + ((j - 1) % 1440) // 10
    last15 = np.r_[k15[1:] != k15[:-1], True]; lastc = np.r_[kc[1:] != kc[:-1], True]; last10 = np.r_[k10[1:] != k10[:-1], True]
    newsess = np.r_[True, sess[1:] != sess[:-1]]
    trades = []
    # state
    b15h = b15l = None; prevc15 = None; trn = 0; trsum = 0.0; atr = 0.0
    cH = cL = None; CH, CL = [], []
    swh = swl = None; swh_open = swl_open = False; got_h = got_l = None
    shi = slo = None; rngs = []; volratio = 0.0
    armed = False; okl = oks = False; lvll = lvls = stpl = stps = atru = 0.0; arm_trades = 0
    # MO
    a_piv, a_osc = 2 / 22, 2 / 4; mH = mL = None; mN = 0; mC = None; nb = 0; prevC = None; atrw = 0.0; piv = 0.0
    osc = None; oscp = None; traded_date = -1
    pos = 0; setup = None; ent = 0.0; ent_i = 0; stop = tgt = 0.0; pend_mo = 0; pend_bo = False; mo_exit_pend = False
    ntr = 0
    for i in range(n):
        # ---------------- fills during bar i (orders from bar i-1) ----------------
        if pos == 0 and pend_mo != 0:
            side = pend_mo if placebo_rng is None else placebo_rng.choice([-1, 1])
            dist = mo_stop_atr * B["atr"][i] if mo_stop_atr > 0 else mo_stop
            pos, setup, ent, ent_i = side, "MO", o[i], i; stop = ent - side * dist; pend_mo = 0
        elif pos == 0 and pend_bo:
            fl = fs = None
            if okl and h[i] >= lvll: fl = max(o[i], lvll)
            if oks and l[i] <= lvls: fs = min(o[i], lvls)
            if fl is not None and fs is not None:
                if abs(o[i] - lvll) <= abs(o[i] - lvls): fs = None
                else: fl = None
            if fl is not None or fs is not None:
                side = 1 if fl is not None else -1; px = fl if fl is not None else fs
                st = stpl if side > 0 else stps; tg = px + side * 2.0 * atru
                if max_stop_mult > 0 and (st - px) * side < 0:   # BO_MaxStopMult: stop no farther than k x ATR
                    st = max(st, px - max_stop_mult * atru) if side > 0 else min(st, px + max_stop_mult * atru)
                if placebo_rng is not None and placebo_rng.random() < 0.5:
                    side = -side; d_st, d_tg = abs(px - st), abs(tg - px); st = px - side * d_st; tg = px + side * d_tg
                pos, setup, ent, ent_i, stop, tgt = side, "BO", px, i, st, tg
                swh_open = swh_open and not (side > 0 and placebo_rng is None)
        elif pos != 0 and i > ent_i:
            px = None; kind = 2
            if setup == "MO":
                if mo_exit_pend: px, kind = o[i], 2
                elif (pos > 0 and l[i] <= stop) or (pos < 0 and h[i] >= stop):
                    px, kind = (min(o[i], stop) if pos > 0 else max(o[i], stop)), 0
                elif mo_target > 0 and ((pos > 0 and h[i] >= ent + mo_target) or (pos < 0 and l[i] <= ent - mo_target)):
                    px, kind = (max(o[i], ent + mo_target) if pos > 0 else min(o[i], ent - mo_target)), 1   # variant: MO profit target
            else:
                if (pos > 0 and stop >= ent) or (pos < 0 and stop <= ent):
                    if i == ent_i + 1: px, kind = o[i], 2
                if px is None and ((pos > 0 and l[i] <= stop) or (pos < 0 and h[i] >= stop)):
                    px, kind = (min(o[i], stop) if pos > 0 else max(o[i], stop)), 0
                elif px is None and ((pos > 0 and h[i] >= tgt) or (pos < 0 and l[i] <= tgt)):
                    px, kind = (max(o[i], tgt) if pos > 0 else min(o[i], tgt)), 1
                elif px is None and sm[i] + 1 >= 1365 and sm[i] < 1380:
                    px, kind = c[i], 2
            if px is not None:
                trades.append(dict(i0=ent_i, i1=i, setup=setup, side=pos, entry=ent, exit=px, kind=kind)); ntr += 1
                pos = 0; setup = None; mo_exit_pend = False
        # ---------------- bar-close script ----------------
        if swh_open and h[i] >= swh: swh_open = False
        if swl_open and l[i] <= swl: swl_open = False
        if newsess[i]:
            if shi is not None and shi > slo:
                rngs.append(shi - slo)
                volratio = rngs[-1] / np.mean(rngs[-51:-1]) if len(rngs) > 50 else 0.0
            shi, slo = h[i], l[i]
        else:
            shi, slo = max(shi, h[i]), min(slo, l[i])
        # 6h candle
        cH = h[i] if cH is None else max(cH, h[i]); cL = l[i] if cL is None else min(cL, l[i])
        if lastc[i]:
            CH.append(cH); CL.append(cL); cH = cL = None
            if len(CH) >= 7:
                a, b = CH[-7:], CL[-7:]
                if a[3] >= max(a[:3]) and a[3] >= max(a[4:]): got_h = a[3]
                if b[3] <= min(b[:3]) and b[3] <= min(b[4:]): got_l = b[3]
        b15h = h[i] if b15h is None else max(b15h, h[i]); b15l = l[i] if b15l is None else min(b15l, l[i])
        if last15[i]:
            tr = (b15h - b15l) if prevc15 is None else max(b15h, prevc15) - min(b15l, prevc15)
            trn += 1
            if trn <= 14:
                trsum += tr
                if trn == 14: atr = trsum / 14
            else: atr = (atr * 13 + tr) / 14
            prevc15 = c[i]; b15h = b15l = None
            if got_h is not None:
                swh = got_h; swh_open = c[i] < swh and h[i] < swh; got_h = None
            if got_l is not None:
                swl = got_l; swl_open = c[i] > swl and l[i] > swl; got_l = None
            armed = False
            if pos == 0 and trn >= 14:
                atru = atr; lvll, stpl, lvls, stps = (swh or 0), (swl or 0), (swl or 0), (swh or 0)
                okl = swh_open and swl is not None and stpl < lvll
                oks = swl_open and swh is not None and stps > lvls
                armed = use_bo and (okl or oks) and sm[i] < 1350 - 1      # 15:30 CT = 1350 min after 17:00
                if volratio > 2.0: armed = False
                arm_trades = ntr
        # MO 10-min bucket
        mH = h[i] if mH is None else max(mH, h[i]); mL = l[i] if mL is None else min(mL, l[i]); mN += 1; mC = c[i]
        fire = 0
        if last10[i]:
            full = mN == 10; endt = ((((j[i] - 1) % 1440) // 10) + 1) * 10; endt = (endt // 60) * 100 + endt % 60
            nb += 1
            if nb == 1: trv = mH - mL; atrw = trv; piv = mC
            else:
                trv = max(mH - mL, abs(mH - prevC), abs(mL - prevC)); atrw += (trv - atrw) / 14; piv += (mC - piv) * a_piv
            prevC = mC; s = 0
            if atrw > 0:
                raw = (mC - piv) / (3 * atrw) * 100
                if osc is None: osc = raw
                else:
                    oscp = osc; osc += (raw - osc) * a_osc
                    if osc > 100 and oscp <= 100: s = 1
                    elif osc < -100 and oscp >= -100: s = -1
            if s != 0 and 840 <= endt <= 930 and full and traded_date != date[i] and not halfd[i] and pos == 0 and nb >= 60:
                traded_date = date[i]
                if use_mo: fire = s
            mH = mL = None; mN = 0
        # orders for the next bar
        pend_mo = 0
        if fire != 0: armed = False; pend_mo = fire
        if armed and (pos != 0 or ntr > arm_trades): armed = False
        pend_bo = armed and pos == 0 and sm[i] + 1 < 1350 and fire == 0
        if pos != 0 and setup == "MO" and 1450 <= (j[i] // 60) * 100 + j[i] % 60 <= 1600: mo_exit_pend = True
    T = pd.DataFrame(trades)
    T["slips"] = np.where(T.kind == 1, 1, 2)
    T["net"] = (T.exit - T.entry) * T.side * pv - comm - T.slips * tick * pv
    T["net_user"] = (T.exit - T.entry) * T.side * pv - 6.0
    T["pct"] = (T.exit - T.entry) * T.side / T.entry * 100 - (comm / pv + T.slips * tick) / T.entry * 100
    T["date"] = pd.to_datetime(B["date"][T.i1].astype(str))
    T["edate"] = pd.to_datetime(B["date"][T.i0].astype(str))
    T["ej"] = B["j"][T.i0]; T["xj"] = B["j"][T.i1]
    return T


def line(x, nm, w=26):
    x = x.dropna(); y = x.index.year; by = x.groupby(y).sum()
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum()); t = x.mean() / x.std() * np.sqrt(len(x))
    return (f"   {nm:<{w}} n {len(x):5d} avg ${x.mean():6.1f} PF {pf:4.2f} t {t:5.2f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 2018-22 ${x[y < 2023].mean():6.1f} 2023-26 ${x[y >= 2023].mean():6.1f}")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); B = flatten(g)
    T = simulate(B); T = T[T.date >= "2018-01-01"].reset_index(drop=True); T.to_pickle(SP + "twin_trades.pkl")
    X = T.set_index("date")
    print(f"\n{len(T)} trades {T.date.min().date()} .. {T.date.max().date()}; overnight-held BO trades {(T.edate != T.date).mean():.0%}")
    for nm, m in (("ALL", slice(None)), ("BO", X.setup == "BO"), ("MO", X.setup == "MO")):
        x = X[m] if not isinstance(m, slice) else X
        print(line(x.net, f"{nm} net (repo costs)")); print(line(x.net_user, f"{nm} net ($5 + $1)"))
        for s, sn in ((1, "longs"), (-1, "shorts")):
            print(line(x[x.side == s].net, f"   {nm} {sn}"))
    print("\n   by year (repo costs):", X.net.groupby(X.index.year).sum().round(0).to_dict())
    print("   BO exits:", X[X.setup == "BO"].kind.map({0: "stop", 1: "target", 2: "time/mkt"}).value_counts().to_dict(),
          "| MO exits:", X[X.setup == "MO"].kind.map({0: "stop", 1: "target", 2: "time"}).value_counts().to_dict())
    days = pd.bdate_range("2018-01-01", X.index.max())
    rows = {}
    for nm, x in (("ALL", X.net), ("longs", X[X.side == 1].net), ("shorts", X[X.side == -1].net),
                  ("BO", X[X.setup == "BO"].net), ("MO", X[X.setup == "MO"].net)):
        rows[nm] = (x.groupby(level=0).sum().reindex(days, fill_value=0.0), x)
    print("\nStandard metrics (1 NQ, repo costs):"); print(M.table(rows))
    b_, p_ = R.report({k: v[0][v[0].index >= "2023"] for k, v in rows.items()}, n=2000)
    print("\n2023+ bootstrap:\n" + b_ + "\n\n2023+ drawdown permutation:\n" + p_)
    print("\nRandom-side placebo (same entry times, exits mirrored), 20 runs:")
    pl = []
    for s in range(20):
        P = simulate(B, placebo_rng=np.random.default_rng(s)); P = P[P.date >= "2018-01-01"]
        pl.append((P.net.mean(), P[P.setup == "BO"].net.mean(), P[P.setup == "MO"].net.mean()))
    pl = np.array(pl)
    for k, nm in enumerate(("ALL", "BO", "MO")):
        real = [X.net, X[X.setup == "BO"].net, X[X.setup == "MO"].net][k].mean()
        print(f"   {nm}: real ${real:.1f}; placebo mean ${pl[:, k].mean():.1f}, max ${pl[:, k].max():.1f}; share >= real {np.mean(pl[:, k] >= real):.2f}")
