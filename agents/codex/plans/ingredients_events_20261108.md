# Frozen event-ingredient round: EOS, NFP Fade, CL Sunday Fade

Summary: Dissect three existing strategies chosen by Codex at the user's request.
Fifteen fixed definitions, five per family; no parameter selection or new combined strategy.
Commit this plan, evidence, exact harness and retained source ports before real returns.

## Fixed definitions

**EOS (NQ, 5):** original short at08:30civilCT (08:31close-labelled bar OPEN), stop0.30×past15weekday ATR,
no target, exit10:00CLOSE on source monthly expiry dates including holiday Thursday shifts;
`no_expiry_gate`: same short on every Friday plus the shifted Thursday expiry dates, preserving nesting;
`opposite_direction`: long on original expiry dates with the same stop/horizon;
`no_stop`: same original dates/short/horizon with no protective stop;
`exit_0900`: same original entry/stop/dates, close09:00 rather than10:00.
The calendar-only explanation is separate from demonstrated forced dealer trades. Current source code's actual
exit is10:00CT, not the10:30 window discussed in some earlier mechanism analyses.

**NFP Fade (NQ, 5):** original source price-release detector:07:30–07:35 range >3×median of the previous20weekday
ranges; Friday, day-of-month<=10; fade07:30CLOSE→07:45CLOSE at07:46labelledOPEN (07:45civilCT), stop0.50×past
15weekday ATR, exit09:00CLOSE; skip all Good Fridays as the current source code does.
`no_spike_gate`: keep early-Friday/date/side/horizon rules but remove the >3×range requirement;
`no_payroll_calendar`: retain spike detector but allow all weekdays, same side/entry/stop/exit;
`opposite_direction`: follow the same original reaction on original dates;
`no_stop`: original dates/fade/horizon without the stop.
This diagnoses the existing early-Friday/spike proxy, not an authenticated complete BLS calendar or surprise signal.
No change to reaction reference, reaction length, close/open interpretation or detector lookback is scanned.

**CL Sunday up-gap fade (CL, 5):** reproduce MC-confirmed Python timing: first observed Sunday open at/after17:01
label minus last close before17:00; up-gap>=0.10×15weekday ATR. Short17:06labelledOPEN (17:05civilCT), stop0.75ATR
from slipped entry, Monday09:00CLOSE exit. Source full-Monday/nonzero-gap calendar and no-roll-skip spec retained.
`no_upgap_gate`: short every otherwise valid nonzero-gap source Sunday, including small/negative gaps;
`opposite_direction`: long the original up-gap dates, with the same distance/horizon;
`no_stop`: original short/dates/horizon without the stop;
`exit_0300`: same original short/entry/stop/dates, Monday03:00CLOSE instead of09:00.
The gap gate bundles sign and size; its removal is not just a threshold-at-zero test. Native dated contracts are
not certified by the unadjusted continuous source. Do not drop additional roll dates based on the outcomes.

## Implementation and admission

Warm-up2017; first run2018-01-01–2022-12-30. Save and inspect implementation/coverage gates, then replay all fifteen
definitions unchanged on already-seen2023-01-01–2026-10-09. This is historical attribution, not an untouched holdout.
No economic gate selects a winner; the condition for recent diagnostics is correct implementation/accounting.

Use pinned Grid24 in memory from explicit annual NQ day/overnight and CL raw files. Verify every raw Git blob and
SHA256 against the snapshot. No persistent grid cache, no extra primary downloads or scout/reservation changes.
AST-extract the retained source functions; never import source top-level experiments or execute PowerLanguage.
Use `grid._walk` without its cache decorator for price paths; no targets exist in these fifteen definitions.
Source NQ stops anchor to raw entry, matching existing Python simulations; CL anchors to slipped entry per the
MC-confirmed Python spec. This one-tick distinction is recorded, not silently unified.

Capture feature clocks, selected/excluded dates, ATR, gap/spike and source-selection flags before pricing. Opening
gap discovery must occur by17:05decision: exclude a CL first-observed open after the first five minutes. Missing
entry/feature prices exclude the event with a reason before outcomes; never impute an entry. Source walker may
skip missing held bars and use last known close for a missing scheduled exit; expose every such observation and
fallback explicitly. This is source-policy replay, not certification of executable native fills or known future
data availability. Abort on nonfinite actual entry/exit/net or cost/daily mismatches. Report original baseline
parity with retained NQ reaction simulator and vectorized CL confirmation function on their common admitted events.
EOS retains source grid/calendar rules; do not claim fresh MC trade-list parity without doing that check.

NFP/EOS calendar exclusions and zero-reaction rules apply identically to corresponding parent/child controls.
CL trades are attributed to Monday's trading date; do not book Sunday's entry as a separate account day.
Source-calendar and raw-contract/roll limitations remain visible; no new historical evidence is manufactured.

## Measurements, costs and interpretation

Fixed one standard contract, no compounding. NQ point value$20/tick0.25, CL$1,000/tick0.01. Each pays$7.25RT
commission plus one adverse tick on each market/stop leg: normal$17.25NQ /$27.25CL. Additional cost view subtracts
another two ticks per round trip on fixed orders; it does not re-anchor/replay stops. No latency saving is claimed.
Native one MNQ/MCL bridge uses one-tenth price/slippage dollars and **assumed$1.25RT micro commission**, hence normal
$2.25MNQ /$3.25MCL. These are research sensitivity units, not verified broker fees or proposed sizes.

For each case/side/year/era: trades, wins, gross/commission/slippage/net, average, trade t, Sharpe/Sortino/PF/
Calmar/Ulcer, zero-initial-peak daily DD, worst trade and source modeled adverse mark, native micro totals/tails,
missing-path/fallback counts, and additional-cost results. Save exact trades and full common-calendar daily ledgers;
daily totals must match trades to a cent. Do not claim account breach odds from standard-contract DD or source MAE.

Every original-minus-intervention calendar effect:1000paired20session moving-block bootstrap, seed20261109,
annual-effect5/50/95%bounds. For nested calendar/spike/up-gap gates, verify retained date/side/entry/exit/net identity;
report removed-trade total/mean/t. Drop the same count randomly within each year1000times and compare total profit
and DD. Mark any nonnested comparison as a rule intervention, not removed-trade alpha. Three gates in EOS/NFP/CL
plus NFP's second selection gate are all recorded; do not omit an unhelpful control.
Reuse the prior committed ingredient study's daily-ledger, JSON and random-subset helpers, binding this round's
fixed seed explicitly; verify their exact committed bytes and hashes. Retain original-rule annual/Sharpe bootstrap
bounds in each era as conditional uncertainty, rather than calling the recent replay a fresh holdout.

Historically persistent profit contribution: baseline beats the intervention on total net in **both** eras.
Stronger attribution additionally requires paired bounds to exclude zero, with earlier selection still relevant.
Primarily risk control: removal worsens tails/DD without reliable profit benefit. Mixed signs or wide bounds:
conditional/inconclusive. These are reporting labels, not adoption/pass-fail recommendations.
Prior source searches and earlier ingredient/combination trials retain multiplicity. Fifteen current definitions
include all baselines; do not present the best diagnostic as a new S/A strategy or erase earlier looks.

No optimizer, new combined rule, account simulations, MultiCharts/live edits, TIER/plan changes, paid data, external
messages, VPS/broker/API-key access, or automation. Any proposed changed/combined strategy needs a separate protocol.
