# Expiring index-option hedge unwinding: NEEDS DATA

Summary: A lawful public full-text copy is available, and the paper contains a specific ES pressure hypothesis.
Owned exports cannot reconstruct its signed SPX market-maker book; gamma, OI and NQ tape delta do not supply it.
Minute labels, delivery delay, starting positions and overnight coverage must be resolved before a tradable test.
Deeper data feasibility is warranted; this review ran zero return tests and selects no eligible family for testing.

Source: Diego Amaya, Pedro A. Garcia-Ares, Neil D. Pearson and Aurelio Vasquez, *The Price Impact of Hedging Expiring Index Options*, August 13, 2026. [SSRN 7330098](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7330098), DOI `10.2139/ssrn.7330098`; SSRN advertises a last revision of August 22, 2026.

Access: [public PDF linked by Algoseek's research page](https://algoseek.com/wp-content/uploads/2026/10/ssrn-7330098.pdf), 76 PDF pages. Reviewed the full-text directional analysis, position construction, key tables and appendix placebos through the connected PDF reader. The author [paper page](https://pedrogares.wordpress.com/2026/08/28/the-price-impact-of-hedging-expiring-index-options-2026/) links back to SSRN. No manuscript bytes were downloaded locally: the first shell request failed to connect to the configured proxy; a network-enabled request through that proxy returned HTTP403 and stopped. **PDF SHA256: unavailable**, not a fabricated hash or an assertion that the manuscript is frozen. A locally retained, hashed source remains necessary before TEST admission. [Access and inventory receipt](../research/scout/runs/7330098_testability_20261029.json).

## 1. What is it about?

Cash-settled SPXW expiration removes option delta while leaving its hedge outstanding. The study separates unwinding that hedge from gamma-driven rebalancing. See Section 2.1, printed pp.6–7.

## 2. What does it find?

The authors report July 2020–June 2023 ES returns differing by about **17 bp** between extreme dealer-delta quintiles over the final 30 minutes; the final-15-minute difference is **12.5 bp**. These are retrospective gross group differences, not verified tradable profits. See Section 4.2/Figure 5, printed pp.18–19; Appendix Figure IAB2.

## 3. Why does it make money, if it does?

Positive expiring-option dealer delta implies a short hedge whose liquidation buys futures; negative delta implies selling. Receiving that information before the pressure is the proposed opportunity. Profit after latency and costs is unverified.

## 4. Can we build on it?

**Yes, conditionally; NEEDS DATA today.** There is a concrete deadline, observable economic sign in principle, direct ES transmission and published directional evidence. Those merits justify retaining the lead. They do not justify replacing the missing book with an OI sign assumption or opening a return trial. No account placement, allocation or MultiCharts implementation is supported.

The source estimates each series' dealer position by accumulating signed market-maker trades from series inception, then multiplying by option delta and the 100 multiplier. Its observations are labeled by minute **start**, with end-of-minute quotes. See Sections 3.3–3.4, printed pp.13–15.

## Exact hypothesis versus a test we can actually run

For an independently reconstructed signed book, define `q_j` as dealer contracts in PM-expiring series `j` and `delta_j` as its contemporaneous option delta. Dollar sensitivity per index point is `D = 100 × sum(q_j × delta_j)`. An ES hedge is approximately `−D / 50` contracts; fully removing it creates an estimated demand of `+D / 50`. This is dimensional accounting, not evidence that dealers actually hold or unwind precisely that ES position. Cross-product netting, discretion and an existing hedge book can change actual orders.

The paper's observation clocks are 15:30/15:45 ET and settlement 16:00 ET, corresponding to 14:30/14:45/15:00 CT. **Do not fill at 14:30 CT with a feature that uses the minute ending 14:31.** The source's labeling and its return-window convention require reconciliation with raw timestamps. Even after that, `available_at` must include feed publication/receipt and processing, with first fill strictly after the decision. This is an availability warning, not an independently proven error in the authors' estimation.

A future tradable adaptation would freeze one received-book observation, its permissible age and first fill; decide long/short from its sign or a design-only threshold; and liquidate by the specified expiration deadline. It must specify early closes, actual historical PM expiry listings, stale/missing quotes, corrections, contract rolls, stops or explicitly unprotected risk, and a priced market exit. Today's daily-expiration calendar cannot be imposed on earlier years. No such executable rule or threshold is preregistered here.

## Owned-data audit: inspected, without computing returns

The configured `/workspace/venvs/thebeginning/bin/python` inspected headers and selected file boundaries. Hashes and counts are in the receipt.
[Reproduction script](../../../analysis/codex_scout_7330098_input_inventory.py) ·
[Saved inventory](../../../analysis/outputs/codex_scout_7330098_input_inventory.json).

| Owned material | What is present | Why it does not provide the source signal |
|---|---|---|
| `data/GEX_1min_*.csv`, 5 files | NDX gamma flip, steepness, centroid, gamma levels, basis, spot, DTE and a few NQ tape/depth fields | No SPX option series positions, signed MM capacity or contract deltas |
| `data/GEXOI_*.csv`, 5 files | NDX strike-level gamma and call/put OI | Unsigned prior-close OI does not identify dealers' positions or aggregate delta |
| `data/OF_1min_*.csv`, 35 files | NQ futures aggressor flow, depth, VWAP and profiles | Futures buying/selling does not identify SPX dealers, their option book or tomorrow's unwinding obligation |
| `data/ES_1min_*.csv` | ES OHLCV history | Outcomes exist, but the explanatory feature and executable spread/receipt evidence do not |
| Prior SPX sample study | Committed script and saved results for 127 days in 2022 | Its expected `scratch_data/options_sample/` directory is absent here; its documented fields were OI/gamma, not signed dealer positions |

The exporter documentation identifies NDX rather than SPX, timestamps in Eastern time, OI as prior-close information and gamma's valid cumulative-history start as 2023-03-28. The selected boundary check found gamma rows beginning 2022-09-01 and ending 2026-07-07; earlier rows are not proof of valid cumulative gamma history. These limitations cannot be fixed by renaming NDX to SPX or by converting futures aggressor delta into option delta.

## Actual public acquisition attempts and a possible data route

The [Cboe Open-Close product page](https://datashop.cboe.com/cboe-options-open-close-volume-summary) advertises C1 one-minute history from 2019-10-07 and ten-minute history from 2011-01-03. Ten-minute files arrive minutes after interval end. The [10-minute specification v1.6](https://datashop.cboe.com/documents/Open_Close_10m_Spec_v1.6.pdf) supplies `mm_buy_vol`/`mm_sell_vol`, with snapshots cumulative through the day; use contract volume rather than trade counts, and do not sum cumulative snapshots. GTH intraday coverage starts December 11, 2023. The [one-minute specification v1.5](https://datashop.cboe.com/documents/Open_Close_1m_Spec_v1.5.pdf) warns about delayed processing and uncorrected broken/canceled trades in that version. Future announced format changes must not be backdated.

In principle, prior daily MM net flows from a verified series inception plus the latest received intraday cumulative net flow could form a book estimate. **Today's flow alone is not the starting inventory.** This route still needs proof of complete sessions, corrections and historical availability; the missing pre-December-2023 GTH snapshots are a specific reconciliation problem for the original sample. A product label is not proof of source parity or a realizable receipt lag.

[Cboe TBT](https://datashop.cboe.com/enhanced-us-options-trade-by-trade-execution-detail) contains capacity and side but is delivered **T+1**. It can aid reconstruction/audit; it cannot silently become today's live forecast. The public Open-Close and TBT sample download links were actually opened; both were rejected by the connected reader as unsupported ZIP content. A network-enabled shell request through the configured proxy for the Open-Close sample returned HTTP403; it was not bypassed or retried. No sample data or complete historical panel was obtained. Exact-ID/title searches found no author-linked public replication code or signed-position panel. The Algoseek listing offers option quotes/minute bars; that does not establish access to the separate proprietary signed Cboe positions.

No account, purchase, paid trial, new API key or author contact was initiated. Source text was treated as evidence, not instructions.

## Existing negatives and overlap remain relevant

Do not recycle the rejected OI/gamma families in [TIER_LIST](../../../TIER_LIST.md): NDX OI/max-pain/pinning trades returned approximately −$111 to +$30 per trade without a robust matched-placebo pass; the gamma flip breakout returned −$79 per trade. The prior [SPX sample output](../../../analysis/outputs/spx_gex_sample_test_output.txt) found no directional feature with absolute t above 1.7, and naive GEX's volatility contribution disappeared after VIX. These are archived findings inspected here, not fresh reruns.

Signed dealer **delta** would be a materially different information input, so those failures do not directly test it. Conversely, aggregate gamma, unsigned OI or a max-pain level do not become a replication merely because both studies mention expiration. The existing [flow evidence sheet D](flow_evidence_sheets.md) proposes time-decay hedging of observed intraday position changes over 14:32–14:49 CT. This paper's terminal hedge removal concerns the level of the expiring book. Merge their data-acquisition work while preserving that economic distinction and all earlier negatives. Likely overlap homes are ES MOC and Late-Day Flow; addition/replacement tests remain unrun.

## Costs, next check and disposition

The existing [flow cost inventory](../../../analysis/outputs/codex_flow_evidence_sheets/cost_hurdles.csv) records **$30 per full ES round trip**: $5 commission plus two one-tick adverse fills at $12.50 each. Its preliminary gross hurdle is $45/ES (0.9 points). This is an existing research convention, not a verified current MES fee or a tested profitability result. A later screen must reconcile native MES commission/spread/latency separately; dividing a full-ES commission by ten is not adequate. A retrospective high-minus-low group difference is not a per-trade net expectancy.

The smallest next check is a **no-return** source/data intake: retain and hash the public PDF; obtain a lawful sample of C1 MM-capacity records and its historical publication convention; reconstruct one expiring series from inception through a decision; reconcile prior position, overnight trades, cumulative snapshots and corrections; then check actual quote receipt and a feasible fill. Stop if sign/availability cannot be established. Only after a complete design-era input census and an evidence sheet marked TEST should one bounded family enter committed preregistration and the cheap gross-versus-cost screen. No threshold/window rescue is authorized by this review.

**Decision: NEEDS DATA; deeper feasibility warranted, immediate return testing not eligible.** Zero new economic definitions, return tests, account simulations or plan changes. The parent task may retain this specific lead in the verification queue and its timing/position-accounting lesson in the execution-reference library; this delegated task changes only this report and its receipt.

For Claude: `agents/codex/results/scout_7330098_testability_20261029.md`.
