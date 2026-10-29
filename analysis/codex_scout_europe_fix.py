"""Frozen first-stage 2018-22 6E pre-European-fix gross/cost screen.

No 2023+ reader, fitting, stop optimization or account simulation. A PASS
requires separately committed executable design/control code before more returns.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import metrics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_scout_europe_fix'
PROPOSAL = ROOT / 'agents/codex/research/scout/proposals/europe_fix.json'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def clock(day, hour):
    t = (pd.Timestamp(day) + pd.Timedelta(hours=hour)).tz_localize('Europe/Berlin')
    return t.tz_convert('America/Chicago')

def inputs():
    return [ROOT / f'data/6E_1min_{y}.csv' for y in range(2018, 2023)]

def census():
    # Price fields deliberately excluded: admission/data census reveals no returns.
    frames = [pd.read_csv(p, usecols=['date', 'time']) for p in inputs()]
    index = set(map(tuple, pd.concat(frames).to_numpy()))
    rows = []
    for d in pd.bdate_range('2018-01-01', '2022-12-31'):
        entry, exit_ = clock(d, 8), clock(d, 14)
        assert entry.date() == exit_.date() == d.date()
        # MultiCharts stamps one-minute bars at close: open of08:01 is08:00.
        et = (entry.hour * 60 + entry.minute + 1)
        xt = exit_.hour * 60 + exit_.minute
        date = int(d.strftime('%Y%m%d'))
        ehhmm, xhhmm = et // 60 * 100 + et % 60, xt // 60 * 100 + xt % 60
        rows.append(dict(date=date, entry_time=ehhmm, exit_time=xhhmm,
                         complete=(date, ehhmm) in index and (date, xhhmm) in index,
                         held_minutes=xt-et+1))
    return pd.DataFrame(rows)

def summarize(t):
    x=t.net.to_numpy()
    p=metrics.perf(pd.Series(x, index=pd.to_datetime(t.date.astype(str))),x)
    p.update(gross_total=float(t.gross.sum()), commission_total=float(t.commission.sum()),
             slippage_total=float(t.slippage.sum()), net_total=float(t.net.sum()),
             gross_avg=float(t.gross.mean()), t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))),
             gross_t=float(t.gross.mean()/t.gross.std()*np.sqrt(len(x))))
    return p

def run(envelope, claim):
    # Recheck the admission command in the process that opens economic outcomes.
    command=[str(Path(__import__('sys').executable)),str(ROOT/'agents/codex/terminal/scout_gates.py'),
             'check',str(envelope),'--confirmed-claim',claim]
    receipt=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=True)
    proposal=json.loads(PROPOSAL.read_text())
    for item in proposal['inputs']:
        assert digest(ROOT/item['path']) == item['sha256']
    c=census()
    assert len(c)==1305 and c.complete.mean() >= .95, 'Frozen data gate failed'
    records=[]
    for path in inputs():
        d=pd.read_csv(path).set_index(['date','time'],verify_integrity=True)
        for row in c[c.date//10000 == int(path.stem[-4:])].itertuples(index=False):
            if not row.complete: continue
            a=d.loc[(row.date,row.entry_time),'open']
            b=d.loc[(row.date,row.exit_time),'close']
            if not np.isfinite(a+b) or min(a,b)<=0: raise ValueError('Invalid endpoint')
            records.append(dict(date=row.date,side=-1,entry_time=row.entry_time,exit_time=row.exit_time,
                                entry_reference=a,exit_reference=b,gross=(a-b)*125000,
                                commission=7.25,slippage=12.50,net=(a-b)*125000-19.75))
    t=pd.DataFrame(records);s=summarize(t)
    # One reserved economic definition. No random/time/control return views here.
    passed=s['gross_avg']>19.75 and s['t']>=2 and len(t)>=1000
    result=dict(status='gross_pass_requires_next_stage' if passed else 'design_reject',
                definition_id='europe_fix_gross_6e_1',period='2018-2022',size='one standard6E reference',
                metrics=s,yearly={str(y):summarize(z) for y,z in t.groupby(t.date//10000)},
                long_trades=0,short_trades=len(t),eligible_weekdays=len(c),resolved=len(t),
                unresolved=int((~c.complete).sum()),unknown_returns_imputed=False,
                missing_dates=c.loc[~c.complete,'date'].tolist(),
                account_results=None,historical_2023_plus_opened=False,
                limitations=['Reference-price gross/cost screen; no protective stop or account sizing tested',
                             'Continuous front-contract exports lack native contract identity; contract/roll audit required before positive admission',
                             'Unknown endpoints excluded explicitly, never zero-filled; not a complete executable equity curve',
                             'No M6E fee/fill evidence; no inference from standard6E to micro account returns'])
    OUT.mkdir(parents=True,exist_ok=True)
    t.to_csv(OUT/'design_reference_ledger.csv',index=False)
    c.to_csv(OUT/'endpoint_census.csv',index=False)
    (OUT/'admission.txt').write_text(receipt.stdout)
    (OUT/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    manifest=dict(claim=claim,envelope=json.loads(Path(envelope).read_text()),code_sha256=digest(__file__),
                  python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,
                  inputs=proposal['inputs'],seed=None,return_definitions_executed=1,
                  results_sha256=digest(OUT/'result.json'))
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--census',action='store_true')
    ap.add_argument('--envelope');ap.add_argument('--confirmed-claim');a=ap.parse_args()
    if a.census:
        c=census();print(c.groupby(c.date//10000).complete.agg(['size','sum']).to_json())
        print('coverage',c.complete.mean(),'missing',int((~c.complete).sum()))
    else:
        if not a.envelope or not a.confirmed_claim: ap.error('Committed admission envelope and claim required')
        run(a.envelope,a.confirmed_claim)
