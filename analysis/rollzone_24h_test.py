"""RollZone 24h NQ Long v1 (RZL1): user upload 2026-10-31 (PowerLanguage + research note, Zarattini-Aziz-Barbon 'noise
area' idea on the 24h Globex session). Code review: agents/cross_review/CODE_REVIEW_LOG.md (2026-10-31 (4)).

Python port of the signal as written (5-minute bars stamped at their close, 24h session from 17:00 CT, 1-minute 'bar
magnifier' for the entry stop / stop / target), on Grid24 (data/NQ_1min_*.csv + NQ_1min_ON_*.csv, CT).
  zone: centre = session open, half-width = 0.75 x the 14-session average |slot close - session open| of the 15-min slot,
        a 5-min close beyond a line by > 0.05 x DailyATR re-centres it there and widens it by 1 + break / DailyATR (0.5-3);
        DailyATR = average high-low of the last 30 completed sessions.
  entry: buy stop at the next bar's upper line, only after a bar whose high stayed below it; one position.
  windows (fill bar end, CT): 17:00-15:30, none 01:00-07:00 and 08:30-09:00; half days none from 11:30.
  exits: target 1.40 x DailyATR, stop 0.80 x DailyATR cut to the session's remaining loss budget (DailyLossCap minus the
         session's closed losses); night exit at 08:25 (market, next bar open), day exit 15:55, half days 11:55,
         carry exit at the next session's first bar.
  Good Friday: the review's fix (no entries in the Good Friday session) unless --as-uploaded.

Variants (budget per contract, in NQ points; 1 NQ = $20 / pt):
  NQCAP  the note's run: 1 NQ with DailyLossCap $1,500 = 75 pts (on MNQ: $150 per micro; the cap sets most stops)
  ATR    1 MNQ with the default $1,500 cap = 750 pts per micro (never binding: the plain 0.8 x ATR stop)
Fills: entry stop at max(minute open, line); stop at min(minute open, stop) (long); target needs 1 tick through (MC's
'fill limit +1'), stop checked first when both are in one minute and on the entry minute. Costs: $7.25 per NQ round trip
+ 1 tick per stop / market fill (entry stop, protective stop, time exits; the target is a limit).
Roll jumps (continuous contract not back-adjusted): trades whose entry -> exit window holds a roll bar are dropped
(rolls as s_rank_gap_round2_test.rolls_index); the indicator state still sees the roll sessions.

Run: python3 analysis/rollzone_24h_test.py [--as-uploaded]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd

PV, TICK, COMM = 20.0, 0.25, 7.25
CACHE = os.environ.get("RZ_CACHE", "scratch_data/rz_g24.pkl")


def grid():
    if os.path.exists(CACHE):
        return pickle.load(open(CACHE, "rb"))
    from grid24 import Grid24
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    g = Grid24(root + "/data/NQ_1min_20*.csv", root + "/data/NQ_1min_ON_*.csv")
    pickle.dump(g, open(CACHE, "wb"), protocol=4)
    return g


def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    return pd.Timestamp(y, (h + l - 7 * m + 114) // 31, (h + l - 7 * m + 114) % 31 + 1)


def short_day(ts):
    m, dd, w, y = ts.month, ts.day, (ts.dayofweek + 1) % 7, ts.year      # w: 0 = Sunday, as PowerLanguage
    return ((m == 1 and w == 1 and 15 <= dd <= 21) or (m == 1 and w == 1 and dd == 2) or (m == 2 and w == 1 and 15 <= dd <= 21)
            or (m == 5 and w == 1 and dd >= 25)
            or (m == 6 and y >= 2022 and ((dd == 19 and 1 <= w <= 5) or (dd == 18 and w == 5) or (dd == 20 and w == 1)))
            or (m == 7 and dd == 3 and 1 <= w <= 5) or (m == 7 and dd == 4 and 1 <= w <= 5) or (m == 7 and dd == 5 and w == 1)
            or (m == 9 and w == 1 and dd <= 7) or (m == 11 and w == 4 and 22 <= dd <= 28) or (m == 11 and w == 5 and 23 <= dd <= 29)
            or (m == 12 and dd == 24 and 1 <= w <= 5) or (m == 12 and dd == 26 and w == 1))


def bars5_aligned(g):
    """5-minute bars closing at minute 5k (k = 1..288 per date; k = 288 is 24:00 = the next date's 00:00 column):
    columns 5k-4 .. 5k. Built on the flattened minute series shifted by one."""
    D = g.D; N = D * 1440
    def flat(a):
        x = a.ravel(); return np.r_[x[1:], np.nan]          # x'[j] = minute j + 1
    o, h, l, c = (flat(getattr(g, k)).reshape(D * 288, 5) for k in "ohlc")
    has = ~np.isnan(c); any_ = has.any(1)
    first = np.argmax(has, 1); last = 4 - np.argmax(has[:, ::-1], 1)
    idx = np.nonzero(any_)[0]
    O = o[idx, first[idx]]; C = c[idx, last[idx]]
    H = np.nanmax(np.where(has[idx], h[idx], -np.inf), 1); L = np.nanmin(np.where(has[idx], l[idx], np.inf), 1)
    endmin = idx * 5 + 5                                     # flat minute index (0 = row 0's 00:00) of the bar's close
    return dict(end=endmin, O=O, H=H, L=L, C=C, o=o[idx], h=h[idx], l=l[idx], c=c[idx])


def run(g, B, cap_pts=75.0, gf_fix=True, noise=0.75, sig_len=14, atr_len=30, tgt_atr=1.40, stp_atr=0.80,
        night=True, no_entry=(100, 700), rolls=None, rand=None):
    TS = pd.DatetimeIndex(g.ts)
    end = B["end"]; row = end // 1440; mod = end % 1440
    # a bar closing at 24:00 belongs to the next date (stamped 00:00 there)
    datei = row.copy(); hhmm = (mod // 60) * 100 + mod % 60
    n = len(end)
    anchor = 17 * 60; barmins = 5; slot = 15
    def m_after(hhmm_): return ((hhmm_ // 100) * 60 + hhmm_ % 100 - anchor + 1440) % 1440
    EST, EEN, SHS, SHE, FLT = m_after(1700), m_after(1530), m_after(830), m_after(900), m_after(1558)
    NES, NEE = m_after(no_entry[0]), m_after(no_entry[1])
    SDS, SDF = 11 * 60 + 30, 11 * 60 + 58
    barmin = mod
    SM = (barmin - anchor - 1 + 2880) % 1440 + 1
    FSM = SM + barmins; FSM = np.where(FSM > 1440, FSM - 1440, FSM)
    slot_now = (SM - 1) // slot; slot_next = (FSM - 1) // slot
    in_entry = (FSM > EST) & (FSM <= EEN)
    in_shut = (FSM >= SHS) & (FSM <= SHE)
    if NES == NEE: in_noent = np.zeros(n, bool)
    elif NEE > NES: in_noent = (FSM > NES) & (FSM <= NEE)
    else: in_noent = (FSM > NES) | (FSM <= NEE)
    days = TS[datei]
    uniq = np.unique(datei)
    sd = {r: short_day(TS[r]) for r in uniq}
    isshort = np.array([sd[r] for r in datei])
    sblock = isshort & (barmin + barmins >= SDS) & (barmin < anchor)
    sflat = isshort & (barmin + barmins >= SDF) & (barmin < anchor)
    gfd = {easter(y) - pd.Timedelta(days=2) for y in range(2016, 2028)}
    gf_sess = np.array([(TS[r] in gfd) for r in datei]) | \
        (np.array([(TS[r] + pd.Timedelta(days=1)) in gfd for r in datei]) & (barmin >= anchor))
    if not gf_fix: gf_sess[:] = False
    O, H, L, C, o, h, l = B["O"], B["H"], B["L"], B["C"], B["o"], B["h"], B["l"]
    rcum = None
    if rolls is not None:
        rb = np.zeros(g.D * 1440 + 2); rb[np.asarray(rolls, int) + 1] = 1; rcum = np.cumsum(rb)

    slot_hist = np.zeros((100, 100)); slot_ptr = np.zeros(100, int); slot_cnt = np.zeros(100, int); slot_sum = np.zeros(100)
    rng = []; atr = 0.0
    have = False; s_hi = s_lo = s_open = 0.0; zc = 0.0; wf = 1.0
    pos = 0; entry = 0.0; e_end = 0; stop_px = tgt_px = np.nan
    sess_pl = 0.0                    # closed P&L (points, gross) since the session open
    pend_entry = None; pend_exit = None; pend_amts = None
    trades = []
    rgen = np.random.default_rng(rand[1]) if rand else None

    def close_trade(px, minute_idx, kind, i):
        nonlocal pos, sess_pl
        pts = px - entry
        sess_pl += pts
        trades.append((e_end, int(minute_idx), entry, px, kind, pts))
        pos = 0

    prev_sm = None
    for i in range(n):
        # ---------------- fills inside bar i (orders placed at bar i-1's close) ----------------
        if pos and pend_exit:
            close_trade(O[i], end[i] - 4, pend_exit, i)                    # market at the bar's open
        elif pos:
            st, tg = pend_amts
            for k in range(5):
                if np.isnan(o[i][k]): continue
                if l[i][k] <= st:
                    close_trade(min(o[i][k], st), end[i] - 4 + k, "stop", i); break
                if h[i][k] >= tg + TICK:
                    close_trade(max(o[i][k], tg), end[i] - 4 + k, "target", i); break
        elif pend_entry is not None:
            line, st_pts, tg_pts = pend_entry
            for k in range(5):
                if np.isnan(o[i][k]): continue
                if pos == 0 and h[i][k] >= line:
                    entry = max(o[i][k], line); pos = 1; e_end = end[i] - 4 + k
                    st, tg = entry - st_pts, entry + tg_pts
                    if l[i][k] <= st:
                        close_trade(st, e_end, "stop", i)
                    break
            if pos:
                for k2 in range(k + 1, 5):
                    if np.isnan(o[i][k2]): continue
                    if l[i][k2] <= st:
                        close_trade(min(o[i][k2], st), end[i] - 4 + k2, "stop", i); break
                    if h[i][k2] >= tg + TICK:
                        close_trade(max(o[i][k2], tg), end[i] - 4 + k2, "target", i); break
            if pos: pend_amts = (st, tg)
        pend_entry = None; pend_exit = None

        # ---------------- bar i close: the signal ----------------
        sm = SM[i]
        is_open = prev_sm is not None and sm < prev_sm
        if have and i > 0 and (is_open or slot_now[i] != slot_now[i - 1]):
            kk = slot_now[i - 1]
            if 0 <= kk <= 99 and s_open > 0:
                v = abs(C[i - 1] - s_open)
                if slot_cnt[kk] >= sig_len: slot_sum[kk] -= slot_hist[kk, slot_ptr[kk]]
                slot_hist[kk, slot_ptr[kk]] = v; slot_sum[kk] += v
                slot_ptr[kk] = (slot_ptr[kk] + 1) % sig_len
                if slot_cnt[kk] < sig_len: slot_cnt[kk] += 1
        if is_open:
            sess_pl = 0.0
            if have and s_hi - s_lo > 0:
                rng.insert(0, s_hi - s_lo); rng = rng[:100]
                if len(rng) >= atr_len: atr = sum(rng[:atr_len]) / atr_len
            have = True
            s_hi, s_lo, s_open, zc, wf = H[i], L[i], O[i], O[i], 1.0
        else:
            s_hi = max(s_hi, H[i]); s_lo = min(s_lo, L[i])
        prev_sm = sm
        conf = 0.05 * atr
        sn = slot_now[i]
        sig_now = slot_sum[sn] / sig_len if slot_cnt[sn] >= sig_len else 0.0
        zone_ok = have and zc > 0 and atr > 0 and len(rng) >= atr_len and sig_now > 0
        if zone_ok:
            zw = noise * sig_now * wf; ztop, zbot = zc + zw, zc - zw
            if C[i] < zbot - conf:
                wf = min(max(1 + (zbot - C[i]) / atr, 0.5), 3.0); zc = C[i]
            elif C[i] > ztop + conf:
                wf = min(max(1 + (C[i] - ztop) / atr, 0.5), 3.0); zc = C[i]
        snx = slot_next[i]
        sig_next = slot_sum[snx] / sig_len if slot_cnt[snx] >= sig_len else 0.0
        ord_ok = zone_ok and sig_next > 0
        if ord_ok: otop = zc + noise * sig_next * wf

        if pos:
            if is_open: pend_exit = "carry"
            elif sm + barmins >= FLT: pend_exit = "eod"
            elif sflat[i]: pend_exit = "half"
            elif night and SHE > SHS and sm + barmins >= SHS and sm < SHE: pend_exit = "night"
        tg_pts = tgt_atr * atr if atr > 0 else 1e9
        st_pts = stp_atr * atr if atr > 0 else 1e9
        budget = cap_pts + sess_pl
        ok_budget = budget > 0
        if ok_budget: st_pts = min(st_pts, budget)
        if pos and not pend_exit:
            pend_amts = (entry - st_pts, entry + tg_pts)
        base = (ord_ok and pos == 0 and ok_budget and in_entry[i] and not in_shut[i] and not in_noent[i]
                and not sblock[i] and FSM[i] + barmins < FLT and not gf_sess[i])
        if rand:                                                   # placebo: market buy at a random allowed bar
            if base and rgen.random() < rand[0]:
                pend_entry = (-1e18, st_pts, tg_pts)
        elif base and H[i] < otop:
            pend_entry = (otop, st_pts, tg_pts)

    t = pd.DataFrame(trades, columns=["e", "x", "entry", "exit", "kind", "pts"])
    erow, xrow = t.e // 1440, t.x // 1440
    t["entry_time"] = TS[erow] + pd.to_timedelta(t.e % 1440, unit="m")
    t["exit_time"] = TS[xrow] + pd.to_timedelta(t.x % 1440, unit="m")
    # Apex trading date: a fill after 17:00 belongs to the next weekday session
    et = t.entry_time
    td = (et + pd.to_timedelta((et.dt.hour >= 17).astype(int), unit="D")).dt.normalize()
    td = td + pd.to_timedelta(np.where(td.dt.dayofweek == 5, 2, np.where(td.dt.dayofweek == 6, 1, 0)), unit="D")
    t["date"] = td
    t["night"] = (et.dt.hour >= 17) | (et.dt.hour * 100 + et.dt.minute <= 830)
    ticks = 1 + (t.kind != "target")                            # entry stop + stop / market exit
    t["gross"] = t.pts * PV
    t["net"] = t.gross - COMM - ticks * TICK * PV
    Lf = g.l.ravel()
    lo = np.array([np.nanmin(Lf[a:b + 1]) for a, b in zip(t.e, t.x)]) if len(t) else np.array([])
    t["adv"] = np.minimum((lo - t.entry) * PV - COMM - ticks * TICK * PV, t.net)    # worst open P&L during the hold, after costs
    t["roll"] = False
    if rcum is not None:
        t["roll"] = (rcum[np.clip(t.x.to_numpy(), 0, len(rcum) - 2) + 1] - rcum[np.clip(t.e.to_numpy(), 0, len(rcum) - 2)]) > 0
    return t


def daily(t, days):
    x = t.net.groupby(t.date).sum()
    return x.reindex(days, fill_value=0.0)


if __name__ == "__main__":
    import metrics as M, resampling as R, montecarlo as MC
    g = grid()
    B = bars5_aligned(g)
    import s_rank_gap_round2_test as SG
    S = SG.Sym("NQ", g); rolls, info = SG.rolls_index(S)
    days = S.days                                     # weekday trading dates from 2018
    gf = "--as-uploaded" not in sys.argv
    print(f"Good Friday fix: {'on' if gf else 'OFF (as uploaded)'}; roll bars: {len(rolls)}; per 1 NQ after $7.25 + 1 tick per stop/market fill")
    out = {}
    for name, cap in (("NQCAP", 75.0), ("ATR", 750.0)):
        t = run(g, B, cap_pts=cap, gf_fix=gf, rolls=rolls)
        t = t[(t.date >= "2018-01-01") & ~t.roll]
        out[name] = t
        d = daily(t, days)
        print(f"\n==== {name} ({'session budget 75 pts = the note: $1,500 on 1 NQ / $150 per MNQ' if cap == 75 else 'plain 0.8 x DailyATR stop'}): "
              f"{len(t)} trades, exits {t.kind.value_counts().to_dict()}")
        y = t.groupby(t.date.dt.year).agg(n=("net", "size"), gross=("gross", "sum"), net=("net", "sum"), avg=("net", "mean"))
        y["pf"] = t.groupby(t.date.dt.year).net.apply(lambda x: x[x > 0].sum() / -x[x < 0].sum())
        print(y.round(2).to_string())
        D, H_ = d[d.index < "2023-01-01"], d[d.index >= "2023-01-01"]
        td, th = t[t.date < "2023-01-01"], t[t.date >= "2023-01-01"]
        rows = {"whole 2018-26": (d, t.net), "design 2018-22": (D, td.net), "holdout 2023+": (H_, th.net),
                "night entries": (daily(t[t.night], days), t[t.night].net), "day entries": (daily(t[~t.night], days), t[~t.night].net)}
        print(M.table(rows, capital=50_000.0))
        for nm, x in (("whole", d), ("design", D), ("holdout", H_)):
            tt = x.mean() / x.std() * np.sqrt(len(x)); print(f"   daily t {nm}: {tt:.2f}", end="")
        print()
        b_, p_ = R.report({"holdout 2023+ (long only = whole)": H_})
        print(b_); print(p_)
        for sz, lab in ((0.1, "1 MNQ"), (0.4, "4 MNQ")):
            print(MC.report(t.net.values, daily=d.values, size=sz, label=f"{name} {lab}"))
    # placebo: same windows, budget and exits, entries at random allowed bars (trade count matched)
    print("\n==== placebo: random-bar market entries, same windows / budget / exits (20 seeds each)")
    for name, cap in (("NQCAP", 75.0), ("ATR", 750.0)):
        real = out[name]; res = []
        for p in (0.02,):
            for sd in range(20):
                u = run(g, B, cap_pts=cap, gf_fix=gf, rolls=rolls, rand=(p, sd)); u = u[(u.date >= "2018-01-01") & ~u.roll]
                res.append((len(u), u.net.mean(), u.net.sum(), u[u.date >= "2023-01-01"].net.mean(), u[u.date < "2023-01-01"].net.mean()))
        r = pd.DataFrame(res, columns=["n", "avg", "total", "avg23", "avg1822"])
        print(f"  {name}: real {len(real)} trades avg ${real.net.mean():.0f} (2018-22 ${real[real.date < '2023-01-01'].net.mean():.0f}, "
              f"2023+ ${real[real.date >= '2023-01-01'].net.mean():.0f}); placebo n {r.n.mean():.0f}, avg ${r.avg.mean():.0f} "
              f"[{r.avg.min():.0f}, {r.avg.max():.0f}], 2018-22 ${r.avg1822.mean():.0f}, 2023+ ${r.avg23.mean():.0f}; "
              f"real beats {100 * (r.avg < real.net.mean()).mean():.0f}% of placebo runs")
    for name, t in out.items():
        os.makedirs("checks/candidates/rollzone_24h", exist_ok=True)
        t.to_csv(f"checks/candidates/rollzone_24h/python_trades_{name}.csv", index=False)
