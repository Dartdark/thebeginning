# dot: seasonal-model and recent-source screen
Author: dot. 2026-11-10. Research-only screening addendum; no new strategy promotion or return tests.

## 1. SSRN 2869969: different method, missing inputs
[Portfolio Optimization of Commodity Futures with Seasonal Components and Higher Moments](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2869969). Reviewed [author-hosted January 2017 thesis chapter, printed pp 63–77](https://bjerring.github.io/assets/media/Phd_Thesis.pdf), not byte-verified November 2016 SSRN.

Monthly Bloomberg continuous futures for ten commodities plus French's broad US equity portfolio. AR(p) lag length uses AIC with 12-lag cap, re-estimated monthly on 120 months. Joint residual-vector resampling preserves cross-asset dependence; long-only portfolios maximize Omega or Sharpe. OOS January 1985–December 2014 has 360 months. Omega version reports Sharpe .82, drawdown 36.08% and average monthly turnover 64.39%. Costs rely on discussion of a borrowed 13 bp estimate, not contract-specific net execution; continuous-roll construction is incomplete.

**Assessment:** Honest rolling design but old evidence, substantial turnover, and no postpublication validation. This is AR allocation rather than a clean calendar anomaly. Personal only. No exact repository match for ID/sieve/Omega in search or codex/work MINED_INDEX. Direct data-directory review finds only GC overlapping its ten commodity markets; other nine absent. HANDOFF reports GC/CL beginning November 2017 with unadjusted rolls, insufficient for 120 months training plus OOS. Existing CL/NQ/GC substitution would be a different hypothesis. Not current-data-qualified.

## 2. SSRN 4575549: version-sensitive caution
[Return Seasonality in Commodity Futures](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4575549), [published 2024 source](https://www.sciencedirect.com/science/article/pii/S1059056024002934). Full methods remain inaccessible; available publisher introduction is stronger than abstract-only but insufficient for coding.

It reports replication of same-month returns at 1.02% monthly for 1975–2011, dominated by 1990–1999; 2004–2023 reports .95% with t 1.52. Removing 1990–1999 removes significance. The 2023 SSRN abstract says seasonal additions weaken momentum; 2024 published abstract instead reports significant combined momentum/reversal/seasonality returns and extends through October 2023.

**Assessment:** Do not merge inconsistent version claims. Use only as qualified evidence that calendar effects can be regime-dependent. Exact costs, training and rolls unaudited; not a new implementation slot.

## 3. arXiv 2609.12227: reproducibility does not remove timing risk
[Seasonal Trading in Commodity Futures](https://arxiv.org/pdf/2609.12227), [public repository](https://github.com/RPKosch/Seasonal-Trading-in-Commodity-Markets-Preprint-Version). No SSRN counterpart located.

Fifteen commodities, rolling 120 months, 2016–2024 OOS; dummy regression, SSA and robust SSA, classic/vol-normalized. One contract per direction; regression requires correct beta sign and Newey–West p ≤ .10 or cash. SSA selects even with forecast signs opposing direction. Costs 8.6 bp each side omit financing/margins/contract-specific impact. Regression-long Sharpe .245 versus benchmark .183; SSA long loses. None of 18 paired bootstrap Sharpe comparisons survives within-family Holm correction. Bootstrap keeps observed temporal ranks without explicitly preserving cross-contract dependence.

**Independent read-only code finding:** [Builder lines 105–120](https://github.com/RPKosch/Seasonal-Trading-in-Commodity-Markets-Preprint-Version/blob/main/Data%20Analysis/Helper%20Function/Compute_Monthly_Returns.py#L105-L120) checks future price coverage and the traded month's full average volume before selection at line 157. Those facts are unavailable at month-start. A pre 2016 universe screen does not fix that separate eligibility issue. Numerical impact was not tested; do not claim all results invalid. Software licensing does not grant underlying market-data rights.

## Practical implication
No new strategy here clears both evidence and existing-data gates. Public code is valuable for audit, not proof of causal execution or licensed data ownership. These sources do not justify reopening failed seasonality experiments or promoting an intraday adaptation.

## Latest commodity papers held at the source gate
- **Extrapolative Commodity Returns, SSRN [6745679](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6745679), Wang/Xu/Ye, May 2026, 83 pages.** Abstract describes holdings-based DOX and cross-sectional predictability attributed to gradual extrapolator unwinding. Exact formula, public aggregate versus restricted positioning inputs, release timing, costs and OOS are unverified. SSRN page/PDF returned 403; [author page](https://sites.google.com/view/zhewangzju/) links only SSRN, with no authenticated alternate full copy found. No exact ID/title match in bounded repository checks. Personal research watch only; no admitted holding horizon, intraday application or current-data fit. Incremental value beyond COT-flow 2449315 and speculative-pressure 3279425 remains unknown.
- **Correlation and Commodity Risk Premia, SSRN [7412084](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7412084) / [6247358](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6247358), Fan/Zhang.** Explicitly linked versions, not two papers: newest 58 pages posted September 4, 2026; earlier 56 pages revised August 14. Abstract says the correlation premium is largely spanned by market, hedging-pressure and skewness exposures. Full SSRN page/PDF returned 403; author/institution searches found no authenticated alternate manuscript, and [ResearchGate](https://www.researchgate.net/publication/401891614_Correlation_and_Commodity_Risk_Premia) lacks full text. Exact correlation, horizon, sorts, contract rules, costs and OOS remain unknown. Secondary 29-market/Sharpe claims are not admitted evidence. No exact title/ID match in current codex/work TIER_LIST, MINED_INDEX or DATA_NEEDED. Personal watch only; no intraday/current-data qualification. D08/D09 and the unrelated failed NQ correlation-risk-budget design do not establish novelty or invalidate this paper.

Neither source gate authorizes contacting authors, purchasing data, inventing a proxy or reopening old tests. No such action was taken. These unreviewed leads are not added to the 43-entry inventory.

## Economic momentum: related macro-FX reserve
**SSRN [2579666](https://ssrn.com/abstract=2579666), March 2019 / JFE 2020.** [Indexed manuscript](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/7f87a876-75db-4ec6-9d90-a7daa19e0a6c.pdf) excerpts, not a complete full-file audit.

Activity combines industrial production, retail sales and inverse unemployment; inflation combines CPI/PPI. Log trends over 1–60 months use three-month-lagged data. Monthly centered rank portfolios normalize each side to $1; sub-strategies use inverse past volatility. Developed-market spot/one-month forwards, 1976–March 2017. Combo Sharpe 0.705, reduced to about 0.64 in indexed cost discussion; older near-1 headline is a different version. Longer horizons contribute more strongly. Ranking may reduce sensitivity to revisions but does not establish vintage correctness.

**Assessment:** Growth/inflation trends differ from entry 41's relative output gap, but both require missing broad macro/forward inputs. Three-month delay alone does not remove revisions. Entry 41's actual vintage evidence remains preferable. Later studies overlap heavily and change weighting; the 2025 currency-basis-momentum comparator also has unresolved printed sign/cost equations documented in the validation audit. No clean modern validation claimed. Personal reserve only; no intraday/current-data qualification. Full original/appendix retrieval remains gated.

## Bitcoin versus gold allocation: later version changes the claim
**SSRN [4241996](https://ssrn.com/abstract=4241996), revisions [4606787](https://ssrn.com/abstract=4606787)/[4606789](https://ssrn.com/abstract=4606789).** [Published NAJEF 2024](https://doi.org/10.1016/j.najef.2024.102260).

Original 2022 abstract favors BTC in stock/bond minimum-volatility portfolios; 2023/2024 versions say it helps in dovish periods but destroys value during rapid rate hikes, when gold helps. Indexed text mentions DCC-GARCH/realized variants and daily rebalancing. Full source was not retrieved: exact sample, training/OOS, constraints, leverage, decision/fill timing, costs and performance tables are unverified.

**Assessment:** Portfolio allocation, not independent alpha. Intraday estimation data do not imply intraday-flat holdings. A retrospective monetary-regime split is not an established causal switching rule. No new qualified entry.

Actual BTC_1min_2018.csv inspection confirms first row December 17, 2018 at 02:29 and last December 31 at 15:59, with date/time/OHLC/volume and no expiry ID. Filename does not imply full-year coverage. GC2017/ZN2017/ES2018 reads returned metadata but empty content, so remained unread, not proven empty. Matching four tickers cannot establish synchronized covariance inputs or faithful replication. No tests were run.

## Further seasonal sources, not new qualified strategies
### Fixed-expiry energy seasonality
[SSRN3792028](https://ssrn.com/abstract=3792028), [complete February2021 author draft](https://www.researchgate.net/publication/349633507_Trading_Time_Seasonality_in_Commodity_Futures_An_Opportunity_for_Arbitrage_in_the_Natural_Gas_and_Crude_Oil_Markets): NG buy February F5–F36, sell June matching F1–F32; expanded panel reaches F60. WTI short July F6–F60, cover December matching expiries. Samples end July2020, start1997/2002/2006. Entry months chosen from full-sample patterns. Monthly-average descriptive prices; separate CAPM pairs every entry-month date with corresponding exit-month dates. Modeled costs NG$51.50/WTI$21.50 per contract per transaction; ample liquidity/margin assumed. Recursive CAPM is not rolling strategy selection.

Assessment: overlapping observations and maturities do not create hundreds of independent years. Approximately23/19/14 annual episodes;2008 important. Positive CAPM alpha is not arbitrage. [Final2022 record](https://eprints.gla.ac.uk/281581/) confirms publication, but final PDF unavailable in this pass. Draft parity, native fills, cluster inference, rights and modern holdout remain gates. Personal multimonth, not intraday.

### Seasonal ranking and trend costs
Baltas [SSRN2710334](https://ssrn.com/abstract=2710334), [full published source](https://www.revue-banque.fr/binrepository/0000000000000000000_RB00764_MG108084026.pdf), pp.47–62. Rank upcoming month's average commodity returns over prior ten years (minimum five); long/short quintiles.1992–February2015 Bloomberg generic continuous futures. Optional7% target uses trailing100-day volatility. Standalone raw Sharpe .49 gross/.34 modeled net; targeted .49/−.11. Costs turnover×25bp. Seasonal trend veto gives commodity targeted trend .85→.89 at10bp, but .77→.75 at25bp; paired improvement p=.0766. Causal histories do not establish untouched selection or native execution. Method/cost reference, not new independent trend alpha.

### Front-running seasonal patterns: explicit post-selection
[SSRN5048183](https://ssrn.com/abstract=5048183), [full author article](https://quantpedia.com/traders-guide-to-front-running-commodity-seasonality/). Four commodity ETFs,2007–June2024. Each takes±25% based on a chosen lag's return rank within its own12-month history. Lag12 loses4.54% annually; authors shift to lag11, reporting6.71% CAR/.55 Sharpe/−20.43% drawdown, then add a correlation filter. This narrative changes the rule after observing failure. No untouched net validation, native-futures equivalence or verified financing/borrow ledger. Anticipatory-trading explanation is conjectural.

### Original arXiv audit independently reconfirmed
The full traded-month volume/future-coverage eligibility gate remains noncausal for first-day orders; impact untested. None of18 paired comparisons survives Holm. Code/documentation GPL does not cover market-data redistribution. No code or strategy returns run here.
