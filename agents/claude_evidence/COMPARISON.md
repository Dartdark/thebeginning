# Evidence-sheet competition: Claude vs Codex (2026-10-22)

Codex: `agents/codex/results/flow_evidence_sheets.md` (codex/work 134e175). Claude: `agents/claude_evidence/` (written
before reading Codex's; sealed outside the repo until Codex pushed). Neither ran a return test. The user judges.

## Independent agreement
Both picked the same two families without seeing each other's sheets:
- **Auction imbalance data** (Codex A + B: SPY opening revisions / post-close reversal on NYSE Arca; Claude #2: NYSE
  closing imbalance for ES MOC, then the open).
- **Leveraged-ETF reset sized by assets** (Codex C, ranked 4th; Claude #1, ranked 1st).
Both concluded that the next edges need new data, not new rules on old price data.

## Scorecard (Claude's own assessment; Claude is not neutral here)

| Criterion | Codex | Claude |
|---|---|---|
| Data detail (fields, timestamps, receipt lag, historical rule changes, point-in-time traps) | **Stronger** (e.g. MOO orders cancellable until 09:29 ET; Nasdaq disclosure moved 09:28→09:25 ET in 2021; T+1 Cboe files unusable same-day) | Weaker (didn't flag cancellable orders or point-in-time AUM risk) |
| Originality | **Stronger** (D: signed market-maker option volume x delta decay; B: post-auction reversal) | Two ideas killed at the sheet (OPEX week, margin hikes) |
| Power checks with numbers | Not done (deferred to an event census) | **Done for all four** |
| Decision-readiness (one verdict, data cost, the cheapest next step) | Lower (one long report, "WATCH" overall, no cost estimates) | **Higher** |
| Followed the task format (`evidence/` files + SUMMARY) | No (single results file) | Yes |
| Cheapest path to a real test | None without purchases | LETF sizing test inside LDF's 895 trades if free daily shares-outstanding history exists |

Main disagreement: the LETF idea. Codex: assets only rescale the same price sign, and the remaining demand after
creations / redemptions is unobservable, so it is blocked. Claude: that is exactly what one pre-registered test inside
LDF would settle (net $ by tercile of AUM-scaled flow / NQ last-hour volume; ~$130 tercile difference needed), with
prior-day shares outstanding as the point-in-time AUM. Codex's point-in-time and offset caveats stand.

## Joint recommendation
1. **Ask NYSE for a quote and a sample** of TAQ NYSE Arca (SPY) and NYSE order imbalances 2018-26. One purchase
   covers Codex A / B and Claude #2. Then an event census (no returns) before any rule.
2. **Check for a free point-in-time shares-outstanding history** for TQQQ / SQQQ / QLD / QID. If it exists, run the
   single LDF tercile test; if not, drop it.
3. Codex D (Cboe Open-Close) only after 1, and only if the historical delivery lag can be verified.
