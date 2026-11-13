"""VB watch rule (user 2026-11-12; WATCHLIST #41). Run in the Friday review after a data refresh:
  tools/run_stamped.sh analysis/vb_watch.py > analysis/outputs/vb_watch_output.txt
Status from VB v1 (rebuild, MC-validated) on the latest data, per 1 NQ, R = net / $1,500 (the 75-point stop):
  Y   trailing 250-trade avg R (about one year of signals) and its t
  DD  drawdown from the equity peak ($ per NQ) vs the 2018-24 worst (-$15,802)
Rules (calibrated on 2018-24 history, printed below; breakout_regime_test.py: a short cold streak does NOT predict the next
trades, VB averaged $108 a trade after cold 60-signal stretches, so the rule watches a YEAR, not a streak):
  RETIRE  Y below the 2018-24 minimum of Y  OR  DD beyond 1.5 x the 2018-24 worst: new territory -> drop from all plans (user decides).
  RETURN  (eligible for the evaluation again) Y >= the 2018-24 25th percentile of Y AND DD shallower than the 2018-24 worst
          AND a 150K bench (bench150 LIVE_EVAL + VB) shows a gain. Never on a streak alone.
  else    WATCH (out of the evaluation, as now).
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24
import vault_break_v8_test as V
print(__doc__.split("\n")[0])
g = Grid24(); T = V.run(g, "v1"); T["R"] = T.net / 1500.0; T["yr"] = T.date.dt.year
Y = T.R.rolling(250).mean(); Yt = T.R.rolling(250).apply(lambda x: x.mean() / x.std() * np.sqrt(len(x)), raw=True)
eq = T.net.cumsum(); dd = eq - eq.cummax()
h = T.yr <= 2024; ymin, y25, ddw = Y[h].min(), Y[h].quantile(0.25), dd[h].min()
print(f"data to {pd.Timestamp(g.ts[g.trading[-1]]).date()}; {len(T)} trades")
print(f"2018-24 calibration: trailing-250 avg R min {ymin:+.3f}, 25th pct {y25:+.3f}, median {Y[h].median():+.3f}; worst DD ${ddw:,.0f}")
y, yt, d_ = Y.iloc[-1], Yt.iloc[-1], dd.iloc[-1]
print(f"NOW ({T.date.iloc[-1].date()}): trailing-250 avg R {y:+.3f} (t {yt:.1f}), DD ${d_:,.0f}")
for k in (60, 120): print(f"   trailing {k}: avg R {T.R.iloc[-k:].mean():+.3f}")
state = "RETIRE (new territory: user decides)" if (y < ymin or d_ < 1.5 * ddw) else \
        "RETURN-ELIGIBLE (needs a 150K bench gain first)" if (y >= y25 and d_ > ddw) else "WATCH (stay out of the evaluation)"
print(f"STATE: {state}")
print("trailing-250 avg R at each year end: " + " ".join(f"{yy % 100:02d}:{Y[T.yr == yy].iloc[-1]:+.3f}" for yy in sorted(T.yr.unique()) if Y[T.yr == yy].notna().any()))
