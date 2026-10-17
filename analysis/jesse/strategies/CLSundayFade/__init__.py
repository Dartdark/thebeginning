# Jesse port of funded_strategies/CL_Sunday_Gap_Fade.txt (5-minute CL, Eastern exchange time as the confirmed chart).
from mcbase import MCBase


class CLSundayFade(MCBase):
    GAP_ATR, STOP_ATR, EXIT = 0.10, 0.75, 1000

    def __init__(self):
        super().__init__(); self.sunday_bar = 0; self.side = 0

    def on_new_day(self): self.sunday_bar = 0

    def on_bar(self):
        self.sunday_bar += 1; self.side = 0
        if self.dow == 0 and self.sunday_bar == 1 and self.atr > 0 and self.prev_real_close > 0:
            if self.o - self.prev_real_close >= self.GAP_ATR * self.atr: self.side = -1

    def should_short(self): return self.real and self.side == -1 and self.position.is_close
    def should_long(self): return False

    def go_short(self):
        p, s = self.price, self.STOP_ATR * self.atr; self.sell = 1, p; self.stop_loss = 1, p + s

    def update_position(self):
        if self.real and self.dow >= 1 and self.hhmm >= self.EXIT: self.liquidate()
