# Event/path builder — code and metadata scope only

Implementation: `analysis/codex_eval_paths_20261104.py`. This note and the code were written before the
root's evaluation-study preregistration. Only synthetic fixtures and Python compilation have run here.
No owned price paths, allocation combinations or account outcomes were calculated by this subtask.

## API

```python
from codex_eval_paths_20261104 import build
tape = build(config_path, preregistration_commit, output_directory)
```

The configuration is a repository JSON file committed before market-path work. Required fields:

```json
{
  "start": "2018-04-02",
  "end": "2026-07-07",
  "markets": ["NQ", "ES", "CL"],
  "ledgers": {
    "VB": {
      "path": "analysis/outputs/codex_portfolio_audit_20261031/VB_unit_ledger.csv",
      "sampling_start": "2018-01-25",
      "sampling_end": "2026-10-09",
      "source_bar_minutes": 15,
      "source_inference": "Report fill timestamps inferred by the prior audit; not certified native fills."
    }
  },
  "market_sources": {
    "NQ": {"files": ["data/NQ_1min_2017.csv", "data/NQ_1min_ON_2017.csv"]}
  },
  "target_trade_through_points": {"NQ": 1.0, "ES": 1.0, "CL": 0.01},
  "frozen_files": ["agents/codex/plans/ROOT_STUDY_PLAN.md"],
  "input_sha256": {"data/EXACT_FILE.csv": "REQUIRED_ACTUAL_HASH"}
}
```

The JSON above illustrates the schema, not a complete registered input universe. Register every needed
raw file, including warm-up, source ledger and source adapter dependency. Omit `market_sources` only if
the committed inventory binds all matching default files. Generated ledger adapters can be registered by
frozen code and original-source hashes; their output hashes are retained after deterministic preparation.
The builder does not substitute last trade for sampling end. Every key requires explicit certified FULL
account-date sampling bounds, strictly `YYYY-MM-DD`; partial timestamps cannot be rounded into coverage.
Every consumed raw file and static ledger must be a member of `input_sha256`, including glob-discovered
files. `generated:true` ledgers require the frozen extra-ledger adapter and its source hash chain. The
builder invokes that adapter on the already loaded NQ grid before constructing the tape.

The returned `Tape` contains:

- `prices[N,A]`: one shared modeled price per asset/event, preserving NaNs.
- `times[N]`: UTC epoch seconds converted from Chicago close labels; no invented DST disambiguation.
- `session[N]`: index into full-calendar `dates[D]`, including weekend/holiday account-clock boundaries.
- `events[E,10]`: row, trade_id, key_id, asset_id, action(+1entry/−1exit), side, raw_fill,
  stop_points_at_entry, requested_qty, fill_kind(0market/1limit/2stop). Root supplies actual integer requested quantities.
  An unsupported source execution has NaN in its event fill; its original claimed price remains in
  `trades.csv`. The shared observed quote is preserved, so a sleeve never allocated by an account
  cannot corrupt another sleeve's mark. Such an event becomes UNKNOWN only if actually required.
- `node_rows`: first/last, every source event, session-start/EOD and15:59daily-flat boundaries.
- `segment_min/max/missing[S,A]`: observed bounds over `node[i]+1:node[i+1]+1`, including the next node's
  price BEFORE its events. After events at the first node, constant net exposures can prove a segment safe
  and jump it; otherwise the core walks the raw tape to find the modeled first crossing.
- `eod`, `cutoff`, `session_start` boundary flags; `coverage[K,D]` sampled-date mask.
- `trading_day[D]`: observed NQ `Grid24.trading` membership, captured while the input grid is loaded.
  It is an elapsed observed-session indicator, not a newly certified official holiday calendar.
- `trades`, `quality` and `metadata` audit records. Source inference flags and hard quote/timing mismatches remain.

NaN boundary marks are harmless only when there is no remaining net asset exposure. Held missing data must
produce UNKNOWN/incomplete treatment, not a zero return. A source key outside its sampled period is not an
observed no-trade strategy. The engine must enforce those masks, contract limits and daily flat rules.

