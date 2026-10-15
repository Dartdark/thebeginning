"""PBO audit (Bailey, Borwein, Lopez de Prado & Zhu 2015, 'The Probability of Backtest Overfitting', user's PDF, 2026-10-15):
CSCV over every variant family we searched where the variants' trades are on disk; daily P&L per NQ, 16 time blocks.
Reports PBO (share of splits where the in-sample winner ranks in the bottom half out of sample), the performance
degradation slope (OOS Sharpe of the IS winner on its IS Sharpe; < 0 = the better it looked, the worse it did) and the
probability of loss (IS winner's OOS Sharpe < 0).
  python3 analysis/pbo_audit.py [SCRATCH_DIR]
"""
import sys, glob, pickle, os, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def daily(x, days):
    x = pd.Series(x); x.index = pd.DatetimeIndex(x.index).normalize(); return x.groupby(level=0).sum().reindex(days, fill_value=0.0)


def show(nm, cols, chosen):
    days = pd.bdate_range("2018-01-01", "2026-10-09"); Rm = pd.DataFrame({k: daily(v, days) for k, v in cols.items()})
    r = M.pbo(Rm, full=True); sr = Rm.mean() / Rm.std() * np.sqrt(252)
    print(f"   {nm:<44} N {Rm.shape[1]:2d}  PBO {r['pbo']:.2f}  degradation slope {r['degradation_slope']:+.2f}  P(loss) {r['p_loss']:.2f}"
          f" | chosen '{chosen}' full-sample Sharpe {sr[chosen]:.2f} (rank {int(sr.rank(ascending=False)[chosen])}/{len(sr)})")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    # Twin Continuation: base + the checker's 16 parameter perturbations
    d = "checks/candidates/twin_continuation/"
    cols = {"base": pd.read_csv(d + "trades.csv", parse_dates=["date"]).set_index("date").net}
    for f in sorted(glob.glob(d + "trades_replica_*.csv")):
        cols[os.path.basename(f)[15:-4]] = pd.read_csv(f, parse_dates=["date"]).set_index("date").net
    show("Twin Continuation (checker perturbations)", cols, "base")
    # round 3 high-win search: 9 entry x exit variants
    res = pickle.load(open(SP + "high_winrate_res.pkl", "rb"))
    show("High-win search round 3 (9 variants)", {f"{k[0]} {k[1]:.2f}/{k[2]:.2f}": v.net for k, v in res.items()}, "E1 0.10/0.20")
    # round 2 MO entries (V1-V3)
    cols = {v: pd.read_pickle(SP + f"mo_pullback_{v}.pkl").net for v in ("V1", "V2", "V3")}
    show("MO pullback / tight-stop round 2 (3 variants)", cols, "V3")
    # round 2 + 3 together (the whole Morning-Momentum-derivative search)
    cols.update({f"{k[0]} {k[1]:.2f}/{k[2]:.2f}": v.net for k, v in res.items()})
    show("Rounds 2 + 3 together (12 variants)", cols, "V3")
