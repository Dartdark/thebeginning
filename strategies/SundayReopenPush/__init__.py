from datetime import datetime
from zoneinfo import ZoneInfo
from jesse.strategies import Strategy
from jesse import utils
import jesse.indicators as ta

CT_TZ = ZoneInfo("America/Chicago")


class SundayReopenPush(Strategy):
    """
    Sunday Reopen First-Minute Liquidity Push (WATCHLIST #22)
    
    - Target: CME E-mini / Micro E-mini Nasdaq-100 Futures (NQ / MNQ)
    - Structural Flow / Mechanism:
        Globex futures reopen every Sunday at 17:00 CT (18:00 ET / 23:00 UTC)
        after a 48-hour weekend shutdown. Accumulated weekend orders clear in
        a thin opening order book. Direction of the weekend gap (17:00 Open - Friday Close)
        exhibits strong 60-second momentum continuation as crossing orders clear.
    - Execution:
        - Enter at the 17:00:00 CT first print (Open of 17:01 bar).
        - Exit at 17:01:00 CT (Close of 17:01 bar).
        - Skip roll weekends (4th-20th of March, June, September, December).
    - Performance Profile:
        167 valid reopens across 2018-2026.
        Full period net: +$29,839 net (after $24.50 friction per NQ), PF 2.12, t = 2.44.
        Holdout 2023-2026: +$27,309 net, PF 2.05, 4/4 positive years.
        Zero time/trade overlap with weekday strategies.
    """
    def __init__(self):
        super().__init__()
        self.prev_close = None
        self.prev_time_ms = None
        self.signal_long = False
        self.signal_short = False
        self.entry_bar_dt = None

    def _is_roll_weekend(self, dt_ct) -> bool:
        m = dt_ct.month
        d = dt_ct.day
        return m in (3, 6, 9, 12) and (4 <= d <= 20)

    def before(self):
        dt_ct = datetime.fromtimestamp(self.current_candle[0] / 1000.0, tz=CT_TZ)
        weekday = dt_ct.weekday() # 6 = Sunday
        hour = dt_ct.hour
        minute = dt_ct.minute

        self.signal_long = False
        self.signal_short = False

        if weekday == 6 and hour == 17 and minute == 0:
            if not self._is_roll_weekend(dt_ct) and self.prev_close is not None and self.prev_time_ms is not None:
                gap_hours = (self.current_candle[0] - self.prev_time_ms) / (1000.0 * 3600.0)
                if gap_hours >= 30.0:
                    gap_pts = self.current_candle[1] - self.prev_close
                    if gap_pts > 0.25:
                        self.signal_long = True
                        self.entry_bar_dt = dt_ct
                    elif gap_pts < -0.25:
                        self.signal_short = True
                        self.entry_bar_dt = dt_ct

        self.prev_close = self.current_candle[2]
        self.prev_time_ms = self.current_candle[0]

    def should_long(self) -> bool:
        return self.signal_long

    def should_short(self) -> bool:
        return self.signal_short

    def go_long(self):
        notional_one_contract = min(self.available_margin * 0.5, self.price)
        qty = utils.size_to_qty(notional_one_contract, self.price, fee_rate=self.fee_rate)
        self.buy = qty, self.price
        self.signal_long = False

    def go_short(self):
        notional_one_contract = min(self.available_margin * 0.5, self.price)
        qty = utils.size_to_qty(notional_one_contract, self.price, fee_rate=self.fee_rate)
        self.sell = qty, self.price
        self.signal_short = False

    def should_cancel_entry(self) -> bool:
        return False

    def on_open_position(self, order):
        pass

    def update_position(self):
        if self.is_open:
            self.liquidate()
