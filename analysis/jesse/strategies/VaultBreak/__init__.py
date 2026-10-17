# Jesse port of apex_strategies/NQ_Vault_Break.txt (30-minute NQ, longs only). Inputs as the file's defaults.
from mcbase import MCBase, early_close


class VaultBreak(MCBase):
    NOISE, FIRST, LAST, FLAT, TGT, STP, MAXT = 0.30, 1000, 1430, 1430, 40.0, 75.0, 3

    def __init__(self):
        super().__init__(); self.sess_open = 0.0; self.cpv = self.cv = 0.0; self.vwap = 0.0

    def on_new_day(self):
        self.sess_open = self.o; self.cpv = self.cv = 0.0

    def on_bar(self):
        v = float(self.current_candle[5])
        self.cpv += (self.h + self.l + self.c) / 3 * v; self.cv += v
        if self.cv > 0: self.vwap = self.cpv / self.cv
        ec = early_close(self.date)
        self.last_entry, self.flatten = (1100, 1130) if ec else (self.LAST, self.FLAT)

    def should_long(self):
        if not self.real or self.atr <= 0: return False
        noise = self.sess_open + self.NOISE * self.atr
        return (self.FIRST <= self.hhmm < self.last_entry and self.closed_today < self.MAXT
                and self.c > noise and self.c > self.vwap)

    def should_short(self): return False

    def go_long(self):
        p = self.price
        self.buy = 1, p
        self.stop_loss = 1, p - self.STP
        self.take_profit = 1, p + self.TGT

    def update_position(self):
        if self.real and self.hhmm >= self.flatten:
            self.liquidate()
