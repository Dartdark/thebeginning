# MBS duration-state hedge adjustment: NEEDS DATA

Summary: A distinct hypothesis would trade changes in an identified mortgage portfolio's hedge requirement.
Saved literature explains prepayment-driven negative convexity, but not an observed compulsory ZN order.
Historical MBS duration/coupon/exposure states and their publication and hedge clocks are not established locally.
Audit those independent inputs first. Do not test a ZN-price-momentum proxy under a mortgage label.

Sources: papers/ssrn-3247865.pdf, *151 Trading Strategies*, section11.7, PDF pages101–102
(printed100–101); analysis/zn_release_momentum_test.py; analysis/zn_month_end_test.py;
agents/codex/evidence/treasury_dealer_award_next_session.md; data-file headers only.
New strategy-return trials for this hypothesis:0. No economic preregistration, thresholds or entry clock frozen.
Existing program trials and the rejected flow-innovation family remain unchanged by this sheet.

## 1. Participant, cause and unobserved obligation

The candidate actor is an identified holder of mortgage-backed passthroughs managing a stated duration target.
Prepayment options can make effective duration extend as refinancing becomes less attractive and contract
as borrowers refinance. For a holder maintaining a fixed net-duration target, a measured increase in MBS
DV01 could require additional short-duration hedges; a decrease could require buying back those hedges.
That is a conditional prediction, not proof that every MBS holder follows this policy or trades futures.
Other assets, existing derivatives, servicing exposures and cash flows can offset or reverse the net need.

The saved secondary source describes MBS passthrough positions and duration hedging with interest-rate
swaps. Hedge ratios require a prepayment model or estimated MBS-price sensitivity to the five-year swap
rate. It does not supply current holdings, an actual mandate, compulsory ZN demand or an intraday deadline.
The source's cited original research is not saved here; a bibliography reference is not a checked primary source.

## 2. Direction, scale and timing before entry

The new information would be an as-of change in effective DV01 of a defined, weighted MBS exposure,
adjusted for its known target and outstanding hedges. Mortgage coupons/refinancing incentive and a
contemporaneous rates or swap curve could support that state estimate if their vintages are auditable.
Direction must come from the resulting hedge adjustment, not the sign of an earlier ZN price move.

No hedge fraction, dollar flow, futures-contract quantity or participation rate is measured. A full hedge
or universal mortgage exposure must not be assumed. Publication policy, original receipt, revisions,
model-update time, hedge trigger, order allowance and actual execution clock are separate unresolved inputs.
Only1-,5-,15- or30-minute signal frames would be eligible for a later plan; none is selected here.

## 3. Transmission to a futures contract

ZN is a possible duration instrument, but the saved strategy discussion uses swaps. Treasury/swap basis,
curve exposure, deliverable-basket DV01 and existing hedges can make a single ZN trade an incomplete or
wrong-signed representation. A documented allocation into ZN or an explicit, source-supported hedge map
is required before estimating pressure. A five-year swap sensitivity does not automatically imply a
ten-year Treasury-futures order. No extra NQ/ES proxy or second strategy leg is proposed.

## 4. Independent input and feasibility

| Input | Available evidence | Missing before TEST |
|---|---|---|
| Mortgage convexity mechanism | Saved secondary MBS discussion in papers/ssrn-3247865.pdf, section11.7 | Original primary evidence and applicability to an identified hedger |
| Coupon/refinancing and prepayment state | No suitable local dataset established by this bounded audit | Historical as-of coupons, refinancing incentive and model inputs/vintages |
| Effective duration/DV01 and exposure | No measured MBS state or weighted holdings established | Published effective risk or a justified past-only model, exposure weights, target and existing hedges |
| Rates and hedge clock | ZN minute files exist; no suitable swap-curve or mortgage hedge-clock input found | Contemporaneous curve data, update/receipt timestamps and evidenced execution trigger |
| Native ZN observations | data/ZN_1min_2017.csv through2026 share date/time/OHLCV headers | Row coverage, individual-contract/roll mapping, native session calendar and executable path audit |

Filename years and headers establish schema only, not complete or point-in-time history. The auction
CSV contains auction terms/results, not mortgage state. Aggregate COT dealer/asset-manager positioning
does not identify mortgage exposure, duration or an intraday hedge requirement. No current revised time
series or fitted ZN-price transformation may silently substitute for an unavailable independent MBS state.

## 5. Costs and actual intraday gaps

