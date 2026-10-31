# Monthly commodity skewness — offline research code

Implements the reviewed SSRN 3507947 selection rule with explicit input and execution assumptions.
It produces one month's target positions for research. It does not calculate historical performance,
manage open positions, execute rolls, submit orders or connect to a broker. Personal-account research
only: the source's month-long holdings do not fit the current Apex intraday plans.

## Run a complete example

From the repository root, with Python 3.10+ and numpy/scipy installed:

```bash
python agents/codex/research/commodity_skew/synthetic_example.py scratch_data/commodity_skew_packet.json
python analysis/codex_commodity_skew.py scratch_data/commodity_skew_packet.json --output scratch_data/commodity_skew_plan.json
python agents/codex/test_commodity_skew.py
```

The generator creates invented prices, contract names and calendars for all 22 source commodities.
It deliberately includes weekdays that are real exchange holidays: it is a deterministic engineering
fixture, **not an exchange calendar or market dataset**. Do not use its dates, contract IDs or prices
for actual trading. It is generated rather than committing thousands of invented observation rows.

For a real validated packet, replace the first command with your data adapter. The second command
validates and writes an atomic JSON result. A rejected packet exits nonzero and neither creates nor
replaces the output file. A previously saved output can therefore remain on disk; always check exit status
and input/code hashes. Import `build_plan(packet)` from `analysis/codex_commodity_skew.py` for offline reuse.
The module also reuses `clock`/`positive` from `analysis/codex_rad_double_sort.py`; keep both files in the repo.

## Implemented rule and explicit choices

1. Supply the exact 22 named commodity IDs in `UNIVERSE` in the module: soybean oil, corn, cocoa, cotton,
   feeder cattle, gold, copper, heating oil, coffee, live cattle, lean hogs, natural gas, oats, orange juice,
   palladium, platinum, soybeans, sugar, silver, soybean meal, wheat and crude oil. No two-market substitute.
2. Use every declared settlement in the 12 calendar months ending with `ranking_month`. Each commodity
   needs at least 200 observations and 15 declared sessions in each month. These are conservative local
   completeness checks, not thresholds given by the paper or a certificate of an authentic exchange calendar.
3. Compute simple daily returns `current_close / previous_same_contract_close - 1`. On a roll, supply the
   incoming contract's previous settlement as the denominator; an outgoing/incoming splice is rejected.
   This is a declared research construction, pending vendor/source parity. Nonpositive prices are rejected,
   including any affected CL negative-price history. No day or commodity is silently removed to get past it.
4. Compute adjusted Fisher-Pearson sample skewness (`scipy.stats.skew(..., bias=False)`). Long the four
   lowest, short the four highest. This estimator is our explicit choice because the paper does not specify it.
   Reject zero variance and cutoff ties within absolute/relative tolerance 1e-12 rather than invent a winner.
5. Decision occurs in the following calendar month, in the declared timezone, after every input receipt.
   Earliest fill must be strictly later. The caller chooses a verified formation session; the planner does not
   infer a market opening, holiday, DST schedule or actual fill. Twelve-month selection is monthly, not daily.
6. Interpret the no-leverage/equal-weight description as 12.5% NAV per leg: 50% long + 50% short = 100%
   ideal gross. Floor native contract quantities to the leg budget, report weight shortfalls and rounded net
   exposure, reject any selected leg that cannot afford one contract. This sizing is an adaptation awaiting
   source reconciliation, not proof of author weighting or usable margin. Price/multiplier/FX units must agree.
7. Require the next roll/exit action within the holding month and strictly before an effective contract-specific
   deadline. Supply that deadline as the earliest relevant first-notice/delivery/last-trade/broker restriction.
   The code cannot verify venue rules and does not perform that action. It never assumes the paper's generic
   first-day-of-delivery-month roll is safe.

## Packet schema

All monetary values, prices, multipliers and FX rates are **decimal strings**, not JSON numbers. Every clock
is an ISO timestamp with an explicit UTC offset. Session labels are ISO dates interpreted in `calendar_timezone`.
Example packets generated above contain every field; the schema is:

