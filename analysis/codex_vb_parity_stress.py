"""Complete the frozen VB robustness audit after a registered fill-parity check.

Only .25-point MC parity is new. Original code, gate, stresses/seeds and
1-point research baseline remain unchanged. No shared-cache or live writes.
"""
from pathlib import Path
import argparse
import json
import pickle
import subprocess
import time
import warnings

import numpy as np
import pandas as pd
from importlib.metadata import version

import codex_break_vb_onb as B

ROOT=B.ROOT
OLD=ROOT/'analysis/outputs/codex_break_vb_onb'
OUT=ROOT/'analysis/outputs/codex_vb_parity_stress'
PLAN='agents/codex/plans/vb_parity_trade_through_amendment.md'
REVIEW='agents/codex/inputs/break_vb_onb/REVIEW_break_vb_onb_and_rest.md'
REVIEW_COMMIT='d82cbd39928e9d1cb63a883e66e3de019cb76dfe'


def dump(name,x):
    (OUT/name).write_text(json.dumps(x,indent=2,default=lambda v:v.item())+'\n')


def setup():
    OUT.mkdir(parents=True,exist_ok=True)
    committed=subprocess.check_output(['git','show','HEAD:'+PLAN],cwd=ROOT)
    assert committed==(ROOT/PLAN).read_bytes(),'Amendment must be committed before replay'
    amendment=subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip()
    original=json.loads((OLD/'reproduction.json').read_text())
    checks={p:B.sha(ROOT/p)==h for p,h in original['code_sha256'].items()}
    assert all(checks.values()),'Original dependency or preregistration changed'
    warnings.filterwarnings('ignore',message='All-NaN slice encountered')
    warnings.filterwarnings('ignore',message='invalid value encountered in divide')
    g=B.ControlledGrid(pickle.load((ROOT/'scratch_data/g24.pkl').open('rb')))
    manifest=B.verify_cache(g)
    prior=json.loads((OLD/'input_manifest.json').read_text())
    assert manifest['cache_sha256']==prior['cache_sha256']
    assert manifest['files']==prior['files'],'Inputs differ from the frozen audit'
    manifest.update(amendment_commit=amendment,original_plan_commit='109a752',
       review_source_commit=REVIEW_COMMIT,review_sha256=B.sha(ROOT/REVIEW),
       original_dependency_hash_checks=checks,runner_sha256=B.sha(__file__))
    B.OUT=OUT  # Local report output routing only; no engine parameter/global mutation.
    return g,manifest


def fill_fixtures():
    o=np.full((2,1440),100.);h=o+.5;l=o-.5;c=o.copy()
    sig=np.array([[1,600,75,40,870,870]],float)
    h[1,601]=140.
    touch=B.vb_engine(o,h,l,c,sig,3,.25,0)
    assert touch[0,6]!=1
    h[1,601]=140.25
    tick=B.vb_engine(o,h,l,c,sig,3,.25,0)
    point=B.vb_engine(o,h,l,c,sig,3,1.,0)
    assert tick[0,2]==601 and tick[0,6]==1 and point[0,6]!=1
    h[1,631]=141.
    more=np.vstack([sig,np.array([[1,630,75,40,870,870],[1,660,75,40,870,870]],float)])
    a=B.vb_engine(o,h,l,c,more,3,.25,0);b=B.vb_engine(o,h,l,c,more,3,1.,0)
    assert len(a)==3 and len(b)==2
    return dict(touch_does_not_fill=True,one_tick_fills_only_parity_convention=True,
                later_reentry_is_recomputed=True)


