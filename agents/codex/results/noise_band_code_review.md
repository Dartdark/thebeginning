# Uploaded noise-band CODE.txt: REJECT promotion on the supplied evidence

Summary: Keep the current plan; this source does not establish a profitable or useful replacement/addition.
Default sizing gives a $2,000 position stop, exhausting the nominal initial trail before costs; unchanged MNQ inputs imply a 500-point stop.
History sampling and open/close anchors depend on undeclared chart settings, and the exact-time flatten can be missed.
Related noise-band variants have already failed to improve earlier plan benches, but those are not results for this implementation.
No source repairs, strategy-return tests, simulations or live changes were made.

Scope: `agents/codex/plans/noise_band_code_source_review.md` (review record, not strategy-return preregistration).
Evidence: `agents/codex/evidence/noise_band_code.md` (NEEDS DATA).
Input: unchanged `agents/codex/inputs/noise_band_code/source.txt` (user's CODE.txt).
Script/output: `analysis/codex_noise_band_code_review.py`, `analysis/outputs/codex_noise_band_code_review/summary.json`.
New strategy-return trials / account simulations: **0 / 0**; original selection history unknown.
Context: Codex `743e520a5b368ebf64e1abf091d9f5ed50d1278f`; Claude `8f6b75cc1c6044f712c3ad5f1a774de60dd14859`.

## Rule and evidence boundary

The code follows closes outside gap-aware noise bands, using historical absolute moves from a date-based opening price.
It adds candle-direction gates, EMA/band exit thresholds, explicit reversal orders, a fixed dollar stop/target and daily
entry/large-loss counters. LongTrail/ShortTrail are recalculated thresholds, not explicitly ratcheted monotonic trails.
It is a price-based momentum variant. No independent flow estimate or forced participant order is supplied.

The file declares neither its instrument nor chart timeframe/session/timezone. Its multiplier default suggests NQ, but
that is an inference, not a supplied chart specification. There is no report, trade ledger, selection record or current-version
checker result. Actual profitability, yearly/side statistics, risk-adjusted metrics and account contribution are unknown.

## 1. Risk budget and instrument conversion are unsuitable for the current plan

Lines 6-9 and 72-107 use a nominal 50-point stop, $2,000 budget, input DollarPerPoint=20 and target at half the stop amount.
They produce **two contracts**, a **$2,000 position stop** and **$1,000 position target**. Stop/target dollar amounts are
position-wide under SetStopPosition; these are not per-contract dollar inputs.
[Official MultiCharts definition](https://www.multicharts.com/trading-software/index.php?title=SetStopPosition).

| Actual chart instrument | Unchanged contracts | Position stop / target | Effective stop / target points |
|---|---:|---:|---:|
| NQ, $20/point | 2 | $2,000 / $1,000 | 50 / 25 |
| MNQ, $2/point | 2 | $2,000 / $1,000 | 500 / 250 |

The source calculates from an input multiplier rather than the actual instrument BigPointValue. Moving to MNQ without
reconciling that input changes the point distances tenfold; it does **not** reduce the dollar stop. The $2,000 allowance
consumes the entire nominal trail before costs, adverse fills and other plan positions. Three nominal full stops would be
$6,000; a three-stop counter does not mean the account can survive to that counter, and external loss limits may intervene first.
No replacement risk number or instrument configuration is chosen here.

Built-in stop/target calls are made while flat whenever calculated quantity is valid (87-109). Unlike the prior GC upload,
there is no MarketPosition-only initialization branch here. Do not allege a blanket missing-entry-bar stop.
[MultiCharts built-in stop behavior](https://www.multicharts.com/trading-software/index.php?title=SetStopLoss).

## 2. LookbackDays can be observations rather than days

Lines 182-224 assign every eligible bar to a fifteen-minute bucket and read the last LookbackDays records. Lines 402-427
then append that bar's move. There is no per-date/per-slot insertion guard or restriction to one evaluation per bucket.

On aligned fifteen-minute bars, one record per slot/day is possible. On five-minute bars, 09:00, 09:05 and 09:10 all update
the same bucket. A nominal twenty-record history then spans roughly seven sessions and includes earlier observations from
the current day. The strategy is no longer a twenty-prior-day, same-time noise-band rule.

The audit script demonstrates this with invented observations, not historical prices: an initial twenty-record mean of 1%
becomes 1.1% at 09:05 after storing the current day's 09:00 move of 3%. This is **causal contamination of the intended daily
sample**, not demonstrated future-price leakage: the current bar is appended after the signal calculation.
The required chart interval and sampling convention must be specified before interpreting any backtest.

## 3. Session anchors and flattening need exact chart provenance

- Lines 120-126 set TodayOpen=Open and PrevClose=Close[1] when the **calendar date** changes. On RTH-only bars these
  can represent the regular open/prior close. On a full Globex chart they become midnight-area anchors; they do not
  explicitly select 08:30 or the prior regular-session close. EMA also uses all available chart bars. This is a confirmed
  configuration dependency, not a universal leak or proof that every chart is wrong.
- Lines 434-446 flatten only on **Time = 1430**. If that timestamp is missing because of an early close, data gap or
  misaligned interval, no fallback time exit exists. Ordinary signal exits are themselves gated to Time<=1430 (176-179),
  so later bars leave the dollar stop/target as the remaining exits and a position can carry. There is no holiday schedule
  or mandatory 15:59 fallback. This is incompatible with relying on the code alone for the plan's intraday requirement.
- A next-bar market exit generated at the 14:30 close can fill on the following tick around 14:30. Do not infer a mandatory
  14:45 fill merely because the chart might use fifteen-minute closing labels.

## 4. Counter and reversal findings: distinguish limitations from false bugs

PositionProfit(1) is **total realized currency P&L** for the latest closed position on MultiCharts. Comparing it with total
ActualStopDollars at line 139 has no inherent points/per-contract units mismatch.
[Official PositionProfit documentation](https://www.multicharts.com/trading-software/index.php?title=PositionProfit).
It classifies losses by amount rather than actual exit cause and checks only one latest position when TotalTrades rises;
multiple closes between calculations need a trace. TradesToday increments when entry orders are issued, not on confirmed
broker fills. These counters are not an account-wide daily loss limit or a guarantee against rejected orders.

Explicit exits plus opposite entries are redundant but not proven double sizing. MultiCharts prioritizes an opposite
entry that reverses the position; an incompatible leftover exit can then be discarded. Do not claim a confirmed double
fill from Sell+SellShort or BuyToCover+Buy alone.
[Official execution priority](https://www.multicharts.com/trading-software/index.php?title=How_Scripts_Work).

## 5. Existing family evidence and plan fit

The latest tier list already contains noise-area momentum and the Chuk noise-band variant. That later rule used different
history, RTH anchors, timing and VWAP exits. An earlier paired bench reported adding one MNQ lowered two-year payouts
from $12,035 to $11,812 and raised blown from 7.2% to 8.7%. Removing VB and adding noise-band gave $11,990 / 5.0% blown,
while simply leaving the VB slot empty gave $12,013 / 4.8%. The lower risk did not establish an incremental noise-band gain.

Those are **earlier rule/plan/cost results**, not an exact-version test or a current benchmark. In particular the old Chuk
script used $24.50 round-trip NQ cost, versus the latest builder convention $17.25 for two market/stop fills. Do not silently
treat those outputs as a rerun at today's convention. The saved rows and source commit are in this review's JSON output.

This upload differs in history cadence, calendar anchors, EMA/candle filters, brackets and reversals. Similarity suggests
possible shared momentum exposure with Vault Break/ONB/RS, not measured correlation. No new add/replace/empty-slot bench
is supplied. Prior related failures are a reason to demand clear incremental evidence, not a proof that this code loses.

## Decision and next evidence

**Keep the plan; do not add this source or substitute it for a current leg on the available evidence.** Source names and
positive family descriptions do not establish risk-adjusted returns. No new rank is assigned for Claude.

The smallest useful evidence is the exact instrument/timeframe/session/inputs plus the existing MultiCharts performance
report and timestamped trade list for this code. Confirm one-record-per-intended-day sampling, anchors, multiplier and
early-close/missing-flat-bar behavior before considering new returns. Any correction would be a separately frozen version,
with committed preregistration and trial counting before a new replication. Latest independent statistical gates and the
paired bootstrapped account comparisons still apply; no forward/live tracking was started here.

Validation: source defaults/anchors and synthetic risk/sampling examples checked by the audit script; independent read-only
subreviews checked code semantics and prior family context. No compile, original-engine parity, strategy-checker PASS,
price replay, account simulation, cache rebuild, source fix, live access or PR action occurred.
