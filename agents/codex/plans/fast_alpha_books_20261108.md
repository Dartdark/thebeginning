# Preregistration: current-book fast-alpha execution timing

Summary: One common rule across24fixed parent streams; no parameter search or new strategy-selection universe.
Compare unchanged source timing, delayed entry, and delayed entry plus stop/signal liquidation.
ENTRY−BASE attributes entry timing; BOTH−ENTRY attributes the additional exit policy (not an exit-only test).
Design2018-04-02–2022-12-30first; unchanged2023+historical validation and account stages only when earned.
Research only. No source/live strategy, account settings, ranking, allocation or paused-program changes.

## Identity and scope

Program `user-fast-alpha-books-20261108`; evidence `../evidence/fast_alpha_books_20261108.md`;
config/inputs/lease/trials in`../inputs/fast_alpha_books_20261108/`.
Exact runner `analysis/codex_fast_alpha_books_20261108.py`; no import-time prices or returns.
Current source pinned in config, including November8 capped Twin and early-close NBL updates.
This is the user's explicit cross-book request, following the separate direct-user N15 experiment precedent;
it does not spend/reset the autonomous scout or earlier evaluation sizing budget.

Five reserved definitions per parent,120maximum total, including baseline and gross/design screens:
`BASE`, `ENTRY`, `BOTH`, `RANDOM_DELAY`, `RANDOM_DROP`. Two candidate variants, two unselectable null controls,
one baseline. No other waits, parameters, sides, bands, stops, hold windows or bracket geometries may be selected.
Repeated source generation/engineering reruns preserve every earlier view and are not free research resets.

## Frozen execution interpretation

Original strategies continue virtually, supplying the same entry/exit intent stream. Child fills are the
object of the experiment. This makes the retained parent state an explicit architecture, rather than falsely
calling unchanged realized exits a regenerated strategy with new entry-anchored stops. Parent bracket price
levels and virtual future decisions are not recalibrated to the child fill. Any implementation that recomputes
those levels or refits signals is outside this study. Source/report intent clocks remain conditional until checked.

BASE: existing parent ticket, native gross cash, original limit/market cost categories.
ENTRY: after an original entry event, wait for the first fully observed five-minute close-to-close return
against its side, strictly after the original event minute. Execute next minute open with one adverse tick.
Cancel if the virtual parent exits before that fill. No maximum wait fallback chosen from old15/30/60results.
The first qualifying pullback can be above the old buy price/below the old sell price: no favorable-price filter.
Then follow original parent exits. Existing target limit must be qualified after actual entry, never before it.
BOTH: same entry policy; delay original stop/band/reversal-signal liquidation until the first completed
five-minute return in the position's favor, then next minute open. Preserve fixed time/holiday exits and
target requests; they are not delayed. Hard deadline fields are fixed in config and runner. No new disaster
stop is optimized; realized loss can exceed the original stop. Record every extra held minute and suppression
of another parent entry while actual execution is still pending. Account kill/floor/DLL are not deferred.

Regular source flatten clocks: VB/ONB/LDF14:30; EOS10:00; NFP09:00; MON/RS/MOC/S4715:00;
FC2B14:59open; DT14:56open; ST15:00open; PT14:55close; NBL14:31open; CL Monday09:00;
Kusho21:00; Twin BO15:45close/MO14:51open; source holiday exceptions retained. S30 has no artificial daily
flat introduced. Final unavailable exits remain unresolved, not last-known marks. Clocks are Central.

## Inputs, data and costs

Config hashes only owned2017–22raw inputs for this first stage. Do not read future prices to repair design.
Reuse Grid24; never forward/backfill minute prices or construct returns through unknown held intervals.
Skip only frozen documented closed minutes (normal maintenance, dated index pause, weekend), not arbitrary
missing observations. Every five-minute signal needs all required closes; incomplete earlier waiting data is
UNKNOWN, not an excuse to choose a later prettier bar. Original entry/exit must trade inside their source minute;
same-minute crossing order is checked on the existing common OHLC convention. Limit targets require trade-through.
Original source roll-adjusted cash is preserved only when altered entry/exit intervals avoid the frozen quarterly
roll clocks; unsupported changed-roll intervals are UNKNOWN. No synthetic roll profit or native micro quote claim.

Main/stress costs and instruments are fixed in config. Report total gross, fee, slippage, net and stress net;
no double-charge of RT fees. Changed limit entry pays market execution cost. One micro is a diagnostic unit,
not actual funded sizing. Saved source gross is reconciled before and after endpoint changes.

## Design decision, controls and reporting

Keep all source tickets in result files. Standard table for whole/long/short, every design year and total:
trades/win/average/total/t, Sharpe/Sortino/PF/Calmar/Ulcer/maxDD; paired incremental t/DSR, missed/UNKNOWN counts,
cost bridge/stress, entry/exit delay and extra adverse exposure. The closed-ticket daily series is explicitly a
**common complete-ticket contribution**, not full market-to-market equity or a funded-account daily proxy.
Publish known conditional descriptive results even when the full data gate fails; never promote that subset.

Cheap pass per candidate requires every gate in the evidence sheet, including zero unresolved tickets.
Multiple-testing n includes root registry rows +120project reservations +at least58earlier fast-alpha looks;
unknown author/family selection is disclosed. No long/short optimization. If both pass, select greatest total
paired design effect, ENTRY wins ties. Commit disposition/choice before any control/historical validation.

Conservative numeric floor for earlier repository selection is10,000definitions (rather than only registry rows),
then add120project reservations and58prior fast-alpha looks. This retains the known2,965evaluation configurations,
roughly3,700S47settings and other prior selection; uncounted author/repository multiplicity remains disclosed.

Only then implement/commit the two already specified nulls before their outcomes:1000causal random delays
(sample only previously matured candidate delays, fixed5min seed fallback) and1000same-year/side random drops
matching the candidate's missed tickets. Required: incremental total positive with paired uncertainty, beat
95%of delay controls, removed tickets lose on average, and beat95%of random drops on profit and DD. Preserve
stochastic histories as one fixed policy each, not tunable seeds. A failure stops the parent without a new variant.

Historical validation reads only the selected unchanged rule once on previously seen2023+; all signs, native
costs, path gates and multiplicity remain. Independent raw-spec/intent reconstruction and exact current-book
native BASE/ADD/REPLACE/EMPTY comparisons are later gates, not inferred from these diagnostic ticket curves.
Actual book sizes, funded cushion state and account first-passage/expiry rules must be identified. Prior weekly
account-engine findings are binding; do not reuse flawed legacy pass rates. Missing baseline inputs yield UNKNOWN.
Only earned survivors proceed, with frozen forward/platform parity pending as appropriate. No allocation follows.

## Reproduction/continuation

`python analysis/codex_fast_alpha_books_20261108.py selftest` uses invented arrays only.
`python analysis/codex_fast_alpha_books_20261108.py design --commit COMMITTED_SHA` verifies exact bytes,
input hashes,120reservation IDs, an unexpired two-hour project lease and HEAD/origin/FETCH_HEAD equality first.
Commit/push preregistration and reread the published claim before returns. Lease renewal retains owner/run and
old selection history. The scout gate is hard-coded to a different program; do not falsify its identity or ledger.
This dedicated user-code admission enforces the corresponding commit/hash/lease boundaries for this project.
Stop genuine failures, preserve artifacts and checkpoint the same project if execution/context is interrupted.
