"""Read-only follow-up: classify gaps conservatively and inventory build evidence.

Regular-hours closures have CME support. Holiday candidates are NOT certified by
a complete historical exchange calendar. No missing row is generated or filled.
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import zipfile
from pathlib import Path

MINUTE = dt.timedelta(minutes=1)
PAUSE_END = dt.date(2021, 6, 28)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def nth_monday(year, month, n):
    d = dt.date(year, month, 1)
    return d + dt.timedelta(days=(-d.weekday()) % 7 + (n - 1) * 7)


def holiday_candidates():
    # Explicit screening hypotheses, not an authoritative exchange calendar.
    full = set(map(dt.date.fromisoformat, [
        '2018-01-01', '2018-03-30', '2018-12-25',
        '2019-01-01', '2019-04-19', '2019-12-25',
        '2020-01-01', '2020-04-10', '2020-12-25',
        '2021-01-01', '2021-12-24', '2022-04-15', '2022-12-26']))
    close = {}
    for y in range(2018, 2023):
        may31 = dt.date(y, 5, 31)
        thanksgiving = dt.date(y, 11, 1)
        thanksgiving += dt.timedelta(days=(3 - thanksgiving.weekday()) % 7 + 21)
        for d in [nth_monday(y, 1, 3), nth_monday(y, 2, 3),
                  may31 - dt.timedelta(days=may31.weekday()), nth_monday(y, 9, 1), thanksgiving]:
            close[d] = 13 * 60
        close[thanksgiving + dt.timedelta(days=1)] = 13 * 60 + 15
    for s in ['2018-07-04', '2019-07-04', '2020-07-03', '2021-07-05', '2022-07-04', '2022-06-20']:
        close[dt.date.fromisoformat(s)] = 13 * 60
    for s in ['2018-07-03', '2019-07-03', '2018-12-24', '2019-12-24', '2020-12-24']:
        close[dt.date.fromisoformat(s)] = 13 * 60 + 15
    close[dt.date(2021, 4, 2)] = 9 * 60 + 15
    return full, close


FULL, EARLY = holiday_candidates()


def classification(t):
    d, m, wd = t.date(), t.hour * 60 + t.minute, t.weekday()
    if wd == 5 or (wd == 6 and m <= 1080) or (wd == 4 and m > 1020):
        return 'regular_weekend_closed'
    if 1020 < m <= 1080:
        return 'regular_daily_maintenance'
    if d < PAUSE_END and wd < 5 and 975 < m <= 990:
        return 'historical_15min_pause'
    if d == dt.date(2018, 12, 5) and 570 < m <= 1020:
        return 'CME_verified_Bush_closure'
    session_date = d + dt.timedelta(days=1) if m > 1080 else d
    if session_date in FULL:
        return 'holiday_calendar_candidate'
    if d in EARLY and EARLY[d] < m <= 1020:
        return 'holiday_calendar_candidate'
    return 'unresolved'


def write_csv(path, fields, rows):
    with path.open('x', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prior', default='scratch_data/codex_bridge_20261108_01')
    p.add_argument('--out', required=True)
    a = p.parse_args()
    prior, out = Path(a.prior), Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    original = json.loads((prior / 'audit.json').read_text())
    source = Path(original['source'])
    inputs = [source] + sorted(prior.glob('NQ_1min_native_ET_close_*.csv'))
    inputs += [prior / 'gaps_2018_2022.csv', prior / 'audit.json']
    before = {str(path): sha(path) for path in inputs}
    assert before[str(source)] == original['sha256_before_and_after']
    for path in inputs[1:6]:
        assert before[str(path)] == original['exports'][path.name]['sha256']
    counts = collections.Counter()
    byyear = collections.defaultdict(collections.Counter)
    gaps, runs = [], []
    unresolved = set()
    with (prior / 'gaps_2018_2022.csv').open(newline='') as f:
        for i, row in enumerate(csv.DictReader(f), 1):
            start = dt.datetime.fromisoformat(row['previous_close_ET']) + MINUTE
            end = dt.datetime.fromisoformat(row['next_close_ET'])
            start = max(start, dt.datetime(2018, 1, 1))
            c = collections.Counter()
            run_start = None
            t = start
            while t < end:
                kind = classification(t)
                c[kind] += 1
                byyear[t.year][kind] += 1
                if kind == 'unresolved':
                    unresolved.add(t)
                    if run_start is None:
                        run_start = t
                elif run_start is not None:
                    runs.append({'gap_id': i, 'start_ET': str(run_start), 'end_ET_inclusive': str(t - MINUTE),
                                 'minutes': int((t - run_start).total_seconds() // 60)})
                    run_start = None
                t += MINUTE
            if run_start is not None:
                runs.append({'gap_id': i, 'start_ET': str(run_start), 'end_ET_inclusive': str(end - MINUTE),
                             'minutes': int((end - run_start).total_seconds() // 60)})
            counts.update(c)
            gaps.append(dict(row, gap_id=i, classifications=json.dumps(dict(c), sort_keys=True)))
    # Input bars: identify off-schedule observations and keep a sparse deterministic
    # sample for comparison timestamp checks. Observed does not imply market open.
    sample, anomalous = {}, []
    for path in inputs[1:6]:
        date_cache = {}
        with path.open(newline='') as f:
            for i, r in enumerate(csv.DictReader(f)):
                date = r['Date']
                if date not in date_cache:
                    mm, dd, yy = map(int, date.split('/'))
                    date_cache[date] = dt.datetime(yy, mm, dd)
                t = date_cache[date] + dt.timedelta(hours=int(r['Time'][:2]), minutes=int(r['Time'][3:]))
                kind = classification(t)
                if kind not in ('unresolved', 'holiday_calendar_candidate'):
                    anomalous.append(dict(r, stamp_ET=str(t), schedule_label=kind))
                if i % 1000 == 0:
                    sample[t] = tuple(r[k] for k in ('Open', 'High', 'Low', 'Close', 'Volume'))
    comparison_inputs = sorted(Path('data').glob('NQ_1min_20[12][0-9].csv'))
    comparison_inputs += sorted(Path('data').glob('NQ_1min_ON_20[12][0-9].csv'))
    hits = collections.defaultdict(list)
    alignment = collections.defaultdict(collections.Counter)
    comp_hashes = {}
    for path in comparison_inputs:
        if not 2018 <= int(path.stem[-4:]) <= 2022:
            continue
        comp_hashes[str(path)] = sha(path)
        cache = {}
        with path.open(newline='') as f:
            for row in csv.DictReader(f):
                d = row['date']
                if d not in cache:
                    cache[d] = dt.datetime(int(d[:4]), int(d[4:6]), int(d[6:8]))
                m = int(row['time'])
                # Repository Grid24 specifies CT bar-close stamps. ET is always CT+1h
                # on these trading dates, with synchronized US DST transitions.
                t = cache[d] + dt.timedelta(hours=m // 100 + 1, minutes=m % 100)
                if t in unresolved:
                    hits[t].append({'file': str(path), 'volume': float(row['volume'])})
                values = tuple(float(row[k]) for k in ('open', 'high', 'low', 'close', 'volume'))
                for shift in (-1, 0, 1):
                    ref = sample.get(t + shift * MINUTE)
                    if ref is not None:
                        c = alignment[str(shift)]
                        c['comparisons'] += 1
                        c['exact_ohlcv_matches'] += values == tuple(map(float, ref))
                        c['exact_ohlc_matches'] += values[:4] == tuple(map(float, ref[:4]))
    for run in runs:
        t, stop = dt.datetime.fromisoformat(run['start_ET']), dt.datetime.fromisoformat(run['end_ET_inclusive'])
        n, positive = 0, 0
        while t <= stop:
            n += t in hits
            positive += any(x['volume'] > 0 for x in hits[t]) if t in hits else False
            t += MINUTE
        run['other_owned_bars'] = n
        run['other_owned_positive_volume_bars'] = positive
    assert sum(r['minutes'] for r in runs) == counts['unresolved'] == len(unresolved)
    assert sum(r['other_owned_bars'] for r in runs) == len(hits)
    assert all(r['other_owned_positive_volume_bars'] <= r['other_owned_bars'] <= r['minutes'] for r in runs)
    assert sum(counts.values()) == sum(sum(json.loads(r['classifications']).values()) for r in gaps)
    write_csv(out / 'classified_gap_intervals.csv', list(gaps[0]), gaps)
    write_csv(out / 'unresolved_runs.csv', list(runs[0]), sorted(runs, key=lambda r: -r['minutes']))
    write_csv(out / 'off_schedule_observed.csv', ['stamp_ET', 'schedule_label'] + list(anomalous[0].keys())[:-2]
              if anomalous else ['stamp_ET', 'schedule_label'], anomalous)
    # Build metadata: restrict to named research-data roots; never read config,
    # licence, login, environment, API-key or broker files.
    research_names = {'ofb_bars_NQ.csv', 'ofb_hist.bin', 'ofb_depth.bin', 'ofb_gex.bin', 'ofb_cot.bin',
                      'ofb_no_data_days.json', 'OrderFlowBridge.dll', 'raw'}
    inventory = []
    root = Path(r'C:\OFB')
    for path in root.iterdir():
        if path.name in research_names:
            st = path.stat()
            inventory.append({'name': path.name, 'bytes': st.st_size, 'mtime_local_host': str(dt.datetime.fromtimestamp(st.st_mtime))})
    headers = {}
    for name in ('ofb_hist.bin', 'ofb_depth.bin'):
        with (root / name).open('rb') as f:
            headers[name] = f.read(16).hex()  # opaque header, no speculative decoder
    archives = []
    for path in sorted(Path(r'C:\Users\dmoto\Downloads').glob('TheBridge*.zip')):
        with zipfile.ZipFile(str(path)) as z:
            archives.append({'path': str(path), 'sha256': sha(path), 'entries': z.namelist(),
                             'manuals': {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('/MANUAL.pdf')}})
    after = {str(path): sha(path) for path in inputs}
    assert before == after, 'Preserved input changed during investigation'
    assert comp_hashes == {path: sha(Path(path)) for path in comp_hashes}, 'Comparison input changed'
    summary = {'preserved_hashes': before, 'preserved_before_after': before == after,
               'classified_minutes': dict(counts), 'classified_minutes_by_year': dict(byyear),
               'prior_gap_intervals': len(gaps), 'unresolved_runs': len(runs),
               'unresolved_length_distribution': dict(collections.Counter(r['minutes'] for r in runs)),
               'unresolved_other_owned_bar_minutes': len(hits),
               'unresolved_other_owned_positive_volume_minutes': sum(any(x['volume'] > 0 for x in h) for h in hits.values()),
               'comparison_hashes': comp_hashes, 'comparison_sample_alignment': dict(alignment),
               'off_schedule_observed_rows': anomalous,
               'data_root_inventory': inventory, 'opaque_binary_first16_hex': headers,
               'raw_directory_present': (root / 'raw').exists(), 'archives': archives,
               'holiday_warning': 'Candidate screening rules, NOT exchange-certified historical trading calendar.',
               'mapping_warning': 'No dated-contract mapping, original request receipt or build manifest recovered. No fill/merge.'}
    with (out / 'summary.json').open('x') as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('preserved_hashes', 'archives', 'comparison_hashes', 'data_root_inventory')}, indent=2))


if __name__ == '__main__':
    main()
