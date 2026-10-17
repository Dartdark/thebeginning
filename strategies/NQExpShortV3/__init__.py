from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQExpShortV3(Strategy):
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

        self.closed_third_fridays = {
            datetime(2019, 4, 19).date(),
            datetime(2022, 4, 15).date(),
            datetime(2025, 4, 18).date(),
            datetime(2026, 6, 19).date(),
        }

    def _is_expiration_day(self, d):
        if d in self.closed_third_fridays:
            return False
        if d.weekday() == 4 and 15 <= d.day <= 21:
            return True
        fri = d + timedelta(days=1)
        if fri in self.closed_third_fridays:
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
        return False

    def should_short(self) -> bool:
        if self.current_ct_date is None or self.current_close_dt_ct is None:
            return False
        if self.current_ct_date < datetime(2018, 1, 2).date():
            return False
        if not self._is_expiration_day(self.current_ct_date):
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

    def go_long(self):
        pass

    def go_short(self):
        notional_one_contract = min(self.available_margin * 0.5, self.price)
        qty = utils.size_to_qty(notional_one_contract, self.price, fee_rate=self.fee_rate)
        self.sell = qty, self.price

    def on_open_position(self, order):
        if self.is_short and self.signal_atr is not None:
            stop_price = self.position.entry_price + 0.30 * self.signal_atr
            self.stop_loss = self.position.qty, stop_price

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        if self.is_short and self.current_close_dt_ct is not None:
            # Variant 3: Exit at 09:30 CT (end of Initial Balance) instead of 10:00 CT
            if (self.current_close_dt_ct.hour, self.current_close_dt_ct.minute) >= (9, 30):
                self.liquidate()
