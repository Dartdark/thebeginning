from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils
import numpy as np


class GoldenCross(Strategy):
    """
    Golden Cross Strategy for NQ (Nasdaq-100)
    -----------------------------------------
    Adapted for Nasdaq (NQ) index futures / equities trading sessions:
    - Trading Hours: US Regular Trading Hours (09:30 - 16:00 America/New_York).
    - Session-Filtered History: Indicators read session candles only, filtering out off-hours noise and weekend gaps.
    - Entry Gating: Entries are only evaluated during market trading hours (self.is_trading_hours).
    - Unfilled Orders: Cancelled once the session closes (should_cancel_entry).
    - 24/7 Risk Management: Stop-loss orders and trailing stops remain active around the clock in update_position().
    - Dynamic Sizing: Sized with utils.risk_to_qty based on available margin and ATR stop distance.
    """

    def trading_hours(self) -> dict:
        """
        US Regular Trading Hours (RTH) for Nasdaq / Equities:
        09:30 - 16:00 ET, Monday through Friday.
        """
        return {
            'timezone': 'America/New_York',
            'hours': {'Mon-Fri': '09:30-16:00'}
        }

    def hyperparameters(self) -> list:
        return [
            {'name': 'fast_period', 'type': int, 'min': 20, 'max': 100, 'default': 50},
            {'name': 'slow_period', 'type': int, 'min': 100, 'max': 300, 'default': 200},
            {'name': 'stop_loss_atr_mult', 'type': float, 'min': 1.0, 'max': 5.0, 'step': 0.5, 'default': 3.0},
            {'name': 'risk_percentage', 'type': float, 'min': 0.5, 'max': 5.0, 'step': 0.5, 'default': 1.5},
        ]

    @property
    @cached
    def session_candles(self) -> np.ndarray:
        """
        Candles filtered by the defined trading hours.
        This provides consistent indicator history aligned with market session hours.
        """
        return utils.filter_candles_by_hours(self.candles, self.trading_hours())

    @property
    @cached
    def fast_sma(self) -> np.ndarray:
        return ta.sma(self.session_candles, period=self.hp['fast_period'], sequential=True)

    @property
    @cached
    def slow_sma(self) -> np.ndarray:
        return ta.sma(self.session_candles, period=self.hp['slow_period'], sequential=True)

    @property
    @cached
    def atr(self) -> float:
        return ta.atr(self.session_candles)

    def should_long(self) -> bool:
        if not self.is_trading_hours:
            return False
        if len(self.session_candles) < self.hp['slow_period'] + 2:
            return False
        return utils.crossed(self.fast_sma, self.slow_sma, direction='above')

    def should_short(self) -> bool:
        if self.is_spot_trading:
            return False
        if not self.is_trading_hours:
            return False
        if len(self.session_candles) < self.hp['slow_period'] + 2:
            return False
        return utils.crossed(self.fast_sma, self.slow_sma, direction='below')

    def go_long(self):
        stop_price = self.price - self.atr * self.hp['stop_loss_atr_mult']
        qty = utils.risk_to_qty(
            self.available_margin,
            self.hp['risk_percentage'],
            self.price,
            stop_price,
            fee_rate=self.fee_rate
        )
        self.buy = qty, self.price

    def go_short(self):
        stop_price = self.price + self.atr * self.hp['stop_loss_atr_mult']
        qty = utils.risk_to_qty(
            self.available_margin,
            self.hp['risk_percentage'],
            self.price,
            stop_price,
            fee_rate=self.fee_rate
        )
        self.sell = qty, self.price

    def on_open_position(self, order):
        if self.is_long:
            self.stop_loss = self.position.qty, self.price - self.atr * self.hp['stop_loss_atr_mult']
        elif self.is_short:
            self.stop_loss = self.position.qty, self.price + self.atr * self.hp['stop_loss_atr_mult']

    def update_position(self):
        # Exits and risk management run 24/7 across session boundaries
        if self.is_long:
            trail_stop = self.price - self.atr * self.hp['stop_loss_atr_mult']
            if trail_stop > self.average_stop_loss:
                self.stop_loss = self.position.qty, trail_stop
            if len(self.session_candles) >= self.hp['slow_period'] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.liquidate()
        elif self.is_short:
            trail_stop = self.price + self.atr * self.hp['stop_loss_atr_mult']
            if trail_stop < self.average_stop_loss:
                self.stop_loss = self.position.qty, trail_stop
            if len(self.session_candles) >= self.hp['slow_period'] and self.fast_sma[-1] > self.slow_sma[-1]:
                self.liquidate()

    def should_cancel_entry(self) -> bool:
        # Cancel unfilled entry orders once regular market session has ended
        return not self.is_trading_hours

    def update_chart(self) -> None:
        if len(self.session_candles) >= self.hp['slow_period']:
            self.add_line_to_candle_chart('Fast SMA', self.fast_sma[-1], color='gold')
            self.add_line_to_candle_chart('Slow SMA', self.slow_sma[-1], color='blue')

    def watch_list(self) -> list:
        if len(self.session_candles) < self.hp['slow_period']:
            return [('Session', 'Open' if self.is_trading_hours else 'Closed')]
        return [
            ('Session', 'Open' if self.is_trading_hours else 'Closed'),
            ('Fast SMA', round(float(self.fast_sma[-1]), 2)),
            ('Slow SMA', round(float(self.slow_sma[-1]), 2)),
            ('Trend', 'Bullish' if self.fast_sma[-1] > self.slow_sma[-1] else 'Bearish'),
        ]
