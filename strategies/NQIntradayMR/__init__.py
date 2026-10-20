from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQIntradayMR(Strategy):
    """
    Intraday Mean Reversion Strategy (Phase 1 & Phase 2 Compliant):
    - Entry 4: Low-Volume / Low-Momentum Reversal (Fade extremes when volume is low and ADX < 25)
    - Exit 6: Tight Volatility Stop Loss (Entry +/- 1.5 * ATR)
    - Exit 7: Quick Spike Take-Profit Limit (Entry -/+ 1.5 * ATR back to mean)
    - Mandatory Intraday Flat: Liquidate at 15:50 CT (Zero overnight exposure)
    - Real Futures Friction: Evaluated on full 2018-2026 data under $17.25/NQ ($1.72/MNQ)
    """

    def hyperparameters(self):
        return [
            {"name": "lookback", "type": int, "min": 5, "max": 20, "default": 8},
            {"name": "atr_period", "type": int, "min": 5, "max": 25, "default": 14},
            {"name": "atr_mult_stop", "type": float, "min": 1.0, "max": 3.0, "default": 1.5, "step": 0.5},
            {"name": "atr_mult_target", "type": float, "min": 1.0, "max": 3.0, "default": 1.5, "step": 0.5},
            {"name": "adx_threshold", "type": int, "min": 15, "max": 35, "default": 25},
        ]

    def _get_time_ct(self):
        dt_ct = datetime.fromtimestamp(self.current_candle[0] / 1000.0, tz=CT_TZ)
        return dt_ct.hour * 100 + dt_ct.minute

    def should_long(self) -> bool:
        lookback = self.hp["lookback"]
        if len(self.candles) < max(lookback + 10, 50):
            return False

        time_int = self._get_time_ct()
        # Only enter between 08:45 and 14:00 CT (leaves plenty of time to resolve before 15:50 CT flat)
        if not (845 <= time_int <= 1400):
            return False

        # Regime Filter: ADX < threshold (Chop / Mean-Reverting regime, not trending)
        adx_val = ta.adx(self.candles, period=14)
        if adx_val >= self.hp["adx_threshold"]:
            return False

        # Entry 4 Condition: Volume below 10-bar average (exhaustion)
        vol_avg = np.mean(self.candles[-11:-1, 5])
        if self.current_candle[5] >= vol_avg:
            return False

        # Price hits lowest low of last X bars (excluding current bar) -> Fade the low
        lowest_low = np.min(self.candles[-lookback - 1 : -1, 4])
        return self.close <= lowest_low

    def should_short(self) -> bool:
        lookback = self.hp["lookback"]
        if len(self.candles) < max(lookback + 10, 50):
            return False

        time_int = self._get_time_ct()
        # Only enter between 08:45 and 14:00 CT
        if not (845 <= time_int <= 1400):
            return False

        # Regime Filter: ADX < threshold (Chop / Mean-Reverting regime, not trending)
        adx_val = ta.adx(self.candles, period=14)
        if adx_val >= self.hp["adx_threshold"]:
            return False

        # Entry 4 Condition: Volume below 10-bar average (exhaustion)
        vol_avg = np.mean(self.candles[-11:-1, 5])
        if self.current_candle[5] >= vol_avg:
            return False

        # Price hits highest high of last X bars (excluding current bar) -> Fade the high
        highest_high = np.max(self.candles[-lookback - 1 : -1, 3])
        return self.close >= highest_high

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
        stop_dist = atr * self.hp["atr_mult_stop"]
        target_dist = atr * self.hp["atr_mult_target"]

        if self.is_long:
            self.stop_loss = self.position.qty, self.price - stop_dist
            self.take_profit = self.position.qty, self.price + target_dist
        elif self.is_short:
            self.stop_loss = self.position.qty, self.price + stop_dist
            self.take_profit = self.position.qty, self.price - target_dist

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        # Mandatory EOD exit: liquidate at 15:50 CT (Zero overnight exposure)
        time_int = self._get_time_ct()
        if time_int >= 1550:
            self.liquidate()
