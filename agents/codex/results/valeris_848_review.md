# Valeris 848: REJECT for plan promotion on the supplied evidence

Summary: I would keep the current plan; Valeris has not demonstrated an improvement to it.
The author reports positive historical results, but selection followed visible OOS results and 2,429,305 combinations in this run.
Reported OOS t-statistics fail both author gates; one-MNQ drawdown is about $2,030 before our higher research-cost convention.
The supplied source differs from the report's stated defaults, and current-version MNQ confirmation and paired account comparisons are absent.
This rejects promotion now, not the possibility of a future edge; no new strategy returns or live changes were made.

Scope: `agents/codex/plans/valeris_848_source_review.md` (review record, not a preregistered backtest).
Evidence: `agents/codex/evidence/valeris_848.md` (NEEDS DATA).
Script: `analysis/codex_valeris_848_review.py`; outputs: `analysis/outputs/codex_valeris_848_review/`.
Inputs: `agents/codex/inputs/valeris_848/{source.txt,report.pdf,report_extracted.txt}` (unchanged originals archived; SHA-256 in output).
New strategy-return trials / account simulations: **0 / 0**. Author-reported trials are disclosed below, not independently audited.
Context: Codex `1bab29f05d57da9801b700a163de1e1e3d2ffb36`; latest Claude `b1256664232722b25afefc0004e6f9e04c1976ae`.

## Rule and positive evidence

On five-minute full-session NQ/MNQ bars, follow the 08:35 CT close versus the 08:30 close when signed distance from
Supertrend exceeds the threshold. Stop distance is yesterday's regular-session ADR times the stop input; a favorable move
arms a next-bar break-even stop. The base exits at 15:00; same-side reentries cross a level based on yesterday's close and
ATR and finish later that afternoon. Size is optionally inverse square-root volatility with integer rounding and minimum one.

