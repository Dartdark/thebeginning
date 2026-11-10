"""Two more macro angles (user 2026-11-10: 'run both'). PRE-REGISTERED (header committed before the first run; 8 items, bar
t_threshold(8)). Robust surprise z as analysis/macro_followups.py (MAD scale), BIG = |z| >= 1.
1 First 15 minutes: on BIG-surprise days of INFLATION / JOBS / CLAIMS / RETAIL / GDP (07:30 CT releases), follow the 07:30 bar's
  move (close - open) at the 07:31 open, out at the 07:45 close, stop 0.5 x ATR15; costs $7.25 + 3 ticks per fill (fast market:
  2 extra ticks). 5 items.
2 NFP Fade with surprise filters (NFP Fade = analysis/ingredient_ablation4 nfp(): first-10-day Friday, 07:31-07:35 range > 3x its
  median, fade the 07:30 -> 07:45 move at 07:46, stop 0.5 ATR, out 09:00): (a) only BIG payroll surprises, (b) only when the
  reaction AGREES with the payroll surprise sign, (c) only when it DISAGREES. 3 items vs the unfiltered fade; random-skip placebo.
  tools/run_stamped.sh analysis/macro_angles2.py > analysis/outputs/macro_angles2_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from metrics import t_threshold
from ingredient_ablation3 import line
import ingredient_ablation4 as IA4
from macro_followups import events

if __name__ == "__main__":
    print(__doc__.split("\n")[0]); print(f"   bar t >= {t_threshold(8):.2f}")
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); ts = pd.DatetimeIndex(g.ts); pos = pd.Series(np.arange(len(ts)), index=ts)
    E = events(True)
    print("\n1. First 15 minutes, follow the 07:30 bar on big-surprise days (3 ticks per fill):")
    for grp in ("INFLATION", "JOBS", "CLAIMS", "RETAIL", "GDP"):
        days = E[(E.group == grp) & (E.hm == 730) & (E.z.abs() >= 1)].day; rows = []
        for d in days:
            if d not in pos.index: continue
            r = int(pos[d]); o, c = g.o[r, jof(730)], g.c[r, jof(730)]
            if not (np.isfinite(o) and np.isfinite(c)) or o == c or np.isnan(atr[r]): continue
            s = int(np.sign(c - o)); IA4.COMM = 7.25 + 2 * 2 * 0.25 * 20
            x = IA4.walk(g, r * 1440 + jof(731), r * 1440 + jof(745), s, 0.5 * atr[r], 20.0, 0.25)
            if x is not None: rows.append((d, s, x))
        T = pd.DataFrame(rows, columns=["date", "side", "net"]); print(line(T.net, T.date, f"ITEM {grp} ({len(T)} days)"))
    print("\n2. NFP Fade with surprise filters:")
    IA4.COMM = 7.25
    src = open("analysis/ingredient_ablation4.py").read()
    rng_ = g.h[:, jof(731):jof(735) + 1].max(1) - g.l[:, jof(731):jof(735) + 1].min(1)
    wk = [r for r in range(g.D) if ts[r].dayofweek < 5 and np.isfinite(rng_[r])]; med = {}
    for i, r in enumerate(wk):
        if i >= 20: med[r] = np.median([rng_[q] for q in wk[i - 20:i]])
    cand = [r for r in med if ts[r] >= pd.Timestamp("2018-01-01") and ts[r].dayofweek == 4 and ts[r].day <= 10]
    pz = E[E.group == "JOBS"].set_index("day").z
    M = pd.read_csv("data/codex_20261109/macro_events_2018plus.csv", parse_dates=["time"]).dropna(subset=["actual"]); M = M[M.series == "PAYEMS"]
    M["day"] = pd.DatetimeIndex(M.time.dt.tz_convert("America/Chicago").dt.date); M["s"] = M.actual - M.forecast
    sz = M.set_index("day").s / (1.4826 * (M.s - M.s.median()).abs().median())
    rows = []
    for r in cand:
        if not rng_[r] > 3 * med[r]: continue
        ref, rc = g.c[r, jof(730)], g.c[r, jof(745)]
        if not (np.isfinite(ref) and np.isfinite(rc)) or rc == ref or np.isnan(atr[r]): continue
        side = int(-np.sign(rc - ref)); x = IA4.walk(g, r * 1440 + jof(745) + 1, r * 1440 + jof(900), side, 0.5 * atr[r], 20.0, 0.25)
        if x is None: continue
        z = sz.get(ts[r], np.nan); rows.append((ts[r], side, x, z, int(np.sign(rc - ref))))
    T = pd.DataFrame(rows, columns=["date", "side", "net", "z", "react"]); print(line(T.net, T.date, "NFP Fade as is (spike days)"))
    print(f"      payroll surprise known on {T.z.notna().sum()} of {len(T)} days")
    tt = lambda v: v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan
    for nm, m in (("ITEM (a) only big payroll surprises", T.z.abs() >= 1), ("ITEM (b) reaction agrees with the surprise", np.sign(T.z) == T.react),
                  ("ITEM (c) reaction disagrees with the surprise", np.sign(T.z) == -T.react)):
        k = T[m.fillna(False).values]; print(line(k.net, k.date, nm))
        rng = np.random.default_rng(3); pm = [T.net.values[rng.choice(len(T), len(k), replace=False)].mean() for _ in range(1000)] if len(k) else [0]
        print(f"      random keep same count: 95th ${np.percentile(pm, 95):.0f}; kept ${k.net.mean():.0f}; p {np.mean(np.array(pm) >= k.net.mean()):.3f}")
