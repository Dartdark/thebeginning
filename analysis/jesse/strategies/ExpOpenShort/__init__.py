# Jesse port of funded_strategies/NQ_Expiration_Open_Short.txt (5-minute NQ).
from datetime import date, timedelta
from mcbase import MCBase

CLOSED_FRIDAYS = {date(2019, 4, 19), date(2022, 4, 15), date(2025, 4, 18), date(2026, 6, 19)}


class ExpOpenShort(MCBase):
    ENTRY, EXIT, STOP_ATR = 830, 1000, 0.30

    def _is_exp(self):
        d, dow = self.date, self.dow
        third_fri = dow == 5 and 15 <= d.day <= 21
        return (third_fri and d not in CLOSED_FRIDAYS) or (dow == 4 and d + timedelta(days=1) in CLOSED_FRIDAYS)

    def should_short(self):
        return self.real and self._is_exp() and self.hhmm == self.ENTRY and not self.traded_today() and self.atr > 0

    def should_long(self): return False

    def go_short(self):
        p, s = self.price, self.STOP_ATR * self.atr
        self.sell = 1, p; self.stop_loss = 1, p + s

    def update_position(self):
        if self.real and self.hhmm >= self.EXIT: self.liquidate()
