"""Ingredient ablation, round 7: the three Codex bench pieces (Anson momentum, R2Vault, S03 Noise Area v2), from Codex's frozen replay
ledgers (copied from codex/work 2026-11-08 into checks/candidates/<piece>/codex_*.csv). Information only. Their rules are fixed inside
Codex's code, so the 'one part changed' rows are Codex's own alternative models plus side and exit-type splits of the main ledger:
  Anson: intended (threshold 4.5, hold 20 bars) / uploaded defaults (3, 6) / intended with the Apex early-flat adapter; longs / shorts;
         by exit kind
  R2Vault: CT window (09:30-15:30) / ET window (08:30-14:30 CT) / ET with a daily reset / CT Apex; longs / shorts; by exit reason
  S03 v2: v2 (stop factor 0.4) / v1 (no stop factor) / v2 Apex; longs / shorts; by exit reason
Per NQ net = gross_nq - $17.25 x qty ($7.25 + 1 tick per side, the repo standard); 2018-26, both periods, total $ and max DD.
  tools/run_stamped.sh analysis/ingredient_ablation7.py > analysis/outputs/ingredient_ablation7_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from ingredient_ablation3 import line

D = "checks/candidates/"


def load(f):
    t = pd.read_csv(D + f, parse_dates=["date"]); q = t.qty if "qty" in t else 1.0
    t["net"] = t.gross_nq - 17.25 * q; return t[t.date >= "2018-01-01"]


def show(nm, t): print(line(t.net, t.date, nm), flush=True)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for title, main, alts, col in (
            ("1. Anson momentum", ("intended 4.5 / 20 bars (bench)", "anson/codex_intended_raw_trades.csv"),
             (("uploaded defaults 3 / 6 bars", "anson/codex_defaults_raw_trades.csv"), ("intended + Apex early flat", "anson/codex_intended_apex_trades.csv")), "kind_label"),
            ("2. R2Vault", ("CT window 09:30-15:30 (bench)", "r2vault/codex_ct_raw_trades.csv"),
             (("ET window 08:30-14:30 CT", "r2vault/codex_et_raw_trades.csv"), ("ET + daily reset", "r2vault/codex_et_daily_reset_raw_trades.csv"),
              ("CT + Apex flat", "r2vault/codex_ct_apex_trades.csv")), "exit_reason"),
            ("3. S03 Noise Area v2", ("v2, stop factor 0.4 (bench)", "s03_v2/codex_v2_raw_trades.csv"),
             (("v1, no stop factor", "s03_v2/codex_v1_raw_trades.csv"), ("v2 + Apex flat", "s03_v2/codex_v2_apex_trades.csv")), "exit_reason")):
        print(f"\n{title}:"); T = load(main[1]); show(main[0], T)
        for nm, f in alts: show(nm, load(f))
        show("   longs", T[T.side > 0]); show("   shorts", T[T.side < 0])
        for k, grp in T.groupby(col):
            if len(grp) >= 20: show(f"   exit: {k}", grp)
        print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
