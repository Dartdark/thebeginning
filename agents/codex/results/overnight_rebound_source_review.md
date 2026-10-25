# Overnight Rebound source and engine: PASS WITH LIMITS

Summary: No material causal execution blocker found against the frozen source-replication plan.
The supplied synthetic suite and independent Friday/Sunday, short-gap, timing and account-calendar fixtures pass.
The source has no explicit16:45ET/weekend guard; its safety exit is a next-bar cash-session instruction.
The older research supports related hypotheses, while a July2026 primary update reports a faded European-open drift.
This is not independent full-data replication, platform parity, broker permission or a promotion verdict.

Plan: `agents/codex/plans/overnight_rebound.md`, preregistered **d94d815**.
Script: `analysis/codex_rebound_review.py`. Output: `analysis/outputs/codex_rebound/independent_review.json`.
Source hash: `68b90e130b7298a98daf70933f860dd96130ab5dede66d01e86aea2d31214e41`. Engine hash: `231c5e60a09c75713a5f8f059da9db5d88db5d46fc4262f56f26b84e5f12d5db`. New economic trials: **0**.
No price-history cache, strategy return output, live/VPS/broker configuration or API key was opened.

## Source and clock audit

- Source lines5/19/25–28 assume an ET-stamped PC chart and subtract60 minutes. The CT research grid must normalize
  that declared display, not subtract60 again. Raw ET Date matters after23:00CT; normal17:01 entries share the same calendar date.
- Header line6's claim that a wrong clock necessarily gives no trades is not generally true: line45 tests `>=EntryCT`,
  not equality. A wrong shift can produce a different, late strategy rather than no strategy.
- Lines30–42 build cash open/range from the08:31-labeled bar's open through the15:00 close; range is known before entry.
  The exact15:00 signal is required. Missing/shortened cash sessions can skip the evening signal; there is no lookback-history array to repair.
- Lines45–49 consume the armed signal once. A normal down Friday remains armed until Sunday because no Friday-evening/Saturday
  bars consume it. Sunday quantity uses raw chart Date/DayOfWeek, not the adjusted `CTt`; late23:00CT already belongs to Monday ET.
- Entry17:01 close submits next-native-bar market, normally the17:02-labeled bar's open (about17:01 wall CT/18:01ET).
  Exit03:00 close submits the03:01-labeled bar's open, about03:00 wall CT/04:00ET. Do not add another minute to label translation.
- Line53's half-cash-range protective stop is active on the entry bar. Worse stop gaps fill at the open. No target/stop path conflict exists.
- Line55 uses `>=03:00` through08:30, so missing the exact03:00 bar can be caught by the first later bar.
  Line57's fallback starts at08:31 and submits another next-bar exit. It can therefore already hold into the next cash session.
- There is **no explicit16:45ET or Friday/weekend liquidation guard**. Claims of always meeting those limits need actual exception counts.
  A delayed next-available-bar instruction is not an invented punctual liquidation.
- Ordinary17→03 midnight crossing is within a17→16 CME/account day under the adopted current-plan convention.
  Test crossings of the next flat/maintenance checkpoint, not calendar-date changes alone. This convention does not verify broker permission.

## Engine review

Read-through agrees with the planned close-time state sequence: cash ranges update at the source15:00 close, new orders act on the
next available native open, and only post-entry prices contribute to MAE. Quantity is separate from unit P&L and MAE.
The engine retains the ET calendar date and exposes late/safety/open positions and missing held minutes.
Simultaneous pending market exit and gap-stop opens have the same price; the helper keeps the market label. Native MC labeling is unverified.

The parent's synthetic suite passes. Independent additional fixtures verify:

- A down Friday waits until Sunday; Sunday2 doubles quantity without doubling the unit P&L field.
- An earlier pre-entry low is excluded; a normal evening-to-morning trade crosses dates without crossing the next15:59 checkpoint.
- A short null with nominal stop107 pays a worse next open110, with adverse excursion matching its actual entry101.
- A true late next-day exit is flagged; an unresolved terminal null retains its explicit signal ID instead of disappearing as zero P&L.

No material causal blocker was found. This review uses the parent's helper and synthetic arrays; it does not rebuild966 trades,
verify923 shared days/correlation, inspect return results, certify costs/account baselines, or replace an independent raw-data checker.

## Primary literature and scope

1. **Liu et al.** The [current SSRN abstract](https://ssrn.com/abstract=2730304), revised2025, describes buying cross-sectional
   overnight losers for subsequent intraday reversal. That is a different signal/holding direction from NQ cash losses→overnight long.
   The original2016 full text was not independently verified; the current primary abstract was visible in the public search index.
2. **Abdi2018.** The [university paper](https://ux-tauri.unisg.ch/RePEc/usg/sfwpfi/WPF-1829.pdf) studies common-stock quote midpoints:
   an overnight market decline, further intraday declines in volatile stocks, then another overnight reversal. Related liquidity mechanism,
   not a direct test of this NQ down-cash-day rule. Abstract/intro verified, not a full empirical-paper audit.
3. **Bondarenko–Muravyev.** The [publisher abstract](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/market-return-around-the-clock-a-puzzle/089E33AC0B4D3B9A02CBA31EDF6505B3)
   documents historical unconditional European-open concentration in ES futures. It does not validate this NQ filter, half-range stop or Sunday size.
4. **Boyarchenko–Larsen–Whelan.** The [NY Fed paper](https://www.newyorkfed.org/research/staff_reports/sr917.html) offers a relevant
   inventory-pressure/asymmetric selloff-reversal hypothesis. The cited mechanism is not itself verification of the submitted parameter set.
5. **Cliff–Cooper–Gulen2008.** The [primary indexed abstract](https://ssrn.com/abstract=1004081) documents broad historical overnight
   equity premium across stocks/indexes/futures. It does not establish profitability of the modern conditional18–04 strategy.

Direct SSRN opens returned403; no access bypass was attempted. Primary indexed abstracts, the publisher page and university/Fed sources
were used with the access limits above; no secondary retail-strategy commentary supplies the empirical claims here.

## Material current update

The same NY Fed authors' [July1,2026 follow-up](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/)
reports that the02:00–03:00ET premium flattened during2021–25, including NQ/YM, with weaker closing-imbalance predictability.
This cautions against carrying the older timing story forward unchanged. It does not alone refute a down-day18:00–04:00NQ strategy:
that conditions differently and includes other hours. Attribution and recent controls are needed before claiming the cited mechanism.

## Prior repository context

The older Overnight Drift backup had weak incremental funded evidence; part of its return was general overnight long exposure.
Liu's cross-sectional overnight→intraday family is also already ranked and failed a clean synchronized-clock test here.
Neither is an exact duplicate of this upload. Compare all-night totals, removed up/flat nights and random dropping before crediting
the down-day filter; a higher filtered PF alone is insufficient. The reported336-model search and other rejected filters remain prior trials.