## Source-known entry risk

The following are verified source defaults; they are not estimated from future exit prices:

|Key|Initial source stop distance|Source|
|---|---|---|
|VB/VB_N/VB_F|75NQpoints,fixed|`apex_strategies/NQ_Vault_Break.txt` StopPts75 and SetStopLoss. Its0.30ATR is the ENTRY noise threshold, not its stop.|
|ONB30|0.25×prior15weekday-calendar ATR|`apex_strategies/NQ_Overnight_Bias_ADX30.txt`|
|ONBML/EOS|0.30×prior15weekday-calendar ATR|`funded_strategies/NQ_Overnight_Bias_ML.txt`, `NQ_Expiration_Open_Short.txt`|
|LDF|0.25×ATR15|`funded_strategies/NQ_Late_Day_Flow.txt`|
|MON/NFP|0.50×ATR15|`funded_strategies/NQ_Monday_Long.txt`, `NQ_NFP_Fade.txt`|
|DT|50NQpoints,fixed|`funded_strategies/NQ_Dual_Thrust.txt` SLPoints50|
|RS|0.60×mean prior20fullRTHranges|`funded_strategies/NQ_Relative_Strength.txt`|
|TOS|0.40×mean prior20fullRTHranges|`funded_strategies/NQ_T_Oneside_Fade.txt`|
|MOC|0.25×ESATR15|`funded_strategies/ES_MOC_Follow.txt`|
|CLS|0.75×CLATR15|`funded_strategies/CL_Sunday_Gap_Fade.txt`|
|BRIDGE|NO stop at default|`apex_strategies/Bridge_Monday_Long_L644NQ.txt` StopPts0|
|OT|NO stop at default|`funded_strategies/NQ_Overnight_Tick_VIX.txt` UseDisasterStop=false|

No-stop trades get infinity, not an invented finite loss cap. Floor-aware admission must explicitly decide how
to handle such trades under the root's frozen policy. Source ATR15 requires per-key frozen
`source_bar_minutes`: the calendar-date bank uses compressed chart candles, including the00:00candle
that contains the previous date's final minutes. Sunday close updates the prior-close reference, while
only completed weekday chart dates enter the15date ring. RTH20 uses prior full sessions with a15:00close.
`source_clock_offset_minutes` is60for CLS's Eastern chart-date bank and0for CT sources. Its bank boundary
is23:00CT. `risk_input_missing_bars` counts partial and wholly absent required candles between the first/last
observed source-chart candle, excluding only frozen known venue closures. Any detected lookback gap makes
`stop_points_at_entry` NaN. `stop_points_owned_feed_estimate` preserves the conditional reconstruction solely
for diagnostics, not sizing. Fixed source stops remain independent of ATR completeness. A zero detected-gap
count still does not establish original-feed parity or a complete official holiday calendar. These causal calculations do not certify the
author's exact chart/feed/quote history or eliminate unobserved extreme prices. Custom adapters may supply
an explicit `stop_points_at_entry`; they must preserve source clocks and cannot infer it from a later stop exit.

Native micro point values: MNQ2,MES5,MGC10,MCL100 dollars/price point; ticks0.25,0.25,0.1,0.01respectively.
Raw source prices contain no newly added fee/slippage. The account core applies native per-side commission
and adverse market/stop slippage once; target-limit exits avoid an extra market-exit slippage charge.
The committed configuration must explicitly state per-market `target_trade_through_points`. A target
without the required observed trade-through after its modeled crossing becomes an unknown exit event;
a high/low before the entry or target cannot qualify it. A present-but-unknown source qualifier cannot grant
admission. It does not receive a certified exact fill. The example mapping above illustrates configuration
syntax; root freezes the actual market values.

## Source coverage and phase limits

