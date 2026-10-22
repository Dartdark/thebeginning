# Step 1 result: leveraged-ETF data feasibility (2026-10-22, no returns looked at)

**Feasible, free.** ProShares publishes daily NAV, shares outstanding and assets for every fund since inception
(`data/letf/`). Prior-day assets are known before a 14:00 CT decision, so the dollar-flow estimate is point-in-time.

Reset demand per 1% Nasdaq-100 move, Σ L(L−1) x prior-day AUM / 100 (TQQQ, SQQQ, QLD, QID), yearly medians:

| 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| $0.34bn | $0.42bn | $0.59bn | $1.08bn | $1.32bn | $1.63bn | $1.83bn | $2.11bn | $2.61bn |

About 8x growth: the same % move means very different dollar flow, so the estimate varies independently of the
price move (Codex's novelty concern is answered on the data side). For scale, NQ trades a median ~$24bn in
14:00-15:00 CT (2023-25).

Limits: no intraday creation / redemption data (the Ivanov-Lenkey offset remains unobserved; same-day flows show up
only in the next day's shares outstanding). Single-stock leveraged ETFs (e.g. on NVDA) are not included.

Next (not done): pre-register the LDF sizing test on 2018-22 before looking at any LDF returns by flow
(Codex's point 3): one variant, net $ by tercile of predicted flow / NQ 14:00-15:00 volume at the same move size, a
random-tercile placebo, funded bench only if the design gate passes, forward log if it passes.
