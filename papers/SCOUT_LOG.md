# Paper scout log

Every paper the scout (`/scout`, `.claude/skills/scout/SKILL.md`) looked at, newest at the bottom. Verdict: SKIP (why) /
READ (-> TIER_LIST grade) / NEED PDF (user downloads from SSRN and drops it in the Papers session).

| Date | Source | Title | Verdict |
|---|---|---|---|
| 2026-10-29 | arXiv 2605.04004 https://arxiv.org/abs/2605.04004 | Structural Limits of OHLCV-Based Intraday Momentum Signals in MNQ Futures (Mesfin 2026) | READ -> TIER_LIST F (14 OHLCV momentum families fail on MNQ 2021-25; the two 'positive controls' are GMM regime signals picked from 53+ combos, London B flips to t −2.8 with a 15-min delay) |
| 2026-10-29 | arXiv 2508.06788 https://arxiv.org/abs/2508.06788 | Returns and Order Flow Imbalances: Intraday Dynamics and Macroeconomic News Effects (Takahashi 2025) | SKIP as strategy (1-second ES SVAR; shocks die within a second) -> execution note E29 |
| 2026-10-29 | SSRN 3925725 https://papers.ssrn.com/abstract=3925725 | Liquidity Provision to Leveraged ETFs and Equity Options Rebalancing Flows (Barbon, Beckmeyer, Buraschi & Moerke) | SKIP: LETF end-of-day flow + next-open reversal already tested (Late-Day Flow, LETF overnight reversal, Codex LDF flow sizing) |
| 2026-10-29 | SSRN 6328819 https://papers.ssrn.com/abstract=6328819 | How Big Can Mechanical Rebalancing Get? (Nicolai & Risteska 2025) | NEED PDF: vol-targeting / risk-control forced deleveraging size; could time large-move days |
| 2026-10-29 | SSRN 3497537 https://papers.ssrn.com/abstract=3497537 | The Market Impact of Predictable Flows: Evidence from Leveraged VIX Products (Brøgger 2020) | SKIP: VIX futures (CFE, not Apex); author finds front-running unprofitable after costs |
| 2026-10-29 | SSRN 4692190 | 0DTEs: Trading, Gamma Risk and Volatility Propagation (Dim, Eraker & Vilkov) | SKIP: already in TIER_LIST (needs paid 0DTE dealer data) |
| 2026-10-29 | Gao, Han, Li & Zhou 2018 JFE | Market intraday momentum | SKIP: already tested (last-30-minute momentum rows) |
| 2026-10-29 | arXiv 2512.17923 | Inferring Latent Market Forces: LLM Detection of Gamma Exposure Patterns | SKIP: LLM evaluation, no return test |
| 2026-10-29 | arXiv 2601.17247 | Learning Optimal Liquidation with Closing Auctions | SKIP: stock execution theory, no futures fit |
| 2026-10-29 | arXiv 2504.20116 | Compounding Effects in Leveraged ETFs: Beyond the Volatility Drag Paradigm | SKIP: LETF holder returns, no flow timing |
| 2026-10-29 | arXiv 2505.17388 | Stochastic Price Dynamics in Response to Order Flow Imbalance: CSI 300 Index Futures | SKIP: China futures OFI; OFI already F on NQ (E25) |
