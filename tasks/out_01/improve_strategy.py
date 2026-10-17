from datetime import datetime
from zoneinfo import ZoneInfo
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

# Raw CL_1min_*.csv timestamps were exported in Eastern Time and ingested assuming America/Chicago;
# decoding with America/Chicago recovers the exact Eastern clock timestamps (97 trades matching MultiCharts).
CSV_TZ = ZoneInfo("America/Chicago")


class CLSundayFade(Strategy):
    """
    Task 01 Phase 2 Evaluation:
    After testing 5 pre-registered mechanism-driven variants on the 2018-2022 design period
    (V1: Friday close limit target; V2: cap extreme shock gaps <= 1.00 ATR; V3: NYMEX RTH open 09:00 ET exit;
    V4: combined V1 + V2; V5: tighter 0.50 ATR stop), the original baseline specification
    (0.10 ATR minimum Sunday gap, 0.75 ATR stop, Monday 10:00 ET exit) could not be beaten simultaneously
    on both Net $ and Max Drawdown across both 2018-2022 and 2023-2026 without overfitting.
    V5 (0.50 ATR stop) reduced 2018-2022 Max Drawdown from $3,168.00 to $2,993.17 and slightly increased
    2023-2026 Net $ ($40,708.50 vs $40,646.00), but increased 2023-2026 Max Drawdown ($7,093.50 vs $5,182.50).
    Therefore, the original 3-parameter rule is retained unchanged as the production specification.
    """

    def __init__(self):
        super().__init__()
        self._initialized_warmup = False
        self.current_et_date = None
        self.is_first_bar_of_et_date = False
        self.day_high = None
        self.day_low = None
        self.day_close = None
        self.prev_date_last_close = None
        self.last_5m_close = None
        self.prev_5m_close = None
        self.daily_trs = []
        self.current_close_dt_et = None
        self.signal_atr = None

    def _process_5m_candle(self, candle):
        open_ts_ms = int(candle[0])
        close_ts_ms = open_ts_ms + 300_000
        b_open = float(candle[1])
        b_close = float(candle[2])
        b_high = float(candle[3])
        b_low = float(candle[4])

        close_dt_et = datetime.fromtimestamp(close_ts_ms / 1000.0, tz=CSV_TZ)
        bar_date = close_dt_et.date()

        if bar_date != self.current_et_date:
            self.is_first_bar_of_et_date = True
            self.prev_5m_close = self.last_5m_close
            if self.current_et_date is not None:
                if self.current_et_date.weekday() < 5 and self.prev_date_last_close is not None:
                    tr = max(self.day_high, self.prev_date_last_close) - min(self.day_low, self.prev_date_last_close)
                    self.daily_trs.append(tr)
                self.prev_date_last_close = self.day_close
            self.current_et_date = bar_date
            self.day_high = b_high
            self.day_low = b_low
            self.day_close = b_close
        else:
            self.is_first_bar_of_et_date = False
            if b_high > self.day_high:
                self.day_high = b_high
            if b_low < self.day_low:
                self.day_low = b_low
            self.day_close = b_close

        self.last_5m_close = b_close
        self.current_close_dt_et = close_dt_et

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
        if not self.is_first_bar_of_et_date:
            return False
        if self.current_et_date is None or self.current_et_date.weekday() != 6:
            return False
        if self.current_et_date.year < 2018:
            return False
        if len(self.daily_trs) < 15 or self.prev_5m_close is None:
            return False

        atr = sum(self.daily_trs[-15:]) / 15.0
        gap = self.open - self.prev_5m_close
        if gap >= 0.10 * atr:
            self.signal_atr = atr
            return True
        return False

    def go_long(self):
        pass

    def go_short(self):
        notional_one_contract = min(self.available_margin * 0.5, self.price)
        qty = utils.size_to_qty(notional_one_contract, self.price, fee_rate=self.fee_rate)
        self.sell = qty, self.price

    def on_open_position(self, order):
        if self.is_short and self.signal_atr is not None:
            stop_price = self.position.entry_price + 0.75 * self.signal_atr
            self.stop_loss = self.position.qty, stop_price

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        if self.is_short and self.current_close_dt_et is not None:
            if self.current_et_date.weekday() == 0 and (
                self.current_close_dt_et.hour,
                self.current_close_dt_et.minute,
            ) >= (10, 0):
                self.liquidate()
