"""Checker replica of the NR7 flag, from spec.md only.
Session = 1-minute bars stamped 831..1500 CT (= the 30-min bars closing 9:00..15:00), weekdays with such bars.
NR7 day: range <= min(range of previous 6 sessions). The NEXT session is flagged.
Usage: python3 replica.py [variant]   variant in {base, incl830, to1515, strict}
"""
import sys, glob, numpy as np, pandas as pd
ROOT = "/home/user/thebeginning"
CDIR = ROOT + "/checks/candidates/vb_nr7_sizing"

def sessions(lo=831, hi=1500):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(ROOT + "/NQ_1min_20*.csv"))], ignore_index=True)
    d = d.drop_duplicates(["date", "time"])
    d = d[(d.time >= lo) & (d.time <= hi)]
    g = d.groupby("date").agg(h=("high", "max"), l=("low", "min"), n=("time", "size"), last=("time", "max"))
    g.index = pd.to_datetime(g.index.astype(str))
    g = g[g.index.dayofweek < 5]
    g["rng"] = g.h - g.l
    return g

def flags(g, strict=False):
    prev6 = g.rng.shift(1).rolling(6).min()
    nr7 = (g.rng < prev6) if strict else (g.rng <= prev6)
    return nr7.shift(1).fillna(False).astype(bool)   # flag on the next session

if __name__ == "__main__":
    var = sys.argv[1] if len(sys.argv) > 1 else "base"
    lo, hi = (830, 1500) if var == "incl830" else (831, 1515) if var == "to1515" else (831, 1500)
    g = sessions(lo, hi); f = flags(g, strict=(var == "strict"))
    T = pd.read_csv(CDIR + "/trades.csv", parse_dates=["date"])
    T["rep"] = T.date.map(f).fillna(False).astype(int)
    days = T.drop_duplicates("date")
    agree = (days.rep == days.flagged).mean()
    print(f"[{var}] sessions {len(g)}, flagged sessions {int(f.sum())}; trade-days {len(days)}, day agreement {agree:.4f}; "
          f"trade agreement {(T.rep == T.flagged).mean():.4f}")
    print("  maker-only flagged days:", list(days[(days.flagged == 1) & (days.rep == 0)].date.dt.date.astype(str)))
    print("  replica-only flagged days:", list(days[(days.flagged == 0) & (days.rep == 1)].date.dt.date.astype(str)))
    print("  mean net by replica flag:", T.groupby("rep").net.agg(["mean", "count"]).round(1).to_dict())
    if var == "base":
        T.assign(kept=T.rep)[["date", "entry_time", "side", "net", "kept"]].to_csv(CDIR + "_replica/trades.csv", index=False)
        g.assign(flag_next=f.astype(int)).to_csv(CDIR + "/replica_sessions.csv")
