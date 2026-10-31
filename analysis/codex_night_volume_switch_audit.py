"""Independent saved-output arithmetic and version/provenance audit; no replay."""
from pathlib import Path
import hashlib
import io
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'agents/codex/runtime/or_pullback_python'),str(ROOT/'analysis')]
import numpy as np
import pandas as pd

OUT=ROOT/'analysis/outputs/codex_night_volume_switch'
PIN='febc65f1573040abf9a697d1d3468e1bce48c4c0'
MODES=('literal_delay','immediate_stop')


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
    return h.hexdigest()


def period_mask(dates,period):
    dates=pd.DatetimeIndex(dates)
    if period=='2018_22':return (dates.year>=2018)&(dates.year<2023)
    if period=='2023_plus':return dates.year>=2023
    if period=='2018_plus':return dates.year>=2018
    return dates.year==int(period)


def audit():
    checks=0
    diagnostics=pd.read_csv(OUT/'diagnostics/standard_stats.csv')
    replays={}
    dates=None
    for mode in MODES:
        t=pd.read_csv(OUT/'replay'/f'{mode}_trades.csv',parse_dates=['date'])
        a=pd.read_csv(OUT/'replay'/f'{mode}_audit.csv',parse_dates=['date'])
        valid=set(a.loc[a.account_eligible,'date'])
        dates=valid if dates is None else dates.intersection(valid)
        replays[mode]=t
    for row in diagnostics.itertuples():
        t=replays[row.timing]
        t=t[t.date.isin(dates)&period_mask(t.date,row.period)]
        if row.group=='long':t=t[t.side>0]
        elif row.group=='short':t=t[t.side<0]
        elif row.group.startswith('leg_'):t=t[t.leg==row.group[4:]]
        x=(t.exit-t.entry)*t.side*20-row.fee_micro*10-10
        expected=dict(trades=len(x),total_nq=x.sum(),total_mnq=x.sum()/10,
                      avg=x.mean(),avg_mnq=x.mean()/10,win=(x>0).mean(),
                      t=x.mean()/x.std(ddof=1)*np.sqrt(len(x)))
        for key,value in expected.items():
            np.testing.assert_allclose(getattr(row,key),value,rtol=0,atol=1e-8,equal_nan=True)
            checks+=1
    funded=pd.read_csv(OUT/'accounts/funded_summary.csv')
    for row in funded.itertuples():
        z=np.load(OUT/'accounts'/f'funded_results_{row.fee:.2f}_{row.cohort}.npz')
        a,b=z[row.config+'__250'],z[row.config+'__500']
        assert a.shape==b.shape==(1000,5)
        expected=dict(year1=a[:,0].mean(),year1_p5=np.percentile(a[:,0],5),year1_p95=np.percentile(a[:,0],95),
                      year2=b[:,0].mean(),year2_p5=np.percentile(b[:,0],5),year2_p95=np.percentile(b[:,0],95),
                      blown=b[:,3].mean(),all6=(b[:,1]==6).mean(),
                      days6=np.median(np.where(b[:,1]==6,b[:,2],np.inf)))
        for key,value in expected.items():
            np.testing.assert_allclose(getattr(row,key),value,rtol=0,atol=1e-10)
            checks+=1
    parity=[]
    for fee in (1.04,1.24):
        pp=json.loads((OUT/'accounts'/f'funded_parity_{fee:.2f}.json').read_text())
        assert all(p['exact'] and p['original']==p['lookup'] for p in pp)
        parity+=pp
    assert len(parity)==160
    evaluation=pd.read_csv(OUT/'accounts/evaluation_summary.csv')
    for fee in (1.04,1.24):
        e=pd.read_csv(OUT/'accounts'/f'evaluation_starts_{fee:.2f}.csv',parse_dates=['date'])
        for row in evaluation[evaluation.fee==fee].itertuples():
            ok=e.common_complete_21day_start & period_mask(e.date,row.cohort)
            o=e[row.config+'__outcome'][ok]
            assert len(o)==row.starts
            for key,value in (('passed',(o=='pass').mean()),('failed',(o=='fail').mean()),('timed_out',(o=='time').mean())):
                np.testing.assert_allclose(getattr(row,key),value,rtol=0,atol=1e-12)
                checks+=1
    # Compare actual date/leg/side templates with the old published family.
    # Its old row indices and exit-price geometry are intentionally not reused.
    prior=subprocess.check_output(['git','show',PIN+':checks/candidates/t_oneside/python_trades_stop.csv'])
    old=pd.read_csv(io.BytesIO(prior),parse_dates=['date'])
    new=replays['literal_delay']
    old['cell']=old.cell.astype(str)
    joined=new[['date','cell','side','entry','exit']].merge(old[['date','cell','side','entry','exit']],
             on=['date','cell'],how='outer',suffixes=('_new','_prior'),indicator=True)
    joined.to_csv(OUT/'source_version_trade_comparison.csv',index=False)
    versions=dict(prior_context=PIN,prior_family_trades=len(old),new_raw_source_trades=len(new),
                  date_leg_both=int((joined._merge=='both').sum()),
                  new_only=int((joined._merge=='left_only').sum()),prior_only=int((joined._merge=='right_only').sum()),
                  same_side_when_both=int(((joined._merge=='both')&(joined.side_new==joined.side_prior)).sum()),
                  comparison_is_author_parity=False)
    excluded=new.loc[~new.date.isin(dates),['date','cell','side','entry','exit','gross_points']].copy()
    excluded['net_mnq_at_1_04']=excluded.gross_points*2-2.04
    excluded.to_csv(OUT/'excluded_raw_trade_audit.csv',index=False)
    np.testing.assert_array_equal(replays['literal_delay'][['day','entry_j','exit_j','side','entry','exit']].to_numpy(),
                                  replays['immediate_stop'][['day','entry_j','exit_j','side','entry','exit']].to_numpy())
    versions['two_modes_actual_trades_identical']=True
    (OUT/'source_version_summary.json').write_text(json.dumps(versions,indent=2)+'\n')
    result=dict(independent_arithmetic_checks=checks,diagnostic_rows=len(diagnostics),
                funded_rows=len(funded),evaluation_rows=len(evaluation),simulator_parity_checks=len(parity),
                exact_simulator_checks=True,source_version=versions,
                status='PASS WITH CONCERNS',concerns=['8 incomplete morning sessions, including March2020 stress dates',
                'no exact author MultiCharts execution parity','accepted delayed-stop and tick-rounding model assumptions',
                'inherited current-plan path approximations and small saved-baseline difference'])
    (OUT/'independent_output_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    manifest=dict(preregistration_commit='affb482',context_pin=PIN,
                  scripts={p.name:sha(p) for p in (ROOT/'analysis').glob('codex_night_volume_switch*.py')},
                  reused_helpers={p.name:sha(p) for p in [ROOT/'analysis'/n for n in
                  ('codex_ob_v2_accounts.py','codex_or_pullback_plan.py','codex_or_pullback_portfolio.py','codex_or_pullback_exposure.py')]},
                  source_sha256=sha(ROOT/'agents/codex/inputs/night_volume_switch/source.txt'),
                  price_cache_sha256=sha(ROOT/'scratch_data/g24.pkl'),
                  prepared_baseline_sha256=sha(ROOT/'agents/codex/runtime/or_pullback_current_lab.pkl'),
                  python=sys.version)
    (OUT/'final_reproduction.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':audit()
