# Pressure memory: TEST for a prospectively frozen profile extension

Summary: Test whether the preceding120minute activity/flow path adds information beyond the existing three-bar state.
The profile ends5minutes before the current decision; all normalization and fitting use preceding information.
Use the exact existing net-payoff label cache, models, bracket geometry, execution and decision hurdle.
Four definitions compare memory/local features within each estimator; this makes19 newstudy definitions cumulatively.
No new return, native execution, independent factor or portfolio improvement is established by this evidence sheet.

Plan: [pressure_memory_20261110.md](../plans/pressure_memory_20261110.md).
Source implementation: `analysis/codex_pressure_memory_20261110.py`.
This sheet admits only its separately committed design study; it does not permit a missing-data repair or live change.

## Mechanism, participants and distinction

Marcaccioli/Bouchaud/Benzaquen's jump study describes different activity histories around exogenous and endogenous
stock-price events, including a gradual activity buildup before some endogenous events. Persistent aggressive trading
and changing liquidity supply are possible channels. No compelled trader, known signed order or repeatable net premium
is observed in our data. A volatility precursor does not by itself establish the next price direction.

The incremental hypothesis is that a120minute pre-decision activity/pressure profile changes the conditional net
barrier payoff beyond the original three completed five-minute bars. The learner still forecasts both hypothetical
directions and may choose neither. This is a related-family feature extension, not an independent new mechanism or
permission to invert/tune a failed earlier rule. Prior impact-residual, AR-flow, absorption, book and pattern failures
remain part of the selection history.

The source uses one-minute observations (uploaded PDF p.3) and discusses an exponential measure with parameter .12
(p.5). The proposed profile, nine features and NQ transfer are ours. Our normalized signed change u is **not** the
paper's exact jump statistic J. No4.36 jump threshold or future-fitted endogenous/exogenous classification is imported.
Cross-stock sample findings do not supply native NQ or MNQ trading evidence.

## Information clock and matching inputs

For decision close T, use120exact one-minute return endpoints T−124 through T−5, requiring121exact closes T−125
through T−5. Every required price and native buyer/seller quantity must exist and be finite; quantities are nonnegative
and total=buy+sell. No current event-bar constituent T−4 through T enters the added profile. Original local features,
including their current completed bar, are retained. Overlap with the preceding local bars is intentional.

Each date's seasonality uses exact previous20 normal-cash calendar slots, with at least15finite observations per clock.
Finite zero returns remain observations. A positive resulting median is required; positive admitted medians across
all1440clock slots supply the cross-clock normalization. Fit before the date; do not stretch sparse history or include
today. Original shifted ATR, clock/roll/native-data and receipt assumptions remain conditional.

All four definitions share the same profile-known input mask and the original local-feature eligibility. The local
controls keep only their original21features but use exactly the same dates/rows and historical label availability.
No label-validity or future-path condition filters prediction-time eligibility. Historical unknown labels are excluded
from training under the original contract; unknown actual held executions remain visible and stop advancement.

## Costs, risk, training sample and failure modes

Reuse `analysis/outputs/codex_pressure_learning_20261110/features_and_labels.csv.gz` exactly as committed at
`0d61f59e30304a5a9850ef1a20b33a2d1f04cc2d`; do not rebuild labels to favor this feature set.
Those labels implement the same +.3R target/−1R nominal stop with tick rounding, delayed entry, costs, gap losses,
time exits and a full scheduled label-maturity horizon. The costed target is not an assured .3R receipt.

Models fit before each month using the exact previous126 normal-cash dates. Require100represented dates,
10,000valid directional label rows, and50stop labels per side spread across30sessions per side. These are minimum
coverage conditions; overlapping examples do not become independent observations. Daily dependence, selection,
cost and held-path gates still apply. The source mechanism does not waive them.

Permanent information, return/volume misclassification, stale features, state instability and a learner rediscovering
ordinary price patterns can erase the forecast. Missing overnight minutes, unverified continuous-contract construction,
original native receipt/correction clocks, raw quote/queue fills and native micro execution remain unresolved. No offset
against VB/ONB or survival benefit is assumed. Any earned account comparison must inspect the timing of losses and
offsets before the actual floor breach.

## Eight evidence questions: explicit admission checks

| Question | Frozen expectation / required evidence |
|---|---|
|1. Who trades and why? | Persistent liquidity takers and responding liquidity suppliers are a possible channel. No forced mandate, net flow size or compulsory counterparty is observed. |
|2. Direction, size and clock? | Both side forecasts become available at the completed decision; choose only the frozen net-R hurdle. Position sizing is not inferred from a pressure score. Preserve the delayed-open, stop and exit clocks. |
|3. Does it reach the contract? | Inputs are directly NQ futures price and aggressive volume. Stock-paper evidence does not prove current NQ demand. MNQ cash results remain NQ-price proxies pending native quote/fill evidence. |
|4. What is new and available? | The incremental information is the causal120minute pre-event profile, not a new news/participant label. Owned hashes, exact minutes, prior-day fits and matching-estimator local controls establish the bounded test; receipt/roll caveats persist. |
|5. Costs, liquidity role and actual gaps? | Entry/stop orders take liquidity; target limits have queue/adverse-selection risk despite modeled trade-through. The09:00–14:00 window overlaps VB/ONB. There is no measured incumbent-flat slot and no incumbent-flat eligibility filter. |
|6. Is there enough power? | Actual opportunity counts remain unknown until the committed profile census. At the minimum250executed trades, an ASSUMED .55R trade SD implies net mean2×.55/sqrt(250)≈.070R for t2 under independence. Dependence reduces effective n; costs raise the required gross mean and multiplicity raises the eventual bar. This is not observed power or promotion evidence. |
|7. What has been tried and what falsifies this? | Preserve the prior15new-study definitions plus older pressure/book searches; these four make19. Failure of standalone/stress gates or no paired increment over the matching local estimator rejects the extension without a window/hurdle/feature rescue. |
|8. Failure, common losses and timely offsets? | Permanent information, trend/gap stress, depleted liquidity and data failure can cluster losses. VB/ONB share the underlying and part of the clock; joint losses are unmeasured. A later gain may arrive after a floor touch. One position/max4entries/day, a nominal .10ATR stop and timed exit bound the protocol, not gap fills. Only earned chronological BASE/ADD/REPLACE/EMPTY paths can establish an offset before breach. |

## Definitions, falsifiers and next gate

Four definitions are prospectively reserved: selectable HGB_MEMORY and RIDGE_MEMORY; unselectable HGB_LOCAL and
RIDGE_LOCAL. Each memory candidate must beat its matching local estimator, so a change of estimator cannot be
credited to the extra memory features. HGB_MEMORY has first priority if every frozen gate passes, then RIDGE_MEMORY.
No control promotion, effects scan, fitted window, direction inversion or hurdle adjustment follows from outcomes.

The primary falsifier is no incremental costed payoff over the matching local model, including the frozen paired
daily10day-block90%lower confidence bound. All standalone counts/significance/year/cost/ambiguity/path gates must
pass first. Only then are dependent placebos, stress checks and validation earned. Preserve all prior definitions:
these four increase the new study's cumulative count from15 to19, in addition to older pressure/book searches.

Decision: **TEST** only after source, cache identities, this sheet and the exact executable protocol are committed.
No native MultiCharts, VPS, broker, notification, schedule or trading-plan action is part of this study.
