# Turning spread research into a strategy: specific lead, NEEDS DATA

Summary: Pursued a predictive trading rule after the user's clarification, not just execution analysis.
Weekly basis reversal is a concrete verification lead, but primary text and identified paired-maturity data are missing.
Recovered the soft-commodity flow paper; contemporaneous regressions do not establish a ready forecasting rule.
No return tests or account runs occurred; scout economic counters remain unchanged.

## Weekly basis reversal — a concrete rule to verify

[SSRN5250499](https://ssrn.com/abstract=5250499), Rossi, Zhang and Zhu, written May11 2025, advertises a May12 2026 revision with68 pages. [Zhu's author page](https://yandi-zhu.github.io/) confirms the primary abstract. SSRN returned403. [Rossi's page](https://sites.google.com/site/albertorossifrb) links an [author PDF viewer](https://drive.google.com/file/d/1CrIcmR0FWnStqYQTDRVIg0sPUV8eek6e/view?usp=sharing) that yielded loading/sign-in text, not paper pages. No login or download bypass attempted. **Full text not read; metadata plus secondary-code inspection only.**

1. **About:** Reversal of the prior week's return difference between adjacent commodity maturities.
2. **Findings:** Authors claim negative autocorrelation distinct from outright-contract reversal and consistent with differential information sensitivity along the curve. No primary table or net strategy result independently reproduced here.
3. **Why money:** A proposed relative-value opportunity from uneven information absorption and limited arbitrage capital; no verified forced order. Trading/funding costs can absorb it.
4. **Build on it:** Yes, for source/data verification. The specific weekly spread rule below merits the TODO queue, but its primary details and current net/account value remain unverified. Weekly holding is not eligible for Apex as described; personal research is the first possible home. No intraday adaptation selected.

### Provisional rule, not a preregistration

Define `b(t) = return(front, week t) - return(deferred, week t)` on identified, consistently mapped contracts. The inspected third-party time-series spread implementation goes short front/long deferred when `b(t)>0`, and reverses that direction when negative, through the next weekly rebalance. It delays execution one day after observing the signal and uses a pre-expiry roll convention. These are secondary implementation choices, not certified exact primary-paper rules.

The [public notebook](https://github.com/rolling-panda-san/notebooks/blob/ce05661a5d4b3cdb439ece27dcccba88e2cb130a/commodity_basis_reversal.ipynb) was inspected without execution at commit `ce05661a5d4b3cdb439ece27dcccba88e2cb130a`; byte SHA256 `b2c2ae82e7a3b2d39ee5d3ac415d22e73c17d428f872d5dbf7e43543e3a3ca5f`. It imports `vivace` engine/data/signal objects not defined in the inspected file. Saved curves use `calculate_net=False`; no underlying raw panel was acquired. No external code, model import or return engine was executed.

A percentage-return spread can imply equal-dollar rather than equal-contract exposure. A single integer calendar spread has different risks. Resolve that mapping, settlement availability, roll/FND dates, both-leg commissions and entry/exit costs, margin/funding and executable prices before a test. A cross-sectional ranking is a separate economic definition, not a free control.

## Recovered full soft-commodity flow source

[SOAS July2018 working paper211](https://www.soas.ac.uk/sites/default/files/2022-10/economics-wp211.pdf), van Huellen,19 PDF pages, is now readable. This working version is not asserted to match the accepted2020 article or SSRN3357455 revision. An accepted-manuscript endpoint returned502 and a repository-file endpoint403. Reviewed model, factor methods, data, tables, endogeneity discussion and conclusion through the connected reader; no original PDF bytes/hash acquired.

1. **About:** Index demand relative to hedger positions and cocoa, coffee and cotton futures-curve shapes.
2. **Findings:** The author reports offsetting position/curve associations using monthly data, with contemporaneous terms and possible endogeneity (printed pp.13–14). Key cotton index-pressure estimates are weak/insignificant. These are author regressions, not independently verified trading returns.
3. **Why money:** Excess index demand could distort relative maturities, but measured contemporaneous associations do not establish a forecast available before trading.
4. **Build on it:** Retain the relative-demand hypothesis as context. Do not trade a contemporaneous coefficient or use month-end factors before publication. No source-supported profitable protocol/exit recovered: DON'T TEST a naive transcription.

## Data effort, account fit and decision

Refetched remote first; E30 and earlier acquisition failures were reviewed. The runtime still reports enforced restricted networking with no added research-host allowlist. Previously denied samples were not retried unchanged. New searches covered synchronized soybean spread/leg books, raw-data availability and independent basis implementations. The official CME listing offers soybean-spread and corn-outright examples; it does not establish a matched soybean-leg dataset. Archive contents could not be certified.

Earlier free routes remain partial: a one-day sample cannot establish2018–22 power; the secondary modern spread corpus starts2021 and its deep archive ends2004. Daily spreads cannot supply execution books. The public notebook supplies source text, not its private data service. No purchases, accounts, new keys or external requests.

The [no-return input audit](../../../analysis/codex_spread_strategy_inputs_20261029.py) reads filenames and headers only, including the owned legacy/financial COT schemas. Named2018 one-minute exports lack contract-identifier and bid/ask fields. The two inspected COT archive schemas have no index-trader fields and cannot substitute for the Commodity Index Supplement. This is not a claim about every possible local alias. No market rows were read for outcome selection.

| Proposed research | Evaluation50K/150K | Funded50K/150K | Personal |
|---|---|---|---|
| Weekly basis reversal as described by secondary implementation | Ineligible as-is: weekly overnight holding | Ineligible as-is: weekly overnight holding | Potential research fit; full source, paired history, integer sizing and costs unresolved |
| Direct trade from contemporaneous soft-commodity curve regressions | No executable protocol established | No executable protocol established | No executable protocol established |
| Listed-spread execution improvement | Supporting method only | Supporting method only | Supporting method only |

[Evidence sheet](../evidence/scout_basis_reversal_20261029.md): **NEEDS DATA**, not TEST. No lease/reservation/preregistration or admission PASS claimed. Gross screen, historical validation, placebos, Monte Carlo and BASE/ADD/REPLACE/EMPTY comparisons remain unrun. No imputed maturities or fills. Existing failed CL roll searches and old livestock decay remain negative evidence, not reopened variants.

For Claude: this report and its evidence sheet; the new queue item is an unverified market hypothesis, not an allocation.
