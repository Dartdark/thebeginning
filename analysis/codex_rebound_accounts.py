"""Overnight Rebound account-session paths and current personal placement.

Preparation is metadata-only. Candidate returns require a committed root plan
and explicit caller authorization. No shared module/cache or live changes.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import pickle
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scratch_data/codex_deps'))
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_swing_accounts as S
import codex_anson_personal as P
from codex_r2vault_personal import candidate_daily as marked_candidate_daily
import metrics as M

REF='e1a94f7'
OUT=ROOT/'analysis/outputs/codex_rebound'
SNAPSHOT=ROOT/'agents/codex/inputs/rebound/plan_snapshot'
PLAN='agents/codex/plans/overnight_rebound.md'
COHORTS={'2018_plus':('2018-01-01','2100-01-01'),
         '2018_22':('2018-01-01','2023-01-01'),
         '2023_plus':('2023-01-01','2100-01-01')}
SOURCES=('personal_strategies/PORTFOLIO.md','analysis/personal_portfolio.py',
         'analysis/outputs/personal_portfolio_output.txt','funded_strategies/FUNDED_PLAN.md',
         'analysis/overnight_tick_bench.py','analysis/bridge_monday_confirm.py',
         'checks/candidates/overnight_tick/python_trades.csv','checks/candidates/overnight_tick/trades.csv')
LIMITS=[
    'Crossing calendar midnight is not crossing the16:00–17:00 CME session break. Intended17→03 nights are within one account day.',
    'Old builder overnight wording is interpreted through the currently adopted OT17→03 plan; this is a fixed research-policy assumption, not fresh broker-rule verification.',
    'Prepared Bridge Monday starts at Monday00:00 and omits Sunday19→midnight adverse exposure. It cannot certify Sunday2 joint risk.',
    'Prepared CLS/OT use whole-day constant adverse proxies that can invent simultaneous positions. No material Apex benefit is claimed from them.',
    'OT order-flow history ends2026-07-07; later zeros are incomplete baseline evidence, not verified no-trade days.',
    'Personal preserves published17-leg fees/marks: per-nonzero-day plan commissions undercount some reentries, MOC/S30 retain inherited approximations, Twin is the marked v1 checker ledger.',
    'Personal daily drawdown does not certify intraday margin/liquidation safety or hedge delivery before an account breach.',
]


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args])


def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,default=str,allow_nan=True)+'\n',encoding='utf-8')


def prepare_sources():
    manifest=dict(reference=git('rev-parse',REF).decode().strip(),files={},baseline_csv={},returns_computed=False)
    for rel in SOURCES:
        data=git('show',REF+':'+rel);target=SNAPSHOT/rel
        if target.exists() and target.read_bytes()!=data: raise ValueError('Different existing snapshot: '+str(target))
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists(): target.write_bytes(data)
        manifest['files'][rel]=dict(git_blob=git('rev-parse',REF+':'+rel).decode().strip(),sha256=S.A.file_sha(target))
    for fee in (1.24,1.04):
        paths=[ROOT/f'analysis/outputs/codex_swing_target/personal17/{model}/fee_{fee:.2f}/baseline_daily17.csv'
               for model in ('CODE','CODE_BE')]
        if paths[0].read_bytes()!=paths[1].read_bytes(): raise ValueError('Prior common17 baseline differs across models')
        # The baseline is a committed research artifact, not a new cache build.
        rel=paths[0].relative_to(ROOT).as_posix()
        if paths[0].read_bytes().replace(b'\r\n',b'\n')!=git('show','HEAD:'+rel).replace(b'\r\n',b'\n'):
            raise ValueError('Committed current17 baseline artifact changed')
        manifest['baseline_csv'][str(fee)]=dict(path=rel,sha256=S.A.file_sha(paths[0]),columns=17)
    old=ROOT/'agents/codex/inputs/swing_target/plan_update_e08c353/analysis/outputs/personal_portfolio_output.txt'
    current=SNAPSHOT/'analysis/outputs/personal_portfolio_output.txt'
    if old.read_bytes()!=current.read_bytes(): raise ValueError('Latest personal published17 baseline changed; update scope first')
    tree=ast.parse((SNAPSHOT/'analysis/personal_portfolio.py').read_text(encoding='utf-8-sig'))
    node=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='sets' for t in n.targets))
    sets={k.split('.')[0]:v for k,v in ast.literal_eval(node.value).items()}
    if sets!=P.STARTERS: raise ValueError('Current starter ladder changed')
    manifest.update(starter_sets_unchanged=True,latest17_published_output_unchanged=True,
                    personal_overlap_rule='OvernightTick where present, otherwise OvernightBiasML',limitations=LIMITS)
    dump(SNAPSHOT/'manifest.json',manifest)
    return manifest


def authorize(prereg,*,authorized_returns=False,plan_path=PLAN):
    if not authorized_returns: raise PermissionError('Root go and committed preregistration required before returns')
    S.require_plan(prereg,plan_path)


def event_stamp(g,row,j,phase='open'):
    if phase not in ('open','intrabar'): raise ValueError('Unknown executable fill phase')
    return pd.Timestamp(g.ts[int(row)])+pd.Timedelta(minutes=int(j)-1,seconds=30 if phase=='intrabar' else 0)


def account_session(stamp):
    """Day identified by its ending date;17:00→next16:00 is one CME day."""
    stamp=pd.Timestamp(stamp);day=stamp.normalize()
    return day+pd.Timedelta(days=1) if stamp>=day+pd.Timedelta(hours=17) else day


def session_audit(g,trades):
    rows=[]
    for no,t in enumerate(trades.itertuples()):
        e=event_stamp(g,t.day,t.j0,t.entry_phase)
        x=event_stamp(g,t.exit_day,t.j1,t.exit_phase)
        account=account_session(e)
        start=account-pd.Timedelta(days=1)+pd.Timedelta(hours=17)
        end=account+pd.Timedelta(hours=16)
        # 15:59 is the adopted flat deadline. Midnight itself is irrelevant.
        flat=account+pd.Timedelta(hours=15,minutes=59)
        valid=(e>=start and x>=e and x<=flat and account_session(x)==account)
        rows.append(dict(trade_index=no,entry_stamp=str(e),exit_stamp=str(x),account_date=account,
            entry_calendar_date=e.date(),exit_calendar_date=x.date(),cross_calendar_date=e.date()!=x.date(),
            same_account_session=account_session(x)==account,crosses_break=not(e>=start and x<end),
            flat_violation=x>flat,account_window_valid=valid,qty=int(t.qty),
            unknown_held_minutes=int(getattr(t,'unknown_held_minutes',0))))
    result=pd.DataFrame(rows)
    if 'account_date' in trades:
        np.testing.assert_array_equal(pd.DatetimeIndex(result.account_date).to_numpy(),
                                      pd.DatetimeIndex(trades.account_date).to_numpy())
    return result


def native_net_per_unit(t,fee):
    expected=(t.exit-t.entry)*t.side*20.
    if 'pnl' in t: np.testing.assert_allclose(t.pnl,expected,rtol=0,atol=1e-6)
    return expected/10.-fee-.5-.5*t.kind.ne(1).astype(int)


def candidate_night_paths(g,trades,fee=1.24,account_dates=None):
    """Per-unit chronological1380-column17→16 paths plus separate Sunday qty.

    Entry/exit are raw executable prices. Account sizing must multiply the
    full-size candidate base by qty BEFORE cushion/integer rounding.
    """
    audit=session_audit(g,trades)
    # Actual night sessions can exist on dates absent from the RTH-derived
    # account calendar (e.g.2018-12-05). A candidate-only path must retain them.
    dates=(pd.DatetimeIndex(g.ts[g.trading]).union(pd.DatetimeIndex(audit.account_date)).sort_values()
           if account_dates is None else pd.DatetimeIndex(account_dates))
    pos={d:i for i,d in enumerate(dates)}
    if not audit.account_window_valid.all(): raise ValueError('Source crosses a real account flat/session boundary')
    if audit.unknown_held_minutes.gt(0).any(): raise ValueError('Candidate contains unobserved held minutes; no invented path')
    w,r=np.zeros((len(dates),1380)),np.zeros((len(dates),1380))
    qty=np.zeros(len(dates))
    seen=set()
    for no,t in enumerate(trades.itertuples()):
        account=pd.Timestamp(audit.iloc[no].account_date)
        if account not in pos: raise ValueError('Candidate night absent from common account calendar')
        d=pos[account]
        if d in seen: raise ValueError('Multiple events in one night require explicit quantity chronology')
        seen.add(d)
        if int(t.qty) not in (1,2): raise ValueError('Frozen source quantity must be1or2')
        qty[d]=int(t.qty)
        a=int(t.day)*1440+int(t.j0);b=int(t.exit_day)*1440+int(t.j1)
        if b<a: raise ValueError('Exit before entry')
        end=b+int(t.exit_phase!='open')
        source=(g.l if t.side>0 else g.h).ravel()
        price=np.array(source[a:end],copy=True)
        if len(price):
            price[0]=float(t.entry_minute_adverse_px)
            if t.exit_phase!='open': price[-1]=float(t.exit_minute_adverse_px)
            if not np.isfinite(price).all(): raise ValueError('Missing native price inside candidate night')
        start=account-pd.Timedelta(days=1)+pd.Timedelta(hours=17)
        # Native minute j closes at j; its wall-clock open is j−1.
        first=int((event_stamp(g,t.day,t.j0,'open')-start)/pd.Timedelta(minutes=1))
        exitcol=int((event_stamp(g,t.exit_day,t.j1,'open')-start)/pd.Timedelta(minutes=1))
        if not 0<=first<=exitcol<1380: raise ValueError('Candidate extends outside account timeline')
        if len(price)!=exitcol-first+int(t.exit_phase!='open'): raise ValueError('Native chronology/timeline length differs')
        unit=(t.exit-t.entry)*t.side*2.-fee-.5-(0. if int(t.kind)==1 else .5)
        marks=(price-t.entry)*t.side*2.-fee-.5
        if len(marks) and t.exit_phase!='open': marks[-1]=min(marks[-1],unit)
        w[d,first:first+len(marks)]=marks
        w[d,first+len(marks):]=unit
        r[d,exitcol:]=unit
    return w,r,qty,audit


def account_context_limits(g,trades,model,out):
    """Report missing joint chronology without calling legal nights illegal."""
    audit=session_audit(g,trades)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    audit.to_csv(out/'account_session_audit.csv',index=False)
    invalid=int((~audit.account_window_valid).sum())
    rows=[]
    for context in ('50K_evaluation','150K_evaluation','50K_funded','150K_funded'):
        baseline=('Bridge Monday Sunday-night exposure is omitted by prepared Monday00:00 paths'
                  if context.endswith('evaluation') else
                  'OT/CLS whole-day adverse proxies and omitted Bridge Sunday-night path cannot certify causal joint risk; OT data also ends2026-07-07')
        rows.append(dict(model=model,context=context,status='SOURCE_WINDOW_INCOMPATIBLE' if invalid else 'LIMITED_BASELINE_CHRONOLOGY',
            source_invalid_windows=invalid,calendar_crossings=int(audit.cross_calendar_date.sum()),
            same_account_session=int(audit.same_account_session.sum()),candidate_quantity=2 if context=='150K_evaluation' else 1,
            unobserved_held_minutes=int(audit.unknown_held_minutes.sum()),
            comparison_run=False,overlap_slot='ONB30' if context.endswith('evaluation') else 'OT',limitation=baseline))
    dump(out/'account_context_limits.json',dict(contexts=rows,policy='17→next16 account day, flat before15:59; mere midnight crossing allowed',
        no_trade_deletions=True,no_material_Apex_benefit_claim=True,
        gap_interpretation='Unobserved bars can be no-print minutes, closures or feed gaps; no feed-loss cause or illegal hold is inferred from their count alone.',
        limitations=LIMITS))
    return pd.DataFrame(rows)


def validate_candidate_paths(g,trades,model,fee,out):
    """Validate the candidate timeline alone; never infer joint Apex benefit."""
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    contexts=account_context_limits(g,trades,model,out)
    try:
        w,r,q,a=candidate_night_paths(g,trades,fee)
    except ValueError as exc:
        result=dict(status='LIMITED_CANDIDATE_PATH',reason=str(exc),joint_account_comparison_run=False,
                    mere_midnight_crossing_not_rejected=True)
        # Engineering validation only. Every source trade remains in the actual
        # personal comparison; no return statistic is selected on this subset.
        known=trades[trades.unknown_held_minutes.eq(0)].copy().reset_index(drop=True)
        if len(known):
            try:
                w,r,q,a=candidate_night_paths(g,known,fee)
                unit=native_net_per_unit(known,fee)
                np.testing.assert_allclose(r[:,-1].sum(),unit.sum(),rtol=0,atol=1e-6)
                np.testing.assert_allclose((r[:,-1]*q).sum(),(unit*known.qty).sum(),rtol=0,atol=1e-6)
                result.update(complete_price_nights_path_validated=len(known),
                              validation_scope='Engineering-only complete-price subset; all source trades retained in personal results',
                              quantity_weighting_reconciled=True)
            except ValueError as partial:
                result['complete_price_subset_limit']=str(partial)
        dump(out/'candidate_path_validation.json',result)
        return result
    unit=native_net_per_unit(trades,fee)
    np.testing.assert_allclose(r[:,-1].sum(),unit.sum(),rtol=0,atol=1e-6)
    np.testing.assert_allclose((r[:,-1]*q).sum(),(unit*trades.qty).sum(),rtol=0,atol=1e-6)
    result=dict(status='CANDIDATE_TIMELINE_VALID',events=len(trades),contract_roundtrips=int(trades.qty.sum()),
        calendar_midnight_crossings=int(a.cross_calendar_date.sum()),real_account_session_violations=0,
        unit_path_shape=list(w.shape),session_minutes=1380,source_qty_kept_outside_unit_paths=True,
        closing_unit_totals_match=True,weighted_closing_totals_match=True,joint_account_comparison_run=False,
        limits='A valid candidate timeline alone does not repair current baseline Bridge/OT/CLS chronology.')
    dump(out/'candidate_path_validation.json',result)
    return result


def personal_configurations(frame,candidate):
    sets={**P.STARTERS,'FULL':list(frame)}
    plans,meta={},{}
    for group,keys in sets.items():
        overlap='OvernightTick' if 'OvernightTick' in keys else 'OvernightBiasML'
        if overlap not in keys: raise ValueError('Frozen replacement slot missing')
        base=frame[keys].sum(axis=1);empty=base-frame[overlap]
        for name,x in dict(BASE=base,ADD=base+candidate,EMPTY=empty,REPLACE=empty+candidate).items():
            key=group+'__'+name;plans[key]=x
            meta[key]=dict(group=group,allocation=name,replaced_leg=overlap,pieces=keys)
    assert len(plans)==20
    return plans,meta


def personal_benchmark(frame,candidate,out):
    plans,meta=personal_configurations(frame,candidate)
    days=pd.DatetimeIndex(frame.index);rows,effects,historical=[],[],[]
    periods={**COHORTS,**{str(y):(f'{y}-01-01',f'{y+1}-01-01') for y in sorted(days.year.unique())}}
    for name,x in plans.items():
        for period,(lo,hi) in periods.items():
            d=x[(days>=lo)&(days<hi)]
            m=M.perf(np.r_[0.,d.to_numpy()],d[d!=0]);m.update(config=name,period=period,total=d.sum(),days=len(d),**meta[name])
            historical.append(m)
    for cohort,(lo,hi) in COHORTS.items():
        mask=(days>=lo)&(days<hi)
        idx=P.histories(int(mask.sum()),n=1000,horizon=252,block=10,seed=20261025)
        np.save(out/f'personal_histories_{cohort}.npy',idx)
        raw={}
        for name,x in plans.items():
            profit,dd=P.simulate_daily(x[mask].to_numpy(),idx);raw[name]=profit,dd
            rows.append(dict(cohort=cohort,config=name,profit_mean=profit.mean(),profit_p5=np.percentile(profit,5),
                profit_p50=np.median(profit),profit_p95=np.percentile(profit,95),p_losing_year=(profit<=0).mean(),
                dd_p50=np.median(dd),dd_p95=np.percentile(dd,95),capital_20pct=np.percentile(dd,95)/.2,
                median_profit_over_dd95=np.median(profit)/max(np.percentile(dd,95),1e-9),**meta[name]))
        for name,(p,d) in raw.items():
            group=meta[name]['group']
            for ref in (group+'__BASE',group+'__EMPTY'):
                bp,bd=raw[ref]
                hlo,hhi=P.historical_annual_effect_interval((plans[name]-plans[ref])[mask].to_numpy(),n=5000,block=10,seed=20261025)
                plo,phi=P.paired_mean_interval(p-bp,n=5000,seed=20261025)
                dlo,dhi=P.paired_mean_interval(d-bd,n=5000,seed=20261025)
                effects.append(dict(cohort=cohort,config=name,reference=ref,mean_profit_delta=(p-bp).mean(),
                    simulation_profit_lo=plo,simulation_profit_hi=phi,mean_dd_delta=(d-bd).mean(),
                    simulation_dd_lo=dlo,simulation_dd_hi=dhi,historical_annual_mean_lo=hlo,historical_annual_mean_hi=hhi,
                    dd95_delta=np.percentile(d,95)-np.percentile(bd,95)))
        np.savez_compressed(out/f'personal_{cohort}.npz',**{name+'__'+label:value[i]
                              for name,value in raw.items() for i,label in enumerate(('profit','dd'))})
    summary,effect,hist=pd.DataFrame(rows),pd.DataFrame(effects),pd.DataFrame(historical)
    summary.to_csv(out/'mc_summary.csv',index=False);effect.to_csv(out/'paired_effects.csv',index=False)
    hist.to_csv(out/'historical_summary.csv',index=False)
    return summary,effect,hist


def normalized_ledger(trades):
    t=trades.rename(columns={a:b for a,b in {'day':'entry_row','exit_day':'exit_row','j0':'entry_j','j1':'exit_j'}.items()
                            if a in trades and b not in trades}).copy()
    if 'exit_row' not in t: t['exit_row']=t.entry_row
    return t


def run_personal(g,trades,prereg,*,model,fee=1.24,authorized_returns=False,plan_path=PLAN,out=None,open_positions=None):
    authorize(prereg,authorized_returns=authorized_returns,plan_path=plan_path)
    sources=prepare_sources();out=Path(out or OUT/'personal'/model/f'fee_{fee:.2f}');out.mkdir(parents=True,exist_ok=True)
    baseline=ROOT/sources['baseline_csv'][str(fee)]['path']
    frame=pd.read_csv(baseline,index_col=0,parse_dates=True)
    if len(frame.columns)!=17 or 'BB_MRM' in frame: raise ValueError('Current17 baseline required')
    if not trades.qty.isin([1,2]).all(): raise ValueError('Frozen quantities must be1or2')
    # Multiplicity represents contracts and fees, never independent signals.
    expanded=trades.loc[trades.index.repeat(trades.qty.astype(int))].reset_index(drop=True)
    opened=None if open_positions is None else open_positions.loc[open_positions.index.repeat(open_positions.qty.astype(int))].reset_index(drop=True)
    candidate,marks,money=marked_candidate_daily(g,normalized_ledger(expanded),frame.index,fee=fee,
                                                open_positions=None if opened is None else normalized_ledger(opened))
    if opened is None:
        np.testing.assert_allclose(candidate.sum(),(native_net_per_unit(trades,fee)*trades.qty).sum(),rtol=0,atol=1e-6)
    frame.to_csv(out/'baseline_daily17.csv',index_label='date');candidate.to_csv(out/'candidate_daily.csv',index_label='date')
    marks.to_csv(out/'candidate_marks.csv',index=False)
    validate_candidate_paths(g,trades,model,fee,out)
    summary,effects,historical=personal_benchmark(frame,candidate,out)
    portfolios,_=personal_configurations(frame,candidate);joint=[]
    for group in (*P.STARTERS,'FULL'):
        base=portfolios[group+'__BASE'];loss=base<0
        joint.append(dict(group=group,correlation=candidate.corr(base),baseline_loss_days=int(loss.sum()),
            joint_loss_days=int((loss&(candidate<0)).sum()),candidate_net_on_baseline_loss_days=float(candidate[loss].sum())))
    pd.DataFrame(joint).to_csv(out/'joint_losses.csv',index=False)
    dump(out/'manifest_personal.json',dict(reference=sources['reference'],preregistration=prereg,plan_path=plan_path,model=model,fee=fee,
        baseline_sha256=S.A.file_sha(baseline),source_snapshot_sha256=S.A.file_sha(SNAPSHOT/'manifest.json'),
        script_sha256=S.A.file_sha(__file__),independent_events=len(trades),contract_roundtrips=int(trades.qty.sum()),
        bookkeeping_expanded_rows=len(expanded),candidate_marks=money,configurations=20,personal_columns=list(frame),
        no_Apex_limits=True,bootstrap=dict(n=1000,horizon=252,block=10,seed=20261025),interval_level=.95,
        shared_caches_written=False,limitations=LIMITS))
    return dict(summary=summary,effects=effects,historical=historical)


def check_personal_outputs(out,ledger=None,fee=None):
    """Rebook saved arrays and exact20 contrasts without drawing new paths."""
    out=Path(out)
    frame=pd.read_csv(out/'baseline_daily17.csv',index_col=0,parse_dates=True)
    candidate=pd.read_csv(out/'candidate_daily.csv',index_col=0,parse_dates=True).iloc[:,0]
    if len(frame.columns)!=17: raise ValueError('Expected full17 baseline')
    plans,meta=personal_configurations(frame,candidate)
    summary=pd.read_csv(out/'mc_summary.csv');effects=pd.read_csv(out/'paired_effects.csv')
    days=pd.DatetimeIndex(frame.index);checked=paired=0
    for cohort,(lo,hi) in COHORTS.items():
        mask=(days>=lo)&(days<hi);idx=np.load(out/f'personal_histories_{cohort}.npy');raw=np.load(out/f'personal_{cohort}.npz')
        assert idx.shape==(1000,252)
        for name,x in plans.items():
            values=x[mask].to_numpy()[idx];equity=values.cumsum(axis=1)
            peak=np.maximum.accumulate(np.c_[np.zeros(len(idx)),equity],axis=1)[:,1:]
            profit,dd=equity[:,-1],(peak-equity).max(axis=1)
            np.testing.assert_allclose(profit,raw[name+'__profit'],rtol=0,atol=1e-6)
            np.testing.assert_allclose(dd,raw[name+'__dd'],rtol=0,atol=1e-6)
            row=summary[(summary.cohort==cohort)&(summary.config==name)].iloc[0]
            np.testing.assert_allclose([row.profit_mean,row.profit_p50,row.dd_p95],
                                       [profit.mean(),np.median(profit),np.percentile(dd,95)],rtol=0,atol=1e-6)
            checked+=1
        for t in effects[effects.cohort==cohort].itertuples():
            p=raw[t.config+'__profit']-raw[t.reference+'__profit'];d=raw[t.config+'__dd']-raw[t.reference+'__dd']
            np.testing.assert_allclose([t.mean_profit_delta,t.mean_dd_delta],[p.mean(),d.mean()],rtol=0,atol=1e-6)
            paired+=1
    result=dict(configurations=20,current_personal_columns=17,saved_MC_rows_reconciled=checked,
                paired_mean_rows_reconciled=paired,new_history_draws=0,new_strategy_replays=0,
                verification='Adapter-author arithmetic checks, not independent source/parity certification')
    if ledger is not None:
        source=pd.read_csv(ledger)
        expected=(native_net_per_unit(source,float(fee))*source.qty).sum()
        np.testing.assert_allclose(candidate.sum(),expected,rtol=0,atol=1e-6)
        key=f'mnq_fee_{fee:.2f}'
        if key in source:
            np.testing.assert_allclose(candidate.sum(),source[key].sum(),rtol=0,atol=1e-6)
        result.update(independent_source_events=len(source),actual_contract_roundtrips=int(source.qty.sum()),
                      weighted_raw_price_fee_totals_reconcile=True,root_weighted_native_column_reconciles=key in source)
    dump(out/'saved_output_checks.json',result)
    return result


def finalize_saved_case(g,ledger,model,fee,prereg,out=None):
    """Final source/quantity/path checks; preserve every statistical output."""
    authorize(prereg,authorized_returns=True)
    out=Path(out or OUT/'personal'/model/f'fee_{fee:.2f}')
    old_reproduction=json.loads((out/'reproduction.json').read_text())
    names=('candidate_daily.csv','mc_summary.csv','paired_effects.csv','historical_summary.csv')
    before={name:S.A.file_sha(out/name) for name in names}
    t=pd.read_csv(ledger,parse_dates=['date','exit_date'])
    paths=validate_candidate_paths(g,t,model,fee,out)
    checks=check_personal_outputs(out,ledger,fee)
    frame=pd.read_csv(out/'baseline_daily17.csv',index_col=0,parse_dates=True)
    candidate=pd.read_csv(out/'candidate_daily.csv',index_col=0,parse_dates=True).iloc[:,0]
    plans,_=personal_configurations(frame,candidate);days=pd.DatetimeIndex(frame.index)
    rows=[]
    for cohort,(lo,hi) in COHORTS.items():
        mask=(days>=lo)&(days<hi)
        for group in (*P.STARTERS,'FULL'):
            base=plans[group+'__BASE'][mask];c=candidate[mask];loss=base<0
            rows.append(dict(cohort=cohort,group=group,correlation=c.corr(base),baseline_loss_days=int(loss.sum()),
                joint_loss_days=int((loss&(c<0)).sum()),candidate_net_on_baseline_loss_days=float(c[loss].sum())))
    pd.DataFrame(rows).to_csv(out/'joint_losses_by_cohort.csv',index=False)
    audit=session_audit(g,t)
    absent=audit[~pd.DatetimeIndex(audit.account_date).isin(days)]
    mappings=[]
    for a in absent.itertuples():
        index=int(days.searchsorted(a.account_date))
        if index>=len(days): raise ValueError('Candidate account date extends beyond published personal calendar')
        source=t.iloc[a.trade_index]
        value=float(((source.exit-source.entry)*source.side*2-fee-.5-.5*(source.kind!=1))*source.qty)
        mappings.append(dict(source_event=int(a.trade_index),actual_account_date=str(pd.Timestamp(a.account_date).date()),
            published_book_date=str(days[index].date()),weighted_native_pnl=value))
    dump(out/'calendar_bookkeeping.json',dict(published_personal_sessions=len(days),source_events=len(t),
        actual_candidate_sessions_absent_from_published_calendar=len(absent),mappings=mappings,
        policy='Retain the published17-leg calendar and its next-session booking rule; all candidate money is retained. No zero baseline return is invented for an absent session.',
        standalone_exit_date_bookkeeping='Owned by root runner; its actual account-date union is separate from this published-portfolio comparison.'))
    for name,h in before.items(): assert S.A.file_sha(out/name)==h
    dump(out/'reproduction.json',dict(preregistration=prereg,ledger=str(ledger),ledger_sha256=S.A.file_sha(ledger),
         script_sha256=S.A.file_sha(__file__),fee=fee,model=model,python=sys.executable,
         script_hash_role='Current metadata-review/reproduction source; not a preserved first-run full-file hash',
         original_run_script_sha256=old_reproduction.get('original_run_script_sha256'),
         original_run_hash_status='First-run full-file hash was not retained separately before metadata finalization; financial CSV hashes remain preserved',
         previous_metadata_review_script_sha256=old_reproduction['script_sha256'],
         metadata_only_review='Session-calendar/quantity/path validation and provenance annotations; no financial return or history draw changed',
         statistical_outputs_unchanged_in_final_checks=True,statistical_output_sha256=before,
         final_checks_no_new_strategy_or_history_draws=True))
    manifest=json.loads((out/'manifest_personal.json').read_text())
    manifest['script_sha256']=S.A.file_sha(__file__)
    manifest['script_hash_role']='Current metadata-review/reproduction source; original first-run full-file hash not separately retained'
    dump(out/'manifest_personal.json',manifest)
    return dict(model=model,fee=fee,checks=checks,candidate_path_status=paths)


def synthetic_checks():
    from types import SimpleNamespace
    g=SimpleNamespace(ts=pd.DatetimeIndex(['2020-01-05','2020-01-06']),trading=np.array([1]),
        o=np.full((2,1440),100.),h=np.full((2,1440),101.),l=np.full((2,1440),99.),c=np.full((2,1440),100.))
    g.l[1,181]=-1000. # A market exit at this open must exclude the later low.
    t=pd.DataFrame([dict(day=0,j0=1022,exit_day=1,j1=181,side=1,entry=100.,exit=110.,kind=2,qty=2,
        pnl=200.,entry_phase='open',exit_phase='open',entry_minute_adverse_px=99.,exit_minute_adverse_px=110.,unknown_held_minutes=0)])
    w,r,q,a=candidate_night_paths(g,t,1.24)
    assert a.cross_calendar_date.all() and a.same_account_session.all() and a.account_window_valid.all()
    assert q[0]==2
    np.testing.assert_allclose(w[0,0],0.)
    np.testing.assert_allclose(w[0,1],-3.74)
    np.testing.assert_allclose(w[0,600:],17.76)
    np.testing.assert_allclose(r[0,600:],17.76)
    # q stays separate so Sunday2 survives integer rounding at half cushion.
    assert np.floor(q[0]*.5)==1 and np.floor(.5)*q[0]==0
    bad=t.copy();bad['j1']=1000
    assert not session_audit(g,bad).account_window_valid.any()
    days=pd.DatetimeIndex(['2020-01-06'])
    n=normalized_ledger(t.loc[t.index.repeat(t.qty)].reset_index(drop=True))
    daily,_,money=marked_candidate_daily(g,n,days,fee=1.24)
    np.testing.assert_allclose(daily,[35.52],rtol=0,atol=1e-9)
    names=set().union(*[set(v) for v in P.STARTERS.values()])|{'MondayLong','LateDayFlow','FC2B','OvernightTick','DualThrust','Kusho','S47','S30'}
    assert len(names)==17
    frame=pd.DataFrame(1.,index=pd.bdate_range('2020-01-01',periods=30),columns=sorted(names))
    candidate=pd.Series(2.,index=frame.index);plans,meta=personal_configurations(frame,candidate)
    assert len(plans)==20 and meta['FULL__REPLACE']['replaced_leg']=='OvernightTick'
    assert meta['A__REPLACE']['replaced_leg']=='OvernightBiasML'
    return dict(midnight_crossing_same_CME_day=True,real_session_break_rejected=True,
        candidate_before_entry_zero=True,market_exit_excludes_later_low=True,Sunday_qty_before_cushion_rounding=True,
        quantity_weighted_personal_costs=True,fixed_20_overlap_configurations=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--fixtures',action='store_true')
    parser.add_argument('--personal',action='store_true')
    parser.add_argument('--ledger',type=Path)
    parser.add_argument('--model')
    parser.add_argument('--prereg')
    parser.add_argument('--fee',type=float,choices=[1.24,1.04],default=1.24)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    if args.prepare:
        m=prepare_sources();print(json.dumps(dict(reference=m['reference'],files=len(m['files']),returns_computed=False),indent=2))
    elif args.fixtures:
        print(json.dumps(synthetic_checks(),indent=2))
    elif args.personal:
        if not args.ledger or not args.model or not args.prereg: parser.error('--personal requires --ledger, --model, --prereg')
        authorize(args.prereg,authorized_returns=True)
        with (ROOT/'scratch_data/g24.pkl').open('rb') as stream: g=pickle.load(stream)
        t=pd.read_csv(args.ledger,parse_dates=['date','exit_date'])
        out=args.out or OUT/'personal'/args.model/f'fee_{args.fee:.2f}'
        result=run_personal(g,t,args.prereg,model=args.model,fee=args.fee,authorized_returns=True,out=out)
        checks=check_personal_outputs(out,args.ledger,args.fee)
        dump(Path(out)/'reproduction.json',dict(preregistration=args.prereg,ledger=str(args.ledger),ledger_sha256=S.A.file_sha(args.ledger),
             script_sha256=S.A.file_sha(__file__),fee=args.fee,model=args.model,python=sys.executable))
        print(json.dumps(checks,indent=2),flush=True)
        print(result['summary'][(result['summary'].cohort=='2023_plus')&result['summary'].config.str.startswith('FULL__')]
              .drop(columns='pieces').to_string(index=False),flush=True)
    else: parser.error('Use metadata --prepare, synthetic --fixtures or the explicitly gated functions')
