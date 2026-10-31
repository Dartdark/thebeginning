"""Brooks price-action bot v201 (user's bot_v201_SHARE.py + write-up, 2026-10-25; checks/candidates/brooks_bot/): is the surviving
setup book an edge or long beta? Rebuild of the ten detectors on our 24-hour 1-minute grids, NQ (= USTEC) and YM (= US30),
5- and 15-minute bars aligned to the clock, 2018-2026.
  Detectors as coded (signal candle = the last CLOSED bar i, the bot's df.iloc[-2]; df.iloc[-1] is the forming bar i+1, here
  its open). EMA20 = the full-series EMA (the bot's 30-50-bar window EMA differs a little). Strong bar = close in the top /
  bottom 25% of its range. market_direction, in_trading_range and detect_regime (ADX-like dx, volatility, 1-hour direction)
  as coded; each regime runs its setup set. Surviving book = the bot's gates: DISABLED_SETUPS, DIRECTION_LOCK, blocked UTC
  hours {0, 3, 14, 19, 21}, no new trades 20:00-21:59 UTC, all flat at 20:30 UTC.
  Orders as place_order: the forming bar's open beyond the entry -> stop order, short of it -> limit order (a pull-back fill),
  else market. Pending up to 2 hours; cancelled if price trades through the stop first. Stop = the setup's stop, target 1:1.
  Fills on 1-minute bars: a stop or limit the minute opens beyond fills at the open; a minute touching stop and target counts
  as the stop.
Costs per contract: $7.25 NQ / $5 YM round trip + 1 tick per market or stop fill (entry stop orders and stop exits; limit
entries and the target pay none). R = net $ / ($ distance entry -> stop).
Beta control: each trade is matched with 5 random-time trades (same symbol, side, year and UTC hour, same stop distance as a %
of price, market entry, same 1:1 bracket and EOD rule). Edge over drift = trade R - matched random R.
  python3 analysis/brooks_bot_test.py [SCRATCH_DIR] > analysis/outputs/brooks_bot_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from numba import njit

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"NQ": ("g24", 20.0, 0.25, 7.25), "YM": ("gy", 5.0, 1.0, 5.0)}
DISABLED = {("5m", "double_top"), ("15m", "wedge"), ("15m", "bar_reversal"), ("5m", "trend_bar"), ("5m", "bar_reversal")}
LOCK = {"climactic_reversal": 1, "double_top": -1, "range_fade": -1}
BLOCK_H = {0, 3, 14, 19, 21}
TREND = {"trend_bar", "first_pullback", "two_leg_pullback", "wedge"}
RANGE = {"range_fade", "double_top", "double_bottom", "bar_reversal", "ii_pattern", "iii_pattern"}
VOLAT = {"climactic_reversal", "failed_bo", "wedge", "double_top", "double_bottom"}
VOL_BLOCK = {"double_top", "wedge", "two_leg_pullback"}


def load(sym):
    g = pickle.load(open(SP + SPEC[sym][0] + ".pkl", "rb"))
    O, H, L, C = (getattr(g, k).ravel() for k in "ohlc")
    ts = pd.DatetimeIndex(np.repeat(g.ts, 1440)) + pd.to_timedelta(np.tile(np.arange(1440), len(g.ts)), unit="m")
    utc = ts.tz_localize("America/Chicago", ambiguous="NaT", nonexistent="NaT").tz_convert("UTC")
    uh = np.asarray(utc.hour, dtype=float); um = np.asarray(utc.minute, dtype=float)
    uh[pd.isna(utc)] = -1
    return g, O, H, L, C, uh, um, ts


def bars(O, H, L, C, k):
    """Clock-aligned k-minute bars from the flat 1-minute arrays; returns OHLC + the flat index of each bar's last minute."""
    n = len(C) // k * k
    o, h, l, c = (x[:n].reshape(-1, k) for x in (O, H, L, C))
    ok = ~np.isnan(c).all(1)
    with np.errstate(all="ignore"):
        hh, ll = np.nanmax(h, 1), np.nanmin(l, 1)
    first = np.argmax(~np.isnan(o), 1); last = k - 1 - np.argmax(~np.isnan(c[:, ::-1]), 1)
    oo = o[np.arange(len(o)), first]; cc = c[np.arange(len(c)), last]
    end = np.arange(len(c)) * k + last
    sel = np.where(ok)[0]
    return dict(o=oo[sel], h=hh[sel], l=ll[sel], c=cc[sel], end=end[sel])


