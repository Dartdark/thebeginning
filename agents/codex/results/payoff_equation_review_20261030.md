# Veles payoff-equation note: useful risk reference; no new strategy

Summary: The win-rate/payoff arithmetic is correct under its stated two-outcome assumptions.
At 20% wins and 5x average-win/average-loss, expectancy is +0.20 average-loss units before additional costs.
This is an educational identity, not evidence of an executable Jones/Medallion strategy or a new futures signal.
Higher payoff ratios do not automatically improve expectancy; 50 closed trades do not establish a stable edge.
Retain the execution/risk lesson; no return test, account placement, exit change or promising-strategy queue entry.

Source: two user-supplied screenshots of **Wrong 80% of the Time and Still Winning: Paul Tudor Jones and the Payoff
Equation**, displayed author Veles, Independent Research, @velesxbt. Both pages' visible text and tables were read.
Original PDF URL, publication date/revision, DOI and peer-reviewed venue were not verified; indexed title/author
searches did not identify a canonical PDF. This is a screenshot-based note review, not authenticated original-PDF access.
[Source observations](../inputs/payoff_equation_20261030/source_observations.json),
[access/citation receipt](../inputs/payoff_equation_20261030/source_access.json).
Script: [deterministic checks](../../../analysis/codex_payoff_equation_20261030.py).
[Outputs](../../../analysis/outputs/codex_payoff_equation_20261030/math_checks.json).
New economic hypotheses/return trials/account simulations: **zero**. Scout budget and earlier trial history unchanged.

## Four questions

1. **What is it about?** Profitability depends jointly on how often trades win and the realized average size of
   winners relative to losers. The note contrasts a hypothetical retail pattern, a reported Medallion hit rate
   with assumed equal payoffs, and a Jones five-to-one risk/reward illustration. It also discusses the disposition
   effect and suggests measuring recent trade outcomes.
2. **What does it find?** Algebraically, 20% wins at a realized 5:1 payoff ratio has positive expectancy, while 60%
   wins at 0.5:1 loses before additional costs. Those calculations independently check out. The note contains no
   newly tested market signal or trade dataset. The Jones/Medallion quotes are not independently verified realized
   win/payoff records. Its Odean citation is supported by the primary paper's reported realization proportions;
   that empirical study was not independently rerun here.
3. **Why does it make money, if it does?** A sufficiently large realized average win can outweigh more frequent
   average losses. That explains an outcome distribution's positive mean, not why a particular entry/exit rule
   achieves that distribution after costs. A distant target alone does not produce that edge; it can lower win
   probability, extend exposure, increase missed fills or alter the loss distribution.
4. **Can we build on it?** Yes as a diagnostic/reference for a separately justified strategy. No new standalone
   strategy, deeper alpha investigation or current-account addition is warranted from this note. Keep realized
   net expectancy, concentration, sequencing, open losses and account fit in the normal workflow. Do not alter
   current exits for a month merely because the author's suggestion appears in the screenshots.

## What was independently checked

Let `p` be the fraction of wins, `W` the realized average winner and `L>0` the magnitude of the realized average
loser, measured consistently on the same closed-trade set. With only wins and losses:

\[
E=pW-(1-p)L,\qquad R=W/L,\qquad E/L=pR-(1-p).
\]

The break-even win fraction is `1/(1+R)` when the inputs include all relevant costs, or when no additional cost
is modeled. `E/L` is normalized by the realized average loss. It is not automatically profit per dollar of initial
stop risk, margin, invested capital or account equity. The realized average loss need not equal the planned stop.

| Illustrative row in the note | Win fraction | Average win/loss ratio | Expectancy per average-loss unit |
|---|---:|---:|---:|
| Retail illustration |60%|0.5|−0.100|
| Reported Medallion hit rate, equal-payoff assumption |50.75%|1.0|+0.015|
| Jones risk/reward illustration |20%|5.0|+0.200|

| Realized payoff ratio | Break-even win rate |
|---:|---:|
|0.5|66.67%|
|1|50.00%|
|2|33.33%|
|3|25.00%|
|5|16.67%|

These are mathematical examples, not independently observed fund performance or futures backtests.

## Costs, zeros and risk units

For gross winners/losers and average execution/fee cost `c` per trade:

\[
E_{net}=pW-(1-p)L-c,\qquad p_{BE}=\frac{L+c}{W+L}.
\]

