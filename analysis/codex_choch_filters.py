"""Five preregistered hourly R2 CHoCH filter designs. Research only."""
from pathlib import Path
from types import SimpleNamespace
import argparse
import json
import os
import platform
import subprocess
import numpy as np
import pandas as pd
import codex_choch_rr2 as base
import codex_choch4h as core
import codex_choch4h_corrected_data as repaired
from codex_s03_calendar import calendar_status

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_choch_filters_20261028'
PREREG = '1898b1f597a3ef526ced52778e9a48d12b900fbf'
NAMES = ['BASE', 'F1', 'F1_5', 'A4', 'F1_A4']
os.environ['NUMBA_CACHE_DIR'] = str(OUT / 'cache/numba')


def structure_states(bars, radius=2):
    """Instrument the frozen core algorithm; include reset rows for causal as-of."""
    history, highs, lows, events, states = [], [], [], [], []
    trend, previous, consumed = 0, None, set()
    for b in bars:
        if not b['valid']:
            history, highs, lows, trend, previous = [], [], [], 0, None
            states.append(dict(end=b['end'], state=0, known=False))
            continue
        history.append(b)
        changed = False
        if len(history) >= 2*radius+1:
            window = history[-(2*radius+1):]
            pivot, others = window[radius], window[:radius]+window[radius+1:]
            if all(pivot['high'] > x['high'] for x in others):
                highs.append((pivot['end'], pivot['high'])); changed = True
            if all(pivot['low'] < x['low'] for x in others):
                lows.append((pivot['end'], pivot['low'])); changed = True
        if changed and len(highs)>=2 and len(lows)>=2:
            if highs[-1][1]>highs[-2][1] and lows[-1][1]>lows[-2][1]:
                trend = 1
            elif highs[-1][1]<highs[-2][1] and lows[-1][1]<lows[-2][1]:
                trend = -1
        side = 0
        if previous is not None and highs and lows:
            if trend==1 and previous>=lows[-1][1] and b['close']<lows[-1][1]:
                side, stop, broken = -1, highs[-1][1], lows[-1][0]
            elif trend==-1 and previous<=highs[-1][1] and b['close']>highs[-1][1]:
                side, stop, broken = 1, lows[-1][1], highs[-1][0]
            if side and (side,broken) not in consumed:
                events.append(dict(signal=b['end'],close=b['close'],side=side,
                                   stop=stop,broken_pivot=broken,radius=radius))
                consumed.add((side,broken)); trend=side
        previous=b['close']
        states.append(dict(end=b['end'],state=trend,known=len(highs)>=2 and len(lows)>=2))
    return pd.DataFrame(states), pd.DataFrame(events,columns=['signal','close','side','stop','broken_pivot','radius'])


def alignment(states, decisions):
    ends = states.end.to_numpy()
    offsets = np.searchsorted(ends,np.asarray(decisions),side='right')-1
    return [(np.nan,np.nan,False) if i<0 else
            (int(ends[i]),int(states.state.iloc[i]),bool(states.known.iloc[i])) for i in offsets]


def range_features(g, valid, events):
    """Prior20 calendar sessions, never replace a missing window with an older one."""
    expected = repaired.expected_minutes(g)
    good=valid.ravel(); h,l,o=(getattr(g,k).ravel() for k in 'hlo')
    normal=[i for i,d in enumerate(g.ts) if calendar_status(pd.Timestamp(d))['kind']=='normal']
    normal=np.array(normal,dtype=int)
    out=[]
    for e in events.to_dict('records'):
        j=int(e['signal']); day,clock=divmod(j,1440)
        flat=base.intraday_window(pd.Timestamp(g.ts[day]),clock)
        prior=normal[normal<day][-20:]
        ranges=[]; complete=len(prior)==20
        for d in prior:
            start,end=int(d)*1440+clock+1,int(d)*1440+flat
            mask=expected[start:end]
            if not mask.any() or not (good[start:end] | ~mask).all() or not good[end]:
                complete=False
                continue
            hi=max(float(h[start:end][mask].max()),float(o[end]))
            lo=min(float(l[start:end][mask].min()),float(o[end]))
            ranges.append(hi-lo)
        med=float(np.median(ranges)) if complete else np.nan
        risk=int(e['side'])*(float(e['close'])-float(e['stop']))
        known=bool(complete and med>0 and risk>0)
        out.append(dict(signal=j,decision_target_points=2*risk,
                        historical_range_median=med,range_known=known,
                        prior_calendar_sessions=len(prior),complete_windows=len(ranges),
                        history_first_day=int(prior[0]) if len(prior) else -1,
                        history_last_day=int(prior[-1]) if len(prior) else -1,
                        target_range_ratio=2*risk/med if known else np.nan))
    return pd.DataFrame(out)


