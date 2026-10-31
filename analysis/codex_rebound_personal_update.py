"""Fixed Overnight Rebound placement refresh at Claude afde088 (19 legs).

Reuses saved candidate daily returns and reviewed personal engines. The old
17-leg outputs, frozen adapter, shared research caches and live files are read
only. Prepare/freeze before the four fixed financial cases; never refit.
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scratch_data/codex_deps'))
sys.path.insert(0, str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_rebound_accounts as R
import resampling as RES

REF = 'afde088'
OLD_REF = 'e1a94f7'
PLAN = 'agents/codex/plans/overnight_rebound_personal_refresh.md'
SNAPSHOT = ROOT/'agents/codex/inputs/rebound/plan_update_afde088'
OLD_OUT = ROOT/'analysis/outputs/codex_rebound/personal'
OUT = ROOT/'analysis/outputs/codex_rebound/personal19'
LEDGERS = {'SwingTarget':'checks/candidates/swing_target/mc_trades_v3.csv',
           'PaperTrend':'checks/candidates/papertrend/mc_trades_claude.csv'}
CONTEXT = ('personal_strategies/PORTFOLIO.md','analysis/personal_portfolio.py',
           'analysis/personal_variants.py','analysis/outputs/personal_portfolio_output.txt',
           'analysis/outputs/personal_variants_output.txt','funded_strategies/FUNDED_PLAN.md')
DEPENDENCIES = ('analysis/codex_rebound_accounts.py','analysis/codex_swing_accounts.py',
                'analysis/codex_anson_personal.py','analysis/metrics.py','analysis/resampling.py')
FINANCIAL = ('baseline_daily19.csv','candidate_daily.csv','candidate_marks.csv',
             'mc_summary.csv','paired_effects.csv','historical_summary.csv','joint_losses.csv')
LIMITS = [x.replace('published17-leg','published19-leg') for x in R.LIMITS] + [
    'SwingTarget/PaperTrend preserve the published from_trades convention: exits before the first personal date book to the first date, not dropped. Those early trades are disclosed separately.',
    'Published added MC ledgers already subtract17.25/NQ:7.25 commission plus two adverse ticks. Micro repricing adds only native commission minus.725; no second slippage charge.',
    'Current19 common-scale roster is fixed as of afde088. A planned future aggressive allocation is not adopted by this comparison.',
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def function_ast(source, name):
    tree=ast.parse(source.decode('utf-8-sig'))
    return ast.dump(next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name))


def starter_sets(source):
    tree=ast.parse(source.decode('utf-8-sig'))
    node=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='sets' for t in n.targets))
    return {k.split('.')[0]:v for k,v in ast.literal_eval(node.value).items()}


def source_bindings():
    inputs={}
    for model in ('UNIFORM','SUNDAY2'):
        for fee in (1.24,1.04):
            old=OLD_OUT/model/f'fee_{fee:.2f}'
            for name in ('baseline_daily17.csv','candidate_daily.csv','candidate_marks.csv',
                         'calendar_bookkeeping.json','manifest_personal.json','provenance_recheck.json'):
                path=old/name; inputs[path.relative_to(ROOT).as_posix()]=sha(path)
            for cohort in R.COHORTS:
                path=old/f'personal_histories_{cohort}.npy';inputs[path.relative_to(ROOT).as_posix()]=sha(path)
    inputs.update({p:sha(ROOT/p) for p in DEPENDENCIES})
    for path in SNAPSHOT.rglob('*'):
        if path.is_file() and path.name!='frozen_binding.json':
            inputs[path.relative_to(ROOT).as_posix()]=sha(path)
    return inputs


def prepare_sources():
    manifest=dict(reference=R.git('rev-parse',REF).decode().strip(),
                  previous_reference=R.git('rev-parse',OLD_REF).decode().strip(),
                  files={},unchanged_personal_inputs=[],returns_computed=False)
    for rel in (*CONTEXT,*LEDGERS.values()):
        data=R.git('show',REF+':'+rel);dest=SNAPSHOT/rel
        if dest.exists() and dest.read_bytes()!=data: raise ValueError('Different existing snapshot: '+rel)
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists(): dest.write_bytes(data)
        manifest['files'][rel]=dict(git_blob=R.git('rev-parse',REF+':'+rel).decode().strip(),sha256=sha(dest))
    for rel in R.S.SOURCES:
        if rel in CONTEXT: continue
        old=R.git('rev-parse',OLD_REF+':'+rel).decode().strip()
        current=R.git('rev-parse',REF+':'+rel).decode().strip()
        if old!=current: raise ValueError('Unexpected existing personal input change: '+rel)
        manifest['unchanged_personal_inputs'].append(dict(path=rel,git_blob=current))
    old=R.git('show',OLD_REF+':analysis/personal_portfolio.py')
    current=(SNAPSHOT/'analysis/personal_portfolio.py').read_bytes()
    for name in ('from_trades','twin_marked'):
        if function_ast(old,name)!=function_ast(current,name): raise ValueError('Published helper changed: '+name)
    if starter_sets(old)!=starter_sets(current) or starter_sets(current)!=R.P.STARTERS:
        raise ValueError('Starter ladder changed')
    for fee in (1.24,1.04):
        a=OLD_OUT/'UNIFORM'/f'fee_{fee:.2f}'/'baseline_daily17.csv'
        b=OLD_OUT/'SUNDAY2'/f'fee_{fee:.2f}'/'baseline_daily17.csv'
        if a.read_bytes()!=b.read_bytes(): raise ValueError('Original baseline differs across candidate models')
    # Assert the only added concat pieces are the two expressly adopted legs.
    tree=ast.parse(current.decode('utf-8-sig'))
    node=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='P' for t in n.targets))
    names=[n.id for n in node.value.args[0].elts]
    if names!=['p','fc','tw','otv','dth','ku','s47','s30','stg','ptr']:
        raise ValueError('Unexpected current portfolio concat')
    manifest.update(starter_sets_unchanged=True,published_booking_helpers_unchanged=True,
        roster_change='Existing17 unchanged; add SwingTarget v3 and PAPERTREND v2 at1MNQ each',
        new_candidate_replays=0,limitations=LIMITS,
        funded_roster_changes={'50K_funded':'VB2/1 becomes1/1 plus SwingTarget1MNQ',
                              '150K_funded':'DualThrust2MNQ replaced by SwingTarget2MNQ',
                              'evaluations':'unchanged'},
        funded_evaluation_status='LIMITED_BASELINE_CHRONOLOGY; no joint account simulation or pass/payout claim')
    R.dump(SNAPSHOT/'manifest.json',manifest)
    return manifest


def freeze():
    prepare_sources()
    binding=dict(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        reference=R.git('rev-parse',REF).decode().strip(),wrapper_sha256=sha(__file__),
        source_bindings=source_bindings(),new_economic_models=0,
        scope='Four fixed personal19 cases, unchanged saved candidate daily P&L, fixed histories and fees')
    path=SNAPSHOT/'frozen_binding.json'
    if path.exists():
        old=json.loads(path.read_text())
        if old['wrapper_sha256']!=binding['wrapper_sha256'] or old['source_bindings']!=binding['source_bindings']:
            raise ValueError('Frozen source/input binding changed')
        return old
    R.dump(path,binding)
    return binding


def assert_frozen():
    binding=json.loads((SNAPSHOT/'frozen_binding.json').read_text())
    assert sha(__file__)==binding['wrapper_sha256'],'Wrapper changed after freeze'
    assert source_bindings()==binding['source_bindings'],'Input/dependency changed after freeze'
    return binding


def added_daily(days,fee):
    days=pd.DatetimeIndex(days);columns={};audit={}
    for name,rel in LEDGERS.items():
        t=pd.read_csv(SNAPSHOT/rel,parse_dates=['date','exit_date'])
        t=t[t.date<=days[-1]].copy()
        # Match published from_trades exactly, including pre-calendar booking.
        np.testing.assert_allclose(t.net,t.gross-17.25,rtol=0,atol=1e-6)
        x=t.net.to_numpy()/10.-(fee-.725)
        k=np.minimum(days.searchsorted(pd.DatetimeIndex(t.date)),len(days)-1)
        series=pd.Series(x,index=days[k]).groupby(level=0).sum().reindex(days,fill_value=0.).rename(name)
        np.testing.assert_allclose(series.sum(),x.sum(),rtol=0,atol=1e-7)
        early=t.date<days[0]
        audit[name]=dict(source_sha256=sha(SNAPSHOT/rel),trades=len(t),net_micro=float(series.sum()),
            earliest_exit=str(t.date.min().date()),latest_exit=str(t.date.max().date()),
            pre_calendar_trades=int(early.sum()),pre_calendar_native_net=float(x[early.to_numpy()].sum()),
            pre_calendar_book_date=str(days[0].date()),source_commission_NQ=7.25,
            source_total_cost_NQ=17.25,native_commission=fee,native_slippage_already_included=1.)
        columns[name]=series
    return pd.DataFrame(columns,index=days),audit


def verify_published19():
    # Original17 own-fee reconstruction is independent of candidate histories.
    original=R.S.load_current_personal(1.275).drop(columns='BB_MRM')
    addition,audit=added_daily(original.index,1.275)
    frame=pd.concat([original,addition],axis=1);total=frame.sum(axis=1)
    text=(SNAPSHOT/'analysis/outputs/personal_portfolio_output.txt').read_text(encoding='utf-8')
    m=re.search(r'\$([\d,]+) a year \| max DD \$([\d,]+) \| worst month',text)
    assert m is not None
    annual,dd=float(total.sum()/len(total)*252),RES.max_dd(total)
    assert abs(annual-float(m[1].replace(',','')))<=.51,(annual,m[1])
    assert abs(dd-float(m[2].replace(',','')))<=.51,(dd,m[2])
    expected=ast.literal_eval(re.search(r'by year: (\{[^\n]+\})',text)[1])
    yearly={int(y):float(v) for y,v in total.groupby(total.index.year).sum().items()}
    assert set(yearly)==set(expected)
    for y,value in yearly.items(): assert abs(value-float(expected[y].replace('$','').replace(',','')))<=.51
    return dict(columns=19,published_fee=1.275,annual=annual,max_daily_dd=dd,by_year=yearly,
        annual_drawdown_years_match_published_rounding=True,added_ledger_booking=audit,
        original17_reconstruction='Reviewed pinned helper; underlying inputs and booking functions unchanged',
        source_sha256=sha(SNAPSHOT/'analysis/outputs/personal_portfolio_output.txt'))


def check_outputs(out,old,frame,candidate):
    plans,_=R.personal_configurations(frame,candidate)
    summary=pd.read_csv(out/'mc_summary.csv');effects=pd.read_csv(out/'paired_effects.csv')
    days=pd.DatetimeIndex(frame.index);checked=paired=0
    for cohort,(lo,hi) in R.COHORTS.items():
        mask=(days>=lo)&(days<hi);idx=np.load(out/f'personal_histories_{cohort}.npy')
        np.testing.assert_array_equal(idx,np.load(old/f'personal_histories_{cohort}.npy'))
        raw=np.load(out/f'personal_{cohort}.npz')
        for name,x in plans.items():
            values=x[mask].to_numpy()[idx];equity=values.cumsum(axis=1)
            peak=np.maximum.accumulate(np.c_[np.zeros(len(idx)),equity],axis=1)[:,1:]
            p,d=equity[:,-1],(peak-equity).max(axis=1)
            np.testing.assert_allclose(p,raw[name+'__profit'],rtol=0,atol=1e-6)
            np.testing.assert_allclose(d,raw[name+'__dd'],rtol=0,atol=1e-6)
            row=summary[(summary.cohort==cohort)&(summary.config==name)].iloc[0]
            np.testing.assert_allclose([row.profit_mean,row.profit_p50,row.dd_p95],
                [p.mean(),np.median(p),np.percentile(d,95)],rtol=0,atol=1e-6)
            if not name.startswith('FULL__'):
                oldraw=np.load(old/f'personal_{cohort}.npz')
                np.testing.assert_array_equal(raw[name+'__profit'],oldraw[name+'__profit'])
                np.testing.assert_array_equal(raw[name+'__dd'],oldraw[name+'__dd'])
            checked+=1
        for row in effects[effects.cohort==cohort].itertuples():
            p=raw[row.config+'__profit']-raw[row.reference+'__profit']
            d=raw[row.config+'__dd']-raw[row.reference+'__dd']
            np.testing.assert_allclose([row.mean_profit_delta,row.mean_dd_delta],[p.mean(),d.mean()],rtol=0,atol=1e-6)
            paired+=1
    return dict(current_personal_columns=19,configurations=20,MC_rows_reconciled=checked,
        paired_mean_rows_reconciled=paired,starters_A_D_saved_paths_exactly_unchanged=True,
        same_history_indices_as_original=True,saved_candidate_daily_exactly_unchanged=True,
        new_candidate_strategy_replays=0,
        check_type='Saved-output arithmetic by refresh-wrapper author, not independent strategy parity')


def refresh(model,fee,amendment):
    R.S.require_plan(amendment,PLAN);binding=assert_frozen()
    out=OUT/model/f'fee_{fee:.2f}';old=OLD_OUT/model/f'fee_{fee:.2f}'
    if (out/'mc_summary.csv').exists(): raise ValueError('Preserve existing financial run; refuse overwrite')
    out.mkdir(parents=True,exist_ok=True)
    frame17=pd.read_csv(old/'baseline_daily17.csv',index_col=0,parse_dates=True)
    candidate=pd.read_csv(old/'candidate_daily.csv',index_col=0,parse_dates=True).iloc[:,0]
    assert len(frame17.columns)==17 and frame17.index.equals(candidate.index)
    addition,booking=added_daily(frame17.index,fee)
    frame=pd.concat([frame17,addition],axis=1)
    assert len(frame.columns)==19 and not frame.isna().any().any()
    frame.to_csv(out/'baseline_daily19.csv',index_label='date')
    for name in ('candidate_daily.csv','candidate_marks.csv','calendar_bookkeeping.json'):
        shutil.copyfile(old/name,out/name)
        assert sha(old/name)==sha(out/name)
    R.dump(out/'baseline_reconciliation.json',verify_published19())
    R.dump(out/'added_ledger_booking.json',booking)
    summary,effects,historical=R.personal_benchmark(frame,candidate,out)
    portfolios,_=R.personal_configurations(frame,candidate);joint=[];cohort_joint=[]
    for group in (*R.P.STARTERS,'FULL'):
        base=portfolios[group+'__BASE'];loss=base<0
        joint.append(dict(group=group,correlation=candidate.corr(base),baseline_loss_days=int(loss.sum()),
            joint_loss_days=int((loss&(candidate<0)).sum()),candidate_net_on_baseline_loss_days=float(candidate[loss].sum())))
        for cohort,(lo,hi) in R.COHORTS.items():
            mask=(frame.index>=lo)&(frame.index<hi);b=base[mask];c=candidate[mask];loss=b<0
            cohort_joint.append(dict(group=group,cohort=cohort,correlation=c.corr(b),baseline_loss_days=int(loss.sum()),
                joint_loss_days=int((loss&(c<0)).sum()),candidate_net_on_baseline_loss_days=float(c[loss].sum())))
    pd.DataFrame(joint).to_csv(out/'joint_losses.csv',index=False)
    pd.DataFrame(cohort_joint).to_csv(out/'joint_losses_by_cohort.csv',index=False)
    contexts=json.loads((old/'account_context_limits.json').read_text())
    contexts.update(reference=binding['reference'],funded_roster_changes={
        '50K_funded':'VaultBreak1/1 plus SwingTarget1MNQ (previously VB2/1)',
        '150K_funded':'SwingTarget2MNQ replaces DualThrust2MNQ'},
        roster_refresh_repairs_joint_chronology=False,no_pass_payout_fee_benefit_claim=True)
    R.dump(out/'account_context_limits.json',contexts)
    checks=check_outputs(out,old,frame,candidate)
    R.dump(out/'saved_output_checks.json',checks)
    assert_frozen()
    R.dump(out/'manifest_update.json',dict(reference=binding['reference'],amendment_commit=amendment,
        amendment_path=PLAN,original_strategy_preregistration='d94d815',model=model,fee=fee,
        current_personal_columns=list(frame),snapshot_reference=binding['reference'],
        original_daily_input_sha256=sha(old/'candidate_daily.csv'),
        candidate_daily_output_sha256=sha(out/'candidate_daily.csv'),new_strategy_replays=0,
        candidate_daily_oldhash=sha(old/'candidate_daily.csv'),candidate_daily_newhash=sha(out/'candidate_daily.csv'),
        wrapper_sha256=sha(__file__),source_hash_before=binding['wrapper_sha256'],source_hash_after=sha(__file__),
        wrapper_sha256_before=binding['wrapper_sha256'],wrapper_sha256_after=sha(__file__),
        original_adapter_sha256=sha(R.__file__),frozen_binding_sha256=sha(SNAPSHOT/'frozen_binding.json'),
        financial_csv_sha256={name:sha(out/name) for name in FINANCIAL},
        bootstrap=dict(n=1000,horizon=252,block=10,seed=20261025),interval_level=.95,
        preservation='Original17, original adapter, prior verification and shared caches unchanged',
        baseline_calendar_policy='Published personal date index preserved; inherited Dec5→Dec6 candidate mapping logged unchanged',
        native_fee_rule='Added ledgers net/10 minus(fee-.725), source17.25/NQ already includes1MNQ tick costs',
        limitations=LIMITS))
    print(json.dumps(dict(model=model,fee=fee,checks=checks,wrapper_sha256=sha(__file__)),indent=2),flush=True)
    print(summary[(summary.cohort=='2023_plus')&summary.config.str.startswith('FULL__')]
          .drop(columns='pieces').to_string(index=False),flush=True)
    return summary,effects,historical


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--freeze',action='store_true')
    parser.add_argument('--model',choices=['UNIFORM','SUNDAY2'])
    parser.add_argument('--fee',type=float,choices=[1.24,1.04],default=1.24)
    parser.add_argument('--amendment',default='80fff8a')
    args=parser.parse_args()
    if args.prepare: print(json.dumps(prepare_sources(),indent=2))
    elif args.freeze: print(json.dumps(freeze(),indent=2))
    elif args.model: refresh(args.model,args.fee,args.amendment)
    else: parser.error('Use --prepare, --freeze, or --model')
