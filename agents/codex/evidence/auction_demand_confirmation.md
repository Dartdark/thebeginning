# NQ Auction Demand Confirmation: TEST

Summary: Test a new standalone NQ entry based on published Treasury bid-to-cover deviations confirmed by ZN.
The independent input is an auction result, not a copied calendar/price strategy or market-consensus surprise.
Local design intake contains368eligible auctions; history/price confirmation will reduce power materially.
Five frozen models,2018-22 first. Historical publication/receipt and retrospective-vintage limits remain.

Sources: data/treasury_auctions.csv; raw NQ/ZN minute files; analysis/treasury_auction_test.py;
analysis/anti_forced_flow_ideas_test.py; agents/codex/evidence/treasury_dealer_award_next_session.md;
TIER_LIST.md Treasury/Cross-asset rows. Two parallel read-only novelty/intake screens ran no return tests.
Official public source inspected:
https://www.treasurydirect.gov/auctions/auction-results/
https://www.treasurydirect.gov/files/laws-and-regulations/auction-regulations-uoc/auct-reg-gsr-31-cfr-356.pdf

## 1. Participant and proposed mechanism

Treasury auctions reveal the amount bid relative to securities awarded. Primary dealers and investors absorb
issuance; changes in demand can affect yields and risk pricing. A high ratio relative to comparable prior auctions
might support bond prices, and a low ratio might pressure them. NQ's rate sensitivity could transmit that change
into a slower equity repricing. This is a hypothesis: no compulsory equity order, dealer inventory or equity hedge
fraction is observed. ZN corroboration is required because bid-to-cover alone need not move rates.

## 2. Information before entry

Use nominal fixed-rate auctions closing13:00ET=12:00CT. Bid-to-cover becomes an input only after the auction,
never before. Public Treasury results are posted after conclusion, but the local CSV records the bidding deadline,
not original result-publication/receipt timestamps. Primary decisions use12:15CT; a prespecified5min variant
uses12:05. Market entry adds a further whole-minute delay. Neither delay is proof of every historical receipt.
Compare BTC with the median last6 strictly earlier same-tenor/same-reopening results,min4. No full-sample rank.

## 3. Transmission and novelty

Trade NQ in the sign of BTC's historical deviation only when ZN's pre-result-to-decision price change agrees.
ES/ZN are not traded legs. Existing NQ own-price auction momentum and unconditional ZN calendar trades are
prior weak evidence, not this entry. This is not the rejected next-morning dealer-award inventory hypothesis:
no dealer award data, unsupported overnight inventory or unobserved next-day forced-order deadline is used.

## 4. Inputs and availability

Local Treasury results cover674nominal13:00ET auctions fromDecember2017--October2026,368in2018-22;
no missing positive BTC and no simultaneous design events found in intake. Nominal tenor buckets2/3/5/7/10/
20/30years, with shortened reopening labels mapped to their original tenor. Reopening baselines stay separate.
At least4same-group history values leave326design rows in the intake estimate; actual complete-price counts
are not yet measured. NQ/ZN native CT close-stamped prices and ATR are local. No forwardfill/conflicting keys.
Historical result revision vintages and exact receipt times are unverified. No paid input/key/account needed.

## 5. Costs and overlap

NQ$7.25RT plus1tick($5) each market/stopfill; target1pointthrough. NativeMNQ$1.24RT plus$0.50/fill independently.
Fourtickfillstress. One position/trade per auction date, stop0.15priorATR,target0.30,flat12:55ahead of13:00news.
Exposure can overlap RS/VB/Twin cash positions; no empty window, hedge or pre-breach protection is established.

## 6. Power before returns

At approximately150confirmed design trades and assumed SD$500/NQ, t2 needs net$82/trade and t6$245.
AtSD$800 the hurdles are$131/$392. Add costs for the gross hurdle. These are assumptions, not observed profits.
Independent information is at most one event/date; splitting tenor/reopening/year further weakens effective power.
The ambitious t6 goal may be infeasible here; no threshold loosening or false independence to force it.

## 7. Prior work and falsifiers

Treasury calendar pressure is small after ZNcosts. NQ own first5min auction reaction and broad ZNlead/lag were
already weak. No result-conditioned bid_to_cover_ratio return test was found. BTC's historical deviation is NOT
a market-consensus surprise or a yield tail; high_yield is unused because contemporaneous WI yields are absent.
Reject if design/net fails, if the BTC gate removes profitable ZN-response-control trades, or if uniform and
within-year/tenor/reopening matched random dropping does as well. Do not select controls after a failure.

## 8. Failure and diversification

BTC varies with offering size, tenor, dealer bidding and reopening structure; a high ratio can be stale/strategic
bidding rather than new demand. Rates/equity correlation can change sign; information may finish repricing before
entry. Auctions/news/poor liquidity can cluster NQ losses. Orders consume liquidity; stops gap beyond their
nominal risk. Missing result/reference/current-price inputs block entries; held gaps stay reported, never deleted.
Only valid joint whole-contract BASE/ADD/replacement/EMPTY account paths could establish account utility later.

TEST the explicitly result-conditioned, delayed same-afternoon specification. This does not override the earlier
DON'T TEST dealer-award next-morning sheet. A failed hypothesis ends its validation, not the t6 program.
