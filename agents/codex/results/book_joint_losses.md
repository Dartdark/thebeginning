# Current evaluation book: WATCH — shared risk is concentrated in ONB continuation failures

Summary: The current seven-piece research book has seven income sources but little protection when ONB loses.
ONB contributes 87% of the loss on the worst 5% of days since 2023; all 49 of those days have multiple losing pieces.
ONB/Twin/DT/Noise positions are almost always in the same direction when they overlap.
However, only 38% of first $2,000 close-marked loss crossings have multiple positions still open: much of the loss is sequential.
The research gap is early protection against failed continuation in either direction, not another similar NQ momentum entry.

Plan: `agents/codex/plans/book_joint_losses.md`, d8101e98.
Primary script: `analysis/codex_book_joint_losses.py`; initial run 18edc570, market-label correction 9fe520c4.
Detail script: `analysis/codex_book_joint_loss_detail.py`, b1774be4.
Independent arithmetic script: `analysis/codex_book_joint_loss_checks.py`, 9fe520c4.
Outputs: `analysis/outputs/codex_book_joint_losses/`. Strategy trials: **0** (descriptive audit; no rule or sizing selection).

## Book and dates

Frozen from source branch commit a5aeffec, `bench150.LIVE_EVAL`:

| Piece | Size |
|---|---:|
| ONB30 | $3,500 stop-risk sizing |
| Monday Bridge | 5 MNQ |
| Twin | 2 MNQ |
| Dual Thrust | 2 MNQ |
| Jump Fade | 1 MNQ |
| Noise longs | 3 MNQ |
| Late-Day Flow | $1,000 stop-risk sizing |

This replaces the stale six-piece roster discussed earlier. EOS and VB are absent.
Dates: **2018-03-01 through 2026-10-12**, 2,221 trading dates, 7,619 trades.
Start avoids assuming coverage before the Bridge report begins; endpoint uses the earliest report's full-day export coverage,
not its last trade. 2018-22: 1,247 dates; 2023+: 974 dates.
The 2023+ observations are descriptive reuse of well-seen data, not an untouched holdout.

This is the hypothetical continuous stream of the current signals at current risk settings, **without account liquidation,
the daily stop, evaluation target, payouts or restarting accounts**. Dollar drawdowns below are not losses a surviving
evaluation could necessarily experience. A strategy can contribute to raw losses and still help the race to the target.
This audit does not overturn the existing sizing or contribution benches.

## 1. Worst days: ONB sets the scale, other pieces usually add losses

Each period's tail is the worst ceil(5% of dates) by total realized daily P&L.

| Average contribution on a worst-5% day | 2018-22 | 2023+ |
|---|---:|---:|
| ONB | -$3,557 | -$3,464 |
| Monday Bridge | -$36 | -$54 |
| Twin | -$92 | -$95 |
| DT | -$116 | -$164 |
| JF | -$5 | -$13 |
| Noise longs | -$59 | -$117 |
| LDF | -$135 | -$91 |
| **Book** | **-$4,000** | **-$3,996** |

Since 2023, ONB is negative on **49/49** tail dates and accounts for **86.7%** of their net losses.
Every one has >=2 losing pieces; **40/49** have >=3. Across all years: 112/112 and 93/112 respectively.
Winners offset only $3,373 of $199,187 gross losses on recent tail days (**1.7%**); all-years offset is 1.0%.
The ONB-tail contribution's joint 20-day block-bootstrap 90% band is [-$3,485, -$3,432].
JF's [-$31, +$11] band includes zero; its low average correlation is not evidence of dependable tail protection.
All tail contributions, 1% tails and bands are in `tails.csv` and `tail_bands.csv`.

This concentration is partly mechanical: ONB's risk allocation is much larger. It also supplies about 70% of full-period
net signal profit. Do not infer from the tail table alone that cutting ONB improves pass probability.

## 2. Pairs that lose together

On dates when both pieces traded, recent conditional losses are substantially worse than average for the continuation cluster:

| Pair (2023+) | Both traded | Both lost | Independence reference | P(second loses given ONB loses) | Second's baseline loss rate |
|---|---:|---:|---:|---:|---:|
| ONB + DT | 240 | 86 | 61 | 78.2% | 55.4% |
| ONB + Noise longs | 136 | 41 | 26 | 70.7% | 45.6% |
| ONB + Twin | 187 | 47 | 36 | 57.3% | 43.3% |

