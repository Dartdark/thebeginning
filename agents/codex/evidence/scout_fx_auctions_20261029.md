# FX after Treasury auctions before macro announcements: NEEDS DATA

Summary: A scheduled auction × next-day macro-announcement FX interaction has concrete research merit.
The roughly 8bp return and dealer-capacity explanation are authors' abstract claims, not verified net returns.
Full source access timed out; exact instrument, event definitions and executable holding clock remain unresolved.
Owned 6E/auction data and accessible Fed/BEA calendars establish partial feasibility, not reproduction readiness.
NEEDS DATA: obtain/pin the full source and resolve the clock/calendar/contract gates before preregistration or returns.

Sources: [SSRN 5207418, revised March 20, 2026](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5207418);
[HKUST April 2025 version, indexed abstract/first page only](https://fina.hkust.edu.hk/sites/finance/files/paper/Auctions_Announcements_and_Abnormal_Returns.pdf).
[Review and access receipts](../results/scout_fx_auctions_20261029.md), inspected 2026-10-29.
Return trials: **0 new**; no source preregistration, hypothesis reservation or account run was created by this task.
This sheet precedes any strategy preregistration. Only TEST advances; this sheet does not.

## 1. Who trades, and what forces or causes the trade?

Authors propose that Treasury issuance and reduced Treasury demand constrain primary dealers' intermediation capacity and affect FX around following announcements. The obtainable abstract names dealer activity and risk-bearing capacity; it does not establish a binding obligation, exact hedge flow, size or a causal estimate available to us. Treat the channel as a source hypothesis. Scheduled supply and news timing provide a more specific premise than an unconditioned chart pattern, but do not establish that the effect survives current competition and costs.

## 2. Direction, size and timing known before entry

The March 2026 abstract predicts foreign-currency appreciation/USD weakness on major U.S. macro announcement days following an auction. The April 2025 indexed abstract describes pre-announcement drift. No full-text holding window, day-boundary convention or currency weighting was obtained; no exact entry/exit or order type is proposed here.

Known ex ante in principle: announced auction schedule and separately scheduled macro release. Still to verify: publication/receipt time of each schedule, revisions and rescheduling, previous calendar day versus business day, multiple auctions/releases and maturity selection. Auction outcomes are usable only after publication plus a justified receipt delay; macro surprises are unavailable before release. No price-spike classification may select a pre-announcement trade.

Use `America/New_York` and `America/Chicago` timezone rules, not a fixed UTC offset. Do not assume the day starts at midnight, New York close, settlement or CME session open. Position size and participant dollar flow are unknown, so no flow-to-volume ratio is established.

## 3. Does the flow reach the traded contract or its direct hedge?

The claimed effect is in FX. Euro appreciation has the directional sign of a long 6E/M6E position, but a euro-only future is not an unspecified currency basket or spot/forward index. Futures basis, roll and native micro liquidity must be checked; the source's direct instrument remains unverified. There is no demonstrated whole-index ES/NQ transmission.

## 4. New information and data feasibility

| Input | Source / fields inspected | Coverage actually established | Point-in-time timing / revisions | Ownership/access status |
|---|---|---|---|---|
| Full source specification | HKUST PDF; current SSRN metadata | Indexed April 2025 abstract/first page; March 2026 SSRN abstract only | Different versions; specifications may differ | Full PDF timed out twice; not obtained or hashed |
| Euro futures minutes | Owned `data/6E_1min_2017.csv` … `2026.csv`; header `date,time,open,high,low,close,volume` | Annual filenames exist; sample header/rows inspected, not complete-session coverage | Timestamp/session, roll and contract identity unresolved; no contract ID in schema | Owned, partial feasibility |
| Auctions | Owned `data/treasury_auctions.csv`; date, term/type, competitive close, reopening, offering, bid/cover, high yield, CUSIP, TIPS/FRN | Sample includes December 2017 rows and 13:00/11:30 ET close times; prior script describes through October 2026, not re-audited here | Schedule known before auction; outcomes only after auction; original schedule vintages not verified | Owned; live official FiscalData page attempt returned 403 |
| Macro release calendar | `data/` inventory; `analysis/event_days.py`; official Fed and BEA pages | No complete owned ex-ante macro calendar found; Fed calendar and BEA current release schedule readable | Historical original release time/rescheduling requires reconstruction; general price-spike proxy is unavailable before release | Free primary sources partly accessible; BLS attempted page inaccessible |
| Source-specific high-frequency/interdealer data and consensus | Only identified generically in current abstract | Exact products, currencies, dates and access terms unknown | Receipt/revision clocks unresolved | Availability not established; no paid acquisition authorized |

The incremental input is **auction schedule × announcement schedule**. Calendar-only announcement and auction effects must later be separate controls using the same universe and window. The owned general-release price-spike proxy is not an acceptable replacement for pre-entry knowledge. No returns were calculated from any input.

## 5. Costs and actual intraday gaps

No source cost assumptions or exact duration were obtained, so the reported 8bp must not be compared directly with a 6E/M6E cost estimate as though it were an executable euro result. The prior same-day 6E script assumes $19.75 RT per full contract; it is a retained old model, not measured micro costs or this source's assumptions. Native commission, spread, slippage, latency, rolls, integer sizing and announcement fill stress remain required.

Apex flat by **15:59 CT** is a hard compatibility gate. If entry is before the previous day's flat boundary and exit at a following-day release, the proposed interval is incompatible with that account. If the verified source interval is entirely same-day and finishes by 15:59 CT, it might qualify, but that is not yet established. A personal overnight candidate has different margin/gap requirements. No exact overlap window or saved occupancy map was assessed because the candidate clock is unknown; low correlation cannot be inferred from a different ticker.

## 6. Power before a return test

No source-compatible event count, 2018–22 effective sample, volatility estimate or warm-up loss was established. The mean needed for a rough t=2 screen would be approximately `2 × SD / sqrt(effective n)` net, plus execution costs for the gross hurdle, with dependence/multiple trials accounted for. Do not insert an invented event frequency or transfer a pooled FX 8bp to one euro contract. Source window and calendar audit must precede a meaningful power calculation.

## 7. Already tested and falsifiers

No exact SSRN/title match was found in the prior TIER/TODO/result search. Relevant reviewed predecessors:

* `TIER_LIST.md` Treasury auction price-pressure row and `analysis/treasury_auction_test.py`: same-day nominal-coupon pre-short/post-long. Costs defeated ZN; retained 6E pre-short evidence is weak. This differs from the next-day announcement interaction and cannot verify or reject it.
* `analysis/anti_forced_flow_ideas_test.py`: NQ continuation after same-day 10-/30-year auctions failed its design period. Do not revive that rule under a new paper label.
* `agents/codex/results/six_e_cross_asset_review_20261027.md` and TODO: personal multi-day 6E package, source implementation unverified. Related market exposure, different hypothesis.

Before any returns, freeze falsifiers: the exact source interval cannot be traded within account constraints; the ex-ante event set cannot be reconstructed; or full source shows the effect is neither a net executable return nor a euro result and an explicitly bounded proxy lacks a justified mechanism. Later economic falsifiers would include no interaction beyond same-window calendar baselines or a gross edge below native costs. Failure does not authorize choosing a different currency, clock or auction subset after outcomes.

## 8. Failure and diversification — required supplement

| Question | Prediction before results | Needed evidence / falsifier |
|---|---|---|
| What stops the mechanism? | Dealer capacity absorbs issuance, auction demand changes, or the scheduled premium is competed away | Source definitions first; subsequent fixed-calendar design comparison |
| What liquidity role do our orders play? | Unknown until exact rule/order clock is known; pre-news entry may pay spread and exit into stressed liquidity | Same-contract quotes and executable fill assumptions, including missed fills; no passive-fill claim |
| How could losses cluster? | USD rallies, correlated releases, issuance stress, overnight gaps, announcement jumps and data outages | Frozen gap/fill stresses, maximum size and contract/session provenance |
| Which existing strategy shares losses? | Personal 6E package likely shares dollar/euro exposure; equity macro-event strategies may share surprise risk | Later joint chronological P&L, overlap and replacement comparison; no measured correlation here |
| Could an offset arrive before breach? | Unknown; a following-day payoff cannot be assumed to offset an earlier intraday breach | Later account replay at actual integer sizes and netting rules |

No executable stop/time exit, data-failure rule or maximum exposure has been established. Those are prerequisites for TEST, not details to optimize after returns. Any account stage must compare base, addition, replacement and empty-slot control at native sizes/costs; overnight personal feasibility does not waive Apex restrictions.

## Decision and next gate

**NEEDS DATA.** Concrete merit warrants a deeper source/data check, but not a return test. Obtain a lawful full pinned version and verify its native instrument, currency universe, complete event selection, entry/exit clocks and cost treatment. Complete historical calendar and contract/roll provenance checks before reserving a hypothesis or registering exact code. Keep any future 6E proxy explicitly distinct from exact replication. No trial limit, source-admission requirement, 2018–22 gate, historical-validation label or independent/account review requirement is waived.
