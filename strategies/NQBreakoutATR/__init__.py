from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQBreakoutATR(Strategy):
    """
    Modular Foundation Strategy:
    - Entry 10: Resting Stop Breakout (Highest High / Lowest Low of last X bars)
    - Exit 8: Dynamic ATR Volatility Stop Loss
    - Exit 4: Trailing Dollar/Point Giveback from Peak
    - Iteration 1: Active Filter Case 91 (ADX > 30: Strong Trend Regime only)
    """

    def __init__(self):
        super().__init__()
        self.peak_price = None
        self.trough_price = None

    def hyperparameters(self):
        return [
            {"name": "breakout_length", "type": int, "min": 5, "max": 30, "default": 10},
            {"name": "atr_period", "type": int, "min": 5, "max": 25, "default": 14},
            {"name": "atr_mult", "type": float, "min": 1.0, "max": 3.5, "default": 2.0, "step": 0.5},
            {"name": "giveback_points", "type": int, "min": 20, "max": 80, "default": 40},
            {"name": "filter_case", "type": int, "min": 0, "max": 143, "default": 91},
        ]

    def _check_filter(self) -> bool:
        fc = self.hp["filter_case"]
        if fc == 0:
            return True

        # Family 1: Trend / Moving Average Position
        if fc == 4:  # Close > 10 MA
            ma10 = ta.sma(self.candles, period=10)
            return self.close > ma10
        if fc == 3:  # Close < 10 MA
            ma10 = ta.sma(self.candles, period=10)
            return self.close < ma10
        if fc == 12:  # Close > 50 MA
            ma50 = ta.sma(self.candles, period=50)
            return self.close > ma50
        if fc == 11:  # Close < 50 MA
            ma50 = ta.sma(self.candles, period=50)
            return self.close < ma50
        if fc == 20:  # Close > 200 MA
            ma200 = ta.sma(self.candles, period=200)
            return self.close > ma200

        # Family 2: Intraday Time Windows (CT)
        dt_ct = datetime.fromtimestamp(self.current_candle[0] / 1000.0, tz=CT_TZ)
        time_int = dt_ct.hour * 100 + dt_ct.minute
        if fc == 24:  # Before 10:00 AM CT
            return time_int < 1000
        if fc == 25:  # Before 12:00 PM CT
            return time_int < 1200
        if fc == 28:  # After 8:00 AM CT
            return time_int > 800

        # Family 5 & 7: Volatility & Momentum
        if fc == 91:  # Case 91: ADX > 30 (Strong Trend Regime)
            adx_val = ta.adx(self.candles, period=14)
            return adx_val > 30
        if fc == 92:  # Case 92: ADX < 30 (Chop / Range)
            adx_val = ta.adx(self.candles, period=14)
            return adx_val < 30

        # Family 8: Volume
        if fc == 120:  # Volume > 5-bar volume MA
            vol_ma5 = np.mean(self.candles[-6:-1, 5])
            return self.current_candle[5] > vol_ma5

        return True

    def should_long(self) -> bool:
        length = self.hp["breakout_length"]
        if len(self.candles) < max(length + 5, 55):
            return False

        if not self._check_filter():
            return False

        # Highest high of previous X bars (excluding current bar)
        highest_high = np.max(self.candles[-length - 1 : -1, 3])
        return self.close > highest_high

    def should_short(self) -> bool:
        length = self.hp["breakout_length"]
        if len(self.candles) < max(length + 5, 55):
            return False

        if not self._check_filter():
            return False

        # Lowest low of previous X bars (excluding current bar)
        lowest_low = np.min(self.candles[-length - 1 : -1, 4])
        return self.close < lowest_low

    def go_long(self):
        notional = min(self.available_margin * 0.5, self.price * 5)
        qty = utils.size_to_qty(notional, self.price, fee_rate=self.fee_rate)
        self.buy = qty, self.price

    def go_short(self):
        notional = min(self.available_margin * 0.5, self.price * 5)
        qty = utils.size_to_qty(notional, self.price, fee_rate=self.fee_rate)
        self.sell = qty, self.price

    def on_open_position(self, order):
        atr = ta.atr(self.candles, period=self.hp["atr_period"])
        stop_dist = atr * self.hp["atr_mult"]

        if self.is_long:
            self.peak_price = self.price
            self.stop_loss = self.position.qty, self.price - stop_dist
        elif self.is_short:
            self.trough_price = self.price
            self.stop_loss = self.position.qty, self.price + stop_dist

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        giveback = self.hp["giveback_points"]

        # Trailing giveback exit (Exit 4)
        if self.is_long:
            if self.price > self.peak_price:
                self.peak_price = self.price
            elif (self.peak_price - self.price) >= giveback:
                self.liquidate()
        elif self.is_short:
            if self.price < self.trough_price:
                self.trough_price = self.price
            elif (self.price - self.trough_price) >= giveback:
                self.liquidate()
