from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQRelWeaknessShort(Strategy):
    """
    NQ Relative Weakness Intraday Short Strategy:
    - Target: CME E-mini / Micro E-mini Nasdaq-100 Futures (NQ-USD)
    - Data Route: CME E-mini S&P 500 Futures (ES-USD)
    - Initial Balance: 08:30 to 09:30 CT (First hour of RTH session)
    - Breakdown Window: 09:30 to 11:30 CT
    - Entry Signal (Shorts Only):
        1. NQ Close < Initial Balance Low
        2. Relative Weakness: NQ % return from 08:30 open lags ES % return by >= 0.25%
        3. ES Alignment: ES is below its 08:30 open (broad market is not rallying)
    - Risk Controls:
        1. Stop Loss: 1.25x ATR(14)
        2. Profit Target: 2.0x ATR(14)
        3. Breakeven Ratchet: When profit reaches +1.0x ATR, stop moves to Breakeven (+1 pt)
        4. Mandatory EOD liquidation: 15:00 CT (Zero overnight exposure)
    - Position Sizing: Exactly 1 contract (1 NQ = $20/pt, 1 MNQ = $2/pt)
    """

    def __init__(self):
        super().__init__()
        self.current_day = None
        self.nq_open_830 = None
        self.es_open_830 = None
        self.ib_low = None
        self.ib_complete = False
        self.daily_shorts = 0
        self.ib_bars = []
        self.entry_price = 0.0
        self.atr_val = 0.0
        self.be_active = False

    def hyperparameters(self):
        return [
            {"name": "atr_period", "type": int, "min": 5, "max": 25, "default": 14},
            {"name": "atr_mult_stop", "type": float, "min": 0.75, "max": 2.0, "default": 1.25, "step": 0.25},
            {"name": "atr_mult_target", "type": float, "min": 1.0, "max": 3.0, "default": 2.0, "step": 0.25},
            {"name": "spread_threshold", "type": float, "min": -0.005, "max": -0.001, "default": -0.0025, "step": 0.0005},
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
            self.nq_open_830 = None
            self.es_open_830 = None
            self.ib_low = None
            self.ib_complete = False
            self.daily_shorts = 0
            self.ib_bars = []
            self.entry_price = 0.0
            self.atr_val = 0.0
            self.be_active = False

        # Capture 08:30 open prices
        if time_int == 830:
            self.nq_open_830 = self.current_candle[1]
            es_candles = self.get_candles("Custom Data", "ES-USD", "15m")
            if len(es_candles) > 0:
                self.es_open_830 = es_candles[-1, 1]

        # Initial balance: 08:30 to 09:30 CT (bars open at 08:30, 08:45, 09:00, 09:15)
        if 830 <= time_int <= 915:
            self.ib_bars.append(self.current_candle)
            if len(self.ib_bars) == 4:
                lows = [b[4] for b in self.ib_bars]
                self.ib_low = min(lows)
                self.ib_complete = True

    def should_long(self) -> bool:
        return False

    def should_short(self) -> bool:
        if not self.ib_complete or self.daily_shorts >= 1:
            return False

        day_str, time_int = self._get_time_ct()
        # Breakdown entry window: 09:30 to 11:30 CT
        if not (930 <= time_int <= 1130):
            return False

        if self.nq_open_830 is None or self.nq_open_830 <= 0:
            return False

        # NQ breakdown below IB Low
        if self.close >= self.ib_low:
            return False

        # Check ES relative performance
        es_candles = self.get_candles("Custom Data", "ES-USD", "15m")
        if len(es_candles) == 0:
            return False

        es_close = es_candles[-1, 2] # latest close of ES
        if self.es_open_830 is None or self.es_open_830 <= 0:
            self.es_open_830 = es_candles[-4, 1] if len(es_candles) >= 4 else es_close

        ret_nq = (self.close - self.nq_open_830) / self.nq_open_830
        ret_es = (es_close - self.es_open_830) / self.es_open_830
        spread = ret_nq - 1.25 * ret_es

        # Spread must be below threshold (e.g. -0.25%) AND ES must be below its open
        thresh = self.hp.get("spread_threshold", -0.0025)
        return spread <= thresh and es_close < self.es_open_830

    def go_long(self):
        pass

    def go_short(self):
        # Strict 1-contract sizing per specification
        self.sell = 1, self.price
        self.daily_shorts += 1
        self.entry_price = self.price
        self.be_active = False

    def on_open_position(self, order):
        atr = ta.atr(self.candles, period=self.hp["atr_period"])
        self.atr_val = atr
        stop_dist = atr * self.hp["atr_mult_stop"]
        target_dist = atr * self.hp["atr_mult_target"]

        if self.is_short:
            self.stop_loss = self.position.qty, self.price + stop_dist
            self.take_profit = self.position.qty, self.price - target_dist

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        day_str, time_int = self._get_time_ct()

        # Breakeven ratchet: once price drops +1.0x ATR in profit, lock stop to breakeven + 1 pt
        if self.is_short and not self.be_active and self.atr_val > 0:
            if self.entry_price - self.price >= self.atr_val:
                be_stop = self.entry_price - 1.0 # lock in 1 pt profit
                self.stop_loss = self.position.qty, be_stop
                self.be_active = True

        # Mandatory flat by 15:00 CT
        if time_int >= 1500:
            self.liquidate()
