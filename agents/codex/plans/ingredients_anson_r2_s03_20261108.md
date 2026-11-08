# Frozen ingredient grids: Anson, R2Vault, S03 v2

Summary: Build the requested Change / $ per trade / t / Read grids without selecting an improved rule.
Fifteen market definitions, five per family; baseline side breakdowns are contributions, not side-only reruns.
Commit evidence, plan, source hashes and exact harness before real returns; design checkpoint before recent.

## Exact definitions

**ANSON, NQ5-minute intended_apex**: current user inputs strength4.5/hold20; momentum=current close−12
observed chart closes ago, divided by mean range of20 preceding observed bars (exclude current). Flat-only
entries08:30–14:30CT, next observed chart-open. Entry bar counts held1; queue next-chart-open exit after20
completed bars or14:55. Repo early adapter queues exit11:30 and stops entries at/after11:30; no price stop/target.
`original`; `fade_direction`: reverse entry direction, retain same entry/exit clock and holding logic;
`no_strength_gate`: threshold0, nonzero momentum, all other checks retained;
`hold_6`: threshold4.5 retained, hold6 completed bars instead of20; not the confounded file-default3/6;
`no_early_adapter`: same4.5/20 source rule, raw early-close behavior including observed delayed/reopen fills.
Momentum12/range20 and ordinary entry/time window remain fixed, not independently attributed or optimized.

**R2, NQ5-minute ct_apex**, selected for the intraday comparison before returns, not the historically best raw
clock after a new search. Standard576-close OLS; R²≤.030 replaces stored vault with current candle high/low.
When flat and slope>0, next-bar buy-stop at ceil((vault high+.20range)/.25)*.25; at most3 filled entries/CTdate.
Actual-fill anchored75point stop/40point target immediately active; target needs1point trade-through; no BE;
R² exit2.00 is inactive. CT09:30–15:30 window, source15:55/early11:30 next-observed-opening flatten.
`original`; `fade_break`: short at the SAME upward trigger/crossing and price, with mirrored75/40 bracket,
then state/exit simulation continues causally; not a separate downside-break signal or a sell-stop above market;
`no_R2_gate`: update vault on every completed finite-OLS bar (threshold1), keep positive-slope gate;
`no_slope_gate`: retain finite-OLS initialization and R² vault update, remove only slope>0;
`no_stop`: infinite stop distance, target40/one-point-through and flatten retained.
Buffer.20,target40,lookback576,cap3/day remain fixed; no claim that they are independently optimal.

**S03, NQ1-minute v2_apex**: literal source14 accepted-session same-minute noise history, gap-adjusted bands,
cumulative total-volume VWAP and source no-trade calendar. Decisions09:00–14:30CT every30minutes; follow
close beyond band AND VWAP; band/VWAP exits/reversals at those decisions; next observed open fills; source
15:00exit and15:55/early11:30 adapter retained. Stop.4×raw sigma×signal close, actual-entry anchored, tick-rounded
away, entry-minute active; no target. Literal zero-filled incomplete ring slots remain flagged, not repaired.
`original`; `fade_direction`: reverse actual position direction while virtual follow-direction state continues
to govern band/reversal decisions; mirror the protective stop. Never naively attach follow exits to a fade;
`no_entry_VWAP`: remove only entry VWAP confirmation, retain original band/VWAP exit rules;
`no_entry_band`: entry follows VWAP side without band crossing, retain original band/VWAP exits and sigma;
`no_sigma_stop`: factor0 disables the stop, preserving all other rule state and reentries.
Gap anchor/history14/30minute frequency remain fixed and are not claimed optimal.

## Clocks, sources and run boundaries

All prices NQ, Chicago close-stamped minutes; labelled minute OPEN is one minute earlier in civil time.
Keep exact observed next-bar placement, intraminute cursor, gap fills and stop/target priority from retained
engines. R2 fade enters only after the upward trigger crossing; pre-entry Low cannot become a short target.
S03 actual side and virtual follow side differ only in the frozen fade; ordinary/source/calendar logic unchanged.
No measured latency, passive queue or actual order-flow claim follows from these source conventions.

