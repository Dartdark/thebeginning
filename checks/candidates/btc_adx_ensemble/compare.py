"""Compare replica with the maker's trades.csv: match on entry time + book + side."""
import os, sys, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))


def compare(M, Rp, verbose=True):
    M = M.copy(); Rp = Rp.copy()
    for X in (M, Rp): X["t"] = pd.to_datetime(X.t); X["tx"] = pd.to_datetime(X.tx); X["k"] = list(zip(X.t, X.book, X.side))
    j = M.merge(Rp, on=["t", "book", "side"], how="outer", suffixes=("_m", "_r"), indicator=True)
    both = j[j._merge == "both"]
    res = dict(maker=len(M), replica=len(Rp), matched=len(both), match_of_maker=len(both) / len(M),
               match_of_replica=len(both) / len(Rp), corr=both.net_m.corr(both.net_r),
               same_exit=(both.tx_m == both.tx_r).mean(), same_why=(both.why_m == both.why_r).mean(),
               mean_m=M.net.mean(), mean_r=Rp.net.mean(), R_corr=both.R_m.corr(both.R_r),
               R_absdiff=(both.R_m / both.R_r - 1).abs().median())
    if verbose:
        for k, v in res.items(): print(f"{k:18s} {v:.4f}" if isinstance(v, float) else f"{k:18s} {v}")
    return res, j


if __name__ == "__main__":
    M = pd.read_csv(os.path.join(HERE, "trades.csv")); Rp = pd.read_csv(os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "trades_replica.csv"))
    res, j = compare(M, Rp)
    only_m = j[j._merge == "left_only"]; only_r = j[j._merge == "right_only"]
    print("\nmaker-only (first 25):"); print(only_m[["t", "book", "side", "net_m", "why_m", "tx_m"]].head(25).to_string())
    print("\nreplica-only (first 25):"); print(only_r[["t", "book", "side", "net_r", "why_r", "tx_r"]].head(25).to_string())
    b = j[j._merge == "both"]; d = b[b.tx_m != b.tx_r]
    print("\nmatched, different exit (first 25):"); print(d[["t", "book", "side", "net_m", "net_r", "why_m", "why_r", "tx_m", "tx_r"]].head(25).to_string())