The first-candle direction resembles the cited paper's simplified ORB; absence of an opening-high/low breakout is not itself
a paper mismatch. But the Supertrend filter, reentries, ADR exits and sizing are an optimized adaptation, not independent
confirmation of the original QQQ/TQQQ result. The paper's main specification uses the next candle's open, the first candle's
opposite extreme as stop and a 10R/close exit; its later sensitivity section also examines ATR exits. The report's no-stop
"raw paper" baseline is therefore not a literal replication of the paper's main rule.
[Primary paper, pp. 4-6 and 13](https://concretumgroup.com/wp-content/uploads/2026/02/Can-Day-Trading-Really-Be-Profitable.pdf).

There is useful positive evidence: profits persisted in both reported validation periods; the author reports development
execution/cost stresses and old-version MultiCharts parity. The code uses prior-session daily volatility, per-contract dollar
stops and holiday/half-day entry exclusions. Static inspection found no obvious future-day volatility leak. These findings
justify taking the candidate seriously enough to review, but do not establish current-plan value.

## Why the evidence does not clear the plan's gates

1. **Selection and testing are not independent.** PDF pp. 1, 15-16 disclose 2,429,305 combinations for this run,
   9,750,858 across the paper and selection from three finalists after both OOS periods were visible. The long-only
   choice also followed visible results. Correlated combinations are not necessarily independent trials, but their
   scale plus explicit post-selection prevents treating the selected t-statistic as a fresh confirmatory test.
   The author's protocol did not admit the strategy; DSR/PBO/grid checks are marked uncomputed, not passed.
2. **It failed the reported OOS gates.** Dynamic-size OOS 1 t = 1.75 versus 1.96; OOS 2 t = 2.25 versus 3.92.
   The latest repository promotion rule additionally needs its multiple-testing t-bar AND DSR >= 0.95, independent
   checker PASS without open concerns, current-version confirmation and an account-bench gain. None is established here.
3. **Risk is material at minimum size.** PDF p. 23 reports fixed one-MNQ drawdown $2,030, or $2,041 with rounded stops.
   That exceeds the nominal $2,000 trail. It is a serious sizing concern, not proof that every account would fail:
   exact breach risk depends on starting cushion, the trail's lock, withdrawals and the intraday path. A closed-trade
   drawdown cannot replace the required chronological account simulation. The PDF's standalone simulations are not ours.
4. **Long-only is not a validated repair.** It shows lower reported drawdown ($1,484) but was selected after inspecting
   the same history; OOS 1 dynamic-size t is only 0.94. Do not turn off shorts merely because they caused the latest drawdown.
5. **Development stress is not new validation.** The reported cost/delay tests are on the selection period. Neighbor
   stability and a long backtest do not undo selection. Rolling chain reselection found no finalist in any window (p. 18).

## Reported results and cost reconciliation

These are **author-reported**, not reproduced trades. The fixed one-MNQ table (PDF p. 8) uses $0.725 total cost per trade:

| Period | Trades | Net | PF | Trade t | Max DD |
|---|---:|---:|---:|---:|---:|
| Development, 2017 to October 2022 | 1,446 | $23,655 | 1.69 | 5.09 | $959 |
| OOS 1, late 2022 through 2023 | 302 | $4,119 | 1.41 | 1.75 | $832 |
| OOS 2, 2024 to September 2026 | 706 | $10,401 | 1.30 | 2.06 | $2,030 |
| Combined OOS | 1,008 | $14,519 | 1.33 | 2.61 | $2,030 |

Whole/long/short combined OOS net on fixed one MNQ is $14,519 / $9,538 / $4,981 across 1,008 / 509 / 499 trades.
These periods differ from our prescribed design/validation split. Full long/short yearly risk metrics, Sharpe, Sortino,
Calmar, Ulcer, daily bootstrap intervals and plan correlation cannot be independently computed from aggregate tables.
No missing metric is treated as zero or inferred from PF or t.

For this candidate, reported exits are market time exits or stop/break-even exits, with no target fills. The repo convention
is ($7.25 + two $5 slippage ticks) / 10 = **$1.725 per MNQ**, against the report's **$0.725**. Simple arithmetic on the
rounded published totals adds $1 per trade: combined OOS would be approximately **$13,511, $13.40/trade**, before any
further source-level rounding or actual micro-fee correction. The report's rounded-stop total would be approximately
**$13,326**. This does not independently validate the edge or recompute t, PF, drawdown or account probabilities.
Scaled NQ fees remain a research convention; actual micro fees still need reconciliation.

Reentries contribute only $962 over 315 OOS trades at the report's costs (p. 9), approximately **$647, $2.05/trade** at
our convention. That is thin execution margin. It is evidence to investigate, not permission to choose a no-reentry
variant after seeing results. The $1 difference between separately rounded base/reentry totals and total net is immaterial rounding.

## Exact code/report differences and execution limits

- **Actual delivered inputs differ:** source lines 156-160 set `ArrotondaStop=0` and `OraChiusuraLucid=0`, while PDF
  p. 6 describes 1 and 1545 as shipped settings. Source line 127 also defaults dynamic sizing on; prop simulations use
  fixed size. The report's observed weight range would still round a base of one micro to one, but larger bases/future
  volatility need actual integer sizing. Pin exact inputs before parity work; no source edits were made here.
- **Current-version parity is open:** PDF p. 7 says the older verification copy matched the OOS ledger; it also explicitly
  says the version with `Lato` has not been recompiled. No original trade list, emulator, registry or MC report accompanies
  the PDF. Reported prior parity is encouraging, not independent verification of this delivered source on MNQ.
- **Close fills need executable evidence:** lines 500-501, 527-528 and 551-552 generate close orders after a completed
  close is needed. MultiCharts supports them; they are not automatically invalid or backtest-only. But the decision,
  order submission and broker fill occur in sequence, so matching the historical close is an assumption.
  [MultiCharts lifecycle documentation](https://www.multicharts.com/trading-software/index.php?title=How_Scripts_Work).
- **Do not claim an unprotected entry bar:** the unconditional per-contract `SetStopLoss` at lines 583-585 can operate
  intrabar, including the entry bar, even with ordinary close-based signal evaluation. IOG off alone does not recreate
  the older VB defect. [Official SetStopLoss documentation](https://www.multicharts.com/trading-software/index.php?title=SetStopLoss).
- **Raw-roll sensitivity is intentional but consequential:** the requested raw series/roll schedule reaches ATR,
  Supertrend and previous-close reentry levels. Regular-session high-low ADR does not directly include a pure overnight
  additive jump if the whole next RTH session uses the new contract. Do not assume adjusting terminal P&L repairs different
  signals, or silently replace the frozen raw-data specification with adjusted indicators.

## Against the current plan

The report does **not** test this strategy next to our plan, as a replacement, or against leaving the slot empty. Its
last-page reference to another person's seven-strategy pack is not evidence about our current ten-strategy funded plan.
Its first-payout objective and account settings also differ from our six-payout bench. Treat its prop rules as historical
model assumptions, not verified current broker rules.

Latest saved current-plan benchmark at Claude `b125666` (`analysis/outputs/replace_weak_bench_output.txt`): funded
paired histories report $9,354 at one year, $12,088 at two years, 7.0% blown and 259 median days to six payouts; the
separate evaluation benchmark reports 50.1% pass. These are context, not a head-to-head Valeris comparison. In particular,
do not subtract the PDF's 36.2% pass-within-30-calendar-days from our 50.1% with different histories/horizon/model.

Its 08:35 opening-direction signal and afternoon reentries potentially share NQ exposure with ONB, RS, VB and LDF.
That is a timing/factor concern, not measured correlation. A trend-day payoff also does not prove it will protect the
account before other losses breach a limit. The exact paper family and adjacent ORBs have already been tested in
`TIER_LIST.md`; those prior results do not establish this adaptation's profitability either way.

## Decision, remaining evidence and review limits

**Keep the plan. Do not add Valeris or replace an existing leg on this evidence.** I am not ranking it for Claude or
claiming it is inherently unprofitable. Promotion is rejected because the necessary evidence is missing and the supplied
report itself fails its stated validation gates.

The smallest useful next evidence is the original timestamped trade/daily ledger and exact data/roll/input provenance,
plus the current-source MNQ confirmation export. These allow a source/account reconciliation before considering new
returns. Any later replication must be separately registered before returns, preserve all eligible events, count variants,
and use declared fees. Only a candidate clearing independent checks should advance to the paired current-plan,
addition, replacement and empty-slot account bench with intraday risk paths. Forward logging remains discretionary;
the PDF's proposed live/forward rules were not adopted or started.

Validation here: PDF text and relevant rendered tables checked; source defaults and page tokens checked by the committed
script; two independent read-only subreviews checked code and latest plan context. This is not the repository's independent
strategy-checker PASS. No new price-based returns, simulations, code fixes, trading-plan edits, live setup or PR #2 actions.
