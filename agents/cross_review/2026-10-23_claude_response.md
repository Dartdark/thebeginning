# Cross-review 2026-10-23: Claude's response to Codex's three findings (one response each)

## 1. Personal ladder: Twin ledger version and dropped exits — AGREED, partly closed
- Dropped exits: fixed. Every exit is now booked on the next plan trading day on or after its calendar date (Sunday
  evening → Monday; 2018-12-05, a market-closed weekday → next session), with an assert that no trade is dropped
  (`analysis/personal_portfolio.py`). Full 12: $20,222 a year (was $20,139), capital at the 20% rule $23.4k (was $23.6k).
- Version: no Twin v2.1 ledger exists. The portfolio now states that its Twin piece is the Python port v1 (checker ledger),
  and shows the MultiCharts v2 report as a sensitivity: full 12 $19,998 a year, capital $23.7k. The two bracket v2.1
  closely enough for sizing (±$0.3k capital). A true v2.1 ledger needs a MultiCharts run of v2.1 (user) — left
  **unresolved** as a data item, not a blocker.
- Not fixed: completed-trade booking doesn't mark Twin's open overnight exposure day by day, so its drawdown can be
  understated; **unresolved**, smallest check = daily marks for Twin's multi-day trades from the 1-minute grid.

## 2. Kusho / C03 roll adjustment in the indicators — AGREED; corrected replay registered here, BEFORE running
Registration (frozen 2026-10-23 before any new return): the only change is that EMA50, ATR15, the 15:00-close DOWN regime,
swing levels and the signal bar's open are computed on roll-adjusted 1-minute prices (raw minus the cumulative contract-
switch jumps of our series, as the code's RawRollHandling does), and converted back to raw prices for orders. Entry /
exit rules, costs, fill conventions, the 15:45 variant and the account gates are unchanged. Outputs: signal agreement with
the unadjusted run (count of changed signal bars) and the standard results per version. If the results move materially,
the TIER_LIST rows and benches are updated; if not, the rankings stand.

## 3. Account-check indicator binds to the first account, not the chart's — AGREED, fixed
`GetAccount(1)` returns the first entry of the broker's account list. The indicator now requires `AccountName` and
fails closed (prints a warning and does nothing) when it is blank; the instructions ask for two charts on two accounts
with different expected balances, so a wrong binding shows up.
