# S03 Noise Area v2: prior research and implementation review

Summary: The time-of-day noise-band family is already researched here; S03 is not a new foundation.
Its incremental claim is the entry-fixed 0.4 × raw-sigma protective stop, compared with the identical S03 engine without it.
The closest prior family had weak recent evidence and failed the old funded addition/replacement bench; that does not settle this new stop variant.
The uploaded bulletin cannot establish code parity, tick execution, new holdout performance, or Apex account suitability.
No strategy returns, backtests, caches, ranking changes, live changes, commits or pushes were made in this review.

Scope: read-only source/prior review, with this result file as its sole write. Local checkout examined: `codex/work`, `1bab29f`.
The parent review must reconcile current remote instructions before treating this local context as current policy.
Source prose: `agents/codex/inputs/s03_noisearea/source_extracted.txt`, extracted from the uploaded HTML without executing its JavaScript.
All performance figures below are existing repository or bulletin claims, not newly reproduced results.

## Existing research

| Existing item | Evidence already recorded | Relationship to S03 |
|---|---|---|
| `TIER_LIST.md:64`, Noise-area momentum, long only, “Beat the Market” | PF 1.38–1.45; 9/9 positive years; 43% winners; VB replacement $4,100 versus $5,387 | The same time-of-day noise boundary and delayed band/VWAP exit family predates this upload. |
| `analysis/intraday_research.py:49`, `noise_momentum` | Prior-14-session same-clock mean absolute open-to-price return, max/min(open, prior RTH close), half-hour decisions, next-minute entry, check-only band/VWAP market exit | Closer to S03's check-only trail than the Chuk implementation. Important differences: this older code does not require entry VWAP confirmation; no raw-sigma protective stop; different early-close handling and flat execution. |
| `TIER_LIST.md:110`, Chuk 2026 SSRN 7609644; `analysis/noise_band_chuk_test.py` | C: $72/NQ per trade, daily t 2.6; 2023+ t 1.1; 2026 roughly −$16k. Existing old funded bench: +1 MNQ reduced two-year payouts $224 and raised blown accounts from 7.2% to 8.7%. | Same prior-14 same-minute mean absolute return boundary, VWAP confirmation and half-hour entry clock. Not an exact S03 replay: it uses five-minute intrabar trailing stops, no 0.4-sigma protective stop and an earlier close. |
| `analysis/noise_band_bench.py`, its saved output, and `LESSONS.md:21` | The lower failure rate from replacing VB was reproduced by leaving its slot empty; shorts were nearly uncorrelated with VB but economically flat since 2023. | Any future S03 addition/replacement comparison needs the empty-slot control and long/short evidence. Diversification does not follow from a low correlation alone. |
| `TIER_LIST.md:119`, Maroy 2025 exits on VB | VWAP/exit-band/ladder changes; Python-favoured VWAP exits were not confirmed in MultiCharts, because reentries altered the result. | Direct warning that changing an exit requires rebuilding the complete trading process. Applying S03's new stop only to a frozen v1 trade list is invalid. |
| `TIER_LIST.md:93`, Bridge VaultBreak v8 | Calendar high-low average band plus VWAP exit was slightly worse than v1. | Related VB revision, but not the same-clock noise estimator. |
| `TIER_LIST.md:311`, Concretum late-day seasonality | Recent weakening/reversal of late-day day-trend exposure, not a demonstrated change to every plan leg. | Supports examining S03's late-day trend exposure; it does not authorize cutting an exit or filtering trades after seeing the bulletin. |

The searches found the rules under “Beat the Market”, “noise-area”, “noise-band”, Zarattini and Chuk rather than a pre-existing S03/NoiseArea/NoiseBoundary file. ORB, VWAP always-in, and the Concretum fast-alpha execution overlay are separately tested ideas; those citations must not be presented as independent confirmations of this exact stop.

## What is incremental

S03's proposed estimator is

`sigma[d,t] = mean(abs(close[d-k,t] / RTH_open[d-k] - 1), k in previous 14 eligible completed sessions)`.

`upper[d,t] = max(RTH_open[d], prior_RTH_close[d]) * (1 + sigma[d,t])`; lower uses `min` and `1 - sigma`.
Here sigma is a mean absolute fractional return. It is not a standard deviation, ATR, or a dollar stop.

The new claim worth isolating is: on the otherwise identical S03 process, a protective stop at actual entry price minus/plus `0.4 * sigma_at_signal * signal_close` reduces harmful excursions while preserving enough trend-day profit to improve results and account survival. StopSigma zero is the necessary matched baseline. An ATR stop or VB's 75-point stop would test another hypothesis.

The bulletin's v1/v2 comparison claims only StopSigma differs. That is not the same claim as “S03 improves on the existing repository's Chuk strategy” or “S03 improves on Vault Break”. A causal comparison with either prior requires matching its data, costs, timing, holidays, reentries and exposure first.

