"""Checker placebo for the longs-only (and both-sides) replica.

Placebo B (time-matched random day): every replica trade is moved to a random trading day in the SAME calendar year with
the same side, the same entry clock time (open of the fill bar) and the same latest exit clock time; stop 50 / target 25
are active on the 1-minute path (stop first), otherwise exit at market at the real trade's exit clock time. Same costs.
This keeps count, year (drift regime), time of day and holding time; only the signal's choice of day/moment is removed.

Placebo A (in-rule random entry): replica.run() with the entry condition replaced by a coin flip while flat (all exits
exactly as the rule, incl. the band/EMA exit). Reported, not written.

usage: python3 placebo.py <replica csv> <out csv> [runs]
"""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replica as R


def placebo_b(T, runs=200, seed=7, stop_pts=50.0, tgt_pts=25.0):
    G = R.load(); g, rows = G["g"], G["rows"]
    T = T.copy()
    et = pd.to_datetime(T.entry_time); xt = pd.to_datetime(T.exit_time)
    cE = (et.dt.hour * 60 + et.dt.minute - 14).to_numpy()            # first minute column of the fill bar
    mkt = ~T.kind.isin(["stop", "target"]).to_numpy()
    cX = np.where(mkt, xt.dt.hour * 60 + xt.dt.minute - 14, xt.dt.hour * 60 + xt.dt.minute + 1)
    side = T.side.to_numpy(); yr = et.dt.year.to_numpy()
    ry = pd.DatetimeIndex(g.ts[rows]).year.to_numpy()
    byyr = {y: rows[ry == y] for y in set(yr)}
    rng = np.random.default_rng(seed); out = []
    for run in range(runs):
        for i in range(len(T)):
            for _ in range(20):
                r = rng.choice(byyr[yr[i]])
                if not np.isnan(g.o[r, cE[i]]) and not np.isnan(g.o[r, min(cX[i], 1439)]):
                    break
            else:
                continue
            sd = side[i]; ent = g.o[r, cE[i]] + R.TICK * sd
            stop = ent - stop_pts * sd; tgt = ent + tgt_pts * sd; xp = None
            for j in range(cE[i], cX[i]):
                mo, mh, ml = g.o[r, j], g.h[r, j], g.l[r, j]
                if np.isnan(mo): continue
                if sd == 1:
                    if ml <= stop: xp = min(stop, mo) - R.TICK; break
                    if mh >= tgt: xp = tgt; break
                else:
                    if mh >= stop: xp = max(stop, mo) + R.TICK; break
                    if ml <= tgt: xp = tgt; break
            if xp is None:
                j = cX[i]
                while np.isnan(g.o[r, j]): j -= 1
                xp = g.o[r, j] - R.TICK * sd
            out.append((run, (xp - ent) * sd * R.PV - R.COMM))
    return pd.DataFrame(out, columns=["run", "net"])


def placebo_a(n_runs=20, p=0.08, short_on=False):
    """Coin-flip entries inside the rule (monkeypatched comparison)."""
    res = []
    for k in range(n_runs):
        rng = np.random.default_rng(100 + k)
        T = R.run(short_on=short_on, random_entry=(rng, p))
        T = T[T.date >= "2018-01-01"]; res.append((k, len(T), T.net.mean()))
    return pd.DataFrame(res, columns=["run", "n", "mean"])


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]; runs = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    T = pd.read_csv(src)
    P = placebo_b(T, runs)
    P.to_csv(dst, index=False)
    pm = P.groupby("run").net.mean()
    print(f"real mean {T.net.mean():.1f} n {len(T)}; placebo B {runs} runs mean {pm.mean():.1f} sd {pm.std():.1f} "
          f"max {pm.max():.1f}; share >= real {np.mean(pm >= T.net.mean()):.3f}")
