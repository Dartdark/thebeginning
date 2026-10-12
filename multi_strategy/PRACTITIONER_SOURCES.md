# Practitioner research: where market makers, bank desks, options traders and fund quants publish

Started 2026-10-12. A reading guide for new strategy ideas, sorted by **who writes it** and
**what it is good for here** (NQ/ES intraday, Apex, forced flows). Access: **free**, **paid**
(subscription or per article), **client** (bank or broker clients only; usually reaches the
public through press quotes and reposts).

**How to use it:** send me a paper, note or post from any of these. I summarize it, say whether
a strategy can be built on it, test it when it fits, and rank it in `../TIER_LIST.md`.
Highest priority: anything describing **flows someone must trade regardless of price** (dealer
hedging, rebalancing, expiration, index and ETF mechanics). Price-pattern direction signals have
failed out of sample here, so practitioner "setups" without a flow behind them rank last.

A note on market makers: firms like Citadel Securities, Jane Street, Optiver, Susquehanna (SIG),
IMC, Virtu and Jump publish almost nothing about their trading. The useful writing comes from
**people who left them**, from **bank derivatives strategists who watch dealer positioning**,
and from exchanges. The list is sorted with that in mind.

---

## 1. Practitioner journals (peer-reviewed or edited, mostly written by industry)

| Journal | Who writes in it | Access | Good for |
|---|---|---|---|
| *Journal of Portfolio Management* (With Intelligence / PMR) | AQR, Man, Research Affiliates, GMO, bank quants | paid; many papers also on SSRN | Factor and trend research, rebalancing, risk |
| *Journal of Derivatives* (same publisher) | Options desk quants, exchange researchers | paid | Options pricing, hedging flows, volatility |
| *Journal of Financial Data Science* (same publisher) | Fund and bank ML teams | paid | ML filters (like the ONB ridge filter) |
| *Journal of Alternative Investments* (CAIA) | CTA and hedge fund managers | paid | Managed futures, trend following, CTA behaviour |
| *Financial Analysts Journal* (CFA Institute) | Asset managers and academics | paid; free to CFA members | Broad; strong on rebalancing and market structure |
| *Risk* magazine, "Cutting Edge" papers (risk.net) | Bank quants (where local volatility and many vol models first appeared) | paid | Volatility models, dealer hedging, market impact |
| *Wilmott* magazine | Quant practitioners | paid | Options, volatility, model risk |
| *Quantitative Finance*; *Market Microstructure and Liquidity* | Mixed; many fund quants (e.g. CFM) | paid; preprints on arXiv | Microstructure, order flow, impact |

**Free shortcut:** most of these authors post the same papers on **SSRN** (papers.ssrn.com)
and **arXiv q-fin.TR** (trading and microstructure). Search by firm name in the author
affiliation, e.g. "AQR", "Man AHL", "Capital Fund Management", "Goldman Sachs".

## 2. Hedge fund and asset manager research libraries (free)

