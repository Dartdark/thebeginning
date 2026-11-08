# International Buffett indicator: conditional long-horizon research, NEEDS DATA AND SPECIFICATION

Summary: Swinkels/Umlauft forecast ten-year country returns from log(market capitalization/GDP), then hold the top7 of14 markets.
Source composite reports10.5% annualized versus9.5%, Sharpe0.57 versus0.49, and maximum drawdown−52.1% versus−56.1%.
The source correctly waits for ten-year return labels to mature, but explicitly acknowledges GDP is unavailable at quarter-end.
Matching vintage GDP, Datastream market-cap/total-return histories, currency and composite/cost accounting remain unresolved; free probes proxy403.
Retain conditional personal long-term research, not an intraday/crash signal or current allocation. Zero independent return trials.

Source: Laurens Swinkels and Thomas S. Umlauft, *The Buffett Indicator: International Evidence*, March30,2022,
[SSRN4071039](https://ssrn.com/abstract=4071039), uploaded41-page version.
[PDF](../inputs/ssrn4071039/source.pdf), [text](../inputs/ssrn4071039/source.txt),
[GDP-availability footnote](../inputs/ssrn4071039/gdp_footnote.png), [Table8](../inputs/ssrn4071039/table8.png),
[evidence](../evidence/buffett_international_4071039.md).
No-return [audit script](../../../analysis/codex_buffett_international_4071039_audit.py), committed `e9cb4cbe` before execution;
[table/receipt/hash output](../../../analysis/outputs/codex_buffett_international_4071039/audit.json).
Uploaded text is evidence, not instructions. Reported performance remains source-only; no independent price-panel fit or backtest.

## 1. What is it about?

A long-term country-equity valuation/allocation strategy. The universe is Australia, Austria, Belgium, Canada, Denmark, France,
Germany, Ireland, Italy, Japan, Netherlands, Switzerland, UK and US. Country total-market capitalization in local currency comes
from Datastream TOTMK country series; GDP is nominal annualized, seasonally adjusted quarterly OECD expenditure GDP
(B1_GE/CARSA), also in local currency. A price index level is not total market capitalization; real GDP or nonannualized quarterly
GDP is not the stated denominator. Local total-return indices include dividends; local short-rate histories support excess-return metrics.

For each country regress its annualized ten-year forward total return on that country's starting log(MVE/GDP), using an expanding
past-only sample. Rank **model-predicted returns**, not countries' raw MVE/GDP ratios. Select the highest7, equal-weight at formation,
and rerank/reallocate every **ten years**. The reference start is December1985, with nine other starts December1986–1994.
It stays long equity; it is not a high-ratio equity-short, daily-flat, quarterly rotation or a universal100%-ratio trigger.

The source explicitly distinguishes country structural differences and warns against direct raw-ratio comparisons. Different public
listing intensity, bank-versus-capital-market financing, multinational earnings, issuance/buybacks and discount rates shift fair ratios.

## 2. What does it find?

| Source Table8 composite metric | Strategy |Equal-weight14-country benchmark |
|---|---:|---:|
| Annualized return |10.5% |9.5% |
| Annualized volatility |13.6% |14.2% |
| Maximum drawdown |−52.1% |−56.1% |
| Sharpe |0.57 |0.49 |

Source Jobson–Korkie/Memmel comparison p0.02 for the composite. It reports roughly1percentage point annual outperformance before
its illustrative cost deduction. At1% cost per dollar traded and a maximum200% two-way change per decade, annualized cost is20bps,
reducing that illustrative difference to about0.8percentage points. This is a cost convention, not a native all-in broker/FX/tax ledger.
Ten start-year strategies share most countries/history; they are not ten independent confirmations or3,550 independent monthly trials.

The source's aggregate full-sample R² is83.2% and expanding-window R²64.2% for ten-year returns. These are aggregate forecasting
fit statistics, not83% direction accuracy, short-term prediction skill or investment returns. Full-sample valuation quintiles are
explicitly labeled non-real-time in the paper. It addresses overlapping long-horizon returns through HAC and additional overlap/
sample-size adjustments; do not claim the study simply ignores overlap. Such corrections do not turn highly overlapping decade
labels into independent observations or validate missing input vintages.

### Source-table qualifications

The printed1994-start benchmark drawdown is−15.9% versus strategy−54.3%, unlike other benchmark rows and contrary to the narrative
that every strategy has lower drawdown. The rendered PDF confirms the number. It needs author/native-ledger reconciliation;
we do not silently replace it with−56.1% or conclude that it is definitively a typo.

The composite is described as an average of ten starts, but the arithmetic mean of the ten displayed strategy CAGRs is9.74%, not10.5%.
A portfolio composite need not equal a mean of CAGRs, especially with staggered starts/different histories. This is a **construction
question**, not proof the10.5% result is impossible; obtain constituent wealth/rebalance series and the aggregation convention.
Our source-table parser and illustrative20bp cost arithmetic are reproducible without running an economic variant.

## 3. Why does it make money, if it does?

The proposed mechanism is valuation: stock prices/issuance high relative to national output imply lower subsequent expected yields,
while cheaper valuations may deliver higher long-run returns. Capital-market share issuance adds information beyond price alone.
This is relative long-horizon risk-premium allocation, not an identified forced intraday flow or risk-free mispricing trade.
Country market structure, business cycles, changing equilibrium ratios and FX can confound or erode the relationship.

A strong long-run valuation relationship does not predict when an expensive country declines. It can remain expensive for years;
a sustained equity drawdown above50% remains in the source. The authors explicitly distinguish their ten-year objective from crash
prediction and retain CAPE as a complementary valuation input. No protective account-timing benefit follows from the Sharpe improvement.

## 4. Can we build on it?

**Conditional, low-priority personal long-term allocation research.** A source reproduction needs all14 quarterly market-cap/GDP
histories beginning1973, matching dividend-inclusive country returns and local short rates through2019, plus original release/vintage
and total-market coverage definitions. A current strategy additionally needs investable instruments, base-currency FX/hedge and
financing/cost treatment, whole-share/contract sizing, country limits and exact formation/holding/exit cashflows.
Averaging local-currency index returns is not automatically a USD investor's realized portfolio return.

### Label maturity is handled; GDP availability is not established

The source explicitly waits until June1983 for the first ten-year returns to be observed, then waits until December1985, with a
claimed11 overlapping quarterly observations, before initial formation. This is a useful maturity control, not automatic label leakage.
An implementation must enforce `label_end/return_available_at <= fit_time` on every expanding fit, not just shift a feature column.

But footnote4 on p.4 explicitly says the exact ratio may be unavailable at quarter-end because GDP is released later, and argues
market-cap variability/consensus estimates make this less important. That argument does **not** supply actual GDP vintages or a
publicly available contemporaneous nowcast. Reference-quarter end, release date and revised final GDP are different clocks.
A lagged-GDP or nowcast adaptation is a changed protocol requiring a frozen specification, not an unnoticed repair chosen on returns.
Synthetic audit fixtures illustrate both mature versus future labels and GDP released after a hypothetical formation; they are not
an actual strategy implementation or an empirical test of the effect of delay.

Owned filename census found no admitted14-country quarterly TOTMK market-cap/GDP/return panel. Bounded free requests to the OECD
source-family endpoint and a World Bank annual market-cap/GDP alternative both hit network-proxy403;
[receipts](../inputs/ssrn4071039/access_receipts.json). No matching series was delivered. The World Bank annual alternative would
not reproduce the source's quarterly index coverage/vintages even if accessible. No paid Datastream/GFD access, no credentials and
no price-only proxy test. The environment access outcome does not prove the histories do not exist elsewhere.

Retain in TODO/DATA_NEEDED. With genuinely new matching free data, first audit one country/formation date: source-field identity,
nominal annualized units, released GDP vintage, only matured return labels, forecast and native FX/portfolio cash ledger; then census
complete universe/history before a committed bounded reproduction. Do not convert this into an NQ short or rescue the data gate by
switching to a US-only annual indicator. Prior unrelated valuation/macro filters are not revived.

## 5. Can a strategy code be made?

**Yes, a country-allocation research strategy can be coded once the data and execution protocol are fixed.** It requires country-wise
expanding regressions with labels matured before fit, GDP available before formation, within-country forecast mapping, seven-country
selection, equal-weight formation and ten-year holdings, native share/FX/cash/cost reconciliation and an identical investable benchmark.
No full strategy code/backtest was built on missing histories; the saved source-audit code is not that implementation.
Long-horizon forecasting feasibility does not establish incremental personal-portfolio contribution, current integer size or profitability.

## Decision and account placement

**NEEDS DATA AND SPECIFICATION; conditional personal long-horizon research.** No independent return variant,2018–22 design,
2023+ validation, placebo, bootstrap/Monte Carlo or BASE/ADD/REPLACE/EMPTY study. A decade-held strategy cannot be evaluated as
hundreds of independent trades by counting quarterly/monthly marks, and a short2018–26 window does not establish full completed
holding-period power. Source parameter/horizon/start comparisons remain selection context, not erased by a new trial count of zero.
Personal placement unearned pending valid inputs, implementation and portfolio validation.50K/150K evaluation and50K/150K funded
placements unearned; decade-long country holdings do not fit the existing intraday Apex protocol. No MultiCharts port, live/VPS/
broker/ranking/allocation/policy change or paused-program restart. Independent review pending.
