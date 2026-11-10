# Gold: market map and a first hypothesis, before returns

Summary: Gold responds to investment demand, real yields, currencies, risk and slower physical/reserve demand.
For intraday trading, focus on who needs to adjust risk and whether their orders persist after an observable trigger.
First working hypothesis: published managed-money crowding amplifies intraday downside continuation when gold breaks down.
This is untested; crowding is not a standalone short signal and COT does not reveal today's stops or leverage.
No return tests/code promotion/live changes; next research step is participant-data and release-clock admission.

User request November 9, 2026 Pacific: “look at gold and build a hypothesis first,” including why it moves,
who moves it and how to exploit a possible effect. Source/repository review only; **0 new return trials**.
Local starting head `cc168c49`; current Claude tier checked at `9810a528`. Source sheet:
[`gold_crowded_longs_20261110.md`](../evidence/gold_crowded_longs_20261110.md).
No economic preregistration is claimed: the economics come before parameter/code selection in this phase.

## Why gold moves

The useful distinction is between changing the desired ownership of gold and the orders that transmit
that change into prices. At a given quote, urgency and available liquidity matter; each executed contract
still has a buyer and seller. A category being net long does not mean the whole futures market is net long.

| Driver | Economic channel | Research implication |
|---|---|---|
| Real interest rates | Gold has no coupon; changing inflation-adjusted safe yields changes its opportunity cost | Unexpected rate changes matter, but nominal Treasury futures alone do not identify real yields |
| US dollar | Changes dollar gold's relative price and investors' currency exposure | Currency and gold repricing can be simultaneous; a correlation is not a catch-up trade |
| Risk and funding liquidity | Demand for protection can rise; investors can also sell liquid gold to raise cash | Gold can fall alongside stocks during deleveraging; blanket “safe haven” timing is inadequate |
| Investment flows and positioning | Portfolio allocations, ETF flows and futures risk adjustments change marginal demand | The actionable question is whether a measurable state forecasts subsequent aggressive orders |
| Physical use, supply and reserves | Jewellery/industrial demand, recycling, mine production and reserve policies affect the balance | Important background; many observations are too slow or opaque for an intraday entry |

