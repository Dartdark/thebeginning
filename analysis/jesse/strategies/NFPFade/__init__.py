# Jesse port of funded_strategies/NQ_NFP_Fade.txt (5-minute NQ).
from mcbase import MCBase


class NFPFade(MCBase):
    REF, SPIKE, REACT, EXIT, MULT, NDAYS, MAXDOM, STOP_ATR = 730, 735, 745, 900, 3.0, 20, 10, 0.50

    def __init__(self):
        super().__init__(); self.ref = 0.0; self.is_spike = False; self.sp = []; self.side = 0

    def on_new_day(self): self.ref = 0.0; self.is_spike = False

    def on_bar(self):
        t = self.hhmm
        if t == self.REF: self.ref = self.c
        if t == self.SPIKE and 1 <= self.dow <= 5:
            rng = self.h - self.l; base = 0.0
            if len(self.sp) >= self.NDAYS:
                s = sorted(self.sp[-self.NDAYS:]); base = (s[9] + s[10]) / 2
            self.is_spike = base > 0 and rng > self.MULT * base
            self.sp = (self.sp + [rng])[-self.NDAYS:]
        self.side = 0
        if (t == self.REACT and self.is_spike and self.dow == 5 and self.date.day <= self.MAXDOM and self.ref > 0
                and self.atr > 0 and not self.traded_today()):
            r = self.c - self.ref
            if r != 0: self.side = -1 if r > 0 else 1

    def should_long(self): return self.real and self.side == 1
    def should_short(self): return self.real and self.side == -1

    def go_long(self):
        p, s = self.price, self.STOP_ATR * self.atr; self.buy = 1, p; self.stop_loss = 1, p - s

    def go_short(self):
        p, s = self.price, self.STOP_ATR * self.atr; self.sell = 1, p; self.stop_loss = 1, p + s

    def update_position(self):
        if self.real and self.hhmm >= self.EXIT: self.liquidate()
