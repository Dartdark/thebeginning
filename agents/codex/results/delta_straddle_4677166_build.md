# Delta-straddle code: mechanics PASS; personal return test NEEDS DATA

Summary: Built an offline interpreted 41-market signal/whole-contract target engine at the user's request.
All 34 synthetic behavioral tests pass; zero financial-return trials and no historical account simulation.
Owned/free data still fail the complete source-universe/native cash/roll gate; personal profitability is unknown.
No personal allocation earned; all four Apex homes are incompatible with the source multiday holding rule.
Code is saved for review; no MultiCharts/live implementation or independently verified portfolio contribution.

Plan: [bounded engineering protocol](../plans/delta_straddle_4677166_build.md), committed
`04dbfaeef41636fcd68efd47cf49679575e80fd2` **before tests**.
Script: [strategy engine](../../../analysis/codex_delta_straddle_strategy.py) ·
[receipt recorder](../../../analysis/codex_delta_straddle_build_check.py) ·
[behavioral tests](../test_delta_straddle_strategy.py) ·
[usage and input schema](../research/delta_straddle/README.md).
Outputs: [test receipt](../../../analysis/outputs/codex_delta_straddle_build/test_receipt.json) ·
[invented target example](../../../analysis/outputs/codex_delta_straddle_build/synthetic_plan.json) ·
[five-account admission](../../../analysis/outputs/codex_delta_straddle_build/account_admission.json).
Date: November8,2026(America/Los_Angeles). Independent review pending.

## Rule implemented

One interpreted version: average the smooth sample-t-stat signal over32/64/126/252/504complete sessions;
use EWMA0.94 squared-return volatility for sizing; preserve exact41Appendix identifiers and printed source
weights. Weights already include the class allocations. Use a caller-supplied past-only portfolio multiplier
with a10%risk budget. No original expanding-window calibration is invented.

Translate dollar exposure into signed whole lots toward zero. A0.25risk-scaled no-trade band compares
the continuous desired position with **confirmed held lots**, including partial fills supplied in a later snapshot.
Pending proposals never become holdings. Small sign changes may stay inside the band; equality trades.
A dated-contract roll bypasses the band and estimates close/open costs separately. Common proportional
scaling and whole-lot rounding enforce independent target gross/margin budgets even through the band.

Validate causal observation/calibration/holdings/mapping clocks, exact universe,504-session warmup,
fresh snapshots, positive native risk notionals/prices, integer held lots and expiry beyond eligible fill.
Latency is positive; no available-at value may follow decision. This is a target planner, **not a full backtester**:
it does not implement fills, cash settlement, collateral interest, FX funding, historical rolls/carry or return metrics.

Source/model gaps are deliberate and disclosed: simple-return sample SD rather than an authenticated author
signal denominator; fixed EWMA initialization; externally supplied portfolio-risk scale; local integer/band/sign-cross/
roll policies; gross/margin safety guards. No disputed printed AR(1)adjustment, intraday close-out, stop loss,
NQ-only subset, ETF proxy or ED4→SOFR continuation is silently introduced.

## Completed checks

| Check | Result | Evidence limit |
|---|---|---|
| Synthetic mechanical suite | **34pass,0failures,0errors,0skips** | Not market-return observations |
| Known t-stat formula/long-short sign/constant-magnitude EWMA | Pass | Equation/implementation consistency only |
| Actual holdings/band/whole lots/large and small reversals | Pass | No fills confirmed |
| Roll close/open turnover and separate estimated costs | Pass | No measured execution savings |
| Future/stale inputs, wrong universe, invalid mapping, expiry | Rejected as intended | Schema checks cannot authenticate provenance |
| Gross/margin overrides, including zero margin budget | Pass | Final targets only; no transient fill-path margin or gap-loss guarantee |
| Owned-data inventory |158top-level files; source panel unadmitted | Existing native/proxy files are not the full41-market input |
| Historical returns/placebos/account comparison | **Not run** | Data/evidence gate failed before economic trial |

The invented example has520weekday observations and41invented native mappings. Its$100,000NAV and
uniform contract/cost/margin inputs are parser fixtures, not a recommended account size or valid economic proxy.
The receipt includes code/input/test/protocol hashes, Python version, settings and prior plan commit.

Reproduce all saved receipts from root:

```bash
python3 analysis/codex_delta_straddle_build_check.py
```

## Can this earn a personal-account place?

**Not established.** Overnight/multiday holding is structurally compatible with a personal account, but this
does not establish profitability, affordability or added value. The matched41-market history, causal native
FX/return mapping, actual lots/roll/carry/cash/collateral and margin path are missing. Proposed execution fees
are estimates and are not deducted from NAV or available cash; native affordability remains a separate gate.
Review of the existing [free acquisition receipt](../inputs/delta_straddle_4677166/free_data_gate.md) found no
new admitted inputs. No duplicate unchanged public search or paid acquisition was made in this build.

| Home | Current verdict | Portfolio evidence |
|---|---|---|
| Personal | NEEDS DATA AND SPECIFICATION; no allocation earned | BASE/ADD/REPLACE/EMPTY not eligible to run |
|50K evaluation | Source multiday holds incompatible | No account simulation |
|150K evaluation | Source multiday holds incompatible | No account simulation |
|50K funded | Source multiday holds incompatible | No account simulation |
|150K funded | Source multiday holds incompatible | No account simulation |

No P&L, win rate, Sharpe, long/short results, yearly results, drawdown, payout or failure-probability estimates
are available. Missing data do not demonstrate that this strategy loses. Author9.27%annual/Sharpe1.03is
retained only as a source claim in the [paper review](delta_straddle_4677166_review.md), not our backtest.

The reference personal portfolio is [the current19-piece portfolio](../../../personal_strategies/PORTFOLIO.md).
Only after a genuinely new full-input/cash interval passes admission can a separate bounded economic protocol
freeze2018–22design and earned2023+historical validation, integer sizes/costs, placebos, and same-date
BASE/ADD/REPLACE(PAPERTREND)/EMPTY comparisons against the then-current book. Existing failed generic
daily and fast-trend definitions remain negative evidence. No optimization or partial-universe rescue run.

## Retained five answers

1. **About:** slow, diversified smooth-signal trend following, not actual straddle ownership.
2. **Finds:** author historical profitability and sensitivity to turnover; our new finding is engineering feasibility only.
3. **Why money:** persistent trends may outweigh whipsaw/carry/cost losses; not demonstrated on our data.
4. **Build on it:** a conditional personal research sleeve once the full executable panel and accounting exist.
5. **Strategy code:** yes, the signal/risk planner is now built. A complete native replay and MultiCharts strategy
   remain unbuilt/unearned; code mechanics do not establish profit or portfolio placement.

Data requirements remain in[D54](../DATA_NEEDED.md#d54--diversified-delta-straddle-trend-ssrn4677166-november82026).
Execution lesson remains in[E09/E12](../EXECUTION_REFERENCES.md#e09e12-follow-up--slow-trend-signals-actual-position-turnover-and-no-trade-bands):
rebalancing uses confirmed holdings; rolls charge both legs; safety reductions bypass the band. Synthetic tests
verify those declared behaviors, not realized trading savings. No live systems/accounts/allocations changed.

Tell Claude: review `agents/codex/results/delta_straddle_4677166_build.md`;34mechanical checks pass,
but source-equivalent personal backtest remains data-blocked and no strategy earns a current allocation.
