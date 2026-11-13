"""Pivot Continuation ingredient breakdown + data sweep (standing rule; POST HOC, after analysis/pivot_continuation_test.py found no
pass). One part changed at a time from the note's rules, on GC long (best port, t 2.04) and 6E short (closest market to 6J):
swing strength 2 / 5 (base 3); pivot candles 30 / 120 min (base 60); entry window all hours / 08:00-10:00 only (base 17:00-10:00);
exit 10:30 / 13:00 (base 15:30); 2x ATR(14) target on 15-min candles (range ATR); then the data sweep of the base trades.
  tools/run_stamped.sh analysis/pivot_ingredients.py > analysis/outputs/pivot_ingredients_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import pivot_continuation_test as P
from strategy_data_sweep import sweep

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for nm, side in (("GC", 1), ("6E", -1)):
        pk, pv, tick, comm = P.MK[nm]; F = P.Flat(pickle.load(open(P.SP + pk + ".pkl", "rb")))
        h15, l15, e15 = F.candles(15); atr = pd.Series(h15 - l15).ewm(alpha=1 / 14, adjust=False).mean().to_numpy()
        ix = np.searchsorted(e15, np.arange(F.N), side="right") - 1; atr15 = np.where(ix >= 13, atr[np.maximum(ix, 0)], np.nan)
        def go(k=60, s=3, **kw):
            h, l, end = F.candles(k); hi, lo = P.swings(h, l, end, s); T = P.run(F, side, hi, lo, pv, tick, comm, atr15=atr15, **kw)
            return T[T.entry >= "2018-01-01"]
        print(f"\n{nm} {'long' if side > 0 else 'short'}:")
        base = go(); print(P.show(base.net, base.entry, "BASE (note's rules)"))
        for lab, kw in (("swing strength 2", dict(s=2)), ("swing strength 5", dict(s=5)), ("pivot candles 30 min", dict(k=30)),
                        ("pivot candles 120 min", dict(k=120)), ("entries all hours", dict(win=(0, 1440))), ("entries 08:00-10:00 only", dict(win=(1441, 600))),
                        ("exit 10:30", dict(exit_hm=630)), ("exit 13:00", dict(exit_hm=780)), ("2x ATR target", dict(target_atr=2.0))):
            if lab == "entries 08:00-10:00 only":
                T = go(); T = T[(T.entry.dt.hour * 60 + T.entry.dt.minute).between(481, 600)]
            else: T = go(**kw)
            print(P.show(T.net, T.entry, lab), flush=True)
        print(); sweep(base.set_index("entry").net.groupby(lambda d: d.normalize()).sum(), f"{nm} pivot continuation")
