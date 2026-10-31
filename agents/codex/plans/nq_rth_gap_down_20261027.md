# Fixed NQ gap-down RTH long: independent reconstruction

Written before any new market-value intake or returns,2026-10-27. User explicitly
authorizes testing from the written description because original code/logs do
not exist. Branchcodex/work only. This manual task adds no Hunt v2 hypothesis,
does not reset multiplicity and does not resume either paused automation.

Evidence: `agents/codex/evidence/nq_rth_gap_down_20261027.md`.
Archive supplied post/README under `agents/codex/inputs/nq_rth_gap_down_20261027/`.
All outputs/cache under `analysis/outputs/codex_nq_rth_gap_down_20261027/`.
No live operations, shared plan/ranking changes, purchases or external messages.

## Rule, calendars and information clock

- Instrument NQ signal/execution price path, one-minute signal timeframe.
  Report native one-MNQ economics; also one-NQ source diagnostics with its own
  fees. One trade maximum/day, long only, no target/reentry/volatility filter.
- Calendar: existing `codex_s03_calendar.calendar_status`, all expected cash
  sessions. Full cash holidays/weekends have no intended trade. Native times
  are America/Chicago close-labelled bars. Normal cash close15:00CT; preknown
  early cash close12:00CT. Prior reference is the immediately previous CASH
  session's exact close, including its scheduled early close when applicable.
  This early-close interpretation is an explicit reconstruction choice.
- Signal: today's OPEN08:31 (physical08:30CT) < prior cash-session CLOSE.
  Exact equality is no gap, no trade. No magnitude threshold or gap renormalizing.
- Primary executable entry: observe the full08:31 close-labelled minute, then
  fill OPEN08:32 (physical08:31CT) with adverse execution costs. No information
  from the entry or later bar selects the trade. Ordinary bar-close receipt
  plus next-bar-open is the repo's assumed clock, not verified tick latency.
- Stop at raw entry reference minus100NQpoints. Fill costs are charged
  separately; therefore a normal stop costs more than$200/MNQ. Protection starts
  on the entry bar; a later bar opening below stop fills at that worse open.
  A touch triggers. No target, so no within-bar stop/target ordering ambiguity.
- Normal exit CLOSE15:00CT, early exit CLOSE12:00CT. It is a preplanned time
  exit with adverse fill costs. No holiday hold or later-than15:59CT exit.
- An exact-opening-print benchmark is explicitly nonexecutable after its
  condition is observed and can NEVER be selected/promoted as the primary.

## Five frozen economic definitions; no parameter search

1. **GAP_NATIVE**, primary: delayed entry above, MNQfee1.24RT plus .25point
   adverse entry and exit; total nominalRT2.24USD/MNQ.
2. **ALL_LONG_NATIVE**, mandatory matched baseline: same delayed entry, stop,
   exit and costs on every source-admissible cash date, irrespective of gap.
3. **GAP_SOURCE_COST**, diagnostic: SAME delayed trade path, report oneNQ,
   .50point adverse per fill and zero commission, matching source headline
   convention as far as the written description permits.
4. **OPEN_PRINT_SOURCE**, diagnostic only: gap condition and entry at the same
   OPEN08:31print, raw100point stop, source cost above. It includes a timing
   privilege and is not executable evidence. It is never a candidate or control
   for a claimed live gain.
5. **GAP_SEVERE_COST**, diagnostic: SAME delayed primary path, native MNQfee1.24,
   1.50points adverse per fill plus3additional points on stop exits. No parameter
   changes, no alternative selected if the primary fails.

Normal native NQfee7.25RT plus.25point/fill is also a transparent unit/cost
bridge of the PRIMARY ledger, not another entry or selected configuration.
Source post's own severe fee10USD/NQ can be reported as arithmetic on that same
ledger, labelled author convention. Retain every definition and diagnostic.
Own evaluations count primary+always-long+opening-print economic paths=3;
five frozen economic/cost definitions are retained, with no claim of statistical
independence. The author's total variants are UNKNOWN; source selection remains.

## Source admission and split

Before values, bind plan/code/input hashes. Design2018–22 first, previous2017
cash close as warmup. Use day exports; do not load a2023+file in design. Later
validation2023 through latest owned2026date runs once, with no retuning.
The post and repository already exposed later history: NEVER call it fresh.

