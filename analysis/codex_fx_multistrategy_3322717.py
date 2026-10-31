"""Audit source tables and owned-data availability; no return calculation.

python3 analysis/codex_fx_multistrategy_3322717.py
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / 'agents/codex/inputs/fx_multistrategy_3322717/source.pdf'
OUT = ROOT / 'analysis/outputs/codex_fx_multistrategy_3322717'
OUT.mkdir(parents=True, exist_ok=True)
text = subprocess.check_output(['pdftotext', '-layout', str(PDF), '-'], text=True)
pages = text.split('\f')
tables = []
for page, table in ((9, 3), (10, 4), (13, 6)):
    for line in pages[page-1].splitlines():
        match = re.match(r'^\s*([A-Za-z].*?)\s{2,}(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*$', line)
        if match:
            tables.append(dict(table=table, page=page, method=match[1],
                author_annual_return_pct=float(match[2]), author_annual_sharpe=float(match[3])))
df = pd.DataFrame(tables)
assert df.groupby('table').size().to_dict() == {3:12, 4:10, 6:10}
df.to_csv(OUT/'author_tables.csv', index=False)
inventory = []
for sym in ('6A','6B','6C','6E','6J','6M','6N','6S'):
    files = sorted((ROOT/'data').glob(f'{sym}_1min_*.csv'))
    row = dict(symbol=sym, files=len(files), first_date=None, last_date=None,
               dated_contract_roll_ledger_verified=False)
    if files:
        dates = pd.concat([pd.read_csv(f, usecols=['date']) for f in files]).date
        row.update(first_date=int(dates.min()), last_date=int(dates.max()))
    inventory.append(row)
pd.DataFrame(inventory).to_csv(OUT/'owned_fx_inventory.csv', index=False)
best = df[df.table==3].author_annual_sharpe.max()
facts = dict(source_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),
    extracted_table_rows=len(df), author_best_single_sharpe=best,
    author_best_shared_weight_sharpe=df[df.table==4].author_annual_sharpe.max(),
    author_best_product_indicator_sharpe=df[df.table==6].author_annual_sharpe.max(),
    arithmetic_relative_sharpe_gain=df[df.table==6].author_annual_sharpe.max()/best-1,
    return_trials=0, author_results_independently_reproduced=False,
    verdict='NEEDS DATA / SOURCE CLARIFICATION; no Apex fit as written',
    inspected_proxy_headers={f:pd.read_csv(ROOT/'data'/f, nrows=0).columns.tolist()
                             for f in ('macro_proxies_daily.csv','ndx_gold_daily.csv')},
    blockers=['Seven source FX futures absent from owned panel',
        'No complete dated 1Y/10Y yields and linked equity/commodity panel verified',
        'Heuristic product/indicator pruning has no stated train-only calendar',
        'Allocation formulas/constraints and execution clocks insufficiently specified',
        'No explicit transaction-cost, futures cash/collateral or roll-cost reconciliation'])
(OUT/'source_audit.json').write_text(json.dumps(facts, indent=2)+'\n')
print(json.dumps(facts, indent=2))