| Section | Required fields |
|---|---|
| Formation | `ranking_month` YYYY-MM; `decision_at`; `calendar_timezone` IANA name; `reference_nav_usd` |
| Provenance | `universe_provenance`, `calendar_provenance`, `price_provenance` and each corresponding `*_available_at` strictly before decision |
| Calendar | `universe`: exact commodity ID -> complete, unique, ascending expected-session list for the 12-month window; `warmup_sessions`: each ID -> preceding session before the window |
| Daily observations | `commodity`, `session`, `previous_session`, `contract_id`, `previous_contract_id` (must equal current contract), `last_trade_date`, `close`, `previous_close`, `event_at`, `available_at`, `previous_event_at`, `previous_available_at` |
| Entry contracts | `entry_contracts`: selected commodity ID -> specification below; the generator supplies all 22 for convenience, but only the selected eight are needed/validated |
| Contract identity/units | `contract_id`, `currency`, `reference_price`, `multiplier` (native currency per quoted price unit), `fx_to_usd`, `tick_size` (quoted price units), `roll_provenance` |
| Entry information clocks | `reference_event_at`, `reference_available_at`, `fx_event_at`, `fx_available_at`, `spec_available_at` |
| Planned action clocks | `earliest_fill_at`, `next_roll_or_exit_at`, `delivery_deadline_at`, `last_trade_at` |
| Costs | `commission_usd_per_contract_side`: account-USD fee including broker/exchange components; `slippage_ticks_per_side`: explicit nonnegative integer, including any assumed spread/slippage allowance |

Daily `event_at` must have the declared session's local date. Prior settlement must match the previous expected
session/event. On an unchanged contract, both its price and receipt clock must agree with the prior stored row.
On a roll, use separately sourced incoming-contract prior prices and receipts. Contract expiry declarations must
remain consistent and cannot predate an observed session. A dated contract ID cannot represent two commodities.

Entry reference price must be measured at that commodity's final ranking-session timestamp and known before
decision. FX must have the same local measurement date. If entry uses the final history contract, its price and
last-trade date must agree with that history. Incoming contracts can have a different price; their actual reference
quote and identity must be independently sourced. No price/FX forward filling, quote scaling or revisions inferred.

Input declarations do not prove correctness: verify original point-in-time receipts, market identity, quote units,
vendor series definitions, actual calendar completeness, revisions and contract/delivery rules independently.

## Output and cost meaning

Output contains all 22 skew scores with coverage counts; eight signed integer **targets**; reference prices,
native multipliers/FX/ticks; ideal versus rounded weights; gross/net reference exposure; action deadlines;
separate fee/slippage estimates; and CLI input/module/shared-helper hashes plus dependency versions.

For quantity `q`, entry commission is `abs(q) * fee_usd_per_side`. Entry slippage is
`abs(q) * ticks_per_side * tick_size * multiplier * FX_to_USD`. The hypothetical unchanged-contract round trip
is twice their sum. This assumes entry from flat and the same quantity/specifications/FX on exit. It is not
actual monthly rebalance turnover, roll fees, a held-book ledger, management/financing cost or backtest net P&L.
Do not add a second spread deduction if it is already included in the configured slippage allowance.

There is no margin, buying-power, stop-loss, gap-risk or executable exposure guarantee. Whole-contract floor
sizing respects the **reference** notional budget; actual fill prices and FX can change exposures. It does not
rebalance or close existing positions. A future ledger must preserve signed quantities, daily marks, actual roll
transactions, collateral, fees, FX and cash flows before using the repository's metrics/account tools.

## Evidence and next gate

The tests and saved example are constructed mechanics checks, not economic trials. No historical source returns,
2018–22 design gate, post-2019 validation, Monte Carlo, independent strategy check or personal-book comparison
has passed. The complete dated 22-market panel and price/roll/weight definitions remain missing. Real return
work needs those inputs, a reconciled native-contract ledger and a separately committed bounded preregistration.

See [source review](../../results/ssrn_3507947_review_20261030.md),
[build scope](../../plans/commodity_skew_build_20261030.md),
[build report](../../results/commodity_skew_build_20261030.md) and execution reference E53.
