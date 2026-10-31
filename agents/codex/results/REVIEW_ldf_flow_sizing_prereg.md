# Claude's review: LDF flow-sizing pre-registration + input audit (codex/work 383014a, 03a20d0), 2026-10-22

**Verdict: approve with three required changes before any return is computed.** The protocol is careful: all LDF
events (no roster-flat selection), prior-day assets, lagged liquidity, rolling (not whole-sample) ranks, one
selectable rule (R) plus a mandatory two-session lag stress, matched-cell placebo, hard stop before 2023+ and the
funded bench, forward log only after a pass. The return-free audit is honest (492 design entries; $179 / $250
high-low gap for t 2 / 80% power) and it caught its own over-broad assertion (2010 SQQQ zero shares).

## Required changes

1. **The warm-up data doesn't exist.** The score needs 20 sessions of NQ 14:01-15:00 volume and >= 126 prior scores.
   Our NQ daytime files start 2018-01-02 (`NQ_1min_ON_2017.csv` is overnight only, no 14:00-15:00), so the first
   valid score falls around **August 2018**: roughly 60 of 2018's 103 design entries would be "unavailable", about 12%
   of 492, and gate 1 (>= 90% valid) would fail on data, not on the idea. Fix: the user exports `NQ_1min_2017.csv`
   (08:00-15:15, same format) from MultiCharts; or, if not, register the design window as starting when scores exist
   and count the 2018 shortfall openly. Decide before any return.
2. **The score tracks medium-term momentum.** Fund assets rise with NDX (TQQQ's NAV moves ~3x the index), so a
   trailing-252-session rank of H partly measures how far NQ has run. Return-free check on 2018-22 days (no LDF P&L
   used; script in this review's commit message): corr(rank, trailing 63-day NQ return) **0.38**, 252-day 0.16;
   mean trailing-252 return low / mid / high 9.3% / 14.5% / 17.2%; and the groups cluster by year (2021: 168 high vs
   19 low; 2020: 101 low vs 37 high). Add the trailing 63- and 252-session NQ returns (known at the decision) to the
   gate-4 regression, and add a trailing-63-return tercile to the gate-5 placebo cells. Report the rank's correlation
   with them before returns. Otherwise a "flow" result could be a regime / momentum result.
3. **Make the data gate passable.** Historical posting times and original vintages can't be recovered from today's
   files. The D−1 asset rule plus the mandatory two-session lag stress is an adequate standard for a design screen,
   labelled exploratory. Start archiving dated snapshots now for the forward phase. Keeping the status "NEEDS DATA"
   until vintages are verified would block the test permanently.

## Notes (no change required)
- Gates 3, 4 and 5 all test essentially the same high-vs-low contrast ((q−2) x net sums high minus low). That's fine
  as robustness, but requiring all of them lowers power further; expect a pass only for a large effect (high-tercile
  LDF trades near $190+ vs low near $10). Running it is still worth one trial: it's cheap and either answer helps.
- Continuous-contract roll weeks shift NQ volume between contracts; the 20-session median mostly absorbs it. Check
  that the 14:01-15:00 volume on roll Thursdays/Fridays isn't near zero.
- Multipliers are right: TQQQ 6, SQQQ 12, QLD 2, QID 6.
