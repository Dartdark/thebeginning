# Jesse port of funded_strategies/ES_MOC_Follow.txt (5-minute ES), to check the MultiCharts spec against the Python test.
from mcbase import MCBase, early_close


class ESMOCFollow(MCBase):
    DEC, REF, EXIT, MIN_MOVE, STOP_ATR = 1450, 1400, 1500, 0.30, 0.25

    def __init__(self):
        super().__init__(); self.ref = 0.0; self.side = 0; self.stop_pts = 0.0

    def on_new_day(self): self.ref = 0.0

    def on_bar(self):
        if self.hhmm == self.REF: self.ref = self.c
        self.side = 0
        if (self.hhmm == self.DEC and not early_close(self.date) and self.ref > 0 and self.atr > 0
                and not self.traded_today()):
            mv = self.c - self.ref
            if abs(mv) >= self.MIN_MOVE * self.atr: self.side = 1 if mv > 0 else -1

    def should_long(self): return self.real and self.side == 1
    def should_short(self): return self.real and self.side == -1

    def go_long(self):
        p, s = self.price, self.STOP_ATR * self.atr; self.buy = 1, p; self.stop_loss = 1, p - s

    def go_short(self):
        p, s = self.price, self.STOP_ATR * self.atr; self.sell = 1, p; self.stop_loss = 1, p + s

    def update_position(self):
        if self.real and self.hhmm >= self.EXIT: self.liquidate()
