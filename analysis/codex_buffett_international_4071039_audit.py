"""Source arithmetic, input receipts and label/availability fixtures; zero return backtests."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path('agents/codex/inputs/ssrn4071039')
OUT=Path('analysis/outputs/codex_buffett_international_4071039')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    text=(ROOT/'source.txt').read_text()
    # Table8 is uniquely identifiable by start-year rows. No market-price return calculation.
    rows=[]
    for line in text.splitlines():
        if not re.match(r'^\s*19(?:8[5-9]|9[0-4])/12\s',line):continue
        parts=line.split()
        values=[float(x) for x in parts[1:]]
        assert len(values)==10
        rows.append(dict(start=parts[0],strategy_return=values[0],benchmark_return=values[1],
                         strategy_vol=values[2],benchmark_vol=values[3],strategy_dd=values[4],benchmark_dd=values[5],
                         strategy_sharpe=values[6],benchmark_sharpe=values[7],jk_z=values[8],jk_p=values[9]))
    assert len(rows)==10
    with (OUT/'source_table8.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
    # Synthetic availability fixtures are not a fit, an economic variant or a strategy run.
    fit=datetime(2000,12,31,tzinfo=timezone.utc)
    matured=datetime(2000,9,30,tzinfo=timezone.utc)
    unmatured=datetime(2001,3,31,tzinfo=timezone.utc)
    gdp_reference=datetime(2000,12,31,tzinfo=timezone.utc)
    gdp_release=datetime(2001,2,15,tzinfo=timezone.utc)
    assert matured<fit<unmatured and gdp_reference<=fit<gdp_release
    result=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),script_sha256=sha(__file__),
                source_sha256={str(p):sha(p) for p in ROOT.iterdir() if p.is_file()},
                source_composite=dict(annual_return_pct=10.5,benchmark_return_pct=9.5,annual_vol_pct=13.6,
                    benchmark_vol_pct=14.2,max_dd_pct=-52.1,benchmark_max_dd_pct=-56.1,sharpe=.57,benchmark_sharpe=.49,jk_p=.02),
                source_start_rows=rows,
                diagnostics=dict(arithmetic_mean_of_row_CAGRs=sum(r['strategy_return'] for r in rows)/10,
                    warning='An average of CAGRs is not a portfolio composite return; source composite construction needs a ledger.',
                    printed_1994_benchmark_dd=rows[-1]['benchmark_dd'],
                    printed_1994_strategy_dd=rows[-1]['strategy_dd']),
                source_cost_convention=dict(max_two_way_turnover_per_decade=2.,annualized_two_way_turnover=.2,
                    cost_per_traded_dollar=.01,illustrative_annual_cost_bps=.2*.01*10000),
                synthetic_clocks=dict(fit_time=fit.isoformat(),mature_label_end=matured.isoformat(),
                    rejected_label_end=unmatured.isoformat(),gdp_reference=gdp_reference.isoformat(),
                    unavailable_gdp_release=gdp_release.isoformat(),assertions='PASS; reference period is not release time; labels must mature'),
                access_receipts=json.loads((ROOT/'access_receipts.json').read_text()),
                owned_filename_census={pattern:[str(p) for p in Path('data').rglob(pattern) if p.is_file()][:25]
                    for pattern in ['*GDP*','*gdp*','*TOTMK*','*CAPE*','*country*','*market_cap*']},
                return_trials=0,verification='Source table/clock/input audit only; independent economic replication not performed')
    (OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['diagnostics','source_cost_convention','return_trials']},indent=2))

if __name__=='__main__':main()
