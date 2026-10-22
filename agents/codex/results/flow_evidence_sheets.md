# Flow evidence sheets: WATCH — four proposals for comparison, no return tests
Summary: Four evidence sheets, checked against the repo through Claude `2d1f279`; no competing Claude proposal was read.
Priority: A opening-auction demand, B post-auction reversal, D signed expiry hedging, C asset-weighted ETF resets.
A/B have identifiable exchange data and useful gaps; D needs delivery-lag verification; C lacks observable residual demand.
All require external inputs before an honest test. No purchases, candidate signals, returns or account simulations; roster unchanged.
Plan: `agents/codex/plans/flow_evidence_sheets.md`, commit `574f81b`   Script: `analysis/codex_flow_evidence_inventory.py`   Output: `analysis/outputs/codex_flow_evidence_sheets/`   Return trials: **0**

## Decision and common evidence standard

**My first choice is A for data inspection, with B sharing its data request.** This is a research-priority judgment,
not a profitability ranking or permission to buy data. Four proposals represent three flow families: A/B share the
auction channel and should not be counted as independent diversification. No candidate is ready for a return test
using only the current repo. Public documentation verifies mechanics and data products; it does not verify an edge.

Each sheet separates (a) a documented obligation or observable position change, (b) a proposed transmission into
the traded future, and (c) the still-unverified prediction that pressure persists long enough to exceed costs.
Proposed clocks illustrate an executable research question, not finalized parameters. The user chooses among the
competing sheets before any new rule-specific preregistration and cheap design screen.

### Gap and cost inventory — descriptive, not candidate performance

These calculations reuse the **committed 2018–22 actual-roster minute map**, not zero daily P&L. No existing
strategy was re-executed to regenerate it. It includes full planned-size NQ lines, actual overnight Bridge/CL
intervals, and ES MOC 2 MES. Cushion scaling can reduce actual occupancy. CT means America/Chicago; all feed
times must be converted from their documented exchange zone, not interpreted as CT by default.

| Proposal | Future | Decision CT | Illustrative next-bar holding window | Flat decision dates / 1,289 | Unoccupied minutes in that window |
|---|---|---|---|---:|---:|
| A: SPY opening demand | ES | 08:15 | 08:16–08:25 | 1,115 | 86.5% |
| B: SPY post-auction reversal | ES | 15:01 | 15:02–15:10 | 1,211 | 93.9% |
| C: ETF reset demand | NQ | 14:31 | 14:32–14:49 | 924 | 71.9% |
| D: SPX expiry hedge adjustment | ES | 14:31 | 14:32–14:49 | 924 | 71.9% |

Flat-decision dates are **pre-signal upper limits**, not qualifying trades or guaranteed complete flat windows.
The saved map contains marginal minute occupancy, not joint event histories. Candidate-specific overlap must be
measured after selection. The script also saves mathematically valid bounds on completely flat windows.

| Weekday | A window minutes flat | B window minutes flat | C/D window minutes flat |
|---|---:|---:|---:|
| Monday | 49.2% | 69.8% | 28.3% |
| Tuesday | 100% | 100% | 82.2% |
| Wednesday | 100% | 100% | 84.5% |
| Thursday | 100% | 100% | 79.7% |
| Friday | 83.0% | 100% | 85.0% |

The baseline repo market round trip costs **$30 per full ES (0.60 point)** or **$17.25 per full NQ (0.8625 point)**.
A prospective cheap screen at 1.5× baseline costs therefore needs average gross **$45/ES (0.90 point)** or
**$25.875/NQ (1.29375 points)**, before its statistical/stability gates. These are hurdles, not estimated returns.
Opening/after-close spread and latency stress may require higher costs. Native MES/MNQ commissions and fills must
be checked before account-level claims; full-contract costs are not a verified micro fee schedule.

## A — Revised SPY opening-auction demand, traded in ES

**Who trades; what is documented?** Investors submit SPY core-opening orders; liquidity providers can hedge S&P
exposure with ES. SPY tracks the S&P 500 and lists on NYSE Arca ([issuer][spy]). Arca publishes core-open imbalance
information before the auction. Its current schedule shows publication from 08:00 ET, the core auction at 09:30 ET,
and cancellation restrictions on MOO/LOO orders beginning at 09:29 ET ([schedule][nyse-auctions]).

