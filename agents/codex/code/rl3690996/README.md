# Corrected stock and MNQ RL strategies — offline research

Two executable research adaptations of SSRN3690996, explicitly requested by the user. These are new protocols,
not reproductions of the paper's13% return or Sharpe1.30. Neither program connects to a broker or places orders.
[Frozen plan](../../plans/rl3690996_build_20261030.md), [evidence](../../evidence/rl3690996_build_20261030.md).

## Files

- `analysis/codex_rl3690996_core.py`: past-only features and turbulence, data preparation, integer-share cash ledger,
  corporate-action factor adjustments, native-MNQ fills/stops/reversal/daily-budget/session-flatten ledger.
- `analysis/codex_rl3690996_env.py`: Gymnasium stock and futures environments and deterministic action conversion.
- `analysis/codex_rl3690996_train.py`: quarterly PPO/A2C/DDPG fitting, preceding-quarter selection, fixed controls,
  design/stress tests, policy checkpoints and complete daily/fill/closed-realization outputs.
- `analysis/codex_rl3690996_verify.py`: synthetic financial/clock/causality and Gym interface verification.
- `analysis/codex_rl3690996_verify_results.py`: independent saved-ledger cash/position/cost replay and fold checks.
- `analysis/codex_rl3690996_report.py`: render saved results and equity plot; no fitting or policy selection.

Stock observations at close t first execute at the next session's raw open proxy, with fee-inclusive cash clipping.
MNQ observations at completed5-minute bars first execute in the next minute, with a stop active in that entry minute.
Targets are -1/0/+1MNQ, and final exit occurs14:56Chicago time. There is no automatic live deployment or PowerLanguage
translation; trained neural policies and their state/risk engine are required to reproduce decisions.

## Environment

Use a separate Python3.12 environment. Tested versions: Torch2.5.1 CPU, Stable-Baselines3 2.4.1, Gymnasium1.0.0,
NumPy1.26.4, pandas2.2.3, SciPy and the repository's metrics tools. Install CPU Torch from the official CPU wheel
index, then SB3/Gymnasium. Preserve proxy/CA settings; no Docker or API key is required.
Exact versions used are retained in `requirements.txt` in this directory.

```
python -m venv --system-site-packages /workspace/venvs/rl3690996
/workspace/venvs/rl3690996/bin/python -m pip install torch==2.5.1+cpu --index-url https://download.pytorch.org/whl/cpu
/workspace/venvs/rl3690996/bin/python -m pip install stable-baselines3==2.4.1 gymnasium==1.0.0
```

## Data and commands

Run from the repository root. The prior paper review saved source URLs and Git/SHA256 hashes in
`agents/codex/inputs/rl_ensemble_3690996_20261030/data_acquisition.json`. The downloaded raw stock file is currently
`/workspace/scratch/rl3690996/dow_30_2009_2020.csv`. The owned NQ grid is `/workspace/scratch/g24.pkl`; its generation
uses the repository's Grid24. Price-grid pickle compatibility may require using the original NumPy2 data-preparation
environment rather than the NumPy1.26 training environment; the resulting NPZ features work in both.

Optional path selectors: `RL3690996_STOCK_DATA`, `RL3690996_GRID`, `RL3690996_RUNTIME`. Defaults target this workspace;
set them to your own files/cache for another checkout. Runtime feature arrays and model ZIPs are Git-ignored.

```
/workspace/venvs/thebeginning/bin/python analysis/codex_rl3690996_core.py
/workspace/venvs/rl3690996/bin/python analysis/codex_rl3690996_verify.py
/workspace/venvs/rl3690996/bin/python analysis/codex_rl3690996_train.py stocks design
/workspace/venvs/rl3690996/bin/python analysis/codex_rl3690996_train.py futures design
/workspace/venvs/rl3690996/bin/python analysis/codex_rl3690996_verify_results.py
/workspace/venvs/rl3690996/bin/python analysis/codex_rl3690996_report.py
```

Frozen primary seed is3690996. Each profile generates eight declared economic series: four candidates, three fixed
controls and the doubled-cost selector stress. Seed17/29 confirmation is gated on primary-design success; reserved
validation is gated on both confirmations. The CLI supports `--seed 17`/`--seed 29` and `validation` under those gates.
No automatically chosen seed, hyperparameter tuning, or automatic continuation after failure.

Outputs: `analysis/outputs/codex_rl3690996_build/<profile>/design/`. Each includes `summary.csv`, `gate.json`,
`selections.csv`, full daily/fill/closed ledgers, by-year files, side attribution for MNQ, and input/code/model identity.
Validation selection always uses earlier data. Strategy NAV/P&L differs from validation NAV and from simulated Apex payouts.
Postrun verification saves `model_receipts.json` with all84 checkpoint signatures/hashes across the two profiles.
`report_metrics.csv` uses fixed-size dollar-P&L Sharpe/Sortino for MNQ; the original trainer's analytical-NAV ratios
remain untouched in `summary.csv`. Frozen advancement checks use analytical-NAV daily returns; their original
decisions are preserved. The report also shows the fixed-dollar incremental diagnostic and explains the difference.

## Material scope limits

The stock panel ends2020; no2023+ claim can be made. It is a static28-name subset after excluding DD/RTX for unresolved
merger/spin-off accounting. Dividends and a certified point-in-time membership/corporate-action feed are absent.
Future exogenous data revisions and actual opening-auction/arrival routing remain unverified.
Futures tests use continuous NQ bars as MNQ execution proxies and condition on complete observed sessions; incomplete
days remain listed, not interpreted as no-signal days. Stops have gap risk. A$250 daily strategy budget per MNQ is
not an Apex floor model, and standalone return/drawdown is not an earned portfolio improvement.

Neither strategy changes the current trading plan. All five placement verdicts and observed test results belong in
the completed result report. If a design gate fails, deliver the built code and negative test without a rescue search.

Completed results: [both adaptations and performance](../../results/rl3690996_build_20261030.md).
The report renderer asserts both primary gates failed; a passing experiment would require completing its earned
confirmation/validation stages and a report for those results instead of using this negative-result renderer.
