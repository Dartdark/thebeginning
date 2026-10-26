# H04 RS classified support: frozen gross-first research plan

Mechanism before data: `agents/codex/evidence/hunt_v2_next_new_input.md` (TEST for this finite
preregistration). Source/history: `agents/codex/research/hunt_v2_next_new_input.md`. Work on codex/work.
No new input rows or returns have been opened for H04. Commit this plan before them. Root owns counters.

## Parent, input and clocks

Use adopted RelStrength_v3 defaults, not an optimization winner. Pin7f0800f exact
`funded_strategies/NQ_Relative_Strength.txt` SHA256
20882cb3486ccbd60801572fa72f984161d408b89bc1621142e131de86292ffc and the original source SHA256
d819039cd0aedb33aa730f4b3b723adcc3169d10f4e9fa57c351e4652dc79b61. Archive both with Git blob IDs.
No source strategy file is changed. Current personal19 is both sides1MNQ; funded50K long1,
150K both1 with source cushion rules; evaluations do not adopt RS. Native NQ prices proxy MNQ fills.

Pre-data state clarification: literal source DayOK governs EWMA and stored-range history. Additional
shared calendar exclusions affect entry eligibility only, uniformly, and do not rewrite past state.
EWMA has unbounded recursive memory: an unresolved eligible historical NQ/ES return pair or stale
anchor remains an EWMA lineage issue at every later decision. It does not expire after20days or
1950updates and is not repaired by normalization/reset. Stored-range uncertainty leaves only when the
actual affected slot is overwritten in the20slot buffer. Missing ES at a primary timestamp cannot
silently become an admitted synchronized price through forward-fill.

Replay literal observed-bar parent signal: RTH close labels511..900, NewRTH anchors to immediately
previous observed Data1/Data2 closes, normally08:30. Store eligible prior RTH ranges, mean of up to20
stored ranges; no true-range ATR substitute. EWMA alpha2/(20*390+1), first admissible pair initialization,
covariance/variances updated on eligible RTH bars,1950updates minimum. NBA is the actual observed RTH
bar count. Decide once at09:00, Z as exact source, >=1.25long/<=-1.25short. One fill/day, next native
09:01bar OPEN (wall09:00). Missing09:00/09:01 is unresolved, not a later entry chosen by convenience.
Reconstruct source calendar, then apply the shared full-holiday/early-close/mourning/weekend exclusions
uniformly to all replay models. Preserve literal state/history and disclose differences from MC.

FLOW15: sum buy-classified `volume` minus `downvol` over exactly15OF close labels525..539
(08:45..08:59CT; source ET minus60minutes). Every minute must be valid, finite/nonnegative,
volume==upvol, upvol+downvol==native total, close within one NQ tick, positive aggregate total.
DROP only side*D<0. Valid zero is KNOWN KEEP; incomplete/invalid/mismatched/zero-total is UNKNOWN KEEP.
There is no partial sum, size change, alternate entry, freed cap or inferred participant identity.
The last feature event closes08:59; assume1minute availability allowance to09:00decision. Receipt is
unverified. This is a prospective convention; no favorable latency variant may replace it.

PRICE15 unselectable control: P=C539-O525 from the identical complete native15-minute window.
DROP only side*P<0, valid zeroKEEP, invalidUNKNOWNKEEP and flag. Own full-opening sign for later
matching is sign(C540-C510). This preserves known RS own-direction selection history.

Source input scope for first admission/gross: owned NQ DAY2017feature archive at
`agents/codex/inputs/ob_v2_bench/NQ_1min_2017.csv`, data/NQ_1min_2018..2022.csv,
data/ES_1min_2017..2022.csv, and data/OF_1min_2018_*..2022_* annual parts. Exact explicit file inventory,
headers, size/SHA and source/dependency hashes bind before values. Native2017 is feature-only from
2017-09-01; no2017performance or2023+ prices/OF/MC outcomes. Use Grid24 in isolated Codex caches;
deduplicate only identical source rows with IDs retained; conflicts veto admission. Do not load broad
shared caches/pickles or silently forward-fill OHLC/ES/source quantities.

## Five definitions and budget

1. REPLAY_BASE: protected parent, both sides,1MNQ.
2. FLOW15: fixed primary parent subset.
3. PRICE15: unselectable price-only control.
4. DELAY_BASE: extra1minute activation delay, conditional stress only.
5. DELAY_FLOW15: same delay on the primary, conditional stress only.

Only first3 stopped definitions can run after gross PASS. Delay pair only after design and immediate
book bench PASS; never selectable. PUBLISHED is source/ENTRY metadata reference only: no new standalone
MC financial repricing/model. Later published-book versus replay accounting is a disclosed baseline
implementation comparison. Four-tick-per-market/stop cost stress reprices identical positions; no new
position selection. All diagnostic paths/controls remain in selection history.

Checkpoint3/60economic evaluations,3/10registered hypotheses,2gross screens; archived t6=65.
Registration makes H04 the fourth hypothesis. Entry admission adds0gross/economic screens; raw gross
adds1screen/0economic evaluations. Stopped BASE/FLOW/PRICE adds3economic evaluations; conditional delay
pair adds2 if actually run. Retain every failure and exposure. No <=3variant promotion exception.

## Entry/source admission before raw endpoints

Implement and source/synthetic review the entry-only reconstruction before actual run. Bind exact
code/plan/evidence/archive/dependencies at a committed revision and require codex/work, exclusive lock,
write-once artifacts, no unchanged rerun/alternate directory, input/hash recheck and verified marker.

