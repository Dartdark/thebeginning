# Corrected TQQQ/LQQ3 reconstruction: WATCH — NEEDS DATA

Summary: Built and checked corrected research signal components after the user's new instruction.
All28synthetic checks pass; this establishes component behavior, not profitable trading.
Three free Yahoo history probes hit proxy403; no synchronized historical inputs were acquired.
No historical backtest, account comparison or deployable strategy is claimed. Original source rejection stands.

Plan: [reconstruction](../plans/pair7065278_reconstruction_20261108.md), committed before execution at
`22e7fc4e25ca61c6fca9e50ded258d1cd574075c`.
Script: [components](../../../analysis/codex_pair7065278_components_20261108.py),
[checks](../../../analysis/codex_pair7065278_component_checks_20261108.py).
Output: [28checks](../../../analysis/outputs/codex_pair7065278_reconstruction_20261108/components.json).
Trials run:0economic trials; one provisional corrected signal definition,28synthetic component assertions.

## Rule (as tested)

Research components only: validate native bid/ask and event/receipt clocks, convert LQQ3 from explicit
GBX/GBP into USD, calculate past-only20-observation EMA/sample-standard-deviation z-scores and desired
pair direction. Proposed decision15:00UTC avoids the original ordinary summer close mismatch; actual
holiday/half-day calendar admission is externally required. Quotes must be received before decision and
<=60seconds old. Entry bands±0.75, directional exit±0.25 with overshoot exits and no instant reversal.
Unknown units, crossed/nonfinite/nonpositive quotes, future/stale information and unavailable scores reject.

This is a substantive new clock/quote/exit specification, **not an exact source reproduction**. It is not a
complete backtester: integer sizing, execution on later quotes, borrow, funding, cash, collateral, calendar
provenance, corporate actions and position/fill reconciliation remain unimplemented pending inputs.
The validator's open-session boolean is a caller assertion, not independent calendar verification.
The score function accepts a clean sequence; it does not independently certify session gaps or source metadata.

## Results

| Stage | Result |
|---|---|
| Corrected component checks |28/28PASS|
| New free historical endpoint attempts |3; all proxy403|
| Matching historical input acquired |None|
| Historical economic trials |0|
| Net return, Sharpe, drawdown |Unavailable|
| Portfolio contribution |Not tested; not admitted|

Checks include preserving declared GBX499/501, GBP equivalence, information-clock ordering, zero dispersion,
indicator prefix invariance, warm-up, long/short directions and overshoot exits, plus winter/summer clock examples.
These invented fixtures are engineering checks, not simulated market performance or execution savings.

Owned `data/letf/TQQQ.csv` was inspected: its columns are daily NAV, shares outstanding and AUM. That is
useful fund information but not the native intraday quote history. No matching LQQ3/GBPUSD raw history was
found in the tracked data/input inventory. The original author workbook remains a derived later-only sample
with unrecoverable raw conversion provenance, so was not silently reused as a clean corrected dataset.

Free public Yahoo hourly requests for LQQ3.L, TQQQ and GBPUSD=X targeting design-period history returned
**proxy tunnel403**, not an authenticated provider finding that symbols/history do not exist. Exact requests
and errors: [receipts](../inputs/pair7065278_reconstruction_20261108/free_data_receipts.json).
Public discovery also found [daily adjusted LQQ3 prices](https://stockanalysis.com/quote/lon/LQQ3/history/),
[LSE historical products](https://www.londonstockexchange.com/equities-trading/market-data/historical-data-products)
and [subscription intraday history](https://www.barchart.com/stocks/quotes/LQQ3.LN/historical-download).
None supplies an admitted free, synchronized, available-at three-series archive from the inspected evidence.
Daily close histories are not substitutes; no paid service/account or bulk acquisition was used.
The previous Stooq browser-verification limitation was preserved rather than bypassed or repeatedly probed.

## Placebos and account level

Not earned. No2018–22design,2023+validation, by-year/side returns, matched placebos, BASE/ADD/REPLACE/EMPTY,
funded payouts or personal sizing recommendations. The multi-day equity/ETP pair is not eligible as written
for either50K/150Kevaluation or funded futures plan. Personal research remains conditional.

## Five paper-review questions: updated answers

1. **About:** cross-border mean reversion between leveraged Nasdaq products TQQQ and LQQ3.
2. **Findings:** author136.34%total return/Sharpe6.44remain unreplicated; our new result is28component checks,
   not a return. Original unit/clock/alpha rejection has not been reversed.
3. **Why money:** proposed convergence of similar exposures, not demonstrated forced flow or executable
   arbitrage; different product structures and costs can defeat the apparent spread.
4. **Build on it:** these corrected components are a start for personal research only. Need native paired
   quote/receipt/unit/calendar/action and borrow/cash evidence before economic admission. No queue promotion.
5. **Code feasible:** yes; research components now exist. A full economic engine requires the missing native
   execution/financing/capital specifications and a separate committed protocol before any returns.

## What could make this wrong

Free matching histories may exist elsewhere; these attempts do not establish impossibility. Even authentic
hourly OHLC would not alone certify simultaneous executable quotes, receipt latency, short availability or
funding costs. Synthetic prefix tests do not establish corporate-action adjustments or tradability.
No repairing metadata from price levels, interpolating intraday paths, changing the design dates to later-only
coverage or choosing cost/sizing assumptions from the already-seen source curve.

Smallest next check with genuinely new data: one native paired formation-to-later-fill/cash reconciliation,
including actual quote age, units/actions and financing. Then freeze the complete economic protocol and
assess coverage before running it. Independent verification pending. No MultiCharts or live code was written.
