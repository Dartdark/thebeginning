# Rad commodity double-sort: WATCH — personal research only; no test admitted

Summary: Monthly commodity momentum plus carry selects four futures longs and four shorts.
The thesis claims 20.22% annual excess return/24.91% volatility for February 1979–October 2011, excluding costs.
Its $7.63 wealth claim matches an additive return sum; compounded, self-financing NAV is not established.
Whole-book stopping lowers reported VaR 20.27%→13.76%; this is an unverified risk-method result, not our backtest.
Park the exact strategy pending paired data/accounting; all four Apex homes fail its monthly holding rule.

Source: **Hossein Rad**, *Double-sort trading strategy on commodity futures: performance evaluation and stop-loss
implementation*, **December 2012**, EDHEC MSc Financial Markets master thesis, supervisor Joëlle Miffre, SSRN 2614241.
Read all 56 PDF pages, including methodology, results, conclusion and references. PDF page references below include
the five front-matter pages; printed page numbers are generally five lower. This is a thesis, not established
peer-reviewed or independently verified evidence. SSRN posting/revision dates were not verified.

[Owned PDF](../inputs/rad_double_sort_20261031/ssrn-2614241.pdf) ·
[extracted text](../inputs/rad_double_sort_20261031/full_text.txt) ·
[source/access/acquisition receipt](../inputs/rad_double_sort_20261031/source_access.json) ·
[transcribed claims](../inputs/rad_double_sort_20261031/claims.json).
[Evidence sheet](../evidence/rad_double_sort_20261031.md).

Plan: **none admitted**. Return definitions/trials, account simulations and new budget reservations: **0**.
[Reproducible arithmetic/header audit](../../../analysis/codex_rad_double_sort_review_20261031.py) ·
[arithmetic](../../../analysis/outputs/codex_rad_double_sort_20261031/arithmetic.json) ·
[owned headers](../../../analysis/outputs/codex_rad_double_sort_20261031/owned_headers.json) ·
[source/code/hash manifest](../../../analysis/outputs/codex_rad_double_sort_20261031/manifest.json).
Scout progress/lease/budget and all prior selection history are unchanged. This upload review did not start a new
autonomous scout cycle, resume a paused search, or inspect historical strategy returns.

## Four questions

1. **What is it about?** Combining monthly commodity price momentum with the front/second-contract price curve,
   then asking whether daily-monitored stop overlays improve that eight-position long/short book.
2. **What does it find?** The author reports 20.22% annualized excess return,24.91% volatility and 0.81 reward/risk,
   with stronger results in February 2007–October 2011 than before. Most individual stops have little benefit or
   worsen risk. The whole-book 5% cutoff reduces reported 30-day 99% VaR from 20.27% to 13.76%, with return slipping
   to 19.93%. These are source claims; our checks establish arithmetic/reporting concerns, not historical alpha.
3. **Why could it make money?** Price persistence plus compensation for hedging, inventory and convenience-yield
   risks may favor rising/backwardated commodities over falling/contangoed ones. This is a proposed risk-premium
   mechanism, not verified mandatory orders or proof that backwardation guarantees a gain. Long/short formation
   alone does not guarantee crisis protection or current-portfolio diversification.
4. **Can we build on it?** Conditionally, as a personal-account monthly momentum/carry research candidate. The
   full broad paired-contract panel, executable clocks, native costs, integer sizing and cash/NAV accounting are
   missing. A bounded owned/free check did not obtain them. No valid test can be produced from our two commodity
   outrights by inventing deferred prices or shrinking the source universe. Retain the risk-method lesson now;
   park deeper return work until genuinely new matching inputs arrive. No Apex placement or allocation earned.

## Source rule and economic meaning

Datastream daily data cover 37 named commodity futures over January 1979–October 2011, with listing/delisting changes:
22 instruments initially, rising to a peak 35 from July 1997. Thus 37 is the total universe, not 37 simultaneous assets.
It spans metals, energy, livestock, agricultural products, milk/lumber and two non-overlapping fertilizer contracts
(PDF 20). Our owned CL/GC outrights are not that cross-section.