def unmatched(g,t,name):
    """Retain factual causes of missing emulated entries; MC timing uncertainty explicit."""
    p=pd.read_csv(OUT/f'{name}_pairing.csv',parse_dates=['date','entry_bar'])
    signals,_=B.vault_break24(g)
    rows=[]
    for r in p[p._merge.ne('both')].itertuples(index=False,name=None):
        z=dict(zip(p.columns,r));source='python_only' if z['_merge']=='left_only' else 'MC_only'
        date=pd.Timestamp(z['date']);bar=pd.Timestamp(z['entry_bar'])
        d=int(np.searchsorted(g.dates,int(date.strftime('%Y%m%d'))))
        dj=bar.hour*60+bar.minute-30
        ss=signals[(signals.day==d)&(signals.dj==dj)]
        occupied=t[(t.day==d)&(t.j0<=dj)&(t.j1>dj)]
        same=t[t.day==d]
        cause='unresolved_MC_entry_difference'
        certainty='unresolved'
        if source=='MC_only':
            if ss.empty:
                cause='no_qualifying_Python_signal_at_MC_decision';certainty='verified_emulator_fact'
            elif len(occupied):
                cause='Python_position_still_open_at_MC_decision';certainty='verified_emulator_fact'
            elif len(same[same.j1<=dj])>=3:
                cause='Python_three_trade_cap_already_reached';certainty='verified_emulator_fact'
        else:
            cause='Python_entry_absent_from_MC';certainty='unresolved_MC_cause'
        rows.append(dict(source=source,date=str(date.date()),entry_bar=str(bar),decision_column=dj,
           cause=cause,certainty=certainty,qualifying_Python_signal=not ss.empty,
           preceding_Python_position_entry=int(occupied.j0.iloc[0]) if len(occupied) else None,
           preceding_Python_position_exit=int(occupied.j1.iloc[0]) if len(occupied) else None,
           other_Python_entry_columns=','.join(same.j0.astype(str)),
           entry_price=z.get('entry_py') if source=='python_only' else z.get('entry_mc'),
           net=z.get('net_py') if source=='python_only' else z.get('net_mc')))
    pd.DataFrame(rows,columns=['source','date','entry_bar','decision_column','cause','certainty',
        'qualifying_Python_signal','preceding_Python_position_entry','preceding_Python_position_exit',
        'other_Python_entry_columns','entry_price','net']).to_csv(OUT/f'{name}_unmatched_causes.csv',index=False)


def parity_phase(g,manifest):
    checks=B.engineering_checks();checks.update(fill_fixtures())
    base=B.run_strategy(g,'VB',through=1.)
    official=B.original(g,'VB')
    prior=pd.read_csv(OLD/'VB_baseline_trades.csv')
    cols=['day','j0','j1','side','entry','exit','kind','pnl','net']
    assert len(base)==len(official)==len(prior)
    assert np.allclose(base[cols],official[cols],rtol=0,atol=1e-7,equal_nan=True)
    assert np.allclose(base[cols],prior[cols],rtol=0,atol=1e-7,equal_nan=True)
    checks['one_point_accelerator_and_original_ledger_equivalence']=True
    quarter=B.run_strategy(g,'VB',through=.25)
    stats={};table=[]
    for name,t,through,family in [('research_1point',base,1.,'baseline'),
                                  ('parity_quarterpoint',quarter,.25,'parity_reference')]:
        t.to_csv(OUT/f'{name}_trades.csv',index=False)
        stats[name]=B.parity(g,'VB',t)
        stats[name]['target_trade_through_points']=through
        (OUT/'VB_baseline_pairing.csv').rename(OUT/f'{name}_pairing.csv')
        unmatched(g,t,name)
        table.extend(B.metrics(t,g,'VB',name,family,dict(**B.VB,target_trade_through=through)))
    dump('baseline_parity.json',stats)
    pd.DataFrame(table).to_csv(OUT/'baseline_metrics.csv',index=False)
    B.vb_target_diagnostic(g)
    dump('engineering_checks.json',checks)
    dump('input_manifest.json',manifest)
    dump('phase_status.json',dict(parity_only_pass=stats['parity_quarterpoint']['pass'],
       stress_allowed=stats['parity_quarterpoint']['pass'],stress_runs=0,
       mechanical_runs_this_phase=2,runner_sha256=B.sha(__file__)))
    print(json.dumps(stats,indent=2),flush=True)
    if not stats['parity_quarterpoint']['pass']:
        print('Quarter-point parity FAIL; stopped before stresses; unmatched causes saved.',flush=True)


