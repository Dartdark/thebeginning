"""Frozen FOMC-cycle246 ES regular-session gross/cost test, design2018-22.

Inventory reads times only. No learned feature, price-decline filter or2023+reader.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
import pandas as pd
import metrics
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/scout_fomc_cycle_20261030'
OUT=ROOT/'analysis/outputs/codex_scout_fomc_cycle'
SEED=2687614
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def calendar():
    anchors=np.array([r['date'] for r in json.loads((INPUT/'calendar.json').read_text())['anchors']],dtype='datetime64[D]')
    s=pd.read_csv(INPUT/'nyse_sessions.csv',index_col=0)
    full=(pd.to_datetime(s.market_close)-pd.to_datetime(s.market_open)).dt.total_seconds().eq(390*60)
    days=pd.to_datetime(s.index[full]);rows=[]
    for d in days:
        past=anchors[anchors<np.datetime64(d.date())]
        a=past[-1] if len(past) else None
        age=int(np.busday_count(a,np.datetime64(d.date()))) if a is not None else None
        event=age in list(range(9,14))+list(range(19,24))+list(range(29,34))
        rows.append(dict(date=int(d.strftime('%Y%m%d')),anchor=str(a) if a is not None else '',age=age,event=event))
    return pd.DataFrame(rows)
def inventory():
    c=calendar();pairs=set()
    for y in range(2018,2023):
        d=pd.read_csv(ROOT/f'data/ES_1min_{y}.csv',usecols=['date','time'])
        if d.duplicated(['date','time']).any():raise ValueError('Duplicate minute key')
        pairs.update(map(tuple,d.to_numpy()))
    c['complete']=[(d,831) in pairs and(d,1500)in pairs for d in c.date]
    return c
def stats(x):
    x=np.asarray(x,float);d=metrics.perf(pd.Series(x),x)
    d.update(total=float(x.sum()),t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))))
    return d
def run(envelope,claim):
    admission=subprocess.run([sys.executable,str(ROOT/'agents/codex/terminal/scout_gates.py'),'check',envelope,
                             '--confirmed-claim',claim],cwd=ROOT,capture_output=True,text=True,check=True)
    proposal=json.loads((ROOT/'agents/codex/research/scout/proposals/fomc_cycle.json').read_text())
    for i in proposal['inputs']:assert sha(ROOT/i['path'])==i['sha256']
    c=inventory();ev=c[c.event];assert len(ev)>=400 and ev.complete.all(),'Any event endpoint gap stops returns'
    # One timestamp-only preflight gap (2020-11-30) is not a candidate.
    # Require >99% control-pool coverage; retain its unknown row in coverage.csv.
    c=c[c.anchor.ne('')];assert c.complete.mean()>=.99,'Control coverage gate'
    c=c[c.complete].copy()
    prices={}
    for y in range(2018,2023):
        d=pd.read_csv(ROOT/f'data/ES_1min_{y}.csv').set_index(['date','time'])
        for date in c.loc[c.date//10000==y,'date']:
            a=d.loc[(date,831),'open'];b=d.loc[(date,1500),'close']
            assert np.isfinite(a+b) and min(a,b)>0
            prices[date]=(a,b)
    c['entry_reference']=[prices[d][0] for d in c.date];c['exit_reference']=[prices[d][1] for d in c.date]
    c['gross']=(c.exit_reference-c.entry_reference)*50
    c['commission']=5.;c['slippage']=25.;c['net']=c.gross-30.;c['stress_net']=c.gross-55.
    t=c[c.event].copy();s=stats(t.net);s.update(gross_avg=float(t.gross.mean()),gross_total=float(t.gross.sum()),
        commission_total=float(t.commission.sum()),slippage_total=float(t.slippage.sum()),gross_t=stats(t.gross)['t'])
    dates=pd.to_datetime(c.date.astype(str));c['match']=list(zip(dates.dt.year,dates.dt.month,dates.dt.dayofweek))
    groups={key:v.index.to_numpy() for key,v in c.groupby('match')}
    counts=c[c.event].groupby('match').size();rng=np.random.default_rng(SEED);null=[]
    for k in range(1000):
        ids=np.concatenate([rng.choice(groups[key],int(n),replace=False) for key,n in counts.items()])
        null.append(float(c.loc[ids,'net'].sum()))
    p=(1+sum(x>=s['total'] for x in null))/1001
    passed=s['avg']>0 and s['t']>=2 and p<=.05 and t.stress_net.mean()>0
    r=dict(status='gross_pass_requires_execution_stage' if passed else 'design_reject',period='2018-2022',
        size='1standardES reference; no micro/account inference',metrics=s,stress=stats(t.stress_net),
        calendar_null_p=float(p),null_draws=1000,seed=SEED,events=len(t),longs=len(t),shorts=0,
        yearly={str(y):stats(z.net) for y,z in t.groupby(t.date//10000)},definitions_executed=3,
        source_replication=False,reference_screen=True,unknown_returns_imputed=False,
        historical_2023_plus_opened=False,account_results=None)
    OUT.mkdir(parents=True,exist_ok=True)
    t.drop(columns='match').to_csv(OUT/'design_reference_ledger.csv',index=False)
    pd.DataFrame(dict(draw=np.arange(1000),net_total=null)).to_csv(OUT/'calendar_null.csv',index=False)
    inventory().to_csv(OUT/'coverage.csv',index=False)
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    (OUT/'admission.txt').write_text(admission.stdout)
    (OUT/'manifest.json').write_text(json.dumps(dict(claim=claim,code_sha256=sha(__file__),inputs=proposal['inputs'],
        python=sys.version,numpy=np.__version__,pandas=pd.__version__,seed=SEED),indent=2)+'\n')
    print(json.dumps(r,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inventory',action='store_true');p.add_argument('--envelope');p.add_argument('--confirmed-claim');a=p.parse_args()
    if a.inventory:
        c=inventory();print(c[c.event].groupby(c.date//10000).complete.agg(['size','sum']).to_json())
        print('non-event endpoint gaps',int((~c.complete & c.anchor.ne('')).sum()))
    elif a.envelope and a.confirmed_claim:run(a.envelope,a.confirmed_claim)
    else:p.error('Use inventory or checked committed envelope/claim')
