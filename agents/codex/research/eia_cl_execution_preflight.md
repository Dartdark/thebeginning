# EIA candidate execution preflight: CL/MCL units, costs and limits

This is an offline implementation/source review for a possible later EIA fundamentals study. It is not an
economic preregistration, a TEST decision, a strategy-return result, independent promotion or a milestone.
No price files or forward strategy returns were opened or calculated in this review. No web acquisition,
broker/API settings, live actions, code changes, commits or pushes were performed by this reviewer.

## Contract arithmetic and evidence status

| Item | CL | MCL | Status |
|---|---:|---:|---|
| Point value per $1/barrel | $1,000 | $100 | CL explicit in local research; native MCL specification requires primary confirmation |
| Minimum price tick | $0.01 | $0.01 | Native contract expectation; MCL not independently verified in this offline review |
| Dollar tick | $10 | $1 | Point value multiplied by minimum tick |
| Round-trip commission | $7.25 | Unverified | CL repository assumption, not newly verified current broker fees |
| One adverse tick at each of two market fills | $20 | $2 | Excludes commission and additional spread/latency stress |

CL units and commission conventions are stated in [S_RANK_PROGRAM.md:49](../../../S_RANK_PROGRAM.md#L49),
[analysis/cl_forced_flows_test.py:27](../../../analysis/cl_forced_flows_test.py#L27) and
[analysis/s_rank_gap_round2_test.py:57](../../../analysis/s_rank_gap_round2_test.py#L57). The conventional
two-market-fill CL research cost is therefore $27.25. These are existing assumptions, not a newly verified
historical or current fee schedule.

No independently supported native MCL commission was located. Do not import MNQ's $1.24 convention or
divide CL commission by ten. The native calculation must be separate for each contract:

`net = signed_price_points * point_value - commission_rt - slipped_fills * slip_ticks * tick_value`.

## Shared execution kernel and adapter boundaries

Reuse the shared [grid._walk at line146](../../../analysis/grid.py#L146), which accepts price arrays,
scheduled entry and exit indices, side, stop/target prices and an explicit target-through price distance.
Keep original CL price units rather than applying NQ price scaling and then assuming NQ monetary constants.

- `_walk` starts checking the entry minute, so entry-bar stop/target protection is active.
- On later held minutes, stop gaps receive the worse native open. Both-bracket-hit minutes follow the shared
  open-distance path heuristic; this is an OHLC reconstruction assumption, not known event order.
- A missing open is skipped. The time exit searches backward if the scheduled close is absent. Preserve and
  audit unknown held intervals, missing scheduled entries and displaced time exits rather than silently
  treating the path as observed. Audit all held OHLC fields, not only a missing close count.
- A market entry needs a real scheduled native open. Do not search later minutes for a more convenient fill.
  For close-labelled data, preserve the specified decision/order/receipt delay explicitly.

[grid.execute at line190](../../../analysis/grid.py#L190) is NQ-specific: module globals at lines32–34 set
point value20, commission7.25 and target-through1.0. Its use of those globals at lines221–230 makes a direct
CL call financially incorrect. One CL price point is $1/barrel, so a copied1.0 target-through would require
100 CL ticks through a target. Freeze a native oil through distance in ticks before returns; do not silently
treat the NQ one-point convention as universal.

[codex_flow_absorption.replay at line100](../../../analysis/codex_flow_absorption.py#L100) provides useful
signal-time flatness, stale-signal suppression and exact scheduled-entry handling. But lines112–117 hardcode
NQ target-through1.0, point value20, $5 slipped fills and MNQ commission/slippage. It is not a CL/MCL adapter.
[param_clusters.trade_net at line17](../../../analysis/param_clusters.py#L17) likewise uses the NQ $5 tick.

[codex_t6_study_support.evaluate at line53](../../../analysis/codex_t6_study_support.py#L53) calls that
NQ replay at line56 and labels its native micro column `net_mnq` at lines65–68. Parameterize the replay and
native-column names, or use a thin scoped wrapper around shared `_walk`, metrics and resampling. Do not
reuse the NQ monetary result and rename it MCL.

Recommended explicit adapter inputs are `point_value`, `tick_size`, `commission_rt`,
`slip_ticks_market_stop`, `target_through_ticks`, scheduled entry index, time exit, positive stop/target
distances, side and whole contract count. Candidate and matched base should retain identical execution rules.
Opposite-side controls can have different actual stop/target exits and fill costs despite identical rule settings.

## Monthly roll and prior-feature audit

The existing [rolls_cl at line166](../../../analysis/s_rank_gap_round2_test.py#L166) marks a03:33 bar on
LTD−2 and the largest absolute03:30→03:33 jump of at least$0.15 within eight calendar days before LTD.
LTD is estimated from the available business-date sequence and the25th. This documents a historical vendor
splice detector, not a verified native-contract roll calendar. Its largest-jump selection uses the whole
window and must not automatically become an executable causal date filter. A later study should freeze a
conservative predetermined monthly guard or obtain original contract/switch mapping; distinguish that from
deleting trades according to observed P&L.

[Grid24.daily_atr at line101](../../../analysis/grid24.py#L101) includes continuous-contract jumps in true
ranges. A daytime EIA trade clear of an overnight splice can still inherit a distorted prior ATR. Review both
held paths and the history used to construct any prior risk distance. No roll-adjustment choice is authorized
from candidate profits in this source-intake phase.

## April2020 and native micro-history limits

The documentation in [cl_forced_flows_test.py:4](../../../analysis/cl_forced_flows_test.py#L4) and
[s_rank_cl_round1_test.py:10](../../../analysis/s_rank_cl_round1_test.py#L10) states that the continuous export
had rolled before the negative May2020 contract print, reporting a $6.90 low instead. That is a limitation
of this continuous history; it is not evidence of executable coverage of the actual negative-price contract.
No new raw-price audit was run here.

Shared `_walk` arithmetic itself can handle finite negative prices. Do not copy equity-specific positive-price
guards, log returns or percentage normalizations that discard negative/near-zero oil observations without an
explicitly frozen rule. Absolute price differences and positive ATR distances avoid some such singularities,
while roll and source continuity still need separate checks.

No native MCL minute files, independently verified listing-date evidence or CL/MCL historical price/fill parity
was located during the offline review. MCL's exact launch date must be established from a primary source;
do not claim native MCL execution in the2018–20 prelisting period. Any such early micro-sized result would
be a hypothetical CL-price proxy and needs that label. Even after listing, CL bars do not establish MCL
spread, liquidity, target fills or same-minute price parity.

The existing [CL Sunday bench at line54](../../../analysis/cl_sunday_fade_bench.py#L54) divides the full
CL net ledger by ten to create an MCL-sized account contribution. That scales the full-contract commission
down as well and is not evidence of native MCL costs. Its lines21–23 also document a MultiCharts timing
correction and a different roll policy. Historical plan accounting is not an adapter specification for this
new input family.

## Calendar and decision clocks still to freeze

The old EIA price-reaction study estimates release days from Wednesday/holiday-week Thursday rules in
[cl_forced_flows_test.py:74](../../../analysis/cl_forced_flows_test.py#L74). The new source intake has an
actual dated edition calendar and must not revert to that shortcut or assume one release time for every
exception. Likewise, an NYSE cash-calendar mask is not automatically the correct CL session calendar.
Any future15/30-minute signal must use its declared actual release timestamp, complete native input window,
receipt/order delay and CL time-exit/holiday protections. No entries or holding windows are selected here.

Remaining prerequisites include primary CL/MCL contract/listing confirmation, explicit native MCL fee
assumptions with sensitivity, historical release clocks/vintage review, source contract continuity and an
economic evidence sheet followed by a separately committed <=5-configuration preregistration before returns.
This note adds zero return trials, creates no t4/4.5/5/6 event and does not alter the notification watcher.
