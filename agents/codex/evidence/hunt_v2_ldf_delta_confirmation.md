# Hunt v2 H01: LDF long-side delta confirmation — TEST the bounded confirmation

Summary: Revisit the user-named LDF/order-flow lead against the CURRENT book, with native MNQ fees.
This is selected prior research, not a newly discovered signal or fresh holdout. The old funded bench
did not improve. A strict complete-window correction is frozen before outcomes; the old partial-window
version is an unselectable diagnostic. Gross-first design can stop the idea before counted evaluations.

Sources, definitions only: analysis/orderflow_ldf_filter.py; analysis/orderflow_test.py;
tools/exporters/OFB_OrderFlow_Exporter.txt; analysis/es_forced_flows_test.py;
agents/codex/research/hunt_v2_flow_novelty.md; current Claude TIER_LIST and task at92b1d4c.
This sheet was written before any new raw-data, price or strategy-return inspection for this hypothesis.
Parent owns preregistration, execution and progress. No economic test has run from this sheet.

Planned budget: **1 v2 hypothesis / 3 counted design model evaluations IF the gross screen advances**:
STRICT30 selectable, BASE reference, LEGACY unselectable diagnostic. Failed cheap gross screen:0counted
economic evaluations, separately retained as a screened hypothesis. No other window/threshold/side/size
variant. Earlier t6 programme65evaluations/63unique rules, the OF search and unknown older trials remain
part of the selection history; v2's60/10budget is not a reset of statistical multiplicity.

## 1. Who trades, and what forces or causes the trade?

The underlying LDF rationale is daily leverage reset by leveraged equity ETFs near the cash close.
A simplified target-leverage fund's rehedge sensitivity is proportional to L(L−1)×lagged assets×the
underlying return. That predicts same-direction pressure after a large intraday move under its stated
assumptions. Actual creations/redemptions, exposure, derivative netting, existing hedges and execution
schedules can change the quantity. This study measures none of those fund obligations or actual orders.

The added prediction is weaker: negative net aggressive tape before a LONG LDF entry may indicate
opposing/informed demand, rather than the scheduled reset flow dominating that session. Filter those
longs while leaving shorts unchanged. Aggressor volume is not tagged ETF demand, dealer inventory or
evidence that a participant must trade. The known schedule is the underlying LDF prior, not proof that
the sign filter adds alpha. This is a bounded confirmation of an explicitly requested open lead.

## 2. Direction, size and timing known before entry

Preserve canonical LDF: completed cash-session move magnitude at least0.40prior ATR, follow its sign
in the fixed late-day window, original0.25ATR stop/time exit. Root must bind the canonical implementation,
exact clock and trade eligibility in the preregistration; no exit, side or size optimization is authorized.
The existing source uses the last30completed OF minutes immediately before the native entry index j0,
indices j0−30 through j0−1. This is a30-minute information window, not a new30-minute trading chart.
Underlying eligible strategy signal timeframe stays within the user's1/5/15/30minute set.

The old loader treats source labels as Eastern closes and subtracts one hour for CT. Native minute
bars are close-stamped: a bar's label differs from the wall time of its open. Original MC timestamps,
source availability, signal completion, order time and fill must be reconciled explicitly. No actual
historical receipt latency is measured by the CSV. Never use the entry minute's completed flow, a
later snapshot, future session membership or a backward repair to decide the filter.

There is no dollar-flow estimate, hedge fraction or new quantity rule. At the bench use the CURRENT
plan's whole-contract LDF size, with fixed candidate/reference quantities. No winner-dependent resizing.

## 3. Does the flow reach the traded contract or its direct hedge?

Both the underlying rule and observed tape concern NQ; MNQ is the intended cost/exposure unit. NQ can
hedge Nasdaq equity exposure, but neither the parent fund's actual instrument choice nor incremental
NQ demand is identified. Native MNQ execution is not established by scaling NQ gross dollars.

