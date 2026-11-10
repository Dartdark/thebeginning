# Gold crowded-long liquidation: HYPOTHESIS / NEEDS DATA

Summary: User asks to explain gold's movers and build a hypothesis before testing.
Propose testing whether published managed-money crowding amplifies subsequent intraday downside breaks.
Positioning is a state proxy, not observed current leverage, stops or compelled order flow.
Owned GC prices are present; inspected local COT archives are Legacy, not the required disaggregated panel.
No economic definition has been tested and no return/preregistration/plan adoption is claimed.

Source map: [gold_market_hypothesis_20261110.md](../results/gold_market_hypothesis_20261110.md).
Return trials: **0 new**. Prior COT, gold-clock, rates/dollar and breakout failures remain counted.

## 1. Participant and proposed pressure

Managed money includes CTAs, CPOs and certain funds in CFTC's classification. Leveraged trend-following
positions can face stop, volatility, liquidity or risk-budget constraints after an adverse move. Hypothesis:
when that category is already unusually net long, a downside break can produce additional selling over the
next intraday interval. No institution's position, actual leverage, private stop or forced quantity is observed.
CFTC categories describe traders, not the purpose or aggressiveness of every trade.

## 2. Direction and clocks

Candidate direction is short after a predeclared US-morning downside trigger; never short solely because
crowding is high. Use only a gold report already publicly released before the decision. Tuesday position
dates are not availability dates; Friday at 15:30 Eastern is a normal convention, not a sufficient historical
calendar during holidays/shutdowns/catch-up releases. A next-minute-open fill must follow the trigger close.

## 3. Transmission and independent input

Positions concern COMEX gold futures directly. Liquidating a long futures position involves selling,
but the current report cannot establish whether the holder will liquidate, how urgently or through which
instrument. No size/price-impact estimate can be inferred from net open interest alone. Weekly positions
add an independent input to the price trigger; changing an NQ rule's ticker would not establish this mechanism.

## 4. Required data and admission

- Gold disaggregated **futures-only** managed-money long/short/spreading, total open interest, exact contract
  market identifier, observation dates and original publication/correction records. Official CFTC histories
  are publicly listed; the identified gold code must be reconciled with the source contract/name.
- Earlier published reports for any past-only crowding distribution; no full-history percentile. Three years
  of reference history, if chosen, would require 2015–17 warmup for a 2018 design start.
- Owned GC minute OHLCV with declared timezone/bar labels, dated contract/roll mapping and complete held paths;
  MGC execution/cost assumptions require their own unit conversion and stress.
- Source clock/field QA precedes a no-return event/power census. Legacy non-commercial data is not substituted
  for Managed Money. Unknown publication windows remain unknown; no mechanical Tuesday→Friday backdating.

## 5. Costs, holding period and book

Proposed intraday horizon: about 30 minutes after a downside break, with one position/day, entry-bar protection,
whole-MGC risk cap and a hard time exit. These are draft design choices; exact trigger/window/crowding cut,
stop/exit and risk budget must be frozen in a separate return preregistration before outcomes.
GC is 100 oz and MGC 10 oz; a $1/oz move is $10 per MGC. Do not scale NQ fees to gold or claim a guaranteed stop loss.
Gold/rates/dollar shocks can coincide with NQ losses. A gold short could offset some such paths, but actual
strategy correlation, loss timing and evaluation contribution are unmeasured.

## 6. Power before returns

No admitted event count, independent-week count or estimated edge/SD exists yet. Crowding clusters across
days; treating daily entries as independent would exaggerate evidence. An extreme-position filter can
also be too sparse to help a 30-day evaluation. Census frequency and cost hurdle before testing returns.

## 7. Prior evidence and decisive falsifiers

Do not reopen failed NQ/ES COT reversal/dealer-rank definitions or the source-only 52-week-high/low COT paper.
That review found little gold market-timing evidence. The proposed **interaction** of disaggregated money
manager crowding with a fixed intraday trigger is a new hypothesis to falsify, not a validated inference from it.
Generic gold auction follow/fade, first-notice liquidation and rates/dollar catch-up have substantial prior
negative evidence. No related thresholds, holding periods or direction may be rescued after validation.

Compare the identical downside trigger without crowding, matched volatility/time controls and random kept
weeks chosen with equal selection effort. Require incremental total net and account value after native costs,
not a higher win rate/per-trade average from deleting profitable opportunities. Failure of the crowding
interaction, disappearance under proper publication lag, dependence on a few crisis weeks, or insufficient
30-day opportunities refutes the intended case.

## 8. Failure and next gate

Fund longs may be justified, stale or already unwound; shorts can be squeezed; quotes can gap; dealer/physical
buying can absorb selling; common macro shocks can dominate. More volatility alone is not expected short profit.
Next: audit a genuinely disaggregated gold sample and at least one exceptional release week, then count eligible
events without returns. Only a TEST update and committed bounded rule/code can authorize subsequent return work.
This completes the requested hypothesis stage; it is not a strategy recommendation or a claim of background work.
