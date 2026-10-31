"""No-return audit of supplied methods with synthetic fixtures; CSV date/time inventory only.

This does NOT run Jesse, indicators, fills or a strategy backtest. Fee-free fixtures use
the pinned Jesse helper functions with a minimal precision helper. No trading connections.
"""
import ast
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/MeanReversionRSI.py'
REFERENCE = ROOT / 'agents/codex/inputs/jesse_rsi_audit/utils.py'
REF_COMMIT = '9a3ebe075d9d0af5f012f921f46c2286f234af68'
OUT = ROOT / 'analysis/outputs/codex_rsi_bollinger_source_audit'


def helper():
    """Execute only the official helper definitions, with precision stub disclosed."""
    wanted = {'risk_to_qty', 'risk_to_size', 'size_to_qty'}
    tree = ast.parse(REFERENCE.read_text())
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    assert {n.name for n in funcs} == wanted
    namespace = {
        'math': math,
        'jh': SimpleNamespace(floor_with_precision=lambda v, p: math.floor(v * 10**p) / 10**p),
    }
    exec(compile(ast.Module(body=funcs, type_ignores=[]), str(REFERENCE), 'exec'), namespace)
    return SimpleNamespace(risk_to_qty=namespace['risk_to_qty'])


class FixtureStrategy:
    exchange = 'SYNTHETIC'
    symbol = 'SYNTHETIC'
    available_margin = 10_000.0
    fee_rate = 0.0
    price = 2_100.0
    candles = 'current'

    def get_candles(self, exchange, symbol, timeframe):
        assert timeframe == '4h'
        return 'higher'


def methods_audit():
    state = {'atr': 10.0, 'rsi': 75.0, 'trend_line': 1_900.0}
    ta = SimpleNamespace(
        rsi=lambda _: state['rsi'],
        supertrend=lambda _: SimpleNamespace(trend=state['trend_line']),
        adx=lambda _: 50.0,
        bollinger_bands=lambda _: SimpleNamespace(lowerband=2_000.0, middleband=2_100.0, upperband=2_200.0),
        atr=lambda _: state['atr'],
    )
    tree = ast.parse(SOURCE.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    namespace = {'Strategy': FixtureStrategy, 'ta': ta, 'utils': helper()}
    exec(compile(ast.Module(body=[cls], type_ignores=[]), str(SOURCE), 'exec'), namespace)
    strategy_type = namespace[cls.name]
    cases = []
    for side in ('long', 'short'):
        for atr in (10.0, 5.0, 2.0):
            state.update(atr=atr, rsi=75.0 if side == 'long' else 25.0,
                         trend_line=1_900.0 if side == 'long' else 2_300.0)
            s = strategy_type()
            assert getattr(s, f'should_{side}')()
            getattr(s, f'go_{side}')()
            qty, entry = s.buy if side == 'long' else s.sell
            s.is_long, s.is_short = side == 'long', side == 'short'
            s.position = SimpleNamespace(qty=qty, entry_price=entry)
            s.on_open_position(None)
            distance = abs(entry - s.stop_loss[1])
            cases.append(dict(side=side, capital=s.available_margin, atr_submission=atr,
                              atr_fill=atr, submitted_qty=qty, entry=entry, stop=s.stop_loss[1],
                              stop_distance=distance, nominal_stop_loss=qty * distance,
                              risk_pct_of_input_margin=100 * qty * distance / s.available_margin))
    state.update(atr=10.0, rsi=75.0, trend_line=1_900.0)
    s = strategy_type()
    s.go_long()
    qty, entry = s.buy
    state['atr'] = 20.0
    s.is_long, s.is_short = True, False
    s.position = SimpleNamespace(qty=qty, entry_price=entry)
    s.on_open_position(None)
    cases.append(dict(side='long_atr_change', capital=s.available_margin, atr_submission=10.0,
                      atr_fill=20.0, submitted_qty=qty, entry=entry, stop=s.stop_loss[1],
                      stop_distance=entry - s.stop_loss[1],
                      nominal_stop_loss=qty * (entry - s.stop_loss[1]),
                      risk_pct_of_input_margin=100 * qty * (entry - s.stop_loss[1]) / s.available_margin))
    try:
        s.watch_list()
    except AttributeError as exc:
        watch_error = str(exc)
    else:
        raise AssertionError('Expected missing bbw attribute in supplied source')
    assert 'bbw' in watch_error
    assert cases[0]['risk_pct_of_input_margin'] == 15.0
    assert cases[1]['risk_pct_of_input_margin'] == 7.5
    assert cases[2]['risk_pct_of_input_margin'] == 3.0
    assert cases[-1]['risk_pct_of_input_margin'] == 30.0
    assert s.should_cancel_entry() is True
    return pd.DataFrame(cases), dict(watch_list_error=watch_error,
                                    has_update_position='update_position' in {n.name for n in cls.body if isinstance(n, ast.FunctionDef)},
                                    should_cancel_entry=True)


def metadata_inventory():
    """Read only date/time columns; clock coverage is not a completeness audit."""
    rows = []
    patterns = [('GC', 'GC_1min_20*.csv'), ('NQ_day', 'NQ_1min_20*.csv'),
                ('NQ_night', 'NQ_1min_ON_20*.csv')]
    for label, pattern in patterns:
        for path in sorted((ROOT / 'data').glob(pattern)):
            d = pd.read_csv(path, usecols=['date', 'time'])
            t = d.time.astype(int)
            rows.append(dict(market_file_group=label, file=str(path.relative_to(ROOT)), rows=len(d),
                             first_date=int(d.date.min()), last_date=int(d.date.max()),
                             distinct_dates=int(d.date.nunique()), first_clock=int(t.min()), last_clock=int(t.max()),
                             rows_before_0800=int((t < 800).sum()), rows_from_1700=int((t >= 1700).sum()),
                             duplicate_date_time_rows=int(d.duplicated(['date', 'time']).sum())))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sizing, findings = methods_audit()
    inventory = metadata_inventory()
    sizing.to_csv(OUT / 'synthetic_sizing.csv', index=False)
    inventory.to_csv(OUT / 'date_time_inventory.csv', index=False)
    summary = dict(source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                   reference_commit=REF_COMMIT,
                   reference_sha256=hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
                   findings=findings, fixture_rows=len(sizing), metadata_files=len(inventory),
                   returns_read=False, return_trials=0, jesse_engine_executed=False,
                   precision_helper='math.floor(value * 10**precision) / 10**precision; zero-fee fixtures only')
    (OUT / 'audit.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(sizing.to_string(index=False))
    print(json.dumps(summary, indent=2))
    print(inventory.groupby('market_file_group').agg(files=('file', 'count'),
          first_date=('first_date', 'min'), last_date=('last_date', 'max'),
          rows_before_0800=('rows_before_0800', 'sum'), rows_from_1700=('rows_from_1700', 'sum')).to_string())


if __name__ == '__main__':
    main()