**What is forced, and what is a hypothesis?** Auction instructions create a scheduled need for counterparties if
the orders remain live. At the proposed 09:15 ET observation, they are still cancellable: this is **observable
auction interest, not locked mandatory volume**. The hypothesis is that changes in that interest reveal incremental
pressure whose hedging/price response persists into the pre-open interval. No source establishes that persistence.

**Observable direction and size.** Compare signed SPY total auction imbalance at 08:10 and 08:15 CT; normalize
the change by a trailing scale of completed opening-auction volume, available before today. Proposed direction:
follow a sufficiently large revision. Also retain matched volume, reference/indicative prices and auction type.
The signed total is the explicitly labeled imbalance side applied to total imbalance. **Do not silently use that
side to sign the separate market-imbalance quantity**: the specification labels it as the total's side.
Changing reference prices can alter imbalance without new orders; that distinction must be checked.

**Why ES, why this time?** SPY and ES represent the same equity benchmark, giving a direct hedge route. An
illustrative 08:16–08:25 CT trade ends before the cash open and ONB's opening entry. It has 1,115 flat-decision
dates before any imbalance condition. Friday NFP and Monday carry are the main gap cautions. Closest funded
comparators: ONB for morning exposure and ES MOC for the auction channel; neither is modified here.

**Exact information needed and availability.** Historical **TAQ NYSE Arca Order Imbalances**, SPY only if a vendor
supports symbol filtering; auction-result prints for the trailing denominator; synchronized SPY NBBO and ES
quotes/trades. NYSE advertises Arca imbalance history from **2012-01-30** ([catalog][nyse-history]). Historical
end-of-day packaging is usable to reconstruct messages that a licensed live feed disseminated earlier; replay the
original messages, not a final daily auction summary. Retain original sequence/time fields and check historical
schema/rule changes. A free [sample directory][nyse-samples] exists; only its listing was inspected, not the data.
The repo has ES prices and SPY daily closes, **no auction messages or SPY intraday quotes**.

**Difference from prior failures.** Existing order-flow and MOC tests used NQ futures book/delta or a futures price
move; neither is SPY auction-order data. This is a new external input within an already researched flow family,
not a claim that generic imbalance prediction has not been tested. No exact counterpart was found in the catalog.

**What would disprove it?** Drop it if SPY's core-open messages are often empty/too small, revisions mainly reflect
reference-price changes or cancel before the auction, the ES response is already complete before a delayed entry,
or any return association disappears after controlling for prior ES moves and SPY indicative-price changes.
An effect confined to SPY's premium, with no ES transmission, also fails: one ETF's imbalance is not aggregate
S&P demand, and counterparties may absorb it in ETF inventory or offset it against other products.
Even genuine predictive information fails if average tradable gross does not clear $45/ES under credible fills.

**Readiness / next step.** **Best first data-feasibility check.** Obtain a sample/schema and a symbol-level coverage
and price quote; verify informative event frequency before a return trial. Do not substitute ordinary futures depth.

## B — SPY closing-auction pressure reverses after the auction, traded in ES

**Who trades; what is documented?** Close-benchmarked orders concentrate SPY trading at the Arca closing auction.
The exchange has a scheduled close and publishes auction-specific imbalance information; the timing and fields
are documented in the [auction schedule][nyse-auctions] and [feed specification][nyse-spec-2022].
The current Arca closing schedule publishes from 15:00 ET, enters its freeze at 15:59 ET, and crosses at 16:00 ET
(14:00, 14:59 and 15:00 CT). Historical versions must be checked before applying those times to 2018–22.

**What is forced, and what is a hypothesis?** Still-live eligible closing orders must be matched or remain unfilled
under the auction rules; not every indicative imbalance share is a guaranteed execution. Providers supplying those
orders may carry temporary inventory/hedges. The proposed edge is **temporary pressure relaxing after matching**.
Neither inventory unloading nor an ES reversal is mandated by the auction rule. Informed demand can instead
produce a permanent price change. This distinction makes B less certain than simply observing the auction.

