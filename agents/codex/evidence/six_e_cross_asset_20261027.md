# 6E cross-asset package v4: NEEDS DATA

Summary: Potential personal-account diversifier, based on the author's reported results only.
The supplied note is insufficient to reproduce signals, executable integer M6E sizes or costs.
Daily-only MultiCharts data cannot compute the intraday euro-reaction branch.
Obtain the original Python implementation, contract/roll map and reconciled ledgers before a return trial.

Sources: supplied `inputs/six_e_cross_asset_20261027/research_note.txt`; Claude repository
snapshot `6416de2dd39782eb4a43bd665c866409da4deb70`; official sources in the result report.
New return trials: **0**. The author already examined multiple families and parameter sets;
their complete selection count and chronology are unavailable.

## 1. Who trades, and what causes the trade?

Hypothesis: investors rebalance currency exposures after changes in rates,
energy, stocks and gold; gradual adjustment might predict subsequent EUR/USD.
The note identifies no measurable forced order, participant inventory, mandate
or deadline. These are predictive cross-asset hypotheses, not demonstrated
scheduled flows. The cited papers motivate investigation, not these exact signs,
thresholds or a next-day euro response. Persistent price impact need not imply
predictable returns after observing the impact.

## 2. Direction, size and timing known before entry

Decide at 16:00 America/New_York. Define a common as-of cut for every input,
then a later executable order/fill. Daily settlements and last-trade closes are
different fields. A dated row is not proof that it was available at decision time.
Require trailing-volatility definitions, warm-up, lagged denominators, how
simultaneous ZN/euro shocks combine, and sign/priority/cooldown rules.
The euro reaction measured 08:29–09:30 ET is an own-price input; it must be
separated from the purely cross-asset claim. The daily-only proposed chart lacks it.
Define capital/notional behind the 5% vol target and 1.5x cap, signed integer
M6E rounding, net target quantity, rebalances, exits and maximum concurrent risk.

## 3. Does it reach the traded contract?

6E and M6E reference EUR/USD, so the price link is direct. The implementation
and liquidity are different: M6E's price tick is coarser. ZN, CL, ES and GC
are information proxies, not evidence of net EUR futures demand. No asserted
flow amount or absorption constraint is measured.

## 4. Data feasibility

| Input | Present evidence | Unresolved requirement |
|---|---|---|
| 6E minute OHLCV | Repository annual CSVs, 2017-12 through 2026-10; headers/edge timestamps inspected | Author's individual contracts, adjustment/roll history and timestamps |
| ZN/CL/ES/GC | Existing research has these markets | Exact synchronized input series and knowable close fields for this package |
| M6E execution | Official contract specifications | Native quotes/trades, integer target orders and all-in personal-broker fees |
| Python rule | Narrative only; no matching six-leg implementation found in the inspected repository tree | Original implementation, parameters, trial log, source versions |
| Portfolio results | Current 19-piece personal portfolio documented | Same-calendar daily marked-to-market candidate ledger and trade/roll reconciliation |
| European rates/equities | Eurex FGBL/FESX specifications; ECB daily yield-curve metadata | Vendor historical coverage, close availability and provenance; ECB yields are not Bund futures |

Local 2017 6E coverage begins December 1, insufficient for a full 63-session
January warm-up. The author may own other history or start trading later;
ask for actual first valid signal dates rather than declaring a confirmed defect.

## 5. Costs and actual gaps

M6E is EUR 12,500 with 0.0001 price increments ($1.25); 6E's 0.00005
increment scales to $0.625 per M6E-equivalent and is not a valid native M6E tick.
One native tick adverse at entry and exit costs $2.50 per M6E round trip,
in addition to fees if not already included. The note's $1.20 per position
change is ambiguous. Require cost = abs(change in contracts) x per-unit cost,
including reversals, daily vol rebalances and rolls; avoid double counting spread.
This is a multi-day personal sleeve, not a proposed fill for an intraday Apex gap.
No portfolio occupancy or conditional loss contribution is measured by the note.

## 6. Power before a return test

Using the claimed event rates, five design years imply approximately 135
Macro-Shock, 40 Stock-Shock and 60 Gold-Shock opportunities before warm-up.
At iid t=2, net mean hurdles are respectively about 0.17 / 0.32 / 0.26 of
trade standard deviation. Clustering/overlap reduces effective sample size;
multiple testing raises the hurdle. There is no supplied ledger to estimate
actual dispersion, costs or effective n. These are planning illustrations only,
computed in `analysis/codex_six_e_claims_audit.py`, not significance results.

## 7. Already tested and falsifiers

Existing 6E fixing/gap-fade tests and own-price daily blocks failed; broad
cross-market time-series momentum was weak. None settles this exact multi-day
cross-asset package. Fail the replication gate if the supposed lag disappears
after synchronized clocks, next-executable fills, integer sizes or native costs.
Fail a new-feature claim if own-EUR momentum or a common-dollar factor explains
it on matched events. New threshold/leg/currency choices count as trials.
Reported 2023+ and 2022–26 results are already seen; no new holdout is claimed.

## 8. Failure and diversification

| Question | Prediction / evidence required |
|---|---|
| What stops the mechanism? | Faster information absorption, changing rate/risk relationships; monitor frozen signals |
| Liquidity role? | Marketable orders consume M6E liquidity; quotes and paper/live fills needed to measure slippage |
| Clustered losses? | Macro whipsaw, simultaneous USD shocks, overnight/weekend gaps, rising margin requirements |
| Shared portfolio losses? | Potential common macro exposure with NQ/ES and CL; compare current 19-piece book, especially joint worst periods |
| Offset before breach? | Unproven; multi-day statistical diversification is not immediate protection or assured margin relief |

The reported +0.06 correlation covers an intraday NQ book, not necessarily the
current personal portfolio. Require base/addition/prespecified replacement and
empty-slot controls at native quantities and the same capital/drawdown budget.
No stop/emergency exit or data-failure policy is fully specified in the note.

## Decision and next gate

**NEEDS DATA**: original Python code, frozen settings, contract/roll provenance,
trade/order ledger and daily marked-to-market ledger first. Then commit a
bounded replication plan before returns, validate mechanics/costs, independently
check, and measure current personal-portfolio contribution. All four 50K/150K
evaluation/funded destinations are outside this multi-day specification; no
Apex benchmark is inferred or altered. No grading or trading promotion here.
