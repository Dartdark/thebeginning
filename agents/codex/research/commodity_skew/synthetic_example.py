"""Generate invented inputs for exercising the planner; contains no market data."""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "analysis"))
from codex_commodity_skew import UNIVERSE


def make_packet():
    sessions = []
    day = date(2025, 1, 1)
    while day < date(2026, 1, 1):
        if day.weekday() < 5:
            sessions.append(day.isoformat())
        day += timedelta(days=1)
    noise = np.random.default_rng(731).normal(0, 0.001, len(sessions))
    pulse = np.zeros(len(sessions))
    pulse[::19] = 1
    rows, entries = [], {}
    for index, commodity in enumerate(UNIVERSE):
        prices = Decimal(100 + index)
        previous, previous_event = "2024-12-31", "2024-12-31T14:00:00-06:00"
        previous_available = "2024-12-31T14:01:00-06:00"
        contract = f"SYNTHETIC-{commodity}-MAR2026"
        for label, change in zip(sessions, noise + (index - 10.5) * 0.0015 * pulse):
            prior = prices
            prices = (prices * (1 + Decimal(str(change)))).quantize(Decimal("0.000000000001"))
            # Use explicit civil offsets across US DST, without guessing UTC session labels.
            event = datetime.fromisoformat(label + "T14:00:00").replace(tzinfo=ZoneInfo("America/Chicago"))
            received = event + timedelta(minutes=1)
            rows.append(dict(commodity=commodity, session=label, previous_session=previous,
                             contract_id=contract, previous_contract_id=contract,
                             last_trade_date="2026-03-15", close=str(prices), previous_close=str(prior),
                             event_at=event.isoformat(), available_at=received.isoformat(),
                             previous_event_at=previous_event, previous_available_at=previous_available))
            previous, previous_event, previous_available = label, event.isoformat(), received.isoformat()
        entries[commodity] = dict(
            contract_id=contract, currency="USD", reference_price=str(prices), multiplier="100",
            fx_to_usd="1", tick_size="0.01", commission_usd_per_contract_side="2",
            slippage_ticks_per_side=1, reference_event_at=previous_event,
            reference_available_at=previous_available, fx_event_at=previous_event,
            fx_available_at=previous_available, spec_available_at="2024-12-01T00:00:00-06:00",
            earliest_fill_at="2026-01-02T08:00:00-06:00", next_roll_or_exit_at="2026-01-30T13:00:00-06:00",
            delivery_deadline_at="2026-02-20T12:00:00-06:00", last_trade_at="2026-03-15T12:00:00-05:00",
            roll_provenance="SYNTHETIC dates; not a real contract calendar")
    return dict(
        ranking_month="2025-12", decision_at="2026-01-01T00:05:00-06:00",
        calendar_timezone="America/Chicago", reference_nav_usd="1000000",
        universe_provenance="SYNTHETIC complete named source universe",
        calendar_provenance="SYNTHETIC weekdays including real holidays; not an exchange calendar",
        price_provenance="SYNTHETIC seeded prices; not real settlements or returns",
        universe_available_at="2024-12-01T00:00:00-06:00",
        calendar_available_at="2024-12-01T00:00:00-06:00",
        price_available_at="2025-12-31T14:01:00-06:00",
        universe={commodity: sessions[:] for commodity in UNIVERSE},
        warmup_sessions={commodity: "2024-12-31" for commodity in UNIVERSE},
        observations=rows, entry_contracts=entries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(make_packet(), indent=2) + "\n")
    print(f"Invented research packet written to {args.output}")
