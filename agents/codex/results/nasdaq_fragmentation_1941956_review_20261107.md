# NASDAQ fragmentation 1993–2010: execution reference, no trading strategy

Summary: Historical stock-market venue competition, not an NQ directional signal.
NASDAQ's reported execution share falls from 100% to 37%; costs and execution delays generally fall over time.
Annual regression signs vary; the paper's execution-speed interpretation conflicts with its seconds-based dependent variable.
Cancellation percentages describe reported order outcomes, not proof of spoofing or our probability of filling.
Retain the measurement lessons only; no return trial, allocation or live change follows.

Source: Battalio, Egginton, Van Ness and Van Ness, *Exchange Entrances, Mergers and the Evolution of Order Flow
on NASDAQ 1993–2010*, SSRN1941956, draft October 5, 2011. Review date November 7, 2026, America/Los_Angeles.
[Owned PDF](../inputs/nasdaq_fragmentation_1941956/paper.pdf), 34 pages,
[text](../inputs/nasdaq_fragmentation_1941956/paper.txt).
Scope: main narrative and key tables reviewed, Tables 10/12 visually inspected; chart-only pages29–34 not
independently audited. No original-data replication or independent verification of cited studies.
[Audit code](../../../analysis/codex_nasdaq_fragmentation_1941956_audit.py),
[source receipt/printed coefficients](../../../analysis/outputs/codex_nasdaq_fragmentation_1941956/source_audit.json).

## Five questions

1. **What is it about?** How volume, trade size, venue shares, effective spreads, execution delay and cancellations
   evolved for NASDAQ-listed stocks during 1993–2010, including venue entry and mergers. Uses CRSP/TAQ and
   Rule605/DASH5 reports; execution-quality analysis covers 2002–2010. NASDAQ-listed stocks are not NQ futures.
2. **What does it find?** Reported NASDAQ share falls from 100% in 1993 to 37% in 2010, while activity rises and
   average trade size falls. Entry/merger windows do not show statistically significant changes in total volume;
   volatility responses are mixed. Off-NASDAQ share is often associated with lower effective spreads, but not in
   every year. Cancellation rates are high at several reporting venues. The strong abstract claim about faster
   execution must be qualified by the sign/unit conflict described below. These are source results, not our replication.
3. **Why does it make money, if it does?** No strategy P&L is shown. Venue competition could lower execution
   costs, but historical cost associations do not identify a directional premium or guarantee attainable savings.
   High cancellation rates do not establish a profitable signal or an opportunity we can capture.
4. **Can we build on it?** Yes as execution-measurement guidance: distinguish venue count from actual flow
   distribution, historical trend from conditional association, and seconds of delay from a measure of speed.
   Preserve data coverage and reporting-code changes. For an independently justified future execution study, first
   reconcile order types, receipt/fill clocks, partials, cancels and the report denominator. Current minute-bar
   data cannot reproduce a multi-venue stock-order study; no new acquisition or backtest is justified here.
5. **Can a strategy code be made?** No complete trading strategy is specified. An offline venue/cost/delay
   diagnostic is codeable with matched historical stock trade/quote records, point-in-time listings, venue-code
   mappings and reporting metadata. A native futures execution study instead needs contract-specific quote/order
   lifecycle data. The paper supplies no directional entry, holding period, stop, exit or sizing rule; writing a
   cancellation-based NQ strategy would invent a new hypothesis rather than implement this source.

## Findings and necessary qualifications

| Source | Reported evidence | Limit |
|---|---|---|
| Table 2(a), p16 | NASDAQ share100.0% in 1993,37.0% in 2010 | Reported historical trade-volume allocation, not today's shares; reporting facilities are not necessarily economic execution venues. |
| Tables 4–7, pp19–22 | Entry/merger volume changes not significant; mixed volatility outcomes | Failure to reject is not proof of no effect. Thirty-day before/after windows do not isolate all concurrent reforms, technology or selection effects. |
| Table 9, p24 | Fragmentation/spread coefficient negative in 2002–06 and2008–09, positive in 2007 and2010 | Negative in 2002/2006 is not statistically significant at printed thresholds; general cost association is not universal or causal. Venue-count coefficient also changes sign. |
| Table 10, p25 | Fragmentation coefficient negative in 2002–06, positive in 2007–10 | Dependent variable is seconds from receipt to execution: negative means shorter delay, positive means longer delay. The narrative reverses this interpretation. |
| Table 12, p27 | 2010 reported cancellation percentages NASD82.8%, NASDAQ16.3%, ARCA92.1%, AMEX52.8%, ISE97.0%, BATS40.8% | Venue/stock averages from reporting data, not a universal cancellation probability, quote-message rate or evidence of manipulation. |

### Execution-speed sign audit

The rendered [Table 10](../inputs/nasdaq_fragmentation_1941956/table10.png) explicitly defines “Execution Speed”
as the average **number of seconds** from order receipt to execution. Fragmentation coefficients range from
−98.78 in 2002 to−136.14 in 2006, then+123.12 in 2007 to+198.80 in 2010 (intermediate years in the receipt).
Holding the other regressors fixed, the early negative signs imply shorter delay; later positive signs imply
longer delay. §III.B says the opposite in terms of speed. Unless an unreported variable transformation is supplied,
the printed definition and narrative cannot both be used as stated. Do not propagate the abstract's conclusion
as a verified universal relationship.

Table 8's broad historical fall in delays is a different statement from Table 10's within-year conditional slope;
they can coexist. Neither provides a latency assumption for today's CME market orders. The aggregate stock
report averages are not network round-trip latency and are not our observed micro-contract fill delay.

### Cancellations and coverage

[Table 12](../inputs/nasdaq_fragmentation_1941956/table12.png) visually confirms the reported percentages.
Its caption mentions counts and percentage panels, but the displayed page supplies only the percentage table.
Do not invent the missing counts. Missing venue/year cells and uneven reporting coverage cannot be treated as
zero activity. NASDAQ's 2010 percentage is far below ARCA/ISE; “all venues increasingly cancel” is too broad.

The authors speculate about high-frequency trading and “false liquidity” but leave the explanation to future
research. Aggregate cancellation outcomes cannot identify intent, cancelled displayed depth, queue position,
time priority, adverse selection or the fill probability of our order. Rule605/DASH5 coverage and order/size
categories need reconciliation before inferring whole-market message cancellation rates. Their reporting venue
labels are not a complete map of the underlying matching locations or liquidity providers.

## Project disposition

**EXECUTION REFERENCE / DON'T TEST as standalone alpha.** No complete economic trading definition qualifies;
no evidence sheet proceeds to TEST, return trial, holdout, account simulation or PowerLanguage code was run.
No Sharpe, profit factor, drawdown or payout result exists to report. Source integrity and transcription/sign
interpretation were checked; original regressions and execution savings remain independently unverified.

Retained as a follow-up to order-lifecycle reference E03 in
[EXECUTION_REFERENCES.md](../EXECUTION_REFERENCES.md). Existing reporting/clock/data cautions apply; no new
promising-strategy queue entry or data-register request is warranted after checking existing research.
The stock-market evidence does not reopen rejected NQ patterns, change native fees or alter current allocations.

For Claude: `agents/codex/results/nasdaq_fragmentation_1941956_review_20261107.md`.