The same ordering is visible in 2018-22: ONB/DT 93 joint losses vs 62 under the independence reference;
ONB/Noise 37 vs 26; ONB/Twin 70 vs 48. The reference uses loss frequencies among the same both-active dates.
Twin/DT is also a cluster: recent 116 joint-loss dates vs 92 expected, correlation +0.24.

The first three recent daily correlations are only +0.27, +0.27 and +0.37. Low-to-moderate whole-day correlations
can therefore understate the concentration of conditional losses.

The within-year/weekday independent P&L permutations give a recent worst-5% mean of -$3,829 at the median
(90% range -$3,940 to -$3,737), vs actual -$3,996. Only 9/1,000 permutations are as bad or worse.
Recent >=3-loss dates: actual 116 vs null median 94 (90% range 83-106; none of 1,000 reaches 116).
There is **not** an excess of all >=2-loss days: actual 336 vs null median 349. The issue is heavier loss clustering,
not a blanket claim that every measure of dependence is elevated.
These permutations preserve each piece's year/weekday distribution but break serial and shared-market dependence;
they are a diagnostic reference, not a strategy placebo or proof of a causal mechanism.

## 3. Overlap is largely the same directional bet

Actual minute intervals, 2023+; a trade's entry and exit minute both count as occupied:

| Pair | Overlapping minutes | Same direction | Fraction of ONB's live minutes overlapping |
|---|---:|---:|---:|
| ONB + Twin | 19,560 | 100% | 33.5% |
| ONB + DT | 14,729 | 99.99% | 25.2% |
| ONB + Noise longs | 13,985 | 100% | 23.9% |

The same-side pattern is also present in 2018-22 (ONB/Twin and ONB/Noise 100%, ONB/DT 98.1%).
These counts were independently reproduced by intersecting trade intervals instead of the dense position-grid method.
Overlap percentages are pairwise and must not be added: all three can overlap ONB simultaneously.

JF is usually opposite ONB when both are open (2,137 of 2,270 overlapping minutes), but overlap covers just
**3.9%** of ONB's minutes. A different entry direction by itself does not give the book a persistent hedge.
Bridge and LDF have near-zero/low daily correlation with ONB (-0.005 and +0.092), so they diversify ordinary P&L;
they are not reliable loss offsets on ONB's tail days.

## 4. Loss timing: earlier protection matters more than a late recovery

Mark every open piece at the **same NQ close** each minute, with round-trip costs charged at entry.
Do not sum each long's low and each short's high and call that one realizable portfolio mark.

On the recent sample there are **168 calendar dates** with a first close-marked crossing of -$2,000 from that day's
opening mark. At that instant:

- ONB is open and losing in **163/168 (97.0%)** cases.
- Multiple pieces are open in **63/168 (37.5%)** cases; >=3 are open in 19.
- Multiple pieces have negative contributions, including closed trades, in **122/168 (72.6%)** cases.
- First crossings occur in 09:00-10:59 CT in **96/168 (57.1%)** cases.

Thus a cap that applies only when two positions overlap would miss most crossing instants.
At each recent tail day's worst marked minute, 59.3% of the negative contribution is already from closed trades.
Risk accumulates sequentially as well as concurrently. A profitable trade much later in the day is not necessarily useful
to an account already stopped earlier.

This crossing check does **not** liquidate anything, simulate execution at the threshold, or estimate evaluation failure rates.
It uses calendar-day opening equity; the true exchange-session tail check separately covers 17:00-16:00 CT.
Session tails are nearly unchanged: recent mean -$3,992, ONB -$3,464, all 49 dates with >=2 losers.
Intraminute losses can precede close-marked crossings, so the counts are not exact live DLL triggers.

## 5. Drawdown episodes and market behavior

Largest nonoverlapping recent peak-to-trough signal-stream drawdowns:

| Start to trough | Book loss | ONB contribution | Other contributions combined |
|---|---:|---:|---:|
| 2024-01-09 to 2024-02-15 (28 trading dates) | -$19,513 | -$15,876 | -$3,637 |
| 2023-07-06 to 2023-08-18 (32) | -$18,417 | -$19,113 | +$695 |
| 2025-11-07 to 2026-01-15 (48) | -$17,516 | -$14,611 | -$2,906 |

