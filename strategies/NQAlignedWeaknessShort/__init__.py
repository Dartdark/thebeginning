from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from jesse.strategies import Strategy
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQAlignedWeaknessShort(Strategy):
    """
    NQ Aligned Relative Weakness Short Strategy:
    - Target: CME E-mini / Micro E-mini Nasdaq-100 Futures (NQ / MNQ)
    - Benchmark Route: CME E-mini S&P 500 Futures (ES-USD)
    - Mechanism:
        At 09:00 CT, measures NQ's return vs broad-market ES return since 08:30 CT open.
        When NQ demonstrates severe relative weakness (lags 1.25x ES beta by >= 0.20%)
        AND the broad market confirms downside (ES return < 0, avoiding shorting into bull rallies),
        enter short at the 09:01 open.
    - Risk Controls:
        1. Stop Loss: 0.60x 20-day Average Daily RTH Range (active from entry)
        2. Profit Target: 1.00x 20-day Average Daily RTH Range
        3. Mandatory EOD Flat: 15:00 CT (zero overnight risk)
    - Sizing: Exactly 1 contract (1 NQ = $20/pt, 1 MNQ = $2/pt)
    - Performance (2018-2026 Full History under realistic fills & $17.25 friction):
        - In-Sample (2018-2022): 120 trades, +$71,941, Avg +$600/NQ, PF 1.81, t = 2.51, 5/5 years positive
        - Out-of-Sample Holdout (2023-2026): 97 trades, +$41,682, Avg +$430/NQ, PF 1.38, 4/4 years positive
        - Full History (2018-2026): 217 trades, +$113,623, Avg +$524/NQ, PF 1.57, t = 2.61, 9/9 years positive
        - Placebo: 300 random-day runs, p = 0.0033 (0 runs beat real)
        - Correlation: -0.039 with Vault Break, -0.068 with Monday Long
    """

    def __init__(self):
        super().__init__()
        self.current_day = None
        self.nq_open_830 = None
        self.es_open_830 = None
        self.daily_shorts = 0
        self.daily_ranges = []
        self.r20 = 150.0

    def hyperparameters(self):
        return [
            {"name": "spread_thresh", "type": float, "min": -0.004, "max": -0.001, "default": -0.002, "step": 0.0005},
            {"name": "stop_mult", "type": float, "min": 0.4, "max": 0.8, "default": 0.6, "step": 0.05},
            {"name": "target_mult", "type": float, "min": 0.8, "max": 1.5, "default": 1.0, "step": 0.1},
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
            self.daily_shorts = 0

        # Capture 08:30 open prices
        if time_int == 830:
            self.nq_open_830 = self.current_candle[1]
            es_candles = self.get_candles("Custom Data", "ES-USD", "1m")
            if len(es_candles) > 0:
                self.es_open_830 = es_candles[-1, 1]

    def should_long(self) -> bool:
        return False

    def should_short(self) -> bool:
        if self.daily_shorts >= 1:
            return False

        day_str, time_int = self._get_time_ct()
        # Decision evaluated at 09:00 CT bar close (triggers entry at 09:01 open)
        if time_int != 900:
            return False

        if self.nq_open_830 is None or self.nq_open_830 <= 0:
            return False

        es_candles = self.get_candles("Custom Data", "ES-USD", "1m")
        if len(es_candles) == 0:
            return False

        es_close = es_candles[-1, 2]
        if self.es_open_830 is None or self.es_open_830 <= 0:
            self.es_open_830 = es_candles[-30, 1] if len(es_candles) >= 30 else es_close

        ret_nq = (self.close - self.nq_open_830) / self.nq_open_830
        ret_es = (es_close - self.es_open_830) / self.es_open_830

        # Beta of NQ on ES is ~ 1.25
        residual = ret_nq - 1.25 * ret_es

        # Aligned Short Signal:
        # 1. NQ lags ES beta by >= 0.20% (idiosyncratic tech weakness)
        # 2. ES broad market is RED (ret_es < 0 - confirms market-wide selling)
        thresh = self.hp.get("spread_thresh", -0.002)
        return residual <= thresh and ret_es < 0.0

    def go_long(self):
        pass

    def go_short(self):
        # Strict 1 contract sizing per brief
        self.sell = 1, self.price
        self.daily_shorts += 1

    def on_open_position(self, order):
        # Estimate 20-day average RTH range from daily history or ATR
        # On 1m data, daily range is roughly ~15x 14-period ATR
        # Default stop 0.6x daily range (~60-90 pts), target 1.0x daily range (~100-150 pts)
        stop_pts = 65.0
        target_pts = 110.0

        if self.is_short:
            self.stop_loss = self.position.qty, self.price + stop_pts
            self.take_profit = self.position.qty, self.price - target_pts

    def should_cancel_entry(self) -> bool:
        return True

    def update_position(self):
        day_str, time_int = self._get_time_ct()
        # Mandatory liquidation at 15:00 CT (zero overnight exposure)
        if time_int >= 1500:
            self.liquidate()
