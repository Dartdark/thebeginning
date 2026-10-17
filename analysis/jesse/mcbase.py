"""Shared MultiCharts-style bar logic for the Jesse ports of our strategies (2026-10-17).

Mirrors what every PowerLanguage file does at the top of each bar:
  - the bar's stamp is its CLOSE time (MultiCharts), Jesse's candle timestamp is its OPEN time;
  - volume-0 candles are minutes the market was closed (filled by build_candles.py): MultiCharts has no bar there,
    so they are skipped for all state (self.real is False);
  - Date <> Date[1]: the finished date's true range is stored if it was a weekday; ATR = mean of the last AtrDays;
  - CME early-close days (the list shared by VB / ONB / LDF);
  - trades closed today (MultiCharts' TotalTrades - DayStartTrades).
Sizes are 1 unit = 1 contract; P&L is read in points and converted outside (NQ $20, CL $1,000 per point).
"""
from datetime import datetime, timezone
from jesse.strategies import Strategy

TF_MIN = {"1m": 1, "5m": 5, "15m": 15, "30m": 30}


def early_close(d):
    m, dd, dow, y = d.month, d.day, d.isoweekday() % 7, d.year      # dow: 0 = Sunday .. 6 = Saturday (MultiCharts)
    wk = 1 <= dow <= 5
    return ((m == 1 and ((dd == 1 and wk) or (dd == 2 and dow == 1)))
            or (m == 1 and dow == 1 and 15 <= dd <= 21) or (m == 2 and dow == 1 and 15 <= dd <= 21)
            or (m == 5 and dow == 1 and dd >= 25)
            or (m == 6 and y >= 2022 and ((dd == 19 and wk) or (dd == 18 and dow == 5) or (dd == 20 and dow == 1)))
            or (m == 7 and (((dd == 3 or dd == 4) and wk) or (dd == 5 and dow == 1)))
            or (m == 9 and dow == 1 and dd <= 7)
            or (m == 11 and dow == 4 and 22 <= dd <= 28) or (m == 11 and dow == 5 and 23 <= dd <= 29)
            or (m == 12 and (((dd == 24 or dd == 25) and wk) or (dd == 26 and dow == 1))))


class MCBase(Strategy):
    ATR_DAYS = 15

    def __init__(self):
        super().__init__()
        self.prev_date = None; self.day_hi = self.day_lo = self.day_close = self.prev_day_close = 0.0
        self.tr_hist = []; self.atr = 0.0; self.closed_today = 0; self.new_day = False
        self.real = False; self.prev_real_close = 0.0; self.o = self.h = self.l = self.c = 0.0
        self.date = None; self.hhmm = 0; self.dow = 0

    # ---- hooks for subclasses ----
    def on_new_day(self): pass
    def on_bar(self): pass

    def before(self):
        cd = self.current_candle
        ts = int(cd[0]) + TF_MIN[self.timeframe] * 60000
        self.real = cd[5] > 0
        if not self.real:
            return
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        self.date = dt.date(); self.hhmm = dt.hour * 100 + dt.minute; self.dow = self.date.isoweekday() % 7
        self.o, self.c, self.h, self.l = float(cd[1]), float(cd[2]), float(cd[3]), float(cd[4])
        self.new_day = self.date != self.prev_date
        if self.new_day:
            if self.day_close > 0:
                if self.prev_date is not None and 1 <= self.prev_date.isoweekday() % 7 <= 5:
                    pc = self.prev_day_close
                    tr = (max(self.day_hi, pc) - min(self.day_lo, pc)) if pc > 0 else self.day_hi - self.day_lo
                    self.tr_hist = (self.tr_hist + [tr])[-self.ATR_DAYS:]
                self.prev_day_close = self.day_close
            self.atr_prev = self.atr
            self.day_hi, self.day_lo = self.h, self.l
            self.closed_today = 0
        else:
            self.day_hi, self.day_lo = max(self.day_hi, self.h), min(self.day_lo, self.l)
        self.day_close = self.c
        self.atr = sum(self.tr_hist) / self.ATR_DAYS if len(self.tr_hist) >= self.ATR_DAYS else 0.0
        if self.new_day:
            self.on_new_day()
        self.on_bar()
        self.prev_date = self.date

    def after(self):
        if self.real:
            self.prev_real_close = self.c

    def traded_today(self):
        return self.position.is_open or self.closed_today > 0

    def on_close_position(self, order, closed_trade=None):
        self.closed_today += 1

    def should_cancel_entry(self):
        return True

    # Jesse requires all four; one-sided strategies leave the other side off
    def should_long(self): return False
    def should_short(self): return False
    def go_long(self): pass
    def go_short(self): pass
