from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQMondayLongV4(Strategy):
    def __init__(self):
        super().__init__()
        self._initialized_warmup = False
        self.current_ct_date = None
        self.day_high = None
        self.day_low = None
        self.day_close = None
        self.prev_date_last_close = None
        self.daily_trs = []
        self.current_close_dt_ct = None
        self.signal_atr = None
        self.trade_taken_today = False

    def _is_early_close_monday(self, d):
        m = d.month
        day = d.day
        y = d.year
        if m == 1 and (day == 1 or day == 2):
            return True
        if m == 1 and 15 <= day <= 21:
            return True
        if m == 2 and 15 <= day <= 21:
            return True
        if m == 5 and day >= 25:
            return True
        if y >= 2022 and m == 6 and (day == 19 or day == 20):
            return True
        if m == 7 and (day == 4 or day == 5):
            return True
        if m == 9 and 1 <= day <= 7:
            return True
        if m == 12 and (day == 25 or day == 26):
            return True
        return False

    def _process_5m_candle(self, candle):
        open_ts_ms = int(candle[0])
        close_ts_ms = open_ts_ms + 300_000
        b_high = float(candle[3])
        b_low = float(candle[4])
        b_close = float(candle[2])

        close_dt_ct = datetime.fromtimestamp(close_ts_ms / 1000.0, tz=CT_TZ)
        bar_date = close_dt_ct.date()

        if bar_date != self.current_ct_date:
            if self.current_ct_date is not None:
                if self.current_ct_date.weekday() < 5 and self.prev_date_last_close is not None:
                    tr = max(self.day_high, self.prev_date_last_close) - min(self.day_low, self.prev_date_last_close)
                    self.daily_trs.append(tr)
                self.prev_date_last_close = self.day_close
            self.current_ct_date = bar_date
            self.day_high = b_high
            self.day_low = b_low
            self.day_close = b_close
            self.trade_taken_today = False
        else:
            if b_high > self.day_high:
                self.day_high = b_high
            if b_low < self.day_low:
                self.day_low = b_low
            self.day_close = b_close

        self.current_close_dt_ct = close_dt_ct

    def before(self):
        if not self._initialized_warmup:
            self._initialized_warmup = True
            if len(self.candles) > 1:
                for c in self.candles[:-1]:
                    self._process_5m_candle(c)
        self._process_5m_candle(self.current_candle)

    def should_long(self) -> bool:
        if self.current_ct_date is None or self.current_close_dt_ct is None:
            return False
        if self.current_ct_date < datetime(2018, 1, 2).date():
            return False
        if self.current_ct_date.weekday() != 0:
            return False
        if self._is_early_close_monday(self.current_ct_date):
            return False
        if (self.current_close_dt_ct.hour, self.current_close_dt_ct.minute) != (8, 30):
            return False
        if self.trade_taken_today:
            return False
        if len(self.daily_trs) < 15:
            return False

        self.signal_atr = sum(self.daily_trs[-15:]) / 15.0
        self.trade_taken_today = True
        return True

    def should_short(self) -> bool:
        return False

    def go_long(self):
        notional_one_contract = min(self.available_margin * 0.5, self.price)
        qty = utils.size_to_qty(notional_one_contract, self.price, fee_rate=self.fee_rate)
        self.buy = qty, self.price

    def go_short(self):
        pass

    def on_open_position(self, order):
        if self.is_long and self.signal_atr is not None:
            stop_price = self.position.entry_price - 0.50 * self.signal_atr
            self.stop_loss = self.position.qty, stop_price
            # Variant 4: Limit take-profit at entry_price + 1.00 * ATR (2.0R)
            target_price = self.position.entry_price + 1.00 * self.signal_atr
            self.take_profit = self.position.qty, target_price

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        if self.is_long and self.current_close_dt_ct is not None:
            if (self.current_close_dt_ct.hour, self.current_close_dt_ct.minute) >= (15, 0):
                self.liquidate()
