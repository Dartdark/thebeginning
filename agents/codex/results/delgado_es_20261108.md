# Delgado rules on ES: REJECT selected adaptation at design gate

Summary: Yes—owned ES data can test a labeled futures adaptation; this historical test is complete.
2018–22complete-day net: BASE$107,475versus CANDIDATE$25,517.50on$100,000initial referenceNAV.
Daily-return Sharpe falls1.281→0.663; maximum daily closed-P&L drawdown barely improves$16,420→$15,330.
Candidate fails daily/trade significance, baseline profit retention and return/drawdown improvement gates.
Stop: no new2023+returns, tuning or account simulation; no current allocation. Unknown paths remain disclosed.

Plan: [frozen protocol](../plans/delgado_es_20261108.md), initial commit`1c0e1a54`, exact code/clock
clarification frozen **before returns** at`4740cdd2dbbd946140576fe5e1361acf52edca6e`.
[Evidence](../evidence/delgado_es_20261108.md) · [source paper review](delgado_7323419_review.md).
Code: [replay](../../../analysis/codex_delgado_es.py) · [12synthetic checks](../test_delgado_es.py) ·
[report renderer](../../../analysis/codex_delgado_es_report.py).
Outputs: [complete JSON/hash manifest](../../../analysis/outputs/codex_delgado_es/design/summary.json),
`analysis/outputs/codex_delgado_es/design/*_daily.csv`, `*_trades.csv`, `*_cap_breaches.json`.
Date: November8,2026(America/Los_Angeles). Independent review pending.
New financial definitions:3(BASE,SHADOW,CANDIDATE); shadow is mechanical/nonselectable, no winner search.
Known multiplicity lower bound:439;tbar3.686, including80source alternatives.

## Rule as tested

ES futures price/volume on close-stamped CT minute bars, using the existingGrid24cache. No SPY/ES÷10
price or share-cost conversion. BASE uses14prior normal-session same-clock mean absolute open movement,
gap-aware bands and typical-price cumulative-volume VWAP. At09:00–14:30CT half hours, enter beyond both
band and VWAP. Long exits on close<=max(upper,VWAP); short exits on close>=min(lower,VWAP).
Reversals close and reopen with both legs charged. Exits are checkpoint markets, not intraminute stops.

Candidate follows the source's frozen long1.3/short1.6band multipliers, short size.75, relative-volume size
clip(.5,1.5), band-binding size.7and previous30known SHADOW-day performance size.9/1.1. SHADOW is the
same candidate without that performance overlay. No parameter/side/calendar/market search followed results.

Base exposure min(4,.02/prior14daily-returnSD) times$100,000initial and subsequent modeled day-startNAV.
All multipliers precede the final requested4xcap. Whole ES lots round toward zero, using decision-close price;
entry quantity is not chosen with the future fill-open. Actual order size in this run was1–3EScontracts; some
small targets round to zero, particularly under candidate discounts. This discrete effect is part of this tested
implementation. It does not preserve the smooth fractional-share sizing of SPY. A microcontract study would
need a separate frozen sizing/cost/launch-date protocol rather than dividing these returns by10.

Market fills use the next observed native minute open with one adverse.25point tick/side. ES$50/point;
commission$5/roundtrip/lot, so ordinary total modeled cost$30/roundtrip/lot. Fees are stated research
assumptions, not verified historical broker statements. No native MES trades before its launch are invented.
Normal flatten decision14:59CTfills15:00close-stamped minute open; early sessions11:59→12:00.
No broker margin, cash interest or native quarterly roll ledger is inferred from the notional guard.

## Design results:2018–22only

The tables use **1,257complete days out of1,259cash-calendar days**. They retain real zero-trade known days.
Two days are unknown:2020-11-30absent, and2022-01-24with a held-price gap. Price and volume are never
forward/back-filled. Once current cumulativeVWAPis incomplete, new entries stop; held positions close on
the first subsequently observed open and remain flagged. The gapped trade is excluded from complete-day
statistics, retained in the raw ledger/bridge below. This is conditional observed-data reconstruction, not a
complete executable financial history. The source's2007–24or2000–26SPYperformance is not reproduced.

|Definition|Complete-day net|Daily-return Sharpe|Daily-return t|Daily maxDD|Return DSR|Extra-tick fixed-fill stress net|
|---|---:|---:|---:|---:|---:|---:|
|base|$107,475.00|1.281|2.860|$16,420.00|0.432|$65,850.00|
|shadow|$31,280.00|0.796|1.777|$13,667.50|0.079|$18,180.00|
|candidate|$25,517.50|0.663|1.481|$15,330.00|0.044|$12,792.50|

Daily-return Sharpe/t use each day's modeled startNAV, as capital compounds. Dollar-P&L Sharpe below is
a different statistic. Drawdown is the closed daily dollar path, with initialNAV included as a peak; it does not
measure intraday margin needs or worst open loss. DSR is a historical selection correction, not future success.
No candidate is selected: full candidate failed. The profitable baseline was a comparator, not a replacement
winner; its DSR also falls below.95and its existing family/coverage concerns remain.

