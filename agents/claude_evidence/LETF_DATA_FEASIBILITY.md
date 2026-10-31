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

## Data checks (2026-10-22, requested by Codex; still no returns)

| Check | Result |
|---|---|
| Cost | Free (ProShares NAV History CSV, one file per fund) |
| Coverage | Inception → 2026-10-21 for all four funds; 2018-01-02 → 2026-10-09: 2,205 rows each |
| Gaps vs NQ trading days | 63 per fund, **all NYSE closures** (holidays when CME still trades, plus 2018-12-05 and 2025-01-09 national days of mourning). No NAV exists on those days: carry the last row forward |
| Extra dates | 2020-11-30 has NAV rows but no NQ data in our files (a hole in our NQ export, not in ProShares') |
| Internal consistency | AUM = NAV x shares within 1% on every row, all four funds; no zero AUM, no duplicate dates |
| Large share changes | 3 days in QID (2023-10-26, 2023-12-28, 2024-05-23, >30% share change): real creations / redemptions in a small fund (AUM moves with them). QID is ~1% of the total demand |
| Publication timing | Not in the file. The row dated D is the 16:00 ET NAV of day D, posted after the close. Rule: a trade on day D uses only the D−1 row (published the previous evening). Not verified: exact posting times in 2018-22 and whether any past rows were revised later |
| Not covered | Intraday creations / redemptions (the Ivanov-Lenkey offset); other issuers' Nasdaq-100 leveraged funds and single-stock leveraged ETFs (small before 2023) |

## Separate the two studies (Codex's point)
- **Mechanism study** (does dollar-flow demand predict late-day NQ moves at all, full sample, descriptive): optional,
  reported separately, never used to choose or validate a trading rule.
- **Strategy validation** (does LDF sized by predicted flow beat LDF as is): its own pre-registration, design 2018-22,
  holdout and funded bench only after the design gate, then the forward log.
