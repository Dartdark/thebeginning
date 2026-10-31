"""Unchanged hourly R2 CHoCH: frozen direction/time/delay diagnostics."""
from pathlib import Path
from types import SimpleNamespace
import argparse
import json
import os
import platform
import subprocess
import numpy as np
import pandas as pd
import codex_choch_rr2 as foundation
import codex_choch_filters_execution as execution
from codex_s03_calendar import calendar_status

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_choch_placebos_20261029'
PREREG='2e781a6cb5dbe44eb3782cfe77480915c36648b3'
core=foundation.core
os.environ['NUMBA_CACHE_DIR']=str(OUT/'cache/numba')


def legal_clocks(date):
    return [j for j in range(540,841,60) if foundation.intraday_window(date,j) is not None]


def audited_sessions(g,valid):
    """Future data-completeness analysis restriction, never an entry feature."""
    expected=foundation.repaired.expected_minutes(g);good=valid.ravel()
    rows=[]
    for day,date in enumerate(g.ts):
        date=pd.Timestamp(date)
        if date.year<2018:continue
        clocks=legal_clocks(date)
        if not clocks:continue
        flat=foundation.intraday_window(date,540)
        lo,hi=day*1440+540,day*1440+flat
        missing=np.flatnonzero(expected[lo:hi+1] & ~good[lo:hi+1])+lo
        rows.append(dict(day=day,date=str(date.date()),flat=flat,
                         complete=bool(not len(missing) and good[hi]),
                         missing_expected=len(missing),
                         missing_clock_minutes=','.join(str(int(j%1440)) for j in missing)))
    return pd.DataFrame(rows)


def outcome_catalog(g,valid,events):
    """Finite singleton outcomes; one-position admission is replayed separately."""
    o=g.o.ravel();rows=[];day_grids={};good=valid.ravel()
    for event in events.to_dict('records'):
        original=int(event['signal']);original_side=int(event['side'])
        original_entry=original+2
        original_risk=original_side*(o[original_entry]-float(event['stop']))
        day=original//1440;date=pd.Timestamp(g.ts[day])
        flat=foundation.intraday_window(date,540)
        if day not in day_grids:
            local=SimpleNamespace(D=1,dates=g.dates[day:day+1],ts=g.ts[day:day+1])
            for k in 'ohlc':setattr(local,k,getattr(g,k)[day:day+1])
            day_grids[day]=local
        variants=[(day*1440+clock,original_side) for clock in legal_clocks(date)]
        variants.append((original,-original_side))
        for decision,side in sorted(set(variants)):
            entry=decision+2
            stop=float(o[entry]-side*original_risk)
            request=dict(event,signal=decision,side=side,stop=stop,
                         original_signal=original,original_side=original_side,
                         original_entry_j=original_entry,original_stop=float(event['stop']),
                         original_risk=float(original_risk),deadline_j=day*1440+flat)
            if not good[original_entry] or not np.isfinite(original_risk):
                rows.append(dict(request,outcome_id=len(rows),entry_j=entry,
                    entry_time=date+pd.Timedelta(minutes=decision%1440+2),
                    exit_j=day*1440+flat,exit_time=date+pd.Timedelta(minutes=flat),
                    state='reference_fill_missing',net_mnq=np.nan,gross_mnq=np.nan,
                    stop_first_net=np.nan,commission_mnq=np.nan,slippage_mnq=np.nan,
                    stop_target_collision=False,entry_gap_through=False))
                continue
            # The rule is intraday. A day view calls the same engine while
            # avoiding a multi-million-minute missing-prefix rebuild per event.
            local_request=dict(request,signal=decision-day*1440)
            frame=pd.DataFrame([local_request])
            local=day_grids[day]
            actual=execution.ledger(local,valid[day:day+1],frame).iloc[0].to_dict()
            stress=execution.ledger(local,valid[day:day+1],frame,stop_first=True).iloc[0].to_dict()
            assert actual.get('exit_j',flat)==stress.get('exit_j',flat)
            for result in [actual,stress]:
                for key in ['signal','entry_j','exit_j']:
                    if key in result:result[key]=int(result[key])+day*1440
                if 'exit_j' not in result:result['exit_j']=day*1440+flat
                for key in ['net_mnq','gross_mnq','commission_mnq','slippage_mnq']:
                    result.setdefault(key,np.nan)
            row=dict(actual,outcome_id=len(rows),stop_first_net=stress.get('net_mnq',np.nan))
            rows.append(row)
    result=pd.DataFrame(rows)
    if len(result):
        assert not result.duplicated(['event_id','signal','side']).any()
    return result


