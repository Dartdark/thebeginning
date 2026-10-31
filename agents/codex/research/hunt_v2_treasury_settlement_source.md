# Hunt v2: amount-aware Treasury settlement cash — NEEDS DATA / no TEST

Decision: **do not register a return experiment now**. Net issuance settlement is a different input from
auction-day bid-to-cover, dealer allotment or a when-issued yield tail. The current repository does not
establish the dated private-sector settlement cash amount, its historical knowledge clock, or a supported
intraday ZN hedge/funding direction. Gross auction offering amounts cannot substitute for that net input.

Source-only scope,2026-10-26: AGENTS.md, BUILDER_BRIEF.md, RESEARCH_CONTROLS.md, LESSONS.md,
TASK_strategy_hunt_v2.md and current v2 progress read first. Work remains on codex/work. Claude source
**615485fca3160a4c48761f44b0d1972e7b623ef4** was inspected read-only, including TIER_LIST/MINED_INDEX,
tree names and the Treasury source definition. No Claude-branch writes, commits, network requests, raw
price/return/ledger reads, data-row parsing, strategy imports or financial calculations occurred.
This review changes **0 hypotheses,0 gross screens,0 counted evaluations**. Root owns counters; the
checkpoint read here is3/60 evaluations,2/10 hypotheses,2 gross screens. H01/H02 stay CLOSED.

## Distinct question and economic link

Proposed source question only, not a registered trade: does a large, preknown Treasury settlement-day
cash requirement relative to maturing private holdings cause temporary funding or balance-sheet pressure
that reaches ZN during a documented executable intraday window?

Successful Treasury bidders owe payment on issue/settlement dates, while holders receive principal and
coupons on contractual payment dates. This establishes real dated cash obligations. It does **not** by
itself identify a compulsory ZN buy or sell. A bidder can fund in repo, use existing cash, hold securities,
distribute them, or hedge with swaps, other Treasury futures or cash bonds. The cash-flow identity does
not determine which hedge is outstanding at a particular minute or how much duration remains unhedged.
No source reviewed here establishes the required hedge fraction, direction or an intraday deadline for
this proposed ZN trade. Assigning a morning or settlement-close window would invent the missing clock.

Even an accurate gross issuance panel would be insufficient. Net private cash settlement needs the
relevant maturing principal, coupons/accrued interest and issuance cash price, plus consistent treatment
of reopenings, bill discounts, inflation adjustments, SOMA/noncompetitive additions and holders whose
cash is not the same private funding pool. Treasury spending, other Treasury General Account flows,
reserve distribution and money-market/repo offsets prevent gross issuance from equalling a measured
reserve drain or futures order. A realized end-of-day reserve change would also be too late to justify
an earlier entry unless its pre-entry forecast and information clock were independently specified.

## Prior family exclusions

| Existing source | What is already covered | Consequence |
|---|---|---|
| `analysis/treasury_auction_test.py`, latest TIER_LIST Treasury row | Pre-auction short and post-auction long, tenor/calendar/volume variants; related optimisation explicitly includes offering size. | Another large-offering auction-day cut is prior research, not this new net-settlement input. Do not rerun it. |
| `agents/codex/evidence/treasury_dealer_award_next_session.md` | Actual dealer award share is distinct from calendar/BTC, but the proposed next-morning futures clock was DON'T TEST; the cited inventory literature works across weeks and reports limited futures hedging. | Do not infer an immediate settlement hedge from gross awards or recycle the already rejected morning clock. |
| `agents/codex/research/hunt_v2_auction_allotment_source.md` | Same-afternoon unhedged dealer residual/allotment data and clock are not established. | This review does not reopen that completed allocation gate. |
| `agents/codex/research/distinct_input_feasibility_20261026.md` | Already identifies Treasury settlement/reserve-drain as NEEDS DATA because issue/payment/maturity and net-cash inputs are absent. | Preserve that result; do not run its unchanged data audit again. This review checks only whether the newer source adds the missing input or causal evidence. |
| Latest TIER_LIST/MINED_INDEX month-end Treasury extension entry, `analysis/zn_month_end_test.py` | Scheduled duration-extension/calendar effect is already tested. | Month-end/refunding labels are not a substitute for actual cash settlement or a new untested mechanism. |

## Current-source delta and input readiness

`git diff --name-status 92b1d4c..615485f -- data/treasury_auctions.csv` is empty. The latest change to that
file remains **72f11f9**, the original real auction-calendar study. Header-only comparison at both source
pins is identical:

```text
auction_date,security_type,security_term,closing_time_comp,reopening,offering_amt,
bid_to_cover_ratio,high_yield,cusip,inflation_index_security,floating_rate
```

No data values were opened. The schema contains CUSIP and an auction date but no issue/payment date,
maturity date, accepted cash amount/price, accrued interest, maturity principal holder allocation,
coupon cash-flow schedule, original announcement/revision time or receipt history. CUSIP alone does not
recover those missing values. The source script describes nominal note/bond auctions, not a complete
bill/coupon redemption and private-sector funding panel. The repository tree at615485f establishes no
new settlement/redemption/TGA input that repairs these limitations. No second header/data audit was run.

Before TEST, a new admissible input would have to establish:

1. A complete point-in-time issue/settlement/maturity cash-flow panel, including a sufficient pre2018
   outstanding-security history so2018 redemptions are not left-censored.
2. Private-sector versus official/SOMA treatment and issuance/maturity/coupon cash arithmetic, with
   reopening/discount/accrual conventions and original announcement/correction knowledge times.
3. A primary empirical/mechanical link giving expected ZN hedge/funding direction, size and a defensible
   intraday decision→fill→exit clock. A cash obligation alone does not supply these.
4. A frozen calendar-only/auction-only control, actual ZN native per-contract costs, the gross cost hurdle,
   plausible opportunity count/power and current-book exposure question before any price-return look.

These are research prerequisites, not a request to buy data, create accounts, change network policy or
touch a broker. No public-source download, 403 retry or unchanged completed-source audit was attempted.
This is a new-source eligibility record, not a user-action access blocker or a reason to pause the hunt.

## Next action

**NEEDS DATA and independent intraday transmission evidence; no TEST sheet/preregistration/returns.**
Do not count a hypothetical net-settlement proxy as H03 or fill missing cash dates from an auction
calendar. A future genuinely admitted input can support a new eight-question mechanism sheet and only
then a committed at-most-five-configuration plan. Continue a different priority search meanwhile; this
bounded source result does not claim that all forced-flow mechanisms are exhausted.