**Observable direction and size.** Save the last valid SPY closing-auction signed total imbalance before the cross,
the corresponding indicative-price displacement versus contemporaneous SPY NBBO, and the actual auction print.
At 15:01 CT, require that the relevant auction-completion message was actually available. Proposed direction:
fade a large pressure reading whose indicative-price displacement agrees with the imbalance. Normalize size by
past auction volume; no final message is allowed to appear earlier than its actual timestamp.

**Why ES, why this time?** Same-benchmark hedge, with no single-stock-to-index leap. Illustrative entry is the
15:02 bar, exit 15:10 CT, allowing a realistic delay after the auction and avoiding a session break. There are 1,211
flat decisions before signal filters; Tue–Fri are completely flat in the mapped window. Closest comparator is
ES MOC: sequential exposure to the same channel could still create correlated losses. Timing alone does not
establish diversification or justify replacing MOC.

**Exact data and availability.** The same Arca history, auction prints and synchronized SPY/ES quotes as A, with
the **closing** auction identifier. Catalog coverage is compatible with 2018–22, subject to a symbol/date audit.
Existing futures minute bars can support a coarse later screen, but not establish executable spreads or latency.
No source dataset was purchased or parsed. A and B may share a data request; they remain separate future trials.

**Difference from prior failures.** Post-settlement fades based on the day's/last-hour's futures return are already
weak; extending MOC beyond the close was also tested. B uses a new auction-demand observation, not the same
price proxy with a new clock. It must explain something incremental beyond those failed return-based controls.
Do not run it if the proposed signal collapses into the last futures price move.

**What would disprove it?** Reject if auction pressure has no measurable transmission into ES, reverses entirely
before 15:02, represents permanent news, or fails the $45/ES gross hurdle with post-close spreads. A profitable
stock auction reversal smaller than the ES/MES cost budget would not solve our problem.

**Readiness / next step.** **Second priority, shared auction-data feasibility work.** Check timestamped sample
completeness, auction matching and signal frequency; do not assume a documented close produces an after-close edge.

## C — Asset-weighted Nasdaq leveraged-ETF reset demand

