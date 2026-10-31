# S03 Noise Area v2: implementation PASS, research validation WITH CONCERNS

Summary: The declared observed-bar reconstruction passes 3,016,556 independent feature/trade comparisons and 12 selected synthetic fixtures.
Source equivalence, tick execution, data coverage and a clean causal timing placebo remain WITH CONCERNS.
The fixed stop does not meet the registered improvement criterion in either period; its return/risk effects differ.
All 400 frozen comparator outputs are retained. No account, personal or baseline Monte Carlo simulation was run.

Preregistration: `d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad`, [frozen plan](../plans/s03_noisearea.md).
Checker: [codex_s03_diagnostics.py](../../../analysis/codex_s03_diagnostics.py).
Evidence: [design diagnostics](../../../analysis/outputs/codex_s03_noisearea/diagnostics_design/diagnostics_summary.json), [recent diagnostics](../../../analysis/outputs/codex_s03_noisearea/diagnostics_recent/diagnostics_summary.json), and [source-calendar audit](../../../analysis/outputs/codex_s03_noisearea/accounts/native_coverage_audit.json).

## Implementation scope and result

PASS applies to the declared reconstruction on the observed data. The separate raw-array checker rebuilt prior-14-full-session noise, prior normal/early cash closes, anchor choices, typical-price/total-volume VWAP, strict signals and check-time exits. It checked every trade's raw/slipped prices, final costs, frozen stop, earliest observed stop/gap trigger and first-native market fills. Own in-memory fixtures covered causal history, current-day future gaps, both-side entry-bar stops, reversal priority, trailing/flatten timing and unresolved paths. The checks comprise 1,138,144 design and 1,878,412 recent comparisons. This is not certification of the absent author's engine or unobserved prices.

The stop comparison replays all re-entries. Design V2 adds $19,450.75 but slightly increases point drawdown by $114.25. Recent V2 reduces point drawdown by $25,809.25 while reducing net by $1,263.50. Neither period meets the frozen joint improvement rule. These are observed-data trade-offs, not an isolated causal benefit from deleting losing trades.

## Comparator interpretation

The time permutation is explicitly `causal_policy: false`, `retrospective_only: true`. It can move a direction proposed by a later raw signal to an earlier check, using a daily proposal count and directional mixture that were unavailable then. It is a future-informed retrospective comparator, not a causal random-entry strategy. Its recorded p=1 net/Sharpe comparisons cannot establish that causal entry timing fails or that the underlying entry edge is zero. A clean causal timing test remains **OPEN**. No replacement control or new simulation was run after seeing these results.

The side controls compare a joint direction/reversal/occupancy/turnover/cost policy. Opposite randomized proposals create additional reversals: median filled counts are 3,201 versus 1,366 observed in design, and 2,341.5 versus 1,013 in recent history. Their costs and occupancy therefore differ substantially. Their favorable recorded comparisons for V2 do not isolate direction prediction at matched turnover or cost.

All 100 side and 100 time streams per period are retained, including incomplete paths. Unknown held minutes affect 35 design time streams, 45 recent side streams and 93 recent time streams; no stream was removed or repaired. Their closed-ledger comparisons remain descriptive where prices needed to establish an executable path are missing.

## Open source, tick and data concerns

The archived HTML hash matches the frozen source, but its original PL signal, `s03_engine.py`, OFB prices and tick tape are absent. The source's chosen stop, at least 12 prior stop settings, and seen historical results cannot supply independent validation. Source parity and tick validation remain open.

The public source-calendar audit permits 13 flat gaps away from scheduled decisions under the frozen observed-only VWAP rule. Those gaps are not automatic account blockers. Two other dates remain calendar blockers: the unclassified missing 12:00 decision on 2020-03-18 and the entirely missing normal cash session on 2020-11-30. The held position on 2024-10-09 has three unknown native minutes, at 14:47, 14:48 and 14:55 CT. These unresolved observations block account scoring; no price, trade or day was imputed or removed.

The diagnostics flag `has_some_observed_cash_data_on_each_normal_date` has a deliberately narrow definition: every predetermined normal date has at least one observed valid OHLCV minute between the selected anchor and 15:00. It does **not** assert full 390-minute primary-session completeness, scheduled-decision coverage or account eligibility. It is false in design because 2020-11-30 is absent, and true in recent history despite the held-minute gaps. The separate `observed_held_order_paths_complete` flag is true for design and false for recent history. The source-calendar audit and account gate decide required calendar coverage.

Implementation consistency passes. Source/tick/data and clean causal timing validation remain WITH CONCERNS; account simulations remain blocked. This review supplies no allocation or live-trading recommendation.
