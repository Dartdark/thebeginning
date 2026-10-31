"""Offline SSRN3441913 strategy/order proposals. No broker, scheduler or return backtest.

CLI: python3 analysis/codex_bitcoin_inverse_3441913_strategy.py INPUT.json --output OUTPUT.json
All quote-priced fills below are hypothetical review calculations, not executed orders.
"""
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN
import argparse
import hashlib
import json
import math
from pathlib import Path


class ReviewError(ValueError):
    """Input or proposed book cannot be admitted under the declared research protocol."""


def finite(value, name, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ReviewError(f'{name}: finite numeric value required')
    if positive and value <= 0 or nonnegative and value < 0:
        raise ReviewError(f'{name}: invalid sign')
    return value


def utc(value):
    try:
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ReviewError('Explicit ISO-8601 UTC timestamp required') from exc
    if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
        raise ReviewError('Timestamps must carry UTC Z or +00:00')
    return stamp.astimezone(timezone.utc)


def rounded(value, lot):
    """Signed quantity rounded toward zero; Decimal avoids 0.3/0.1 truncating to two lots."""
    finite(value, 'quantity')
    finite(lot, 'lot', positive=True)
    return float((Decimal(str(value)) / Decimal(str(lot))).to_integral_value(rounding=ROUND_DOWN) * Decimal(str(lot)))


@dataclass(frozen=True)
class Model:
    mu_spot: float
    mu_futures: float
    sigma_spot: float
    sigma_futures: float
    correlation: float
    calibration_end: str
    available_at: str

    def coefficients(self, max_condition):
        for name in ('mu_spot', 'mu_futures', 'correlation'):
            finite(getattr(self, name), name)
        for name in ('sigma_spot', 'sigma_futures'):
            finite(getattr(self, name), name, positive=True)
        if abs(self.correlation) >= 1:
            raise ReviewError('Singular/invalid covariance correlation')
        a, d = self.sigma_spot ** 2, self.sigma_futures ** 2
        b = self.correlation * self.sigma_spot * self.sigma_futures
        determinant = a * d - b * b
        largest = (a + d + math.hypot(a - d, 2 * b)) / 2
        if determinant <= 0 or not math.isfinite(determinant):
            raise ReviewError('Invalid covariance determinant')
        condition = largest * largest / determinant
        if condition > max_condition:
            raise ReviewError('Covariance exceeds configured condition-number bound')
        # Main Eq4.4, consistent with Eq4.3 / Appendix C, not the misprinted B.2.
        c1 = (self.mu_spot * d - (self.mu_futures - d) * b) / determinant
        c2 = ((self.mu_futures - d) * a - self.mu_spot * b) / determinant
        finite(c1, 'C1'); finite(c2, 'C2')
        return c1, c2, condition


@dataclass(frozen=True)
class Instrument:
    venue: str
    contract_id: str
    kind: str
    settlement_currency: str
    face_usd: float
    expiry: str


@dataclass(frozen=True)
class Quotes:
    contract_id: str
    observed_at: str
    available_at: str
    spot_bid: float
    spot_ask: float
    spot_mark: float
    futures_bid: float
    futures_ask: float
    futures_mark: float


@dataclass(frozen=True)
class Book:
    contract_id: str
    as_of: str
    available_at: str
    usd_cash: float
    spot_btc: float
    collateral_btc: float
    contracts: int
    entry_price: float  # reciprocal-price cost basis; exactly zero when flat

    def unrealized_btc(self, instrument, mark):
        if not self.contracts:
            return 0.0
        return self.contracts * instrument.face_usd * (1 / self.entry_price - 1 / mark)

    def nav(self, instrument, quotes):
        return self.usd_cash + (self.spot_btc + self.collateral_btc +
                               self.unrealized_btc(instrument, quotes.futures_mark)) * quotes.spot_mark


@dataclass(frozen=True)
class Settings:
    wallet_model: str
    utility: str
    risk_parameter: float  # alpha for power, gamma (inverse USD) for exponential
    spot_lot_btc: float
    spot_fee_rate: float
    futures_fee_rate: float
    initial_margin_rate: float
    maintenance_margin_rate: float
    max_gross_model_exposure: float
    max_covariance_condition: float
    max_quote_age_seconds: float
    max_book_age_seconds: float
    latency_seconds: float


def inverse_fill(contracts, entry_price, delta, price, face_usd):
    """Return new signed quantity, reciprocal-weighted basis and realized BTC (before fees)."""
    for name, value in [('contracts', contracts), ('delta', delta)]:
        if type(value) is not int:
            raise ReviewError(f'{name}: integer contract count required')
    finite(price, 'fill price', positive=True); finite(face_usd, 'face', positive=True)
    finite(entry_price, 'entry basis', nonnegative=True)
    if (contracts == 0) != (entry_price == 0):
        raise ReviewError('Flat book requires zero basis; held book requires positive basis')
    if delta == 0:
        return contracts, entry_price, 0.0
    new = contracts + delta
    if contracts == 0:
        return new, price, 0.0
    if contracts * delta > 0:
        basis = abs(new) / (abs(contracts) / entry_price + abs(delta) / price)
        return new, basis, 0.0
    closed = min(abs(contracts), abs(delta))
    realized = math.copysign(closed, contracts) * face_usd * (1 / entry_price - 1 / price)
    basis = 0.0 if new == 0 else entry_price if new * contracts > 0 else price
    return new, basis, realized


def validate(model, instrument, quotes, book, settings, decision_time):
    now = utc(decision_time)
    if settings.wallet_model != 'pooled_btc_research':
        raise ReviewError('Only explicit pooled_btc_research wallet accounting is implemented')
    if quotes.contract_id != instrument.contract_id or book.contract_id != instrument.contract_id:
        raise ReviewError('Book/quote/instrument contract identity mismatch')
    finite(settings.risk_parameter, 'risk_parameter')
    if settings.utility not in ('power', 'exponential'):
        raise ReviewError('utility must be power or exponential')
    if settings.utility == 'power' and (settings.risk_parameter >= 1 or settings.risk_parameter == 0):
        raise ReviewError('Source power utility requires alpha<1 and alpha!=0')
    if settings.utility == 'exponential' and settings.risk_parameter <= 0:
        raise ReviewError('Exponential gamma must be positive in inverse USD units')
    for name in ('spot_lot_btc', 'max_gross_model_exposure', 'max_covariance_condition',
                 'max_quote_age_seconds', 'max_book_age_seconds', 'latency_seconds'):
        finite(getattr(settings, name), name, positive=True)
    for name in ('spot_fee_rate', 'futures_fee_rate', 'initial_margin_rate', 'maintenance_margin_rate'):
        rate = finite(getattr(settings, name), name, nonnegative=True)
        if rate >= 1:
            raise ReviewError(f'{name}: rate must be below one')
    if not 0 < settings.maintenance_margin_rate < settings.initial_margin_rate:
        raise ReviewError('Require 0<maintenance margin<initial margin')
    if not utc(model.calibration_end) <= utc(model.available_at) <= now:
        raise ReviewError('Calibration must be completed and available before decision')
    for observed, available, limit, label in [
        (quotes.observed_at, quotes.available_at, settings.max_quote_age_seconds, 'quotes'),
        (book.as_of, book.available_at, settings.max_book_age_seconds, 'book')]:
        if not utc(observed) <= utc(available) <= now or (now - utc(observed)).total_seconds() > limit:
            raise ReviewError(f'{label}: stale or unavailable at decision')
    if not instrument.venue.strip() or not instrument.contract_id.strip():
        raise ReviewError('Explicit venue and contract identity required')
    if instrument.kind != 'dated_inverse' or instrument.settlement_currency != 'BTC':
        raise ReviewError('Only dated BTC-settled inverse futures supported; no linear/perpetual splice')
    finite(instrument.face_usd, 'face_usd', positive=True)
    eligible = now + timedelta(seconds=settings.latency_seconds)
    if eligible >= utc(instrument.expiry):
        raise ReviewError('Contract expires before first eligible fill; roll protocol absent')
    for name in ('spot_bid', 'spot_ask', 'spot_mark', 'futures_bid', 'futures_ask', 'futures_mark'):
        finite(getattr(quotes, name), name, positive=True)
    if quotes.spot_bid > quotes.spot_ask or quotes.futures_bid > quotes.futures_ask:
        raise ReviewError('Crossed bid/ask')
    for name in ('usd_cash', 'spot_btc', 'collateral_btc'):
        finite(getattr(book, name), name, nonnegative=True)
    inverse_fill(book.contracts, book.entry_price, 0, quotes.futures_mark, instrument.face_usd)
    nav = book.nav(instrument, quotes)
    if not math.isfinite(nav) or nav <= 0:
        raise ReviewError('Nonpositive/nonfinite marked account NAV')
    margin = abs(book.contracts) * instrument.face_usd / quotes.futures_mark * settings.maintenance_margin_rate
    if book.contracts and book.collateral_btc + book.unrealized_btc(instrument, quotes.futures_mark) <= margin:
        raise ReviewError('Existing book at/below modeled maintenance: actual liquidation path unresolved')
    return now, eligible, nav


def plan_rebalance(model, instrument, quotes, book, settings, decision_time):
    """Plan fixed targets at decision; hypothetical quote execution for funding/cost review only.

    BTC collateral and unrealized inverse P&L count toward the model's non-futures BTC exposure.
    No automatic clipping, borrowing, spot shorts, rolls or fabricated liquidation fills.
    """
    now, eligible, starting_nav = validate(model, instrument, quotes, book, settings, decision_time)
    c1, c2, condition = model.coefficients(settings.max_covariance_condition)
    scale = starting_nav / (1 - settings.risk_parameter) if settings.utility == 'power' else 1 / settings.risk_parameter
    theta = finite(c1 * scale, 'spot dollar target')
    target_f = finite(c2 * scale / (instrument.face_usd * quotes.spot_mark / quotes.futures_mark), 'futures target')
    if theta < 0:
        raise ReviewError('Source target requires short spot; borrow/short protocol unsupported')
    if (abs(theta) + abs(c2 * scale)) / starting_nav > settings.max_gross_model_exposure:
        raise ReviewError('Raw target exceeds gross modeled-exposure cap; target not silently clipped')
    target_contracts = math.trunc(target_f)
    delta = target_contracts - book.contracts
    future_price = quotes.futures_ask if delta > 0 else quotes.futures_bid if delta < 0 else quotes.futures_mark
    new_n, new_entry, realized = inverse_fill(book.contracts, book.entry_price, delta, future_price, instrument.face_usd)
    future_fee = abs(delta) * instrument.face_usd / future_price * settings.futures_fee_rate
    future_unrealized = new_n * instrument.face_usd * (1 / new_entry - 1 / quotes.futures_mark) if new_n else 0.
    # Conservative BTC wallet reserve: initial margin + closing-fee reserve, no credit for positive unrealized P&L.
    reserve = abs(new_n) * instrument.face_usd / quotes.futures_mark * (settings.initial_margin_rate + settings.futures_fee_rate)
    required = reserve + max(0., -future_unrealized)
    desired_physical_btc = theta / quotes.spot_mark - future_unrealized
    if desired_physical_btc + 1e-12 < required:
        raise ReviewError('Spot target cannot fund required BTC collateral without extra model exposure')
    work = book
    actions = []
    spot_fee_usd = 0.
    execution_difference_usd = 0.

    def spot_order(quantity, purpose):
        nonlocal work, spot_fee_usd, execution_difference_usd
        if quantity == 0:
            return
        price = quotes.spot_ask if quantity > 0 else quotes.spot_bid
        fee = abs(quantity) * price * settings.spot_fee_rate
        cash = work.usd_cash - quantity * price - fee
        spot = work.spot_btc + quantity
        if cash < -1e-8 or spot < -1e-10:
            raise ReviewError('Proposed spot fill requires USD borrowing or short BTC')
        work = replace(work, usd_cash=max(0., cash), spot_btc=max(0., spot))
        spot_fee_usd += fee
        execution_difference_usd += quantity * (price - quotes.spot_mark)
        actions.append(dict(kind='spot', quantity_btc=quantity, reference_price=price, fee_usd=fee, purpose=purpose))

    def transfer(amount):
        nonlocal work
        # Positive transfers spot BTC into collateral, negative returns collateral to spot.
        if abs(amount) < 1e-14:
            return
        if work.spot_btc - amount < -1e-10 or work.collateral_btc + amount < -1e-10:
            raise ReviewError('Unfunded BTC wallet transfer')
        work = replace(work, spot_btc=max(0., work.spot_btc - amount), collateral_btc=max(0., work.collateral_btc + amount))
        actions.append(dict(kind='btc_wallet_transfer', spot_to_collateral_btc=amount))

    # Prefund fees, realized losses and postfill reserve before proposing the futures fill.
    prefund = required + future_fee + max(0., -realized)
    shortage = max(0., prefund - work.collateral_btc - work.spot_btc)
    if shortage:
        lots = (Decimal(str(shortage)) / Decimal(str(settings.spot_lot_btc))).to_integral_value(rounding='ROUND_CEILING')
        spot_order(float(lots * Decimal(str(settings.spot_lot_btc))), 'prefund_futures_collateral')
    transfer(max(0., prefund - work.collateral_btc))
    if delta:
        work = replace(work, contracts=new_n, entry_price=new_entry, collateral_btc=work.collateral_btc + realized - future_fee)
        execution_difference_usd += -delta * instrument.face_usd * (1 / future_price - 1 / quotes.futures_mark) * quotes.spot_mark
        actions.append(dict(kind='inverse_futures', quantity_contracts=delta, reference_price=future_price,
                            fee_btc=future_fee, realized_btc=realized, purpose='rebalance'))
    transfer(required - work.collateral_btc)
    adjustment = rounded(desired_physical_btc - work.spot_btc - work.collateral_btc, settings.spot_lot_btc)
    spot_order(adjustment, 'rebalance_total_btc_exposure')
    ending_nav = work.nav(instrument, quotes)
    fees_usd = spot_fee_usd + future_fee * quotes.spot_mark
    if not math.isclose(starting_nav - ending_nav, fees_usd + execution_difference_usd, rel_tol=1e-8, abs_tol=1e-7):
        raise ReviewError('BTC/USD NAV-to-cost reconciliation failed')
    gross = ((work.spot_btc + work.collateral_btc + work.unrealized_btc(instrument, quotes.futures_mark)) * quotes.spot_mark +
             abs(work.contracts) * instrument.face_usd * quotes.spot_mark / quotes.futures_mark)
    if ending_nav <= 0 or gross / ending_nav > settings.max_gross_model_exposure:
        raise ReviewError('Rounded, costed proposal exceeds exposure/NAV constraints')
    for sequence, action in enumerate(actions, 1):
        action.update(sequence=sequence, decision_time=now.isoformat(), earliest_eligible_fill=eligible.isoformat(), status='HYPOTHETICAL_QUOTE_PROPOSAL')
    return dict(status='OFFLINE_REVIEW_ONLY', contract_id=instrument.contract_id,
                coefficients=dict(C1=c1, C2=c2, covariance_condition=condition),
                raw_targets=dict(spot_total_usd=theta, futures_contracts=target_f),
                rounded_contract_target=target_contracts,
                starting_nav_usd=starting_nav, hypothetical_ending_nav_usd=ending_nav,
                expected_fees_usd=fees_usd, expected_execution_mark_difference_usd=execution_difference_usd,
                expected_gross_model_exposure=gross / ending_nav,
                required_collateral_btc=required, hypothetical_book=asdict(work), actions=actions,
                input_book_unchanged=True, empirical_return_trials=0,
                limitations=['Quotes do not establish fills, liquidity, depth or atomic leg execution.',
                             'Margin reserve is a configured research check, not an exchange liquidation engine.',
                             'Fills and wallet transfers require chronological reconciliation before replanning.',
                             'No carry interest, spot borrowing, perpetual funding or expiry/roll implementation.'])


def from_packet(packet):
    if packet['input_status'] not in ('synthetic', 'unverified_research'):
        raise ReviewError('Only synthetic or unverified_research input status is supported')
    args = [Model(**packet['model']), Instrument(**packet['instrument']), Quotes(**packet['quotes']),
            Book(**packet['book']), Settings(**packet['settings']), packet['decision_time']]
    result = plan_rebalance(*args)
    result['input_status'] = packet['input_status']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    result = from_packet(json.loads(raw))
    result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    result['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(f"Saved offline proposal to {args.output}; no orders sent or historical returns evaluated.")


if __name__ == '__main__':
    main()
