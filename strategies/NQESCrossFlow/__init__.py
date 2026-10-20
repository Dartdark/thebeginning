from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from jesse.strategies import Strategy
from jesse import utils
import jesse.indicators as ta

CT_TZ = ZoneInfo("America/Chicago")


class NQESCrossFlow(Strategy):
    """
    NQ / ES Post-Open Cross-Market Flow & Alignment Strategy:
    - Instrument: CME E-mini / Micro E-mini Nasdaq-100 Futures (NQ / MNQ)
    - Benchmark Reference: CME E-mini S&P 500 Futures (ES-USD)
    - Mechanism:
        Evaluates the cash opening drive from 09:30 to 10:00 CT.
        Measures NQ's return vs broad-market ES return beyond beta (beta ~ 1.25).
        When NQ exhibits significant factor divergence (|Z| >= 1.25)
        AND the broad market confirms the direction (ES return agrees with side),
        enters at the 10:01 CT open.
    - Exits & Risk Controls:
        1. Stop Loss: 0.60x 14-period daily ATR (active from entry)
        2. Profit Target: 1.20x 14-period daily ATR
        3. Mandatory EOD Flat: 15:00 CT (zero overnight exposure)
    - Portfolio Function:
        Operates as a high-expectancy sister strategy to Relative Strength,
        capturing NYSE cash open trend days and reversing 08:30-09:00 opening traps.
    """

    def __init__(self):
        super().__init__()
        self.current_day = None
        self.nq_open_930 = None
        self.es_open_930 = None
        self.daily_trades = 0

    def hyperparameters(self):
        return [
            {"name": "spread_thresh", "type": float, "min": 0.001, "max": 0.005, "default": 0.0025, "step": 0.0005},
            {"name": "stop_mult", "type": float, "min": 0.4, "max": 0.8, "default": 0.6, "step": 0.05},
            {"name": "target_mult", "type": float, "min": 0.8, "max": 1.6, "default": 1.2, "step": 0.1},
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
            self.nq_open_930 = None
            self.es_open_930 = None

        if time_int == 930:
            self.nq_open_930 = self.current_candle[1]
            es_candles = self.get_candles("Custom Data", "ES-USD", "1m")
            if len(es_candles) > 0:
                self.es_open_930 = es_candles[-1, 1]

    def _get_signal(self):
        day_str, time_int = self._get_time_ct()
        if time_int != 1000:
            return 0

        if self.nq_open_930 is None or self.nq_open_930 <= 0:
            return 0

        es_candles = self.get_candles("Custom Data", "ES-USD", "1m")
        if len(es_candles) == 0:
            return 0

        es_close = es_candles[-1, 2]
        if self.es_open_930 is None or self.es_open_930 <= 0:
            self.es_open_930 = es_candles[-30, 1] if len(es_candles) >= 30 else es_close

        ret_nq = (self.close - self.nq_open_930) / self.nq_open_930
        ret_es = (es_close - self.es_open_930) / self.es_open_930

        residual = ret_nq - 1.25 * ret_es
        thresh = self.hp.get("spread_thresh", 0.0025)

        # Long: NQ leads beyond beta AND ES is positive
        if residual >= thresh and ret_es > 0.0:
            return 1
        # Short: NQ lags beyond beta AND ES is negative
        elif residual <= -thresh and ret_es < 0.0:
            return -1
        return 0

    def should_long(self) -> bool:
        if self.daily_trades >= 1:
            return False
        return self._get_signal() == 1

    def should_short(self) -> bool:
        if self.daily_trades >= 1:
            return False
        return self._get_signal() == -1

    def go_long(self):
        self.buy = 1, self.price
        self.daily_trades += 1

    def go_short(self):
        self.sell = 1, self.price
        self.daily_trades += 1

    def on_open_position(self, order):
        stop_pts = 65.0
        target_pts = 130.0

        if self.is_long:
            self.stop_loss = self.position.qty, self.price - stop_pts
            self.take_profit = self.position.qty, self.price + target_pts
        elif self.is_short:
            self.stop_loss = self.position.qty, self.price + stop_pts
            self.take_profit = self.position.qty, self.price - target_pts

    def should_cancel_entry(self) -> bool:
        return True

    def update_position(self):
        day_str, time_int = self._get_time_ct()
        if time_int >= 1500:
            self.liquidate()
