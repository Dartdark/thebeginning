"""Disconnected source/accounting checks; never load real returns or operate live systems."""
from pathlib import Path
from types import SimpleNamespace
import ast
import hashlib
import json
import subprocess
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'agents/codex/inputs/weekly_cross_review_20261106'
SRC=BASE/'source'


def function(path,names,env):
    tree=ast.parse((SRC/path).read_text())
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes}==set(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),env)
    return env


def main():
    manifest=json.loads((BASE/'source_manifest.json').read_text())
    for row in manifest:
        if row['retained']:
            assert hashlib.sha256((SRC/row['path']).read_bytes()).hexdigest()==row['sha256']
    env={'np':np,'START':50000.,'TARGET':3000.,'MLL':2000.,'DLL':1000.,'LOCK':100.,'MAXD':21}
    c=function('analysis/combine_levers_test.py',{'challenge'},env)['challenge']
    e=function('analysis/plan_150k_test.py',{'evaluation'},{'np':np})['evaluation']
    r150=dict(st=150000.,dd=4000.,dll=2000.,lock=150100.,tgt=9000.)
    tie50=c(np.array([[-1000.],[-1000.]]),np.array([[-1000.],[4000.]]),np.arange(2),lambda *a:1.)
    tie150=e(np.array([[-2000.],[-2000.]]),np.array([[-2000.],[11000.]]),0,2,r150)
    assert tie50==('pass',2) and tie150==('fail',2)
    # Explicit invented cash tapes: a pre-target EOD high followed by daily losses and recovery.
    w50=np.array([[0.,2500.],[-2100.,-2100.],[-1100.,-1100.],[0.,3000.]])
    r50=np.array([[0.,2500.],[-2100.,-2100.],[-1100.,-1100.],[0.,3000.]])
    capped50=c(w50,r50,np.arange(4),lambda *a:1.)
    assert capped50==('pass',4)
    # Correct uncapped pre-target floor after day1:52500-2000=50500.
    # Day2 model DLL cash51500; day3 observed adverse50400 touches that floor before recovery.
    assert 51500.-1100. < 50500.
    w150=np.array([[0.,7000.],[-3000.,-3000.],[-2500.,-2500.],[0.,7000.]])
    capped150=e(w150,w150.copy(),0,4,r150)
    assert capped150==('pass',4)
    assert 155000.-2500. < 153000.

    jof=lambda hhmm:(hhmm//100)*60+hhmm%100
    common={'np':np,'pd':pd,'J0':jof(831),'J1':jof(1500),'JE':jof(1459),'TICK':.25}
    green=function('analysis/long_after_green_test.py',{'one','run'},dict(common))
    shape=(202,1440)
    g=SimpleNamespace(trading=np.arange(202),ts=pd.date_range('2018-01-01',periods=202),
                      o=np.full(shape,100.),h=np.full(shape,100.),l=np.full(shape,100.),c=np.full(shape,100.))
    nq=green['run'](g,20.,7.25,[0]);es=green['run'](g,50.,5.,[0])
    assert nq.iloc[0]['net']==-24.5 and es.iloc[0]['net']==-35.
    bert=function('analysis/daily_reversal_bertola_test.py',{'trades'},dict(common))['trades']
    bnq=bert(g,20.,7.25,.25,'A','always_long');bes=bert(g,50.,5.,.25,'A','always_long')
    assert bnq.iloc[0]['net']==-24.5 and bes.iloc[0]['net']==-35.

    # Delete essentially the entire invented held path while preserving the two endpoint marks.
    hole=SimpleNamespace(trading=np.arange(2),ts=pd.date_range('2018-01-01',periods=2),
                         o=np.full((2,1440),np.nan),h=np.full((2,1440),np.nan),
                         l=np.full((2,1440),np.nan),c=np.full((2,1440),np.nan))
    hole.c[0,jof(1500)]=100.;hole.c[1,jof(1500)]=101.
    hole.o[0,jof(831)]=99.;hole.o[1,jof(831)]=100.
    accepted_hole=green['run'](hole,20.,7.25,[0])
    assert len(accepted_hole)==1 and np.isfinite(accepted_hole.iloc[0]['net'])

    kill=[]
    for path in ['apex_strategies/NQ_Vault_Break.txt','apex_strategies/NQ_Vault_Break_SP.txt',
                 'apex_strategies/NQ_Overnight_Bias.txt','apex_strategies/NQ_Overnight_Bias_ADX30.txt',
                 'apex_strategies/Bridge_Monday_Long_L644NQ.txt','funded_strategies/NQ_Expiration_Open_Short.txt']:
        t=(SRC/path).read_text()
        assert 'KillErr = GetLastError' in t and 'KillErr <> 2 and KillErr <> 3' in t
        kill.append(path)
    parse=[]
    for path in sorted(SRC.rglob('*.py')):
        try:ast.parse(path.read_text());parse.append(str(path.relative_to(SRC)))
        except SyntaxError as exc:raise AssertionError((path,str(exc))) from exc
    head='d441df2f7921d4dc8e971d9ed4be9f08c585dbc0'
    histories={}
    for path in ['analysis/daily_reversal_bertola_test.py','analysis/long_after_green_test.py','analysis/long_after_green_filters.py']:
        histories[path]=subprocess.check_output(['git','log','--format=%H %s',head,'--',path],cwd=ROOT,text=True).splitlines()
    results=dict(scope='Invented accounting/cost/data-gap tapes, static source and commit history only',
        market_return_tests=0,economic_definitions=0,live_or_external_actions=False,
        source_head=head,
        account_tie_case={'50K':tie50,'150K':tie150,'note':'Same-minute ordering is ambiguous; sources resolve it differently. No observed path probability inferred.'},
        pretarget_floor_cases={'50K_legacy':capped50,'50K_correct_floor_after_day1':50500.,'50K_day3_adverse_equity':50400.,
                              '150K_legacy':capped150,'150K_correct_floor_after_day1':153000.,'150K_day3_adverse_equity':152500.,
                              'note':'Illustrates premature PA-like floor caps. Not a historical rerun; DLL fills also remain model assumptions.'},
        neutral_price_cost_cases={'green_NQ_net':float(nq.iloc[0]['net']),'bertola_NQ_net':float(bnq.iloc[0]['net']),
                                  'NQ_documented_RT_plus_ticks':-17.25,'green_ES_net':float(es.iloc[0]['net']),
                                  'bertola_ES_net':float(bes.iloc[0]['net']),'ES_documented_RT_plus_ticks':-30.,
                                  'cause':'Both helpers subtract2*comm although callers/documentation pass round-trip commission.'},
        missing_held_path_case={'rows_emitted':len(accepted_hole),'finite_net':float(accepted_hole.iloc[0]['net']),
                                'note':'Unknown held path is silently skipped, not rejected or represented as unknown.'},
        tri_state_sources_present=kill,tri_state_scope='Source classification supplied; no Windows/MC native acceptance claimed.',
        python_sources_ast_parsed=len(parse),new_source_commit_histories=histories,
        source_history_scope='First committed code/results association does not authenticate earlier uncommitted bytes or the full private execution chronology.')
    print(json.dumps(results,indent=2))


if __name__=='__main__':
    main()