**Who trades; what is documented?** Daily-reset funds seek a fixed daily multiple of Nasdaq-100 returns, using
stocks/derivatives and their counterparties. [TQQQ][tqqq] and [SQQQ][sqqq] describe +3× and −3× daily objectives;
the fund documentation identifies the daily NAV clock. [CME's explanation][letf-cme] describes why resetting leverage
can require trading index exposure in the direction of the benchmark's move. This verifies a portfolio constraint,
not a particular amount of NQ executed in a particular minute.

**Observable direction and size.** In a simplified linear portfolio with no fees, financing or capital flows,
required exposure adjustment is **D = A × L × (L−1) × r**, where A is prior-NAV assets, L target leverage and r
the benchmark's return since that NAV. Aggregate a fixed point-in-time Nasdaq fund universe, rather than use
today's funds or today's assets throughout history. A proposed signal ranks this dollar demand relative to
contemporaneously observable futures liquidity, at 14:31 CT; follow only unusually large demand to 14:49.

**What is missing from that formula?** Creations/redemptions, counterparty netting and trades already executed
can change or offset the remaining requirement. **D is modeled reset demand, not measured unexecuted orders.**
Today's final shares/AUM are not available merely because an archive later reports today's date. The published
[Ivanov–Lenkey abstract][letf-counter] specifically challenges the simple rebalancing-pressure story once capital
flows are included. Its full paper was not accessible here; treat that as a contrary research lead, not an audited
effect-size estimate. There is no finding for our portfolio in that paper.

**Why NQ, why this time?** Direct Nasdaq exposure/hedging is plausible, unlike the rejected cross-market fixing
proxies. A 14:32–14:49 CT illustration uses the period after LDF exits and before ES MOC enters. Only 924 dates
are flat at the decision before filters. Closest comparator is LDF; future replacement/empty-slot tests would be
essential because this is the same broad source of risk.

**Exact data and availability.** Historical fund-level NAV, shares/assets with publication timestamps, leverage
changes, fund launches/closures, benchmark prices aligned to the fund NAV, holdings/counterparty exposures, and
any genuinely available creation/redemption or execution information. A point-in-time AUM archive vendor or
issuer snapshots must be verified. Current issuer pages are not such an archive. We have NQ prices but none of
the required fund-level history. SEC holdings disclosures alone do not supply timely daily remaining demand.

**Difference from prior failures.** RTH momentum, close-to-close momentum and the LETF family are already tested;
LDF is already funded. The only proposed new information is **time-varying fund scale and credible residual-demand
constraints**. Without it, this is a repeat, not a new idea. Assets merely scaling the same price sign is weak novelty.

**What would disprove it?** Drop before testing if only end-of-day capital-flow observations are available, assets
contribute no meaningful variation beyond old price signals, or realistic capital flows/execution can eliminate
the inferred demand. A later return trial must also clear $25.875/NQ gross and demonstrate contribution beyond LDF.

**Readiness / next step.** **Fourth priority; blocked on observability.** Verify a point-in-time dataset first.
Do not authorize a backtest or buy a general ETF dataset merely because the reset formula exists.

## D — Expiry-related delta decay from observed SPX market-maker position changes

**Who trades; what is documented?** A dealer choosing to keep delta risk near neutral adjusts hedges as option
delta changes with remaining time. PM-settled SPXW contracts lose their remaining optionality at expiry; Cboe's
[specifications][spx-spec] distinguish those contracts from AM-settled SPX. ES is a direct S&P hedge. The hedge
route and rebalance frequency are a risk-management choice, **not an exchange-mandated ES order**.

**Observable direction and size.** Use the latest **received** C1 10-minute cumulative snapshot ending no later
than 14:10 CT and received by 14:25. Per expiring PM series, observed RTH position change is
**q = mm_buy_vol − mm_sell_vol**, subtracting the pre-RTH baseline if a file includes GTH activity. With spot/IV
frozen at information available before the 14:31 decision, estimate
the delta change from 14:31 to 14:49 and the associated hedge adjustment **−100 × Σ q × (delta_end − delta_start)**
in dollars of sensitivity per SPX point; dividing by $50/point gives full-ES contract equivalents. Proposed direction
follows that marginal hedge demand in ES, 14:32–14:49 CT.

This estimates the **time-decay component of observed intraday position changes**, not the dealer community's
total inventory. Starting positions, OTC trades, other venues, transfers, price/volatility moves and existing hedges
are omitted. A dominant omitted book can reverse the true direction. Do not sign prior open interest by assumption,
equate customers with dealers, or call the result a measured total dealer book.

**The data availability gate is substantial.** [Cboe Open-Close][cboe-oc] has C1 10-minute history from 2011-01-03
and delivery minutes after each interval, compatible in principle with 2018–22. Its [specification][cboe-oc-spec]
contains MM buy/sell volume. Values are cumulative through the day: **do not sum cumulative snapshots**, and use
contract volume fields, not trade-count fields. No guaranteed historical receipt lag was verified; a timestamped
interval is not proof it could have been used at its end time.

The more detailed [TBT product][cboe-tbt] starts in 2019 and is delivered **T+1**: it cannot silently replace this
same-day feed in a tradable historical test. It may support later explanatory audits, not same-day inputs. Need
verified intraday receipt timing, contemporaneous SPX/option quotes or IV surfaces, PM contract reference data,
corrections, and ES quotes. None of the signed participant inputs are in our GEX/GEXOI exports. No data were bought.

**Gap and prior work.** The afternoon illustration shares C's 924 flat-decision dates, but actual qualifying PM
expiries must be counted using each historical year's listed expirations. Today's daily-expiry schedule cannot be
backfilled into earlier years. Closest comparators are LDF/ES MOC. Existing gamma-flip, OI pinning and naive GEX
tests do not measure signed MM position changes or time-decay hedging; their failures remain relevant warnings.

**What would disprove it?** Stop before returns if the old live feed cannot reproduce the historical inputs with
a defensible receipt lag, q is too partial to be directionally informative, contracts cannot be identified correctly,
or plausible starting-book assumptions overturn the forecast. A later trial must add information beyond price,
volatility and existing gamma proxies, survive lag/spread stress, and clear $45/ES gross.

**Readiness / next step.** **Third priority, conditional data feasibility only.** Verify the 10-minute feed's historic
delivery and a small sample. A precise Greek calculation cannot compensate for an unknown signed position.

## Comparison, what was excluded, and what happens next

| ID / priority | Observable new input | Mechanics | Main unresolved link | Decision now |
|---|---|---|---|---|
| A / 1 | SPY core-open auction revisions | Actual exchange order interest; cancellable at observation | Does ES react slowly enough after observing the revision? | Inspect auction data feasibility first |
| B / 2 | SPY pre-close imbalance + auction completion | Scheduled matching; future reversal not compelled | Does temporary pressure survive our delayed entry? | Share A's data request; separate hypothesis |
| D / 3 | C1 signed MM position changes + delta decay | Expiry established; hedge policy and total book unknown | Correct sign, history and delivery lag | Conditional; verify delivery before any test |
| C / 4 | Historical ETF assets and reset requirement | Daily leverage objective established | Remaining signed demand after flows and prior execution | Blocked unless residual demand becomes credible |

Excluded from the four: fixed-time macro reactions and broad calendar/expiry patterns already tested; roll-week
shorts already tested; a calendar spread would need separate delivery months and an account-eligibility review;
simple 20/40-day volatility-observation roll-off has a published [index definition][average-risk] but no verified
tracking assets or execution clock here. A published index alone does not demonstrate forced ES orders.

Nasdaq opening-auction interest was considered, but early disclosure moved from 09:28 to 09:25 ET in 2021
([exchange account][nasdaq-open-change]); projecting that extra window backward into 2018 would invent information.
SPY/Arca avoids that specific cross-era assumption, although its own historical rules still require verification.

**Next gate after the user comparison:** choose one research question, verify fields/receipts/coverage and census
its eligible events without looking at forward returns. Require enough events and a detectable effect compatible
with costs before a return study; do not repeat the underpowered minutes-release screen. Then commit a fixed rule,
<=5 variants and the cheap 2018–22 gross-versus-cost/statistical gate. Count that screen as a trial even if it fails.
Only a passing design earns controls, the once-opened candidate holdout, and paired addition/replacement/empty-slot
funded tests. Prior use of 2023+ in the broader research program means fresh forward observations still matter.

## Results, placebos and account level

**Not run**, by task scope. There are no candidate trades, gross returns, Sharpe/PF/t-stat estimates, holdout tables,
placebos, Monte Carlo results or funded-account improvements to report. Return trial count is zero, not four.
Occupancy and fee arithmetic are reproducible with the committed inventory script; its manifest hashes the input map.
No MultiCharts code or changes to live files, funded settings, broker/VPS configuration or API keys.

## Source register — accessed 2026-10-22

Links below establish the indicated mechanics/data availability. A product listing is not a delivered-data audit.
Quoted prices were not obtained; there is no confirmed subscription cost or data purchase authorization.

[nyse-auctions]: https://www.nyse.com/trade/auctions
[nyse-history]: https://www.nyse.com/market-data/historical/taq-order-imbalances
[nyse-samples]: https://ftp.nyse.com/Historical%20Data%20Samples/TAQ%20NYSE%20ARCA%20ORDER%20IMBALANCES/
[nyse-spec-2022]: https://www.nyse.com/publicdocs/nyse/data/Integrated_Feed_Client_Specification_v2.4a.pdf
[spy]: https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy
[tqqq]: https://www.proshares.com/our-etfs/leveraged-and-inverse/tqqq
[sqqq]: https://www.proshares.com/our-etfs/leveraged-and-inverse/sqqq
[letf-cme]: https://www.cmegroup.com/trading/equity-index/files/Leveraged_ETFs.pdf
[letf-counter]: https://pure.psu.edu/en/publications/do-leveraged-etfs-really-amplify-late-day-returns-and-volatility/
[cboe-oc]: https://datashop.cboe.com/cboe-options-open-close-volume-summary
[cboe-oc-spec]: https://datashop.cboe.com/documents/Open_Close_10m_Spec_v1.6.pdf
[cboe-tbt]: https://datashop.cboe.com/enhanced-us-options-trade-by-trade-execution-detail
[spx-spec]: https://www.cboe.com/tradable-products/sp-500/spx-options/spx-specifications/
[average-risk]: https://www.spglobal.com/spdji/en/indices/multi-asset/sp-500-average-daily-risk-control-10-index/
[nasdaq-open-change]: https://www.nasdaq.com/articles/more-inclusive-opening-auctions-make-better-markets-for-all-2021-05-27
