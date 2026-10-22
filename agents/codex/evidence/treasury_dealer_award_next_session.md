# Actual dealer auction awards → next-morning ZN: DON'T TEST

Summary: Actual primary-dealer awards are a new, free information input, unlike the previously tested auction calendar.
The inventory effect is documented across weeks; a forced next-morning futures order is not established.
At an assumed 89 design trades, t = 2 needs $70–102 gross per ZN against $38.50 costs.
The proposed window has a 96.2% weekday-weighted flat-minute estimate, but a gap alone does not justify a trade.
Do not backtest this specification without independent evidence for its intraday clock and size.

Evidence inventory: `analysis/codex_free_data_evidence_inventory.py` →
`analysis/outputs/codex_free_data_evidence/inventory.json` and `auction_inventory.csv`.
Scope record: `agents/codex/plans/free_data_evidence.md`, **41ffc93**. Catalogue/task source: **e097c0f**.
Candidate return tests / strategy trials: **0**. No price fields, research caches, funded bench or live files used.

## 1. Who trades, and why?

Primary dealers must participate competitively in Treasury auctions. Awards create actual cash-security inventory;
dealers subsequently distribute securities and manage risk. The award is known, but neither the remaining inventory
nor a required futures trade follows from it. A dealer can retain the exposure or hedge using other instruments.

