# Jesse port of funded_strategies/NQ_Late_Day_Flow.txt (5-minute NQ).
from mcbase import MCBase, early_close


class LateDayFlow(MCBase):
    OPEN_BAR, SIGNAL, EXIT, MIN_MOVE, STOP_ATR = 835, 1400, 1430, 0.40, 0.25

    def __init__(self):
        super().__init__(); self.open_px = 0.0; self.side = 0

    def on_new_day(self): self.open_px = 0.0

    def on_bar(self):
        if self.hhmm == self.OPEN_BAR: self.open_px = self.o
        self.side = 0
        if (self.hhmm == self.SIGNAL and not early_close(self.date) and self.open_px > 0 and self.atr > 0
                and not self.traded_today()):
            mv = self.c - self.open_px
            if abs(mv) >= self.MIN_MOVE * self.atr: self.side = 1 if mv > 0 else -1

    def should_long(self): return self.real and self.side == 1
    def should_short(self): return self.real and self.side == -1

    def go_long(self):
        p, s = self.price, self.STOP_ATR * self.atr; self.buy = 1, p; self.stop_loss = 1, p - s

    def go_short(self):
        p, s = self.price, self.STOP_ATR * self.atr; self.sell = 1, p; self.stop_loss = 1, p + s

    def update_position(self):
        if self.real and self.hhmm >= self.EXIT: self.liquidate()
