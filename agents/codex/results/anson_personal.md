# Anson personal-plan comparison: no useful place at the tested sizes

Summary: Replayed the intended4.5/20 rule and tested21 frozen personal allocations using5,000 paired histories.
Every1/2MNQ addition and1MNQ VB replacement lowers return/drawdown efficiency in both historical cohorts.
Full14 +1MNQ raises median yearly P&L$23,698→$25,614, but raises p95 drawdown$5,001→$6,077.
The20% drawdown capital budget increases$25,004→$30,387; keep the current personal ladder under this test.
Raw closure carries, unknown observation gaps and original-source validation concerns remain explicit.

Plan: `agents/codex/plans/anson_momentum.md`, commit`928c0ea`.
Script: `analysis/codex_anson_personal.py`. Output: `analysis/outputs/codex_anson/personal/`.
Baseline pin: `e34d71cd3537a9f019d2521e280fc92f3ffdb4c6`.
This comparison consumes the frozen intended_raw ledger; it does not tune the strategy or alter any plan.

## Baseline and accounting

The latest14 pieces include Twin's published16:00 daily marks, Overnight Anomaly and Dual Thrust.
The reconstructed full baseline matches every quoted published rounded number: annual$24,351, historicalDD$5,001,
one-year MC median$23,698 and p95DD$5,001. The five resampling statistics match the pinned MC routine to1e-8.

All2,059 raw trades remain, including1 cross-date trade,11 late fills and8 trades with unknown held-gap spans.
Those spans can include exchange closures that the limited calendar proxy does not identify; they are not proof
of feed loss. Raw source returns are conditional on the observed-bar fill proxy. Open positions mark at the last
observed close on the trading date at/before16:00, without a later-price fill. After16:00 wall-clock fills book to
the next plan session. Entry slip$0.50 is charged in its entry session; fee$1.275 plus exit slip$0.50 at exit.
The resulting daily net$18,951.775 reconciles exactly with all trades at$2.275 total cost perMNQ round trip.

Preserved published baseline limitations: plan pieces pay the extra$0.55 per nonzero day, undercharging VB reentries;
ES MOC's inherited commission is$1.05 rather than$1.275; Twin uses the committed checker ledger, not an exactv2.1
ledger, and its existing marking/cost convention remains unchanged. Candidate fees use exact trade counts.

## Portfolio results

All values below are uncapped personal-account P&L, with1 micro per baseline piece. MC uses5000 paired252-day
histories,20-day blocks and seed1. Capital is p95DD divided by20%, not a broker margin quote.

| Set | Base median P&L | +1MNQ median | Base p95DD | +1MNQ p95DD | Base capital | +1MNQ capital |
|---|---:|---:|---:|---:|---:|---:|
| A | $8,180 | $10,114 | $2,284 | $3,862 | $11,418 | $19,312 |
| B | $8,719 | $10,660 | $2,256 | $3,707 | $11,278 | $18,537 |
| C | $10,468 | $12,413 | $2,717 | $4,038 | $13,587 | $20,188 |
| D | $14,591 | $16,659 | $4,077 | $5,075 | $20,383 | $25,377 |
| Full14 | $23,698 | $25,614 | $5,001 | $6,077 | $25,004 | $30,387 |

Full14 return/DD (median profit divided by medianDD) falls8.25→7.10 with1MNQ and to5.57 with2MNQ.
Replacing VB with1MNQ produces median$23,946 but p95DD$5,673, capital$28,367 and return/DD7.07.
All additions and VB replacements likewise reduce efficiency in setsA-D and the2025+ cohort. At a continuously
equalised baseline p95DD budget, full14 +1MNQ median profit falls$2,622; this diagnostic scaling is not an executable
fractional-contract allocation. No new best size or ladder is selected. The CSVs retain all21 configurations.

For2025+ alone, full14 median P&L moves$42,399→$45,620 with1MNQ, p95DD$6,404→$7,550 and capital$32,018→$37,749;
return/DD falls10.51→9.47. This is already-seen historical replication, not a fresh sealed holdout.

## Uncertainty and standalone evidence

The full-history paired1MNQ profit contribution has a one-year5-95% distribution of−$2,299 to+$6,608,
median+$2,112;20.98% of paired histories have no positive contribution. For2025+ it is−$2,643 to+$10,046,
median+$3,553. Finite-history20-day-block95% intervals for the annualised mean contribution are$274..$3,904
on2018+ and−$1,937..$9,137 on2025+. Those broad historical intervals differ from the narrow uncertainty in a
mean calculated from5000 Monte Carlo draws, which measures simulation precision conditional on the input history.
An interval spanning zero alone does not establish overfitting; the actual risk/capital comparison rejects placement.

At personal costs, the raw strategy's design mean is$4.49/MNQ over1209 trades (t1.11); partial author-IS2018-24
has1686 trades,$7.87 average,t2.12;2023+ has850 trades,$15.91,t1.90;2025+ has373 trades,$15.24,t0.95.
By-year/long/short statistics are in`raw_personal_standalone.csv`; root strategy validation remains separate.

Personal MC uses daily marks and has no Apex limits or payout caps. It cannot certify intraday margin sufficiency
or complete tail risk across unknown gaps. Prior parameter searches and missing original author ledger/chart
properties remain unresolved. The independent peer review checked representative full saved simulation arrays,
allocation construction, marked cash totals and published baseline parity; it does not certify tick-level fills.

No live, broker, infrastructure, ranking or personal allocation was changed. Claude reviews/ranks; the user decides trades.
