"""Kusho / C03 with roll-adjusted indicators (registered 2026-10-23 in agents/cross_review/2026-10-23_claude_response.md before
running; Codex's cross-review finding 2). Same rules, costs and fills as analysis/kusho_test.py; only the indicator inputs
change. Compares signals (entry bars) and results with the unadjusted run.
  python3 analysis/kusho_roll_adjusted_replay.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import kusho_test as K

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); D0 = K.Data(g, adjust=False); D1 = K.Data(g, adjust=True)
    print(f"contract switches adjusted: {len(D1.rolls)}; bars whose indicators differ: EMA {np.mean(np.abs(D1.ema + D1.cum - D0.ema) > 0.25):.1%}, "
          f"ATR {np.nanmean(np.abs(D1.atr - D0.atr) > 0.25):.1%}, DOWN days {np.mean(D1.down != D0.down):.1%}")
    for mode, kw in (("FAR", {}), ("v9", {}), ("v9 flat 15:45", dict(flat_rth=True)), ("C03", {})):
        m = mode.split()[0]
        a, b = K.run(D0, m, "ours", **kw), K.run(D1, m, "ours", **kw)
        ka, kb = set(zip(a.date, a.fm)), set(zip(b.date, b.fm))
        print(f"\n{mode}: entries unadjusted {len(a)}, adjusted {len(b)}, same entry minute {len(ka & kb)} "
              f"({len(ka & kb) / max(len(ka), 1):.1%}); net per NQ ${a.net.sum():,.0f} -> ${b.net.sum():,.0f}")
        print(K.line(a, f"{mode} unadjusted")); print(K.line(b, f"{mode} roll-adjusted"))
        if (b.side < 0).any(): print(K.line(b[b.side > 0], "  longs (adjusted)")); print(K.line(b[b.side < 0], "  shorts (adjusted)"))
