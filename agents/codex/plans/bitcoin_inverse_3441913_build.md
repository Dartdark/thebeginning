# SSRN3441913 strategy implementation for Claude review

User explicitly requests strategy code for review after the source/data audit. This is a narrower implementation task,
not authorization to substitute CME data, run new economic variants or change accounts. Evidence remains NEEDS DATA
AND SPECIFICATION for historical returns; the user authorizes building the offline code despite that data gate.

Build a Python allocation/rebalance module using main Eqs4.2–4.6 and matrix Eq4.4 (correct minus sign for C2).
Support the paper's exponential and power utility as equation implementations; use power alpha−0.5 in the one
synthetic example. No optimized variant selection or empirical return trials. Fixed external calibration carries
sample-end and available-at clocks; no fitting to synthetic or real future outcomes.

One explicit protocol: caller supplies a reconciled USD/spotBTC/collateralBTC/inverse-position snapshot and fresh
spot/futures bid/ask/mark values at a UTC decision time. At caller-chosen rebalance times compute targets, round
spot to declared BTC lot and futures toward zero to integer lots, then create quote-priced offline order proposals.
No scheduling, external I/O, broker connector or autonomous placement. Earliest eligible fill is decision+configured
positive latency; expected bid/ask cash bridge is a review calculation, never a confirmed fill.

Account in USD cash plus BTC inventory/collateral and marked inverse unrealized BTC. Include collateral and unrealized
BTC in the model's total non-futures BTC exposure to avoid double counting. A futures partial close realizes only the
closed quantity's reciprocal-price P&L; adding in the same direction uses reciprocal-weighted entry basis; reversals
realize old inventory first. Fees are native BTC on futures fills and USD on spot. Spot buys/sells fund/redeem collateral
within the same wallet model; no spot shorts, lending interest, USD borrowing, perpetual funding or implicit liquidation.
Reject a target requiring these unsupported operations rather than silently clipping risk or shrinking quantities.

Caller configures costs, BTC lot, contract face, initial/maintenance margin, maximum gross modeled exposure,
condition-number bound, account/quote maximum ages and latency. All are explicit research assumptions, not verified
historical BitMEX settings. Require dated BTC-settled inverse identity and expiry beyond decision/fill eligibility.
Do not implement a perpetual or contract roll. Reject nonfinite/nonpositive prices, invalid clocks, stale snapshots,
unreconciled position basis, unsupported short spot, ill-conditioned covariance and insufficient cash/collateral.
If existing collateral breaches modeled maintenance, stop with a review error; do not invent a liquidation fill.

Deliver reusable strategy module, CLI JSON input/output, one labeled synthetic packet, behavioral tests and review notes.
Tests must independently verify the source constants, long/short payoff signs, reciprocal entry basis, partial closes,
reversals, collateral and fee cash bridge, lot rounding, clock/expiry guards, rejection paths and immutable inputs.
No Sharpe/portfolio metrics: no empirical replay. Personal eligibility remains conditional; all four Apex homes unearned.
Document source/model differences, exact command and input schema. Update existing queue/evidence/library status without
removing data gates or claiming independent Claude review. Commit, preserve concurrent work and push codex/work.
