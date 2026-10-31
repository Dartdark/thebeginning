# SniperAlgo: DON'T TEST as standalone alpha

Summary: The supplied class executes an externally chosen order using best bid/ask conditions. It has no forecast, signal-generation rule, position exit policy or independently specified parent-order schedule. Review its mechanics without inventing a trading strategy. New economic trials: 0.

## Participant, cause and clock

The participant is our own parent order, not an identified forced counterparty. Direction, price cap/floor, quantity and offset come from the caller. A matching top-of-book quote triggers an order; later ticks request cancellation while an order ID remains set. No scheduled external flow, expected dollar imbalance or edge mechanism is specified. Posted quotes must precede the actual send; decision price is not guaranteed fill price.

## Transmission and data

The class is generic to a vn.py contract; it does not identify an NQ/ES signal or any other market. Our minute OHLCV and order-flow summaries do not establish the tick-level quote, order, acknowledgement, cancellation and trade-event sequence required to estimate this helper's fills. No complete historical replay dataset for it has been established. A one-minute low touching the limit is not sufficient evidence of a fill.

## Costs, power and prior work

No defined closed trade, eligible event count, gross edge or native-cost P&L exists to screen. Quoted depth caps requested child volume; it does not guarantee that volume remains available at execution. Quantity and price are not predictive features by themselves. The repo's previous limit-versus-market entry study is relevant to missed-trade/adverse-selection risk, but does not test this exact helper.

## Failure and diversification

No low correlation or hedge benefit is claimed. The source needs consideration of stale/invalid quotes, asynchronous terminal-order messages, delayed trade messages, overfill protection and an external deadline/risk controller. A parent order with CLOSE offset can execute an externally requested exit, but does not itself decide when that exit is needed. No protection before an account breach is established.

## Decision

No standalone placement in personal, 50K/150K funded or 50K/150K evaluation. A research-only execution-helper role is possible for an existing strategy, conditional on separate quote/order replay and implementation verification. Run only the committed synthetic callback study described in [the review plan](../plans/sniper_execution_20261027.md). Do not fabricate a signal, measure returns or alter live code. No queue addition is merited by a generic execution utility without measured benefit.
