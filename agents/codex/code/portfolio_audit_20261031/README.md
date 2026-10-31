# Current portfolio audit — offline research

[Completed findings](../../results/portfolio_audit_20261031.md),
[frozen protocol and retained corrections](../../plans/portfolio_audit_20261031.md).

Current five-home baseline audit. No new strategy, fit, allocation selection, signal tuning or live integration.
Exact source Claude `c3126aa01796133f3aecb368e688726931dea440`; source checkout must remain separate from codex/work.
Current source retains T_ONESIDE/VB2/1 on50K funded, restores DT2 on150K funded, and keeps Swing Target personal.

The scripts use the existing NumPy/pandas/SciPy/Numba/openpyxl/matplotlib environment. Exact installed versions,
input/cache hashes, code hashes and every result file are retained in `delivery_manifest.json` and `preparation.json`.
Source report, account-engine and data-readiness limits are part of the results, not solved by a successful run.

From the repository root, with a read-only source checkout and the existing owned-grid caches:

```
export PORTFOLIO_AUDIT_SOURCE=/workspace/scratch/portfolio_audit_source
export PORTFOLIO_AUDIT_SCRATCH=/workspace/scratch
/workspace/venvs/thebeginning/bin/python analysis/codex_portfolio_audit_verify.py mechanics
/workspace/venvs/thebeginning/bin/python analysis/codex_portfolio_audit_prepare.py
/workspace/venvs/thebeginning/bin/python analysis/codex_portfolio_audit_run.py
/workspace/venvs/thebeginning/bin/python analysis/codex_portfolio_audit_verify.py saved
/workspace/venvs/thebeginning/bin/python analysis/codex_portfolio_audit_diagnostics.py
/workspace/venvs/thebeginning/bin/python analysis/codex_portfolio_audit_report.py
/workspace/venvs/thebeginning/bin/python analysis/codex_portfolio_audit_manifest.py
```

Scratch inputs: `g24.pkl`, `ge.pkl`, `cl.pkl`, `rs_trades.csv`, `single_print_sessions.pkl`, `s_rank_gap2.pkl`.
These are existing repository-library caches built from owned minute data and fixed strategy helpers; their exact
hashes are recorded. A cache with the same name is not necessarily the same input. Runtime NPZ unit paths are
Git-ignored under `agents/codex/runtime/portfolio_audit_20261031/`. Output CSV/JSON/PNG files are committed under
`analysis/outputs/codex_portfolio_audit_20261031/`.

Main commissions: user-reported MNQ estimate$1.04RT; MES/MCL$1.04 assumed. Main adverse market/stop slippage:
one native tick, target-limit exits no slipped tick. Fee sensitivity$1.24RT; stress$2.08RT/two ticks.
No external credentials, payments or broker connection are required.

Known recorded cash/size coverage and complete held-minute risk coverage are separate masks. Reports retain
both. Root account results are conditional sparse-price/source-simulator sensitivities, not certified live Apex odds.
The personal book retains explicitly disclosed Twin-version, Kusho exit-day and contract-roll/margin limits.

Archived `initial_complete_path_subset/` removes too many CL trades to represent the full book and its150K funded
account outputs also use the wrong50K preset. `implementation_wrong_150_preset/` retains the later failed attempt;
its150K account results are invalid. Use verified root outputs; never mix an archived failure into an account verdict.

The final source-preset selection is an explicit account-name mapping. Independent checks enforce start balance,
each cumulative payout ladder and all five canonical account outputs on fixed paired histories. This caught the
runner's original ambiguous suffix bug; it does not claim every remaining simulator assumption is verified.
