# Standalone unchanged ES baseline: user-nominated validation

User: “why cant we just use the baseline set?” This nominates the existing baseline for consideration;
it overrides the old comparison protocol's nonselectable-comparator restriction for this new explicit task.
The modified candidate remains rejected and receives no further returns. Commit before2023+calculation.
[Evidence](../evidence/delgado_es_baseline_20261108.md).

## Freeze

Use exactly `analysis/codex_delgado_es.py` from4740cdd2, model`base`, with identicalGrid24ge.pkl/raw
inputs and costs. No change to14normal-session noise, symmetric1.0band/VWAP gates, checkpoint/reversal/
flat clocks, missing-data policy, whole ES sizing,100k2018initial capital, volatility target or4xrequested cap.
No additional candidate/parameters. The unchanged rule is already one of the three original definitions;
count one extra selection observation conservatively (combined lower bound440, not reset to1).

Replay from2018to preserve NAV/features, but require the2018–22daily/trade CSV bytes to match the
previously committed design outputs **exactly**. Halt on mismatch rather than inspect new returns or fix
parameters. Confirm code/cache/protocol hashes before replay. Save outputs in a distinct baseline-validation
directory. No use of the failed candidate's gated`--stage recent` command or candidate/shadow replay.

Once only: summarize2023through latest owned ES session (2026-10-09expected), whole/long/short/year
using repository metrics and unchanged native-cost gross/net bridge. Preserve full through-time ledger.
Report both actual dollar-P&L and daily simple-return statistics for compounded risk sizing, intraday paths
unknown, complete-day sample/exclusions, observed-endpoint NAV bridge, exposure flags and cost stress.
2023+is historical validation on already-seen family data, not a pristine holdout. No retuning if it weakens.

Use existing`resampling.bootstrap`,1000moving-block samples, block20, seed7323419on complete recent
daily dollar P&L and daily returns. Label intervals conditional on observed history/missing-day treatment;
return-based helper annualization is arithmetic, not a compounded CAGR guarantee. Report only its return
Sharpe/mean interval where relevant. No interpolation or unknown return turned into0.

1000matched-duration random-side controls, seed7323420: on known recent trades keep entry/exit dates,
quantities and gross absolute direction-return magnitudes, randomly assign side, subtract the same commission/
slippage, aggregate to the same known-day calendar. Save net/Sharpe distributions and plus-one p-values.
This conditions on actual endogenous exit durations/quantity path; it is a descriptive fixed-exit control, not
proof from a fully causal independent strategy. Do not silently treat it as an untouched placebo win.

## Decision and account scope

Continue as a research watch only if recent net/stress are positive, at least3of4calendar years positive,
return t>=2, >=300known trades and bootstrap return-Sharpe p5>0. Independently report multiplicity tbar/
DSR(.95promotion standard), data coverage, native margin/roll and exposure. Any failure means no current
standalone recommendation; no rescue. Passing these descriptive checks does not waive promotion gates.

The design already has unknown native held/calendar paths and marked notional-cap breaches. Without new
validated inputs these are binding limits for allfive homes; therefore **no account simulation**, even if
recent standalone statistics pass. Report personal,50K/150Kevaluation and50K/150Kfunded individually.
No portfolio contribution or payout/risk improvement inferred from baseline standalone profitability. If every
statistical and native execution gate later passes with genuinely new evidence, refresh current book and
use personal PAPERTREND/propVB as prespecified replacement with BASE/ADD/REPLACE/EMPTY controls.
That conditional later stage is not earned by this new validation protocol alone.

Report the baseline's own result rather than treating the modified candidate's failure as evidence it fails.
No live/MultiCharts code, allocation change or claim of post-selection independent validation.