Deduplicate only byte-equivalent OHLCV keys, retain all duplicate source IDs;
conflicting keys and invalid candles are unresolved, not chosen silently.
No forward fill of prior reference, opening/entry/exit or held bars.
Enumerate every expected cash date, missing date/reference, half-day and row.
A missing required reference/open means UNKNOWN signal, never no-trade zero.
For held gaps, outcome is UNKNOWN unless stop/time exit was already resolved
strictly before the first missing/invalid minute. Preserve unknown events and
do not repair them from later prints. Statistics may describe only resolved
coverage; unknown outcomes/dates block a clean promotion or full account PASS.

Input continuous-contract identity and rolls must be reported. Do not alter
prices with an outcome-selected jump filter. Raw gap/roll exposure is a limit;
calendar quarter-expiry-week counts may be disclosed, never optimized exclusions.
No current2026date receives an invented zero or future observation.

## Gross first, fixed historical reproduction and promotion

First screen2018–22 raw delayed-entry-to-time-exit move on down-gap dates:
counts, mean/t, both sides(the rule is long only) and each year. Native mean
must be at least2x2.24=4.48USD/MNQ for further design work. Retain failure; no
stop/window/side/threshold rescue. Missing-path limits remain visible even if
known endpoints permit descriptive gross arithmetic.

If gross passes, evaluate frozen stopped primary and always-long control on
design. Design indication needs100resolved primary events, positive total,
trade t>=2,dailyNW5t>=2 and at least4/5positive years. A failure blocks book
promotion work. Because this is the user's ONE fixed-rule historical
reconstruction rather than a model-selection program, one2023+descriptive pass
of the already frozen primary/control may still be produced after recording
design failure; it is labelled historical diagnosis, NOT a rescued validation
pass. Commit the design disposition/unchanged selection before that pass.
No alternative is nominated and failed design is never retroactively cleared.

Full significance is trade t>=metrics.t_threshold(current rankedN) ORDSR>=.95,
positive2018–22 AND2023+, source/execution integrity, same-exit placebos and
independent review. Record currentN and DSR basis; neither erases unknown author
searches or overlapping prior families. Compute dailyNW5 and dependence checks,
not just selected unadjusted t. No PowerLanguage before all relevant gates.

## Controls, resampling and books

After an indicated design pass run immediate current-book BASE, ADD1MNQ,
REPLACE VaultBreak with GAP1MNQ, and EMPTY VaultBreak on identical covered dates
before further robustness. Use current personal19/daily marks and inherited
implementation/coverage limits; do not represent daily-book proxies as joint
intraday accounts. Pair5000one-year252day histories,20dayblocks, seed2026102701.
Require positive paired median profit and return/DD gain versus BASE AND EMPTY
without worsening DD95, or a valid funded/evaluation improvement. Report all
nominal gains, even when the frozen gate fails. No seed/size rescue.

Report explicit eligible/limited/not-run dispositions for personal,50K/150K
funded and50K/150Kevaluation. Reuse current shared bootstrap/account engines
only with valid joint paths. Missing paths forbid invented pass/payout gains.

Fixed additional diagnostics after immediate design bench, or as clearly
nonpromotion requested historical analysis on a rejected design:
- Same-exit random side and random intraday entry on the SAME intended gap
  dates,1000paths each, seed2026102702/03; keep IDs/times/sides. Random-time
  entries uniformly from observed valid opening minutes08:31through14:00CT
  (early:through11:00),100point stop, same scheduled session exit. Do not redraw
  based on outcomes. UNKNOWN sampled paths remain unknown, not resampled away.
  Use plus-one p for total and mean; random-side/time each needp<=.05.
- Gap as a filter: total BASE/all-long, KEPT/down-gap, REMOVED/other profit;
  1000year-stratified random subsets preserving kept counts, seed2026102704.
  Retain selected IDs and daily paths; compare totalprofit/DD, not mean alone.
- Shared metrics Sharpe/Sortino/PF/Calmar/Ulcer, maxDD from initialzero, win,
  trade t andNW5, daily Sharpe including KNOWN no-trade dates, long/short/year,
  native fees/slippage bridge. Unknown coverage never becomes a zero.
- Shared resampling/blockMC/permutation. One-year standalone MNQ trailing
  diagnostics are NOT account-improvement or reliable intraday-breach claims.
- Source-window2020-12through2025-11 and ex2025 are descriptive slices of
  the same fixed ledger, not extra selected hypotheses or freshholdouts.

No2025/volatility/gap/stop optimization. No implementation of the unspecified
VWAP engine or inference that the combined charts can be replicated. Final
report/ledgers/code stay in the authorized Codex paths with actual run IDs,
all source limitations, counts and a concrete verdict.
