"""Audit supplied S47 documents and clocks; never load prices or run a strategy.

Re-extract text when needed:
pdftotext -layout agents/codex/inputs/s47/overview.pdf \
    agents/codex/inputs/s47/overview_extracted.txt
"""
from pathlib import Path
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from difflib import unified_diff
import csv
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/s47'
OUT = ROOT / 'analysis/outputs/codex_s47_source_audit'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    v1 = (INPUT / 'source_v1.txt').read_text()
    v2 = (INPUT / 'source_v2.txt').read_text()
    text = (INPUT / 'overview_extracted.txt').read_text()
    normalized = text.replace('\u2060', '').replace('−', '-')
    rows = []
    for year, n1, pnl1, n2, pnl2 in re.findall(
        r'^\s*(20\d{2})\s+(\d+)\s+(-?\$[\d,.]+)\s+(\d+)\s+(-?\$[\d,.]+)\s*$',
        normalized, re.M
    ):
        money = lambda x: float(x.replace('$', '').replace(',', ''))
        rows.append(dict(year=int(year), v1_trades=int(n1), v1_claimed_net_MNQ=money(pnl1),
                         v2_trades=int(n2), v2_claimed_net_MNQ=money(pnl2)))
    assert len(rows) == 10 and [r['year'] for r in rows] == list(range(2017, 2027))
    with (OUT / 'overview_annual_claims.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    totals = {}
    for label, keep in [('full', lambda y: True), ('2017_22', lambda y: y <= 2022),
                        ('2018_22', lambda y: 2018 <= y <= 2022), ('2023_plus', lambda y: y >= 2023)]:
        subset = [r for r in rows if keep(r['year'])]
        totals[label] = {k: sum(r[k] for r in subset) for k in rows[0] if k != 'year'}
    assert totals['full']['v1_trades'] == 1566
    assert totals['full']['v2_trades'] == 785
    assert totals['full']['v1_claimed_net_MNQ'] == 31253
    assert totals['full']['v2_claimed_net_MNQ'] == 24586.5
    # Independent calendar comparison, no market observations or returns.
    london, chicago = ZoneInfo('Europe/London'), ZoneInfo('America/Chicago')
    d = date(2017, 1, 1)
    end = date(2026, 10, 23)
    checked, mismatches, clocks = 0, [], {}
    while d <= end:
        if d.weekday() < 5:
            # PowerLanguage DayOfWeek: Sunday=0. Formulas copied from source.
            dow = lambda month, day: (date(d.year, month, day).weekday() + 1) % 7
            last_mar = 31 - dow(3, 31)
            last_oct = 31 - dow(10, 31)
            second_mar = 8 + (7 - dow(3, 1)) % 7
            first_nov = 1 + (7 - dow(11, 1)) % 7
            md = d.month * 100 + d.day
            uk = 300 + last_mar <= md < 1000 + last_oct
            us = 300 + second_mar <= md < 1100 + first_nov
            formula = 120 + 60 * us - 60 * uk
            actual = datetime(d.year, d.month, d.day, 8, tzinfo=london).astimezone(chicago)
            minute = actual.hour * 60 + actual.minute
            checked += 1
            clocks[str(formula)] = clocks.get(str(formula), 0) + 1
            if formula != minute:
                mismatches.append(dict(date=str(d), formula=formula, iana=minute))
        d += timedelta(days=1)
    assert not mismatches, mismatches
    # Locate syntax, without treating source comments as executable statements.
    executable = re.sub(r'\{.*?\}', '', v2, flags=re.S)
    flags = dict(iog_off=bool(re.search(r'IntrabarOrderGeneration\s*=\s*false', executable, re.I)),
                 builtin_stop_present=bool(re.search(r'\bSetStopLoss\b', executable, re.I)),
                 this_bar_on_close_count=len(re.findall(r'this\s+bar\s+on\s+close', executable, re.I)),
                 next_bar_stop_count=len(re.findall(r'next\s+bar\s+at\s+StopPx\s+stop', executable, re.I)),
                 v1_default_last_date=int(re.search(r'LastTradeDate\(\s*(\d+)\s*\)', v1).group(1)),
                 v2_date_gate_present='LastTradeDate' in executable or 'FirstTradeDate' in executable)
    assert flags['iog_off'] and not flags['builtin_stop_present']
    assert flags['this_bar_on_close_count'] == 4 and flags['next_bar_stop_count'] == 2
    n = totals['2018_22']['v2_trades']
    summary = dict(operation='static source/document and independent clock audit only', new_strategy_return_trials=0,
                   published_annual_claims_summed=totals,
                   power_arithmetic_only=dict(v2_claimed_design_n=n, mean_for_t2_as_multiple_of_unknown_SD=2/math.sqrt(n),
                                              note='iid upper-bound count; no SD, actual power or new return test computed'),
                   source_flags=flags,
                   london_open_clock_check=dict(start='2017-01-01', end=str(end), weekdays_checked=checked,
                                                formula_minutes_after_midnight_counts=clocks, mismatches=mismatches),
                   cost_arithmetic_only=dict(author_NQ_round_trip=15, author_scaled_MNQ_round_trip=1.5,
                                             verified_actual_MNQ_cost=False),
                   existing_Claude_research_snapshot='3d74b9a',
                   read_in_progress_Claude_strategy_returns=False)
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (OUT / 'v1_v2_normalized.diff').write_text(''.join(unified_diff(v1.splitlines(True), v2.splitlines(True),
                                                                fromfile='source_v1.txt', tofile='source_v2.txt')))
    manifest = dict(input_sha256={str(p.relative_to(ROOT)): sha(p) for p in sorted(INPUT.iterdir())},
                    code_sha256={str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
                    notes='Published performance claims are transcribed/summed, not independently reproduced.')
    (OUT / 'reproduction.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