|Definition|Side|Trades|Win|Net|Mean/trade|Mean net/ESlot/trade|Trade t|Dollar Sharpe|Sortino|PF|Calmar|Ulcer%|Daily DD|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|base|whole|964|38.2%|$107,475.00|$111.49|$75.68|2.691|1.205|2.218|1.318|1.312|2.739|$16,420.00|
|base|long|490|40.8%|$49,545.00|$101.11|$75.92|2.225|1.014|1.776|1.352|0.949|3.993|$10,462.50|
|base|short|474|35.4%|$57,930.00|$122.22|$75.43|1.746|0.780|1.568|1.294|0.757|3.896|$15,332.50|
|shadow|whole|405|41.0%|$31,280.00|$77.23|$62.38|1.640|0.742|1.504|1.319|0.459|4.279|$13,667.50|
|shadow|long|224|42.4%|$6,455.00|$28.82|$21.62|0.647|0.285|0.455|1.139|0.216|2.626|$5,980.00|
|shadow|short|181|39.2%|$24,825.00|$137.15|$112.82|1.528|0.699|1.645|1.484|0.317|5.164|$15,680.00|
|candidate|whole|388|39.9%|$25,517.50|$65.77|$54.47|1.360|0.612|1.221|1.267|0.334|4.755|$15,330.00|
|candidate|long|211|41.7%|$9,202.50|$43.61|$28.41|0.955|0.420|0.731|1.221|0.387|2.005|$4,772.50|
|candidate|short|177|37.9%|$16,315.00|$92.18|$85.54|1.012|0.460|0.985|1.302|0.184|6.631|$17,817.50|

Side rows are slices of the same joint strategy, not newly selected long-only/short-only replays. Dollars are
actual modeled whole-ES quantities, not perNQ. Net/ESlot/trade averages each trade's normalized net; it is
not a fixed-one-contract equity curve or a claim of equivalent MES fills.

|Year|BASEnet|CANDIDATEnet|Candidate long|Candidate short|Candidate trades|
|---|---:|---:|---:|---:|---:|
|2018|$27,932.50|$8,295.00|$-1,755.00|$10,050.00|108|
|2019|$3,827.50|$5,382.50|$2,742.50|$2,640.00|103|
|2020|$29,990.00|$11,492.50|$-1,750.00|$13,242.50|45|
|2021|$24,532.50|$-3,967.50|$8,770.00|$-12,737.50|115|
|2022|$21,192.50|$4,315.00|$1,195.00|$3,120.00|17|

## Gross/net bridge, missing paths and risk

|Definition|Complete gross|Slippage|Commission|Complete net|All observed-endpoint net|Flagged-day bridge|Unknown days|Unknown trades|Fill/marked cap flags|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|base|$157,425.00|$41,625.00|$8,325.00|$107,475.00|$107,232.50|$-242.50|2|1|3|
|shadow|$47,000.00|$13,100.00|$2,620.00|$31,280.00|$30,800.00|$-480.00|2|1|0|
|candidate|$40,787.50|$12,725.00|$2,545.00|$25,517.50|$25,275.00|$-242.50|2|1|0|

Every observed endpoint trade satisfies gross−slippage−commission=net, and observed closed trade totals
equal observed daily endpoint totals. Excluded unknown-path returns are NaN, never zero-return evidence.
The absent day's observed cash bridge0does not establish that a real strategy would have stayed flat.
The observed endpoint path, including the flagged known entry/exit endpoints, updates later modeled sizing;
this is another reason the capital path is conditional rather than independently certified.

Pre-return audit found10cash sessions with missing minutes in2017–Oct2022, including2020halt periods.
Other gaps can occur while flat and causally suppress entries; their missing prices are not invented. Missing
2020-11-30blocks subsequent adjacent-close volatility windows rather than bridging the missing session.
The cache has continuous ES prices/volume; historical contract IDs, roll adjustments and execution at native
contract prices remain unverified. Source covariance/flow interpretation is not a measured forced ES order.

The requested4xnotional cap does not guarantee actual marked exposure stays below4through a gap/loss.
BASEhas3fill/mark cap flags; candidate/shadow0in this run. These flags are retained, never retrospectively
resized with future prices. Final targets and actual exposure/cash paths are distinct. Broker margin feasibility
and smaller personal-account affordability were not established by this$100kreference reconstruction.

## Frozen gates and stop

|Criterion|Outcome|
|---|---|
|at_least_300_trades|PASS|
|at_least_95pct_days_known|PASS|
|positive_net|PASS|
|positive_stress|PASS|
|four_positive_years|PASS|
|daily_return_t_at_least_2|FAIL|
|trade_t_at_least_2|FAIL|
|net_dd_improves_10pct|FAIL|
|retains_70pct_baseline_net|FAIL|

The candidate's trade t1.360and return t1.481are below2; it retains only about24%of BASEnet and its
net/drawdown ratio is substantially worse. Positive profit and four positive years do not overcome those
failures. The source's overlays did not transfer beneficially to this whole-ES implementation.

Following the committed stop rule, no new2023+calculation, bootstrap, placebo, random-drop or account
simulation ran. Past2023+ES/NQstudies remain prior evidence, not newly obtained validation. No rescue
variant, threshold change, favorable-side selection or shadow promotion. Twelve synthetic causality/fill/
rounding/cost checks passed before returns; these complement rather than replace the historical result.

## All five account homes

|Home|Verdict|BASE/ADD/REPLACE/EMPTY|
|---|---|---|
|Personal|No place earned: candidate fails design; capital/margin/coverage unverified|Not run after failed gate|
|50Kevaluation|No place earned; source-reference sizing is not an Apex account model|Not run|
|150Kevaluation|No place earned; candidate fails same design gate|Not run|
|50Kfunded|No place earned; no payout/risk improvement established|Not run|
|150Kfunded|No place earned; not inferred from50K|Not run|

No MultiCharts strategy was written; source/continuous-price/fill and native margin parity remain unverified.
Tell Claude: review `agents/codex/results/delgado_es_20261108.md`; the requested ES adaptation was actually
tested, made positive conditional design profit, but its selected overlays substantially underperform BASE.

Reproduce original design with `python3 analysis/codex_delgado_es.py --stage design` at the frozen code
commit. Rebuild this report without returns: `python3 analysis/codex_delgado_es_report.py`.