The [New York Fed paper, revised March 2024](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr299.pdf)
was checked beyond its abstract: introduction and relevant passages in sections 6.1 and 8. It associates issuance
inventory with subsequent appreciation across weeks and finds limited futures hedging of issuance-driven changes.
This supports an inventory-premium hypothesis, but weakens the claim of compulsory ZN buying at a specified morning
time. It does not establish this proposed intraday trade. The
[Fed's auction-cycle discussion](https://libertystreeteconomics.newyorkfed.org/2015/10/dealers-positions-and-the-auction-cycle/)
also distinguishes auction purchases from inventory retained afterwards.

## 2. Direction, size and timing before entry

Proposed specification for assessing feasibility, **not registered for a return test**: pool nominal 5-, 7- and
10-year note auctions closing at 13:00 ET; compare dealer accepted share with the previous twelve same-tenor auctions;
after an above-median award share, buy ZN the following regular session at 07:46 CT, exit 08:25 CT. No overnight
position, price-direction filter or selection by the funded roster's holdings. Initial issues and reopenings would
need appropriate separate controls. The entry/exit clock is a gap-directed proposal, not a documented dealer deadline.

Use `primary_dealer_accepted / total_competitive_accepted`. Do not include SOMA or noncompetitive awards in that
denominator. Two freely accessible historical result PDFs were spot-checked:

| Auction result | Dealer accepted | Competitive accepted | Dealer share |
|---|---:|---:|---:|
| [2018-01-10, nominal 10-year reopening](https://www.treasurydirect.gov/instit/annceresult/press/preanre/2018/R_20180110_1.pdf) | $4.407bn | $19.992bn | 22.05% |
| [2022-01-12, nominal 10-year reopening](https://www.treasurydirect.gov/instit/annceresult/press/preanre/2022/R_20220112_2.pdf) | $5.978bn | $35.992bn | 16.61% |

These are auction purchases, not unhedged holdings or known next-morning demand. An illustrative $1bn unexpected
inventory award, seven-year modified duration and $70/bp ZN DV01 imply 10,000 contracts **if fully futures-hedged**.
All three quantities are planning assumptions; actual hedge fraction and unwind timing are unknown, including zero.
Owned ZN files show median 85,424 contracts over this 40-bar window across 1,249 complete weekday windows in 2018–22
(10th percentile 47,606). The hypothetical hedge is 11.7% of that median, but it is **not measured order pressure**;
establishing that fraction or its sign at this clock is the missing evidence. Cash awards cannot be equated directly
with futures contract notional. The paper's limited hedging result particularly cautions against the full-hedge scenario.

## 3. Does it reach the traded contract?

ZN is an owned-data, direct duration-hedge candidate for medium/long Treasury notes. It is outside the preferred
NQ/ES target. A 5- or 7-year award can instead reach other Treasury futures, cash securities or swaps; even 10-year
cash exposure does not guarantee ZN orders. No claim of compelled NQ/ES hedging is made. A cross-asset equity proxy
would add another unsupported link and is excluded.

## 4. New input, history, timing and cost

The repository owns ZN minutes and the auction calendar but **not dealer awards**. Actual awards vary independently
of the price trend, unlike an auction-day momentum rule. Cost to retrieve the public results is **$0**; assembly and
validation remain work, not a subscription requirement.

- [Treasury auction query](https://www.treasurydirect.gov/auctions/auction-query/) offers downloadable historical
  results, with non-TIPS history from July 1998. Do not assume every recently added field existed in 2018.
- The dated 2018/2022 PDFs above establish the needed dealer/competitive award fields on actual historical releases.
  The [previous-result archive](https://www.treasurydirect.gov/auctions/auction-previous-announcements-results/)
  supplies the public historical route. Full 2017 warm-up and 2018–22 coverage have **not** been bulk downloaded or audited.
- [Treasury's publication timeline](https://www.treasurydirect.gov/research-center/timeline/auctions/) records automated
  PDF posting and simultaneous publication of additional bidder statistics in 2004. Results were targeted within
  minutes of competitive closing. A following-session entry provides a substantial buffer; this is publication policy,
  not a receipt-time log for every file. Exceptional delayed or corrected releases must be screened separately.
- The repo calendar begins in December 2017, insufficient for twelve prior same-tenor awards in January 2018.
  A free 2017 result census is necessary before claiming the planning sample is usable. No reconstructed-vintage
  or corrected value may silently replace what was available at the decision.

## 5. Costs and actual occupancy gap

Existing `analysis/treasury_auction_test.py` specifies $1,000/point, tick 1/64 = $15.625, commission $7.25 and one tick
slippage per side: **$38.50 per ZN round trip**. The NQ $17.25 convention is inapplicable. There is no supported
expected 40-minute move; gross $57.75 would only clear 1.5× costs, below the planning t = 2 hurdle.

The saved funded-roster minute map, including ES MOC at 2 MES, gives these marginal flat-minute fractions for
07:46–08:25 CT: Monday 49.2%, Tuesday–Thursday 100%, Friday 83.0%. Equal weekday weighting gives 86.4%.
Weighting by following cash-session weekdays of the 178 eligible auction dates gives **96.2%**
(Tuesday 19, Wednesday 37, Thursday 82, Friday 40).
Monday overnight holdings and Friday morning exposure are the main existing overlaps.

This uses the saved map's weekday averages, **not actual auction-conditioned occupancy**, and does not imply a
96.2% chance the entire window is flat. XNYS is only a descriptive next-session proxy; actual ZN/SIFMA holiday and
early-close rules and full bars must be established before a plan. All events would be tested irrespective of overlap.

## 6. Numerical power check

The owned schedule has **178** qualifying auction dates: 36/34/36/36/36 by 2018/2019/2020/2021/2022, and
59/59/60 by 5/7/10-year tenor. There are no simultaneous qualifying auctions. The 13:00-ET condition excludes
early-close auctions. Assuming half exceed their prior same-tenor median gives **89 trades**, not an observed signal count.
Missing warm-up/results/bars would reduce it. Inventory autocorrelation could reduce effective n further.

| Assumed per-trade SD, one ZN | n | Net mean for t ≥ 2 | Gross mean including $38.50 costs | Gross ticks |
|---|---:|---:|---:|---:|
| $150 | 89 | $31.80 | $70.30 | 4.50 |
| $300 sensitivity | 89 | $63.60 | $102.10 | 6.53 |

Formula: `2 × assumed_SD / sqrt(n)`; gross adds round-trip costs. SDs are scenario assumptions for a short Treasury
window, not measured strategy SDs or price-derived estimates. These are optimistic single-trial screening hurdles,
not the repository's promotion threshold or a power calculation guaranteeing detection. No source establishes the
required gross premium inside this clock; spreading a weekly premium into forty minutes would invent evidence.

## 7. Catalogue difference and decision

TIER_LIST's Treasury auction row and `analysis/treasury_auction_test.py` already test pre-auction shorts,
same-afternoon longs, maturity subsets and price/volume/calendar proxies; related optimisation includes offering size.
Those results are discouraging cost context, not a new run here. The owned calendar and old scripts do not use
actual dealer accepted allocations. This sheet proposes a **new input within an already investigated auction family**;
changing the entry time by itself would not make it new. It is not counted as another fresh calendar effect.

**DON'T TEST this intraday specification.** Timely free data and a gap pass; identified intraday direction, executable
forced flow and an evidence-based expected move do not. Reconsider only with independent evidence connecting actual
award surprises to next-session intraday distribution/hedging. Do not pay for data, scan morning windows or run a
return test to choose the clock. Claude reviews this evidence sheet before any later plan.
