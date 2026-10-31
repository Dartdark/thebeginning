"""Replicate frozen CHoCH rules with corrected uploads; no source overwrites."""
import argparse
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
import codex_choch4h as core

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_choch4h_corrected_20261028'
INPUT = ROOT / 'agents/codex/inputs/choch4h_corrected_20261028/local'
ORIGINAL_EXPECTED = core.expected_minutes
ORIGINAL_LEDGER = core.trade_ledger


def expected_minutes(g):
    result = ORIGINAL_EXPECTED(g)
    minute = np.arange(g.D * 1440) % 1440
    date = np.asarray(g.dates).repeat(1440)
    historical_pause = (date < 20210628) & (minute > 915) & (minute <= 930)
    return result & ~historical_pause


def calendar_checks():
    from types import SimpleNamespace
    dates = np.array([20210625, 20210628])
    g = SimpleNamespace(D=2, dates=dates,
                        ts=pd.to_datetime(dates.astype(str)).to_numpy())
    result = expected_minutes(g).reshape(2, 1440)
    assert result[0, 915] and not result[0, 916] and not result[0, 930]
    assert result[0, 931]
    assert result[1, 915:931].all()
    assert result[:, 960].all() and not result[:, 961:1021].any()
    assert result[1, 1021]
    return dict(pre_pause_end=True, post_pause_end=True, maintenance=True)


def ledger(g, valid, events, timing):
    result = ORIGINAL_LEDGER(g, valid, events, timing)
    # Unknown-only ledgers still need the reporting schema; never assign P&L.
    for column in ('state', 'side', 'gross_mnq', 'net_mnq'):
        if column not in result:
            result[column] = np.nan
    return result


def reconcile(overnight_dir):
    destination = INPUT / 'reconciled_overnight'
    destination.mkdir(parents=True, exist_ok=True)
    audit = []
    for year in range(2017, 2023):
        new = overnight_dir / f'NQ_1min_{year}.csv'
        old = ROOT / 'data' / f'NQ_1min_ON_{year}.csv'
        a = pd.read_csv(new).set_index(['date', 'time'])
        b = pd.read_csv(old).set_index(['date', 'time'])
        if not a.index.is_unique or not b.index.is_unique:
            raise ValueError('Duplicate source key requires separate review')
        keys = a.index.intersection(b.index)
        columns = ['open', 'high', 'low', 'close', 'volume']
        if not np.array_equal(a.loc[keys, columns].to_numpy(), b.loc[keys, columns].to_numpy()):
            raise ValueError('Old/new OHLCV conflict; abort reconciliation')
        added = b.index.difference(a.index)
        merged = pd.concat([a, b.loc[added]]).sort_index().reset_index()
        output = destination / f'NQ_1min_{year}.csv'
        if output.exists():
            pd.testing.assert_frame_equal(pd.read_csv(output), merged, check_dtype=False)
        else:
            merged.to_csv(output, index=False)
        audit.append(dict(year=year, identical_overlap=len(keys), conflicts=0,
                          restored_observed_rows=len(added), old_sha256=core.loader.sha(old),
                          uploaded_sha256=core.loader.sha(new), reconciled_sha256=core.loader.sha(output)))
    (OUT / 'reconciliation.json').write_text(json.dumps(audit, indent=2)+'\n')
    return destination


def run(overnight_dir):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'calendar_checks.json').write_text(json.dumps(calendar_checks(), indent=2)+'\n')
    overnight_dir = reconcile(overnight_dir)
    stage = INPUT / 'design_source_reconciled' / 'data'
    stage.mkdir(parents=True, exist_ok=True)
    for year in range(2017, 2023):
        for role, source in [('ON', overnight_dir / f'NQ_1min_{year}.csv'),
                             ('DAY', ROOT / 'data' / f'NQ_1min_{year}.csv')]:
            if not source.exists():
                if year == 2017 and role == 'DAY':
                    continue
                raise FileNotFoundError(source)
            link = stage / f'NQ_1min_{role}_{year}.csv'
            if link.is_symlink():
                if link.resolve() != source.resolve():
                    raise ValueError('Existing input link points to another source')
            elif link.exists():
                raise ValueError('Refusing to replace existing source')
            else:
                link.symlink_to(source.resolve())
    core.OUT = OUT
    core.ROOT = stage.parent
    core.loader.ROOT = stage.parent
    core.expected_minutes = expected_minutes
    core.trade_ledger = ledger
    os.environ['NUMBA_CACHE_DIR'] = str(OUT / 'cache/numba')
    (OUT / 'synthetic_checks.json').write_text(json.dumps(core.synthetic_checks(), indent=2)+'\n')
    core.run_design()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overnight-dir', type=Path, default=INPUT / 'overnight')
    args = parser.parse_args()
    run(args.overnight_dir)
