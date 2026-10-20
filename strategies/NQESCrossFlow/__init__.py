from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from jesse.strategies import Strategy
from jesse import utils
import jesse.indicators as ta

CT_TZ = ZoneInfo("America/Chicago")


class NQESCrossFlow(Strategy):
    """
    NQ / ES Post-Open Cross-Market Flow & Alignment Strategy — FAILED / REJECTED (Rank D)
    
    - Status: FAILED (Holdout t = 0.20; degrades Relative Strength 2023+ Sharpe 1.37 -> 1.22, DD +$16k)
    - Instrument: CME E-mini / Micro E-mini Nasdaq-100 Futures (NQ / MNQ)
    - Benchmark Reference: CME E-mini S&P 500 Futures (ES-USD)
    - Exact Rule (matching trades.csv & Claude audit in anti_nq_es_crossflow_test.py):
        Evaluates the 09:30 to 10:00 CT return of NQ vs ES.
        Residual = (NQ return) - 1.25 * (ES return).
        Normalizes residual via rolling 20-day mean & std: Z = (residual - mean) / std.
        If Z >= 1.25 and ES return > 0: Long at 10:01 CT open.
        If Z <= -1.25 and ES return < 0: Short at 10:01 CT open.
        Stop Loss: 0.60x 14-period daily ATR.
        Take Profit: 1.20x 14-period daily ATR.
        Mandatory EOD Flat: 15:00 CT.
    """

    def __init__(self):
        super().__init__()
        self.current_day = None
        self.daily_trades = 0
        self.past_res_1000 = []
        self.daily_atr = 80.0

    def hyperparameters(self):
        return [
            {"name": "z_thresh", "type": float, "min": 1.0, "max": 2.0, "default": 1.25, "step": 0.25},
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

    def _get_signal(self):
        day_str, time_int = self._get_time_ct()
        if time_int != 1000:
            return 0

        # Need 1m candles for NQ and ES
        nq_candles = self.candles
        es_candles = self.get_candles("Custom Data", "ES-USD", "1m")
        if len(nq_candles) < 31 or len(es_candles) < 31:
            return 0

        # Bar 30 mins ago was 09:30 CT close/open
        nq_open_930 = nq_candles[-30, 1]
        nq_close_1000 = self.close
        es_open_930 = es_candles[-30, 1]
        es_close_1000 = es_candles[-1, 2]

        if nq_open_930 <= 0 or es_open_930 <= 0:
            return 0

        ret_nq = (nq_close_1000 - nq_open_930) / nq_open_930
        ret_es = (es_close_1000 - es_open_930) / es_open_930

        residual = ret_nq - 1.25 * ret_es
        self.past_res_1000.append(residual)

        if len(self.past_res_1000) < 21:
            return 0

        prior_window = self.past_res_1000[-21:-1]
        m = float(np.mean(prior_window))
        s = float(np.std(prior_window))
        z = (residual - m) / s if s > 0 else 0.0

        thresh = self.hp.get("z_thresh", 1.25)

        # Long: Z >= 1.25 AND ES positive
        if z >= thresh and ret_es > 0:
            return 1
        # Short: Z <= -1.25 AND ES negative
        elif z <= -thresh and ret_es < 0:
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
        # Calculate daily ATR using daily candles if available, else standard proxy
        daily_candles = self.get_candles("Custom Data", "NQ-USD", "1D")
        if len(daily_candles) >= 15:
            atr_val = ta.atr(daily_candles, period=14)
        else:
            atr_val = 100.0

        stop_pts = self.hp.get("stop_mult", 0.6) * atr_val
        target_pts = self.hp.get("target_mult", 1.2) * atr_val

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
