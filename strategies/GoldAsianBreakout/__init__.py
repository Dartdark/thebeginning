from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from jesse.strategies import Strategy
from jesse import utils
import jesse.indicators as ta

CT_TZ = ZoneInfo("America/Chicago")


class GoldAsianBreakout(Strategy):
    """
    COMEX Gold Asian-Range Breakout Strategy (GoldAsianBreakout)
    
    - Target Instrument: CME Micro Gold Futures (MGC / GC)
    - Macro / Structural Reason:
        Asian trading (20:00 to 00:00 CT) forms a consolidated physical bullion liquidity range.
        London physical fixing desks and European bullion institutions begin pre-open positioning
        at 00:00 CT. Clean breakouts during 00:00-02:00 CT capture sustained trend momentum
        that persists through the European morning to 12:00 CT.
    - Risk Controls:
        1. Asian Range: High and Low established between 20:00 and 23:59 CT.
        2. Execution Window: 00:00 to 01:59 CT.
        3. Filter B: Cancel unfilled orders at 02:00 CT (avoids late, decayed fills).
        4. Filter D: Trade breakouts opposite to yesterday's daily candle direction.
        5. Stop Loss: 1.0x Range width.
        6. Profit Target: 1.5x Range width.
        7. Mandatory Exit: 12:00 CT.
    """

    def __init__(self):
        super().__init__()
        self.current_day = None
        self.asian_high = None
        self.asian_low = None
        self.range_width = 0.0
        self.yesterday_dir = 0
        self.daily_trades = 0
        self.armed = False

    def hyperparameters(self):
        return [
            {"name": "stop_mult", "type": float, "min": 0.5, "max": 1.5, "default": 1.0, "step": 0.1},
            {"name": "target_mult", "type": float, "min": 1.0, "max": 2.5, "default": 1.5, "step": 0.25},
            {"name": "use_filter_d", "type": bool, "default": True},
        ]

    def _get_time_ct(self):
        dt_ct = datetime.fromtimestamp(self.current_candle[0] / 1000.0, tz=CT_TZ)
        time_int = dt_ct.hour * 100 + dt_ct.minute
        day_str = dt_ct.strftime("%Y-%m-%d")
        return day_str, time_int

    def before(self):
        day_str, time_int = self._get_time_ct()
        if day_str != self.current_day:
            self.current_day = day_str
            self.daily_trades = 0
            self.armed = False

        # Asian range: 20:00 to 23:59 CT
        if 2000 <= time_int <= 2359:
            if self.asian_high is None or self.high > self.asian_high:
                self.asian_high = self.high
            if self.asian_low is None or self.low < self.asian_low:
                self.asian_low = self.low
            self.range_width = self.asian_high - self.asian_low

        # At 00:00 CT, arm orders
        if time_int == 0 and self.range_width >= 1.0:
            self.armed = True

        # Filter B: At 02:00 CT, disarm if not entered
        if time_int >= 200:
            self.armed = False

    def should_long(self) -> bool:
        if self.daily_trades >= 1 or not self.armed:
            return False
        day_str, time_int = self._get_time_ct()
        if not (0 <= time_int < 200):
            return False

        use_fd = self.hp.get("use_filter_d", True)
        if use_fd and self.yesterday_dir == 1:
            return False

        return self.close >= self.asian_high

    def should_short(self) -> bool:
        if self.daily_trades >= 1 or not self.armed:
            return False
        day_str, time_int = self._get_time_ct()
        if not (0 <= time_int < 200):
            return False

        use_fd = self.hp.get("use_filter_d", True)
        if use_fd and self.yesterday_dir == -1:
            return False

        return self.close <= self.asian_low

    def go_long(self):
        self.buy = 1, self.price
        self.daily_trades += 1
        self.armed = False

    def go_short(self):
        self.sell = 1, self.price
        self.daily_trades += 1
        self.armed = False

    def on_open_position(self, order):
        stop_dist = self.hp.get("stop_mult", 1.0) * self.range_width
        target_dist = self.hp.get("target_mult", 1.5) * self.range_width

        if self.is_long:
            self.stop_loss = self.position.qty, self.price - stop_dist
            self.take_profit = self.position.qty, self.price + target_dist
        elif self.is_short:
            self.stop_loss = self.position.qty, self.price + stop_dist
            self.take_profit = self.position.qty, self.price - target_dist

    def should_cancel_entry(self) -> bool:
        day_str, time_int = self._get_time_ct()
        return time_int >= 200

    def update_position(self):
        day_str, time_int = self._get_time_ct()
        if time_int >= 1200:
            self.liquidate()
