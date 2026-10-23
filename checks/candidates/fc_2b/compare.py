"""Compare trade lists by entry date: python3 compare.py A.csv B.csv [from_date]"""
import sys, pandas as pd, numpy as np
a = pd.read_csv(sys.argv[1], parse_dates=["date"]); b = pd.read_csv(sys.argv[2], parse_dates=["date"])
f = sys.argv[3] if len(sys.argv) > 3 else "2018-01-01"
a = a[a.date >= f]; b = b[b.date >= f]
m = a.merge(b, on="date", how="outer", suffixes=("_a", "_b"), indicator=True)
both = m[m._merge == "both"]
print(f"A {len(a)}  B {len(b)}  same date {len(both)}  only A {sum(m._merge=='left_only')}  only B {sum(m._merge=='right_only')}")
print(f"  date match: {len(both)/len(m):.1%} of union;  same side {np.mean(both.side_a==both.side_b):.1%}")
if "entry_a" in both and "entry_b" in both:
    print(f"  entry equal {np.mean(np.isclose(both.entry_a, both.entry_b)):.1%};  exit equal {np.mean(np.isclose(both.exit_a, both.exit_b)):.1%};"
          f"  net equal (+-$1) {np.mean(np.abs(both.net_a-both.net_b)<1):.1%};  corr net {np.corrcoef(both.net_a, both.net_b)[0,1]:.3f}")
print(f"  net A ${a.net.sum():,.0f} (avg {a.net.mean():.1f})  B ${b.net.sum():,.0f} (avg {b.net.mean():.1f});  common: A ${both.net_a.sum():,.0f} B ${both.net_b.sum():,.0f}")
print(f"  only-A net ${m[m._merge=='left_only'].net_a.sum():,.0f} (avg {m[m._merge=='left_only'].net_a.mean():.1f}); only-B net ${m[m._merge=='right_only'].net_b.sum():,.0f} (avg {m[m._merge=='right_only'].net_b.mean():.1f})")
m.to_csv(sys.argv[4] if len(sys.argv) > 4 else "/dev/null", index=False)
