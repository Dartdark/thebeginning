# Resting liquidity entry on frozen pressure events: TEST an execution extension

Summary: Market-entry residual and monthly payoff-model batches failed; all6 definitions remain counted.
Test the materially changed liquidity role using resting limits on UNCHANGED frozen RESID2 events.
No threshold/side/stop retuning, averaging, price improvement or future-fill-conditioned market control.
Native minute OHLC can support a conservative conditional fill study, not proof of native queue priority.
Three more definitions; no real outcomes for this execution extension at this checkpoint.

Sources: uploaded2003impact/liquidity paper and review; original events atc852212a, batch1_design_qa2/RESID2_signals.csv.gz.

## Mechanism, clock and transmission

Liquidity replenishment may pay differently when quoting a resting price instead of crossing after confirmation.
This is an explicitly related execution extension of a failed signal, not a new independent factor. A negative gross
market-entry signal cannot be repaired merely by removing entry slippage; changed execution/selection must earn positive
gross and net outcomes. Adverse selection is likely: a limit can fill exactly when the earlier repair fails.
Quotes/stops/targets are frozen from closed NQ bars; activation waits5fullminutes. Pending orders and held positions
occupy the single slot. NQ tape maps to separately costed MNQproxy, not verified native microquotes.

## Feasibility, costs and power

Use the same hashed native2018–22 tape and fixed eventfile; no missing-minute fill. Limit orders need1NQpointthrough,
stopfirst ambiguous paths and worse gaps. No maker rebate or favorableprice improvement. Target fills in the entryminute
require ordering evidence; a closing trade through the target certifies that opportunity only with an immediate bracket.
Native acceptance/partial fills/queue and receipt remain unknown. Fullfees and entry-coststress must be positive.
Original eventcount beforeorderguards is fixed; actualsubmissions/fills saved. Fewer150filledtrades fails basicpowergate.
Outcome rows cluster; dailyNW and year/side evidence remain necessary. Highhit rate is not a source result.

## Failure and book role

Trend continuation, informed repricing, illiquidity and latency can turn repeatedsmall wins into full losses. No
independent diversification or VBtail offset is assumed. Quotes can remain unfilled on a winning move and fill on a
losing one; do not exclude that selection cost. Missing active/pending prices mean unknownexposure, not nofill or zero.
All prior rawflow/absorption/jump/learning failures remain counted. No positive account claims before earned replay.

Decision: **TEST only after committed plan/code**, with conditionalbarfill limits. No live quotes/orders or settings.
