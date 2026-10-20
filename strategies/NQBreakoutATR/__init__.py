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
    - Iteration 2: Combined Filter (ADX > 30 AND US RTH Cash Session 08:30-14:30 CT)
    - Exit Modulations:
        exit_mode = 0: Baseline (Exit 4 Trailing Giveback only)
        exit_mode = 5: Exit 5 (Protect Profit Ratio: lock 50% profit if peak gain >= protect_trigger)
        exit_mode = 7: Exit 7 (Quick Spike Profit: limit take-profit target at entry +/- spike_mult * ATR)
        exit_mode = 10: Exit 10 (Stale Bar Exit: liquidate if bars >= 16 and profit < 20 points)
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
            {"name": "filter_case", "type": int, "min": 0, "max": 9999, "default": 9128},
            {"name": "exit_mode", "type": int, "min": 0, "max": 10, "default": 5},
            {"name": "protect_trigger", "type": float, "min": 30.0, "max": 100.0, "default": 50.0},
            {"name": "spike_mult", "type": float, "min": 2.0, "max": 5.0, "default": 3.5, "step": 0.5},
            {"name": "stale_bars", "type": int, "min": 8, "max": 24, "default": 16},
        ]

    def _check_filter(self) -> bool:
        fc = self.hp["filter_case"]
        if fc == 0:
            return True

        dt_ct = datetime.fromtimestamp(self.current_candle[0] / 1000.0, tz=CT_TZ)
        time_int = dt_ct.hour * 100 + dt_ct.minute

        # Case 9128: Combined ADX > 30 AND US Cash Session (08:30 to 14:30 CT)
        if fc == 9128:
            if not (830 <= time_int <= 1430):
                return False
            adx_val = ta.adx(self.candles, period=14)
            return adx_val > 30

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
            # Exit 7: Quick Spike Profit Limit Target
            if self.hp["exit_mode"] == 7:
                target_dist = atr * self.hp["spike_mult"]
                self.take_profit = self.position.qty, self.price + target_dist
        elif self.is_short:
            self.trough_price = self.price
            self.stop_loss = self.position.qty, self.price + stop_dist
            # Exit 7: Quick Spike Profit Limit Target
            if self.hp["exit_mode"] == 7:
                target_dist = atr * self.hp["spike_mult"]
                self.take_profit = self.position.qty, self.price - target_dist

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        giveback = self.hp["giveback_points"]
        mode = self.hp["exit_mode"]

        # Track peaks / troughs
        if self.is_long:
            if self.price > self.peak_price:
                self.peak_price = self.price
        elif self.is_short:
            if self.price < self.trough_price:
                self.trough_price = self.price

        # Exit 10: Stale Bar Exit (chop timeout)
        if mode == 10:
            bars_held = int((self.current_candle[0] - self.position.opened_at) / (15 * 60 * 1000))
            if bars_held >= self.hp["stale_bars"]:
                profit_dist = (self.price - self.position.entry_price) if self.is_long else (self.position.entry_price - self.price)
                if profit_dist < 20.0:
                    self.liquidate()
                    return

        # Exit 5: Protect Profit Ratio
        if mode == 5:
            trigger = self.hp["protect_trigger"]
            if self.is_long:
                max_gain = self.peak_price - self.position.entry_price
                if max_gain >= trigger:
                    current_gain = self.price - self.position.entry_price
                    if (current_gain / max_gain) < 0.50:
                        self.liquidate()
                        return
            elif self.is_short:
                max_gain = self.position.entry_price - self.trough_price
                if max_gain >= trigger:
                    current_gain = self.position.entry_price - self.price
                    if (current_gain / max_gain) < 0.50:
                        self.liquidate()
                        return

        # Exit 4: Trailing Peak Giveback (active across baseline and as backstop)
        if self.is_long:
            if (self.peak_price - self.price) >= giveback:
                self.liquidate()
        elif self.is_short:
            if (self.price - self.trough_price) >= giveback:
                self.liquidate()
