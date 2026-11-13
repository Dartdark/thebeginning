"""Fair placebo for the personal Overnight Tick version of WATCHLIST #38 ('skip stretched S&P + 3 MNQ on any-fear days': full book
return/DD 5.92 -> 6.37, +0.44). Mimics the selection: a 'skip' split = the best same-sign NEGATIVE-gap split of 63 random day
splits, a 'size-up' split = the best POSITIVE-gap split of another 63 (on-shares as the real regimes); OT 0 on skip days, 3 on
size-up days, 2 otherwise; full-book 1-year bootstrap return/DD change; 20 runs. Information.
  tools/run_stamped.sh analysis/ot_version_placebo.py > analysis/outputs/ot_version_placebo_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    P = pd.read_pickle("scratch_data/personal_P.pkl"); ot = P.OvernightTick; act = (ot != 0).values; v = ot[act].values; e = (P.index.year <= 2022)[act]
    shares = pd.read_csv("analysis/outputs/data_sweep_table.csv").query("piece == 'OvernightTick'").on_share.values
    f = lambda x: (lambda r: r["pnl_p50"] / r["dd_p95"])(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    base = P.sum(axis=1) + ot; b0 = f(base); rng = np.random.default_rng(8); out = []
    def best(sign):
        bt, bm = -1, None
        for sh in shares:
            h = rng.random(len(v)) < sh
            if h.sum() < 15 or (~h).sum() < 15: continue
            a, b = v[h], v[~h]; t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
            same = np.sign(v[e & h].mean() - v[e & ~h].mean()) == np.sign(v[~e & h].mean() - v[~e & ~h].mean())
            if same and np.sign(t) == sign and abs(t) > bt: bt, bm = abs(t), h
        return bm
    for run in range(20):
        sk, up = best(-1), best(1); m = np.full(len(v), 2.0); m[up] = 3.0; m[sk] = 0.0
        mult = pd.Series(2.0, index=P.index); mult[act] = m; out.append(f(base - 2 * ot + ot * mult) - b0)
    out = np.array(out); print(f"   book return/DD now {b0:.2f}; random best-of-63 versions: change median {np.median(out):+.2f}, 95th {np.percentile(out, 95):+.2f}, max {out.max():+.2f}; real version +0.44 -> p {np.mean(out >= 0.44):.2f}")
