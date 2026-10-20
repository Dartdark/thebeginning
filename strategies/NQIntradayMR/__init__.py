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
    - Entry 4: Low-Volume / Low-Momentum Reversal
    - Iteration 1: Macro Trend-Aligned Fades (SMA 200 regime filter)
        * Only buy dips when Close > 200 SMA (uptrend)
        * Only sell rallies when Close < 200 SMA (downtrend)
    - Iteration 2B: Asymmetric Payoff Modulation (2.0x ATR target vs 1.5x ATR stop)
    - Exit 6: Tight Volatility Stop Loss (Entry +/- 1.5 * ATR)
    - Exit 7: Quick Spike Take-Profit Limit (Entry -/+ 2.0 * ATR back to mean)
    - Mandatory Intraday Flat: Liquidate at 15:50 CT (Zero overnight exposure)
    - Real Futures Friction: Evaluated on full 2018-2026 data under $17.25/NQ ($1.72/MNQ)
    """

    def hyperparameters(self):
        return [
            {"name": "lookback", "type": int, "min": 5, "max": 20, "default": 8},
            {"name": "atr_period", "type": int, "min": 5, "max": 25, "default": 14},
            {"name": "atr_mult_stop", "type": float, "min": 1.0, "max": 3.0, "default": 1.5, "step": 0.25},
            {"name": "atr_mult_target", "type": float, "min": 1.0, "max": 4.0, "default": 2.0, "step": 0.25},
            {"name": "adx_threshold", "type": int, "min": 15, "max": 35, "default": 25},
            {"name": "trend_ma_period", "type": int, "min": 50, "max": 250, "default": 200},
            {"name": "wick_ratio", "type": float, "min": 0.0, "max": 2.0, "default": 0.0, "step": 0.25},
        ]

    def _get_time_ct(self):
        dt_ct = datetime.fromtimestamp(self.current_candle[0] / 1000.0, tz=CT_TZ)
        return dt_ct.hour * 100 + dt_ct.minute

    def should_long(self) -> bool:
        lookback = self.hp["lookback"]
        ma_period = self.hp["trend_ma_period"]
        if len(self.candles) < max(lookback + 10, ma_period + 10):
            return False

        time_int = self._get_time_ct()
        # Only enter between 08:45 and 14:00 CT
        if not (845 <= time_int <= 1400):
            return False

        # Trend Filter: Only fade dips if macro trend is UP (Close > 200 SMA)
        ma_val = ta.sma(self.candles, period=ma_period)
        if self.close <= ma_val:
            return False

        # Regime Filter: ADX < threshold (Chop / Mean-Reverting regime, not trending)
        adx_val = ta.adx(self.candles, period=14)
        if adx_val >= self.hp["adx_threshold"]:
            return False

        # Entry 4 Condition: Volume below 10-bar average (exhaustion)
        vol_avg = np.mean(self.candles[-11:-1, 5])
        if self.current_candle[5] >= vol_avg:
            return False

        # Price hits lowest low of last X bars (excluding current bar) -> Fade the dip in an uptrend
        lowest_low = np.min(self.candles[-lookback - 1 : -1, 4])
        if self.close > lowest_low:
            return False

        # Entry 5: Rejection Wick Confirmation (if enabled)
        wick_ratio = self.hp.get("wick_ratio", 0.0)
        if wick_ratio > 0.0:
            c_open = self.current_candle[1]
            c_close = self.current_candle[2]
            c_low = self.current_candle[4]
            body = abs(c_close - c_open)
            lower_wick = min(c_open, c_close) - c_low
            if lower_wick < body * wick_ratio or lower_wick <= 0:
                return False

        return True

    def should_short(self) -> bool:
        lookback = self.hp["lookback"]
        ma_period = self.hp["trend_ma_period"]
        if len(self.candles) < max(lookback + 10, ma_period + 10):
            return False

        time_int = self._get_time_ct()
        # Only enter between 08:45 and 14:00 CT
        if not (845 <= time_int <= 1400):
            return False

        # Trend Filter: Only fade rallies if macro trend is DOWN (Close < 200 SMA)
        ma_val = ta.sma(self.candles, period=ma_period)
        if self.close >= ma_val:
            return False

        # Regime Filter: ADX < threshold (Chop / Mean-Reverting regime, not trending)
        adx_val = ta.adx(self.candles, period=14)
        if adx_val >= self.hp["adx_threshold"]:
            return False

        # Entry 4 Condition: Volume below 10-bar average (exhaustion)
        vol_avg = np.mean(self.candles[-11:-1, 5])
        if self.current_candle[5] >= vol_avg:
            return False

        # Price hits highest high of last X bars (excluding current bar) -> Fade the rally in a downtrend
        highest_high = np.max(self.candles[-lookback - 1 : -1, 3])
        if self.close < highest_high:
            return False

        # Entry 5: Rejection Wick Confirmation (if enabled)
        wick_ratio = self.hp.get("wick_ratio", 0.0)
        if wick_ratio > 0.0:
            c_open = self.current_candle[1]
            c_close = self.current_candle[2]
            c_high = self.current_candle[3]
            body = abs(c_close - c_open)
            upper_wick = c_high - max(c_open, c_close)
            if upper_wick < body * wick_ratio or upper_wick <= 0:
                return False

        return True

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
