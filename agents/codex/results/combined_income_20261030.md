# Twenty activated 150K funded accounts plus the full current personal portfolio

Summary: Published benchmarks imply about $775,870 in the first modeled year, averaging $64,656/month.
That combines $361,120 in funded cash payouts and approximately $414,750 in personal trading profit.
User definition: current 19-piece personal portfolio at one mini per leg, without the aggressive five doubled positions.
This is conditional benchmark arithmetic before taxes/replacement fees, not a live-income forecast or a new simulation.
The same funded cohort has a $410,000 lifetime payout cap; personal sizing implies roughly $363,960 of capital.

Sources pinned at Claude `a01be1bfd0a3c33bc2c6745b24acbf5c14e924c1`. [Input/hash manifest](../inputs/combined_income_20261030/manifest.json).
Script: [calculation](../../../analysis/codex_combined_income_20261030.py).
Output: [calculation.json](../../../analysis/outputs/codex_combined_income_20261030/calculation.json).
No market-return test, parameter selection or account simulation was run.

## First-year reference calculation

| Component | Basis | First year | Monthly average |
|---|---|---:|---:|
|20already activated 150K funded PAs|20 x $18,056 source mean payout|$361,120|$30,093|
|Current19-piece personal portfolio|10 x $41,475 published one-micro annual profit|$414,750|$34,562|
|Combined|Arithmetic sum of the above reference figures|**$775,870**|**$64,656**|

Funded source: `analysis/outputs/t_oneside_bench2_output.txt`, current 150K base row, 1,000 paired two-year
bootstrap histories. Mean first-year payout is $18,056 per account; year one is 250 modeled trading days.
This is the current roster (including Swing Target in place of Dual Thrust, while 150K keeps Relative Strength,
Monday Long and Overnight Tick). Existing cushion, integer-size and payout rules remain part of the source model.
It does not assume constant maximum size regardless of drawdown or add T_ONESIDE to 150K.

Personal source: `analysis/outputs/personal_variants_output.txt`, the current 19-piece row, not conservative/aggressive.
Its published 2018–2026 historical annual profit is $41,475 at one micro per strategy unit. One mini is 10 micro
equivalents for the included contracts, so the fixed-size annual reference is $414,750. S30's two underlying legs
both scale with its source unit; it is not replaced with a quarter-weight ladder mix. This is the exact user-selected
current portfolio definition. The older $322,400 top ladder row uses a different core/S30 mix and is not used.

Personal risk figures scale the same way: published p95 annual drawdown about $72,790, historical max
drawdown $65,920, and risk-rule capital around $363,960 to hold the modeled p95 drawdown at 20%.
This is the published risk-capital rule, not a verified broker margin requirement or a recommendation to allocate.

## These figures are not a perpetual monthly salary

The funded simulator's payout ladder is $2,500, $3,000, $3,000, $3,000, $4,000, $5,000, totaling $20,500 per account.
After payout six, that modeled account closes. Thus these original 20accounts can pay at most $410,000 in total,
not that amount every year. The latest source mean two-year payout is $20,183 per account, so without
replacements the source implies approximately $42,540 additional funded cash in year two. With unchanged
personal size/annual reference, the illustrative second-year total would then be $457,290.
Maintaining an ongoing 20-slot fleet requires replacement evaluations, their fees, waiting time and failures;
no current-roster recurring-fleet result was newly simulated here. The first-year number starts after activation
and must not be substituted for the earlier ramp-from-zero projections.

Monthly figures are annual arithmetic divided by 12. Payout eligibility, correlated losses and trading profits are
uneven through the year. Twenty copies are not 20 independent opportunities for diversification. Adding separate
payout/profit references gives no joint confidence interval or guaranteed minimum; neither source's p5 can simply
be added to the other's p5 to make a combined percentile.

## Costs and verification limits

- Figures retain the source models' trading-cost deductions and are before tax and future evaluation/replacement
  costs. Activation is assumed already paid/completed. No gross trading P&L was substituted for funded cash withdrawals.
- Personal is a tenfold scaling of costed micro results, not a fresh native-mini fill/commission/impact simulation.
  The source charges micro costs of roughly $1.25 RT (NQ-normalized fees plus $0.55 extra per micro trade). Mini commissions
  could differ, but no fee saving is credited here; unchanged fill quality at mini size is not certified.
- The funded $18,056 benchmark is published research. After the reviewed Swing Target exit-kind correction,
  the complete current account replay is still pending. Do not label this a corrected independently verified forecast.
- Personal results include pieces awaiting live/forward verification and known marking/data limits; the live edge
  is unproven. Constant sizes are assumed, and transfers from Apex into personal capital are not counted again as profit.
- No combined 75%-edge payout simulation exists for this exact setup. Multiplying funded payouts by 0.75 would not
  reproduce drawdown, consistency, payout-cap and eligibility effects, so no such result is invented.

Inputs are rounded published summaries. Dollar arithmetic precision is not prediction accuracy.

No plan, allocation, live strategy, VPS, broker or API settings were changed. Research/scout selection history
and budgets are untouched. For Claude: `agents/codex/results/combined_income_20261030.md`.
