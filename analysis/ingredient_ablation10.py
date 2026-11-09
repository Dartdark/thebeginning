"""Ingredient ablation, round 10 (user 2026-11-09: 'second batch'): Kusho v9, S47 v2, FC 2B, the personal-book pieces still on their
forward logs. PRE-REGISTERED (header committed before the first run). Information only; ONE part changed at a time; per NQ after
$7.25 + 1 tick per market / stop fill (rebuilds' own conventions); 2018-26, both periods, total $ and max DD
(ingredient_ablation3.line). Side splits are information, not ablations. A variant beating its current version on t AND in both
periods gets the two-bar book check in a follow-up.
  1. Kusho v9 (analysis/kusho_test.py, 'ours' fills): 15-min bar 09:00-13:45 closing up, above EMA50, small lower wick -> buy limit
     at its open (mirrored shorts on DOWN days), fractal swing stop / 3R target / break-even, out after 21:00 (holds overnight and
     weekends). Variants: longs only (FAR) / no wick filter / no EMA filter / flat by 15:45 (no overnight or weekend hold) /
     random entries at the same rate (placebo, 1 seed) / split: longs vs shorts of v9.
  2. S47 v2 (analysis/s47_test.py): London-open impulse (EU-15 -> EU+30 min) / overnight ATR > 0.0625, confirmed by the 09:30 move
     -> 09:31 entry, stop 0.5 ATR_ON, out 15:00. Variants: v1 (no 09:30 confirmation) / New York only (no London signal, Codex's
     control) / threshold 0 / 0.125 / stop 0.25 / 1.0 / no stop / fade instead / split: longs vs shorts.
  3. FC 2B (analysis/fc_2b_test.py = v1 rebuild; v2's 11:30 holiday flatten and entry-bar stop are not in it): 08:31-09:00 opening
     drive with a volume-weighted flow z >= 1 in the same direction -> 09:01 entry, stop 100 / trail 150 / break-even at +66,
     out 14:59. Variants: no flow filter (every drive day) / z >= 0.5 / z >= 1.5 / opposite side / no trail / no break-even /
     stop 50 / stop 150 / split: longs vs shorts.
  tools/run_stamped.sh analysis/ingredient_ablation10.py > analysis/outputs/ingredient_ablation10_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from ingredient_ablation3 import line
import kusho_test as KU
import s47_test as S4
import fc_2b_test as FC

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sh = lambda nm, T: print(line(T.net, T.date, nm), flush=True)
    g = pickle.load(open("scratch_data/g24.pkl", "rb"))
    # ---------------- 1. Kusho v9
    print("\n1. Kusho v9:")
    D = KU.Data(g); base = KU.run(D, mode="v9"); sh("as is (v9)", base)
    sh("split: v9 longs", base[base.side > 0]); sh("split: v9 shorts (DOWN days)", base[base.side < 0])
    sh("longs only (FAR, no shorts)", KU.run(D, mode="FAR"))
    sh("no wick filter", KU.run(D, mode="v9", wick_on=False)); sh("no EMA filter", KU.run(D, mode="v9", ema_on=False))
    sh("flat by 15:45 (no overnight / weekend hold)", KU.run(D, mode="v9", flat_rth=True))
    rate = len(base) / max(1, int(((D.hhmm >= 900) & (D.hhmm <= 1345)).sum() * 8.8 / 9.0))
    sh(f"random entries, same rate (p {rate:.3f})", KU.run(D, mode="v9", rand_p=rate))
    # ---------------- 2. S47 v2
    print("\n2. S47 v2:")
    T = S4.build(g); b = S4.run(g, T); sh("as is (v2)", b)
    sh("split: longs", b[b.side > 0]); sh("split: shorts", b[b.side < 0])
    sh("v1 (no 09:30 confirmation)", S4.run(g, T, v2=False)); sh("New York only (no London signal)", S4.run(g, T, ny_only=True))
    sh("threshold 0", S4.run(g, T, thr=0.0)); sh("threshold 0.125", S4.run(g, T, thr=0.125))
    sh("stop 0.25", S4.run(g, T, stop_atr=0.25)); sh("stop 1.0", S4.run(g, T, stop_atr=1.0)); sh("no stop", S4.run(g, T, stop_atr=99.0))
    sh("fade instead", S4.run(g, T, side_override=lambda i, s: -s))
    # ---------------- 3. FC 2B
    print("\n3. FC 2B (v1 rebuild):")
    days = FC.load(); sig = FC.signals(days); f0 = FC.run(days, sig); sh("as is", f0)
    sh("split: longs", f0[f0.side > 0]); sh("split: shorts", f0[f0.side < 0])
    sh("no flow filter (every drive day)", FC.run(days, sig.assign(side=sig.dir.where(sig.index >= 20, 0))))
    sh("z >= 0.5", FC.run(days, FC.signals(days, zmin=0.5))); sh("z >= 1.5", FC.run(days, FC.signals(days, zmin=1.5)))
    sh("opposite side", FC.run(days, sig.assign(side=-sig.side)))
    sh("no trail", FC.run(days, sig, trail=0)); sh("no break-even", FC.run(days, sig, be=0))
    sh("stop 50", FC.run(days, sig, sl=50.0)); sh("stop 150", FC.run(days, sig, sl=150.0))