At month-end, rank prior-month average daily `ln(P_t/P_previous)` returns. Keep the eight winners and eight losers.
Within winners buy the four with highest prior-month mean `ln(front_close/second_close)`; within losers short the
four with lowest mean. This carry measure is not maturity-gap annualized. Hold for one month, initially equal
weight within each side, then allow weights to drift. Trade nearest futures and roll at the end of the month
before maturity (PDF 21–25). The ranking/holding period follows the earlier Fuertes–Miffre–Rallis 2010 selected setting.

One collateral unit supports one unit long plus one unit short: **2x gross exposure**, not a half-sized unlevered
allocation. A selected missing daily return is handled by equal redistribution among available positions in the
paper; that is not an executable or admitted substitute for our missing data. The same collateral and short-side
weight drift need an explicit futures cash/quantity ledger. No raw panel, source code or trade ledger is supplied.

## Reported performance — author claims, before costs

| Configuration | Annual excess return | Annual volatility | Reward/risk | Sortino | 30-day 99% VaR |
|---|---:|---:|---:|---:|---:|
|No added stop|20.22%|24.91%|0.81|1.18|20.27%|
|Individual cumulative 13%|20.97%|25.07%|0.84|1.22|20.88%|
|Individual cumulative 5%|15.65%|27.56%|0.57|0.81|22.47%|
|Individual exponential 0.6 /5%|18.60%|24.92%|0.75|1.08|21.42%|
|Individual consecutive losses, threshold 5days|20.99%|25.72%|0.82|1.19|18.88%|
|Whole portfolio 5%|19.93%|22.47%|0.89|1.31|13.76%|

Sources: Table 1/PDF 26; Tables 3/5/6/7 and accompanying text, PDF 39–48. Baseline reported t=4.58 and 8543 daily
observations. Long contribution is 12.28 percentage points annually; short contribution is+7.94, obtained by
subtracting the selected short basket's−7.94 underlying return. These are not executable integer-leg net returns.
The author reports 17.12% annually before February 2007 and 34.50% from February 2007 through October 2011. Those
retrospective periods do not constitute our 2018–22 design or 2023+ historical validation, nor a frozen forward test.

Do not flatten the stop result into “none reduced risk.” Whole-book VaR falls **6.51 percentage points /32.12%
relative**, volatility falls 2.44 points /9.80%, while annual excess return falls 0.29 points. Its paired return-test
p=0.079 fails a 5% mean-difference criterion; that test does **not** establish insignificance of the VaR reduction,
nor validate the chosen overlay. The 13% individual and consecutive methods report p=0.0362, but thresholds were
selected after exploration, not multiplicity-adjusted frozen replications. The thesis omits trading costs and
acknowledges extra transactions can erase small improvements. No turnover-based breakeven-cost estimate exists.

## What independently checks, and what does not

**Return/wealth reconciliation problem.** Eq 1 defines instrument log returns; Eq 3 subtracts long and short basket
returns; Eq 4 adds daily returns (PDF 20–22). Table 1 reports a 663.66% sum, and Figure 3/prose call the endpoint of a
$1 investment $7.63 (PDF 26–28). Independently, `1+6.6366=7.6366`, matching that additive chart. If 6.6366 were a valid
cumulative portfolio log return, wealth would instead involve `exp(6.6366)≈762.50`. Weighted instrument log returns
are not generally exact self-financing portfolio log returns, and a negated underlying log return is not the log
return of the collateralized short book. The audit includes simple constructed identities demonstrating both.

An additive fixed-notional excess-P&L index can be legitimate if labelled and reconciled accordingly. It cannot
be read as compounded NAV/CAGR. If the plotted $7.63 were actual ending wealth, its implied CAGR over the stated
dates would be approximately 6.40%; **neither that figure nor 762.50 is a corrected strategy result**. We lack the
raw returns/quantity/cash ledger to reconstruct actual net wealth. The 20.22% label is annualized excess return,
not demonstrated after-cost CAGR or an income forecast.

Additional source checks: the PDF 21 worked example says `ln(40.95/36.65)=13.8%`; it is approximately**11.09%**.
PDF 48 calls whole-book return higher despite Table 7's 19.93% being below 20.22%. The conclusion says October 2010,
whereas data/method/results use October 2011. These are reproducible source inconsistencies, not evidence that the
underlying risk premia cannot exist. No author historical result was independently reproduced.

