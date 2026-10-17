# Jesse port of the Overnight Bias family (15-minute NQ): apex_strategies/NQ_Overnight_Bias.txt (ADX 20, stop 0.30 ATR),
# NQ_Overnight_Bias_ADX30.txt (ADX 30, 0.25 ATR) and funded_strategies/NQ_Overnight_Bias_ML.txt (ADX 20, 0.30, ML filter).
import math
from mcbase import MCBase, early_close


class ONBias(MCBase):
    ON_START, ON_END, OR_END, FRAC, ADX_LEN, ADX_MIN, STOP_ATR, RR, LAST, EXIT = 2300, 830, 845, 0.3333, 14, 20, 0.30, 3, 1400, 1430
    BUF = 2 * 0.25
    ML = False; LONG_MIN, SHORT_MIN = 0.03, 0.0

    def __init__(self):
        super().__init__()
        self.in_on = self.on_ready = False; self.on_hi = self.on_lo = 0.0
        self.open_px = self.or_hi = self.or_lo = 0.0; self.or_done = False; self.bias = 0
        self.adx = 0.0; self._adx = dict(n=0, tr=[], pdm=[], mdm=[], str=None, sp=None, sm=None, dx=[], adx=None, ph=None, pl=None, pc=None)
        self.stop_pts = 0.0
        # ML filter state
        self.ch, self.oh, self.ah = [], [], []
        self.ml_prev_date = None; self.has_rth = False; self.cl1500 = 0.0; self.rth_open = 0.0
        self.ndays = 0; self.last_month = 0; self.month_count = 0
        self.skip_long = self.skip_short = False

    # ---- Wilder ADX on real bars (MultiCharts ADX: first smoothed values are sums / averages of the first Length) ----
    def _update_adx(self):
        a = self._adx; n = self.ADX_LEN
        if a["pc"] is None:
            a["ph"], a["pl"], a["pc"] = self.h, self.l, self.c; return
        up, dn = self.h - a["ph"], a["pl"] - self.l
        pdm = up if (up > dn and up > 0) else 0.0
        mdm = dn if (dn > up and dn > 0) else 0.0
        tr = max(self.h, a["pc"]) - min(self.l, a["pc"])
        a["ph"], a["pl"], a["pc"] = self.h, self.l, self.c
        if a["str"] is None:
            a["tr"].append(tr); a["pdm"].append(pdm); a["mdm"].append(mdm)
            if len(a["tr"]) < n: return
            a["str"], a["sp"], a["sm"] = sum(a["tr"]), sum(a["pdm"]), sum(a["mdm"])
        else:
            a["str"] = a["str"] - a["str"] / n + tr; a["sp"] = a["sp"] - a["sp"] / n + pdm; a["sm"] = a["sm"] - a["sm"] / n + mdm
        if a["str"] <= 0: return
        pdi, mdi = 100 * a["sp"] / a["str"], 100 * a["sm"] / a["str"]
        dx = 100 * abs(pdi - mdi) / (pdi + mdi) if pdi + mdi > 0 else 0.0
        if a["adx"] is None:
            a["dx"].append(dx)
            if len(a["dx"]) == n: a["adx"] = sum(a["dx"]) / n
        else:
            a["adx"] = (a["adx"] * (n - 1) + dx) / n
        self.adx = a["adx"] or 0.0

    def on_new_day(self):
        self.open_px = self.or_hi = self.or_lo = 0.0; self.or_done = False; self.bias = 0
        if not self.ML: return
        pd_ = self.ml_prev_date
        if pd_ is not None and 1 <= pd_.isoweekday() % 7 <= 5 and self.has_rth and self.cl1500 > 0 and self.rth_open > 0:
            self.ch.insert(0, self.cl1500); self.oh.insert(0, self.rth_open); self.ah.insert(0, self.atr_prev)
            del self.ch[100:], self.oh[100:], self.ah[100:]
            self.ndays += 1
            self.month_count = 1 if pd_.month != self.last_month else self.month_count + 1
            self.last_month = pd_.month
        self.ml_prev_date = self.date; self.has_rth = False; self.cl1500 = 0.0; self.rth_open = 0.0
        self.skip_long = self.skip_short = True       # file since 2026-10-17: no trades until the score is ready
        if self.ndays >= 59 and self.atr > 0:
            ch, ah = self.ch, self.ah; L = math.log
            r1, r5, r20, rth1 = L(ch[0] / ch[1]), L(ch[0] / ch[5]), L(ch[0] / ch[20]), L(ch[0] / self.oh[0])
            atr_ratio = self.atr / ((self.atr + sum(ah[:59])) / 60)
            dist50 = L(ch[0] / (sum(ch[:50]) / 50))
            rk = [L(ch[k] / ch[k + 1]) for k in range(20)]
            m5, m20 = sum(rk[:5]) / 5, sum(rk) / 20
            v5, v20 = sum((x - m5) ** 2 for x in rk[:5]), sum((x - m20) ** 2 for x in rk)
            rv = math.sqrt(v5 / 4) / math.sqrt(v20 / 19) if v20 > 0 else 1.0
            dow = self.dow
            tdm = 1 if self.date.month != self.last_month else self.month_count + 1
            fridom = self.date.day + (5 - dow)
            opex = 1 if (1 <= dow <= 5 and 15 <= fridom <= 21) else 0
            s = (0.05535517974 + 2.550842376 * r1 + 0.05697325462 * r5 - 0.08269967616 * r20 + 1.729498386 * rth1
                 - 0.03608247696 * atr_ratio - 0.3355796551 * dist50 - 0.03976333906 * rv
                 + 0.07809504609 * (dow == 1) - 0.008560935801 * (dow == 2) - 0.02267574106 * (dow == 3)
                 - 0.03459885088 * (dow == 4) - 0.005544247888 * (dow == 5) + 0.1654566373 * (tdm <= 3) - 0.003794081905 * opex)
            self.skip_long, self.skip_short = s < self.LONG_MIN, s < self.SHORT_MIN

    def on_bar(self):
        self._update_adx()
        t = self.hhmm
        if t > self.ON_START and not self.in_on:
            self.in_on, self.on_ready, self.on_hi, self.on_lo = True, False, self.h, self.l
        elif self.in_on:
            self.on_hi, self.on_lo = max(self.on_hi, self.h), min(self.on_lo, self.l)
            if t == self.ON_END: self.in_on, self.on_ready = False, True
        if self.on_ready and self.open_px == 0 and self.ON_END < t <= self.OR_END:
            self.open_px = self.o
            if self.on_hi > self.on_lo:
                pos = (self.open_px - self.on_lo) / (self.on_hi - self.on_lo)
                self.bias = 1 if pos >= 1 - self.FRAC else (-1 if pos <= self.FRAC else 0)
        if self.open_px > 0 and self.ON_END < t <= self.OR_END:
            if self.or_hi == 0: self.or_hi, self.or_lo = self.h, self.l
            else: self.or_hi, self.or_lo = max(self.or_hi, self.h), min(self.or_lo, self.l)
            if t == self.OR_END: self.or_done = True
        if self.ML:
            if 830 < t <= 845 and self.rth_open == 0: self.rth_open = self.o
            if t <= 1500: self.cl1500 = self.c
            if 1100 <= t <= 1515: self.has_rth = True
        ec = early_close(self.date)
        self.last_entry, self.day_exit = (1100, 1130) if ec else (self.LAST, self.EXIT)

    def _ok(self, side):
        if not self.real: return False
        if not (self.or_done and self.bias == side and self.atr > 0 and not self.traded_today()
                and self.OR_END <= self.hhmm < self.last_entry and self.adx > self.ADX_MIN): return False
        if self.ML and ((side == 1 and self.skip_long) or (side == -1 and self.skip_short)): return False
        return True

    def should_long(self): return self._ok(1)
    def should_short(self): return self._ok(-1)

    def go_long(self):
        self.stop_pts = self.STOP_ATR * self.atr
        self.buy = 1, (self.price if self.c >= self.or_hi - self.BUF else self.or_hi)

    def go_short(self):
        self.stop_pts = self.STOP_ATR * self.atr
        self.sell = 1, (self.price if self.c <= self.or_lo + self.BUF else self.or_lo)

    def on_open_position(self, order):
        e = self.position.entry_price; s = self.stop_pts
        if self.is_long:
            self.stop_loss = 1, e - s; self.take_profit = 1, e + self.RR * s
        else:
            self.stop_loss = 1, e + s; self.take_profit = 1, e - self.RR * s

    def update_position(self):
        if self.real and self.hhmm >= self.day_exit:
            self.liquidate()
