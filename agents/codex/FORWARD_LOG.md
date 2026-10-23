# Forward log: rules frozen before they can trade

A rule that passes testing is frozen here (exact rule, code / script commit, date frozen). From then on its paper
results are added at each Friday review. 2023+ has been reused by many ideas, so forward results are the clean test.

## Every entry must state BEFORE tracking starts
- **Rule and code:** exact rule, script / MultiCharts commit, date frozen.
- **What counts as a signal:** every eligible signal is logged (filled, missed, rejected, skipped by an overlap or risk
  rule, with the reason). Paper P&L uses the rule's own fills with full costs ($7.25 + 1 tick per market / stop fill;
  targets need 1 point through); live fills, if any, are logged next to it.
- **Review dates and minimum sample:** e.g. each Friday review for updates, decisions only at the stated checkpoints
  (number of signals or months, whichever the entry names).
- **Decision rule at each checkpoint**, fixed in advance, for example:
  - CONTINUE: forward net per trade inside the backtest's 10-90% Monte Carlo range for that many trades;
  - REJECT: below the 10% band at the checkpoint, or forward mean <= 0 with t <= -1 once the minimum sample is reached;
  - EXTEND: in between, with a stated new checkpoint (at most once);
  - PROMOTE: only after the final checkpoint, and only by the user.
- Nothing in an entry changes after tracking starts; a changed rule is a new entry with a new start date.

| Rule | Frozen (date, commit) | Source report | Forward trades | Forward net (per NQ) | Status |
|---|---|---|---|---|---|
| **FC 2B v2** (Flow-Confirmed Opening Drive, NQ 1-min; `checks/candidates/fc_2b/FC_2B_v2.txt`) | 2026-10-23, commit aa41668 (v2 report) | `checks/candidates/fc_2b/REVIEW.md`, `verdict.md` | 0 | $0 | Tracking from 2026-10-26 |

### FC 2B v2: decision rule (written 2026-10-23, before tracking)
- **Signals:** every day the v2 rule fires, from a re-exported MultiCharts v2 backtest (same chart, same inputs) at each
  month's first-Friday review; skipped days logged with the reason (data gap, holiday flatten). Paper only: not traded.
- **Costs:** $7.25 per NQ round trip + 1 tick per market / stop fill (results per NQ; 1 MNQ = 1/10).
- **Checkpoints:** 40 signals (~6 months) and 80 signals (~11 months).
- **CONTINUE** if the forward mean per trade is inside the backtest's 10-90% Monte Carlo band for that many trades;
  **REJECT** if below the 10% band, or forward mean <= 0 with t <= -1 at 40 signals; **EXTEND** once (to 80) when in
  between. **PROMOTE** (personal account or a 150K plan test) only after 80 signals, and only by the user.