Audit native/ES dates, clocks, DST convention, duplicates, OHLCV validity, observed-bar alignment,
08:30anchors, prefix counts, warmup, stored-range completeness/lineage, normal/half-day/full-holiday
calendar and source gaps. Missing native/ES reference or held bars remain unresolved, not zero returns
or profitable deletion. H03's already observed gaps are context, not an inherited verdict or permission
to repair this new parent's data. Literal observed-bar state is reconstructed, with every reference
gap flagged; require zero unresolved reference/decision/entry/held-event issues for gross admission.
Do not assume a common gap is an exchange halt without a bound source calendar proving it.

Existing RS MC workbook may supply ENTRY metadata only for2018–22: date, entry type/side, entry price
and time if present. Read selected columns only, filter dates before converting prices, never exit,
gross/net, commissions or trade P&L. Compare first event/date against parent date/side/entry within
one tick, require >=90% each direction in fixed jointly observed eligible calendar, retain every
unmatched record/reason. Do not use an outcome-dependent universe, timestamp offset search or tolerance
relaxation. A missing necessary field is unresolved, not invented parity. Archive parser conventions.
Required MC fields are date, entry type/side and entry price. MC time is optional as stated above:
when an explicit time/date-clock is present it must parse and match native label541 exactly, with
no offset search. A missing optional time is recorded MC_CLOCK_NOT_VERIFIED, never fabricated09:01;
date/side/price admission may still proceed without claiming independent MC clock parity. The native
source/decision/fill clock remains fully audited. A malformed present clock is unresolved. Read XLSX
through selected raw XML cells so excluded price/exit/P&L/future cells are not implicitly converted.

After entry/source PASS, attach only fixed raw no-stop endpoints OPEN541 through CLOSE900 (15:00CT).
Require every endpoint and held minute observed/valid, known flow on>=90%parent entry days, at least
100kept FLOW15 events, and mean FLOW15 gross>=4.48USD/MNQ. Raw market RT cost assumption1.24commission
+2*.50adverse fills=2.24; hurdle2x=4.48. Gross gate is not net significance. Save BASE/FLOW/PRICE and
kept/removed counts, mean, SD, SE, t and totals by side/year. Admission failure saves pre_gross marker
with0raw returns/0newgrossscreens; raw gate failure closes H04 before stopped/bench/2023+.

## Stopped design and immediate book gate, only after gross PASS

Reuse shared execution, metrics and resampling. Same parent stop.6/target1.0mean range, protected
from entry bar, stop-before-target in ambiguous bars, worse gap stop fills. Conservative order ticks:
long stop floor/short stop ceil; long target ceil/short target floor, tick.25. Target needs1NQpoint
trade-through; no target slippage, entry/flat/stop adverse.50perfill/MNQ plus1.24RT. Close900time exit,
no hold after15:59CT, source/shared holiday/half-day skips. All changes apply to all replay models and
are implementation effects against the published book, not filter alpha. No PowerLanguage now.

Frozen cheap design PASS: FLOW15 has>=100trades, positive total, trade t>=2 and daily NW5t>=2,
>=4of5positive years and positive total excluding any single year; kept total>BASE total, removed
total<0; primary total>PRICE15 control total. Save all five metrics, side/year, base/kept/removed
averages/t and1,000matched subset paths plus IDs. Subset strata fixed year,side,entry_j,flow-known,
own full-opening sign and same-window price sign (including explicit unknown/zero categories);
no post-result pooling of sparse strata. Seed2026102604. Require actual primary to beat>=90%subsets
jointly on strictly higher total profit and strictly lower maxDD. Subsets are diagnostics, not an
executable book. A failure stops this hypothesis's later gates, not the hunt.

Immediately after design PASS, before other robustness, compare current personal19 on identical
2018–22dates/whole contracts: published BASE, RS-slot EMPTY, REPLACE RS by protected BASE (repair
control), REPLACE by FLOW15, and ADD FLOW15 to published BASE. Do not call implementation repair alpha.
Use fixed1year252day/20dayblock/5000paired histories, seed20261026, shared personal engine. Require
at least one candidate ADD/REPLACE to improve return/DD ratio versus BOTH published BASE and EMPTY,
with positive paired median annual profit difference and nonworse paired95%DD; REPLACE must also
beat protected-base repair control. Publish all rows, paired differences/intervals, aligned VB/DT/RS
correlations and source fee/mark/coverage envelopes frozen before bench returns. Candidate gain must
survive bounded implementation uncertainty. If a required bound cannot be supported, that claim is
LIMITED rather than a pass. Missing current joint funded/evaluation paths prohibit pass/payout claims.
Use current definitions; cutoff cannot exceed observed joint book coverage (currently2026-07-07).

## Only a surviving book candidate advances

Then freeze/commit selected FLOW15 and matched REPLAY_BASE control BEFORE2023+ once. Call it previously
seen historical validation, never a fresh holdout; no other variant/PRICE15 future outcome or retuning.
Full2018–26 native-cost trade t must clear metrics.t_threshold(N_items) from current pinned ranking
OR DSR>=.95, both design/validation positive. Retain earlier RS~170 and OF/Bridge/H01/H03 searches,
all hunt counters and prior65t6; also report broader multiplicity sensitivity. No selected headline
can substitute for dependence checks. Freeze same-exit random-time and random-side placebos, each
p<=.05, use shared resampling/MonteCarlo at real size, fixed delay/cost stresses and fresh independent
raw-spec checker before promotion. Missing raw-spec/joint paths stay limitations. Only after all
applicable gates pass create a Codex PowerLanguage draft for Claude's MC review, never live deployment.
