# dot: SSRN continuation, pass 3
Author: dot. Date: 2026-11-10. Branch: codex/work. Research only.

## Summary
One new conditional commodity-positioning lead survives the source screen, but not costs/data/holdout gates.
The expiration paper supports an existing strategy family, not a distinct new portfolio slot.
Two full-paper risk-overlay audits qualify the original volatility-management shortlist.
No return tests, strategy changes, data purchases or live actions were performed.

## 24. A Tale of Two Premiums: The Role of Hedgers and Speculators in Commodity Futures Markets
Kang, Rouwenhorst and Tang. [SSRN 2449315](https://ssrn.com/abstract=2449315), related listing 3374982.
[Full August 2018 manuscript](https://www.carloalberto.org/wp-content/uploads/2018/11/Liquidityprovision-Luxembourg2.pdf), section 3.3 and Table 4.

**Source evidence:** Across 26 commodities during 1994–2017, rank weekly changes in commercial net positions normalized by open interest. Equal-weight extreme quintiles buy the largest commercial purchases and sell the largest sales. The mechanism separates short-horizon liquidity provision from slower hedging demand. The paper explicitly distinguishes returns before the Tuesday-position report is released from later returns. The top-minus-bottom gross return is 29 basis points over post-ranking trading days 5–10 (t=3.73) and 19 over days 11–20 (t=1.68). The earlier 24 basis points are unavailable to an investor trading only after publication. Conditioning on high 52-week-smoothed hedging pressure gives a 49-basis-point days 5–20 spread (t=3.97). Prices come from Pinnacle; COT provides positions. A complete net-cost strategy and untouched holdout are not established.

**dot decision:** Personal: conditional, potentially complementary to price-only trend. Intraday/Apex: no, holding is multiweek. Existing data: not verified; a partial gold archive does not establish the required commodity cross-section.
The implementable design must wait for the actual report release and the next attainable fill. Do not use a Tuesday snapshot timestamp as Tuesday information. Normalize overlapping weekly cohorts into one capital-constrained portfolio and reconcile offsetting positions. Freeze the paper-defined signal rather than optimizing a gold-only crowding threshold. Check COT category consistency, revisions, public-release timestamps, 52-week warmup, matched contracts, market breadth and realistic two-sided costs. Public COT access does not confer rights to the futures history.

This is distinct from the separately reported failed gold crowding feasibility screen, not permission to repeat or reopen it. Existing raw-COT and equity-index positioning failures remain relevant counterevidence.

**Counterevidence:** [A Tale of Two Premiums Revisited, SSRN 3881922](https://ssrn.com/abstract=3881922), [2021 conference manuscript](https://acfr.aut.ac.nz/__data/assets/pdf_file/0006/530781/P3.pdf), extends the analysis through 2020. Commercial short-term net trading remains predictive after controls, but the slow insurance premium weakens after 2004. Its Tuesday-to-Tuesday factors do not prove post-publication tradability. Retain this as a paired audit, not another strategy slot.

**Current release-process risk:** [CFTC October 27, 2026 announcement](https://www.cftc.gov/PressRoom/PressReleases/9316-26) plans twice-weekly COT publication by year-end: Monday positions on Wednesday and Wednesday positions on Friday, at 15:30 Eastern. This is a planned change, not confirmation it is already operational. Any future study must preserve historical publication schedules and separately verify the effective change date.

## 25. The Third Friday Price Spike
[SSRN 4562800](https://ssrn.com/abstract=4562800).
[Full author manuscript, August 2026](https://julianterstegge.com/assets/papers/third_friday_price_spike.pdf), pages 7–10 and Tables I/A.4.

**Source evidence:** ES five-minute trade VWAP observations during 2003–2023 show an expiration-morning rise of roughly 12 basis points, reversing by noon. Expiration follows the third Friday with holiday adjustment, and the active futures maturity changes when the next contract becomes more liquid. The strategy illustration buys from the previous close to the Special Opening Quotation and shorts from that quotation to the expiration-day close. SPX intraday mean return is -15.10 basis points (t=-3.57). The paper relates the pattern to option-dealer delta exposure near expiration. Three crisis expirations are excluded in the main analysis, with inclusion robustness reported. It does not establish a frozen, net-cost, executable futures strategy.

**dot decision:** Existing-family support, not a fresh independent strategy. Personal: the full illustrated round trip includes overnight exposure. Intraday: the short leg suggests a separately specified same-day adaptation. Existing data: coarse NQ/ES timing adaptation may be possible, but exact trade VWAP, contract selection and SOQ fills are not verified.
SOQ is not an executable ES trade price. Do not book that fill or fabricate dealer exposures from OHLCV. The current codex/work file agents/tasks/TASK_06_EXPIRATION_OPEN_SHORT.md already specifies monthly expiry NQ shorts after the 08:30 Central bar, a 0.30 ATR stop and a 10:00 exit. A longer hold would be a new modification, not a replication or new discovery.

**Mechanism risk verified:** [Cboe notice C 2025092500](https://www.cboe.com/notices/content/?id=56357) postponed the proposed extension of expiring AM-settled SPX option trading to 09:25 Eastern, leaving the effective date undetermined and requiring another notice. Do not label September 2025 an implemented structural break based on the superseded plan. Recheck the actual effective date before any future implementation.

## 26. On the Performance of Volatility-Managed Portfolios
Cederburg, O'Doherty, Wang and Yan. [SSRN 3357038](https://ssrn.com/abstract=3357038).
[Full published JFE paper](https://www.lehigh.edu/~xuy219/research/COWY.pdf), equations 3–4, 15–16 and Tables 2, 6–7.

**Source evidence:** The monthly baseline exposure is a constant divided by previous-month realized variance, not inverse standard deviation. Across 103 equity strategies, direct scaling raises Sharpe in 53 cases, only eight significantly, concentrated in momentum. A constant full-sample normalization does not itself affect Sharpe. Positive spanning alpha instead concerns an ex-post combination of managed and unmanaged portfolios. The real-time comparison estimates normalization, moments and combination weights using an expanding window starting with 120 months, risk aversion five and absolute exposure capped at five. Certainty-equivalent return falls in 72 of 103 cases. The authors attribute poor results to instability. Inputs include factor returns and CRSP/Compustat/IBES data ending December 2016. This is not primarily a transaction-cost analysis.

**dot decision:** Counterevidence and method guardrail, not alpha candidate. Personal: risk-control research only. Intraday: not an intraday entry mechanism. Existing data: current futures bars do not replicate equity factors.
This qualifies original shortlist paper 10. Do not infer that all volatility targeting fails, but do not describe it as a demonstrated return enhancer. Real account survival needs drawdown, margin and loss-limit analysis. Inverse variance can aggressively increase exposure in quiet periods, and lagged volatility cannot preclude a jump. Any later authorized futures study must freeze leverage caps, lagged scaling, integer contract sizing and costs, then compare with simpler constant-risk exposure.

## 27. A Multifactor Perspective on Volatility-Managed Portfolios
DeMiguel, Martín-Utrera and Uppal. [SSRN 3982504](https://ssrn.com/abstract=3982504).
[Full 2024 Journal of Finance paper](https://lbsresearch.london.edu/id/eprint/3716/1/The%20Journal%20of%20Finance%20-%202024%20-%20DeMIGUEL%20-%20A%20Multifactor%20Perspective%20on%20Volatility%E2%80%90Managed%20Portfolios.pdf), equations 3, 6, 10–12; Tables II–III.

**Source evidence:** Monthly factor weights are a nonnegative constant plus a nonnegative coefficient divided by market volatility, measured using previous-month daily returns. Coefficients maximize mean-variance utility after modeled trading costs. Nine equity factors use expanding estimation initialized over 1967–1976 and reported OOS performance during 1977–2020. Net Sharpe is 1.062 versus 0.940 for an unconditional portfolio, one-sided bootstrap p=0.006. Crucially, stock-level trades are netted across factors before applying estimated half-spreads; removing netting eliminates the OOS net advantage. Price impact and leverage restrictions are examined. Replication requires stock-level holdings and CRSP/Compustat. The replication package warns some data contain protective noise, so exact table reproduction is not guaranteed.

**dot decision:** Evidence for cost-aware portfolio construction, not a plug-in volatility rule. Personal: conditional method, not immediate strategy. Intraday: no. Existing-data replication: no. A portfolio of a few futures strategies cannot assume the same constituent-level netting advantage. This does not restore a universal claim that scalar volatility targeting improves returns.

[Replication package, version 3](https://data.mendeley.com/datasets/dmjfztbc4y/3) supplies MATLAB code. Access to code or noise-protected data is not a license to the underlying proprietary stock datasets.

## Other source and duplication decisions
- Cross-Market Intraday Time-Series Momentum: SSRN 4978089, aliases 4765613/4651331. Full source unavailable; later published title and authors differ. Index/ETF evidence must not be labeled a futures replication.
- SSRN 3493927, Chinese intraday momentum: accessible full manuscript explicitly excludes costs and predates night trading; no strong new US-futures candidate.
- SSRN 3225611, commodity forecasting: reported net/OOS portfolio is overwhelmingly Treasury exposure. Do not attribute portfolio success to an implementable commodity alpha without decomposition.
- SSRN 4778937, Improving Volatility-Managed Portfolios in Real Time: full source not recovered; headline evidence not promoted.

The search remains research-only. Conditional leads, corroborating papers and rejected sources are deliberately distinguished rather than padded into a list of approved strategies.
