# EUR/USD futures after the London FX fix

## Motivation and plan gaps

The current plan is concentrated in NQ and Monday trades. `agents/tasks/plan_daily_pnl.csv` has zero recorded activity
on 88/455 Thursdays, 74/456 Tuesdays and 64/453 Wednesdays, versus 0/452 Mondays. Daily P&L does not show intraday
positions: these are date-level gaps, not proof of an unused intraday hour. EUR/USD futures add a different flow and
instrument without conditioning on the existing strategies' later profits or losses.

Claude review `680f304:agents/codex/results/REVIEW_marginal_contribution.md` accepted the roster and rejected further
VB overlap tuning. No VB sizing test will be run. This new idea was absent from the tier list and research-script search
for WMR / WM/Reuters / FX fixing. The previously failed FX weekend-gap and NQ European-close rules are different mechanisms.

## Mechanism and sources

Benchmark-tracking investors submit currency-conversion orders to transact at the London 16:00 WMR fix. Concentrated
benchmark execution can temporarily push price away from equilibrium; after orders finish, liquidity providers may
unwind inventory. The directional reversal and its survival after futures costs are hypotheses, not established findings
of the cited sources. This is a new futures test, not a claim to replicate a published profitable strategy.

- LSEG WMR benchmark description: https://www.lseg.com/en/ftse-russell/benchmarks/wmr-fx-benchmarks
- WMR methodology v30, January 2026, section 4.4.2: five-minute window centered on the fix, ending 16:02:30 London:
  https://www.lseg.com/content/dam/ftse-russell/en_us/documents/ground-rules/wmr-fx-methodology.pdf
- Michelberger and Witte, *Foreign Exchange Market Microstructure and the WM/Reuters 4pm Fix*, arXiv:1501.07778v2.
  The paper documents unusual fixing-window volatility and extrema on pre-2015 spot data; it does not prove net futures
  reversal profitability. https://arxiv.org/html/1501.07778v2
- CME Euro FX specs: https://www.cmegroup.com/markets/fx/g10/euro-fx/specs

## Exact rule and two variants

Instrument: front-month 6E EUR/USD futures, $125,000 per full price point; tick 0.00005 = $6.25. One trade per weekday.

1. Use `Europe/London` timestamps converted per date to `America/Chicago`; never hard-code 10:00 CT.
2. At the close of the 16:03 London minute, compare that close with the 15:30 London close. Fade the sign: short if up,
   long if down; no trade if unchanged or either required observation is missing. Both sides use identical parameters.
3. Enter at the next minute's open (the bar closing 16:04 London), after the entire fixing window is observed.
4. Stop at 0.25 times the previous 15 stored weekdays' daily ATR, rounded UP to whole 6E ticks; no target.
   Stop anchoring and entry/exit slippage follow the repository's convention: raw next open anchors the stop and net
   prices absorb one tick per market/stop fill. Gap-through stops fill at the opening price, including the entry bar.
5. Variant A: exit at the 16:33 London minute close (30 minutes after decision).
6. Variant B: exit at the 17:03 London minute close (60 minutes after decision).
7. No overnight positions. On truncated sessions use the last available bar as a data fallback, report how often; all
   trades must finish before 15:59 CT. Missing decision data never get backfilled from a later observation.

No signal threshold, calendar subset, news filter, alternative stop, or separate side parameter will be optimized.
All endpoint-complete data-quality checks are fixed before P&L is inspected. Diagnose incomplete sessions explicitly.
Costs: $7.25 per 6E round trip plus 0.00005 slippage each on entry and exit ($19.75 total), with additional gap loss if any.

## Selection, holdout and decision

- Design: 2018-2022. Only design trade P&L and design placebos may select a variant.
- Rank by design Calmar. Select A unless B's design Calmar exceeds A by at least 10%; this favors the shorter exposure
  for near ties. Apply this rule mechanically even if both fail. Record selection before opening 2023 onward once.
- Design gate: net mean > 0, trade t >= 2, and both random-side and random-time placebo p <= 0.05. Random time uses
  the same dates, same stop, same 33-minute signal lookback and same holding horizon at a minute drawn uniformly from
  08:00-13:00 CT, excluding decision times within 90 minutes of the actual fix. Stops and exits are re-executed.
- Use 1,000 independently randomized paths for each placebo; precompute per-date/per-minute long and short returns
  with the existing execution walker to make exact re-execution feasible. Count them as controls, not optimized rules.
- A candidate must pass design, retain positive net and t >= 2 on holdout, beat both holdout placebos at p <= 0.05,
  and have a positive 5th-percentile holdout annual-net bootstrap estimate. Otherwise REJECT; partial statistical evidence
  with positive net is WATCH. Either outcome still gets funded addition/replacement evidence.
- Since <=3 variants have a stated ex-ante mechanism, the builder brief's preregistration exception is used. Also disclose
  t_threshold and deflated Sharpe against the repository trial count; no automatic promotion or live change.

## Account size, overlap and funded comparisons

Use the confirmed current roster including ES MOC 2 MES and RS longs 1 MNQ, with VB 2/1 and $1,500 cushion scaling.
Test the selected rule at one full 6E contract with ordinary integer cushion rounding: off when floor(1*f)=0. Do not
silently substitute fractional contracts or M6E fills. This makes the research size conservative in low-cushion states.

Choose the most-overlapping existing strategy by greatest absolute DESIGN daily-P&L correlation at its current size,
using the same design dates including zeros; break ties alphabetically. Fix the replacement slot before opening holdout.
Report timing overlap and correlation magnitude to avoid portraying a weak correlation as a shared mechanism.

Funded configurations (four): current; current + candidate; current minus overlap slot; current minus overlap slot +
candidate. Use 2,000 paired circular 20-day-block, 500-day histories for design and holdout with fixed seeds. Report mean
one-/two-year paid value, year-one and two-year blown, all-six-payout rate, median days to six (non-completers counted as
infinite), paired payout-difference mean confidence intervals and realized difference quantiles versus current and empty.
Candidate admission requires no lower mean one-/two-year paid value, no more than +1 pp year-one blown, and no slower
median six-payout time in BOTH periods. As replacement it must also beat the empty slot in both paid horizons.

## Required outputs

Report both variants' design metrics and the selected rule's full/design/holdout whole/long/short standard metrics,
trade count, win rate, native dollars per 6E (not per NQ), t, year-by-year sides, 5,000-sample daily holdout bootstrap
intervals, drawdown permutation and one-year/trade Monte Carlo at the actual 1-6E size. Report gross versus total costs,
both placebos, wrong-clock DST-mismatch diagnostic, candidate days filling the documented date-level gaps, and intraday
overlap with the chosen slot. An off-clock control is falsification evidence and will not become a traded variant.

New script: `analysis/codex_fx_fix_reversal.py` (extend existing execution/path tools in this file only where needed).
Output: `analysis/outputs/codex_fx_fix_reversal/`; report: `agents/codex/results/fx_fix_reversal.md`.
No MultiCharts code unless the idea passes and is independently reviewed. No live, broker, VPS or API changes.
