# Current evaluation book: shared-loss diagnostic

Frozen 2026-11-13, before calculating results. Source book: `bench150.LIVE_EVAL`
at source commit a5aeffec; ONB $3,500 risk, MON_BR 5 MNQ, TWIN 2, DT 2,
JF 1, NBL 3, LDF $1,000 risk. Verify this against expected_setup.json.

This is a descriptive portfolio audit, not a strategy/filter search. No new
entries, exits, size variants, trading changes, or promotion decisions. Zero
strategy trials. The historical book is hypothetical at today's fixed sizes.

## Questions and fixed definitions

1. Which pairs lose together? Daily Pearson correlation, both-active loss
   counts, conditional loss probabilities vs the both-active independence
   reference; aggregate days with >=2 and >=3 losing pieces.
2. What causes the book's losses? Fixed worst 5% and 1% of days, each piece's
   signed contribution, gross losses offset by winners, and worst 10 distinct
   peak-to-trough drawdown episodes. Separate 2018-22 and 2023+ descriptions;
   these are not fresh holdouts or validation of a predictive rule.
3. When do risks coincide? Actual minute positions by strategy and side,
   same-side vs opposed overlap, hourly exposure and hourly mark-to-market
   losses. Report concurrent losses at the worst close-marked minute each day.
4. What market behavior accompanies stress? Ex-post RTH direction, opening
   hour direction and range/ATR on tail days. No conditioning an entry on
   that day's outcome; these labels are diagnostic only.

## Data and safeguards

Use existing loaders/simulators for every current piece. Portfolio metadata
comes from the latest shared research branch; do not use stale legacy bases.
Use g24.pkl read-only from C:/TradingVault/scratch_data and verify date coverage
against underlying NQ CSV files. Avoid calling bench150.setup's unrelated
funded-book build. Reproduce its evaluation trade sources and risk multipliers.
Set the common cutoff from export coverage, not each strategy's last trade.
Use a conservative common endpoint no later than the earliest report's export
coverage or raw NQ coverage. Report data provenance, omitted records and gaps.

Daily realized P&L is booked on exit trading date, Sunday into Monday. For
intraday overlap use actual entries/exits (including Sunday evening and Twin
cross-midnight holdings), NOT the bench's synthetic exit-day placement.
Build close-marked equity using a single shared price per minute. The sum of
each side's adverse high/low is not a simultaneously realizable portfolio
price; don't use that for correlation, timing or hedge-benefit claims.
Full round-trip costs charged at entry in close-marked paths, final actual
net P&L substituted at exits. Trade timestamps on 5/15-min MC exports are
resolved by existing minute loader, with coarse-bar uncertainty disclosed.

Uncertainty: 2,000 joint 20-day block-bootstrap draws for tail contributions;
1,000 independent within-year/weekday P&L permutations as a descriptive
dependence reference for joint losses and book expected shortfall (breaks
serial dependence; not a trading-rule placebo). Use existing metrics and
resampling utilities where applicable. Summaries for whole/long/short and
by year. Verify trade/daily reconciliation, common-price cancellation,
position reconstruction and accounting across date boundaries.

## Decision

Rank vulnerabilities by magnitude, persistence across periods and sample size.
Translate them into requirements for FUTURE research, not inferred profitable
hedges or advice to remove/reweight a strategy. A new engine or risk rule
would require its own evidence sheet, preregistration and account-level tests.
