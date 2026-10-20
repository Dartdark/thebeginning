from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQIBBreakout(Strategy):
    """
    Initial Balance (IB) RTH Momentum Breakout Strategy:
    - In-Sample Period: 2018-04-01 through 2022-12-31
    - Candidate Gate: Must achieve t >= 2.5 under $17.25 friction and 15:50 CT flat
    - Initial Balance: 08:30 to 09:30 CT (First 4 bars of 15m RTH session)
    - Breakout Entry Window: 10:00 to 11:45 CT (Post-open price discovery, institutional continuation)
    - Long Entry: Close > IB High AND Close > 200 SMA
    - Exits: Stop Loss (1.25x ATR), Take Profit (2.5x ATR, 2:1 R:R)
    - Mandatory Flat: 15:50 CT
    """

    def __init__(self):
        super().__init__()
        self.current_day = None
        self.ib_high = None
        self.ib_low = None
        self.ib_complete = False
        self.daily_longs = 0
        self.ib_bars = []

    def hyperparameters(self):
        return [
            {"name": "atr_period", "type": int, "min": 5, "max": 25, "default": 14},
            {"name": "atr_mult_stop", "type": float, "min": 0.5, "max": 2.5, "default": 1.25, "step": 0.25},
            {"name": "atr_mult_target", "type": float, "min": 1.0, "max": 4.0, "default": 2.5, "step": 0.25},
            {"name": "trend_ma_period", "type": int, "min": 50, "max": 250, "default": 200},
            {"name": "entry_start_time", "type": int, "min": 930, "max": 1030, "default": 1000},
            {"name": "entry_end_time", "type": int, "min": 1100, "max": 1300, "default": 1145},
        ]

    def _get_time_ct(self):
        dt_ct = datetime.fromtimestamp(self.current_candle[0] / 1000.0, tz=CT_TZ)
        time_int = dt_ct.hour * 100 + dt_ct.minute
        day_str = dt_ct.strftime("%Y-%m-%d")
        return day_str, time_int

    def before(self):
        day_str, time_int = self._get_time_ct()

        # Day transition
        if day_str != self.current_day:
            self.current_day = day_str
            self.ib_high = None
            self.ib_low = None
            self.ib_complete = False
            self.daily_longs = 0
            self.ib_bars = []

        # Collect 4 bars of Initial Balance: 08:30, 08:45, 09:00, 09:15 open times
        if 830 <= time_int <= 915:
            self.ib_bars.append(self.current_candle)
            if len(self.ib_bars) == 4:
                highs = [b[3] for b in self.ib_bars]
                lows = [b[4] for b in self.ib_bars]
                self.ib_high = max(highs)
                self.ib_low = min(lows)
                self.ib_complete = True

    def should_long(self) -> bool:
        if not self.ib_complete or self.daily_longs >= 1:
            return False

        day_str, time_int = self._get_time_ct()
        # Institutional continuation window: 10:00 to 11:45 CT
        start_t = self.hp.get("entry_start_time", 1000)
        end_t = self.hp.get("entry_end_time", 1145)
        if not (start_t <= time_int <= end_t):
            return False

        ma_period = self.hp["trend_ma_period"]
        if len(self.candles) < ma_period + 10:
            return False
        ma_val = ta.sma(self.candles, period=ma_period)
        if self.close <= ma_val:
            return False

        # Breakout condition: Close above IB High
        return self.close > self.ib_high

    def should_short(self) -> bool:
        return False

    def go_long(self):
        notional = min(self.available_margin * 0.5, self.price * 5)
        qty = utils.size_to_qty(notional, self.price, fee_rate=self.fee_rate)
        self.buy = qty, self.price
        self.daily_longs += 1

    def go_short(self):
        pass

    def on_open_position(self, order):
        atr = ta.atr(self.candles, period=self.hp["atr_period"])
        stop_dist = atr * self.hp["atr_mult_stop"]
        target_dist = atr * self.hp["atr_mult_target"]

        if self.is_long:
            self.stop_loss = self.position.qty, self.price - stop_dist
            self.take_profit = self.position.qty, self.price + target_dist

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        # Mandatory EOD exit: liquidate at 15:50 CT (Zero overnight exposure)
        day_str, time_int = self._get_time_ct()
        if time_int >= 1550:
            self.liquidate()