def features(g,valid,eligible):
    states,state_events=structure_states(core.four_hour_bars(g,valid))
    pd.testing.assert_frame_equal(state_events,core.signals(core.four_hour_bars(g,valid),2))
    f=eligible.merge(range_features(g,valid,eligible),on='signal',validate='one_to_one')
    joined=alignment(states,f.signal.to_numpy())
    f['h4_end']=[x[0] for x in joined]
    f['h4_state']=[x[1] for x in joined]
    f['alignment_known']=[x[2] for x in joined]
    f['common_known']=f.range_known & f.alignment_known
    f['BASE']=f.common_known
    f['F1']=f.common_known & f.target_range_ratio.le(1.)
    f['F1_5']=f.common_known & f.target_range_ratio.le(1.5)
    f['A4']=f.common_known & f.h4_state.eq(f.side)
    f['F1_A4']=f.F1 & f.A4
    return f,states


def checks():
    # Prefix, confirmation and mirror parity against original signal algorithm.
    rng=np.random.default_rng(17)
    price=np.cumsum(rng.normal(size=160))+100
    bars=[dict(end=i*240,valid=True,high=float(p+1),low=float(p-1),close=float(p)) for i,p in enumerate(price)]
    bars[80]['valid']=False
    states,ev=structure_states(bars)
    pd.testing.assert_frame_equal(ev,core.signals(bars,2))
    assert len(ev)>0
    for n in [30,60,80,81,110,160]:
        s,e=structure_states(bars[:n])
        pd.testing.assert_frame_equal(s,states.iloc[:n].reset_index(drop=True))
        pd.testing.assert_frame_equal(e,ev[ev.signal<=bars[n-1]['end']].reset_index(drop=True),check_dtype=False)
    assert not states.known.iloc[80] and states.state.iloc[80]==0
    got=alignment(states,[states.end.iloc[60]-1,states.end.iloc[60]])
    assert got[0][0]==states.end.iloc[59] and got[1][0]==states.end.iloc[60]
    mirror=[dict(b,high=-b['low'],low=-b['high'],close=-b['close']) for b in bars]
    ms,me=structure_states(mirror)
    assert np.array_equal(ms.state.to_numpy(),-states.state.to_numpy())
    # Range window clock, exact previous20 normal sessions and current-day mutation.
    dates=pd.date_range('2021-03-01','2021-04-16')
    g=SimpleNamespace(D=len(dates),ts=dates.to_numpy(),dates=dates.strftime('%Y%m%d').astype(int).to_numpy())
    for k in 'ohlc':setattr(g,k,np.full((g.D,1440),100.))
    g.h[:]=110.;g.l[:]=90.
    v=repaired.expected_minutes(g).reshape(g.D,1440)
    day=g.D-1;signal=day*1440+540
    events=pd.DataFrame([dict(signal=signal,side=1,close=100.,stop=95.)])
    a=range_features(g,v,events)
    assert a.range_known.iloc[0] and a.historical_range_median.iloc[0]==20.
    g.h[day]=10000.;g.l[day]=-10000.;g.o[day,542]=20000.
    pd.testing.assert_frame_equal(a,range_features(g,v,events))
    # Flatten open included, later high on flatten minute excluded.
    yesterday=int(a.history_last_day.iloc[0])
    g.h[yesterday,958]=999999.
    pd.testing.assert_frame_equal(a,range_features(g,v,events))
    broken=v.copy();broken[yesterday,541]=False
    b=range_features(g,broken,events)
    assert not b.range_known.iloc[0] and b.complete_windows.iloc[0]==19
    short=range_features(g,v,pd.DataFrame([dict(signal=10*1440+540,side=1,close=100.,stop=95.)]))
    assert not short.range_known.iloc[0]
    return dict(structure_core_parity=True,prefix_invariance=True,mirror=True,
                reset_and_asof_confirmation=True,prior20_range_clock=True,
                future_fill_and_range_invariance=True,missing_history_not_replaced=True)


