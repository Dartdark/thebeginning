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
| (none yet) | | | | | |