Retain sources from codex/work4d88f53 (manifest exact full commit/blobs), Grid24/early calendar and raw data
from`fe35af99aa90d7f31b91f8693859251bb44dd9ab`. Use configured Python, shared Grid24/metrics/resampling,
observed-bar adapters and prior ingredient daily-mark helpers. No new persistent cache or top-level source runs.
Design2018-01-01–2022-12-30; recent2023-01-01–2026-10-09 unchanged, both already seen.2017 is feature warm-up.
Each era starts flat; R2 vault/OLS and S03 history retain past information. No design trade uses future exit data.
If any case is still open at an era boundary, preserve the state and stop dependent interpretation rather than
invent a terminal fill or silently omit an open loss. Missing held observations/queued fills remain explicit.

Original baseline price/side/time/gross must match unmodified retained engines on identical features and era.
Source-wrapper equality is implementation admission, not independent original-author MC parity. Retained raw
engines are extended only for listed component changes; do not repair unrelated source behavior after returns.
Use independent synthetic cursor/gap/reversal tests before market returns; abort on implementation failure.
S03 source calendar/history semantics and R2 clock ambiguity remain limits. No unseen holdout claim.

## Costs, risk and measurements

One standard NQ:PV20,tick.25,$7.25RTcommission, one adverse tick per market/stop fill. Anson/S03 pay two
market legs ($17.25RT); R2 target exit is limit, so$12.25target trade, otherwise$17.25. Distinguish this from
older1.04/MNQ-equivalent tables ($20.40/$15.40NQ): compare own frozen baselines, don't splice their means.
Native MNQ sensitivity scales price/slippage dollars by1/10 and uses **assumed$1.25RTcommission**; not a
broker quote. Extra cost stress adds1tick on each market/stop leg, fixed orders, without a latency/path claim.
No compounding/sizing/roll execution. Preserve source raw price geometry; flag cross-date/possible roll spans.

Marked daily ledger uses weekday23:59CT last-observed closes and next-weekday booking of weekend events;
commission half at entry/exit, separate entry/exit slip. No imputed executable quote. Daily marks/stale ages,
observed adverse paths, intraminute entry/exit bounds, unknown/closed gaps and late/cross-date fills retained.
Trade/gross/cost, daily, side and marked yearly totals reconcile to cent. Research DD is not prop-floor replay.

All cases/eras/years/sides:count,win,average,t,total gross/net/fees/slip,Sharpe/Sortino/PF,zero-initial-peak
DD/Calmar/Ulcer,worst trade/observed adverse,missing/fallback/carry counts,native-micro/cost stress. Save exact
features or feature digests/admission, dependencies/versions, raw hashes, settings and trade/daily ledgers.
Report original both/long/short rows; these are component contributions, **not** standalone long/short-only
strategy tests, and do not nominate a side. Mark unavailable/absent sides explicitly.

Original annual/Sharpe bounds and original-minus-each-intervention annual effect:1000moving20weekday blocks,
seed80315. Persistent contribution means original-minus-case net>0 in both eras; stronger also requires both
paired lower bounds>0. Wide intervals/mixed signs stay conditional, not 'decoration' or proof of no effect.

Filter removals generally change occupancy, levels, daily caps or future signals. Verify exact entry-event keys
and retained side/entry/exit/net before claiming a pure subset; never match multi-trade days by date alone.
Only a verified nested same-day set gets removed n/total/avg/t and1000within-year matched-count random drops
on profit/DD. Otherwise report a paired whole-policy comparison with nested controls inapplicable. This does
not satisfy a new-feature admission claim. No sixth return definition, timing null or threshold rescue.

## User grid and scope

Saved report and final chat: separate strategy grids with Change / $ a trade / t / Read. Show full-history
mean/t and design/recent mean/t together, or companion era columns, to expose instability. Include totals/DD
where they change the reading. No average-only 'improvement', certainty from a post-hoc side split or claim
that unisolated fixed settings are best.15 definitions and all previous research remain trial history.

No account/portfolio tests, combination, new MC code, plan/TIER edits, live/VPS/broker/key access, external
messages, paid data, scout-history changes or schedules. Earlier rejection/placement results remain intact.
Complete attribution, preserve useful execution lessons, commit/push codex/work for independent Claude review.
