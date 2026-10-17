from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils
import numpy as np


class GoldenCross(Strategy):
    """
    Golden Cross Strategy
    ---------------------
    Classic moving average crossover trend-following strategy.
    - Long Entry: When Fast SMA crosses above Slow SMA.
    - Short Entry: When Fast SMA crosses below Slow SMA.
    - Risk Management: Sized with utils.risk_to_qty based on available margin and ATR stop distance.
    - Exits: ATR-based trailing stop and signal reversal liquidation in update_position().
    - Data Handling: Compatible with 24/7 markets, RTH, and overnight session feeds.
    """

    def trading_hours(self):
        # Set to None to trade all candles present in the historical data (or return schedule dict)
        return None

    def hyperparameters(self) -> list:
        return [
            {'name': 'fast_period', 'type': int, 'min': 10, 'max': 100, 'default': 50},
            {'name': 'slow_period', 'type': int, 'min': 100, 'max': 300, 'default': 200},
            {'name': 'stop_loss_atr_mult', 'type': float, 'min': 1.0, 'max': 5.0, 'step': 0.5, 'default': 3.0},
            {'name': 'risk_percentage', 'type': float, 'min': 0.5, 'max': 5.0, 'step': 0.5, 'default': 1.5},
        ]

    @property
    @cached
    def session_candles(self) -> np.ndarray:
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
        return not self.is_trading_hours

    def update_chart(self) -> None:
        if len(self.session_candles) >= self.hp['slow_period']:
            self.add_line_to_candle_chart('Fast SMA', self.fast_sma[-1], color='gold')
            self.add_line_to_candle_chart('Slow SMA', self.slow_sma[-1], color='blue')

    def watch_list(self) -> list:
        if len(self.session_candles) < self.hp['slow_period']:
            return []
        return [
            ('Fast SMA', round(float(self.fast_sma[-1]), 2)),
            ('Slow SMA', round(float(self.slow_sma[-1]), 2)),
            ('Trend', 'Bullish' if self.fast_sma[-1] > self.slow_sma[-1] else 'Bearish'),
        ]