def stress_phase(g,manifest):
    phase=json.loads((OUT/'phase_status.json').read_text())
    assert phase['parity_only_pass'] and phase['stress_allowed'],'Original parity gate has not passed'
    assert phase['runner_sha256']==B.sha(__file__),'Runner changed after parity; stop for review'
    prior=json.loads((OUT/'input_manifest.json').read_text())
    assert prior['cache_sha256']==manifest['cache_sha256'] and prior['files']==manifest['files']
    table=pd.read_csv(OUT/'baseline_metrics.csv')
    tables=table.to_dict('records');start=time.monotonic()
    # This baseline always uses one full point, never the parity-only .25 setting.
    base=pd.read_csv(OUT/'research_1point_trades.csv',parse_dates=['date'])
    def save(run,family,t,p):
        tables.extend(B.metrics(t,g,'VB',run,family,p))
    seeds=np.random.SeedSequence(B.SEED).spawn(4)
    noise_seeds=[int(x.generate_state(1)[0]) for x in seeds[0].spawn(100)]
    assert noise_seeds==json.loads((OLD/'run_manifest.json').read_text())['noise_seeds']
    for i,seed in enumerate(noise_seeds):
        sd=1 if i<50 else 2
        ng=B.noise(g,sd,seed)
        save(f'noise_{sd}tick_{i%50:02}','noise',B.run_strategy(ng,'VB'),dict(sd_ticks=sd,seed=seed))
        if (i+1)%20==0:print('VB noise',i+1,'/100',flush=True)
    for n,style in [(10,'sma'),(20,'sma'),(10,'wilder'),(15,'wilder'),(20,'wilder')]:
        p=B.VB.copy();p['atr_n']=n
        save(f'atr_{n}_{style}','indicators',B.run_strategy(B.ControlledGrid(g,style=style),'VB',p),dict(**p,atr_style=style))
    save('anchor_or_swap','indicators',B.run_strategy(B.ControlledGrid(g,anchor=830),'VB'),dict(vwap_anchor=830))
    save('entry_one_bar_later','timing',B.run_strategy(g,'VB',delay=30),dict(delay_minutes=30))
    for sign in [-1,1]:
        p=B.VB.copy()
        for k in ['flat','early_flat']:p[k]=B.hhmm(B.minute(p[k])+sign*30)
        save('flat_earlier' if sign==-1 else 'flat_later','timing',B.run_strategy(g,'VB',p),p)
    rng=np.random.default_rng(seeds[1]);draws=[];valid=0;candidate=0
    while valid<200:
        p,raw,reason=B.jitter('VB',rng)
        draws.append(dict(candidate=candidate,accepted=not reason,reason=reason,
                          parameters=json.dumps(p),factors=json.dumps(raw)))
        candidate+=1
        if reason:continue
        save(f'jitter_{valid:03}','jitter',B.run_strategy(g,'VB',p),p);valid+=1
        if valid%50==0:print('VB jitter',valid,'/200',flush=True)
    pd.DataFrame(draws).to_csv(OUT/'VB_jitter_draws.csv',index=False)
    for slips,through in [(2,1),(3,1),(1,2),(2,2),(3,2)]:
        save(f'execution_slip{slips}_through{through}','execution',
             B.run_strategy(g,'VB',slips=slips,through=through),dict(slippage_ticks=slips,target_trade_through=through))
    table=pd.DataFrame(tables)
    table.to_csv(OUT/'run_metrics.csv',index=False)
    # Exclude the .25-point reference from all stress-denominator calculations.
    research=table[table.family.ne('parity_reference')]
    summary=B.summarize(research);summary.to_csv(OUT/'family_summary.csv',index=False)
    days=pd.DatetimeIndex(g.ts[g.trading]);days=days[days.year>=2023]
    z=base[base.date.dt.year>=2023]
    daily=z.groupby('date').net.sum().reindex(days,fill_value=0.)
    boot=B.R.bootstrap(daily,n=2000,block=10,seed=B.SEED).reset_index(names='metric');boot['side']='all/long'
    boot.to_csv(OUT/'VB_research_baseline_bootstrap.csv',index=False)
    pd.DataFrame([dict(side='all/long',**B.R.permutation(daily,n=2000,seed=B.SEED))]).to_csv(OUT/'VB_research_baseline_permutation.csv',index=False)
    runs=table[['run','family']].drop_duplicates()
    assert len(runs)==316 and len(runs[runs.family.isin(['noise','indicators','timing','jitter','execution'])])==314
    phase.update(stress_runs=314,mechanical_scenarios_in_new_output=316,
       original_VB_robustness_trial_completed=True,runner_sha256=B.sha(__file__),
       elapsed_stress_seconds=time.monotonic()-start,noise_seeds=noise_seeds,master_seed=B.SEED,
       parity_only_points=.25,stress_default_through_points=1.,execution_stress_through_points=[1.,2.])
    dump('phase_status.json',phase)
    print(summary.to_string(index=False),flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--parity',action='store_true');p.add_argument('--stress',action='store_true')
    args=p.parse_args();assert args.parity!=args.stress
    g,manifest=setup()
    if args.parity:parity_phase(g,manifest)
    else:stress_phase(g,manifest)
    paths=list(json.loads((OLD/'reproduction.json').read_text())['code_sha256'])
    paths+=['analysis/codex_vb_parity_stress.py',PLAN,REVIEW]
    dump('reproduction.json',dict(original_plan_commit='109a752',amendment_commit=manifest['amendment_commit'],
       review_source_commit=REVIEW_COMMIT,versions={p:version(p) for p in ['numpy','pandas','numba','openpyxl','scipy','scikit-learn']},
       code_sha256={p:B.sha(ROOT/p) for p in paths},phase='parity' if args.parity else 'stress',
       original_reports_and_outputs_unchanged=True,trading_plan_changes=False,live_changes=False))


if __name__=='__main__':main()