The filter removes some existing LONG LDF exposure; it does not add an independent stream. Shared NQ
positions net in one account. Any benefit must survive whole-book chronology and actual contract sizes,
not an annual correlation headline or a separate-account hedge.

## 4. New information, literal old rule and frozen engineering correction

| Input | Source definition | Availability limit before returns |
|---|---|---|
| Canonical LDF entries/exits | Current adopted source and shared execution engine, frozen by root | Bind version, native CT clocks, full eligible days and early closes; no old-roster substitution |
| Aggressive buy/sell quantities | OF_1min exports and original exporter definitions | OF volume is buy volume, not total; use correctly bound buy/sell fields, not a cumulative-delta difference |
| Native audit/execution | NQ native one-minute OHLCV and shared grid | Require audited exact clock/quantity alignment; NQ prices remain a micro fill proxy |
| Current book and benchmarks | Current adopted personal/funded/evaluation definitions and repo engines | Joint inputs and MC parity must be verified; missing paths are limits, not proxy payouts |

**Literal LEGACY rule:** analysis/orderflow_ldf_filter.py calls T.wsum, implemented as np.nansum, over
the30prior bars when ANY OF data exist somewhere that day. A fully missing/zero sum becomes0/NaN and
is retained, but a PARTIAL window sums the available values and can remove a long. The old rule keeps
all shorts and drops a long only when agree30==0. This is not a complete-window filter.

The preregistered diagnostic repairs that whole-day existence check to ANY OF available AS OF14:00.
It uses original OFvolume-downvol partial sums; STRICT30 uses upvol-downvol with the native checks.
Differences between volume and upvol remain audited. The diagnostic therefore preserves the old
predicate subject to a disclosed causal repair; no literal old-ledger parity is claimed.

**Selectable STRICT30 correction, explicitly frozen before outcomes:** all30completed source minutes
must have valid finite nonnegative buy/sell quantities and positive total quantity, source/native close
agreement within one NQ tick, and exact native total-volume agreement. Finite valid native/source prices
and unambiguous timestamps are required; no silent duplicate overwrite or NaN aggregation may certify
completeness. If the complete source window cannot be established, the filter state is UNKNOWN and the
original BASE trade is RETAINED. Balanced valid net flow (sum delta=0) is also retained. A valid negative
sum removes a LONG; a valid positive sum keeps it. SHORTS are unchanged. No magnitude threshold exists.

This is a NEW counted engineering correction to the old filter, not an equivalent reproduction. Root
will retain LEGACY as an unselectable diagnostic plus unchanged BASE, for3counted models after a gross
pass. If STRICT30 fails, do not nominate LEGACY or change the completeness/sign policy. Preserve all
unknown/zero/partial counts and the exact causal evidence attached to each decision.

## 5. Costs and actual intraday gaps

Task MNQ assumptions:1.24USD roundtrip plus0.50USD per market/stop fill; two market fills cost2.24USD,
so the gross-first2×hurdle is4.48USD per MNQ. NQ reference assumptions remain7.25USD roundtrip plus
5USD per such fill. These are research assumptions, not newly verified broker quotes. Compute native
micro costs separately; target-fill versus stop/time-fill counts can change per-ticket costs.

Use the canonical execution engine with entry-bar protection, worse gap fills and target-through when
applicable. No passive improvement or fill-on-touch benefit is assumed. A missing held minute cannot
become a known closure. Real spread/receipt/roll and micro listing/parity limits remain explicit.

LDF overlaps the existing late-day book by construction. The task's01:00–03:00CT empty window is not
this candidate's window, and the study cannot claim that it fills an empty time slot. Test all eligible
LDF events before account-level overlap; do not select dates when another strategy happens to be flat.

## 6. Power and gross-first stop

Prior ranked work establishes an existing multi-year LDF sample, but no new event/retention count is
known before this sheet. Complete OF coverage, unknown retained states and the number of eligible long
removals must be censused without using future information. Correlated daily trades and selected prior
research reduce effective evidence; the nominal ticket count is not effective sample size.