Existing ZN research specifies1000USD per price point, tick1/64=15.625USD,7.25USD round-trip commission
and one adverse tick per market/stop fill. Two market fills imply38.50USD under those existing assumptions.
See analysis/zn_release_momentum_test.py and analysis/treasury_auction_test.py. These are repository
conventions, not newly verified broker quotes or a supported expected gross move for this hypothesis.

Native contract parameters, spread/latency stress and target-through measured in ZN ticks require a
separate adapter audit. Do not copy NQ's point value or one-point target-through. No native micro history,
cost or fill-parity evidence for this exposure was established; dividing ZN returns cannot create it.
No candidate-conditioned empty plan window is known. Do not select an entry clock from a flat-roster map.

## 6. Power before any return test

The2018–22 opportunity count, event frequency, warm-up loss and effective sample size are unknown until
the historical state/clock census exists. Daily bars or available ZN dates are not observed hedge events.
For assumed trade standard deviation s and effective count n, net means2*s/sqrt(n) and6*s/sqrt(n) would
be needed for t2 and t6 before adding costs to form gross hurdles. No measured s, n or intraday premium
is available here. Dependence, common hedge days and the cumulative search would raise the burden.
There is no basis for relaxing a count gate or assuming a short-window return to justify a backtest now.

## 7. Prior definitions, novelty and falsifiers

analysis/zn_release_momentum_test.py already follows a large07:30–07:35CT ZN macro-release move at07:36,
with later time exits, and explicitly invokes duration dealers, pensions and mortgage hedgers. It labels
that explanation as the prior author's inference rather than the cited books' rule. Repeating this entry
with a mortgage name, reversed direction, shifted window or another threshold is not a new mechanism.

analysis/zn_month_end_test.py separately defines month-end Treasury index-duration extension. The prior
NQ Correlation Risk Budget family models stock/bond covariance-driven allocation; this sheet is not a ZN
ticker port of it. A genuine increment would be independently observed mortgage-specific risk/exposure
changes and their known hedge adjustment, not price momentum or a calendar standing in for those inputs.

Data falsifiers include state unavailable before entry, later-vintage substitution, unidentifiable net
exposure, absent ZN transmission or no evidenced execution trigger. Economic falsifiers belong in a later
committed plan. The failed flow-innovation family stays closed; no inversion or control nomination follows.

## 8. Failure, liquidity and account timing

| Question | Pre-test limit and evidence needed |
|---|---|
| Why it fails | Prepayment-model error, offsetting portfolios, anticipation, hedging through swaps/cash or flexible targets can eliminate the proposed futures flow |
| Our liquidity role | Order type is not chosen; market entries/stops would consume liquidity, while passive fills need queue/adverse-selection evidence |
| Loss clustering | Rate shocks, refinancing-regime shifts, curve/basis changes, rolls and illiquid gaps can produce clustered losses; stops cannot guarantee a quoted loss |
| Common plan losses | Treasury/rates exposure can coincide with equity-duration and macro-sensitive NQ/ES positions; no measured diversification or offset is established |
| Before-breach offset | None demonstrated; actual entry/hedge timing and whole-contract joint account chronology are required, not annual correlation |

A later plan must freeze native protective stops active on the entry bar, worse gap fills, target-through,
data-failure handling, maximum holding time and a same-session exit before15:59CT or the earlier native
session close. No stop distance or clock is invented here. Proposed scope is one standalone position;
whole-contract size and executable risk still need evidence. Missing inputs prevent entries, not future
backfills. BASE/ADD/replacement/EMPTY comparisons require valid joint account paths; no pass/payout or
hedge improvement can be inferred from scaled proxies.

## Decision and next gate

**NEEDS DATA** for the state-conditioned mortgage-duration hypothesis. Obtain and audit historical as-of
MBS risk/exposure/coupon/curve inputs, original primary evidence, update clocks and ZN transmission before
deciding TEST. **DON'T TEST** a price-only mortgage relabel. No purchases, accounts or user action are
requested by this sheet; the separate EIA host-access issue remains pending under its existing record.

Only after those gates pass may a separate <=5-configuration economic preregistration be committed before
2018–22 returns. Any selected2023+ test would be previously seen historical validation, never a fresh
holdout. Promotion would still need dependence/selection/placebo checks, a fresh raw-spec checker and
valid account comparisons. No PowerLanguage, deployment, trading approval, new milestone or pause of the
continuing research program follows this evidence screen.
