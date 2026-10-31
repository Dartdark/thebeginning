"""Refresh only the fixed Swing personal contrasts after BB_MRM removal.

No strategy replay. The original18-leg outputs and adapter remain unchanged.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scratch_data/codex_deps'))
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_swing_accounts as S
import resampling as R

REF = 'e08c353'
SNAPSHOT = ROOT/'agents/codex/inputs/swing_target/plan_update_e08c353'
OUT = ROOT/'analysis/outputs/codex_swing_target/personal17'
PLAN = 'agents/codex/plans/swing_target_personal_refresh.md'
CHANGED = ('personal_strategies/PORTFOLIO.md','analysis/personal_portfolio.py','analysis/personal_variants.py',
           'analysis/outputs/personal_portfolio_output.txt','analysis/outputs/personal_variants_output.txt')


def starter_sets(source):
    tree = ast.parse(source.decode('utf-8-sig'))
    node = next(n for n in ast.walk(tree) if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=='sets' for t in n.targets))
    return {k.split('.')[0]:v for k,v in ast.literal_eval(node.value).items()}


def prepare_sources():
    manifest = dict(reference=S.git('rev-parse',REF).decode().strip(),previous_reference=S.REF,files={},unchanged_inputs=[])
    for rel in CHANGED:
        data = S.git('show',REF+':'+rel)
        target = SNAPSHOT/rel
        if target.exists() and target.read_bytes()!=data:
            raise ValueError('Refuse to overwrite a different update snapshot')
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists(): target.write_bytes(data)
        manifest['files'][rel] = dict(git_blob=S.git('rev-parse',REF+':'+rel).decode().strip(),sha256=S.A.file_sha(target))
    for rel in S.SOURCES:
        if rel in CHANGED or 'bb_mrm' in rel: continue
        old = S.git('rev-parse',S.REF+':'+rel).decode().strip()
        new = S.git('rev-parse',REF+':'+rel).decode().strip()
        if old!=new: raise ValueError('Unexpected changed baseline source: '+rel)
        manifest['unchanged_inputs'].append(dict(path=rel,git_blob=new))
    old = starter_sets(S.git('show',S.REF+':analysis/personal_portfolio.py'))
    new = starter_sets(S.git('show',REF+':analysis/personal_portfolio.py'))
    if old!=new or old!=S.P.STARTERS: raise ValueError('Starter sets changed')
    manifest.update(starter_sets_unchanged=True,roster_change='Drop BB_MRM only; retain all other17 legs and source fees/marks',
                    candidate_returns_replayed=False,baseline_returns_computed=False)
    S.dump(SNAPSHOT/'manifest.json',manifest)
    return manifest


def authorize(commit):
    S.require_plan(commit,PLAN)
    for model in ('CODE','CODE_BE'):
        for fee in (1.24,1.04):
            source = S.OUT.parent/'personal'/model/f'fee_{fee:.2f}'/'reproduction.json'
            if S.A.file_sha(S.__file__)!=json.loads(source.read_text())['script_sha256']:
                raise ValueError('Frozen original adapter changed')


def verify_published17():
    # This is baseline reconciliation at its published fee, not a candidate
    # cost/model selection. Only the authorized source-roster deletion changes.
    y = S.load_current_personal(1.275).drop(columns='BB_MRM').sum(axis=1)
    source = SNAPSHOT/'analysis/outputs/personal_portfolio_output.txt'
    text = source.read_text(encoding='utf-8')
    m = re.search(r'\$([\d,]+) a year \| max DD \$([\d,]+) \| worst month',text)
    if m is None: raise ValueError('Updated published baseline controls missing')
    annual,dd = float(y.sum()/len(y)*252),R.max_dd(y)
    assert abs(annual-float(m[1].replace(',',''))) <= .51
    assert abs(dd-float(m[2].replace(',',''))) <= .51
    expected = ast.literal_eval(re.search(r'by year: (\{[^\n]+\})',text)[1])
    year = {int(a):float(b) for a,b in y.groupby(y.index.year).sum().items()}
    for a,b in year.items(): assert abs(b-float(expected[a].replace('$','').replace(',',''))) <= .51
    return dict(columns=17,published_fee=1.275,annual=annual,max_daily_dd=dd,by_year=year,
                annual_drawdown_years_match_published_rounding=True,source_sha256=S.A.file_sha(source))


def check_outputs(out):
    out = Path(out)
    frame = pd.read_csv(out/'baseline_daily17.csv',index_col=0,parse_dates=True)
    candidate = pd.read_csv(out/'candidate_daily.csv',index_col=0,parse_dates=True).iloc[:,0]
    assert len(frame.columns)==17 and 'BB_MRM' not in frame
    plans,_ = S.personal_configurations(frame,candidate)
    summary = pd.read_csv(out/'mc_summary.csv')
    effects = pd.read_csv(out/'paired_effects.csv')
    days = pd.DatetimeIndex(frame.index)
    checked = paired = 0
    for cohort,(lo,hi) in S.COHORTS.items():
        mask = (days>=lo)&(days<hi)
        idx = np.load(out/f'personal_histories_{cohort}.npy')
        raw = np.load(out/f'personal_{cohort}.npz')
        assert idx.shape==(1000,252)
        for name,x in plans.items():
            values = x[mask].to_numpy()[idx]
            equity = values.cumsum(axis=1)
            peak = np.maximum.accumulate(np.c_[np.zeros(len(idx)),equity],axis=1)[:,1:]
            p,dd = equity[:,-1],(peak-equity).max(axis=1)
            np.testing.assert_allclose(p,raw[name+'__profit'],rtol=0,atol=1e-6)
            np.testing.assert_allclose(dd,raw[name+'__dd'],rtol=0,atol=1e-6)
            row = summary[(summary.cohort==cohort)&(summary.config==name)].iloc[0]
            np.testing.assert_allclose([row.profit_mean,row.profit_p50,row.dd_p95],
                                       [p.mean(),np.median(p),np.percentile(dd,95)],rtol=0,atol=1e-6)
            checked+=1
        for r in effects[effects.cohort==cohort].itertuples():
            p = raw[r.config+'__profit']-raw[r.reference+'__profit']
            dd = raw[r.config+'__dd']-raw[r.reference+'__dd']
            np.testing.assert_allclose([r.mean_profit_delta,r.mean_dd_delta],[p.mean(),dd.mean()],rtol=0,atol=1e-6)
            paired+=1
    result = dict(current_columns=17,configurations=16,MC_rows_reconciled=checked,paired_mean_rows_reconciled=paired,
                  same_history_indices_as_original=True,new_candidate_strategy_replays=0,
                  check_type='Saved-output arithmetic by refresh-wrapper author, not independent strategy parity')
    S.dump(out/'saved_output_checks.json',result)
    return result


def refresh(model,fee,amendment):
    authorize(amendment)
    sources = prepare_sources()
    old = S.OUT.parent/'personal'/model/f'fee_{fee:.2f}'
    out = OUT/model/f'fee_{fee:.2f}'
    out.mkdir(parents=True,exist_ok=True)
    old_inputs = {name:S.A.file_sha(old/name) for name in ('baseline_daily18.csv','candidate_daily.csv','reproduction.json')}
    frame18 = pd.read_csv(old/'baseline_daily18.csv',index_col=0,parse_dates=True)
    frame = frame18.drop(columns='BB_MRM')
    candidate = pd.read_csv(old/'candidate_daily.csv',index_col=0,parse_dates=True).iloc[:,0]
    assert len(frame.columns)==17 and frame.index.equals(candidate.index)
    frame.to_csv(out/'baseline_daily17.csv',index_label='date')
    shutil.copyfile(old/'candidate_daily.csv',out/'candidate_daily.csv')
    assert S.A.file_sha(old/'candidate_daily.csv')==S.A.file_sha(out/'candidate_daily.csv')
    S.dump(out/'baseline_reconciliation.json',verify_published17())
    summary,effects,historical = S.personal_benchmark(frame,candidate,out)
    for cohort in S.COHORTS:
        np.testing.assert_array_equal(np.load(old/f'personal_histories_{cohort}.npy'),np.load(out/f'personal_histories_{cohort}.npy'))
    portfolios,_ = S.personal_configurations(frame,candidate)
    joint=[]
    for group in (*S.P.STARTERS,'FULL'):
        base = portfolios[group+'__BASE'];loss=base<0
        joint.append(dict(group=group,correlation=candidate.corr(base),baseline_loss_days=int(loss.sum()),
                          joint_loss_days=int((loss&(candidate<0)).sum()),candidate_net_on_baseline_loss_days=float(candidate[loss].sum())))
    pd.DataFrame(joint).to_csv(out/'joint_losses.csv',index=False)
    for name,h in old_inputs.items(): assert S.A.file_sha(old/name)==h
    S.dump(out/'manifest_update.json',dict(reference=sources['reference'],amendment_commit=amendment,amendment_path=PLAN,
        original_strategy_preregistration='a4064ac',model=model,fee=fee,columns=list(frame),new_strategy_replays=0,
        original_adapter_sha256=S.A.file_sha(S.__file__),wrapper_sha256=S.A.file_sha(__file__),original_inputs=old_inputs,
        snapshot_manifest_sha256=S.A.file_sha(SNAPSHOT/'manifest.json'),
        bootstrap=dict(n=1000,horizon=252,block=10,seed=20261025),
        intervals='Historical annual-mean and simulation-precision intervals remain95%; source benchmark algorithms unchanged',
        preservation='Original18-leg outputs, original62e82a0 snapshot and original adapter unchanged',limitations=S.LIMITS))
    checks=check_outputs(out)
    print(json.dumps(dict(model=model,fee=fee,out=str(out),checks=checks),indent=2),flush=True)
    print(summary[(summary.cohort=='2023_plus')&summary.config.str.startswith('FULL__')].drop(columns='pieces').to_string(index=False),flush=True)
    return summary,effects,historical


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--model',choices=['CODE','CODE_BE'])
    parser.add_argument('--fee',type=float,choices=[1.24,1.04],default=1.24)
    parser.add_argument('--amendment',default='145c3ed')
    args=parser.parse_args()
    if args.prepare:
        m=prepare_sources();print(json.dumps(dict(reference=m['reference'],files=len(m['files']),starters_unchanged=m['starter_sets_unchanged']),indent=2))
    elif args.model:
        refresh(args.model,args.fee,args.amendment)
    else: parser.error('Choose --prepare or --model')
