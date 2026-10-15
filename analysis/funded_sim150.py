"""Apex 150K EOD Performance Account: a copy of funded_sim.py with the 150K numbers (2026-10-15; user: $4,000 drawdown,
$2,000 DLL; payout ladder 2,400 / 2,400 / 3,100 / 3,900 / 3,900 / 4,800 = $20,500 and the $350 qualifying day ASSUMED from
2026 guides). Docstring below is the 50K original.

Apex 50K EOD Performance Account (funded phase): payouts on real days.

The goal in the funded phase is not passing but the money taken out: at most
6 payouts per account, capped at $1,500 / $1,500 / $2,000 / $2,500 / $2,500 /
$3,000 for the 50K, $13,000 in all. After the 6th payout the account closes.

Rules (Apex EOD Performance Account payouts page, 50K, as supplied; rechecked against the user's dashboard 2026-10-15):
  - payout request needs, since the last approved payout (or the start):
      * at least 5 trading days that each made at least $250 (net)
      * balance at least $52,600 (safety net $52,100 + $500 minimum payout)
      * 50% consistency: the best day / total profit since the last payout
        must be below 50% (losing days reduce the total)
  - a payout is at least $500 and at most the cap for its number, and it
    cannot take the balance below the safety net ($52,100)
Rules assumed from Apex's help center as quoted by third-party guides (the
help center itself is not reachable from here; confirmed by the user on 2026-10-13):
  - $2,000 drawdown trailing the end-of-day balance, locking at $50,100
    (start + $100, reached when the balance closes at $52,100); open equity
    at or below the threshold closes the account
  - daily loss limit by the previous close's profit level: under $3,000
    profit $1,000, $3,000-$5,999 $2,000, $6,000 and up $3,000; hitting it
    liquidates and ends the day (the account stays open)
  - contract cap 2 NQ (20 MNQ) under $1,500 profit, 3 NQ to $2,999, 4 NQ
    above; the sizes tested here stay at or under 20 MNQ
  - payouts are requested at the close of the day the conditions are met
    and come off the balance at once

A day is reduced to two numbers: the lowest open-equity P&L of the day
(`low`, from portfolio.paths' `worst`) and the closing P&L (`close`). With no
profit target in the funded phase, that is all the rules need: the day hits
the threshold or the daily loss limit if `low` reaches it, otherwise it
closes at `close`.

Payout policy: `keep` = dollars left above the safety net after a full-cap
payout. A payout is requested once the balance reaches safety net + cap +
keep (and the other conditions hold); `keep=None` requests as soon as $500
or more is allowed, taking what is there up to the cap.
"""
import numpy as np

try:
    from numba import njit
except ImportError:
    def njit(*a, **k):
        return (lambda f: f) if not (a and callable(a[0])) else a[0]

START = 150_000.0
MLL = 4_000.0
LOCK = 150_100.0
SAFETY = 154_100.0
MIN_PAYOUT = 500.0
MIN_DAY = 350.0
MIN_DAYS = 5
CAPS = np.array([2400.0, 2400.0, 3100.0, 3900.0, 3900.0, 4800.0])
FULL = CAPS.sum()


@njit(cache=True)
def _dll(bal):
    return 2000.0


@njit(cache=True)
def run_pa(low, close, s, horizon, keep, any_amount, consistency):
    """One Performance Account started on day s, for at most `horizon` days.
    Returns (total paid, payouts, days used, blown 0/1, days to first payout)."""
    D = len(low)
    bal = START; floor = START - MLL
    cyc_start = START; best = 0.0; qual = 0
    paid = 0.0; n = 0; first = -1
    end = min(D, s + horizon)
    for d in range(s, end):
        dll = _dll(bal)
        lim = max(floor, bal - dll)
        if bal + low[d] <= lim:
            if floor >= bal - dll:
                return paid, n, d - s + 1, 1, first
            pnl = -dll
        else:
            pnl = close[d]
        bal += pnl
        if pnl >= MIN_DAY:
            qual += 1
        if pnl > best:
            best = pnl
        if floor < LOCK:
            floor = max(floor, min(bal - MLL, LOCK))
        # payout at the close
        prof = bal - cyc_start
        room = bal - SAFETY
        cap = CAPS[n]
        if qual >= MIN_DAYS and room >= MIN_PAYOUT and prof > 0 and \
                (not consistency or best < 0.5 * prof):
            amt = 0.0
            if any_amount:
                amt = min(cap, room)
            elif room >= cap + keep:
                amt = cap
            if amt > 0:
                bal -= amt; paid += amt; n += 1
                if first < 0:
                    first = d - s + 1
                if n == 6:
                    return paid, n, d - s + 1, 0, first
                cyc_start = bal; best = 0.0; qual = 0
    return paid, n, end - s, 0, first


@njit(cache=True)
def run_all(low, close, starts, horizon, keep, any_amount, consistency):
    out = np.zeros((len(starts), 5))
    for i in range(len(starts)):
        a, b, c, e, f = run_pa(low, close, starts[i], horizon, keep, any_amount, consistency)
        out[i, 0] = a; out[i, 1] = b; out[i, 2] = c; out[i, 3] = e; out[i, 4] = f
    return out


