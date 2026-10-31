# Valeris 848: source-review scope (no new strategy returns)

Summary: Review the user's supplied code/report and decide whether they justify changing the current plan.
Inspect reported statistics, selection history, cost/account assumptions and exact implementation.
Do not optimize, reconstruct a ledger from prices, run an account simulation or start a forward test.

Evidence: `agents/codex/evidence/valeris_848.md` (NEEDS DATA).
Starting Codex commit: `1bab29f05d57da9801b700a163de1e1e3d2ffb36`.
Current Claude context: `b1256664232722b25afefc0004e6f9e04c1976ae`.
This records review scope after reading the supplied report; it is **not** a preregistration of unseen strategy results.

## Authorized checks

- Archive and hash the unchanged code and PDF; extract/render the PDF and audit its published tables.
- Compare literal source inputs, timing, stop mechanics, roll treatment and sizing with the report.
- Use primary paper/MultiCharts documentation to check claims.
- Reconcile cost conventions arithmetically against rounded reported totals; do not invent new trade nets or risk metrics.
- Compare evidence standards and hours with the current funded/evaluation plan. Keep separate-model figures descriptive.
- Get independent read-only code and plan-context reviews, then check the final conclusion.

## Decision rule

Do not recommend an addition/replacement without current-version confirmation, clean selection-adjusted evidence,
full declared costs, independent checker acceptance and a paired bootstrapped add/replace/empty-slot comparison with
intraday account paths. Positive standalone P&L alone is insufficient. Recommend no plan change if these are missing.

New return variants: 0. Reading published long/short, size, stress and account tables does not create a new Codex backtest.
Published author trials are disclosed separately. No source fix, live setup, cache rebuild, PR #2 action or trading decision.
