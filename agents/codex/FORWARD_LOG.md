# Forward log: paper tracking for promising candidates with open doubts

Since 2026-10-23 (user) the forward log is discretionary: a candidate that clears every test, including a gain on the
plan bench, goes straight into the plan and is monitored live (`DEVELOPMENT_PROCESS.md`, 'Straight into the plan, or the
forward log'). The entries below were all logged for open doubts (fitted on the full sample or after seeing 2023+, DSR
below 0.95, weekend / drift dependence) and none improved the Apex plans, so they stay as paper tracking.

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
| **FC 2B v2** (Flow-Confirmed Opening Drive, NQ 1-min; `checks/candidates/fc_2b/FC_2B_v2.txt`) | 2026-10-23, code commit 848923d (v2 report aa41668) | `checks/candidates/fc_2b/REVIEW.md`, `verdict.md` | 0 | $0 | Tracking from 2026-10-26 |
| **S47 v2** (Europe-Open Impulse, NQ; rule = `checks/candidates/s47_v2/S47_v2.txt`, fixed code `S47_v2_fixed.txt`) | 2026-10-23, rule script commit 130020c | `checks/candidates/s47_v2/REVIEW.md` | 0 | $0 | Tracking from 2026-10-26 |
| **Kusho v9** (both exits: 21:00 with weekend holds, and flat 15:45; NQ; `checks/candidates/kusho/Kusho_v9.txt`) | 2026-10-23, rule script commit ea18c5f | `checks/candidates/kusho/REVIEW.md` | 0 | $0 | Tracking from 2026-10-26 |
| **S30 IBS reversal** (NQ + ES, long only; `checks/candidates/s30_ibs/S30_IBS.txt`) | 2026-10-23, rule script commit 28be7ae | `checks/candidates/s30_ibs/REVIEW.md` | 0 | $0 | Tracking from 2026-10-26 |

### FC 2B v2: decision rule (written 2026-10-23, before tracking)
- **Signals:** every day the v2 rule fires, from a re-exported MultiCharts v2 backtest (same chart, same inputs) at each
  month's first-Friday review; skipped days logged with the reason (data gap, holiday flatten). Paper only: not traded.
- **Costs:** $7.25 per NQ round trip + 1 tick per market / stop fill (results per NQ; 1 MNQ = 1/10).
- **Checkpoints:** 40 signals (~6 months) and 80 signals (~11 months).
- **CONTINUE** if the forward mean per trade is inside the backtest's 10-90% Monte Carlo band for that many trades;
  **REJECT** if below the 10% band, or forward mean <= 0 with t <= -1 at 40 signals; **EXTEND** once (to 80) when in
  between. **PROMOTE** (personal account or a 150K plan test) only after 80 signals, and only by the user.

### S47 v2, Kusho v9, S30: decision rule (written 2026-10-23, before tracking)
- **Signals:** every signal of the frozen rule from 2026-10-26 on, computed with the frozen Python rebuilds
  (`analysis/s47_test.py`, `analysis/kusho_test.py`, `analysis/s30_ibs_test.py`, unchanged) on the weekly 1-minute NQ / ES
  exports (TODO: 'export fresh 1-minute data' each Friday); a MultiCharts run of the same code replaces the rebuild once
  the user exports one. Paper only: none of them is traded.
- **Costs:** as in each review ($7.25 per NQ / $5 per ES round trip + 1 tick per market / stop fill; limits 1 tick through,
  targets 1 point through).
- **Checkpoints:** S47 v2 40 / 80 signals (~6 / 12 months); Kusho v9 100 / 200 signals (~4 / 8 months); S30 20 / 40 trades
  per market (~9 / 18 months; it trades ~28 times a year).
- **CONTINUE** if the forward mean per trade is inside the backtest's 10-90% Monte Carlo band for that many trades;
  **REJECT** if below the 10% band, or forward mean <= 0 with t <= -1 at the first checkpoint; **EXTEND** once when in
  between. **PROMOTE** (personal account; S30 only once the account is ~$33k) only after the last checkpoint, by the user.

### Frozen bands and exhaustive decisions (2026-10-23, before any forward observation; after Codex's review)
Computed once by `analysis/forward_bands.py` (output `analysis/outputs/forward_bands_output.txt`; backtest ledgers as they
are today, iid resampling of trades, 20,000 draws, seed 20261023). **Not recomputed later**, even if a backtest changes.
Per full contract, after the repo's costs:

| Rule | Checkpoint 1: p10 / p90 | Checkpoint 2: p10 / p90 | False rejection if the backtest is true |
|---|---|---|---|
| FC 2B v2 | 40: −$104 / $658 | 80: −$1 / $550 | 9.9% at 40, 15.0% by 80 |
| S47 v2 | 40: −$102 / $809 | 80: $33 / $671 | 9.8%, 15.5% |
| Kusho v9 (21:00) | 100: −$36 / $255 | 200: $6 / $213 | 9.9%, 15.5% |
| Kusho v9 flat 15:45 | 100: −$41 / $230 | 200: −$4 / $188 | 10.0%, 15.0% |
| S30 NQ | 20: −$381 / $3,057 | 40: $122 / $2,568 | 10.1%, 15.4% |
| S30 ES | 20: −$192 / $1,818 | 40: $98 / $1,537 | 10.0%, 15.1% |

- At each checkpoint: **REJECT** if the forward mean < p10 (checkpoint 1 also: mean <= 0 with t <= −1); **CONTINUE** if
  p10 <= mean <= p90 (after checkpoint 2: 'passed', eligible for the user's decision, not automatic promotion); **CHECK** if
  mean > p90: continue as above, but audit data and fills first. No extension beyond checkpoint 2 unless the user decides.
- The joint false-rejection rate of the two checkpoints is ~15%, not 10% (accepted openly, not tuned later).
- **Power is low:** a band whose p10 is near or below zero can only catch a clearly broken rule; a dead edge (mean about
  −costs) still passes checkpoint 1 about half the time. These logs detect breakage, not prove an edge.
- Records: each month's export / rebuild output is archived under `agents/codex/forward/<rule>/YYYY-MM-DD/` with the chart
  inputs, session and data source; new signals are appended, old ones never rewritten; missing data is logged separately
  from a no-signal day. Paper results can't establish spreads, fills or protective-order timing.
