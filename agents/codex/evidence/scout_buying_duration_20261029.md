# Clock-aware Treasury index extension: NEEDS DATA

Summary: The US index-pricing deadline changed in January 2021; the old ZN test kept its earlier exit.
This is a documented coverage limitation and a reason to inspect the new paper, not verified net alpha.
Full text, source windows, exact event calendars and historical pre-entry duration forecasts remain unresolved.
Complete those no-return checks before selecting rules; no return trial or economic preregistration has begun.

Source triage: [Buying Duration review](../results/scout_buying_duration_20261029.md), 2026-10-29; SSRN7601879 metadata/abstract only, full-text delivery403.
Independent primary source: [Bloomberg Fixed Income Index Methodology, October15 2024](https://data.bloomberglp.com/professional/sites/27/Fixed-Income-Index-Methodology.pdf), printed pp.45–46 and80.
Related primary observations: [NYFed, Treasury Trading at the Close, September22 2026](https://libertystreeteconomics.newyorkfed.org/2026/09/treasury-trading-at-the-close/).
Repository context: `codex/work` at `49b48b8064a57a13fd114ee9d527c69cc7c58f0a`.
New return trials: **0**. Earlier ZN month-end family includes A/B/C, refunding splits and calendar controls; none is erased or newly counted here.
This sheet is **not TEST**, does not freeze a strategy and does not authorize economic testing or trading.

## 1. Who trades, and what causes the trade?

The proposed participant is an investor managing duration against a month-end bond benchmark. A change in benchmark risk can require portfolio adjustment; tracking-error objectives can concentrate its timing. Neither every index extension nor every benchmarked fund implies an identical forced futures order. Existing holdings, cash, new subscriptions, other hedges and permitted tracking error matter.

Bloomberg documents how index membership and accumulated cash enter extension calculations and distinguishes final figures from earlier forecasts. That establishes index mechanics. It does not measure net ZN demand, an investor's required adjustment or an unexploited return. The new paper's causal and return evidence has not been read beyond its abstract.

## 2. Direction, scale and timing known before entry

Use a source-supported pre-entry extension forecast and its publication/receipt timestamp if the proposed rule is state-conditioned. A later realized extension is an explanatory variable unless its information was demonstrably available at the decision. No forecast vintage, dollar flow, hedge fraction or futures allocation was acquired in this screen.

The independently established US ordinary-day deadline moves from14:00CT to15:00CT effective2021-01-14. Early closes need their own dated schedule. A future plan must map event_time, forecast available_at, decision_time, first executable order/fill and exit separately using named timezones. The snapshot itself is not a trade price or a guaranteed fill. No source entry offset or holding window has been recovered, so none is invented.

## 3. Transmission to the contract

ZN is a possible Treasury-duration hedge and already exists in our research history. An aggregate government-bond-futures result does not identify an incremental ZN order or an ES/NQ effect. Before TEST, inspect the paper's exact instruments, duration scaling, deliverable-basket exposure, roll rule, curve weights, cash/futures substitution and contemporaneous basis. No micro return series or contract-equivalent division can substitute for native micro cost/fill evidence.

## 4. New information and data feasibility

| Required input | What was actually established | Missing gate |
|---|---|---|
| Primary manuscript/version | SSRN record, author abstract and advertised60pages; direct PDF403; institutional/author searches found no accessible copy | Lawful full text, version/hash, source methods/tables and code/data availability |
| US pricing-time eras | Provider p.80 inspected; ordinary-day change and dated early-close exception documented | Event-by-event historical holiday/early-close map and exact index applicability |
| Duration-extension signal | Provider pp.45–46 describe forecasts and final extension; forecast reports are advertised via INP | Historical as-published forecasts, revisions, receipt times, accessible rights/cost and specific fields |
| Native price/contract history | Existing ZN test script and saved output inspected | Minute coverage, roll map, contract identity, bar stamp/session rules, unresolved paths and hashes |
| Execution cost inputs | Old script's explicit point/tick values and deductions inspected | Current research convention reconciliation and native contract/micro executable fill assumptions |
| Candidate event census | None performed | No-return2018–22 count, holiday exclusions, eligible clock coverage, feature missingness and warm-up loss |

No licensed feed, account, credential or paid subscription was acquired. The blocked PDF and alternative-search attempts are recorded in the review. No historical forecast dataset was claimed obtainable merely because Bloomberg advertises a Terminal report. Do not silently substitute refunding months, contemporaneous ZN momentum or a revised monthly series for the proposed independent input.

Owned/free follow-up: ZN2018–22 files were inventoried locally (header/date fields,19.6–21.5MB each), without prices-to-returns
calculations. A public mirror supplied a four-page March2020 Bloomberg forecast report with index-duration fields as of
2020-03-27; inspected via connected reader, no local copy/hash. This is evidence that dated examples exist, not an acquired
complete as-of forecast panel. See the review and [access receipt](../research/scout/runs/20261029_initial_access.json).

## 5. Costs and actual intraday gaps

The old ZN code deducts two one-tick fills and two7.25USD commission charges; its saved net outcomes must remain tied to that convention. Another existing evidence sheet uses7.25USD round trip for ZN. Reconcile this discrepancy before a new gross-to-net bridge; changing fees must be an explicit matched comparison, not a rescue of the old result. No current broker quote is verified here.

The new source's duration-scaled basis points cannot yet be converted to native dollars or compared with a quoted contract cost. Parent order type, latency, spreads, target-through and gaps need explicit assumptions. No candidate-conditioned plan occupancy census was done. A15:00CT snapshot can intersect afternoon plan positions; do not select eligible events according to empty slots. Whole-contract risk and actual account paths determine any later fit.

## 6. Power before a return test

A month-end design has at most60calendar opportunities in2018–22 before exclusions, with fewer in each clock regime or forecast subset. This is a calendar ceiling, not a measured eligible sample. Future inference must preserve month-level dependence; adjacent minutes are not independent events. No observed candidate standard deviation, gross expectancy or break-even cost was estimated.

For trade standard deviation s and effective count n, a net mean near2*s/sqrt(n) is required for an approximate t2 before the stronger cumulative-search promotion bar. Costs raise the gross hurdle. Calculate with justified inputs after the census; stop if plausible source magnitude cannot support it. The small post-change design history is a material limitation, not grounds to relax gates or treat already-seen2023+ as fresh.

## 7. Already tested and falsifiers

[Existing script](../../../analysis/zn_month_end_test.py) tests last-day and preceding-day morning-to13:59CT longs, plus last-day12:00–13:59CT. [Archived output](../../../analysis/outputs/zn_month_end_test_output.txt) and TIER_LIST preserve negative net results. It was not replayed for this review. Its endpoint omits the changed ordinary-day deadline in later years, so the result is neither a full replication nor irrelevant evidence.

The specific prospective increment is a provider-documented pricing regime and, if supported by the manuscript and as-of data, independently forecast duration demand. It is not simply moving an exit after observing losses, adding a volatility threshold, reversing direction or reopening all Treasury seasonalities. A calendar-only baseline must use the identical event universe/window/costs; no source-defined forecast condition may be fitted on later returns.

Data falsifiers: the paper does not support the proposed executable window; forecasts are unavailable before entry; historical clocks/calendars cannot be pinned; contract transmission is absent; or unresolved data dominates the sample. Economic falsifiers and a cheap-screen stop rule belong in a later committed plan. Failure authorizes no offset/threshold/ticker search.

## 8. Failure and diversification

| Question | Present judgment and evidence needed |
|---|---|
| What stops it working? | Anticipation, offsetting flows, mandate changes or arbitrage can remove pressure. Need source evidence and later calendar/state controls. |
| Our liquidity role? | Unchosen. Market orders consume liquidity; passive orders require queue/adverse-selection and missed-fill evidence. A benchmark deadline alone does not establish our fills. |
| Loss clustering? | Rates announcements, duration repricing, curve/basis shocks, rolls and thin/early-close sessions can cluster losses. Need native marked paths and worse gap fills. |
| Shared losses with current strategies? | Macro/rates exposures can overlap equity-duration positions. Joint conditional losses and exposure timing are unmeasured; no portfolio hedge benefit is claimed. |
| Offset before account breach? | None demonstrated. A later reversal is not protection against an earlier loss. Need actual chronological account replay and integer quantities. |

No stop distance, order type, maximum position or holding protocol is selected. Those must be frozen before returns, including entry-bar protection, data-failure skip rules and a same-session exit by15:59CT or an earlier native close. A paper's after-snapshot reversal cannot waive flat-time limits. At the account stage, valid base/addition/replacement/empty-slot paths and all five homes remain required; no account allocation is supported by this source screen.

## Decision and next gate

**NEEDS DATA.** Obtain full text and complete a no-return source/calendar/forecast audit first. If that establishes a distinct executable hypothesis, mark a separately reviewed sheet TEST and commit a bounded preregistration before any returns. Existing five-configuration limits,2018–22 cheap screen, historical-validation labeling, independent review and account gates remain binding. Keep the old negative family result visible. This record is a worthwhile paper lead, not a tested strategy, new budget or live-system instruction.