def stamped(g,t):
    t=t.copy();t['trade_id']=['s'+str(int(s)) for s in t.signal]
    return t


def run():
    from codex_choch_filters_execution import ledger
    from codex_choch_filters_subsets import evaluate
    dest=OUT/'design';dest.mkdir(parents=True,exist_ok=False)
    files=sorted((base.SOURCE/'data').glob('NQ_1min_*.csv'))
    assert len(files)==11 and all(int(p.stem[-4:])<=2022 for p in files)
    previous=json.loads((ROOT/'analysis/outputs/codex_choch_rr2_20261028/design/summary.json').read_text())
    hashes={f'data/{p.name}':core.loader.sha(p) for p in files}
    assert hashes==previous['input_hashes']
    core.loader.ROOT=base.SOURCE;core.loader.OUT=OUT
    g,valid,audit=core.loader.load_grid(files,'design',dest)
    raw=core.signals(base.hourly_bars(g,valid),2)
    raw=raw[raw.signal.map(lambda j:pd.Timestamp(g.ts[int(j)//1440]).year>=2018)].copy()
    eligible=raw[raw.signal.map(lambda j:base.intraday_window(pd.Timestamp(g.ts[int(j)//1440]),int(j)%1440) is not None)].copy()
    old=base.ledger(g,valid,eligible,'executable',True)
    archived=pd.read_csv(ROOT/'analysis/outputs/codex_choch_rr2_20261028/design/h1_r2_executable_trades.csv')
    for col in ['signal','state','entry_j','exit_j','net_mnq']:
        if col=='state':assert old[col].tolist()==archived[col].tolist()
        else:np.testing.assert_allclose(old[col].to_numpy(float),archived[col].to_numpy(float),equal_nan=True,rtol=1e-12,atol=1e-9)
    stamped(g,old).to_csv(dest/'original_full_baseline_trades.csv',index=False)
    f,states=features(g,valid,eligible)
    f.to_csv(dest/'signal_features.csv',index=False);states.to_csv(dest/'h4_states.csv',index=False)
    summary=dict(preregistration_commit=PREREG,design_only=True,validation_run=False,
                 implementation_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                 code_hashes={p.name:core.loader.sha(p) for p in sorted((ROOT/'analysis').glob('codex_choch_filters*.py'))},
                 input_hashes=hashes,source_audit=audit,baseline_reproduced=True,
                 configurations=5,new_active_filters=4,prior_structural_configurations=6,
                 prior_economic_definitions=12,cumulative_economic_definitions=16,
                 accounting_note='BASE reused, four active filters; coverage controls, execution correction and stresses retained separately; prior12 definitions include ideal-close benchmarks.',
                 raw_signals=len(raw),eligible_signals=len(eligible),common_signals=int(f.common_known.sum()),
                 range_unknown=int((~f.range_known).sum()),alignment_unknown=int((~f.alignment_known).sum()),
                 costs=dict(commission_roundtrip=1.24,slippage_roundtrip=1.,total_roundtrip=2.24,native_contract='MNQ'),
                 versions=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__),
                 seed=20261028,models=[],references=[])
    full=stamped(g,ledger(g,valid,eligible))
    full.to_csv(dest/'corrected_full_baseline_trades.csv',index=False)
    for name,t in [('original_full_baseline',old),('corrected_full_baseline',full)]:
        m,d=base.measurements(g,t,name,len(raw),len(eligible));summary['references'].append(m)
        d.rename('net_mnq').to_csv(dest/f'{name}_daily.csv',index_label='date')
    unknown_ids=set(f.loc[~f.common_known,'signal'])
    exclusions=full[full.signal.isin(unknown_ids)]
    exclusions.to_csv(dest/'unknown_feature_full_baseline_trades.csv',index=False)
    summary['coverage_exclusions']=dict(full_baseline_states=exclusions.state.value_counts().to_dict(),
        resolved_net=float(exclusions.loc[exclusions.state.eq('resolved'),'net_mnq'].sum()),
        note='Coverage/warmup exclusion, not predictive filter alpha; rerun opportunity sets may differ.')
    ledgers,dailies={},{}
    for name in NAMES:
        selected=f[f[name]].copy()
        t=stamped(g,ledger(g,valid,selected));ledgers[name]=t
        t.to_csv(dest/f'{name}_trades.csv',index=False)
        m,d=base.measurements(g,t,name,len(raw),len(selected));dailies[name]=d
        d.rename('net_mnq').to_csv(dest/f'{name}_daily.csv',index_label='date')
        stress=stamped(g,ledger(g,valid,selected,stop_first=True))
        stress.to_csv(dest/f'{name}_stop_first_trades.csv',index=False)
        sm,sd=base.measurements(g,stress,name+'_stop_first',len(raw),len(selected))
        sd.rename('net_mnq').to_csv(dest/f'{name}_stop_first_daily.csv',index_label='date')
        m['stop_first']=sm
        m['extra_cost_net']=float(m['net_total']-2.24*len(t[t.state.eq('resolved')]))
        m['breakeven_extra_cost_per_trade']=float(m['net_total']/max(1,len(t[t.state.eq('resolved')])))
        m['collision_count']=int(t.stop_target_collision.fillna(False).sum())
        m['entry_gap_stop_count']=int(t.entry_gap_through.fillna(False).sum())
        summary['models'].append(m)
    bt=ledgers['BASE'];resolved=bt[bt.state.eq('resolved')].copy().reset_index(drop=True)
    lookup=f.set_index('signal')
    masks={name:resolved.signal.map(lookup[name]).to_numpy(bool) for name in NAMES[1:]}
    subset_result=evaluate(resolved,masks,dailies['BASE'],dest/'matched_subsets')
    diagnostics=subset_result['filters']
    summary['filter_diagnostics']=diagnostics
    summary['subset_base']=subset_result['base']
    summary['subset_daily_verified']=subset_result['baseline_daily_verified']
    for m in summary['models']:
        name=m['model']
        if name=='BASE':m['filter_design_pass']=False;continue
        q=diagnostics[name]
        m['filter_design_pass']=bool(m['design_pass'] and q['kept_net']>q['base_net'] and
            q['removed_net']<0 and q['p_profit']<=.05 and q['p_dd']<=.05 and
            m['net_total']>summary['models'][0]['net_total'] and
            m['max_dd']<=summary['models'][0]['max_dd'] and
            m['extra_cost_net']>0 and m['stop_first']['net_total']>0)
    summary['survivors']=[m['model'] for m in summary['models'] if m['filter_design_pass']]
    summary['design_dates']=dict(start=str(dailies['BASE'].index.min().date()),end=str(dailies['BASE'].index.max().date()))
    (dest/'summary.json').write_text(json.dumps(core.loader.safe(summary),indent=2,allow_nan=False)+'\n')
    compact={name:{k:q[k] for k in ['kept_net','base_net','removed_net','p_profit','p_dd','p_joint']} for name,q in diagnostics.items()}
    print(json.dumps(core.loader.safe(dict(models=[{k:m[k] for k in ['model','trades','net_total','trade_t','daily_NW5','max_dd','unresolved','filter_design_pass']} for m in summary['models']],diagnostics=compact,survivors=summary['survivors'])),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--design',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    from codex_choch_filters_execution import checks as execution_checks
    from codex_choch_filters_subsets import checks as subset_checks
    result=dict(features=checks(),execution=execution_checks(),subsets=subset_checks(),foundation=base.checks())
    (OUT/'checks.json').write_text(json.dumps(core.loader.safe(result),indent=2)+'\n')
    if args.design:run()
