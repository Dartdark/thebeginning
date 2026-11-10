# Ten SSRN papers worth building research around
Author: dot | 2026-11-10 | Source review only

## Decision summary
- Ten distinct papers, not ten independent strategies: nine full-paper methods/results reviews and one clearly marked source-verification gap.
- Start with Basis-Momentum and Relative Basis, conditional on a legally usable native-contract panel.
- Use diversified trend and value/carry as portfolio foundations; volatility management is a risk overlay, not new alpha.
- Prefer monthly research over daily curve trading for this account context; none is approved for live trading or a prop-account adaptation.
- No return tests, paid data, schedules, live systems, broker access, or changes to strategy rankings were performed.

This extends [the initial source screen](dot_ssrn_shortlist_20261110.md). Publication aliases are counted once. “Full paper reviewed” means relevant methods, evidence and implementation sections were inspected, not every sentence or an independent replication. All performance below is authors’ historical evidence, not our results or a forecast.

## 1. Basis-Momentum
Boons and Porras Prado. [SSRN 2587784](https://ssrn.com/abstract=2587784). [Full 2016 manuscript inspected](https://conference.nber.org/confer/2016/CEMf16/Boons_Prado.pdf); later Journal of Finance 2019 version parity is not fully verified.

**About / finds / why money:** Differences in momentum across nearby maturities may capture maturity-specific price pressure and risk compensation. The manuscript studies 21 commodities, with returns from 1960 through February 2014. Its monthly signal is trailing 12-month compounded first-nearby return minus second-nearby return. Equal-weight top-four minus bottom-four portfolios earn reported annualized 18.38% outright and 4.08% using calendar spreads, with t-statistics 6.73 and 6.43. A cost illustration assumes 4.4bp effective half-spread and 211.2bp yearly costs. Currency evidence is cross-universe validation, not prospective trading.

**Build:** Reconstruct both maturity return streams, rank monthly, hold the next month; implement outright and spread specifications separately. Source roll convention moves to the next contract at month-end when the current contract expires in t+2. Main universe: crude, gasoline, heating oil, rice, corn, oats, wheat, cotton, lumber, feeder/live cattle, lean hogs, gold, silver, copper, soybean oil/meal/beans, coffee, orange juice and cocoa.

**Can code?** Yes after data admission, not production-ready now. Need actual contract IDs, expiries, settlements and availability times, at least 12 months warmup, both-leg execution costs, integer lots, margin and collateral accounting. CRB/Futures Industry Institute history is not verified free or licensed here.

**Our decision:** Highest-priority conditional research lead. Same panel infrastructure as existing D06–D09, but not the same signal. Do not count it as a crash hedge or assume broad-paper returns transfer to CL alone. Personal overnight portfolio only until a separate prop-compatible design has evidence.

## 2. Relative Basis and the Expected Returns of Commodity Futures
Gu, Kang, Lou and Tang. [SSRN 3404561](https://ssrn.com/abstract=3404561). [Full July 2024 manuscript](https://personal.lse.ac.uk/loud/RelativeBasis.pdf), especially Sections 3–5 and portfolio tables.

**About / finds / why money:** Relative basis subtracts distant basis from near basis to reduce persistent storage/financing components and better identify temporary scarcity. It is the time-scaled first/second contract price difference minus the second/third difference. Monthly high-minus-low terciles across 24 commodities over 1979–2019 report 81bp/month (t=3.99), and 69bp alpha controlling commodity market, price momentum and basis-momentum. Relative basis does not similarly forecast financial futures, consistent with the inventory mechanism.

**Build:** Calculate both annualized basis segments using the source’s exact normalization, rank month-end, buy high and short low for the next month. Freeze inclusion and roll rules before any return test; verify formula and units against a hand-calculated three-contract example.

**Can code?** Conditional yes. Needs three simultaneous native maturities, expiry day counts, seasonality checks and quote/settlement availability. The signal itself does not require live inventory releases. Exact executable fill timing and contemporary net costs remain unverified.

**Our decision:** Second priority, potentially more distinct than another momentum variant. Distinct source does not establish independence from existing carry/basis risk. Exclude stale illiquid distant contracts and inspect sensitivity to seasonal delivery pairs. No verified recent post-publication holdout or accessible complete licensed panel.

## 3. An Anatomy of Commodity Futures Risk Premia
Szymanowska, de Roon, Nijman and van den Goorbergh. [SSRN 1343809](https://ssrn.com/abstract=1343809). Journal of Finance 2014. [Full manuscript inspected](https://a.storyblok.com/f/331657/x/52c4b117cd/szymanowska_de_roon_nijman_van_den_goorbergh.pdf), Section II and Tables I–III.

**About / finds / why money:** Separates commodity spot risk premiums from maturity/term premiums. CRB data cover 21 commodities, March 1986–December 2010. Observations and rebalancing are every two months, with approximately two-, four-, six- and eight-month maturities. Four portfolios are sorted on basis. Table II’s high-minus-low short-roll returns are negative under its basis sign convention: -8.29% to -14.53% annualized across maturities. That is not a contradiction of backwardation strategies using the opposite basis sign. The paper distinguishes outright return drivers from excess holding returns.

**Build:** First reproduce the source’s return decomposition and basis sign; then separately specify a backwardation long-short sleeve and maturity-spread sleeve. Do not substitute the front continuous contract. Source excludes prices during and one month before delivery and rolls earlier to avoid thin trading.

**Can code?** Yes as infrastructure/reference implementation once matched maturity data exist. Futures, maturity dates and two-leg cash flows required; no verified modern net cost or independent prospective evidence.

**Our decision:** Useful research foundation, not an additional independent “winner.” The most valuable contribution is preventing false diversification between outright carry and curve returns. Lower priority than #1/#2 for new strategy discovery.

## 4. The Fundamentals of Commodity Futures Returns
Gorton, Hayashi and Rouwenhorst. [SSRN 996930](https://ssrn.com/abstract=996930); 1000353 is an alias, not another paper. [Full January 2012 version](https://www.summerhavenindex.com/assets/fundamentals_of_commodity_futures_returns.pdf), Sections on portfolio sorts, Tables 6–9 and footnote 20. Published Review of Finance 2013.

**About / finds / why money:** Storage theory links scarce inventories to convenience yield and expected futures premiums. This version studies 31 commodities and inventories over 1971–2010; earlier drafts use different dates. Month-end raw-basis sorts split commodities into equal-weight top/bottom halves. Table 6 reports 10.64% annual high-minus-low return (t=3.92); trailing 12-month futures momentum reports 11.94% (t=4.40). High-basis and high-momentum portfolios are highly related. Importantly, the paper explicitly says its full-sample-demeaned basis diagnostic is not a feasible real-time strategy.

**Build:** Use raw basis as the executable baseline; inventory analysis requires publication-lagged, unrevised-as-known observations. Any rolling normalization is a new specification, not replication.

**Can code?** Price-only baseline conditional on native-contract data. Inventory version requires a much harder commodity-specific release archive, units and revision provenance. No verified net contemporary implementation.

**Our decision:** Already present in repository as commodity storage/momentum and rejected for NQ scope. Included transparently as a distinct strong foundation, NOT a new discovery or permission to reopen that rejection. Relevant to a broad personal commodity book, not an NQ intraday signal.

## 5. Exploiting Commodity Momentum Along the Futures Curves
de Groot, Karstanje and Zhou. [SSRN 2485314](https://ssrn.com/abstract=2485314). Journal of Banking & Finance 48 (2014), 79–93. [Institutional publication record](https://repub.eur.nl/pub/84083/) and [publisher record](https://www.sciencedirect.com/science/article/abs/pii/S0378426614002751).

**Evidence status: LIMITED.** Publication, mechanism and abstract are verified; accessible full-paper methods were not successfully obtained in this run. Do not represent this as a completed replication-ready review.

**About / finds / why money:** Contract maturity choice can improve a commodity momentum strategy by incorporating expected roll yield or maturity-specific momentum and reducing turnover. The institutional record reports more than twice the traditional strategy’s net return for a low-turnover alternative under the authors’ cost assumptions. This is a relative historical comparison, not a return forecast.

**Build:** The proposed research object is a maturity selector on top of an existing commodity momentum ranking, not another directional signal. Exact universe, ranking window, permitted maturities, holding/exit rule, sample and cost assumptions must be extracted from the full source before preregistration.

**Can code?** Not yet to source fidelity. Needs maturity-by-maturity prices, bid/ask or defensible execution assumptions, volume/open interest, delivery filters and a complete specification.

**Our decision:** Worth retaining among the ten substantive leads because turnover is economically important, but SOURCE BLOCKED for implementation. Does not count as a tenth verified strategy. Do not infer parameters from summaries or pay for access without permission.

## 6. Exploiting the Dynamics of Commodity Futures Curves
Bianchi, Fan, Miffre and Zhang. [SSRN 3749061](https://ssrn.com/abstract=3749061). [Full July 2023 manuscript](https://arxiv.org/pdf/2308.00383), Sections 2–3 and Table 5. Journal of Banking & Finance 154 (2023).

**About / finds / why money:** Tests short-horizon continuation in fitted curve movements. Daily Nelson–Siegel fits use the first four contracts; the slope-change signal trades a front-versus-fourth spread for the next day. The 21-commodity sample runs January 1992–June 2019. Reported slope-strategy gross Sharpe is 1.41, but Table 5 net Sharpe falls to 0.44–1.04 across three cost cases; net annual return is 0.55–1.31%. Daily turnover is 1.17. The paper explicitly cautions that low institutional execution costs matter. Butterfly results are less robust after costs.

**Build:** Positive daily slope change buys front/sells fourth; reverse for negative change, with source group weights and daily roll handling. Fit decay using only that day’s curve, not the full sample.

**Can code?** Signal yes, credible execution no until quote-level timing and costs are resolved. Same-settlement signal-and-fill is a potential availability issue: require an executable delayed fill or documented pre-cutoff inputs. Listed-spread economics cannot be assumed for legged retail orders.

**Our decision:** Lower priority than monthly curve ideas. Sequential one-day forecasts are not a fresh post-publication holdout. Personal overnight exposure remains even with daily holding periods. Cost and liquidity gate first; no butterfly build recommended.

## 7. Time Series Momentum
Moskowitz, Ooi and Pedersen. [SSRN 2089463](https://ssrn.com/abstract=2089463). [Full published paper](https://fairmodel.econ.yale.edu/ec439/mosk.pdf), Equations 1/5 and Table 3. Journal of Financial Economics 2012.

**About / finds / why money:** Persistent own-market trends may reflect slow information adjustment and hedging demand. Monthly positions follow each instrument’s trailing 12-month excess-return sign, scaled by ex-ante volatility; the paper uses exponentially weighted daily squared returns with 60-day center of mass. Across 58 equity-index, currency, commodity and bond futures/forwards during 1985–2009, all have positive estimates and 52 are significant at 5%. Aggregate monthly factor-adjusted alpha is 1.58% (t=7.99). Earlier 1966–1985 evidence is thinner. Late-2008 gains do not eliminate reversal losses.

**Build:** One frozen 12-month sign rule, source volatility estimator, monthly rebalancing, equal instrument allocations. The source’s 40% per-instrument normalization is NOT an account-volatility recommendation.

**Can code?** Yes conditional on native rolls, financing and execution costs. Published figures are not verified net retail outcomes. Need separate current holdout and integer-lot feasibility before any allocation.

**Our decision:** Strong diversified personal-account baseline, not novel relative to the repository’s existing trend/capital-expansion bench. Do not resurrect failed NQ trend adaptations or assume flat-by-15:59 truncation preserves the edge. Trend can diversify some crises but is vulnerable to abrupt reversals.

## 8. Value and Momentum Everywhere
Asness, Moskowitz and Pedersen. [SSRN 2174501](https://ssrn.com/abstract=2174501); 1363476 is an older version. [Full paper](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf), Sections I.B–D, V and Table I. Journal of Finance 2013.

**About / finds / why money:** Combines negatively related value and momentum exposures across eight markets/classes, with differing starting dates and ending July 2011. Momentum uses 12-month returns excluding the latest month. Value is asset-specific: commodity old/current spot price, FX purchasing-power changes, bond yield changes, equity book/market. A 50/50 combination has reported nonstock Sharpe 1.03 for tercile portfolios and 1.14 for signal-weighted portfolios. These are gross research portfolios, not directly executable account returns.

**Build:** Start with the non-equity specification. Month-end asset-class ranks and separate value/momentum sleeves; retain source normalization and weighting. Commodity historical spot averages use roughly 4.5–5.5 years back.

**Can code?** Conditional yes. Needs long warmup, point-in-time CPI/yields/spot, publication lags, native futures mapping, roll and trading costs. Using today's revised macro series would contaminate historical signals. Do not equate freely downloadable factor returns with tradable raw inputs.

**Our decision:** Value provides a more useful complementary hypothesis than adding another trend variant. Still overlaps #7 and commodity momentum. Monthly overnight book, not current intraday deployment; independent net holdout required.

## 9. Carry
Koijen, Moskowitz, Pedersen and Vrugt. [SSRN 2298565](https://ssrn.com/abstract=2298565); 2632697, 2362320 and 2311574 are version aliases. [Full accepted manuscript](https://research-api.cbs.dk/ws/portalfiles/portal/57294842/lasse_heje_pedersen_et_al_carry_acceptedmanuscript.pdf), Sections 2–3 and Equation 19. Journal of Financial Economics 2018.

**About / finds / why money:** Carry is return if market prices remain unchanged, measured ex ante. Monthly cross-sectional ranks produce long high-carry/short low-carry weights normalized to +1/-1. Relevant samples include 24 commodities from 1980, 20 FX forwards and ten government-bond markets from 1983, ending September 2012. Authors report average asset-class Sharpe around 0.8 and diversified carry Sharpe 1.2. Carry strategies share recession, liquidity and volatility exposures despite low unconditional correlations.

**Build:** Define carry correctly for each asset: commodity term structure, FX forward discount, bond financing plus roll-down. Start with one instrument family; cash-bond evidence is not automatically Treasury-futures evidence because of cheapest-to-deliver and financing effects.

**Can code?** Conditional yes, with matched quotes, funding curves, maturity details and costs. [Author factor data](https://www.koijen.net/code-and-data.html) include updates through July 2021; these are research benchmarks, not proof of executable source-data availability.

**Our decision:** Broad foundational comparator; commodities overlap #2–#4 and existing D08. A carry-heavy book can lose together exactly when account survival matters. Manuscript is CC BY-NC-ND; that does not license underlying market data.

## 10. Volatility-Managed Portfolios
Moreira and Muir. [SSRN 2659431](https://ssrn.com/abstract=2659431); 2773438 is a version alias. [Full published manuscript](https://amoreira2.github.io/alan-moreira.github.io/VolPortfolios_published.pdf), Tables I and IV. Journal of Finance 2017.

**About / finds / why money:** Monthly exposure scales inversely with the preceding month’s realized variance. Volatility is forecastable while expected returns do not rise proportionately. Market/value/momentum samples extend 1926–2015; FX carry spans 1983–2015. Market-factor regression alpha is 4.86% annualized; FX-carry alpha 2.78% is weaker statistically. Table IV examines market-portfolio costs and leverage-capped alternatives. Findings are not universal across every factor.

**Build:** A separate exposure overlay using only completed daily observations. Compare a predeclared capped inverse-variance version with a fixed-risk baseline; any cap/floor must be frozen before a future test. Do not estimate its scale using future full-sample volatility.

**Can code?** Technically straightforward, but actual strategy-level daily P&L, reliable mark times and account constraints are essential. Public factor data can illustrate the method; they cannot validate its effect on this book. Costs include resizing and integer-lot discontinuities.

**Our decision:** Highest practical account-survival research priority alongside data work, but NOT a new directional alpha and not a guarantee against a gap from a calm regime. Never let quiet markets authorize unlimited leverage. Do not stack it blindly on already volatility-scaled trend/carry.

## Repository comparison and research priority

Reviewed the handoff, AGENTS/BUILDER_BRIEF, TIER_LIST, DATA_NEEDED, progress and relevant previous reviews. Exact-ID searches found no selected-ID matches in those current branch records, but that is not an exhaustive semantic proof. The Gorton storage/momentum family already appears as rejected for NQ scope, and diversified trend already has a capital-expansion bench. These are explicitly not promoted.

Current commodity research D06 weekly basis reversal (5250499), D07 roll spreads (2942340), D08 momentum/carry (2614241), D09 skewness (3507947) shares the same matched-contract panel blocker. Neither continuous CL/GC data nor partial daily panel coverage resolves maturity fidelity. Annual index reweights were already reviewed and are not padded into this ten.

Priority order for preparation, not test authorization:
1. Obtain a no-purchase data/source manifest for #1/#2 and reconcile the existing panel. Kill work early if no legally usable contract history exists.
2. Define #10 as a book-risk question, without changing sizing or running a return test.
3. Use #7/#8/#9 as one coordinated diversified-sleeve research design, not three independent allocations.
4. Use #3/#4 to validate the commodity return accounting and economic mechanism.
5. Resolve #5 full text before a specification; place #6 behind a strict execution-cost and timestamp gate.

## Common implementation and evidence gates

- **Data/license:** Record owner, URL, coverage, frequency, contract identity, retrieval date, terms, permitted research/commercial use and redistribution limits. Free paper access is not a market-data license. No data was purchased or underlying datasets redistributed.
- **Universe:** Freeze point-in-time contract eligibility, exchange, first-notice/last-trade restrictions, minimum liquidity and missing-data handling. Exact 21/24/31-market constituent maps must match the chosen paper version before replication; do not silently substitute today's survivors.
- **Timing:** Signals must exist before orders. Settlement publication, CPI/inventory release lags, holidays and stale quotes require explicit treatment.
- **Costs:** Use both-leg fees/spreads, realistic roll costs, slippage under stress, financing/collateral, FX conversion and integer contracts. A negative-price-safe return convention must be declared for commodities.
- **Survival:** Evaluate joint intraday drawdowns, margin calls, liquidity and gap scenarios rather than only daily-return correlation or Sharpe. Low notional directional exposure does not mean low calendar-spread risk.
- **Validation:** None of these author results establishes present-day alpha. Keep a genuinely untouched period, document specification choices and avoid treating many closely related maturity signals as independent trials.
- **Account fit:** Most evidence requires monthly or overnight exposure across many markets. No evidence here supports porting it unchanged into a small NQ/MNQ/ES/MES book, ordinary prop flat rules or current capital limits. Actual account constraints were not accessed.
- **Status:** Ten papers found; nine have full-source methods/evidence inspected; #5 is explicitly limited. No strategy is admitted, no schedule is started, and no return test has been run.