| Source | Who | Good for here |
|---|---|---|
| **AQR Research** (aqr.com, "Insights / Research") | Asness, Pedersen, Moskowitz, Ilmanen | Time-series momentum and trend following in futures; *Fact, Fiction* series (one already ranked F here: it's stock momentum) |
| **Man Institute** (man.com, "Insights") and **Man AHL** papers | Man AHL quants; Oxford-Man Institute link | Trend following, CTA positioning, intraday futures execution, ML in trading |
| **Capital Fund Management (CFM)** research (cfm.com) | Bouchaud and team | Market impact, order flow, intraday mean reversion vs momentum; book *Trades, Quotes and Prices* |
| **Winton** research (winton.com) | Trend-following CTA | Futures trend, seasonality |
| **Graham Capital** research notes (grahamcapital.com) | Macro / CTA | Trend following, CTA flows |
| **Lynx Asset Management** research | CTA | Trend following behaviour in crises |
| **Two Sigma** articles (twosigma.com) | Systematic fund | Factor and regime research |
| **Research Affiliates** (researchaffiliates.com) | Arnott and team | Rebalancing, index construction (index-change flows) |
| **Robeco Quant** research (robeco.com) | Blitz, Baltussen, van Vliet | *Hedging demand and market intraday momentum* (Baltussen et al. 2021, tested here: D); low-vol, factor timing |
| **Bridgewater** "Research & Insights" (public part of the Daily Observations) | Macro | Macro regimes; long horizon, little for intraday |
| **GMO** white papers | Value / macro | Long horizon; little for intraday |

## 3. Bank derivatives and flow strategists (client; mostly seen through press and reposts)

These are the people who model **dealer gamma, vol-control funds, CTA trigger levels,
leveraged-ETF rebalancing, buyback windows and pension rebalancing**, which is the
forced-flow family that has worked best here (Expiration Open Short, Late-Day Flow).

| Desk / note | What it covers | How to get it |
|---|---|---|
| **JPMorgan** equity derivatives / quant strategy (Kolanovic's team until 2024) | Dealer gamma, vol-control and risk-parity deleveraging, CTA positioning; the 2017 *Big Data and AI Strategies* report | Client; the 2017 report circulates as a PDF; quotes in Bloomberg / FT |
| **Goldman Sachs** flow desk (*Tactical Flow-of-Funds*) and derivatives research; *Top of Mind* | Systematic and buyback flows, CTA trigger levels, options positioning | Desk notes client; *Top of Mind* is public on goldmansachs.com |
| **Nomura** cross-asset strategy (McElligott) | Dealer gamma, vol-control, CTA flows around big moves | Client; widely quoted |
| **BofA** *Flow Show* (Hartnett) and derivatives research | Fund flows, positioning extremes | Client; summaries in the press |
| **Citi, Barclays, UBS, Deutsche, Société Générale** derivatives strategy | Options positioning, vol, 0DTE flows | Client |

**Public substitutes that rebuild the same flow models:**
- **SqueezeMetrics** white papers (free): *Gamma Exposure* (GEX) and *Short Is Long* (DIX). Used here
  already: GEX filters ranked B/D, DIX D.
- **Cboe** Insights and research (free): 0DTE volume and dealer positioning studies, VIX and SPX
  expiration mechanics, settlement (the mechanism behind Expiration Open Short).
- **CME Group** education and market data notes (free): futures roll, settlement, block and
  liquidity data, options on futures expirations (weekly NQ / ES options).
- **BIS Quarterly Review** and **Federal Reserve FEDS / NY Fed Staff Reports** (free): regulators
  studying dealers and forced flows, e.g. the February 2018 VIX-product unwind, vol-targeting
  funds, leveraged-ETF rebalancing. Not practitioners, but they use dealer data the public can't
  see.

## 4. Former market makers and options traders (books, blogs, newsletters)

| Author / source | Background | Format | Good for |
|---|---|---|---|
| **Euan Sinclair**: *Volatility Trading*, *Positional Option Trading*, *Retail Trading Edges* | Options market maker, fund manager | Books | Which option and volatility edges are real; how to judge an edge |
| **Kris Abdelmessih**: *Moontower* newsletter | Former SIG options trader and MM | Free Substack | Volatility, dealer mechanics, how market makers think |
| **Sheldon Natenberg**: *Option Volatility and Pricing* | Floor trader, trainer of MMs | Book | The standard MM text |
| **Colin Bennett**: *Trading Volatility* | Head of derivatives strategy at a bank | Book | Dividend, skew, vol-of-vol, dealer hedging |
| **Benn Eifert** (QVR Advisors) | Volatility hedge fund | Posts on X, interviews | Dealer gamma, vol-control flows, 0DTE |
| **Robert Almgren / Quantitative Brokers** research notes | Execution quants (Almgren–Chriss), **CME futures** execution | Free notes | Intraday liquidity and impact in NQ/ES, roll, auction times |
| **Larry Harris**: *Trading and Exchanges* | Former SEC chief economist | Book | Who trades and why; the base for any "forced flow" idea |

## 5. Systematic fund quants (books and blogs)

| Author | Background | Format | Good for |
|---|---|---|---|
| **Robert Carver**: *Systematic Trading*, *Advanced Futures Trading Strategies*; blog *qoppac* | Former Man AHL portfolio manager | Books, free blog | Futures systems, sizing, costs, overfitting guards |
| **Ernest Chan**: *Algorithmic Trading*, *Quantitative Trading* | Former bank and fund quant | Books, blog | Intraday futures mean reversion and momentum; ready-made tests |
| **Marcos López de Prado**: *Advances in Financial Machine Learning*; SSRN papers | Former Guggenheim / AQR | Book, free papers | Backtest overfitting, deflated Sharpe, purged walk-forward |
| **Antti Ilmanen**: *Expected Returns*, *Investing Amid Low Expected Returns* | AQR | Books | Which premia are structural |
| **Grinold & Kahn**: *Active Portfolio Management* | BGI | Book | Combining signals, the information ratio |
| **Corey Hoffstein / Newfound Research** blog | Systematic manager | Free | **Rebalance timing luck** (when funds rebalance = forced flow), trend following |
| **Alpha Architect** blog (Wes Gray) | Systematic manager | Free | Summaries of new SSRN papers each week |
| **Perry Kaufman**: *Trading Systems and Methods* | CTA and system developer | Book | Large catalogue of tested futures rules |

## 6. Interviews and podcasts (practitioners talking about what they actually trade)

- **Flirting with Models** (Hoffstein): systematic managers, volatility and options traders.
- **Top Traders Unplugged**: CTA and trend-following managers.
- **Odd Lots** (Bloomberg): dealers, market makers, flow strategists on market plumbing.
- **Market Wizards** series (Schwager): older, but the futures traders' chapters are first-hand.

---

## What to look for first (fits this repo's best direction)

| Flow / mechanism | Practitioner source | Status here |
|---|---|---|
| Options expiration and settlement (monthly, quarterly, 0DTE) | Cboe research, bank derivatives notes, SqueezeMetrics GEX | **Expiration Open Short (A)**; 0DTE dealer data is paid |
| Leveraged-ETF and last-hour rebalancing | Bank derivatives notes, BIS / Fed papers | **Late-Day Flow (A)** |
| Weekend / Monday inflows | Flow desks (fund flows) | **Monday Long (A)** |
| Dealer gamma regime (long vs short gamma days) | SqueezeMetrics, Nomura / JPM notes, Eifert | GEX filter B (needs daily data entry) |
| Vol-control and risk-parity deleveraging | JPM / Nomura notes, BIS | Simple realized-vol trigger F; a version using published vol-control models is **untested** |
| CTA trend-following trigger levels | GS / Nomura CTA models, Man / AQR / Carver on trend rules | **Untested**: rebuild a public CTA model (e.g. 20/60/120-day breakouts on NQ) and test the day after a trigger level is crossed |
| Buyback blackout windows | GS flow desk | F (no effect found) |
| Pension / quarter-end rebalancing | Bank strategists, Hoffstein (timing luck) | F (quarter-end fade) |
| Index rebalances (S&P, Nasdaq-100 reconstitution, QQQ special rebalances) | Research Affiliates, bank index desks | F for regular rebalance days; **Nasdaq-100 special rebalances untested** |
| Futures roll and auction mechanics | Quantitative Brokers, CME | Roll-week short D |

The two **untested** forced flows above (CTA trigger levels, vol-control models) are the
next candidates when you want a test without a new paper.
