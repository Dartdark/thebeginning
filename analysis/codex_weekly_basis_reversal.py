"""Research signal prototype, NOT an admitted return test or trading implementation.

Secondary-source hypothesis: reverse front-minus-deferred weekly return differences.
No data loading, universe/roll selection, sizing, order submission or P&L engine.
Real-data use requires a TEST evidence sheet and committed scout preregistration.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from fractions import Fraction


def aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('Timezone-aware information and decision clocks are required')


@dataclass(frozen=True)
class Contract:
    identifier: str
    commodity: str
    currency: str
    last_trade_at: datetime
    first_notice_at: datetime | None = None

    def risk_deadline(self) -> datetime:
        aware(self.last_trade_at)
        if self.first_notice_at is not None:
            aware(self.first_notice_at)
        return min(x for x in (self.last_trade_at, self.first_notice_at) if x is not None)


@dataclass(frozen=True)
class Settlement:
    contract_id: str
    event_at: datetime
    available_at: datetime
    price: Decimal

    def validate(self) -> None:
        aware(self.event_at)
        aware(self.available_at)
        if self.available_at < self.event_at:
            raise ValueError('Settlement cannot be available before its event')
        if not isinstance(self.price, Decimal) or not self.price.is_finite() or self.price <= 0:
            raise ValueError('Percentage-return prototype requires finite positive Decimal prices')


@dataclass(frozen=True)
class Direction:
    front_contract: str
    deferred_contract: str
    front_side: int
    deferred_side: int
    signal_available_at: datetime
    decision_at: datetime
    planned_exit_at: datetime
    # Side is direction only, never an equal-dollar or one-contract sizing claim.


def build_direction(
    front: Contract,
    deferred: Contract,
    front_start: Settlement,
    front_end: Settlement,
    deferred_start: Settlement,
    deferred_end: Settlement,
    *,
    decision_at: datetime,
    planned_exit_at: datetime,
    minimum_remaining_days: int,
) -> Direction:
    """Build a lagged signal from an explicitly selected same-contract weekly pair.

    The caller must supply source-verified weekly endpoints, holiday/roll calendar,
    publication clocks and an explicit expiry buffer. This function does not infer
    them from available price rows. Changes of month require separately measured
    endpoints for the newly selected contracts, never spliced continuous returns.
    """
    aware(decision_at)
    aware(planned_exit_at)
    if type(minimum_remaining_days) is not int or minimum_remaining_days < 0:
        raise ValueError('Explicit nonnegative integer expiry buffer required')
    if not front.identifier or not deferred.identifier or front.identifier == deferred.identifier:
        raise ValueError('Two different identified contracts are required')
    if not front.commodity or front.commodity != deferred.commodity:
        raise ValueError('Both contracts must reference the same commodity')
    if not front.currency or front.currency != deferred.currency:
        raise ValueError('Both legs must have the same price currency')
    front.risk_deadline()
    deferred.risk_deadline()
    if front.last_trade_at >= deferred.last_trade_at:
        raise ValueError('Front must mature before deferred')
    observations = (front_start, front_end, deferred_start, deferred_end)
    for observation in observations:
        observation.validate()
    if (front_start.contract_id != front.identifier or front_end.contract_id != front.identifier
            or deferred_start.contract_id != deferred.identifier
            or deferred_end.contract_id != deferred.identifier):
        raise ValueError('Contract identity changed within the measured interval')
    if (front_start.event_at != deferred_start.event_at
            or front_end.event_at != deferred_end.event_at):
        raise ValueError('Both legs must use matched measurement endpoints')
    if front_start.event_at >= front_end.event_at:
        raise ValueError('Measurement endpoints must increase')
    signal_available = max(x.available_at for x in observations)
    if decision_at <= signal_available:
        raise ValueError('Decision must follow all final settlement availability times')
    if planned_exit_at <= decision_at:
        raise ValueError('Planned exit must follow the decision')
    for contract in (front, deferred):
        deadline = contract.risk_deadline()
        if decision_at + timedelta(days=minimum_remaining_days) > deadline:
            raise ValueError('Contract fails the explicit entry expiry buffer')
        if planned_exit_at >= deadline:
            raise ValueError('Planned holding reaches first notice or last trade')
    # Compare relative gross growth using exact decimal cross-products. This avoids
    # false signs from binary rounding when economically identical returns cancel.
    difference = (Fraction(front_end.price) * Fraction(deferred_start.price)
                  - Fraction(deferred_end.price) * Fraction(front_start.price))
    front_side = -1 if difference > 0 else 1 if difference < 0 else 0
    return Direction(front.identifier, deferred.identifier, front_side, -front_side,
                     signal_available, decision_at, planned_exit_at)