def rmax(x, a, b):
    """max of x over offsets [a, b] relative to each index (a <= b <= 0)."""
    s = pd.Series(x); return s.shift(-b).rolling(b - a + 1).max().to_numpy()


def rmin(x, a, b):
    s = pd.Series(x); return s.shift(-b).rolling(b - a + 1).min().to_numpy()


def shift(x, k):
    return pd.Series(x).shift(k).to_numpy()


def direction(B, ema, a=2 / 21):
    """market_direction with df ending at the forming bar i+1 (its open)."""
    o1 = shift(B["o"], -1)
    ema_f = ema + a * (o1 - ema)
    slope = (ema_f - shift(ema, 3)) / shift(ema, 3) * 100
    r_hi = np.fmax(rmax(B["h"], -8, 0), o1); r_lo = np.fmin(rmin(B["l"], -8, 0), o1)
    p_hi = rmax(B["h"], -18, -9); p_lo = rmin(B["l"], -18, -9)
    d = np.zeros(len(ema), int)
    d[(slope > 0.05) & (r_hi > p_hi) & (r_lo > p_lo)] = 1
    d[(slope < -0.05) & (r_hi < p_hi) & (r_lo < p_lo)] = -1
    return d


def detect(B, d1h, tf):
    o, h, l, c = B["o"], B["h"], B["l"], B["c"]; n = len(c)
    rng = h - l; pos = np.where(rng > 0, (c - l) / np.where(rng > 0, rng, 1), 0.5)
    sb, ss = pos >= 0.75, pos <= 0.25
    ema = pd.Series(c).ewm(span=20, adjust=False).mean().to_numpy()
    D = direction(B, ema)
    # regime (detect_regime): dx over the last 20 bars of the 50-bar df (bars i-18 .. i+1, forming bar = its open)
    o1 = shift(o, -1)
    hs = np.c_[[shift(h, k) for k in range(18, -1, -1)]].T; ls = np.c_[[shift(l, k) for k in range(18, -1, -1)]].T
    hs = np.c_[hs, o1]; ls = np.c_[ls, o1]
    up = np.clip(np.diff(hs, axis=1), 0, None).mean(1); dn = np.clip(-np.diff(ls, axis=1), 0, None).mean(1)
    dx = np.where(up + dn > 0, np.abs(up - dn) / np.where(up + dn > 0, up + dn, 1) * 100, 0)
    recent = (shift(rng, 1) + rng + 0) / 3; avg = pd.Series(rng).shift(2).rolling(17).mean().to_numpy()
    volat = recent > 2 * avg
    reg = np.full(n, "ranging", object)
    tb = (dx > 20) & ((D == 1) | (d1h == 1)); tr_ = (dx > 20) & ~tb & ((D == -1) | (d1h == -1))
    reg[tb] = "bull"; reg[tr_] = "bear"
    w = (dx > 10) & (reg == "ranging"); reg[w & (D == 1)] = "bull"; reg[w & (D == -1)] = "bear"
    reg[volat] = "volatile"
    S = []                                                    # (name, side, entry, stop) per bar, possibly several

    def add(name, mask, side, entry, stop):
        for i in np.where(mask & np.isfinite(entry) & np.isfinite(stop))[0]:
            S.append((i, name, side, entry[i], stop[i]))

    # trend_bar
    cl = np.c_[[shift(c, k) for k in (4, 3, 2, 1)]].T
    down2 = (np.diff(cl, axis=1) < 0).sum(1) >= 2; up2 = (np.diff(cl, axis=1) > 0).sum(1) >= 2
    add("trend_bar", (D == 1) & sb & down2, 1, h, l); add("trend_bar", (D == -1) & ss & up2, -1, l, h)
    # failed_bo: prev high > max(high of bars i-10..i-1) can never be true (the window holds the prev bar) -> never fires
    # two_leg_pullback
    L6 = np.c_[[shift(l, k) for k in (6, 5, 4, 3, 2, 1)]].T; H6 = np.c_[[shift(h, k) for k in (6, 5, 4, 3, 2, 1)]].T
    leg1b = (L6[:, 1:4] < L6[:, 0:3]).any(1); leg2b = (L6[:, 4:6] < L6[:, 3:5]).any(1)
    leg1s = (H6[:, 1:4] > H6[:, 0:3]).any(1); leg2s = (H6[:, 4:6] > H6[:, 3:5]).any(1)
    add("two_leg_pullback", (D == 1) & (np.abs(l - ema) / ema < 0.003) & leg1b & leg2b & sb & (L6.min(1) < h), 1, h, L6.min(1))
    add("two_leg_pullback", (D == -1) & (np.abs(h - ema) / ema < 0.003) & leg1s & leg2s & ss & (H6.max(1) > l), -1, l, H6.max(1))
    # range_fade (in_trading_range over bars i-18 .. i+1)
    rh = np.fmax(rmax(h, -18, 0), o1); rl = np.fmin(rmin(l, -18, 0), o1); rr = rh - rl
    isr = rr / ((rh + rl) / 2) < 20 * 0.0012
    add("range_fade", isr & (c >= rh - 0.15 * rr) & ss, -1, l, rh + 0.1 * rr)
    add("range_fade", isr & (c <= rl + 0.15 * rr) & sb, 1, h, rl - 0.1 * rr)
    # wedge (bars i-8 .. i-1)
    h0, h7, l0, l7 = shift(h, 8), shift(h, 1), shift(l, 8), shift(l, 1)
    hsl, lsl = (h7 - h0) / 8, (l7 - l0) / 8
    add("wedge", (h7 > h0) & (l7 > l0) & (lsl > hsl) & ss, -1, l, h)
    add("wedge", (h7 < h0) & (l7 < l0) & (np.abs(lsl) > np.abs(hsl)) & sb, 1, h, l)
    # double top / bottom (bars i-13 .. i-7 and i-6 .. i-1)
    fh, sh = rmax(h, -13, -7), rmax(h, -6, -1); fl, sl_ = rmin(l, -13, -7), rmin(l, -6, -1)
    add("double_top", (np.abs(fh - sh) / fh < 0.003) & ss & (sh * 1.002 > l), -1, l, sh * 1.002)
    dbm = (np.abs(fl - sl_) / fl < 0.003) & sb & ~((np.abs(fh - sh) / fh < 0.003) & ss)
    add("double_bottom", dbm & (h > sl_ * 0.998), 1, h, sl_ * 0.998)
    # bar_reversal (bars i-13 .. i-1)
    s_hi, s_lo = rmax(h, -13, -1), rmin(l, -13, -1)
    sup = (np.abs(l - ema) / ema < 0.003) | (np.abs(l - s_lo) / s_lo < 0.002)
    res = (np.abs(h - ema) / ema < 0.003) | (np.abs(h - s_hi) / s_hi < 0.002)
    add("bar_reversal", sup & sb, 1, h, l - 0.1 * rng); add("bar_reversal", ~(sup & sb) & res & ss, -1, l, h + 0.1 * rng)
    # climactic_reversal (prev bar range > 2.5 x mean of bars i-18 .. i-2)
    clim = shift(rng, 1) > 2.5 * avg; green1 = shift(c, 1) > shift(o, 1)
    add("climactic_reversal", clim & (green1 == True) & ss, -1, l, h)
    add("climactic_reversal", clim & (green1 == False) & sb, 1, h, l)
    # first_pullback (prior structure bars i-13 .. i-7, recent i-6 .. i-1)
    ph, rh6 = rmax(h, -13, -7), rmax(h, -6, -1); pl, rl6 = rmin(l, -13, -7), rmin(l, -6, -1)
    add("first_pullback", (D == 1) & (rh6 > ph) & sb & (l > ph), 1, h, l)
    add("first_pullback", (D == -1) & (rl6 < pl) & ss & (h < pl), -1, l, h)
    # inside bars
    ii = (h < shift(h, 1)) & (l > shift(l, 1)); iii = ii & (shift(h, 1) < shift(h, 2)) & (shift(l, 1) > shift(l, 2))
    phi = np.where(iii, shift(h, 2), shift(h, 1)); plo = np.where(iii, shift(l, 2), shift(l, 1))
    for nm, m in (("ii_pattern", ii & ~iii), ("iii_pattern", iii)):
        add(nm, m & (D == 1), 1, phi, plo); add(nm, m & (D == -1), -1, plo, phi)
    X = pd.DataFrame(S, columns=["i", "setup", "side", "entry", "stop"])
    X["tf"] = tf; X["regime"] = reg[X.i]
    ok = ((X.regime.isin(["bull", "bear"]) & X.setup.isin(TREND | VOLAT)) | ((X.regime == "volatile") & X.setup.isin(VOLAT))
          | ((X.regime == "ranging") & X.setup.isin(RANGE | VOLAT)))
    X["regime_ok"] = ok & ~((X.regime == "volatile") & X.setup.isin(VOL_BLOCK))
    X["dist"] = (X.entry - X.stop) * X.side
    return X[X.dist > 0].reset_index(drop=True)


