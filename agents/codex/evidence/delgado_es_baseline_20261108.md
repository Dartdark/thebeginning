# Unchanged ES baseline: TEST completed; recent-strength gates fail

The user asks why the profitable baseline cannot be used. This explicitly nominates the unchanged baseline
for a separate evaluation after the modified candidate failed. It does not promote the failed overlays or grant
live/account changes. Prior context: [ES comparison](../results/delgado_es_20261108.md).

- **Mechanism/participant:** intraday price persistence beyond time-of-day noise; no measured forced order.
- **Timing/direction:** same frozen14-session noise/VWAP baseline in code4740cdd2; completed checkpoint
  close determines side/quantity, next observed minute open executes. No rules or sizing changes.
- **Data/transmission:** actual owned ES continuous minutes with documented close-stamped CT grid/calendar.
  Unknown days/held paths and roll mapping remain certification limits; no SPY minute data needed for this test.
- **Costs/power:** native ES$50/point,.25tick, commission$5RTplus one tick/side. Existing design964complete
  trades,$107,475complete-day net, return t2.86; positive all five years and fixed-fill extra-tick stress.
- **Prior/selection:** baseline is selected after seeing design comparison, not a fresh preregistered winner.
 439combined trial-count lower bound is retained and conservatively incremented to440for this additional
  selection step. No claim of clean2023+holdout: family/source history already seen. No parameter search.
- **Liquidity/failure:** market-taking, whipsaw/reentry costs, exposure/roll/gap risk and correlated trend losses.
  Earlier baseline has unknown calendar/held paths and3small marked4xbreaches, so no account promotion
  even if newer conditional returns are positive. No guaranteed before-breach offset established.
- **Decision:** TEST limited to the once-only unchanged baseline2023+historical reconstruction and fixed
  diagnostics under a new committed protocol. The old stop still applies to the failed modified candidate.
  Statistical merit, sizing/execution certification and account contribution remain separate decisions.

## Completed outcome

[Report](../results/delgado_es_baseline_20261108.md): unchanged2018–22daily/trade prefixes match byte
for byte.2023–October9,2026known-day net+$49,755, return Sharpe.550, daily return t1.065;
2025+$852.50and2026−$32,910. Daily DD$56,842.50;1000block-bootstrap Sharpe p5−.175.
The baseline's own recent validation fails t/interval gates. No new variants, account simulations or allocation.
One recent unknown held-price day retained; source/cost/margin/roll certification limits remain.
