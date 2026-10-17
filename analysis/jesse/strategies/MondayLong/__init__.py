# Jesse port of funded_strategies/NQ_Monday_Long.txt (5-minute NQ).
from mcbase import MCBase


def monday_early(d):
    m, dd, y = d.month, d.day, d.year
    return d.isoweekday() == 1 and ((m == 1 and dd in (1, 2)) or (m == 1 and 15 <= dd <= 21) or (m == 2 and 15 <= dd <= 21)
                                     or (m == 5 and dd >= 25) or (m == 6 and y >= 2022 and dd in (19, 20))
                                     or (m == 7 and dd in (4, 5)) or (m == 9 and dd <= 7) or (m == 12 and dd in (25, 26)))


class MondayLong(MCBase):
    ENTRY, EXIT, EARLY_EXIT, STOP_ATR = 830, 1500, 1145, 0.50

    def on_bar(self):
        self.ec = monday_early(self.date); self.day_exit = self.EARLY_EXIT if self.ec else self.EXIT

    def should_long(self):
        return (self.real and self.dow == 1 and not self.ec and self.hhmm == self.ENTRY and not self.traded_today()
                and self.atr > 0)

    def should_short(self): return False

    def go_long(self):
        p, s = self.price, self.STOP_ATR * self.atr
        self.buy = 1, p; self.stop_loss = 1, p - s

    def update_position(self):
        if self.real and self.hhmm >= self.day_exit: self.liquidate()
