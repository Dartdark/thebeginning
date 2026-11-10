"""Oil intraday lead (user 2026-11-10 'what about the oil intraday lead'; Codex ssrn_five: Alturki & Kurov, SSRN 3747330). PRE-REGISTERED
(header committed before the first run). The paper's signal (API actual - Bloomberg EIA consensus) needs data we do not own; its
Table 2 price version is testable: the post-API 30-minute CL return predicts the return in the hour before EIA (slope 0.17).
API: 15:30 CT the day before each EIA release (EIA days as analysis/satellite_cushing_test.releases: Wed 9:30 CT, Thu in holiday
weeks, 2 delayed weeks dropped). Signal = CL 15:29 -> 15:59 CT close move after API. Trade on the EIA day: FOLLOW its sign, in at the
08:29 close (EIA - 61 min), out at the 09:29 close; 1 CL, $7.25 + 1 tick per fill ($27.25 a round trip); 2018-26.
ITEMS (bar t_threshold(2), positive 2018-22 and 2023+): P1 every event; P2 extreme events only, |signal| above the 80th percentile
of the previous 52 events (past-only). Context: entries at EIA - 90 / - 120 min; the fade side; the same rule on non-API days
(Mon/Thu 15:29 -> 15:59 move -> next day 08:29 -> 09:29).
  tools/run_stamped.sh analysis/api_pre_eia_test.py > analysis/outputs/api_pre_eia_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from metrics import t_threshold
from cl_forced_flows_test import load, line, PV, COST
from satellite_cushing_test import releases

if __name__ == "__main__":
    print(__doc__.split("\n")[0]); bar = t_threshold(2); print(f"   items 2, bar t >= {bar:.2f}")
    cl = load("CL"); cf = pd.Series(cl.c.ravel()).ffill().to_numpy(); ts0 = pd.Timestamp(cl.ts[0])
    px = lambda d, hm: cf[int((d - ts0).days) * 1440 + jof(hm)]
    rows = cl.trading[pd.DatetimeIndex(cl.ts[cl.trading]) >= pd.Timestamp("2018-01-01")]; idx = pd.DatetimeIndex(cl.ts[rows])
    def build(days):
        R = []
        for d in days:
            a = d - pd.Timedelta(days=1); sig = px(a, 1559) - px(a, 1529)
            R.append(dict(date=d, sig=sig, **{f"m{k}": px(d, 929) - px(d, h) for k, h in ((60, 829), (90, 759), (120, 729))}))
        T = pd.DataFrame(R).set_index("date").dropna(); return T[T.sig != 0]
    T = build(releases(idx)); s = np.sign(T.sig)
    thr = T.sig.abs().rolling(52, min_periods=26).quantile(0.8).shift(1); ext = T.sig.abs() > thr
    print(f"   EIA events {len(T)}; corr(post-API 30 min, EIA-60 -> EIA-1) {T.sig.corr(T.m60):+.3f}; extreme events {int(ext.sum())}")
    p1 = s * T.m60 * PV - COST; p2 = p1[ext]
    for x, nm in ((p1, "ITEM P1 follow, every event, 08:29 -> 09:29"), (p2, "ITEM P2 follow, extreme events only")):
        y = x.index.year; ok = x.mean() / x.std() * np.sqrt(len(x)) >= bar and x[y < 2023].mean() > 0 and x[y >= 2023].mean() > 0
        print(line(x, nm) + ("  PASS" if ok else "  fail"))
    print("   context:")
    print(line(s * T.m60 * PV, "gross, every event")); print(line((s * T.m60 * PV)[ext], "gross, extreme"))
    for k in (90, 120): print(line(s * T[f"m{k}"] * PV - COST, f"follow, in EIA-{k}")); print(line((s * T[f"m{k}"] * PV - COST)[ext], f"follow, in EIA-{k}, extreme"))
    print(line(-s * T.m60 * PV - COST, "fade, every event"))
    other = idx[idx.dayofweek.isin([1, 4]) & ~idx.isin(T.index)]          # Tue / Fri: the move the day before is Mon / Thu (no API)
    C = build(other); print(line(np.sign(C.sig) * C.m60 * PV - COST, "control: same rule on non-API days"))
