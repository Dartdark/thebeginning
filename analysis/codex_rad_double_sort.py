"""Offline monthly commodity momentum/carry research planner (SSRN2614241).

No orders, fills, performance calculation, data download or historical return runner.
Real-data outcome work still requires TEST evidence and committed budget/preregistration.
See agents/codex/research/rad_double_sort/README.md for schema and source differences.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
from datetime import date, datetime
from decimal import Decimal, localcontext, ROUND_FLOOR
from pathlib import Path


def clock(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError('All clocks must include a UTC offset')
    return dt


def positive(value: str) -> Decimal:
    if not isinstance(value, str):
        raise ValueError('Prices, NAV, multipliers and FX must be decimal strings')
    result = Decimal(value)
    if not result.is_finite() or result <= 0:
        raise ValueError('Finite positive values required; no undefined logs or silent exclusions')
    return result


def build_plan(packet: dict) -> dict:
    """Validate a frozen calendar/universe and produce scores, selections and draft quantities.

    Input universe maps every eligible commodity to its complete ordered ranking-month
    session list. Each row supplies the previous SAME contract close, including on a
    front-contract change. Provider calendar/front-chain provenance is caller supplied.
    Missing rows stop the entire formation; they never change the eligible universe.
    """
    month = date.fromisoformat(packet['ranking_month'] + '-01')
    last = month.replace(day=calendar.monthrange(month.year, month.month)[1])
    following = date(last.year + (last.month == 12), last.month % 12 + 1, 1)
    hold_end = following.replace(day=calendar.monthrange(following.year, following.month)[1])
    decision = clock(packet['decision_at'])
    # Session labels use the declared strategy calendar, independent of UTC date conversion.
    if date.fromisoformat(packet['formation_session']) != following:
        raise ValueError('Formation session label must be first calendar day of holding month')
    if decision.date() != following:
        raise ValueError('Draft convention: decide on first UTC calendar day of holding month')
    if not packet['universe_provenance'] or not packet['calendar_provenance']:
        raise ValueError('Frozen universe/calendar provenance required')
    if clock(packet['universe_available_at']) > decision:
        raise ValueError('Universe was unavailable at decision')
    if clock(packet['calendar_available_at']) > decision:
        raise ValueError('Calendar was unavailable at decision')
    universe = packet['universe']
    if not isinstance(universe, dict) or len(universe) < 22:
        raise ValueError('Supply the full eligible universe; source starts with 22 commodities')
    expected = set()
    calendars = {}
    for symbol, sessions in universe.items():
        dates = [date.fromisoformat(s) for s in sessions]
        if not symbol or not dates or dates != sorted(set(dates)):
            raise ValueError('Each commodity needs unique ordered expected sessions')
        if any(d < month or d > last for d in dates):
            raise ValueError('Expected session outside ranking month')
        calendars[symbol] = dates
        expected.update((symbol, d) for d in dates)
    observed = {}
    for row in packet['observations']:
        key = (row['symbol'], date.fromisoformat(row['session']))
        if key not in expected or key in observed:
            raise ValueError('Duplicate, unexpected commodity or out-of-window observation')
        observed[key] = row
    if set(observed) != expected:
        raise ValueError('Incomplete expected panel; no missing-return reallocation')
    scores = []
    with localcontext() as ctx:
        ctx.prec = 40
        for symbol, dates in calendars.items():
            momentum, carry = [], []
            for index, session in enumerate(dates):
                row = observed[symbol, session]
                if not row['front_id'] or not row['second_id'] or row['front_id'] == row['second_id']:
                    raise ValueError('Distinct dated first/second maturity IDs required')
                if row['previous_close_contract_id'] != row['front_id']:
                    raise ValueError('Momentum requires prior close of the same contract, including rolls')
                previous = date.fromisoformat(row['previous_session'])
                if previous >= session or (index and previous != dates[index - 1]):
                    raise ValueError('Prior close must match previous expected session')
                if not index and (previous >= month or previous != date.fromisoformat(
                        packet['warmup_sessions'][symbol])):
                    raise ValueError('First ranking observation needs declared calendar warm-up close')
                front_event, second_event = clock(row['front_event_at']), clock(row['second_event_at'])
                if front_event != second_event:
                    raise ValueError('Front and second prices require a common declared measurement clock')
                if index and clock(row['previous_event_at']) != clock(
                        observed[symbol, dates[index - 1]]['front_event_at']):
                    raise ValueError('Prior event must match previous expected measurement clock')
                if (clock(row['previous_event_at']) >= front_event or
                        clock(row['previous_available_at']) < clock(row['previous_event_at'])):
                    raise ValueError('Invalid prior close clocks')
                if clock(row['previous_available_at']) > front_event:
                    raise ValueError('Prior price not available by current measurement')
                for prefix in ('front', 'second'):
                    available = clock(row[prefix + '_available_at'])
                    if available < front_event or available >= decision:
                        raise ValueError('Decision must follow both price availability clocks')
                first_expiry = date.fromisoformat(row['front_expiry'])
                second_expiry = date.fromisoformat(row['second_expiry'])
                if not session < first_expiry < second_expiry:
                    raise ValueError('Invalid maturity ordering or expired front contract')
                f, s, prev = (positive(row[k]) for k in ('front_close', 'second_close', 'previous_close'))
                momentum.append((f / prev).ln())
                carry.append((f / s).ln())
            scores.append({'symbol': symbol, 'momentum': sum(momentum) / len(dates),
                           'carry': sum(carry) / len(dates), 'sessions': len(dates)})
        # Symbol order breaks exact ties, an explicit implementation convention.
        winners = sorted(scores, key=lambda x: (-x['momentum'], x['symbol']))[:8]
        losers = sorted(scores, key=lambda x: (x['momentum'], x['symbol']))[:8]
        if {s['symbol'] for s in winners} & {s['symbol'] for s in losers}:
            raise ValueError('Tied momentum tails overlap; formation unresolved')
        longs = sorted(winners, key=lambda x: (-x['carry'], x['symbol']))[:4]
        shorts = sorted(losers, key=lambda x: (x['carry'], x['symbol']))[:4]
        nav = positive(packet['reference_nav'])
        plans = []
        for side, selected in ((1, longs), (-1, shorts)):
            for item in selected:
                symbol = item['symbol']
                spec = packet['entry_contracts'][symbol]
                quote_time = clock(spec['reference_price_event_at'])
                available = clock(spec['reference_price_available_at'])
                fx_time = clock(spec['fx_event_at'])
                fx_available = clock(spec['fx_available_at'])
                if not quote_time <= available < decision or not fx_time <= fx_available < decision:
                    raise ValueError('Reference price and FX must be known before decision')
                if clock(spec['spec_available_at']) >= decision:
                    raise ValueError('Contract specification unavailable at decision')
                earliest = clock(spec['earliest_fill_at'])
                roll = clock(spec['next_roll_or_exit_at'])
                deadline = clock(spec['delivery_or_last_trade_deadline'])
                if not decision < earliest < roll < deadline:
                    raise ValueError('Explicit future fill/action and delivery-safe deadline required')
                if roll.date() > hold_end:
                    raise ValueError('Next roll or monthly exit action cannot follow holding month')
                if not spec['contract_id'] or not spec['currency'] or not spec['roll_calendar_provenance']:
                    raise ValueError('Entry contract, currency and roll calendar required')
                price, multiplier, fx = (positive(spec[k]) for k in
                                         ('reference_price', 'multiplier', 'fx_to_account'))
                notional = price * multiplier * fx
                quantity = int((nav / 4 / notional).to_integral_value(rounding=ROUND_FLOOR))
                if quantity == 0:
                    raise ValueError('One full contract exceeds leg budget; do not silently drop leg')
                plans.append({'symbol': symbol, 'side': side, 'contract_id': spec['contract_id'],
                              'signed_quantity': side * quantity, 'reference_notional': str(quantity * notional),
                              'ideal_signed_weight': str(Decimal(side) / 4),
                              'reference_signed_weight': str(side * quantity * notional / nav),
                              'earliest_fill_at': spec['earliest_fill_at'],
                              'next_roll_or_exit_at': spec['next_roll_or_exit_at']})
        return {'status': 'OFFLINE_RESEARCH_PLAN_ONLY', 'ranking_month': packet['ranking_month'],
                'holding_month': following.strftime('%Y-%m'), 'decision_at': packet['decision_at'],
                'scores': [{**s, 'momentum': str(s['momentum']), 'carry': str(s['carry'])}
                           for s in sorted(scores, key=lambda x: x['symbol'])],
                'positions': plans, 'gross_reference_weight': str(sum(
                    abs(Decimal(p['reference_signed_weight'])) for p in plans)),
                'limits': ['Reference prices are not fills; no orders submitted',
                           'Integer floor sizing is an adaptation, not exact fractional source weights',
                           'Margin, fees, cash, roll execution, held-book marks and account gates remain unimplemented',
                           'No stop overlays, missing-data reallocation or summed-log NAV']}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path, help='Offline JSON packet; schema in research README')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.packet.read_bytes()
    result = build_plan(json.loads(raw))
    result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    result['code_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
