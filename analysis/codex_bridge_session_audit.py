"""Summarize observed ET session coverage without assuming a holiday calendar."""
import collections
import csv
import datetime as dt
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
sessions = collections.defaultdict(list)
for path in sorted(out.glob('NQ_1min_native_ET_close_*.csv')):
    with path.open(newline='') as f:
        for row in csv.DictReader(f):
            date = row['Date']
            m = int(row['Time'][:2]) * 60 + int(row['Time'][3:])
            sessions[(date, m > 1080)].append(m)
joined = collections.defaultdict(list)
for (date, evening), minutes in sessions.items():
    day = dt.datetime.strptime(date, '%m/%d/%Y').date()
    if evening:
        day += dt.timedelta(days=1)
    joined[day].extend(m - 1080 if m > 1080 else m + 360 for m in minutes)
summary = {}
with (out / 'session_counts.csv').open('x', newline='') as f:
    w = csv.writer(f)
    w.writerow(['session_date', 'observed_rows', 'first_close_offset_from_1800_ET',
                'last_close_offset', 'interior_unrepresented_minutes', 'evening_rows', 'morning_rows'])
    for day, offsets in sorted(joined.items()):
        offsets.sort()
        interior = sum(b - a - 1 for a, b in zip(offsets, offsets[1:]))
        w.writerow([day, len(offsets), offsets[0], offsets[-1], interior,
                    sum(m <= 359 for m in offsets), sum(360 <= m <= 930 for m in offsets)])
for year in range(2018, 2023):
    subset = {d: ms for d, ms in joined.items() if d.year == year}
    summary[year] = {
        'observed_sessions': len(subset),
        'row_count_distribution': dict(sorted(collections.Counter(map(len, subset.values())).items())),
        'sessions_with_evening_and_morning': sum(any(m <= 359 for m in ms) and any(360 <= m <= 930 for m in ms) for ms in subset.values()),
        'sessions_starting_1801_ending_1700_ET': sum(min(ms) == 1 and max(ms) == 1380 for ms in subset.values()),
        'sessions_with_exact_1380_contiguous_close_minutes': sum(sorted(ms) == list(range(1, 1381)) for ms in subset.values()),
    }
with (out / 'session_summary.json').open('x') as f:
    json.dump(summary, f, indent=2)
print(json.dumps(summary, indent=2))
