# Hunt v2 H01: LDF long-side delta confirmation

Evidence: agents/codex/evidence/hunt_v2_ldf_delta_confirmation.md. Task source92b1d4c.
This is a disclosed revisit of a result-selected filter against the CURRENT book, with an explicit
causal/completeness correction. It is not a new forced-flow discovery or fresh holdout. Old selection
among roughly40splits and the failed old funded benchmark remain part of its history.

## Fixed mechanism, clock and gross-first gate

Daily-reset leveraged/inverse ETFs can require same-direction exposure adjustment after a large index
move. Last30minute aggressive pressure might distinguish that demand from opposing information-driven
selling. Neither fund inventory, actual orders, hedge fraction nor compulsory NQ flow is measured.
An opposing tape can instead predict reversal only after the current book has already lost; no hedge
or before-breach diversification is assumed. No filter threshold is fitted.

Use canonical5-minute LDF: exact native08:31minute open (08:30wall-time cash open),14:00completed close,
absolute daymove>=0.40*prior15STOREDweekday ATR, direction=sign(daymove). Daily TR/shift use shared
Grid24.daily_atr(15), based on date bars and previous observed close, not exact15calendar slots.
Source2018-22day+overnight files only; no2017warm-up. Retain initial15stored-date warm-up exclusions.
Never use g.trading or later-day OF availability to decide eligibility. Native labels are CT closes;
Bridge OF labels are Eastern closes, subtract60minutes. Receipt latency is assumed, not observed.

The primary cheap screen is RAW_NO_STOP: signednative14:01-labelled minute OPEN through14:30CLOSE,
with no stop, target, commission or execution simulation. The first open is14:00wall time after the
14:00decision, with no additional full-minute latency; disclose this limit. The0.25ATRstop belongs
only to the later counted design. Do not choose a different window/receipt lag after seeing gross.

Before data, freeze primary gross gate: >=100STRICT30-kept design events and mean raw gross per1MNQ
>=2*$2.24=$4.48, where2market fills cost$1.24RT+$0.50each. Report BASE/kept/removed gross, t, both
sides and every design year. Other gross rows are diagnostics, not alternate winners. Incomplete held
windows remain in the unresolved-event audit and BLOCK gross promotion; do not silently delete them.
Audit complete valid OHLCV08:31..14:00 and every14:01..14:30held minute, native duplicate conflicts,
ATR references, normal calendar and replica.is_early_close (includingJuly3/December24). No future repair.

A failed gross gate stops H01 with0counted economic evaluations and1hypothesis. Retain its gross result
and statistical-selection history separately. A gross pass authorizes only the frozen design below.

## Three configurations, fixed selection

BASE: canonical LDF, one trade/day. PRIMARY STRICT30: drop a LONG only when all30completed OF minutes
13:31..14:00have valid finite nonnegative upvol/downvol, positive total, valid source OHLCV, source/native
close agreement<=0.25point and exact nativevolume=upvol+downvol, and sum(upvol-downvol)<0. Unknown,
zero or positive flow retains BASE; SHORTS always remain. No future source availability is used.

LEGACY: diagnostic/unselectable original partial-window np.nansum(OFvolume-downvol), with missing/zero
retained. Repair its whole-day-any-OF check to ANY-OF-AS-OF14:00 only to remove future availability.
Audit volume versus upvol differences. This is a disclosed causal diagnostic, not an assertion of literal
old-ledger parity. STRICT30's completeness correction is a new counted model, not a renamed old result.

After gross passes, count all3evaluations (BASE, LEGACY, STRICT30), including the repeated base/legacy;
one new strict formula. No both-sides filter, threshold, entry clock, size or exit variants. LEGACY can
never be nominated if STRICT30 fails. Start v2 budget0/60evaluations, H01is1/10hypotheses; old t6is65
evaluations/63unique, unchanged. Stop the hunt at60counted evaluations OR10hypotheses.

## Counted design and immediate book test

Design2018-22 only. BASE uses shared execution with stop0.25prior ATR rounded UP to0.25points, active
on entry bar, worse-gap stop fills, no target, exit14:30, one/day; no BE/trail/queued signals. Thus
target-through is inapplicable. Keep all failures and complete data/clock/half-day audits. Fees per
MNQ$1.24RT+$0.50market/stopfill; NQ$7.25RT+$5fill diagnostic, plus fixed4tick-fill stress. NQ-price
micro modeling does not establish native MNQ listing/parity/spreads/receipt or broker quotes.

Primary cheap design gate: >=100kept trades, positive net, trade t>=2, dailyNW5>=1.5, PF>=1.20,
>=4positive design years, positive4tickstress. Filter must keep >=BASE total net, remove negative
total/mean net, and beat >=90% of1000year/side/signal-hour matched random subsets jointly on total
profit and drawdown. Store selected IDs and paths; subset diagnostics are not executable portfolios.

On design pass, run CURRENT personal19 bench immediately, before expensive robustness. Source roster
92b1d4c equals retained afde088: STv3/PTv2in, BB_MRMout, each current piece1micro. Verify saved fee1.24
baseline/source bindings rather than importing stale funded defaults. Use design2018-22 only first;
do not let a full-book bench expose future candidate returns before selection freeze.

Rows: BASE current19, ADD one STRICT30 micro, EMPTY remove one LDF micro, REPLACE LDF1withSTRICT30one.
Preserve whole contracts, identical calendar/coverage/fees and paired indices. Historical daily return/DD
and shared MC252day horizon,20day blocks,5000draws,seed20261026; report paired intervals. A candidate
must beat BOTH BASE and EMPTY in historical and median-MC return/DD on at least one frozen ADD/REPLACE
row to continue. Treat gains smaller than baseline fee/mark/coverage uncertainties as unresolved, not
invented utility. No Apex pass/payout claim from published daily curves or defective joint paths.

## Selection, validation and remaining gates

If design or early book gate fails, close H01; no2023+ candidate access, retune or LEGACY nomination.
If both pass, COMMIT STRICT30selection and the bench disposition before running ONLY STRICT30andBASE
on2023+ once. Call this previously seen historical validation. Freeze common book-coverage end at
2026-07-07 for comparisons because the retained OT baseline ends then; later candidate-only returns
may be reported separately, never as invented complete-book history. Initial warm-up coverage is shared.

Full native-cost promotion requires positive design/validation and net t>=metrics.t_threshold(N_items)
OR DSR>=0.95; report repository/cumulative/unknown search history, including gross screens separately.
Random-time and random-side placebos with identical exits each need p<=0.05; filters also retain all
1000matched-subset evidence. Standard five metrics plus side/year, dependence, selection and MC at
actual plan size, exact half-day/holiday exits before15:59CT and a fresh independent checker remain.
No trading approval or PowerLanguage before all gates. If it passes, draft PL under agents/codex/ for
Claude's MC check; never alter live/shared plan files. No further t6 research or t6 alerts follow H01.
