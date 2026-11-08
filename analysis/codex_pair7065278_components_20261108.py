"""Research components only: no historical returns, orders, cash ledger or data download."""
from dataclasses import dataclass
from datetime import datetime
import math

import pandas as pd


@dataclass(frozen=True)
class Quote:
    bid: float
    ask: float
    event_time: datetime
    available_at: datetime
    unit: str


def validate_quote(q: Quote, decision: datetime) -> float:
    for t in (q.event_time, q.available_at, decision):
        if t.tzinfo is None or t.utcoffset() is None:
            raise ValueError('timezone-aware timestamps required')
    if not all(math.isfinite(v) and v > 0 for v in (q.bid, q.ask)):
        raise ValueError('prices must be positive and finite')
    if q.ask < q.bid:
        raise ValueError('crossed quote')
    if not q.event_time <= q.available_at <= decision:
        raise ValueError('invalid event/receipt/decision ordering')
    if (decision - q.event_time).total_seconds() > 60:
        raise ValueError('stale quote')
    return (q.bid + q.ask) / 2


def ratio(us: Quote, uk: Quote, fx: Quote, decision: datetime,
          *, both_continuous_open: bool) -> float:
    # Calendar evidence must be supplied externally, not inferred from a weekday.
    if not both_continuous_open:
        raise ValueError('both continuous sessions must be established open')
    if decision.tzinfo is None or decision.utcoffset() is None:
        raise ValueError('timezone-aware decision required')
    if (decision.hour, decision.minute, decision.second, decision.microsecond) != (15, 0, 0, 0) or decision.utcoffset().total_seconds() != 0:
        raise ValueError('decision must be exactly 15:00 UTC')
    if us.unit != 'USD' or uk.unit not in ('GBX', 'GBP') or fx.unit != 'USD_PER_GBP':
        raise ValueError('unrecognized native currency units')
    u = validate_quote(us, decision)
    k = validate_quote(uk, decision) / (100 if uk.unit == 'GBX' else 1)
    x = validate_quote(fx, decision)
    return u / (k * x)


def scores(values: list[float]) -> pd.Series:
    s = pd.Series(values, dtype=float)
    if not s.map(lambda v: math.isfinite(v) and v > 0).all():
        raise ValueError('ratios must be positive and finite; no imputation')
    mean = s.ewm(span=20, adjust=False, min_periods=20).mean()
    sd = s.rolling(20, min_periods=20).std(ddof=1)
    return (s - mean) / sd.where(sd > 0)


def desired_side(prior: int, z: float) -> int:
    if prior not in (-1, 0, 1):
        raise ValueError('invalid prior position')
    if not math.isfinite(z):
        raise ValueError('warm-up, missing or zero-dispersion score: no decision')
    if prior == 1:
        return 0 if z >= -0.25 else 1
    if prior == -1:
        return 0 if z <= 0.25 else -1
    return 1 if z < -0.75 else -1 if z > 0.75 else 0