The worst full-sample drawdown is $33,519, not an account-survival claim. Existing metrics, annual results,
long/short splits and joint block-bootstrap metrics are saved in `metrics.csv`, `yearly.csv`, and `book_bootstrap_*.csv`.
Recent raw book Sharpe is 2.40, with 90% block-bootstrap band [1.84, 3.17]; good average performance coexists with the tail concentration.

The bad days do not all look like equity crashes. ONB's 49 recent tail trades include **22 longs and 27 shorts**.
The median absolute 08:31-15:00 move is 80.25 points on those dates, vs 117.5 across all recent dates.
Median intraday range/lagged ATR is 0.79 vs 0.75. This is descriptive evidence consistent with failed continuation
and reversals as well as trends, not proof of one tradeable whipsaw regime. A permanent short hedge would not directly
address a book that loses on both long and short continuation attempts.

## Where the book needs help

1. **The ONB loss state, early enough to matter.** New research should demonstrate an independent positive contribution
   during ONB failures in both directions, especially before the morning loss budget is used. Mere low daily correlation
   or later profits are insufficient. This describes a requirement, not an available proven hedge.
2. **The continuation cluster.** Another entry with the same sign and holding window as ONB/Twin/DT/Noise is unlikely
   to provide the specific diversification missing here. It may still earn money, but must be evaluated as additional shared risk.
3. **Cumulative loss plus open exposure.** If testing a book-level rule later, consider already-realized losses as well as
   current same-side exposure. Earlier cushion-cap tests and sizing tests already had tradeoffs; this report does not establish a better rule.

No strategy is removed or resized by this report. No hedge, skip filter, account simulator or new engine was optimized.

## Accounting limitations and validation

- **Noise cost omission in the shared base:** NBL's saved CSV prices are raw, and bench150's NBL path charges $7.25/NQ
  but no extra tick slippage. We matched it for the main comparison, then applied the standard entry/exit ticks separately.
  Recent tail mean changes only from -$3,996 to -$3,999; the diagnosis survives. Flag for Claude's benchmark review.
- **Historical risk sizing vs monitoring thresholds:** the benchmark/code risk formula has no quantity cap; historically
  ONB reaches 110 MNQ and LDF 32, above expected_setup's monitoring ceilings 25 and 6 (358 and 543 historical trades).
  Those ceilings are not enforced by these strategy files. This is a convention mismatch to review, not an assertion
  that today's charts traded those quantities. We did not invent a cap or silently change the base.
- **Missing price minutes:** 1,395 trade-minutes lack an observed raw close and use the previous observed close, mostly
  after 15:15 on Bridge/Twin trades. Core daily totals use exported/simulated exit prices. Exact intraday extrema are not known.
  No forward-filled mark is treated as evidence that no adverse price move happened during that gap.
- **Clock conventions:** resolved 5/15-minute MC fills still have intrabar ambiguity. Bridge entry uses its report's
  Sunday 19:00 stamp; early targets retain the report stamp. Twin uses simulated actual calendar intervals, not its benchmark's
  synthetic exit-day placement. Minute overlap includes fills at the boundaries; it is not tick-level execution reconstruction.
- **Close marking vs exit booking:** 26 dates differ (max $239.55) due to cross-midnight open Twin marks. Both daily series
  are saved. The session-clock tail sensitivity leaves the conclusion intact.
- **Verified:** all cached observed closes match raw NQ CSVs for 2018-26; all trade costs reconcile independently;
  all trade/daily totals and tail contributions reconcile; ONB/Twin/DT/Noise overlaps match independent interval intersections;
  all 363 first-crossing rows' positions reconcile to the ledger. Source hashes and exact code references are in `provenance.json`.
- **Not verified:** the audit has not had an external independent checker, is not a fresh forward test, and has not simulated
  changed allocations through the actual evaluation/funded rules. Neither causality nor profitability of any proposed protection is established.

## Reproduce

Run from the checked-out repository root (Python 3.11, numpy/pandas/scipy/openpyxl/matplotlib):

```
python analysis/codex_book_joint_losses.py --grid C:/TradingVault/scratch_data/g24.pkl
python analysis/codex_book_joint_loss_detail.py C:/TradingVault/scratch_data/g24.pkl
python analysis/codex_book_joint_loss_checks.py
```

The provided grid is read only. Shared modules' import-time cache arguments are redirected into the audit output's
`_cache` folder. Large caches are not committed. No live code, strategy inputs, VPS file or broker setting was changed.