def simulate(low, close, horizon=250, keep=0.0, any_amount=False, consistency=True, starts=None):
    """Start a Performance Account on every day in `starts` (default: every day
    with `horizon` days after it) and walk the real days. Returns a dict of
    per-start arrays: paid, payouts, days, blown, first (days to the first
    payout, -1 if none)."""
    low = np.ascontiguousarray(low, dtype=np.float64)
    close = np.ascontiguousarray(close, dtype=np.float64)
    if starts is None:
        starts = np.arange(max(1, len(low) - horizon))
    o = run_all(low, close, np.asarray(starts, dtype=np.int64), horizon,
                float(keep or 0.0), keep is None or any_amount, consistency)
    return dict(paid=o[:, 0], payouts=o[:, 1], days=o[:, 2], blown=o[:, 3], first=o[:, 4])


def summary(res):
    paid, n, days, blown = res["paid"], res["payouts"], res["days"], res["blown"]
    done = n == 6
    return dict(exp_paid=paid.mean(), full=done.mean(), blown=blown.mean(),
                payouts=n.mean(), med_days_full=np.median(days[done]) if done.any() else np.nan,
                paid_per_100d=(paid / days).mean() * 100, any_payout=(n > 0).mean())


# ---------- sizing that changes with the account (path-based) ----------

@njit(cache=True)
def run_pa_sized(W, C, base, s, horizon, keep, consistency, fmin, fmax, ref, stage):
    """Like run_pa, but each strategy k trades floor(base[k, d] x f) MNQ,
    where f = (balance - threshold) / ref, clipped to [fmin, fmax], set at
    each day's start. W[k] is strategy k's open-equity path per MNQ (days x
    minutes, worst case), C[k] its closing P&L per MNQ. fmin = fmax = 1
    gives fixed sizes. stage[n] multiplies all sizes while n payouts have
    been made (stage[n] = 1 for all n: the same sizes throughout)."""
    K, D, M = W.shape
    bal = START; floor = START - MLL
    cyc_start = START; best = 0.0; qual = 0
    paid = 0.0; n = 0; first = -1
    end = min(D, s + horizon)
    q = np.zeros(K)
    for d in range(s, end):
        f = (bal - floor) / ref
        f = min(max(f, fmin), fmax) * stage[n]
        any_q = False
        for k in range(K):
            q[k] = np.floor(base[k, d] * f + 1e-9)
            if q[k] > 0:
                any_q = True
        if not any_q:
            continue
        dll = _dll(bal)
        lim = max(floor, bal - dll)
        low = 0.0
        for j in range(M):
            x = 0.0
            for k in range(K):
                if q[k] > 0:
                    x += q[k] * W[k, d, j]
            if x < low:
                low = x
        if bal + low <= lim:
            if floor >= bal - dll:
                return paid, n, d - s + 1, 1, first
            pnl = -dll
        else:
            pnl = 0.0
            for k in range(K):
                pnl += q[k] * C[k, d]
        bal += pnl
        if pnl >= MIN_DAY:
            qual += 1
        if pnl > best:
            best = pnl
        if floor < LOCK:
            floor = max(floor, min(bal - MLL, LOCK))
        prof = bal - cyc_start
        room = bal - SAFETY
        cap = CAPS[n]
        if qual >= MIN_DAYS and room >= cap + keep and prof > 0 and \
                (not consistency or best < 0.5 * prof):
            bal -= cap; paid += cap; n += 1
            if first < 0:
                first = d - s + 1
            if n == 6:
                return paid, n, d - s + 1, 0, first
            cyc_start = bal; best = 0.0; qual = 0
    return paid, n, end - s, 0, first


@njit(cache=True)
def run_all_sized(W, C, base, starts, horizon, keep, consistency, fmin, fmax, ref, stage):
    out = np.zeros((len(starts), 5))
    for i in range(len(starts)):
        a, b, c, e, f = run_pa_sized(W, C, base, starts[i], horizon, keep, consistency, fmin, fmax, ref,
                                     stage)
        out[i, 0] = a; out[i, 1] = b; out[i, 2] = c; out[i, 3] = e; out[i, 4] = f
    return out


def simulate_sized(W, C, base, horizon=250, keep=0.0, consistency=True, fmin=1.0, fmax=1.0,
                   ref=2000.0, starts=None, stage=None):
    """Performance Accounts with per-strategy sizes `base` (K x days, MNQ at
    f = 1) scaled by the cushion above the threshold. See run_pa_sized."""
    D = W.shape[1]
    if starts is None:
        starts = np.arange(max(1, D - horizon))
    o = run_all_sized(W, C, np.ascontiguousarray(base, dtype=np.float64),
                      np.asarray(starts, dtype=np.int64), horizon, float(keep), consistency,
                      float(fmin), float(fmax), float(ref),
                      np.ones(6) if stage is None else np.asarray(stage, dtype=np.float64))
    return dict(paid=o[:, 0], payouts=o[:, 1], days=o[:, 2], blown=o[:, 3], first=o[:, 4])
