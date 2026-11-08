"""Noise-area 15-min longs, RTH-anchored on the 24h chart: effect of the early-close flat (2026-11-05, before live).
Early-close days (replica.is_early_close): no entry after 11:00, flat at the 11:30 bar (fills ~11:31, before the 12:00/12:15 halt).
  tools/run_stamped.sh analysis/bridge_noise_15m_earlyclose.py > analysis/outputs/bridge_noise_15m_earlyclose_output.txt
"""
import sys; sys.path.insert(0, "analysis")
import bridge_noise_15m_test as B
from replica import is_early_close
S = B.series("24h")
for nm, kw in (("as now (no early-close rule)", {}), ("early-close flat 11:30", dict(early_flat=True))):
    T = B.run(S, shorts=False, anchor=(845, 1500), **kw); T = T[T.date >= "2018"]
    print(B.line(T, nm))
    ec = T[T.date.map(is_early_close)]
    print(f"      early-close-day trades {len(ec)}, net ${ec.net.sum():.0f}; held past session: {T.attrs.get('flagged', 'n/a')};",
          "exits:", ec.kind.value_counts().to_dict())
    print("      by year $:", T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict())
