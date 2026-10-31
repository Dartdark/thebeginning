# Hourly 2-bar CHoCH: one bounded round (pre-registered 2026-10-29, before any new returns)

User request 2026-10-29: make the hourly two-candle CHoCH 1:2 foundation (Codex, codex/work
`agents/codex/results/choch_rr2_20261028.md`, filters and placebos 10/28-29) Apex / personal-plan ready if possible.
Codex's design result (2018-22, one MNQ): 408 trades, $4,896, t 1.22, PF 1.19; 4 filters failed; random side p 0.11.
2023+ prices for this rule are unopened by anyone. Filters on the same baseline are NOT retried here.

## Signal (unchanged from Codex's frozen engine `codex_choch4h.signals`, radius 2)
CT clock-hour bars over the whole CME session (bar closes at :00); strict pivot = high (low) above (below) the 2 bars on
each side, usable when the 2nd right bar closes; trend +1 after HH+HL, -1 after LH+LL; long when trend -1 and an hourly
close crosses above the last confirmed swing high (stop = last swing low), short mirrored; each broken pivot used once;
signal closes 09:00-14:00 CT on normal cash days, entry OPEN of the 2nd minute after the close (Codex: signal+2), flat at
the OPEN of the 15:58 bar; one position at a time; early-close days skipped (Codex flattened 11:30; too few to matter).
Our data (g24, data/NQ_1min*): an hour bar uses the minutes that exist (no whole-hour invalidation for one missing
quiet minute, the 17:01 issue in Codex's source); a data hole (no minute at all in the hour) resets the structure.

## Variants (5 trials; all counted in analysis/trials.py)
- B0  rebuild of the baseline (stop swing, target 2R with 1 pt trade-through), NQ. Reproduction, also a trial.
- V1  TIME: same entry and swing stop, NO target, out at 15:58.
- V2  BE: same, stop to entry once +1R is touched, no target, out at 15:58.
- V3  ONB SIDE: B0 exits, only signals on the Overnight Bias side (08:30 open in the top third of the 23:00-08:30
      range -> longs only, bottom third -> shorts only, middle -> no trade).
- V4  ES: B0 on ES (24-hour ES data), $5 + 1 tick.
No other variant, parameter or filter will be run in this round.

## Costs / measurement
$7.25 per NQ ($5 ES) + 1 tick on the market entry and on stop / time exits; targets are limits filled only on a 1-point
trade-through. Report per NQ and per MNQ (/10). Metrics per CLAUDE.md (Sharpe, Sortino, PF, Calmar, Ulcer; longs and
shorts), by year.

## Gates
Design 2018-22: >= 100 trades, net > 0, t >= 2.0, PF >= 1.25, >= 4 of 5 years positive.
Only a design survivor opens 2023-26 (holdout): net > 0 and t >= 1.5 there; promotion above C needs the full-period
t >= metrics.t_threshold(N_items) (3.62 at N 346, rising) or deflated Sharpe >= 0.95. Then the plan benches (add AND
replace: personal portfolio, 50K funded bootstrap, evaluation). No survivor -> stop, record in TIER_LIST, no rescue.
