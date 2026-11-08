"""Source-table and input-schema audit; not historical trading/return replication."""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess

ROOT=Path('agents/codex/inputs/ssrn499103')
OUT=Path('analysis/outputs/codex_analyst_market_makers_499103')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    text=(ROOT/'source.txt').read_text()
    table=text.split('Profitability Estimates for 1999-2000')[-1].split('Total')[0]
    rows=[]
    for symbol,ret,profit in re.findall(r'^\s*([A-Z]{4})\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*$',table,re.M):
        rows.append(dict(mpid=symbol,source_marginal_return_sum_pct=float(ret),source_estimated_profit_mn=float(profit)))
    assert len(rows)==32
    total_return=sum(r['source_marginal_return_sum_pct'] for r in rows)
    total_profit=sum(r['source_estimated_profit_mn'] for r in rows)
    assert abs(total_return-75.0492)<.001 and abs(total_profit-592.0770)<.001
    with (OUT/'source_table21.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    concentration=sum(r['source_estimated_profit_mn'] for r in rows if r['mpid'] in ['RSSF','FBCO'])/592.0770
    census={pattern:[str(p) for p in Path('data').rglob(pattern) if p.is_file()][:20]
            for pattern in ['*analyst*','*recommend*','*Nastraq*','*nastraq*','*MPID*','*FirstCall*','*level2*']}
    p=Path('data/NQ_1min_2020.csv')
    with p.open() as f:header=next(csv.reader(f))
    result=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                script_sha256=sha(__file__),source_files={str(p):sha(p) for p in ROOT.iterdir() if p.is_file()},
                source_inside_counts=dict(up_1999_2000_week1=208/327,up_1999_2000_week2=181/327,
                    difference_percentage_points=100*(208-181)/327,up_2001_week1=101/179,up_2001_week2=101/179),
                source_table21=dict(displayed_non_total_rows=len(rows),sum_return_entries_pct=total_return,
                    sum_estimated_profit_mn=total_profit,source_headline_estimated_profit_mn=592.0770,
                    estimated_profit_mn_per_327_upgrades=592.0770/327,
                    marginal_return_sum_pct_per_327_upgrades=75.0492/327,
                    top_two_share_of_net_estimated_profit=concentration,
                    warning='Model-attributed event/firm estimates, not portfolio CAGR or observed native fill/account PnL'),
                owned_filename_census=census,inspected_header={str(p):header},
                return_trials=0,verification='Source arithmetic/file/schema checks only; independent market-data replication not run')
    (OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'source_inside_counts':result['source_inside_counts'],'source_table21':result['source_table21'],'return_trials':0},indent=2))

if __name__=='__main__':main()
