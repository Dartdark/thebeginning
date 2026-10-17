from jesse.strategies import Strategy
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
CT = ZoneInfo("America/Chicago")


class NQExpirationOpenShort(Strategy):
    """
    Task 06 — NQ 3rd-Friday Monthly Options Expiration Open Short
    Phase 2 Verdict: Original baseline retained after strict 2018-2022 design /
    2023-2026 holdout validation.
    - Design (2018-2022): 60 trades, $18,317.20 net ($14.50 RT + $10 slip), Max DD $4,543.80
    - Holdout (2023-2026): 45 trades, $30,679.00 net ($14.50 RT + $10 slip), Max DD $7,467.20
    """

    def __init__(self):
        super().__init__()
        self.cur_day = None
        self.day_high = None
        self.day_low = None
        self.day_close = None
        self.prev_day_close = None
        self.tr_history = []
        self.daily_atr = None
        self.traded_today = False
        self.stop_price = None

    def _ct_dt(self):
        return datetime.fromtimestamp(self.current_candle[0] / 1000.0, tz=timezone.utc).astimezone(CT)

    def _is_third_friday(self, dt):
        return dt.weekday() == 4 and (15 <= dt.day <= 21)

    def _update_daily_atr(self, dt):
        d = dt.date()
        h = float(self.high)
        l = float(self.low)
        c = float(self.close)
        if self.cur_day is None:
            self.cur_day = d
            self.day_high = h
            self.day_low = l
            self.day_close = c
            return
        if d != self.cur_day:
            if self.day_high is not None and self.day_low is not None:
                if self.prev_day_close is not None:
                    tr = max(
                        self.day_high - self.day_low,
                        abs(self.day_high - self.prev_day_close),
                        abs(self.day_low - self.prev_day_close),
                    )
                else:
                    tr = self.day_high - self.day_low
                self.tr_history.append(tr)
                if len(self.tr_history) > 14:
                    self.tr_history.pop(0)
                if len(self.tr_history) == 14:
                    self.daily_atr = sum(self.tr_history) / 14.0
            self.prev_day_close = self.day_close
            self.cur_day = d
            self.day_high = h
            self.day_low = l
            self.day_close = c
            self.traded_today = False
        else:
            if h > self.day_high:
                self.day_high = h
            if l < self.day_low:
                self.day_low = l
            self.day_close = c

    def before(self):
        dt = self._ct_dt()
        self._update_daily_atr(dt)

    def should_long(self) -> bool:
        return False

    def should_short(self) -> bool:
        if self.traded_today:
            return False
        if self.daily_atr is None or self.daily_atr <= 0:
            return False
        dt = self._ct_dt()
        if not self._is_third_friday(dt):
            return False
        return dt.hour == 8 and dt.minute == 35

    def go_long(self):
        pass

    def go_short(self):
        entry = float(self.price)
        self.stop_price = entry + 0.35 * self.daily_atr
        self.sell = 1.0, entry
        self.traded_today = True

    def on_open_position(self, order):
        if self.is_short and self.stop_price is not None:
            self.stop_loss = self.position.qty, self.stop_price

    def update_position(self):
        dt = self._ct_dt()
        if (dt.hour == 10 and dt.minute >= 5) or dt.hour > 10:
            self.liquidate()

    def should_cancel_entry(self) -> bool:
        return True
