# Strategy Adaptation Report: GoldenCross for NQ (Nasdaq-100)

## Objective
Adapt the `GoldenCross` strategy for trading **NQ (Nasdaq-100 index futures / tokenized index instruments)**, implementing Jesse's formal Trading Hours adaptation workflow.

## Target Instrument & Market Specifications
- **Instrument**: NQ (Nasdaq-100 / E-mini Nasdaq futures / tokenized US100 index)
- **Primary Market Schedule**: US Regular Trading Hours (RTH)
  - Timezone: `America/New_York`
  - Hours: `Mon-Fri 09:30-16:00`
- **Underlying Dynamics**: High point value / index scale requiring dynamic risk sizing, session alignment to avoid false crosses during low-liquidity overnight sessions, and around-the-clock exit protection.

## Implemented Architectural Adaptations

### 1. Market Schedule Definition (`trading_hours`)
Defined explicit RTH schedule using IANA timezone:
```python
def trading_hours(self) -> dict:
    return {
        'timezone': 'America/New_York',
        'hours': {'Mon-Fri': '09:30-16:00'}
    }
```

### 2. Session-Filtered Indicator History (`session_candles`)
Instead of calculating moving averages across non-session or weekend drift, indicator calculations are isolated to active trading sessions via `utils.filter_candles_by_hours()` cached per candle:
- `fast_sma`: 50-period SMA computed strictly on session candles.
- `slow_sma`: 200-period SMA computed strictly on session candles.
- `atr`: ATR calculated on session volatility.

### 3. Entry Decision Gating (`self.is_trading_hours`)
- Evaluated via `self.is_trading_hours` on both `should_long()` and `should_short()`.
- Guarantees entries are only initiated during high-liquidity regular trading hours.

### 4. End-of-Day Order Policy (`should_cancel_entry`)
- Pending entry orders that have not filled by the market close are automatically cancelled once the session closes (`return not self.is_trading_hours`), preventing stale overnight fills.

### 5. 24/7 Risk & Position Management (`update_position`)
- Position management deliberately ignores session gating: stop-loss orders remain active on the exchange, and ratcheting trailing stops dynamically trail in `update_position()` around the clock.

### 6. Warm-Up Considerations
- Because NQ RTH consists of 6.5 trading hours per day, a 200-period SMA requires at least 200 session candles (~31 trading days).
- When backtesting on a 24/7 exchange feed (such as crypto perpetuals or tokenized indices), ensure `warm_up_candles` is set to at least 800-1000 candles on the 1h timeframe so sufficient session history is retained after filtering.

## Backtest & Dashboard Status
- **Dashboard**: dashboard URL unavailable (no backtest session run yet; candles need to be imported first).
- **Existing Candles**: 0 stored candle sets in the database.
- **Next Steps**: Import historical candle data for your desired NQ route/exchange, then launch a backtest to analyze performance.
