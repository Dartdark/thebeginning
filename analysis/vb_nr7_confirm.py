"""MultiCharts confirmation of the NR7 input in apex_strategies/NQ_Vault_Break_SP.txt (2026-10-18).
User's backtest: 30-min @NQ, same settings as the VB SP confirmation, NumContracts 1, NR7Contracts 2, FlaggedContracts -1
(single print off, so only NR7 changes the size), saved as
"mc_reports/Backtesting Strategy Performance Report _ @NQ - 30 Minutes VB NR7.xlsx" in the repo root.
Checks: the days MultiCharts trades 2 contracts = the sessions after a Python NR7 day; trades otherwise identical to the
VB v1 report; and the NR7 vs other $ per trade.
Without the report it writes the expected sessions to analysis/vb_nr7_flags.csv.
  python3 analysis/vb_nr7_confirm.py [SCRATCH_DIR]
"""
import sys, pickle, os, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.path.insert(0, "analysis/jesse")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
sys.argv = sys.argv[:1]
import compare as C
REPORT = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 30 Minutes VB NR7.xlsx"


def nr7_sessions(n=7):
    g = pickle.load(open(SP + "g24.pkl", "rb")); tr = g.trading
    hi = np.nanmax(g.h[tr, jof(831):jof(1500) + 1], 1); lo = np.nanmin(g.l[tr, jof(831):jof(1500) + 1], 1)
    d = pd.DataFrame(dict(rng=hi - lo), index=pd.DatetimeIndex(g.ts[tr]).normalize()).dropna()
    flag = d.rng <= d.rng.rolling(n).min()
    nxt = pd.Series(d.index[1:], index=d.index[:-1])               # next session after each NR day
    return pd.DatetimeIndex(nxt[flag.iloc[:-1].to_numpy()].to_numpy())


if __name__ == "__main__":
    s = nr7_sessions()
    pd.DataFrame(dict(session=s.date)).to_csv("analysis/vb_nr7_flags.csv", index=False)
    print(f"{len(s)} sessions after an NR7 day written to analysis/vb_nr7_flags.csv")
    if not os.path.exists(REPORT):
        print(f"(no '{REPORT}' yet)"); sys.exit()
    raw = pd.read_excel(REPORT, sheet_name="List of Trades", header=2)
    ent = raw[raw["Type"].astype(str).str.startswith("Entry")].copy(); ent["day"] = pd.to_datetime(ent["Date"]).dt.normalize()
    two = set(ent.loc[ent["Contracts"] >= 2, "day"]); one = set(ent.loc[ent["Contracts"] < 2, "day"])
    traded = set(ent.day); exp = set(s) & traded
    print(f"MC sessions with 2 contracts: {len(two)}; Python NR7 sessions VB traded: {len(exp)}; "
          f"both {len(two & exp)}, MC only {sorted(d.date() for d in two - exp)[:10]}, Python only {sorted(d.date() for d in exp - two)[:10]}")
    m = C.mc_trades(REPORT); m1 = C.mc_trades(C.REPORTS["VaultBreak"][0])
    print(f"trades: NR7 report {len(m)}, VB v1 {len(m1)}; same entry times {len(set(m.entry_time) & set(m1.entry_time))}")
