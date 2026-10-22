# RSI/Bollinger source audit: WATCH — sizing defects; performance remains untested

Summary: Checked the pasted strategy separately; user selected both gold and NQ with hourly/four-hour inputs.
Synthetic $10,000 long cases risk 3%, 7.5% or 15% of input margin; one ATR-change case reaches 30%.
Undefined `bbw` and non-frozen ATR at fill are confirmed source issues; these figures are not historical trades.
Owned GC and NQ files include overnight observations, but futures-unit/candle/fill parity remains unresolved.
Do not trade this version. Audit complete; return trials, strategy backtests and live changes: zero.

Plan: `agents/codex/plans/rsi_bollinger_source_audit.md`, **ec70219**, amended **55528ab**.
Evidence: [`rsi_bollinger_standalone.md`](../evidence/rsi_bollinger_standalone.md).
Script: `analysis/codex_rsi_bollinger_source_audit.py`.
Output: `analysis/outputs/codex_rsi_bollinger_source_audit/`. Return trials: **0**.

## Rule (as checked)

Buy the lower Bollinger Band when four-hour RSI >70, price > four-hour Supertrend line, current ADX >20 and
four-hour ADX >40. Mirror for shorts with RSI <30. The source calls Jesse's 3% sizing helper then multiplies units
by five; on fill it sets a six-current-ATR stop and the opposite-band target. No trailing stop or time exit is
implemented. Canceling unfilled entries at the next strategy check is expected Jesse behavior, not a defect.

The [original class](../inputs/MeanReversionRSI.py) is preserved without behavioral changes. It is not the video's
Donchian/trailing-stop strategy. No historical profit, Sharpe or video result is attributed to it.

## Results — synthetic method checks and date/time metadata

The audit executes the original class methods with declared, constant synthetic indicator fixtures, not Jesse's
engine. Three official sizing helpers are extracted from [Jesse commit 9a3ebe0](https://github.com/jesse-ai/jesse/blob/9a3ebe075d9d0af5f012f921f46c2286f234af68/jesse/utils.py).
Fees are zero and the precision function is a disclosed floor stub. These examples represent generic framework
units; they are not CME contracts, historical scenarios, expected losses, maximum losses or account forecasts.

Long fixture: input margin $10,000, limit/fill price 2,000, band target 2,200. Quantity is 25 units in each case:

| ATR at submission | ATR at fill | Stop distance | Nominal loss at stop | % of input margin |
|---:|---:|---:|---:|---:|
| 10 | 10 | 60 | $1,500 | 15.0% |
| 5 | 5 | 30 | $750 | 7.5% |
| 2 | 2 | 12 | $300 | 3.0% |
| 10 | 20 | 120 | $3,000 | 30.0% |

The helper caps notional size before `qty*5`, so saying every trade risks 15% would be wrong. Short fixtures use
entry 2,200 and show the same multiplier/cap issue; their full outputs are in `synthetic_sizing.csv`.
Available margin can differ from equity, and actual loss also depends on gaps, fees, liquidation and fills.

| Finding | Severity / implication |
|---|---|
| `qty*5` after the helper | Critical sizing discrepancy: multiplying units raises exposure, rather than preserving the computed risk under leverage |
| ATR evaluated again in `on_open_position()` | Actual initial stop distance can differ from the one used to size the pending order; a policy must be explicit before a faithful replay |
| `self.bbw` is undefined | `watch_list()` raises `AttributeError` in the method fixture; the checked Jesse base class does not supply this property. A run that never calls the watch list may still proceed |
| No `update_position()` override | Initial exits remain unchanged by this class; no trailing stop, refreshed target or maximum hold is present |
| External configuration / contract mapping | Entry timeframe, symbol, route, hours, leverage and commission are not established by the class alone. User selected both markets and 1h/4h in chat |

Date/time-only inspection, reading no OHLC or volume fields:

| File group | Annual files | First observed date | Last observed date | Overnight clock observations? |
|---|---:|---|---|---|
| GC | 10 | 2017-11-30 | 2026-10-13 | Yes, before 08:00 and from 17:00 |
| NQ daytime | 9 | 2018-01-02 | 2026-10-09 | No, as expected for the daytime export |
| NQ overnight | 10 | 2017-12-01 | 2026-10-09 | Yes, before 08:00 and from 17:00 |

These are observed boundaries, not a completeness, roll-adjustment or session audit. `Grid24` already supports
the relevant file sets; no cache or new price engine was built. Contract sizes and Central close-stamped bar
aggregation must not be substituted for Jesse base-asset quantities and UTC candle semantics without disclosure.

## Placebos and account level

Not run. No historical trade list exists for this source audit. Metrics by year, long/short performance, bootstrap
intervals and funded-account results are not applicable. A personal account's lack of an Apex trail makes multi-day
holds possible, but provides no evidence of profitability or protection from losses or margin calls.

## What could make this wrong

The author may have used an older Jesse version or different configuration. The pin records what was checked,
not proof of the author's environment. Synthetic methods do not establish fill ordering, indicator math or live
callbacks. The floor helper is intentionally minimal and not a complete exchange precision/margin implementation.
Four-hour availability, DST/aggregation, roll gaps, pending-order lifetime and cost assumptions need explicit
parity checks before performance can be tested credibly. No risk correction was silently substituted.

## Differences between MultiCharts code and the test

No MultiCharts code or historical strategy test was written. No live, VPS, broker, funded-roster or strategy files
were changed. The preserved input is research material only; it must not be placed on a live chart.

Reproduce: `/workspace/venvs/thebeginning/bin/python analysis/codex_rsi_bollinger_source_audit.py`.

Publication note: the plan commits cited above are local preregistration commits. Git HTTPS authentication failed
after the audit commit; the connected GitHub service is used to append the same files to `codex/work`. Local
commits are retained without reset or rewrite; their hashes need not be objects on the remote branch.

Tell Claude: review `agents/codex/results/rsi_bollinger_source_audit.md`; both markets selected, source-risk audit
only, NEEDS DATA / execution specification, no return trials and no performance verdict.
