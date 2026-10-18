from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils


class NarangBlackBox(Strategy):
    """
    NarangBlackBox: Quantitative Systematic Trading Architecture (Iteration 3)
    Based on Rishi K. Narang's 'Inside the Black Box: A Simple Guide to Quantitative and High-Frequency Trading'
    (2nd Edition, John Wiley & Sons, ISBN: 978-1-118-41699-0).

    Controlled Refinement:
    1. Reverted to Iteration 1's superior middle-band equilibrium ratcheting.
    2. Tightened initial structural invalidation stop from 2.0x ATR to 1.6x ATR to improve the win/loss payoff ratio.
    3. Calibrated profit target to 2.5x ATR to capture the mean-reversion overshoot.
    """

    def __init__(self):
        super().__init__()
        self.bars_held = 0

    @property
    def ema_fast(self):
        return ta.ema(self.candles, 50)

    @property
    def ema_slow(self):
        return ta.ema(self.candles, 200)

    @property
    def adx(self):
        return ta.adx(self.candles, 14)

    @property
    def atr(self):
        return ta.atr(self.candles, 14)

    @property
    def bb(self):
        return ta.bollinger_bands(self.candles, period=20, devup=2.0, devdn=2.0)

    def should_long(self) -> bool:
        if len(self.candles) < 220:
            return False

        atr_val = self.atr
        bb_val = self.bb

        # 1. Macro Alpha Horizon (Structural Uptrend Regime)
        is_uptrend = (self.ema_fast > self.ema_slow) and (self.price > self.ema_slow) and (self.adx > 18)
        if not is_uptrend:
            return False

        # 2. Transaction Cost Model (TCM Hurdle)
        expected_alpha = bb_val.middleband - self.price
        if expected_alpha < 1.2 * atr_val:
            return False

        # 3. Micro Alpha Horizon (Statistical Mean-Reversion Pullback with Confirmation)
        pullback_touched = (self.low <= bb_val.lowerband) or (self.candles[-2][4] <= bb_val.lowerband)
        confirmed_bounce = (self.close > self.open) and (self.close > bb_val.lowerband)

        return pullback_touched and confirmed_bounce

    def should_short(self) -> bool:
        if len(self.candles) < 220:
            return False

        atr_val = self.atr
        bb_val = self.bb

        # 1. Macro Alpha Horizon (Structural Downtrend Regime)
        is_downtrend = (self.ema_fast < self.ema_slow) and (self.price < self.ema_slow) and (self.adx > 18)
        if not is_downtrend:
            return False

        # 2. Transaction Cost Model (TCM Hurdle)
        expected_alpha = self.price - bb_val.middleband
        if expected_alpha < 1.2 * atr_val:
            return False

        # 3. Micro Alpha Horizon (Statistical Mean-Reversion Rally with Confirmation)
        rally_touched = (self.high >= bb_val.upperband) or (self.candles[-2][3] >= bb_val.upperband)
        confirmed_rejection = (self.close < self.open) and (self.close < bb_val.upperband)

        return rally_touched and confirmed_rejection

    def go_long(self):
        atr_val = self.atr
        stop_price = self.price - 1.6 * atr_val

        # Risk Model: Volatility-budgeted sizing (1.5% risk per trade)
        qty = utils.risk_to_qty(
            self.available_margin,
            1.5,
            self.price,
            stop_price,
            fee_rate=self.fee_rate
        )

        max_notional = self.available_margin * self.leverage * 0.90
        max_qty = utils.size_to_qty(max_notional, self.price, fee_rate=self.fee_rate)
        qty = min(qty, max_qty)

        if qty > 0:
            self.buy = qty, self.price

    def go_short(self):
        atr_val = self.atr
        stop_price = self.price + 1.6 * atr_val

        # Risk Model: Volatility-budgeted sizing (1.5% risk per trade)
        qty = utils.risk_to_qty(
            self.available_margin,
            1.5,
            self.price,
            stop_price,
            fee_rate=self.fee_rate
        )

        max_notional = self.available_margin * self.leverage * 0.90
        max_qty = utils.size_to_qty(max_notional, self.price, fee_rate=self.fee_rate)
        qty = min(qty, max_qty)

        if qty > 0:
            self.sell = qty, self.price

    def on_open_position(self, order):
        self.bars_held = 0
        atr_val = self.atr

        # Risk Model: Tightened 1.6x ATR Invalidation Stop & 2.5x ATR Profit Target
        if self.is_long:
            self.stop_loss = self.position.qty, self.position.entry_price - 1.6 * atr_val
            self.take_profit = self.position.qty, self.position.entry_price + 2.5 * atr_val
        elif self.is_short:
            self.stop_loss = self.position.qty, self.position.entry_price + 1.6 * atr_val
            self.take_profit = self.position.qty, self.position.entry_price - 2.5 * atr_val

    def should_cancel_entry(self) -> bool:
        return True

    def update_position(self):
        self.bars_held += 1

        # Alpha Decay / Holding Horizon: If reversion does not complete within 24 bars (decay half-life), liquidate
        if self.bars_held >= 24:
            self.liquidate()
            return

        bb_val = self.bb
        atr_val = self.atr

        # Dynamic Risk Management: Middle-band equilibrium profit lock
        if self.is_long:
            if self.price > bb_val.middleband:
                new_stop = max(self.average_stop_loss, self.position.entry_price, bb_val.middleband - 0.5 * atr_val)
                if new_stop > self.average_stop_loss and new_stop < self.price:
                    self.stop_loss = self.position.qty, new_stop
        elif self.is_short:
            if self.price < bb_val.middleband:
                new_stop = min(self.average_stop_loss, self.position.entry_price, bb_val.middleband + 0.5 * atr_val)
                if new_stop < self.average_stop_loss and new_stop > self.price:
                    self.stop_loss = self.position.qty, new_stop
