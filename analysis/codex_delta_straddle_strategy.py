"""Offline interpreted SSRN4677166 signal/whole-lot planner; never sends orders.

No fills, returns backtest or account profitability are inferred from proposals.
Usage/schema: agents/codex/research/delta_straddle/README.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HORIZONS = (32, 64, 126, 252, 504)
DECAY = .94
RISK_TARGET = .10
BAND = .25
# Appendix weights already include the asset-class allocation. Preserve printed rounding.
WEIGHTS = dict((s, w / 100) for s, w in (
    ('GX1', 2.24), ('VG1', 3.53), ('Z1', 1), ('ES1', 12.06), ('FTJGUSSE', .69),
    ('NQ1', 1.32), ('NI1', 1.08), ('TP1', .88), ('KM1', .94), ('HI1', 1.26),
    ('EURUSDCR', 9.46), ('GBPUSDCR', 3.87), ('SEKUSDCR', .67), ('CADUSDCR', 1.54),
    ('JPYUSDCR', 6.75), ('AUDUSDCR', 2.07), ('NZDUSDCR', .63),
    ('CO1', 4.64), ('CL1', 9.75), ('HO1', 1.06), ('XB1', .96), ('NG1', 1.77),
    ('GC1', 2.89), ('SI1', .60), ('HG1', .65), ('C1', .60), ('S1', 2.09),
    ('ED4', 2.52), ('TU1', 1.38), ('FV1', 2.06), ('TY1', 3.83), ('US1', .85),
    ('DU1', 1.58), ('OE1', 2.96), ('RX1', 5.04), ('OAT1', .82), ('IK1', .65),
    ('G1', .60), ('JB1', 1.47), ('YM1_Australian3Y', .56), ('XM1', .66)))


def number(value, name, minimum=None, strict=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{name}: finite number required')
    if not math.isfinite(value) or (minimum is not None and
            (value <= minimum if strict else value < minimum)):
        raise ValueError(f'{name}: out of range')
    return float(value)


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name}: nonempty provenance/identity required')
    return value


def clock(value):
    stamp = datetime.fromisoformat(text(value, 'timestamp').replace('Z', '+00:00'))
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError('Offset-aware UTC/action clock required')
    return stamp.astimezone(timezone.utc)


def session(value):
    result = date.fromisoformat(value)
    if result.isoformat() != value:
        raise ValueError('Session must use YYYY-MM-DD')
    return result


def signal(returns):
    """Completed daily simple-return observations only; no AR(1) adjustment."""
    if len(returns) < max(HORIZONS):
        raise ValueError('Need 504 complete prior observations')
    values = [number(r, 'simple return', -1, strict=True) for r in returns]
    components = {}
    for horizon in HORIZONS:
        tail = values[-horizon:]
        sd = statistics.stdev(tail)
        if sd <= 0:
            raise ValueError('Undefined zero-variance horizon signal')
        components[str(horizon)] = math.erf(math.sqrt(horizon) * statistics.mean(tail)
                                             / sd / math.sqrt(2))
    variance = values[0] ** 2
    for value in values[1:]:
        variance = DECAY * variance + (1 - DECAY) * value ** 2
    vol = math.sqrt(252 * variance)
    if not math.isfinite(vol) or vol <= 0:
        raise ValueError('Invalid EWMA sizing volatility')
    return {'signal': statistics.mean(components.values()), 'components': components,
            'annual_vol': vol}


def _snapshot(snap, decision, maximum_age):
    text(snap['contract_id'], 'dated contract ID')
    text(snap['provenance'], 'native mapping/margin/cost provenance')
    event, available = clock(snap['asof_at']), clock(snap['available_at'])
    if not event <= available <= decision or (decision - event).total_seconds() > maximum_age:
        raise ValueError('Future or stale native contract/margin/cost snapshot')
    if clock(snap['expiry_at']) <= decision:
        raise ValueError('Expired native contract')
    for name in ('usd_return_notional', 'reference_price', 'margin_per_lot'):
        number(snap[name], name, 0, strict=True)
    for name in ('fee_per_lot_usd', 'spread_slippage_per_lot_usd'):
        number(snap[name], name, 0)


def validate(packet):
    if packet['kind'] not in ('synthetic', 'historical_review'):
        raise ValueError('Explicit synthetic/historical_review input kind required')
    decision = clock(packet['decision_at'])
    nav = number(packet['nav_usd'], 'NAV', 0, strict=True)
    margin = number(packet['margin_budget_usd'], 'margin budget', 0)
    if margin > nav:
        raise ValueError('Margin budget exceeds NAV')
    number(packet['gross_limit_multiple'], 'gross limit', 0, strict=True)
    latency = number(packet['latency_seconds'], 'latency', 0, strict=True)
    maximum_age = number(packet['max_snapshot_age_seconds'], 'snapshot age', 0, strict=True)
    held_at, held_available = clock(packet['held_asof_at']), clock(packet['held_available_at'])
    text(packet['held_provenance'], 'confirmed holdings provenance')
    if not held_at <= held_available <= decision or (decision - held_at).total_seconds() > maximum_age:
        raise ValueError('Future or stale confirmed holdings')
    text(packet['calendar_provenance'], 'calendar provenance')
    text(packet['history_provenance'], 'history provenance')
    if clock(packet['calendar_available_at']) > decision:
        raise ValueError('Future calendar knowledge')
    dates = [session(s) for s in packet['sessions']]
    if len(dates) < 504 or dates != sorted(set(dates)):
        raise ValueError('Need at least 504 unique ordered complete sessions')
    if dates[-1] != session(packet['last_complete_session']):
        raise ValueError('Last complete session mismatch')
    following = session(packet['next_session'])
    if not dates[-1] < following or decision.date() > following:
        raise ValueError('Invalid supplied next-session clock')
    if not 0 <= (decision.date() - dates[-1]).days <= 7:
        raise ValueError('Stale/future last complete observation')
    multiplier = packet['portfolio_multiplier']
    value = number(multiplier['value'], 'portfolio multiplier', 0, strict=True)
    if value > 10:
        raise ValueError('Portfolio multiplier exceeds build bound 10')
    text(multiplier['provenance'], 'risk calibration provenance')
    if not clock(multiplier['sample_end_at']) <= clock(multiplier['available_at']) <= decision:
        raise ValueError('Future or impossible risk calibration')
    if clock(multiplier['sample_end_at']) >= decision:
        raise ValueError('Risk calibration must precede decision')
    if (decision - clock(multiplier['available_at'])).total_seconds() > maximum_age:
        raise ValueError('Stale risk calibration')
    rows = packet['observations']
    if len(rows) != len(dates):
        raise ValueError('Calendar/observation count mismatch')
    histories = {s: [] for s in WEIGHTS}
    previous = None
    for day, row in zip(dates, rows):
        event, available = clock(row['event_at']), clock(row['available_at'])
        if session(row['session']) != day or event.date() != day:
            raise ValueError('Observation session/event mismatch')
        if not event <= available <= decision or (previous is not None and event <= previous):
            raise ValueError('Unavailable or unordered observations')
        previous = event
        if set(row['returns']) != set(WEIGHTS):
            raise ValueError('Exact 41-market universe required; no proxies/drop/fill')
        for symbol, result in row['returns'].items():
            histories[symbol].append(number(result, 'return', -1, strict=True))
    if set(packet['markets']) != set(WEIGHTS) or set(packet['held']) != set(WEIGHTS):
        raise ValueError('Explicit 41-market native mapping and confirmed holdings required')
    for symbol in WEIGHTS:
        snap, held = packet['markets'][symbol], packet['held'][symbol]
        _snapshot(snap, decision, maximum_age)
        if clock(snap['expiry_at']) <= decision + timedelta(seconds=latency):
            raise ValueError('Contract expires before eligible fill')
        text(held['contract_id'], 'held contract ID')
        if isinstance(held['lots'], bool) or not isinstance(held['lots'], int):
            raise ValueError('Confirmed held lots must be integers')
        if held['lots'] and held['contract_id'] != snap['contract_id']:
            old = snap['old_contract']
            _snapshot(old, decision, maximum_age)
            if clock(old['expiry_at']) <= decision + timedelta(seconds=latency):
                raise ValueError('Old contract expires before eligible roll close')
            if old['contract_id'] != held['contract_id']:
                raise ValueError('Old roll mapping does not identify actual holdings')
    return histories, decision + timedelta(seconds=latency)


def plan(packet):
    """Return offline proposals without mutating the supplied actual holdings."""
    histories, eligible = validate(packet)
    nav = packet['nav_usd']
    budget = nav * RISK_TARGET * packet['portfolio_multiplier']['value']
    legs, desired = {}, {}
    for symbol, weight in WEIGHTS.items():
        snap, held = packet['markets'][symbol], packet['held'][symbol]
        diagnostic = signal(histories[symbol])
        scale = budget * weight / diagnostic['annual_vol']
        target_usd = scale * diagnostic['signal']
        raw_lots = math.trunc(target_usd / snap['usd_return_notional'])
        rolling = bool(held['lots'] and held['contract_id'] != snap['contract_id'])
        held_snap = snap['old_contract'] if rolling else snap
        held_usd = held['lots'] * held_snap['usd_return_notional']
        inside_band = abs(target_usd - held_usd) < BAND * scale
        desired[symbol] = held['lots'] if inside_band and not rolling else raw_lots
        legs[symbol] = {**diagnostic, 'target_usd': target_usd,
                        'band_usd': BAND * scale, 'unrounded_lots': target_usd / snap['usd_return_notional'],
                        'raw_target_lots': raw_lots, 'held_lots': held['lots'], 'rolling': rolling,
                        'band_held': inside_band and not rolling}
    gross = sum(abs(n) * packet['markets'][s]['usd_return_notional'] for s, n in desired.items())
    margin = sum(abs(n) * packet['markets'][s]['margin_per_lot'] for s, n in desired.items())
    cap = packet['gross_limit_multiple'] * nav
    shrink = min(1., cap / gross if gross else 1.,
                 packet['margin_budget_usd'] / margin if margin else 1.)
    final = {s: math.trunc(n * shrink) for s, n in desired.items()}
    orders = []
    for symbol, lots in final.items():
        snap, held, item = packet['markets'][symbol], packet['held'][symbol], legs[symbol]
        item.update({'target_lots': lots, 'budget_override': lots != desired[symbol],
                     'whole_lot_tracking_error_usd': lots * snap['usd_return_notional'] - item['target_usd']})
        changes = [(snap, lots - held['lots'], 'rebalance')]
        if item['rolling']:
            changes = [(snap['old_contract'], -held['lots'], 'roll_close'), (snap, lots, 'roll_open')]
        for mapping, change, reason in changes:
            if change:
                orders.append({'symbol': symbol, 'contract_id': mapping['contract_id'],
                               'delta_lots': change, 'reason': reason,
                               'earliest_eligible_fill_at': eligible.isoformat(),
                               'estimated_commission_usd': abs(change) * mapping['fee_per_lot_usd'],
                               'estimated_spread_slippage_usd': abs(change) * mapping['spread_slippage_per_lot_usd']})
    gross_final = sum(abs(n) * packet['markets'][s]['usd_return_notional'] for s, n in final.items())
    margin_final = sum(abs(n) * packet['markets'][s]['margin_per_lot'] for s, n in final.items())
    if gross_final > cap + 1e-7 or margin_final > packet['margin_budget_usd'] + 1e-7:
        raise ValueError('Post-rounding budget violation')
    return {'status': 'OFFLINE_PROPOSALS_ONLY', 'input_kind': packet['kind'],
            'financial_return_trials': 0, 'personal_account_admitted': False,
            'decision_at': packet['decision_at'], 'market_count': len(WEIGHTS),
            'budget_scale': shrink, 'gross_notional_usd': gross_final,
            'margin_usd': margin_final, 'signals_and_targets': legs, 'orders': orders,
            'estimated_commission_usd': sum(o['estimated_commission_usd'] for o in orders),
            'estimated_spread_slippage_usd': sum(o['estimated_spread_slippage_usd'] for o in orders),
            'limits': ['No fills or historical P&L inferred',
                       'Budgets constrain targets, not gap losses or transient roll execution exposure',
                       'No collateral/carry/cash/FX/native execution backtest admitted']}


def demo_packet():
    """Invented 41-market engineering fixture, never market evidence."""
    start = date(2024, 1, 1)
    dates = []
    while len(dates) < 520:
        if start.weekday() < 5:
            dates.append(start)
        start += timedelta(days=1)
    decision = datetime.combine(dates[-1], datetime.min.time(), timezone.utc) + timedelta(hours=23)
    snapshots = {}
    for symbol in WEIGHTS:
        snapshots[symbol] = {'contract_id': symbol + '_INVENTED_DATED_CONTRACT',
            'asof_at': (decision - timedelta(minutes=2)).isoformat(),
            'available_at': (decision - timedelta(minutes=1)).isoformat(),
            'expiry_at': (decision + timedelta(days=30)).isoformat(),
            'usd_return_notional': 1000., 'reference_price': 100., 'margin_per_lot': 50.,
            'fee_per_lot_usd': .50, 'spread_slippage_per_lot_usd': .75,
            'provenance': 'SYNTHETIC: no executable market mapping implied'}
    next_day = dates[-1] + timedelta(days=1)
    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)
    return {'kind': 'synthetic', 'decision_at': decision.isoformat(), 'nav_usd': 100000.,
        'gross_limit_multiple': 3., 'margin_budget_usd': 25000., 'latency_seconds': 60.,
        'max_snapshot_age_seconds': 86400., 'calendar_provenance': 'SYNTHETIC weekday-only fixture',
        'calendar_available_at': (decision - timedelta(days=1)).isoformat(),
        'history_provenance': 'SYNTHETIC sinusoidal simple returns, not prices or fitted parameters',
        'held_asof_at': (decision - timedelta(minutes=2)).isoformat(),
        'held_available_at': (decision - timedelta(minutes=1)).isoformat(),
        'held_provenance': 'SYNTHETIC explicit zero lots, no broker connection',
        'sessions': [d.isoformat() for d in dates], 'last_complete_session': dates[-1].isoformat(),
        'next_session': next_day.isoformat(),
        'portfolio_multiplier': {'value': 1., 'sample_end_at': (decision - timedelta(hours=2)).isoformat(),
            'available_at': (decision - timedelta(hours=1)).isoformat(), 'provenance': 'SYNTHETIC fixed scalar'},
        'observations': [{'session': d.isoformat(), 'event_at': d.isoformat() + 'T21:00:00+00:00',
            'available_at': d.isoformat() + 'T21:05:00+00:00',
            'returns': {s: .0004 * (1 if j % 2 == 0 else -1) + .01 * math.sin(i * .83 + j)
                        for j, s in enumerate(WEIGHTS)}} for i, d in enumerate(dates)],
        'markets': snapshots,
        'held': {s: {'contract_id': m['contract_id'], 'lots': 0} for s, m in snapshots.items()}}


def admission():
    root = Path(__file__).resolve().parents[1]
    return {'personal': 'NEEDS DATA AND SPECIFICATION; no measured portfolio place',
            'apex_50k_evaluation': 'Incompatible source multiday holding rule',
            'apex_150k_evaluation': 'Incompatible source multiday holding rule',
            'apex_50k_funded': 'Incompatible source multiday holding rule',
            'apex_150k_funded': 'Incompatible source multiday holding rule',
            'financial_trials': 0, 'historical_backtest_run': False,
            'owned_top_level_file_count': sum(p.is_file() for p in (root / 'data').glob('*')),
            'blockers': ['No admitted complete 41-market return panel with 504-session warmup',
                         'No authenticated native FX/contract/roll/carry/collateral/cash/margin ledger',
                         'Original signal/risk-calibration/clock choices remain unresolved',
                         'Evidence is not TEST; no economic preregistration or portfolio comparison earned'],
            'data_receipt': 'agents/codex/inputs/delta_straddle_4677166/free_data_gate.md'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--packet', type=Path)
    mode.add_argument('--demo', action='store_true')
    mode.add_argument('--admission', action='store_true')
    mode.add_argument('--write-demo', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.write_demo:
        args.write_demo.write_text(json.dumps(demo_packet(), indent=2, allow_nan=False) + '\n')
        print('Wrote synthetic input packet; no financial test')
        return
    if args.admission:
        output = admission()
    else:
        packet = demo_packet() if args.demo else json.loads(args.packet.read_text())
        output = plan(packet)
        output['input_sha256'] = hashlib.sha256(json.dumps(packet, sort_keys=True, allow_nan=False).encode()).hexdigest()
    output['code_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rendered = json.dumps(output, indent=2, allow_nan=False) + '\n'
    if args.output:
        args.output.write_text(rendered)
        print(json.dumps({'output': str(args.output), 'financial_trials': 0}))
    else:
        print(rendered)


if __name__ == '__main__':
    main()
