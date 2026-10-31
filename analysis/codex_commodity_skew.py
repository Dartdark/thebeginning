"""Offline monthly commodity-skewness planner for SSRN 3507947.

Produces research target positions, never orders or historical performance.
Schema and explicit adaptations: agents/codex/research/commodity_skew/README.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import tempfile
from datetime import date
from decimal import Decimal, ROUND_FLOOR, localcontext
from importlib.metadata import version
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from scipy.stats import skew

from codex_rad_double_sort import clock, positive


UNIVERSE = (
    "soybean_oil", "corn", "cocoa", "cotton", "feeder_cattle", "gold", "copper",
    "heating_oil", "coffee", "live_cattle", "lean_hogs", "natural_gas", "oats",
    "orange_juice", "palladium", "platinum", "soybeans", "sugar", "silver",
    "soybean_meal", "wheat", "crude_oil",
)
MIN_OBSERVATIONS = 200
TIE_TOLERANCE = 1e-12


def nonnegative(value: str) -> Decimal:
    if not isinstance(value, str):
        raise ValueError("Monetary values must be decimal strings")
    number = Decimal(value)
    if not number.is_finite() or number < 0:
        raise ValueError("Finite nonnegative cost required")
    return number


def month_offset(month: date, offset: int) -> date:
    index = month.year * 12 + month.month - 1 + offset
    year, number = divmod(index, 12)
    return date(year, number + 1, 1)


def adjusted_skew(returns) -> float:
    """Adjusted Fisher-Pearson sample skew, scipy bias=False; no fitted parameter."""
    values = np.asarray(returns, dtype=float)
    if values.ndim != 1 or len(values) < 3 or not np.isfinite(values).all():
        raise ValueError("Skewness needs at least three finite daily returns")
    # Positive rescaling preserves skew and avoids third-moment overflow.
    scale = float(np.max(np.abs(values)))
    if scale == 0 or np.ptp(values / scale) == 0:
        raise ValueError("Zero-variance return history has undefined skewness")
    result = float(skew(values / scale, bias=False))
    if not math.isfinite(result):
        raise ValueError("Undefined skewness; no asset may be silently removed")
    return result


def rank_scores(scores: list[dict]) -> tuple[list[dict], list[dict]]:
    if len(scores) != 22 or {s["commodity"] for s in scores} != set(UNIVERSE):
        raise ValueError("Ranking requires the exact 22-commodity universe")
    if not all(math.isfinite(s["skewness"]) for s in scores):
        raise ValueError("Nonfinite score")
    ranked = sorted(scores, key=lambda s: (s["skewness"], s["commodity"]))
    for a, b in ((3, 4), (17, 18)):
        if math.isclose(ranked[a]["skewness"], ranked[b]["skewness"],
                        rel_tol=TIE_TOLERANCE, abs_tol=TIE_TOLERANCE):
            raise ValueError("Ambiguous skewness cutoff tie; formation unresolved")
    return ranked[:4], list(reversed(ranked[-4:]))


def build_plan(packet: dict) -> dict:
    tz = ZoneInfo(packet["calendar_timezone"])
    ranking = date.fromisoformat(packet["ranking_month"] + "-01")
    start, end = month_offset(ranking, -11), month_offset(ranking, 1)
    holding_end = month_offset(end, 1)
    decision = clock(packet["decision_at"])
    if not end <= decision.astimezone(tz).date() < holding_end:
        raise ValueError("Decision must be in the month following the ranking month")
    for kind in ("universe", "calendar", "price"):
        if not packet[kind + "_provenance"]:
            raise ValueError("Universe, calendar and price provenance required")
        if clock(packet[kind + "_available_at"]) >= decision:
            raise ValueError("Input provenance/universe/calendar unavailable before decision")
    universe = packet["universe"]
    if not isinstance(universe, dict) or set(universe) != set(UNIVERSE):
        raise ValueError("Supply every one of the source's 22 commodities, without substitutions")
    if set(packet["warmup_sessions"]) != set(UNIVERSE):
        raise ValueError("Each commodity needs its declared prior warm-up session")
    calendars, expected = {}, set()
    for commodity, labels in universe.items():
        sessions = [date.fromisoformat(label) for label in labels]
        if len(sessions) < MIN_OBSERVATIONS or sessions != sorted(set(sessions)):
            raise ValueError("Need at least 200 unique ordered expected sessions per commodity")
        if any(not start <= session < end for session in sessions):
            raise ValueError("Expected session outside the prior 12 calendar months")
        for offset in range(12):
            month = month_offset(start, offset)
            if sum(month <= s < month_offset(month, 1) for s in sessions) < 15:
                raise ValueError("Each of the 12 calendar months needs at least 15 expected sessions")
        warmup = date.fromisoformat(packet["warmup_sessions"][commodity])
        if warmup >= start:
            raise ValueError("Warm-up close must precede the 12-month window")
        calendars[commodity] = sessions
        expected.update((commodity, s) for s in sessions)
    observed = {}
    for row in packet["observations"]:
        key = (row["commodity"], date.fromisoformat(row["session"]))
        if key not in expected or key in observed:
            raise ValueError("Unexpected or duplicate daily observation")
        observed[key] = row
    if set(observed) != expected:
        raise ValueError("Incomplete panel, including nonselected commodities; no silent reweighting")

    scores = []
    expiries, owners = {}, {}
    for commodity in UNIVERSE:
        sessions, returns, prior_row = calendars[commodity], [], None
        for i, session in enumerate(sessions):
            row = observed[commodity, session]
            previous = date.fromisoformat(row["previous_session"])
            required = sessions[i - 1] if i else date.fromisoformat(packet["warmup_sessions"][commodity])
            if previous != required or previous >= session:
                raise ValueError("Prior close must use the preceding expected session")
            contract = row["contract_id"]
            if not contract or row["previous_contract_id"] != contract:
                raise ValueError("Each return requires two prices of the SAME dated contract, including rolls")
            if owners.setdefault(contract, commodity) != commodity:
                raise ValueError("One dated contract cannot represent different commodities")
            expiry = date.fromisoformat(row["last_trade_date"])
            contract_key = (commodity, contract)
            if session > expiry or expiries.setdefault(contract_key, expiry) != expiry:
                raise ValueError("Expired or inconsistently identified history contract")
            event, available = clock(row["event_at"]), clock(row["available_at"])
            prev_event = clock(row["previous_event_at"])
            prev_available = clock(row["previous_available_at"])
            if event.astimezone(tz).date() != session or prev_event.astimezone(tz).date() != previous:
                raise ValueError("Settlement event dates must match the declared local session labels")
            if not prev_event <= prev_available < event <= available < decision:
                raise ValueError("Invalid event/receipt/decision ordering")
            if prior_row and prev_event != clock(prior_row["event_at"]):
                raise ValueError("Previous measurement clock does not match prior expected session")
            close, prev_close = positive(row["close"]), positive(row["previous_close"])
            if prior_row and prior_row["contract_id"] == contract and prev_close != positive(prior_row["close"]):
                raise ValueError("Inconsistent previous price on an unchanged contract")
            if prior_row and prior_row["contract_id"] == contract and prev_available != clock(prior_row["available_at"]):
                raise ValueError("Prior receipt clock must match the same stored contract observation")
            with localcontext() as ctx:
                ctx.prec = 40
                value = float(close / prev_close - 1)
            if not math.isfinite(value):
                raise ValueError("Daily return overflows; unsupported price series")
            returns.append(value)
            prior_row = row
        scores.append(dict(commodity=commodity, skewness=adjusted_skew(returns),
                           observations=len(returns), first_session=str(sessions[0]),
                           last_session=str(sessions[-1])))
    longs, shorts = rank_scores(scores)
    nav = positive(packet["reference_nav_usd"])
    positions = []
    contract_ids = set()
    with localcontext() as ctx:
        ctx.prec = 40
        for side, chosen in ((1, longs), (-1, shorts)):
            for score in chosen:
                commodity = score["commodity"]
                spec = packet["entry_contracts"][commodity]
                contract = spec["contract_id"]
                if not contract or contract in contract_ids or not spec["currency"] or not spec["roll_provenance"]:
                    raise ValueError("Unique identified entry contracts, currency and roll provenance required")
                if contract in owners and owners[contract] != commodity:
                    raise ValueError("Selected entry contract belongs to a different commodity")
                contract_ids.add(contract)
                quote, received = clock(spec["reference_event_at"]), clock(spec["reference_available_at"])
                fx_event, fx_received = clock(spec["fx_event_at"]), clock(spec["fx_available_at"])
                last_row = observed[commodity, calendars[commodity][-1]]
                if quote != clock(last_row["event_at"]) or not quote <= received < decision:
                    raise ValueError("Reference quote must be a known final-ranking-session measurement")
                if fx_event.astimezone(tz).date() != quote.astimezone(tz).date():
                    raise ValueError("FX must be measured on the final-ranking session")
                if not fx_event <= fx_received < decision or clock(spec["spec_available_at"]) >= decision:
                    raise ValueError("FX and contract specifications must be known before decision")
                fill = clock(spec["earliest_fill_at"])
                action = clock(spec["next_roll_or_exit_at"])
                deadline, last_trade = clock(spec["delivery_deadline_at"]), clock(spec["last_trade_at"])
                if not decision < fill < action < deadline <= last_trade:
                    raise ValueError("Future fill and action must precede the effective delivery/broker deadline")
                if not end <= fill.astimezone(tz).date() <= action.astimezone(tz).date() < holding_end:
                    raise ValueError("Entry and next mandatory roll/exit must be within the holding month")
                price, multiplier, fx, tick = (positive(spec[k]) for k in
                                              ("reference_price", "multiplier", "fx_to_usd", "tick_size"))
                if contract == last_row["contract_id"]:
                    if price != positive(last_row["close"]) or last_trade.astimezone(tz).date() != date.fromisoformat(last_row["last_trade_date"]):
                        raise ValueError("Entry quote/spec contradict the same contract's historical observation")
                if spec["currency"] == "USD" and fx != 1:
                    raise ValueError("USD contracts require FX_to_USD = 1")
                ticks = spec["slippage_ticks_per_side"]
                if type(ticks) is not int or ticks < 0:
                    raise ValueError("Slippage ticks must be an explicit nonnegative integer")
                fee = nonnegative(spec["commission_usd_per_contract_side"])
                notional = price * multiplier * fx
                quantity = int((nav / 8 / notional).to_integral_value(rounding=ROUND_FLOOR))
                if quantity < 1:
                    raise ValueError("A selected leg cannot afford one contract; no leg may be dropped")
                entry_fee = quantity * fee
                entry_slippage = quantity * ticks * tick * multiplier * fx
                positions.append(dict(
                    commodity=commodity, skewness=score["skewness"], side="long" if side > 0 else "short",
                    contract_id=contract, signed_quantity=side * quantity,
                    currency=spec["currency"], reference_price=spec["reference_price"],
                    multiplier=spec["multiplier"], fx_to_usd=spec["fx_to_usd"], tick_size=spec["tick_size"],
                    commission_usd_per_contract_side=spec["commission_usd_per_contract_side"],
                    slippage_ticks_per_side=ticks, reference_event_at=spec["reference_event_at"],
                    reference_available_at=spec["reference_available_at"],
                    reference_notional_usd=str(quantity * notional),
                    ideal_signed_weight=str(Decimal(side) / 8),
                    reference_signed_weight=str(side * quantity * notional / nav),
                    rounding_notional_shortfall_usd=str(nav / 8 - quantity * notional),
                    entry_commission_estimate_usd=str(entry_fee),
                    entry_slippage_estimate_usd=str(entry_slippage),
                    unchanged_contract_roundtrip_cost_estimate_usd=str(2 * (entry_fee + entry_slippage)),
                    earliest_fill_at=spec["earliest_fill_at"], next_roll_or_exit_at=spec["next_roll_or_exit_at"],
                    delivery_deadline_at=spec["delivery_deadline_at"], last_trade_at=spec["last_trade_at"]))
        gross = sum(Decimal(p["reference_notional_usd"]) for p in positions)
        net = sum(Decimal(p["reference_notional_usd"]) * (1 if p["side"] == "long" else -1) for p in positions)
        commission = sum(Decimal(p["entry_commission_estimate_usd"]) for p in positions)
        slippage = sum(Decimal(p["entry_slippage_estimate_usd"]) for p in positions)
        return dict(
            status="OFFLINE_RESEARCH_TARGETS_ONLY", source="SSRN 3507947",
            ranking_month=packet["ranking_month"], holding_month=end.strftime("%Y-%m"),
            calendar_timezone=packet["calendar_timezone"], decision_at=packet["decision_at"],
            window_start=str(start), window_end_exclusive=str(end), estimator="adjusted_Fisher_Pearson_bias_false",
            reference_nav_usd=str(nav), ideal_gross_weight="1", gross_reference_weight=str(gross / nav),
            net_reference_weight=str(net / nav), entry_from_flat_commission_estimate_usd=str(commission),
            entry_from_flat_slippage_estimate_usd=str(slippage),
            unchanged_contract_roundtrip_cost_estimate_usd=str(2 * (commission + slippage)),
            scores=sorted(scores, key=lambda s: (s["skewness"], s["commodity"])), positions=positions,
            limits=["Targets are not rebalance orders or executable fills",
                    "Native integer sizing and same-contract returns are declared adaptations",
                    "Estimates exclude roll/rebalance turnover, management fees, financing, margin and cash interest",
                    "No position ledger, P&L, performance, stops, account admission or live trading",
                    "Calendar, contract identity and provenance declarations still require independent verification",
                    "Nonpositive-price histories are unsupported and cannot be silently excluded"])


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        raw = args.packet.read_bytes()
        packet = json.loads(raw, object_pairs_hook=unique_object,
                            parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Invalid JSON constant {x}")))
        result = build_plan(packet)
        result.update(input_sha256=hashlib.sha256(raw).hexdigest(),
                      code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      helper_code_sha256=hashlib.sha256(Path(__file__).with_name("codex_rad_double_sort.py").read_bytes()).hexdigest(),
                      versions={"python": platform.python_version(), "numpy": version("numpy"), "scipy": version("scipy")})
        serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    except (ValueError, KeyError, TypeError, ArithmeticError, OSError) as exc:
        parser.error(f"Invalid research packet: {exc}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=args.output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(serialized)
        os.replace(temporary, args.output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