@njit(cache=True)
def sim(O, H, L, C, uh, um, start, entry, stop, side, mode, tick):
    """mode: 0 market at O[start], 1 stop order, 2 limit order. Returns fill flat index (-1 none), exit price, kind
    (0 stop, 1 target, 2 eod), fill price."""
    n = len(start); out = np.full((n, 5), np.nan)
    N = len(O)
    for t in range(n):
        s, e, sp, sd, md = start[t], entry[t], stop[t], side[t], mode[t]
        f = -1; fp = np.nan; j = s; lim = s + 120
        if md == 0:
            k = s
            while k < N and np.isnan(O[k]): k += 1
            if k >= N: continue
            f = k; fp = O[k]
        else:
            while j < N and j < lim:
                if np.isnan(O[j]):
                    j += 1; continue
                if uh[j] == 20 and um[j] >= 30: break
                if md == 1:
                    if (sd > 0 and H[j] >= e) or (sd < 0 and L[j] <= e):
                        f = j; fp = max(O[j], e) if sd > 0 else min(O[j], e); break
                else:
                    if (sd > 0 and L[j] <= e) or (sd < 0 and H[j] >= e):
                        f = j; fp = min(O[j], e) if sd > 0 else max(O[j], e); break
                if (sd > 0 and L[j] <= sp) or (sd < 0 and H[j] >= sp): break
                j += 1
            if f < 0: continue
        risk = abs(e - sp) if md != 0 else abs(e - sp)
        tp = (fp + sd * abs(fp - sp)) if md == 0 else (e + sd * abs(e - sp))
        k = f; xp = np.nan; kind = -1
        while k < N:
            if np.isnan(O[k]):
                k += 1; continue
            if (sd > 0 and L[k] <= sp) or (sd < 0 and H[k] >= sp):
                xp = min(O[k], sp) if sd > 0 else max(O[k], sp)
                if k == f: xp = sp
                kind = 0; break
            if (sd > 0 and H[k] >= tp) or (sd < 0 and L[k] <= tp):
                xp = tp if k > f else tp; kind = 1; break
            if uh[k] == 20 and um[k] >= 30:
                xp = C[k]; kind = 2; break
            if uh[k] > 20 or uh[k] < 0:
                xp = C[k]; kind = 2; break
            k += 1
        out[t, 0] = f; out[t, 1] = xp; out[t, 2] = kind; out[t, 3] = fp; out[t, 4] = k
    return out


