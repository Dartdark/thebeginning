# Hunt v2: Treasury dealer-allotment input — NEEDS DATA / causal evidence

Decision: **no new TEST is justified**. Actual dealer accepted share is distinct from the owned bid-to-cover
input, but it has already received an evidence-only review. The existing next-morning specification remains
**DON'T TEST**. Moving its story to the release afternoon does not establish a mandatory futures hedge or an
evidence-based entry/exit clock. Do not preregister a price/calendar substitute or manufacture a flow size.

This source-only follow-up adds **0 hypotheses, 0 gross screens, 0 counted economic evaluations**. Root owns
the live counters. H01 stays closed; H02's separate gross-data veto is not reconsidered here. No raw prices,
financial ledgers, CSV data rows, return calculations, source executable imports, network requests or completed
source/data audits were run. Only the owned auction CSV's header was inspected. No shared plan/ranking or git
state was changed.

## Scope and prior definitions

Read AGENTS.md, BUILDER_BRIEF.md, LESSONS.md, RESEARCH_CONTROLS.md, TASK_strategy_hunt_v2.md and progress.
The latest fetched ranking/source reference is `92b1d4cde768bcfce019cf9a95944158dd0ebba3` on the Claude
branch, read only. TIER_LIST/MINED_INDEX and the saved flow-novelty/next-priority maps were searched first.

| Source | What it establishes | Consequence |
|---|---|---|
| `analysis/treasury_auction_test.py`; TIER_LIST Treasury row | Pre-auction short, same-afternoon long, maturity/calendar/volume variants already exist. Related prior optimisation includes offering size, as recorded in the dealer-award evidence sheet. | A larger-offering calendar cut is not an untested independent input. Do not repeat those returns. |
| `agents/codex/evidence/treasury_dealer_award_next_session.md` | Actual `primary_dealer_accepted / total_competitive_accepted` was previously identified as new information, with two historical public-PDF spot checks. Its proposed next-morning ZN trade was **DON'T TEST**, not a failed return experiment. | Preserve this selection/mechanism history. Do not relabel the input as newly discovered or run the rejected clock. |
| `analysis/codex_free_data_evidence_inventory.py`; scope plan `free_data_evidence.md` (`41ffc93`) | Existing source explicitly records `dealer_award_fields_owned=False`; its two PDF award numbers are hard-coded reference spot checks, not a bulk historical result feed. | Do not rerun this completed inventory or treat its worked examples as complete 2018–26 coverage. |
| `agents/codex/evidence/auction_demand_confirmation.md`; `analysis/codex_auction_demand_confirmation.py` | The earlier standalone NQ rule uses published bid-to-cover deviation, prior comparable-auction references and ZN price confirmation; it explicitly does **not** use dealer awards, WI tails or dealer inventory. | Dealer allotment is a different source variable within the already researched auction family; the earlier BTC results cannot validate it. |

## Owned schema and price-path feasibility

The exact `data/treasury_auctions.csv` header inspected was:

```
auction_date,security_type,security_term,closing_time_comp,reopening,offering_amt,
bid_to_cover_ratio,high_yield,cusip,inflation_index_security,floating_rate
```

It contains **no** primary-dealer accepted/tendered quantities, total competitive accepted/tendered quantities,
direct/indirect bidder allocations, original result-publication/receipt time, correction time or vintage ID.
`offering_amt` cannot supply the dealer residual; bid-to-cover cannot identify who received the securities.
The competitive closing deadline is not the result's actual publication or receipt timestamp. `high_yield`
is not a same-CUSIP predeadline when-issued yield and cannot be renamed an auction tail.

Native ZN minute filenames exist for each 2018–26 year (and 2017), and owned NQ inputs are already part of the
program. Filename existence does not establish complete held paths, native tick/fee fidelity, result-to-fill
availability or valid current-book joint account histories. No market file body was opened in this review.

## Public evidence already available, and its limit

The earlier evidence sheet records actual dealer/competitive award fields on these public historical releases:

- [2018-01-10 nominal 10-year reopening](https://www.treasurydirect.gov/instit/annceresult/press/preanre/2018/R_20180110_1.pdf).
- [2022-01-12 nominal 10-year reopening](https://www.treasurydirect.gov/instit/annceresult/press/preanre/2022/R_20220112_2.pdf).

It also identifies the [Treasury query](https://www.treasurydirect.gov/auctions/auction-query/),
[historical result archive](https://www.treasurydirect.gov/auctions/auction-previous-announcements-results/)
and [publication timeline](https://www.treasurydirect.gov/research-center/timeline/auctions/) as free routes.
These are retained source findings, **not newly requested/downloaded/verified in this follow-up**. Two releases
show field feasibility; they do not prove a complete point-in-time 2018–26 panel, pre-2018 reference history,
original release/correction vintages or safe intraday receipt delays. No new public archive was established.
No Treasury or EIA host/network-policy change, blocked-host request or search-tool retry was attempted.

## Why dealer awards do not identify an immediate forced ZN order

Primary dealers participate competitively in auctions and can acquire actual cash-security inventory. However:

- Awarded quantity is not unexpected **unhedged residual** inventory. Dealers can prehedge bids, distribute
  awards, retain duration, or hedge with cash, swaps or a different futures contract.
- A larger dealer share can reflect weak end-investor demand, the dealer's bid decisions and price concessions;
  it does not alone identify a later sign or compulsory hedge fraction.
- The previously inspected [New York Fed Staff Report299, revised March2024](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr299.pdf)
  associates issuance inventory with subsequent appreciation across **weeks** and reports limited futures
  hedging of issuance-driven changes. That evidence does not support an invented release-afternoon ZN short.
- The [Fed auction-cycle discussion](https://libertystreeteconomics.newyorkfed.org/2015/10/dealers-positions-and-the-auction-cycle/)
  distinguishes auction purchases from inventory retained afterwards. No fresh directional claim is attached to it.

No source inspected here establishes a hedge deadline, residual duration, observed hedge fraction or the gross
premium required to clear realistic ZN round-trip costs. Dollar awards cannot be converted directly into futures
notional or assumed to be fully hedged. A hypothetical DV01 conversion is scenario arithmetic, not measured flow.

## Reopening this source question would require

1. An archived result panel with original dealer accepted and total competitive accepted fields, stable CUSIP /
   tenor / reopening definitions, historical references and release/correction/availability provenance.
2. Independent evidence connecting the **unexpected unhedged** allocation component to a specified ZN hedging
   direction, time and economically plausible magnitude. A known weak price reaction or a different clock is
   not this evidence.
3. An eight-question TEST evidence sheet and a newly committed at-most-five-configuration plan **before** any
   raw return screen, with the existing auction/BTC/dealer-award history preserved. The same-window calendar-only
   baseline, native contract costs, realistic publication-to-fill delay and full source/held-path audits belong
   in that plan. Only then could a gross screen determine whether any economic evaluation is warranted.

This does not establish that all public sources or mechanisms are exhausted. It supplies no new user-action
blocker and does not justify pausing the whole bounded hunt. No evidence sheet marked TEST or candidate plan was
created from this review.