def covered_measurements(g,t,name,raw_count,eligible_count,days):
    m,full_daily=foundation.measurements(g,t,name,raw_count,eligible_count)
    d=full_daily.reindex(pd.DatetimeIndex(days))
    assert not d.isna().any() and np.isclose(d.sum(),m['net_total'])
    known=t[t.state.eq('resolved')]
    m.update(core.M.perf(d,known.net_mnq),daily_NW5=core.nw_t(d.to_numpy()),
             daily_clock='Audited complete cash sessions only, including no-event sessions; not zero-filled incomplete days.')
    for side in m['sides']:
        st=t[t.side.eq(side['side'])];sk=known[known.side.eq(side['side'])]
        sd=core.daily_marks(g,st).reindex(d.index)
        side.update(core.M.perf(sd,sk.net_mnq))
    return m,d


def checks():
    dates=pd.date_range('2021-06-28','2021-06-29')
    g=SimpleNamespace(D=len(dates),dates=dates.strftime('%Y%m%d').astype(int).to_numpy(),ts=dates.to_numpy())
    valid=foundation.repaired.expected_minutes(g).reshape(g.D,1440)
    for k in 'oc':setattr(g,k,np.where(valid,100.,np.nan))
    g.h=np.where(valid,101.,np.nan);g.l=np.where(valid,99.,np.nan)
    g.o[0,542]=101.;g.o[0,602]=103.;g.o[0,958]=105.
    event=pd.DataFrame([dict(event_id=0,signal=540,close=100.,side=1,stop=95.,radius=2,broken_pivot=0)])
    catalog=outcome_catalog(g,valid,event)
    original=catalog[(catalog.signal==540)&(catalog.side==1)].iloc[0]
    same=execution.ledger(g,valid,event).iloc[0]
    assert original.entry==same.entry and original.stop==same.stop and original.net_mnq==same.net_mnq
    opposite=catalog[(catalog.signal==540)&(catalog.side==-1)].iloc[0]
    assert opposite.risk==original.risk and opposite.stop==107. and opposite.target==89.
    later=catalog[(catalog.signal==600)&(catalog.side==1)].iloc[0]
    assert later.entry==103. and later.risk==6. and later.stop==97. and later.target==115.
    assert later.original_entry_j<=later.entry_j
    next_day=event.copy();next_day['signal']=1440+540
    second=outcome_catalog(g,valid,next_day)
    second_original=second[(second.signal==1980)&(second.side==1)].iloc[0]
    second_full=execution.ledger(g,valid,next_day).iloc[0]
    assert second_original.entry_j==second_full.entry_j and second_original.exit_j==second_full.exit_j
    assert second_original.net_mnq==second_full.net_mnq and second_original.entry_time==second_full.entry_time
    before=audited_sessions(g,valid)
    assert before.complete.all()
    bad=valid.copy();bad[0,700]=False
    after=audited_sessions(g,bad)
    assert not after.complete.iloc[0] and after.missing_expected.iloc[0]==1
    assert after.complete.iloc[1]
    assert legal_clocks('2024-11-29')==[540,600] and legal_clocks('2021-01-18')==[]
    # Current risk cannot use later scheduled-entry changes.
    risk=catalog.original_risk.copy();g.o[0,602]=110.
    changed=outcome_catalog(g,valid,event)
    np.testing.assert_array_equal(changed.original_risk,risk)
    assert changed.loc[(changed.signal==600)&(changed.side==1),'stop'].iloc[0]==104.
    # A zero/negative original fill risk is a charged immediate round trip.
    gap=event.copy();gap['stop']=102.
    gc=outcome_catalog(g,valid,gap)
    assert (gc.gross_mnq==0).all() and np.allclose(gc.net_mnq,-2.24)
    missing=valid.copy();missing[0,542]=False
    unknown=outcome_catalog(g,missing,event)
    assert unknown.state.eq('reference_fill_missing').all() and unknown.net_mnq.isna().all()
    return dict(original_outcome_parity=True,mirrored_side_risk=True,
                translated_time_risk=True,coverage_is_whole_session=True,
                early_holiday_clocks=True,risk_information_clock=True,
                negative_risk_charged=True,day_view_full_engine_parity=True,unknown_reference_propagated=True)


