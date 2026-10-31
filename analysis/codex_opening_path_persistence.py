"""Result-informed standalone opening path nomination; frozen before validation returns."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_opening_path_persistence'
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_t6_study_support as S
import codex_opening_pressure as P
C=S.C;os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
PLAN='agents/codex/plans/opening_path_persistence.md'
CONFIGS={'OPP':(.50,.15),'E40':(.40,.15),'E60':(.60,.15),'M10':(.50,.10),'ALL5':(0.,0.)}


def signal_rows(feature,efficiency,move):
    rows=[];counts=feature.reason.value_counts().to_dict()
    for r in feature.to_dict('records'):
        if r['reason']!='eligible':continue
        side=r['NQ5_side']
        if not side or r['NQ5_eff']<efficiency or r['NQ5_move']<move:continue
        rows.append(dict(day=r['day'],signal_j=540,dj=540,side=side,stop=np.ceil(.15*r['atr']*4)/4,target=np.ceil(.60*r['atr']*4)/4,
            exit_j=895,delta_fraction=np.nan,input_last_j=540,first_entry_j=541))
    return pd.DataFrame(rows,columns=P.SCOLS),counts


def run(prereg,phase):
    S.bind(OUT,PLAN,prereg,CONFIGS,['NQ','ES','YM'],20,['codex_opening_pressure.py','codex_opening_path_persistence.py'])
    C.dump(OUT/'engineering_checks.json',P.engineering())
    lo=pd.Timestamp('2018-01-01' if phase=='design' else '2023-01-01');hi=pd.Timestamp('2022-12-31' if phase=='design' else '2026-10-09')
    if phase=='validation' and json.loads((OUT/'design_nomination_gate.json').read_text())['selected'] is None:raise ValueError('Design nomination veto; do not validate')
    audit={sym:S.intake(sym,hi) for sym in ('NQ','ES','YM')};C.dump(OUT/f'{phase}_intake.json',audit)
    if any(a['conflicting_keys'] for a in audit.values()):raise ValueError('NEEDS DATA: conflicting keys')
    grids={sym:S.load(sym,hi) for sym in ('NQ','ES','YM')};feature=P.features(grids,lo,hi);C.csv(OUT/f'{phase}_features.csv',feature)
    configs=CONFIGS if phase=='design' else {k:CONFIGS[k] for k in ('OPP','ALL5')}
    sigs={};counts={}
    for name,args in configs.items():sigs[name],counts[name]=signal_rows(feature,*args)
    days=S.sessions(grids['NQ'],lo,hi)
    # Reproduction check happens before the newly nominated ledger enters performance reporting.
    if phase=='design':
        source_path=ROOT/'analysis/outputs/codex_opening_pressure/design_OWN5_trades.csv';source=pd.read_csv(source_path)
        replica,_=S.F.replay(grids['NQ'],sigs['OPP'])
        cols=['day','j0','j1','side','entry','exit','kind','pnl','net','net_mnq','stress_four_ticks']
        np.testing.assert_allclose(replica[cols].to_numpy(),source[cols].to_numpy(),rtol=0,atol=1e-8)
        C.dump(OUT/'source_reproduction.json',dict(source=str(source_path.relative_to(ROOT)),source_sha256=C.sha(source_path),matched_rows=len(source),exact_economic_ledger=True,already_seen_design=True,unique_new_configurations=4,counted_evaluations=5))
    ledgers,df,selected=S.evaluate(OUT,grids['NQ'],sigs,days,phase,prereg,['OPP'],{'OPP':'ALL5'},20,counts=counts)
    if phase=='design':
        base=json.loads((OUT/'design_gate.json').read_text());fc=json.loads((OUT/'design_filter_diagnostics.json').read_text())['OPP']
        neighbors=[C.stats(ledgers[k],days) for k in ('E40','E60','M10')]
        extra={k:bool(v) for k,v in dict(basic=base['selected']=='OPP',neighbors_all_positive=all(m['total']>0 for m in neighbors),neighbors_two_t2=sum(m['t_trade']>=2 for m in neighbors)>=2,
            removed_loses=fc['removed_avg']<0,kept_total_ge_base=fc['kept_net']>=fc['base_net'],beats_random_net=fc['p_random_net_ge_kept']<=.10,beats_random_joint=fc['p_kept_better_net_and_dd']>=.90).items()}
        selected='OPP' if all(extra.values()) else None
        C.dump(OUT/'design_nomination_gate.json',dict(prereg=prereg,checks=extra,selected=selected,unique_new_models=4,counted_program_evaluations=25,unique_program_models=24,nomination='selected after prior design control results; not independent discovery',program_continues=True))
        print('Nomination:',selected,extra,flush=True)
    return ledgers,df,selected


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['design','validation'],required=True);p.add_argument('--prereg',required=True);a=p.parse_args();run(a.prereg,a.phase)