Saved prior-audit MC settings explicitly support these source end dates: VB2026-10-09,ONB302026-10-13,
BRIDGE2026-10-13,EOS2026-10-11,ONBML/LDF/MON/NFP2026-10-12or13. Their common April2018start is after
those reports' declared starts. Non-MC keys need their own input/run sampling declaration; the last ledger
trade cannot certify no-signal periods. In particular OT cannot be silently zero-extended past known coverage.

Normalized Bridge timestamps include Sunday19:00/18:56fills and Monday exits. The builder preserves the
entire17→16account session; it never truncates Sunday exposure at Monday00:00. The18:56inferred first-touch
minute is not asserted to be the real order's exact fill time at a19:00chart stamp.

The portfolio-independent OHLC path is O→nearest extreme→other extreme→C. Opposite sleeves in one asset
therefore see the SAME price, netting correctly. Source fill-level crossings are inserted only when matched to
the observed minute; unmatchable source fills/phase conflicts become NaN in their source event's fill field,
preserving actual observed common quotes. Explicit
failed adapter touches cannot be repaired by a coincidental level match. This is a disclosed within-minute/
cross-asset model, not recovered simultaneous quote chronology. Fractional insertions preserve every other asset's latest modeled point WITHIN
that same minute; a later different-asset event cannot reset an earlier fill to an older OHLC endpoint. Integer
phase endpoints advance all assets. Nothing is carried across a missing raw minute. Material barrier/order
uncertainty cannot be called native economic verification.
No source-price interpolation, missing-bar fill or per-sleeve adverse-extrema sum is used.

Closed-market Sunday DST gaps are compressed to explicit unknown nodes at known clocks. No ambiguous
fold or nonexistent civil clock is invented. A source's own zero-duration entry/exit is represented by
separate identical-price/time nodes, preserving entry-before-own-exit causality.

## Frozen venue closure schedule

The configuration must include the dated closure rules justified by `calendar_audit.md/json`, for example:

```json
"market_closures": [{
  "markets": ["NQ", "ES"], "end_account_date": "2021-06-27",
  "close_label_start": "15:16", "close_label_end": "15:30",
  "weekdays": [0, 1, 2, 3, 4]
}, {
  "markets": ["NQ", "ES", "CL"],
  "close_label_start": "16:01", "close_label_end": "17:00"
}]
```

Only a minute with no source event, no contradictory observed quote, and every potentially held asset
documented closed can be omitted. The observed reopening gap carries the risk. An open other asset
prevents omission; the closed asset remains unknown at that shared point. A source event during the
closure or a contradictory source quote is retained and flagged hard unknown. After2021-06-27,
15:16–15:30gaps are open-market unknowns. No missing17:01bar is classified as a scheduled closure.

The builder uses only the union of source holding intervals plus account-clock nodes, so flat inactive minutes
need not be expanded. Numeric row storage is preallocated to avoid millions of Python row objects and a
second full tape copy. For3,100dates and3assets, raw OHLC alone is about429MB; an all-minute-active tape
could add roughly700MB plus source grids/frames and temporary features. Several GB peak remains possible;
actual time/memory has not been measured before preregistration. Segment-bound
skipping is designed to make large bounded allocation screens feasible without rewalking every safe minute.

## Synthetic verification

`python analysis/codex_eval_paths_20261104.py selftest` passed checks for Sunday session mapping,17:00boundary,
shared-price opposite-position cancellation, fixed OHLC path, fill-crossing phase, missing quote propagation,
segment bounds/missing masks, source event inclusion, chronological nodes and EOD/cutoff/start markers.
A separate two-asset fractional-insertion fixture prevents a phantom within-leg backtrack. Malformed OHLC
is retained as unknown rather than converted into a plausible price path.
Additional fixtures cover illegal weekend carries around both DST transitions, entry-before-own-exit ties,
dated closed-only omission, mixed open/closed assets, source events/observed quotes contradicting a closure,
explicit adapter mismatch propagation, strict full-date sampling bounds and source-chart ATR midnight/future
mutation causality. Every fixture uses fabricated inputs.
`python -m py_compile analysis/codex_eval_paths_20261104.py` passed. These are engineering checks only.
