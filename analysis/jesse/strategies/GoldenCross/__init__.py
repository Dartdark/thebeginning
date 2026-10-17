# Port of Antigravity's GoldenCross (branch antigravity/jesse, strategies/GoldenCross) on our NQ candles (exchange clock CT):
# 50 / 200 SMA cross of RTH-only bars (9:30-16:00 ET = 8:30-15:00 CT, Mon-Fri), entries only in RTH, initial stop 3 x ATR(14)
# of RTH bars, trailing every bar (24 h), exit on the reverse cross. 1 contract (their risk_to_qty % sizing is dropped so
# results are per contract). FLAT_EOD = True adds the Apex rule: flat at the 15:00 CT RTH close, no overnight holds.
from datetime import datetime, timezone
from jesse.strategies import Strategy

TF = {"15m": 15, "30m": 30, "1h": 60}


class GoldenCross(Strategy):
    FAST, SLOW, STOP_ATR, ATR_N = 50, 200, 3.0, 14
    FLAT_EOD = False

    def __init__(self):
        super().__init__()
        self.closes = []; self.fast = []; self.slow = []; self.atr = None; self.prev_c = None; self._tr = []
        self.rth = False; self.hhmm = 0

    def before(self):
        cd = self.current_candle
        o_ts = int(cd[0]); dt = datetime.fromtimestamp(o_ts / 1000, tz=timezone.utc)
        self.hhmm = (dt + __import__("datetime").timedelta(minutes=TF[self.timeframe])).hour * 100 + (dt + __import__("datetime").timedelta(minutes=TF[self.timeframe])).minute
        op = dt.hour * 100 + dt.minute
        self.rth = dt.weekday() < 5 and 830 <= op < 1500 and cd[5] > 0
        if not self.rth: return
        c, h, l = float(cd[2]), float(cd[3]), float(cd[4])
        tr = h - l if self.prev_c is None else max(h, self.prev_c) - min(l, self.prev_c)
        if self.atr is None:
            self._tr.append(tr)
            if len(self._tr) == self.ATR_N: self.atr = sum(self._tr) / self.ATR_N
        else:
            self.atr = (self.atr * (self.ATR_N - 1) + tr) / self.ATR_N
        self.prev_c = c
        self.closes.append(c)
        if len(self.closes) > self.SLOW + 5: self.closes.pop(0)
        f = sum(self.closes[-self.FAST:]) / self.FAST if len(self.closes) >= self.FAST else None
        s = sum(self.closes[-self.SLOW:]) / self.SLOW if len(self.closes) >= self.SLOW else None
        self.fast = (self.fast + [f])[-2:]; self.slow = (self.slow + [s])[-2:]

    def _cross(self, up):
        if not self.rth or len(self.slow) < 2 or None in self.slow or None in self.fast or self.atr is None: return False
        if self.FLAT_EOD and self.hhmm >= 1500: return False
        a0, a1, b0, b1 = self.fast[0], self.fast[1], self.slow[0], self.slow[1]
        return (a0 <= b0 and a1 > b1) if up else (a0 >= b0 and a1 < b1)

    def should_long(self): return self._cross(True)
    def should_short(self): return self._cross(False)

    def go_long(self): self.buy = 1, self.price
    def go_short(self): self.sell = 1, self.price

    def on_open_position(self, order):
        d = self.atr * self.STOP_ATR
        self.stop_loss = 1, (self.price - d if self.is_long else self.price + d)

    def update_position(self):
        if self.FLAT_EOD and self.rth and self.hhmm >= 1500:
            self.liquidate(); return
        if self.atr is None: return
        d = self.atr * self.STOP_ATR
        if self.is_long:
            if self.price - d > self.average_stop_loss: self.stop_loss = 1, self.price - d
            if self.rth and self.fast[-1] is not None and self.fast[-1] < self.slow[-1]: self.liquidate()
        else:
            if self.price + d < self.average_stop_loss: self.stop_loss = 1, self.price + d
            if self.rth and self.fast[-1] is not None and self.fast[-1] > self.slow[-1]: self.liquidate()

    def should_cancel_entry(self): return True
