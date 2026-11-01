# Paper scout log

Every paper the scout (`/scout`, `.claude/skills/scout/SKILL.md`) looked at, newest at the bottom. Verdict: SKIP (why) /
READ (-> TIER_LIST grade) / NEED PDF (user downloads from SSRN and drops it in the Papers session).

| Date | Source | Title | Verdict |
|---|---|---|---|
| 2026-10-29 | arXiv 2605.04004 https://arxiv.org/abs/2605.04004 | Structural Limits of OHLCV-Based Intraday Momentum Signals in MNQ Futures (Mesfin 2026) | READ -> TIER_LIST F (14 OHLCV momentum families fail on MNQ 2021-25; the two 'positive controls' are GMM regime signals picked from 53+ combos, London B flips to t −2.8 with a 15-min delay) |
| 2026-10-29 | arXiv 2508.06788 https://arxiv.org/abs/2508.06788 | Returns and Order Flow Imbalances: Intraday Dynamics and Macroeconomic News Effects (Takahashi 2025) | SKIP as strategy (1-second ES SVAR; shocks die within a second) -> execution note E29 |
| 2026-10-29 | SSRN 3925725 https://papers.ssrn.com/abstract=3925725 | Liquidity Provision to Leveraged ETFs and Equity Options Rebalancing Flows (Barbon, Beckmeyer, Buraschi & Moerke) | SKIP: LETF end-of-day flow + next-open reversal already tested (Late-Day Flow, LETF overnight reversal, Codex LDF flow sizing) |
| 2026-10-29 | SSRN 6328819 https://papers.ssrn.com/abstract=6328819 | How Big Can Mechanical Rebalancing Get? (Nicolai & Risteska 2025) | NEED PDF -> PDF from the user (papers/ssrn-6328819.pdf) -> READ -> TIER_LIST F (theory; mechanism already traded as Vol-Control Sell) |
| 2026-10-29 | SSRN 3497537 https://papers.ssrn.com/abstract=3497537 | The Market Impact of Predictable Flows: Evidence from Leveraged VIX Products (Brøgger 2020) | SKIP: VIX futures (CFE, not Apex); author finds front-running unprofitable after costs |
| 2026-10-29 | SSRN 4692190 | 0DTEs: Trading, Gamma Risk and Volatility Propagation (Dim, Eraker & Vilkov) | SKIP: already in TIER_LIST (needs paid 0DTE dealer data) |
| 2026-10-29 | Gao, Han, Li & Zhou 2018 JFE | Market intraday momentum | SKIP: already tested (last-30-minute momentum rows) |
| 2026-10-29 | arXiv 2512.17923 | Inferring Latent Market Forces: LLM Detection of Gamma Exposure Patterns | SKIP: LLM evaluation, no return test |
| 2026-10-29 | arXiv 2601.17247 | Learning Optimal Liquidation with Closing Auctions | SKIP: stock execution theory, no futures fit |
| 2026-10-29 | arXiv 2504.20116 | Compounding Effects in Leveraged ETFs: Beyond the Volatility Drag Paradigm | SKIP: LETF holder returns, no flow timing |
| 2026-10-29 | arXiv 2505.17388 | Stochastic Price Dynamics in Response to Order Flow Imbalance: CSI 300 Index Futures | SKIP: China futures OFI; OFI already F on NQ (E25) |
| 2026-10-29 | arXiv 2610.35887 https://arxiv.org/abs/2610.35887 | Evaluating ICT's Accumulation-Manipulation-Distribution (AMD) Model on NQ (Taylor 2026) | READ -> TIER_LIST F (rebuilt on NQ 2018-26) |
| 2026-10-29 | arXiv 2605.11423 https://arxiv.org/abs/2605.11423 | A Validated Volatility-Volume-Gap Classifier for Regime Identification in MNQ (Mesfin 2026) | READ -> TIER_LIST F (rebuilt on NQ 2018-26) |
| 2026-10-29 | arXiv 2607.01550 https://arxiv.org/abs/2607.01550 | Is Trend Still Your Friend? The Demise of Short-Term Trend-Following | READ -> TIER_LIST F (multi-day CTA trends; no test; tick-size finding noted) |
| 2026-10-29 | arXiv 2605.17724 | Sequential Structure in Intraday Futures Data: LSTM vs Gradient Boosting on MNQ | SKIP: negative ML result (OOS accuracy = base rate), nothing to test |
| 2026-10-29 | arXiv 2510.01542 | Equity Market Price Changes Are Predictable: A Natural Science Approach (ESM) | SKIP: unfalsifiable claims, no costs / OOS |
| 2026-10-29 | arXiv 2610.34787 | Do Round Numbers Hold Prices? (5 Nasdaq stocks, LOB) | SKIP: stocks; round levels attract depth but don't hold price (cf. E26 placebo levels) |
| 2026-10-29 | arXiv 2610.31141 | Intraday Forecasting Ability and Liquidity Provision of Institutional Traders | SKIP: needs exchange account-level flow |
| 2026-10-29 | arXiv 2408.05659 | A GCN-LSTM Approach for ES-mini and VX Futures Forecasting | SKIP: vol / volume forecasting ML, no trading test |
| 2026-10-29 | Kurov, Wolfe & Gilbert 2020 FRL (skidmore.edu PDF) | The Disappearing Pre-FOMC Announcement Drift | SKIP: pre-FOMC drift already tested (gone since 2018); paper agrees (weak since 2016) |
| 2026-10-29 | Harvey, Mazzoleni & Melone (SSRN, no free copy) | The Unintended Consequences of Rebalancing | SKIP: stock-vs-bond month-end rebalancing signal already tested (forced_flows_round5_test.py, t 1.2 / quarter-end −0.2) |
| 2026-10-29 | Princeton ORFE thesis 2026 | 0DTE Options and Intraday Volatility | SKIP: thesis; 0DTE gamma needs paid dealer data (TIER_LIST) |
| 2026-10-30 | NY Fed SR 917 https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf | The Overnight Drift (Boyarchenko, Larsen & Whelan; RFS 2023) + Liberty Street 2026 'The Disappearing Overnight Drift' | READ -> TIER_LIST F (hourly test on NQ / ES 2018-26) |
| 2026-10-30 | JFQA 2023 (no free PDF; Alpha Architect summary) | Market Return Around the Clock: A Puzzle (Bondarenko & Muravyev) | SKIP: claim (4 h around the European open = the whole ES return) covered by the same hourly test, 23:00-03:00 CT window |
| 2026-10-30 | arXiv 2507.04481 https://arxiv.org/abs/2507.04481 | Does Overnight News Explain Overnight Returns? (Glasserman, Krstovski, Laliberte & Mamaysky 2025) | READ -> TIER_LIST F (stock cross-section, NLP on 2.4M articles; no futures analogue) |
| 2026-10-30 | arXiv 2607.03669 | Split-Session Cluster GARCH for Overnight and Intraday Returns | SKIP: volatility model, no return timing |
| 2026-10-30 | arXiv 2610.06948 | Opening-Price Shortcut in Stock Prediction | SKIP: ML stock prediction methodology |
| 2026-10-30 | arXiv 2107.12516 / 2201.00223 / 1811.04994 | Knuteson follow-ups (They Chose to Not Tell You, They Still Haven't Told You, How to Increase Global Wealth Inequality) | SKIP: same thesis as SSRN 3705017 (F) |
| 2026-10-30 | arXiv 1410.5513 | 4-Factor Model for Overnight Returns | SKIP: stock factor model |
| 2026-10-30 | arXiv 2610.21846 https://arxiv.org/abs/2610.21846 | Where Backtests and Live Trading Part Ways: Six Defects from One Intraday System (Vidovich & Zerjal 2026) | READ -> execution note E31 (no strategy; backtest-live parity checklist mapped to our setup) |
| 2026-10-30 | practitioner pages (SpotGamma, NexusFi, LuxAlgo) | OPEX-week drift / pinning / dealer gamma | SKIP: no paper; OPEX open covered by Expiration Open Short (A), 0DTE gamma needs paid data, pinning F (NDX 0DTE study) |
| 2026-10-30 | Maberly & Waggoner, Atlanta Fed WP 2000-11 | Turn-of-the-month in S&P 500 futures | SKIP: turn of the month already tested on NQ / ES (overnight round, t 1.0-1.4); paper itself finds it gone after 1990 |
| 2026-10-30 | arXiv 2604.26063 | A Volume-Price-Adjusted MACD Trading Strategy for U.S. Equity Indices | SKIP: indicator paper (user's skip list) |
| 2026-10-30 | arXiv 2606.08586 | Cross-sectional topological anomaly scores and intraday return predictability in the S&P 500 | SKIP: stock cross-section, ML |
| 2026-10-30 | arXiv 2608.05373 | Detection of Intraday Options Market Manipulation | SKIP: surveillance, options |
| 2026-11-01 | ECB WP 1901 (JFQA 2019) https://ecb.europa.eu/pub/pdf/scpwps/ecbwp1901.lv.pdf | Price Drift before U.S. Macroeconomic News (Kurov, Sancetta, Strasser & Wolfe) | READ (method + release list) -> lab idea Q016 (ES / ZN pre-release drift at 09:00 CT releases) |
| 2026-11-01 | Van Hemert 2014 (SSRN; summaries Quantpedia / CXO) | MOM-TOM: Momentum and the Turn of the Month | LAB IDEA Q017 (CTA flow on TOM days in CL / NG / GC / ZN / 6E); NEED PDF optional for the lab |
| 2026-11-01 | Blose, Gondhalekar & Kort 2018 (J. Futures Markets?) | Gold overnight vs day returns, COMEX 1985-2012 | LAB IDEA Q018 (GC overnight long / day short); NEED PDF optional |
| 2026-11-01 | AEA 2023 slides (Ge, Kang, Tang & Yang) | WTI negative price: settlement-window closing pressure | SKIP: CL settlement window already F (cl_forced_flows_test.py) |
| 2026-11-01 | IAEE proceedings 2025 | Intraday seasonality in Brent futures | SKIP: ICE Brent (no data / not Apex); CL seasonality covered by CL forced-flow rows |
| 2026-11-01 | OPEC meeting-window hedging study (MPRA) | OPEC meeting cycles and commercial hedging | SKIP: ~2-4 meetings a year, fails the lab's power check (Q012 lesson) |
| 2026-11-01 | Kellard, Jiang & Liu 2020 JFM; Zhou (AUT); GFJ 2025 | Chinese gold / silver futures night session | SKIP: SHFE effects; Shanghai open / SGE items already F |
| 2026-11-01 | LSEG 2024 research paper | How markets react to CPI surprises | SKIP: reaction to surprise needs consensus data; ZN after 07:30 releases already F |
| 2026-11-01 | Baltas & Kosowski; GSCI rebalancing study (AgEcon) | CTA capacity / index-roll flows | SKIP: GSCI / BCOM roll windows already F |
| 2026-11-01 17:43 UTC | scheduled run | (no search) | STOP: 6 ideas already queued in lab/IDEAS.md (Q013-Q018 >= 5); nothing added |
| 2026-11-01 22:43 UTC | scheduled run (re-run after a worker restart) | (no search) | STOP: 5 ideas already queued in lab/IDEAS.md (Q014, Q015, Q017, Q018, Q019); nothing added |