These are context, not a fixed forecasting equation. The WGC's [GRAM framework](https://www.gold.org/goldhub/tools/gold-return-attribution-model)
separates growth, uncertainty, opportunity cost and momentum, and explicitly treats the relationships as varying.
Its monthly/weekly attribution is not a one-minute predictive model. The WGC's
[2022 liquidity discussion](https://www.gold.org/goldhub/gold-focus/2022/05/you-asked-we-answered-explaining-golds-recent-performance)
describes gold sales to meet cash/redemption/margin needs; this supports considering liquidation, not a proven signal.

## Who trades and what that can mean

| Participant | Reason for activity | What we can and cannot observe |
|---|---|---|
| Macro funds, CTAs and other managed money | Directional allocation, trend/risk changes and possible deleveraging | Public weekly category positions; current stops, leverage and next orders are private |
| Bullion banks, dealers and swap intermediaries | Client execution, financing and inventory/derivative hedges | Some category positions/benchmark activity; a bank short need not be a directional bearish bet |
| ETF investors and authorized participants | Investment allocation, share creations/redemptions and arbitrage | Published shares/holdings may be delayed; changes cannot automatically be mapped to a same-time futures order |
| Central banks and reserve managers | Reserve allocation and diversification | Mostly slower disclosures, not a dependable intraday schedule |
| Miners, refiners, fabricators and other physical users | Hedge production, processing, supply and inventory needs | Physical risk can explain futures hedges; a profitable physical book can have a losing futures leg |

[CME gold participant overview](https://www.cmegroup.com/trading/metals/files/fact-card-gold-futures-options.pdf)
and [CFTC category definitions](https://www.cftc.gov/MarketReports/CommitmentsofTraders/DisaggregatedExplanatoryNotes/index.htm)
support the participant distinctions; they do not identify who traded an individual candle.

London OTC and exchange futures are linked price-discovery venues. The
[WGC market-structure guide](https://www.gold.org/about-us/what-we-do/market-infrastructure/gold-trading-wholesale-market)
explains their different trading arrangements. Arbitrage, forwards and inventory connect venues, but gold
location, delivery, funding and balance-sheet constraints mean the link is not an instantaneous costless identity.

## First working hypothesis: crowded-long liquidation

**When the latest publicly available CFTC report shows unusually high managed-money net long exposure in
COMEX gold, a subsequent US-morning downside break is more likely to continue over the next intraday
interval than an otherwise comparable break with lighter positioning.**

Proposed causal chain:
1. Some funds begin the episode with substantial long exposure.
2. Gold starts falling for information, liquidity or another reason; crowding alone does not time this.
3. A subset may cut positions under stops, volatility limits, funding or portfolio risk constraints.
4. If selling is sufficiently persistent relative to liquidity, an entry after the observable break can participate
   in further downside. If selling already completed or buyers absorb it, there is no usable edge.

This chain is **our conjecture**, not a measured fact. The
[WGC March 2026 retrospective](https://www.gold.org/goldhub/research/gold-market-commentary-march-2026)
discusses a COMEX long unwind and possible CTA/cross-asset deleveraging. Its account is partly estimated/anecdotal
and monthly; it does not validate the proposed intraday clock, signal or trade. We do not choose a historical
cutoff/threshold because that particular episode looks persuasive.

Draft measurable inputs:
- Crowding: `(managed_money_longs − managed_money_shorts) / total_open_interest`, compared with its own
  past published distribution. Retain gross longs/shorts/spreading for interpretation; net exposure is not leverage.
- Trigger: a fixed downside break, such as the previous completed exchange session's low, during a defined
  liquid US-morning window. This is an observable proxy for weakness, not evidence of exact stop locations.
- Response: gold's next approximately 30 minutes, using a next-minute-open entry, a protected risk cap and
  time exit in a later frozen strategy. No position is entered merely because a report is crowded.

These are **draft design elements**, not tested/final parameter choices. Freeze the percentile/lookback,
session clock, breakout definition, stop/exit and whole-MGC quantity before any economic result. Do not
create a broad feature search or adjust definitions after 2023+ outcomes.

## The comparison that decides whether this adds anything

The essential control is the **same downside trigger without the positioning input**, on known source dates.
Then compare matched time/volatility conditions and equal-count random kept weeks with the same costs/exits.
Crowding clusters by week, so infer uncertainty from report/week blocks rather than treating daily trades as
independent. Report total net and removed-trade performance; mean-per-trade improvement alone is insufficient.

Reject the intended case if the positioning interaction adds no predictive/executable value; if proper report
publication timing erases the effect; if a few crisis weeks drive it; if the gross move cannot cover native MGC
costs; or if opportunities are too sparse for the evaluation deadline. At the account stage it must improve
the updated BASE/ADD/REPLACE/EMPTY comparison before a floor breach, not just look uncorrelated annually.

A gold short might help on some episodes where gold and the NQ book fall together. It can also lose with the
book or be squeezed. Neither low unconditional correlation nor reliable protection is assumed.

## What is verified, and the missing admission work

Verified by source/metadata inspection: participant definitions, public disaggregated COT archive listings,
normal publication convention, existing GC price files and the local Legacy COT schema. The latter has
commercial/non-commercial columns, so it must not be silently relabeled as Managed Money.

[CFTC's timing FAQ](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) says Tuesday observations
are normally released Friday at 15:30 Eastern, with exceptions. It does not offer a complete historical release list.
Holiday/shutdown/catch-up clocks and source corrections need explicit handling; do not mechanically backdate.
[Official historical archives](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm)
list the disaggregated series needed for participant-specific work. That is a free acquisition route, not a claim
that a complete vintage/publication-aware gold panel has already been downloaded and admitted.

Next research check: a genuine gold disaggregated sample with identifier/fields, sufficient earlier warmup,
and at least one exceptional release week; then a no-return event/frequency/cost census. Data need D56 records
this exact distinction. No user purchase/export is requested by this report.

**Can strategy code be made? Conditional yes.** A prototype can combine release-aware weekly states, a
causal minute-price trigger and bounded MGC exits once those inputs/rules are admitted. That does not establish
profitability. No trading code, performance metrics, independent check or live change is claimed in this phase.

## Other mechanisms retained and prior failures respected

Gold has explicit benchmark auctions at 10:30/15:00 London and a COMEX settlement clock; calendar conversion
must respect US/UK DST and historical rules. [IBA](https://www.ice.com/iba/lbma-precious-metals)
documents auction order rounds and imbalance sharing. A residual obligation does not prove a particular
futures hedge, direction or time. [LBMA's FAQ](https://www.lbma.org.uk/prices-and-data/lbma-gold-price/lbma-gold-price)
distinguishes live redistributor information from delayed website prices. A final historical auction value cannot
be used as if known during the auction. Actual signed-round data is a separate data-dependent lead.

The repo's `analysis/s_rank_gc_round1_test.py` already covers broad auction follow/fade, Shanghai clocks,
delivery/option cycles, macro reactions and settlement windows. `analysis/gold_rates_dollar_test.py` has
extensive negative catch-up/relative-price evidence. Prior Asian breakouts, first-notice liquidation,
GC_COMBO and COT-index work also retain their outcomes. This report neither reruns nor revives them.

The [52-week commodity COT source review](cot_52week_4534852.md) found little market-timing evidence and
does not justify a COT strategy on its own. This is a separate participant-state interaction hypothesis,
held at **NEEDS DATA / untested**, not a promotion based on that paper. Source-level research merit is the
measurable independent state and falsifiable control, not any demonstrated return.