Constructed example: gross average win $500, average loss $100, 20% wins and $5 average cost gives $20 gross
expectancy, **$15 net per trade**, and a 17.5% break-even win rate. This is illustrative arithmetic, not an assumed
MNQ execution model. If wins, losses and win fraction were already calculated from net-after-cost outcomes,
do not subtract the same costs again. If costs change which trades are wins/losses, recalculate that net classification.

Exact-zero outcomes require `E=p_win W-p_loss L`, with their own zero-probability mass; treating every nonwinner
as an average loser changes the identity. Record all closed trades, quantities, fees and genuine flat outcomes.
Use dollar outcomes at executable size. An average of individually normalized trade R-multiples is not necessarily
the same as expectancy normalized by the aggregate average realized dollar loss.

## Two recommendations need qualification

- **A higher payoff ratio with a slightly lower win rate is not automatically better.** With the same average
  loss magnitude, changing from 60% wins/R 1.0 to 55% wins/R 1.1 lowers normalized expectancy from 0.200 to 0.155.
  This deterministic counterexample disproves a general rule; it does not identify preferred market settings.
- **R below one is not itself a problem.** At 75% wins and R 0.5, normalized expectancy is +0.125. Lowering a target
  or taking partial profits can be useful in some strategies and harmful in others; assess the complete rule,
  removed opportunities, costs and account outcomes under a committed plan. No exit experiment was started.

## Fifty trades and low win rates

The note's last 50 closed-trade exercise is useful for describing a recent sample, not proving future expectancy.
In an invented IID example, 10 wins in 50 trades gives a 95% Wilson interval for the win fraction of approximately
**11.2%–33.0%**. Even assuming the 5x payoff is known and fixed, that interval includes the 16.7% break-even rate.
Real payoff estimates, dependence, regime changes and rare winners add uncertainty; this calculation is not a
power analysis for a specific futures candidate.

With 20% IID wins, a specified five-trade block contains five losses with probability 32.768%. This is **not** the
probability of at least one such streak anywhere in a longer history. Positive mean expectancy does not prevent
drawdown breaches before the next large winner. Closed-trade ratios also cannot hide open losing positions:
reconcile daily marks, realized cash, costs and unfinished exposures.

The repo already distinguishes these questions. TIER_LIST's Morning Momentum tight-stop study reported 29% wins
and PF 2.00, yet did not earn an Apex addition after sizing/account tests. That is existing repository evidence,
not a new test or independently repeated result here. Do not reopen its exit family based on this note.

## Citation and evidence check

Odean's author-hosted [1998 paper](https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/areinvestorsreluctant.pdf)
reports 10,000 discount-brokerage accounts from 1987–1993. Table I gives aggregate proportion of gains realized 0.148
versus losses realized 0.098, a ratio of about 1.51. These proportions use realized plus unrealized positions as
denominators; they are not a 60% trade win rate or a 0.5 payoff estimate. The reported evidence supports a disposition
effect in that historical sample, not an ES/NQ trading signal or a universal prescription to hold every winner.
Only the relevant primary definitions/table were checked; no brokerage data were obtained or empirical model rerun.

The note cites Robbins 2014 for Jones and Zuckerman 2019 for Medallion. The screenshots provide no supporting
closed-trade ledger, sample dates, costs, fill rules, payoff distribution or uncertainty estimate for either fund.
The five-to-one rule is not proof of a realized 5x average payoff; the equal-payoff Medallion row is explicitly an
illustration. Their precise realized statistics and attribution remain unverified in this review.

## Placement and retained reference

No standalone slot is established in 50K/150K evaluation, 50K/150K funded or personal. The useful lesson supports
research/account diagnostics for all five homes, but none received a new BASE/ADD/REPLACE/EMPTY test or allocation.
No promising unverified strategy is added to TODO: this note supplies no specific independent signal or mechanism.
No author suggestion inside the screenshots was treated as a user instruction to change strategy settings.

Retained in [EXECUTION_REFERENCES E37](../EXECUTION_REFERENCES.md#e37--realized-payoff-expectancy-costs-and-account-survival).
Smallest future application: when a separately specified candidate is eligible, calculate realized net win fraction,
average win/loss, cost bridge and concentration from its frozen ledger; then use its chronological account path.
The arithmetic check is complete. No additional strategy investigation is warranted from this note alone.
For Claude: `agents/codex/results/payoff_equation_review_20261030.md`.