The frozen primary gross screen is RAW_NO_STOP on2018–22 only: signednative14:01-labelled minute
OPEN through14:30CLOSE, no stop, fees or simulated execution. The0.25ATRstop applies only in later
counted design. Require>=100STRICT30-kept events and primary mean gross>=4.48USD per MNQ. Report
BASE/LEGACY/STRICT kept/base/removed gross, t and both sides/year; diagnostics cannot nominate a winner.
Use2018–22native day+overnight inputs, NO2017warm-up; the prior15STOREDweekday shifted ATR and its
initial warm-up exclusions are explicit. Incomplete held windows remain audited and block advancement.
If gross is below2×cost or quality/count fails, retain the failed screen and0counted evaluations.
Do not select a more favorable window, side, unknown-state policy or old diagnostic from that result.

Only a gross pass permits the3frozen counted model evaluations. Promotion later requires the actual
metrics.t_threshold(N_items) or DSR>=0.95 at native micro costs, positive design and2023+historical
validation, not an approximate3.6headline, per-trade average lift or a design-only t. No effect-size,
power or pass probability is estimated by this sheet.

## 7. Already tested and falsifiers

The original lead was selected among roughly40OF splits. The old filtered-LDF result and old funded
benchmark failure are recorded in latest TIER_LIST. analysis/orderflow_ldf_filter.py tested long-only
and both-side agreement filters and changed size; broader Bridge scans add still more selection.
Known2023+history is previously seen replication, never a fresh holdout. Preserve that history even
when the current benchmark differs. No claim of novel standalone alpha follows.

Refute the proposed utility if STRICT30 fails the gross/design gate, removes profitable exposure
without improving total profit/risk versus matched removals, loses significance after native fees,
depends on partial/late source windows, or cannot improve any current plan versus both BASE and EMPTY.
Freeze and commit selection before one selected-rule/control2023+run. No retuning after that run.

After a design pass run the repo plan benches immediately, before spending on further robustness.
Use paired current-plan paths for addition/replacement/empty slot; a separate simultaneous extra copy
of the same LDF leg must not be mistaken for a filter. If no plan improves, stop this candidate.
If it survives, random-time and random-side placebos need the same exits and p<=0.05. The filter also
requires total kept/base/removed profits and at least1000matched random subsets (with deterministic
seeds and preserved paths). Dropping winners can raise average trade profit without helping the book.

## 8. Failure and diversification

| Question | Prediction before new returns | Evidence needed or refutation |
|---|---|---|
| What stops the mechanism? | Tape is informed, quantities stale/partial, scheduled flow absorbed, or ETF exposures change | Native/source coverage and clock audit, frozen gross/design and controls |
| Liquidity role | Original market entries/stops consume liquidity; removing a trade saves those costs | Conservative actual fill counts and native cost stress |
| Loss clustering | Persistent trends, late news, gaps and OF outages can align missed winners or retained losers | Side/year, missing-state and chronological stress/MC |
| Common losses | Shared NQ cash momentum with VB/DT/RS and unchanged LDF; low correlation is not assumed | Current book joint losses and covariance after a candidate exists |
| Before-breach offset | No offset is established; skipping a ticket can remove useful income before another leg's loss | Whole-contract paired account chronology versus BASE and EMPTY |

No new stop, target, time exit, size or concurrency is optimized. Retain original LDF risk limits, native
half-day/calendar handling and same-session flatness before15:59CT for Apex. No holiday fallback may hold
across a halt. Missing input leaves BASE active under the frozen UNKNOWN policy; it cannot be backfilled
from later data. Stops can gap and do not guarantee a breach is avoided.

## Decision and next gate

**TEST this bounded confirmation under root's committed preregistration**, not a new-alpha claim.
Gross-first2018–22; stop locally if it fails. After design success, assess current-plan utility promptly;
then only surviving work earns historical validation/placebo/selection/Monte Carlo and independent checks.
Any qualifying pass still needs Claude's MultiCharts check and a draft under agents/codex/, not live files.
No trading, deployment, purchase, account, external message or shared-plan change is authorized here.