def run_symbol(sym, n_rand=5, seed=1):
    g, O, H, L, C, uh, um, ts = load(sym); pv, tick, comm = SPEC[sym][1:]
    H1 = bars(O, H, L, C, 60); e1 = pd.Series(H1["c"]).ewm(span=20, adjust=False).mean().to_numpy()
    d1 = direction(H1, e1)
    rows = []
    for tf, k in (("5m", 5), ("15m", 15)):
        B = bars(O, H, L, C, k)
        idx1h = np.searchsorted(H1["end"], B["end"], side="right") - 1        # last closed 1h bar at that moment
        X = detect(B, np.where(idx1h >= 0, d1[np.clip(idx1h, 0, None)], 0), tf)
        X = X[X.i < len(B["c"]) - 1].reset_index(drop=True)
        X["start"] = B["end"][X.i] + 1                                        # first minute of the forming bar
        cur = O[np.clip(X.start.to_numpy(), 0, len(O) - 1)]
        X["mode"] = np.where(np.abs(X.entry - cur) <= tick, 0, np.where((X.entry - cur) * X.side > 0, 1, 2))
        X.loc[X["mode"] == 0, "entry"] = cur[X["mode"] == 0]
        rows.append(X)
    X = pd.concat(rows, ignore_index=True)
    X["t"] = ts[X.start.to_numpy()]; X["uh"] = uh[X.start.to_numpy()]
    X = X[(X.t >= "2018-01-01") & (X.uh >= 0)].reset_index(drop=True)
    out = sim(O, H, L, C, uh, um, X.start.to_numpy(np.int64), X.entry.to_numpy(float), X.stop.to_numpy(float),
              X.side.to_numpy(np.int64), X["mode"].to_numpy(np.int64), tick)
    X["fill"], X["exit"], X["kind"], X["fp"], X["xk"] = out.T
    X = X[X.fill >= 0].reset_index(drop=True)
    slips = (X["mode"] != 2).astype(int) + (X.kind != 1).astype(int)
    X["dist_d"] = (X.entry - X.stop).abs() * pv
    X["net"] = (X.exit - X.fp) * X.side * pv - comm - slips * tick * pv
    X = X[(X.dist_d >= tick * pv) & ((X.fp - X.stop) * X.side > 0)].reset_index(drop=True)      # a stop on the wrong side is rejected
    X["R"] = X.net / X.dist_d
    X["R_gross"] = (X.exit - X.fp) * X.side * pv / X.dist_d
    # matched random baseline: same side, year, UTC hour, stop distance as % of price, market entry
    rng_ = np.random.default_rng(seed)
    valid = np.where(~np.isnan(O) & (uh >= 0))[0]; vt = ts[valid]; vy = np.asarray(vt.year); vh = uh[valid]
    key = vy * 100 + vh; order = np.argsort(key, kind="stable"); ks = key[order]
    tk = np.asarray(X.t.dt.year) * 100 + X.uh.to_numpy()
    lo, hi = np.searchsorted(ks, tk, "left"), np.searchsorted(ks, tk, "right")
    pick = valid[order[np.minimum(lo[:, None] + (rng_.random((len(X), n_rand)) * np.maximum(hi - lo, 1)[:, None]).astype(int), len(order) - 1)]]
    st = pick.ravel(); px = O[st]; frac = (X.dist_d / pv / X.fp).to_numpy().repeat(n_rand); sd = X.side.to_numpy().repeat(n_rand)
    o2 = sim(O, H, L, C, uh, um, st.astype(np.int64), px, px - sd * frac * px, sd.astype(np.int64), np.zeros(len(st), np.int64), tick)
    net2 = (o2[:, 1] - o2[:, 3]) * sd * pv - comm - (1 + (o2[:, 2] != 1)) * tick * pv
    R2 = net2 / (frac * px * pv)
    R2[~np.isfinite(R2)] = np.nan
    X["R_rand"] = pd.Series(R2).groupby(np.arange(len(R2)) // n_rand).mean().to_numpy()
    X["sym"] = sym
    X["book"] = (~X.apply(lambda r: (r.tf, r.setup) in DISABLED, axis=1)) & X.regime_ok & \
                ~X.uh.isin(list(BLOCK_H | {20})) & X.apply(lambda r: LOCK.get(r.setup, r.side) == r.side, axis=1)
    return X


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def summary(X, by):
    G = X.groupby(by)
    return pd.DataFrame(dict(n=G.R.size(), win=G.R.apply(lambda r: (r > 0).mean()).round(3), R_gross=G.R_gross.mean().round(3),
                             R=G.R.mean().round(3), t=G.R.apply(tst).round(1),
                             R_rand=G.R_rand.mean().round(3), edge=G.apply(lambda d: (d.R - d.R_rand).mean()).round(3),
                             t_edge=G.apply(lambda d: tst(d.R - d.R_rand)).round(1)))


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    X = pd.concat([run_symbol(s) for s in ("NQ", "YM")], ignore_index=True)
    X.to_csv(SP + "brooks_bot_trades.csv", index=False)
    pd.set_option("display.width", 250)
    print(f"\n1. All filled signals, 2018-2026: {len(X):,} trades; 'failed_bo' never fires as coded (its swing window holds the bar it tests).")
    print(summary(X, ["setup", "tf", "side"]).to_string())
    B = X[X.book]
    print(f"\n2. The surviving book (the bot's disable list, direction locks, regime sets, blocked hours): {len(B):,} trades")
    print(summary(B, ["sym", "side"]).to_string()); print(summary(B, ["setup", "tf", "side"]).to_string())
    tot = summary(B.assign(all="book"), ["all"]); print(tot.to_string())
    # the bot's position caps: max 2 open per symbol, 3 Brooks positions in all; signals taken in time order
    B2 = B.sort_values("fill"); keep = []; open_ = []
    for idx, r in zip(B2.index, B2[["sym", "fill", "xk"]].itertuples(index=False)):
        open_ = [(s_, x_) for s_, x_ in open_ if x_ >= r.fill]
        if len(open_) >= 3 or sum(1 for s_, _ in open_ if s_ == r.sym) >= 2: continue
        open_.append((r.sym, r.xk)); keep.append(idx)
    C2 = B.loc[keep]
    print(f"\n   with the position caps (2 per symbol, 3 in all): {len(C2):,} trades ({len(C2) / 8.8:,.0f} a year)")
    print(summary(C2.assign(all="capped book"), ["all"]).to_string()); print(summary(C2, ["sym", "side"]).to_string())
    print(summary(C2.assign(y=C2.t.dt.year), ["y"]).to_string())
    X["capped"] = X.index.isin(keep)
    print("   exit mix, book vs capped:", B.kind.value_counts(normalize=True).round(2).to_dict(), C2.kind.value_counts(normalize=True).round(2).to_dict(),
          "| stop distance $ median", round(B.dist_d.median()), round(C2.dist_d.median()))
    print("\n   by year (book):"); print(summary(B.assign(y=B.t.dt.year), ["y"]).to_string())
    print("\n   by entry type (0 market, 1 stop, 2 limit = pull-back fill):"); print(summary(B, ["mode"]).to_string())
    aw, al = B.R[B.R > 0].mean(), -B.R[B.R < 0].mean()
    print(f"\n   avg win {aw:.2f}R, avg loss {al:.2f}R after costs -> break-even win rate {al / (aw + al):.1%}; actual {(B.R > 0).mean():.1%}")
    # key levels (score factor 7): within 0.2% of the session open, prior session high / low, last-5-sessions high / low
    print("\n3. Key-level tag (the bot's strongest finding, z = -5.06):")
    for sym in ("NQ", "YM"):
        g = pickle.load(open(SP + SPEC[sym][0] + ".pkl", "rb"))
        tr = g.trading; o, h, l = g.o, g.h, g.l
        sess = []
        for r in tr:                                                          # session = prior 17:00 CT -> 16:00 CT
            hi_ = np.nanmax(np.r_[h[r - 1, 1020:], h[r, :960]]); lo_ = np.nanmin(np.r_[l[r - 1, 1020:], l[r, :960]])
            op = o[r - 1, 1020:][~np.isnan(o[r - 1, 1020:])]; sess.append((pd.Timestamp(g.ts[r]), op[0] if len(op) else np.nan, hi_, lo_))
        S = pd.DataFrame(sess, columns=["d", "op", "hi", "lo"]).set_index("d")
        S["yh"], S["yl"] = S.hi.shift(1), S.lo.shift(1); S["wh"], S["wl"] = S.hi.shift(1).rolling(6).max(), S.lo.shift(1).rolling(6).min()
        m = (B.sym == sym); t = B.loc[m, "t"]
        sd = t.dt.normalize() + pd.to_timedelta((t.dt.hour >= 17).astype(int), unit="D")
        lv = S.reindex(sd.values)[["op", "yh", "yl", "wh", "wl"]].to_numpy()
        e = B.loc[m, "entry"].to_numpy()[:, None]
        X.loc[B.index[m], "key"] = (np.abs(e - lv) / lv < 0.002).any(1)
    B = X[X.book]
    print(summary(B.assign(key=B.key.fillna(False)), ["key", "side"]).to_string())
    print(f"\n   share of book trades on Mon / Tue: {B.t.dt.dayofweek.isin([0, 1]).mean():.0%}")
