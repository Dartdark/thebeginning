# Strategy Specification & Design Report: GoldenCross

## Objective
Implement a robust, production-grade **Golden Cross** trend-following strategy for the Jesse trading framework.

- **Fast Indicator**: 50-period Simple Moving Average (configurable via `fast_period`).
- **Slow Indicator**: 200-period Simple Moving Average (configurable via `slow_period`).
- **Signal Definition**:
  - **Long (Golden Cross)**: Fast SMA crosses above Slow SMA (`utils.crossed(fast_sma, slow_sma, direction='above')`).
  - **Short (Death Cross)**: Fast SMA crosses below Slow SMA (`utils.crossed(fast_sma, slow_sma, direction='below')`) on futures accounts.
- **Risk Management**:
  - Position sizing calculated dynamically using `utils.risk_to_qty` based on account available margin, user risk percentage (default 2%), and ATR stop distance.
  - Initial protective stop loss placed via `self.stop_loss` in `on_open_position()`.
- **Exit Logic**:
  - Position liquidated in `update_position()` if reverse moving average cross occurs (Fast SMA below Slow SMA for longs; Fast SMA above Slow SMA for shorts).
  - Stop-loss execution handled automatically by exchange/engine orders.

## Architecture & Code Standards Compliance
1. **No Hardcoded Quantities**: Quantity derived from `available_margin`, `risk_percentage`, and `fee_rate` via `utils.risk_to_qty`.
2. **Proper Order Placement**:
   - `self.buy = qty, self.price` and `self.sell = qty, self.price` in `go_long()` and `go_short()`.
   - Protective stops configured inside `on_open_position(order)` with proper direction checks (`self.is_long` / `self.is_short`).
3. **Spot vs. Futures Support**:
   - `should_short()` checks `self.is_spot_trading` and returns `False` on spot markets.
4. **Interactive Charting & Monitoring**:
   - `update_chart()` plots `Fast SMA` (gold) and `Slow SMA` (blue) on the candle price chart.
   - `watch_list()` outputs `Fast SMA`, `Slow SMA`, and current `Trend` status for live/paper monitoring.
5. **Optimization Ready**:
   - Hyperparameters defined for `fast_period`, `slow_period`, `stop_loss_atr_mult`, and `risk_percentage`.

## Data & Backtesting Status
- Database candle check (`get_existing_candles`): 0 stored candle sets found in the database.
- Dashboard: dashboard URL unavailable (no session executed yet).
- To run backtests, import historical candles for your chosen exchange and pair (e.g., Binance `BTC-USDT` on `1h` or `4h`), then configure a backtest draft.
