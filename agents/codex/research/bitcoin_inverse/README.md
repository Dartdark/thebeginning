# Bitcoin spot + dated inverse-futures strategy — offline review packet

Implements Deng/Pan/Zhang/Zou, SSRN3441913, main Eqs4.2–4.6/4.4. The main C2 minus sign is used;
the inconsistent printed AppendixB.2 plus sign is not. See the [source review](../../results/bitcoin_inverse_3441913_review.md).

- Strategy module: `analysis/codex_bitcoin_inverse_3441913_strategy.py`.
- Behavioral tests: `agents/codex/test_bitcoin_inverse_strategy.py`.
- Input example: [synthetic_input.json](synthetic_input.json). All quotes, account balances, contract identity and
  timestamps are fabricated. Model parameters reproduce the paper's published calibration for arithmetic only.
- [Review handoff](../../results/bitcoin_inverse_3441913_build.md) and [frozen build scope](../../plans/bitcoin_inverse_3441913_build.md).

## Run from repository root

```sh
python3 -m unittest discover -s agents/codex -p test_bitcoin_inverse_strategy.py -v
python3 analysis/codex_bitcoin_inverse_3441913_strategy.py \
  agents/codex/research/bitcoin_inverse/synthetic_input.json \
  --output analysis/outputs/codex_bitcoin_inverse_3441913_build/synthetic_proposal.json
```

Python standard library only. No HTTP client, credentials, broker hooks, scheduler or historical return runner.
`from_packet(packet)` is the reusable JSON interface. `plan_rebalance(...)` accepts immutable typed objects.
`inverse_fill(...)` is the pure reciprocal-price position-accounting helper, separate from quote proposals.
The CLI records script/input SHA256. It creates the output parent directory but rejects invalid inputs before writing a proposal.

## Strategy and rebalance protocol

The caller explicitly chooses each decision/rebalance time and supplies fixed annualized calibration available by that time.
There is no hidden rolling fit or automatic daily-close execution. A later historical study must freeze its observation,
calibration-update and rebalance schedule before returns; continuous rebalancing from the paper is not reproduced.

Power utility uses scale=NAV/(1−alpha), with alpha<1, alpha!=0. Exponential uses scale=1/gamma; gamma carries inverse-USD
units, so copying a dimensionless gamma from a differently scaled account changes the risk. Then:

- Total non-futures BTC exposure target in USD = C1×scale.
- Inverse contract target = C2×scale/(K×Z), Z=spotMark/futuresMark; round toward zero to whole contracts.
- Collateral and unrealized inverse P&L are BTC exposures too. Subtract marked unrealized BTC from the total model
  BTC target to obtain physical spot+collateral inventory; do not buy theta again outside the collateral wallet.
- Proposed spot adjustments, rather than all wallet balances, round toward zero to the supplied BTC lot. Fees and realized
  inverse P&L can leave non-lot wallet balances. A minimal collateral-prefund purchase rounds **up** to ensure funding.

Bid/ask quotes are reference prices for a hypothetical funding/cost bridge at a fixed mark. Every action carries a sequence,
decision time, strictly later earliest eligible fill and HYPOTHETICAL status. The same timestamp is a lower bound, not a promise
that all sequenced actions execute atomically. Actual receipt/fill/transfer chronology and refreshed quotes must be reconciled
before replanning; this packet includes no order lifecycle or exchange execution adapter.

## Input contract

All fields shown in the synthetic JSON are required; the dataclasses in the module define exact component schemas.

| Object | Meaning and units |
|---|---|
| `input_status` | `synthetic` or `unverified_research`; never a claim that source data was independently validated |
| `decision_time` | Explicit UTC ISO8601 timestamp with Z/+00:00 |
| `model` | Annual arithmetic drifts, annual volatilities, correlation; calibration_end≤available_at≤decision |
| `instrument` | Explicit venue and contract ID, `dated_inverse`, settlement `BTC`, face USD per whole contract, expiry |
| `quotes` | Matching contract ID; observation/availability clocks; positive spot and futures bid/ask plus separate marks |
| `book` | Matching contract ID; snapshot/availability clocks; USD cash, unpledged spot BTC, pledged BTC, signed integer contracts, inverse entry basis |
| `settings` | Utility/risk, pooled research wallet, spot lot, fees, initial/maintenance rates, exposure/condition/age bounds and positive latency |

Use globally unambiguous contract IDs; an ID match validates consistency of supplied fields, not authenticity of an exchange record.
An index level is not an executable spot bid/ask. Linear CME futures and perpetuals are explicitly rejected.
Contract identity may not change for a held position; a roll must be implemented as a separately specified close/open protocol.

All timestamps must be UTC and timezone-aware. Quote observation≤quote availability≤decision; same for account snapshot.
Age limits use observation/snapshot time, not the later receipt time. Expiry must follow decision+latency. Quotes may have
marks outside their bid/ask, so the execution-to-mark difference is signed and can represent improvement as well as cost.

## Native BTC/USD accounting

NAV = USD cash + spotMark×(spotBTC+collateralBTC+unrealizedInverseBTC).
Unrealized BTC = N×K×(1/entryBasis−1/futuresMark). No USD multiplier is substituted for inverse settlement.
Adding same-direction contracts uses a reciprocal-weighted entry basis. A partial close realizes the closed amount only;
a reversal closes the old quantity then opens the remainder at the new price. Future fees are BTC, spot fees USD.

The proposed sequence buys any needed prefunding BTC, transfers wallet BTC into collateral, changes inverse inventory,
releases excess collateral, then adjusts spot inventory. Reserve = target face/futuresMark×(initialMargin+closingFeeRate),
plus negative unrealized BTC; positive unrealized gains do not fund that conservative reserve. Pre-funding also covers
futures fill fees and realized losses. If the declared target cannot fund collateral, the proposal is rejected.

**Pooled-wallet assumption:** transfers between spot inventory and collateral are bookkeeping moves in one research pool.
Real separate venues may require confirmations, transfer fees, delays and venue-specific collateral eligibility. Those are
not modeled or verified; the proposals cannot be directly executed as if transfers were instantaneous.
The exchange's actual mark tiers, haircuts, maintenance deductions and liquidation process are not implemented.
An existing book at/below the configured maintenance level raises an error rather than booking a fictional liquidation.

USD borrowing and short spot are unsupported. A source target requiring either, an exposure cap breach or a badly
conditioned covariance raises `ReviewError`; there is no silent clipping, shrinkage or fallback strategy.
For power utility, the paper's nonnegative continuous wealth property is not a discrete exchange solvency guarantee.
No interest, custody/network fees, spot borrowing, perpetual funding or expiry settlement/roll is inserted.
Synthetic input rates (including10%/5% margin,0.1% spot fee and0.075% inverse fee) are illustrative assumptions, not
verified historical/current BitMEX settings. Each configured change is reviewable; no return-based optimization occurred.

## Verification and research boundary

Twenty behavioral tests cover source coefficients, reciprocal P&L/basis, reversal/partial close, cash conservation,
BTC exposure including collateral, fees, immutability, integer lots, both utility forms, timestamps/age/expiry/identity,
short inverse support and failure paths. The cash bridge reconciles NAV change to explicit fees plus execution-to-mark differences.
These test synthetic state transitions, not strategy performance or exchange integration.

Current matching data/specification blockers remain in the source review and evidence sheet. No empirical return trial,
MultiCharts port, personal allocation or50K/150K evaluation/funded placement follows. Claude's independent review is pending.
