"""Unvalidated research event core for SSRN6722841's explicit native adaptation.

No broker/network/order API. No historical-data runner or account claims.
Consumes verified completed-M15 snapshots and native minute OHLC events.
See agents/codex/plans/us100_donchian_6722841_build_20261108.md.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import floor, isfinite
from typing import Optional


class InputError(ValueError):
    pass


def aware(t):
    if t.tzinfo is None or t.utcoffset() is None:
        raise InputError("Event clocks must be timezone-aware")


@dataclass(frozen=True)
class Minute:
    start: datetime
    open: float
    high: float
    low: float
    close: float
    contract: str
    closed_session_gap: bool = False

    def validate(self):
        aware(self.start)
        if self.start.second or self.start.microsecond:
            raise InputError("Minute start must be an exact minute boundary")
        values = (self.open, self.high, self.low, self.close)
        if not all(isfinite(x) and x > 0 for x in values):
            raise InputError("Invalid OHLC")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close):
            raise InputError("OHLC bounds do not contain open/close")
        if not self.contract:
            raise InputError("Native dated contract identity required")


@dataclass(frozen=True)
class Snapshot:
    known_at: datetime
    previous_close: float
    entry_high: float
    exit_low: float
    atr: float

    def validate(self, now):
        aware(self.known_at)
        if self.known_at != now or now.minute % 15:
            raise InputError("Snapshot must become available at this M15 boundary")
        if not all(isfinite(x) and x > 0 for x in
                   (self.previous_close, self.entry_high, self.exit_low, self.atr)):
            raise InputError("Invalid indicator snapshot")
        if self.entry_high < self.exit_low:
            raise InputError("Entry160 high cannot be below contained exit60 low")


@dataclass(frozen=True)
class Policy:
    """Must be provided by an independently audited session/roll calendar."""
    allow_entry: bool
    force_flat: bool
    calendar_id: str

    def validate(self):
        if not self.calendar_id:
            raise InputError("Missing audited calendar policy identity")
        if self.force_flat and self.allow_entry:
            raise InputError("Flatten policy cannot permit an entry")


@dataclass
class Position:
    entry_time: datetime
    entry: float
    stop: float
    contract: str


@dataclass(frozen=True)
class Trade:
    entry_time: datetime
    exit_time: datetime
    entry: float
    exit: float
    reason: str
    contract: str
    fee: float
    net: float


class NativeCore:
    """One integer MNQ, long only; costs separate from native indicator prices.

    M15 snapshots are not computed here: exact ATR seed/smoothing and data
    admission remain prerequisites. This is not an exact broker-US100 replay.
    Price OHLC has no bid/ask: one adverse tick per market/stop fill is a
    research assumption, not measured spread. Tick/point values are native MNQ.
    """

    def __init__(self, ticks=1, fee=1.04):
        if not isinstance(ticks, int) or isinstance(ticks, bool) or ticks < 0:
            raise InputError("Slippage must be nonnegative integer ticks")
        if not isfinite(fee) or fee < 0:
            raise InputError("Invalid round-trip commission")
        self.tick = 0.25
        self.value = 2.0
        self.slip = ticks * self.tick
        self.fee = float(fee)
        self.position: Optional[Position] = None
        self.cash = 0.0
        self.trades = []
        self.last_time = None
        self.last_contract = None

    def stop_tick(self, price):
        return floor((price + 1e-10) / self.tick) * self.tick

    def _close(self, raw_price, minute, reason):
        p = self.position
        if p is None:
            raise InputError("No position to close")
        fill = raw_price - self.slip
        net = (fill - p.entry) * self.value - self.fee
        # 'exit_time' is the minute start whose OHLC establishes the fill.
        # A protective stop within that minute has unresolved subminute time.
        self.trades.append(Trade(p.entry_time, minute.start, p.entry, fill,
                                 reason, p.contract, self.fee, net))
        self.cash += net
        self.position = None

    def step(self, minute, policy, snapshot=None):
        """Advance one audited minute. Returns closed cash and adverse/close marks.

        Existing stops at a gap-open precede M15 signal management. New/trailing
        stops are active on this minute. Exit-minute marks cap at stop fill;
        do not mark a position after its protective liquidation.
        Roll switches with an open position and unclassified missing time fail.
        """
        minute.validate()
        policy.validate()
        if snapshot is not None:
            snapshot.validate(minute.start)
        if self.last_time is not None:
            if minute.start <= self.last_time:
                raise InputError("Duplicate or backwards event")
            if minute.start - self.last_time != timedelta(minutes=1):
                if self.position and not minute.closed_session_gap:
                    raise InputError("Unresolved missing tradable minutes")
            if self.position and minute.contract != self.last_contract:
                raise InputError("Cannot carry a continuous-contract splice")
        if self.position and minute.contract != self.position.contract:
            raise InputError("Position native contract mismatch")
        self.last_time = minute.start
        self.last_contract = minute.contract
        cash_at_start = self.cash
        open_marks = ([self.cash+(minute.open-self.position.entry)*self.value-self.fee]
                      if self.position else [self.cash])

        # An already-crossed protective stop has priority over calendar/signals.
        if self.position and minute.open <= self.position.stop:
            self._close(minute.open, minute, "gap_stop")
            open_marks.append(self.cash)
        if policy.force_flat:
            if self.position:
                self._close(minute.open, minute, "calendar_flat")
            return dict(cash=self.cash, close=self.cash,
                        adverse=min(open_marks + [self.cash]),
                        realized_delta=self.cash-cash_at_start)

        if snapshot is not None:
            if self.position and snapshot.previous_close < snapshot.exit_low:
                self._close(minute.open, minute, "channel")
                open_marks.append(self.cash)
            elif self.position:
                proposed = self.stop_tick(minute.open - 2.0 * snapshot.atr)
                self.position.stop = max(self.position.stop, proposed)
            if (self.position is None and policy.allow_entry and
                    snapshot.previous_close > snapshot.entry_high):
                stop = self.stop_tick(minute.open - 1.5 * snapshot.atr)
                if stop <= 0 or stop >= minute.open:
                    raise InputError("Invalid native initial stop")
                self.position = Position(minute.start, minute.open+self.slip,
                                         stop, minute.contract)

        if self.position:
            p = self.position
            open_marks.append(self.cash+(minute.open-p.entry)*self.value-self.fee)
            if minute.low <= p.stop:
                # The stop level is crossed after minute open; adverse slippage
                # is charged on that fill. Subminute stop time is not asserted.
                self._close(p.stop, minute, "stop")
                end_mark = self.cash
                adverse = min(open_marks + [self.cash])
            else:
                end_mark = self.cash+(minute.close-p.entry)*self.value-self.fee
                adverse = min(open_marks + [self.cash+(minute.low-p.entry)*self.value-self.fee])
        else:
            end_mark = self.cash
            adverse = min(open_marks + [self.cash])
        return dict(cash=self.cash, close=end_mark, adverse=adverse,
                    realized_delta=self.cash-cash_at_start)

    def reconcile(self):
        total = sum(t.net for t in self.trades)
        if abs(total-self.cash) > 1e-8:
            raise AssertionError("Trade/cash reconciliation failed")
        return dict(closed_trades=len(self.trades), closed_net=self.cash,
                    open_position=self.position is not None)
