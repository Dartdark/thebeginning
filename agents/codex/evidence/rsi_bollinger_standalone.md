# Uploaded RSI/Bollinger, gold and NQ: TEST — bounded user-requested diagnostic

Summary: User authorized a separate GC/NQ screen and supplied the matching hourly/four-hour video transcript.
Fixed-contract diagnostic will isolate signals; it will not reproduce the crypto compounded sizing curve.
Source risk is not reliably 3%; the video confirms fivefold sizing was added for demonstration after results.
The new frozen plan defines causal candles, fill-time brackets, conservative limits and an explicit warm-up.
Return trials at this amendment: zero; TEST authorizes only the bounded design screen, not live use.

Source: [supplied code](../inputs/MeanReversionRSI.py); current official sizing helper pinned in
[`jesse_rsi_audit/SOURCE.md`](../inputs/jesse_rsi_audit/SOURCE.md).
Audit scope: `agents/codex/plans/rsi_bollinger_source_audit.md`, **ec70219**, amended **55528ab** for both markets.
Reproducer: `analysis/codex_rsi_bollinger_source_audit.py`; outputs:
`analysis/outputs/codex_rsi_bollinger_source_audit/`. These are synthetic quantities and date/time metadata only.

## 1. Who trades, and what causes the trade?

The rule hypothesizes a temporary pullback within a persistent higher-timeframe trend. It identifies no forced
participant, mandate, observed inventory demand or independent flow data. User-requested source inspection is
justified, but this is not evidence of an economic edge or a new forced-flow candidate.

## 2. Direction, size and timing before entry

Higher-timeframe RSI and Supertrend plus ADX gate direction; a long waits at the lower current-timeframe Bollinger
Band, and a short at the upper band. A six-ATR stop distance feeds Jesse's sizing helper; returned units are then
multiplied by five. On fill, the stop uses the then-current ATR and target uses the then-current opposite band.
The class has no trailing or maximum-holding-time update. Pending entries cancel at the next strategy check.

The supplied class sets four-hour indicator input only. The user selected hourly entries and both markets in chat;
route, provider, Jesse version, timezone/aggregation, leverage and account configuration are still external inputs.
Five times the calculated units is not a leverage adjustment that preserves stop risk. Available margin is also
not necessarily the account's equity. Exact sizing depends on the helper cap, fees and changes before fill.

## 3. Does the flow reach the traded contract?

There is no measured external flow. The proposed tests would use GC/MGC and NQ/MNQ directly. Jesse base-asset
quantities cannot be copied straight into CME contracts: stop distance must be translated using contract point
value, integer/micro quantity constraints, commissions and margin. No funding or roll assumptions are resolved
by setting a generic framework's mode to futures.

## 4. Data and information beyond price

No additional information independent of prices is used. The metadata-only audit finds ten GC annual files with
dates from 2017-11-30 to 2026-10-13; nine NQ daytime files from 2018-01-02 to 2026-10-09; ten NQ overnight files
from 2017-12-01 to 2026-10-09. Both have early-morning and evening observations. Counts are file metadata, not
proof of complete sessions or a sufficiently complete warm-up. All historical price/return fields stayed unread.

`Grid24` supports these file sets, but uses Central close-stamped bars. Jesse's timestamp/aggregation and the
partly formed versus completed four-hour candle available at each hourly decision must be matched explicitly.
Check roll adjustments/expiry, missing bars, DST and hours against the actual intended futures series before a
multi-day replay. The original author's asset/data source and framework version remain unknown.

## 5. Costs and portfolio gaps

No cost-clearing edge has been measured. Use actual futures commission, spread/slippage and contract-roll costs;
do not transplant the video's percent-fee assumption. A personal account permits multi-day holds but still needs
adequate margin and capital for adverse moves. No occupancy filter was applied. NQ longs can overlap the existing
long exposure; gold is not assumed to diversify it merely because it is another market.

## 6. Power

Historical signal frequency, filled-trade count, trade SD and gross edge are unknown. No numerical power pass is
claimed. The metadata file count is not the number of strategy trades. A later no-return signal/eligibility audit,
under a frozen executable rule, must establish support and a plausible `2 × SD / sqrt(effective n)` hurdle before
a return screen. No historical rule or opposite-direction variants were selected here.

## 7. Already tested and falsifiers

Related catalogue entries include generic Bollinger reversals (`analysis/bollinger_reversal_test.py`), ES mean
reversion (`analysis/es_mean_reversion_test.py`), RSI-based overnight buying, and the NarangBlackBox hourly
trend-filtered Bollinger idea. Their failures or weak results are context, not a test of this exact rule on GC/NQ.
The pasted class also differs from the video's Donchian breakout with a trailing exit; none of its reported
performance can be assigned to this source.

Falsifiers for a future test include no conditional return after costs, too few actual limit fills, dependence on
unexecutable band touches, profit dominated by roll jumps, or sensitivity to unavailable four-hour information.

## 8. Failure and diversification

Trend filters can remain strong while a pullback becomes a persistent reversal. Six-ATR stops can be wide relative
to the opposite-band target; risk/reward is not fixed. Passive entry exposure brings adverse selection and missed
fills. Later target/stop touches require minute-level sequencing and fill assumptions, including overnight gaps.
The code supplies no hedge. Market shocks, synchronized losses and a margin call can occur before any hoped-for
rebound or diversification benefit. Neither portfolio correlations nor concurrent contract exposure were measured.

## Decision

**TEST, diagnostic only**, following the user's explicit request and supplied mean-reversion transcript.
The original source-audit limitations above remain part of the record. The performance plan
`agents/codex/plans/rsi_bollinger_screen.md` now fixes the futures mapping and tests only fixed-contract signals,
with two execution variants on each of two markets. It does not claim original engine/crypto parity or solve
unknown roll provenance. Reject on the cheap design gate; do not optimize or silently substitute a sizing rule.

## Completed screen — stop

The preregistered screen is now complete: four market/execution trials, no parameter search. GC loses money;
NQ is positive with only 24 trades and t 0.76. Both fail the frozen support and t gates. See
[`rsi_bollinger_screen.md`](../results/rsi_bollinger_screen.md). Do not advance these tested versions or open
2023+ after this failed gate. The TEST decision above records eligibility before the screen, not a live verdict.