| Rule | S03 bulletin | Existing Vault Break v1/SP |
|---|---|---|
| Anchor and noise | RTH open, prior RTH close, prior 14 sessions at the same minute | Midnight CT open plus 0.30 times prior 15 completed weekday calendar-date true ranges |
| VWAP | RTH-session confirmation and check-only exit | Midnight anchor, entry confirmation |
| Entry clock | 10:00–15:30 ET, every 30 minutes = 09:00–14:30 CT | 10:00 CT onward, before 14:30 CT |
| Side | Both, opposite signal reverses | Long only |
| Exit | Check-only trail; entry-fixed raw-sigma protective stop; next-bar after 16:00 ET | 40-point target/75-point stop; 14:30 CT close |
| Trade limit | Reentries and reversals described; no daily cap specified | Maximum three trades per day |
| Holidays | Skip scheduled holidays/early closes and mourning days | Earlier entry cutoff/flat times on designated half days |

The price-persistence story is shared with existing NQ momentum. The source does not identify a new forced counterparty flow or scheduled liquidity need that would make this a separate economic foundation.

## Point-in-time and selection checks

- **Shift history by one eligible session.** Computing a daily-by-clock table with `rolling(14).mean().shift(1)` is the intended chronology. Including the current day's later closes, a centered window, a current-day full-session statistic or the full-sample mean noise curve would leak future information.
- **Use the correct bar's open.** With close-stamped one-minute bars the 09:30 ET session opens at the open of the 09:31 ET bar, corresponding to 08:31 CT. The bar stamped 09:30 ET contains the preceding minute. Confirm the real signal's convention before asserting parity.
- **VWAP uses observations through the signal close only.** Signal at the half-hour close, order at the next minute's open. A completed bar's high/low must never justify filling at that same bar's open.
- **The stop distance is frozen from the signal.** Use the actual fill as its anchor, with signal sigma and signal close already known. Enable it in the fill minute. Recalculation from a future bar or failure to cover the entry minute changes the rule.
- **Respect gaps and competing orders.** Determine priority between an existing protective stop, reversal and scheduled exit, including a gap beyond a stop and a reversal's close-plus-open costs. OHLC “on-tick” price rounding is not a tick-path validation.
- **Completion flags must be causal.** Historical completed full sessions can enter the next session's lookback. Scheduled half days are known in advance. Unexpected future data gaps cannot justify excluding an entire current session before the gap appears. The bulletin names two fallback SetExitOnClose days; reproduce their actual handling rather than silently dropping them.
- **Prior close must be contract-consistent.** Unadjusted rolls can change the open/prior-close band even when a trade does not span a roll. Source and repository both warn about this. Freeze a roll-aware mapping or a stated adjusted-series sensitivity; do not automatically treat prior research's no-roll-spanning-trade finding as sufficient for S03's band.
- **No fresh historical holdout remains in the bulletin period.** The source was generated 22 September 2026 using data through 7 July 2026, reports a StopSigma sweep and yearly walk-forward, and discusses selected recent periods, times, sides and largest winners. Replaying 2023 through that date is historical replication. Anchored walk-forward addresses the yearly selector, not every earlier design choice. Any later local data must be designated and frozen before inspection; a true forward log starts after the frozen decision rule and review.
- **Count the whole search.** The stop plateau is useful descriptive sensitivity, but cannot reveal the number of earlier variants or prevent post-selection bias. Do not adopt the red-noon exclusion, weekday filter, short removal or April-2025 exclusion from these already-seen figures.

## Required inputs and account scope

The repository has close-stamped CT NQ day and overnight OHLCV exports (`data/NQ_1min_20*.csv`, `data/NQ_1min_ON_*.csv`), with day coverage beginning in 2018. They can support a newly specified OHLC replication after data checks. Do not import the existing Chuk module to inspect it: its top-level code loads caches, simulates trades and later writes a trade CSV.

Exact author-replica parity still needs the referenced PowerLanguage signal, `s03_engine.py`, the original `ofb_bars_NQ.csv` or its reproducible export specification, contract/roll metadata, session/calendar details, and a position ledger showing signal/fill/exit times and stop levels. The HTML's aggregated tables are insufficient to distinguish several implementations consistent with the prose. Tick data or a one-tick magnifier is needed to validate the execution claim; the bulletin itself labels it provisional.

Costs must be reconciled explicitly: S03 claims $5 round trip plus one tick per side, $15/NQ total; `DEVELOPMENT_PROCESS.md` and `CLAUDE.md` specify $7.25 round trip plus one tick per market/stop fill, $17.25 on a two-market/stop-fill NQ trade. The old Chuk script instead subtracts $14.50 commission plus two ticks, $24.50. Its saved $72 mean cannot be compared directly with S03's $112. Use the latest reviewed cost policy and report any discrepancy; do not silently standardize historical figures.

S03's LucidFlex first-passage and payout tables are not Apex 50K/150K evidence. Their targets, limits, payout conditions, sizing, costs and account reference differ. The reported exit signal at 16:00 ET fills at 16:01 ET = 15:01 CT; that is before the repository's 15:59 CT Apex deadline. It still needs calendar/session/fill validation. The bulletin's full-horizon ruin probability against a $50k loss is not a one-year Apex trailing-limit breach probability.

The user's broader default scope remains 50K and 150K evaluation, funded and personal accounts. None has been tested here for S03. Existing C/no-add findings on the old funded bench should inform the prior, without being presented as results for the new stop, current plans, the 150K, evaluations or personal account. A future authorized test must compare addition, replacement of VB and the empty slot on matched periods, with intraday open risk and account-specific rules. A small personal sizing recommendation in the uploaded bulletin is not a research-to-live promotion.