def run():
    from codex_choch_placebo_paths import simulate
    dest=OUT/'design';dest.mkdir(parents=True,exist_ok=False)
    files=sorted((foundation.SOURCE/'data').glob('NQ_1min_*.csv'))
    assert len(files)==11 and all(int(p.stem[-4:])<=2022 for p in files)
    previous=json.loads((ROOT/'analysis/outputs/codex_choch_rr2_20261028/design/summary.json').read_text())
    hashes={f'data/{p.name}':core.loader.sha(p) for p in files}
    assert hashes==previous['input_hashes']
    core.loader.ROOT=foundation.SOURCE;core.loader.OUT=OUT
    g,valid,audit=core.loader.load_grid(files,'design',dest)
    raw=core.signals(foundation.hourly_bars(g,valid),2)
    raw=raw[raw.signal.map(lambda j:pd.Timestamp(g.ts[int(j)//1440]).year>=2018)].copy()
    eligible=raw[raw.signal.map(lambda j:foundation.intraday_window(pd.Timestamp(g.ts[int(j)//1440]),int(j)%1440) is not None)].copy()
    eligible['event_id']=np.arange(len(eligible))
    eligible.to_csv(dest/'all_eligible_signals.csv',index=False)
    full=execution.ledger(g,valid,eligible)
    old=pd.read_csv(ROOT/'analysis/outputs/codex_choch_filters_20261028/design/corrected_full_baseline_trades.csv')
    for col in ['signal','entry_j','exit_j','net_mnq']:
        np.testing.assert_allclose(full[col].to_numpy(float),old[col].to_numpy(float),equal_nan=True,rtol=1e-12,atol=1e-9)
    assert full.state.tolist()==old.state.tolist()
    full.to_csv(dest/'full_source_baseline_trades.csv',index=False)
    full_m,full_d=foundation.measurements(g,full,'full_source_BASE',len(raw),len(eligible))
    full_d.rename('net_mnq').to_csv(dest/'full_source_baseline_daily.csv',index_label='date')
    sessions=audited_sessions(g,valid);sessions.to_csv(dest/'session_coverage.csv',index=False)
    good_days=set(sessions.loc[sessions.complete,'day'])
    events=eligible[eligible.signal.map(lambda j:int(j)//1440 in good_days)].copy()
    events['source_event_id']=events.event_id;events['event_id']=np.arange(len(events))
    events.to_csv(dest/'covered_eligible_signals.csv',index=False)
    covered=execution.ledger(g,valid,events)
    covered.to_csv(dest/'covered_baseline_trades.csv',index=False)
    covered_days=pd.to_datetime(sessions.loc[sessions.complete,'date'])
    m,d=covered_measurements(g,covered,'covered_BASE',len(raw),len(events),covered_days)
    d.rename('net_mnq').to_csv(dest/'covered_baseline_daily.csv',index_label='date')
    catalog=outcome_catalog(g,valid,events);catalog.to_csv(dest/'outcome_catalog.csv',index=False)
    result=simulate(catalog,events,d,dest/'paths')
    excluded=full[~full.signal.map(lambda j:int(j)//1440 in good_days)]
    excluded.to_csv(dest/'coverage_excluded_full_baseline_trades.csv',index=False)
    summary=dict(study='Hourly R2 CHoCH placebo diagnostics',preregistration_commit=PREREG,
        implementation_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        code_hashes={p.name:core.loader.sha(p) for p in sorted((ROOT/'analysis').glob('codex_choch_placebo*.py'))},
        input_hashes=hashes,source_audit=audit,full_source_baseline_reproduced=True,
        full_source_baseline=full_m,covered_baseline=m,
        coverage=dict(cash_sessions=len(sessions),complete_sessions=int(sessions.complete.sum()),
            incomplete_sessions=int((~sessions.complete).sum()),eligible_signals=len(eligible),
            covered_signals=len(events),excluded_trade_states=excluded.state.value_counts().to_dict(),
            excluded_resolved_net=float(excluded.loc[excluded.state.eq('resolved'),'net_mnq'].sum()),
            note='Future data-completeness analysis restriction, not a live entry filter or new alpha rule.'),
        catalog_states=catalog.state.value_counts().to_dict(),catalog_outcomes=len(catalog),
        nulls=result,design_only=True,validation_run=False,account_benches_run=False,
        definitions=dict(prior_inspected=16,reused_baseline=1,new_fixed_null_questions=3,
                         cumulative_inspected_context=19,random_paths=3000,
                         note='Nulls are diagnostics, not three promoted alpha strategies or3000 independent market histories.'),
        cost=dict(native_contract='MNQ',point_value=2.,commission=1.24,slippage=1.,round_trip=2.24),
        versions=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__),
        final_verdict='Diagnostic only: prior full foundation economic/data gates remain failed; no advancement or new filters.')
    (dest/'summary.json').write_text(json.dumps(core.loader.safe(summary),indent=2,allow_nan=False)+'\n')
    print(json.dumps(core.loader.safe(dict(coverage=summary['coverage'],baseline={k:m[k] for k in ['trades','net_total','trade_t','daily_NW5','max_dd']},nulls=result)),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--design',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    from codex_choch_placebo_paths import synthetic_checks
    tests=dict(controls=checks(),paths=synthetic_checks(),execution=execution.checks(),foundation=foundation.checks())
    (OUT/'checks.json').write_text(json.dumps(core.loader.safe(tests),indent=2)+'\n')
    if args.design:run()
