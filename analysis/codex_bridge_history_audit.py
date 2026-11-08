"""Export and audit existing Bridge bars; no network, DLL, config or trading access."""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', default=r'C:\OFB\ofb_bars_NQ.csv')
    p.add_argument('--destination', required=True)
    a = p.parse_args()
    source, out = Path(a.source), Path(a.destination)
    out.mkdir(parents=True, exist_ok=False)
    before = digest(source)
    stats = collections.defaultdict(collections.Counter)
    days = collections.defaultdict(collections.Counter)
    hours = collections.defaultdict(collections.Counter)
    first, last, previous = {}, {}, None
    seen = set()
    handles, writers = {}, {}
    gaps = []
    native = {}
    with source.open(newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for row in reader:
            stamp = dt.datetime.strptime(row['Date'] + ' ' + row['Time'], '%m/%d/%Y %H:%M')
            y = stamp.year
            s = stats[y]
            s['rows'] += 1
            s['duplicate_timestamps'] += stamp in seen
            s['non_increasing'] += previous is not None and stamp <= previous
            seen.add(stamp)
            first.setdefault(y, str(stamp))
            last[y] = str(stamp)
            minute = stamp.hour * 60 + stamp.minute
            # Close labels: RTH 09:31..16:00 ET; all other bars count as outside RTH.
            s['outside_rth_rows'] += not (571 <= minute <= 960)
            s['evening_rows_1801_2359'] += minute >= 1081
            s['premarket_rows_0000_0930'] += minute <= 570
            s['maintenance_rows_1701_1800'] += 1021 <= minute <= 1080
            s['sunday_rows'] += stamp.weekday() == 6
            v, buy, sell = (int(row[k]) for k in ('Volume', 'UpVol', 'DownVol'))
            s['volume_identity_failures'] += v != buy + sell
            s['negative_volume_rows'] += min(v, buy, sell) < 0
            o, h, l, c = (float(row[k]) for k in ('Open', 'High', 'Low', 'Close'))
            s['invalid_ohlc_rows'] += not (l <= min(o, c) <= max(o, c) <= h)
            s['off_tick_rows'] += any(abs(x * 4 - round(x * 4)) > 1e-6 for x in (o, h, l, c))
            days[y][str(stamp.date())] += 1
            hours[y][str(stamp.hour)] += 1
            if 2018 <= y <= 2022:
                if y not in handles:
                    handles[y] = (out / ('NQ_1min_native_ET_close_%d.csv' % y)).open('x', newline='')
                    writers[y] = csv.DictWriter(handles[y], fieldnames=fields)
                    writers[y].writeheader()
                writers[y].writerow(row)
                native[(int(stamp.strftime('%Y%m%d')), stamp.hour * 100 + stamp.minute)] = (v, buy, sell)
                if previous is not None and stamp - previous > dt.timedelta(minutes=1):
                    gaps.append([str(previous), str(stamp), int((stamp - previous).total_seconds() / 60) - 1])
            previous = stamp
    for f in handles.values():
        f.close()
    legacy = {}
    for path in sorted(Path('data').glob('OF_1min_20[12][0-9]_*.csv')):
        if not 2018 <= int(path.name[8:12]) <= 2022:
            continue
        counter = collections.Counter()
        with path.open(newline='') as f:
            for row in csv.DictReader(f):
                key = int(row['date']), int(row['time'])
                values = tuple(int(float(row[k])) for k in ('volume', 'upvol', 'downvol'))
                counter['rows'] += 1
                counter['identity_failures'] += values[0] != values[1] + values[2]
                if key in native:
                    counter['matched_timestamps'] += 1
                    counter['all_volume_fields_match_native'] += values == native[key]
                    counter['legacy_volume_equals_native_buy'] += values[0] == native[key][1]
                    counter['legacy_upvol_equals_native_buy'] += values[1] == native[key][1]
                    counter['legacy_downvol_equals_native_sell'] += values[2] == native[key][2]
        legacy[str(path)] = dict(counter)
    after = digest(source)
    assert before == after, 'Source changed during audit'
    result = {'source': str(source), 'sha256_before_and_after': before, 'source_bytes': source.stat().st_size,
              'native_fields': fields, 'first': first, 'last': last, 'year_stats': dict(stats),
              'hour_counts_ET': dict(hours), 'legacy_exports': legacy,
              'exports': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in out.glob('*.csv')},
              'gap_note': 'All >1 minute gaps listed, including expected maintenance/weekends/holidays; not a missing-data verdict.'}
    with (out / 'audit.json').open('x') as f:
        json.dump(result, f, indent=2)
    with (out / 'gaps_2018_2022.csv').open('x', newline='') as f:
        w = csv.writer(f)
        w.writerow(['previous_close_ET', 'next_close_ET', 'unrepresented_minutes'])
        w.writerows(gaps)
    with (out / 'daily_counts.csv').open('x', newline='') as f:
        w = csv.writer(f)
        w.writerow(['calendar_date_ET', 'rows'])
        for y in sorted(days):
            w.writerows(sorted(days[y].items()))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