## Why its stops do not establish protection for our plans

The paper's daily-close calculations affect the following day, rather than representing broker-held intraday
stop orders. Individual stops usually redistribute the removed weight over surviving positions, which can increase
concentration instead of reducing gross exposure. Reopening variants add turnover and under-specified state logic.
The consecutive-loss method says “more than” the threshold in its methodology, while later language describes
reaching it. The whole-book section describes a cumulative trigger without a precise cumulative formula. No
submission/fill/gap/currency policy resolves these ambiguities. Neither a 5% trigger nor a reported VaR is a hard
loss limit. Future log-based rules also need a valid ex ante treatment of non-positive prices.

It would be unjustified to remove or widen any current protective order, add a portfolio cutoff, or claim the
paper disproves stops. Such changes define separate hypotheses requiring evidence and committed bounded trials.
Retained as [EXECUTION_REFERENCES E38](../EXECUTION_REFERENCES.md#e 38--commodity-stop-overlays-exposure-redistribution-and-returnnav-accounting).

## Feasibility, deduplication and account status

The audit inspected 141 owned CSV headers; CL and GC each have ten yearly files labelled 2017–2026 with only
date/time/OHLCV. No maturity IDs, expiry or simultaneous second-contract fields were found. Other named workspace
data roots and relevant contract/basis filenames added no usable paired universe. Filename ranges establish no
full-history coverage. The bounded free check inspected provider schemas/access and attempted a no-account CSV
sample; its tunnel returned 403. Provider offerings inspected were front-month-only, short/old samples, an
unavailable download archive, or account/paid long history. Respect the boundary and move on; no recurring search
for unchanged missing inputs. This is scoped feasibility evidence, not proof that suitable free data cannot exist.

TIER_LIST already has the broad Gorton commodity storage/momentum reference. Exact Rad rules were not previously
reviewed here. Weekly basis reversal is a separate parked definition with the same paired-data need; this paper
does not unblock it. Prior CL/GC hedging-pressure trial rejection remains intact. No replacement with COT, indices,
an outright carry proxy, a reduced universe, or intraday liquidation was tested under this paper's identity.

| Home | Status | Portfolio comparison |
|---|---|---|
|50K evaluation|Monthly overnight rule ineligible as written|Not run|
|150K evaluation|Monthly overnight rule ineligible as written|Not run|
|50K funded|Monthly overnight rule ineligible as written|Not run; no payout/blow-up claim|
|150K funded|Monthly overnight rule ineligible as written|Not run; no payout/blow-up claim|
|Current 19-piece personal book, one mini per leg|Potential research fit, data/accounting gate unresolved|BASE/ADD/REPLACE/EMPTY not run; no contribution claim|

No whole/long/short yearly return reconstruction, cheap gross-cost screen, placebos/random-drop controls, historical
validation, independent raw-spec review, Monte Carlo or native-account replay ran. Missing results remain missing.
No MultiCharts code was written or compiled. Artifact-admission and independent economic verification are unclaimed.

## Decision and exact continuation condition

Add one **parked, low-priority personal research** item to TODO's verification queue: specific monthly commodity
momentum/carry double-sort, merging its broad family context and shared data prerequisite. Merit is its explicit
two-signal selection rule and hypothesized risk-premium diversification, supported only by old pre-cost source
claims. Missing data alone is not the merit. Stop overlay lessons belong in the execution library.

Deeper testing is warranted **conditionally**, after actual matching inputs and a cash/NAV specification arrive,
not an immediate proxy backtest. Smallest next check: reconcile one identified formation/roll month using both
maturities, executable clocks and self-financing integer cashflows, then do a no-return 2018–22 coverage/power census.
Only a passed evidence gate can advance to the existing committed budget/preregistration and design-first process.
No user action is requested; owned-data-compatible scout discovery should pass over this unchanged parked lead.

For the user to send Claude: `agents/codex/results/rad_double_sort_review_20261031.md`.

Subsequent user-requested [code build](rad_double_sort_build_20261031.md): monthly selector and draft integer
reference allocation implemented with23 synthetic mechanics checks. This does not change the source/economic
verdict, supply missing paired data or constitute historical returns/account verification.
