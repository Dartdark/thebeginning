"""Window-trade grid (2026-10-12): fixed-bracket follow/fade trades at midday and pre-market,
all days vs quiet days (no Vault Break / Overnight Bias entry yet). Expects pickled grids from a
scratch run; kept as the record of the test."""
import sys, warnings, pickle, itertools; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid import execute
from grid24 import jof
from portfolio import load_mc
from multi_strategy24 import VB_REPORT, ONB_REPORT
import funded_candidates as FC, intraday_research as IR
g = pickle.load(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/g24.pkl","rb"))
vb, onb = load_mc(g, VB_REPORT), load_mc(g, ONB_REPORT)
def busy_before(t0):
    """rows where VB or ONB entered before t0 (known at t0)"""
    j = jof(t0)
    return np.unique(np.r_[vb.day[vb.j0 <= j], onb.day[onb.j0 <= j]])
def run(s):
    t = execute(g, s, max_trades=1)
    t = t[pd.DatetimeIndex(t.date).year >= 2018].copy(); t["slips"] = 1 + (t["kind"] != 1); t["net"] -= t["slips"] * 5
    return t
rows = {}
WIN = [("midday 11:00->13:00, signal 8:30->11:00", 1100, 1300, 830),
       ("midday 11:00->13:00, signal 10:00->11:00", 1100, 1300, 1000),
       ("midday 12:00->14:00, signal 8:30->12:00", 1200, 1400, 830),
       ("pre-mkt 3:00->7:00, signal 0:00->3:00", 300, 700, 0),
       ("pre-mkt 3:00->7:00, signal 2:00->3:00", 300, 700, 200),
       ("pre-mkt 5:00->7:15, signal 3:00->5:00", 500, 715, 300)]
for (lab, t0, t1, lf), mode, k, (st, tg), quiet in itertools.product(WIN, ("follow", "fade"), (0.0, 1.0),
                                                                    ((0.1, 0.1), (0.15, 0.08), (0.2, 0.1), (0.1, None)), (False, True)):
    if quiet and t0 < 1000:      # pre-market: VB/ONB never trade before 8:45, quiet filter is moot
        continue
    s = FC.window_signals(g, t0, t1, lf, mode=mode, k=k, stop_atr=st, tgt_atr=tg, skip_rows=busy_before(t0) if quiet else None)
    r = IR.summary(run(s))
    rows[(lab, mode, k, f"{st}/{tg}", "quiet days" if quiet else "all")] = r
df = pd.DataFrame(rows).T
df.index.names = ["window", "mode", "k", "stop/tgt", "days"]
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
df["t"] = df["t_stat"].astype(float)
print(df.sort_values("t", ascending=False).head(25).drop(columns="t").to_string())
print("\n... worst 5"); print(df.sort_values("t").head(5).drop(columns="t").to_string())
df.to_pickle("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/win1.pkl")
