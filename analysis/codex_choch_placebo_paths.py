"""Frozen CHoCH catalog resampling; no market-data loading or execution.

RT is a noncausal conditional counterfactual. RS and RD use the causal
clocks documented in the preregistration. All paths retain chosen catalog
IDs and admissions; unknown fills are never assigned zero P&L.
"""
from pathlib import Path
import json
import tempfile

import numpy as np
import pandas as pd

import metrics as M
import resampling as R
from codex_hunt_v2_ldf_delta import tstat
from codex_hunt_v2_ldf_delta_design import nw_t

SEED = 20261029
N_PATHS = 1000
NAMES = ('RS', 'RT', 'RD')


def _safe(value):
    if isinstance(value, dict):
        return {str(k): _safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(v) for v in value]
    if isinstance(value, np.generic):
        return _safe(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _cents(values):
    a = np.asarray(values, dtype=float)
    finite = np.isfinite(a)
    rounded = np.rint(a[finite] * 100)
    np.testing.assert_allclose(a[finite] * 100, rounded, rtol=0, atol=1e-6)
    out = np.zeros(a.shape, dtype=np.int64)
    out[finite] = rounded.astype(np.int64)
    return out


def _dd_cents(daily_cents):
    eq = np.r_[np.int64(0), np.cumsum(daily_cents, dtype=np.int64)]
    return int(np.max(np.maximum.accumulate(eq) - eq))


def _stats(daily, trades):
    daily, trades = np.asarray(daily, float), np.asarray(trades, float)
    if not np.isfinite(daily).all() or not np.isfinite(trades).all():
        return dict(net_total=None, max_dd=None, trade_t=None, daily_NW5=None)
    result = M.perf(daily, trades)
    result.update(net_total=float(daily.sum()), max_dd=float(R.max_dd(daily)),
                  trade_t=tstat(trades), daily_NW5=nw_t(daily))
    return _safe(result)


def _prepare(catalog, events, baseline_daily):
    required = ('outcome_id', 'event_id', 'original_signal', 'signal', 'side',
                'original_side', 'entry_j', 'exit_j', 'state', 'net_mnq',
                'commission_mnq', 'slippage_mnq', 'stop_target_collision',
                'stop_first_net', 'entry_time', 'deadline_j')
    absent = [k for k in required if k not in catalog]
    if absent:
        raise ValueError(f'Catalog missing columns: {absent}')
    if not isinstance(baseline_daily, pd.Series):
        raise TypeError('baseline_daily must be the coverage-matched daily Series.')
    c, e = catalog.copy(deep=True).reset_index(drop=True), events.copy(deep=True).reset_index(drop=True)
    days = pd.DatetimeIndex(baseline_daily.index)
    if days.empty or days.has_duplicates or not days.is_monotonic_increasing:
        raise ValueError('Baseline daily dates must be nonempty, unique and sorted.')
    if days.min().year < 2018 or days.max().year > 2022:
        raise ValueError('Only the registered 2018--22 design calendar is allowed.')
    if e.empty:
        raise ValueError('No eligible events supplied.')
    for frame in (c, e):
        frame['event_id'] = frame.event_id.astype(str)
    c['outcome_id'] = c.outcome_id.astype(str)
    if c.outcome_id.duplicated().any() or e.event_id.duplicated().any():
        raise ValueError('Outcome IDs and event IDs must be unique in their tables.')
    if set(c.event_id) != set(e.event_id):
        raise ValueError('Catalog and events must describe exactly the same events.')
    if not np.isin(c.side, [-1, 1]).all() or not np.isin(e.side, [-1, 1]).all():
        raise ValueError('Directions must be +/-1.')
    for k in ('original_signal', 'signal', 'entry_j', 'deadline_j'):
        a = c[k].to_numpy(float)
        if not np.isfinite(a).all() or not np.equal(a, np.floor(a)).all():
            raise ValueError(f'{k} must contain finite integer indices.')
    if not c.entry_j.eq(c.signal + 2).all():
        raise ValueError('Catalog entries must use scheduled signal+2.')
    if not (c.signal.floordiv(1440).eq(c.original_signal.floordiv(1440))).all():
        raise ValueError('Control clocks must stay on their original calendar session.')
    if (c.entry_j >= c.deadline_j).any():
        raise ValueError('Scheduled entries must precede session flatten.')
    if c.duplicated(['event_id', 'signal', 'side']).any():
        raise ValueError('Each event/time/side outcome must be unique.')
    resolved = c.state.eq('resolved').to_numpy()
    if not np.isfinite(c.loc[resolved, ['net_mnq', 'stop_first_net', 'exit_j']].to_numpy(float)).all():
        raise ValueError('Resolved outcomes need finite net, stress net and exit indices.')
    if (c.loc[resolved, 'exit_j'] < c.loc[resolved, 'entry_j']).any():
        raise ValueError('An outcome cannot exit before entry.')
    if (c.loc[resolved, 'exit_j'] > c.loc[resolved, 'deadline_j']).any():
        raise ValueError('An outcome cannot exit after flatten.')
    if not c.loc[resolved, 'commission_mnq'].eq(1.24).all() or not c.loc[resolved, 'slippage_mnq'].eq(1.).all():
        raise ValueError('Catalog must retain the registered native MNQ costs.')
    if (c.loc[resolved, 'stop_first_net'] > c.loc[resolved, 'net_mnq'] + 1e-8).any():
        raise ValueError('Stop-first stress cannot improve a matched outcome.')
    entries = pd.DatetimeIndex(pd.to_datetime(c.entry_time))
    if entries.isna().any():
        raise ValueError('Even unknown fills need their planned entry_time.')
    if not np.array_equal(entries.hour * 60 + entries.minute, c.entry_j.to_numpy(int) % 1440):
        raise ValueError('entry_time and flattened entry_j clocks disagree.')
    epochs = entries - pd.to_timedelta(c.entry_j.to_numpy(int), unit='m')
    if len(pd.DatetimeIndex(epochs).unique()) != 1:
        raise ValueError('All catalog entry indices must use the same grid epoch.')
    positions = days.get_indexer(entries.normalize())
    if (positions < 0).any():
        raise ValueError('A catalog session is absent from the baseline daily calendar.')
    c['_day_position'] = positions
    c['_net_cents'] = _cents(c.net_mnq)
    c['_stress_cents'] = _cents(c.stop_first_net)
    pools = {name: [] for name in NAMES}
    base_choices = []
    for row in e.itertuples(index=False):
        group = c[c.event_id.eq(row.event_id)]
        if not group.original_signal.eq(row.signal).all() or not group.original_side.eq(row.side).all():
            raise ValueError('Catalog original metadata disagrees with events.')
        original = group[group.signal.eq(row.signal)]
        rs = original.sort_values('side')
        if len(rs) != 2 or rs.side.tolist() != [-1, 1]:
            raise ValueError('RS needs exactly both sides at the original signal.')
        rt = group[group.side.eq(row.side)].sort_values('signal')
        clocks = (rt.signal % 1440).tolist()
        if clocks not in ([540, 600], [540, 600, 660, 720, 780, 840]):
            raise ValueError('RT needs every normal or early legal decision clock.')
        rd = rt[rt.signal.ge(row.signal)]
        base = rt[rt.signal.eq(row.signal)]
        if len(base) != 1 or rd.empty:
            raise ValueError('Every event needs its unchanged baseline outcome.')
        base_choices.append(int(base.index[0]))
        for name, frame in [('RS', rs), ('RT', rt), ('RD', rd)]:
            pools[name].append(frame.index.to_numpy(dtype=np.int64))
    return c, e, days, pools, np.asarray(base_choices, np.int64)


def _path(c, e, choices, day_count):
    rows = c.iloc[choices]
    # Original signals are unique in the registered engine; event ID remains
    # the deterministic final tie-breaker for general catalog reconstruction.
    ids = e.event_id.to_numpy()
    numeric_ids = pd.to_numeric(e.event_id, errors='coerce')
    tie = numeric_ids.to_numpy() if numeric_ids.notna().all() else ids
    entries = rows.entry_j.to_numpy(dtype=np.int64)
    exits = rows.exit_j.to_numpy(dtype=float)
    states = rows.state.to_numpy()
    deadlines = rows.deadline_j.to_numpy(dtype=np.int64)
    order = np.lexsort((tie, rows.original_signal.to_numpy(), entries))
    admitted = np.zeros(len(e), dtype=bool)
    blocked = -1
    for column in order:
        if entries[column] <= blocked:
            continue
        admitted[column] = True
        if states[column] == 'missing_entry' or not np.isfinite(exits[column]):
            blocked = int(deadlines[column])
        else:
            blocked = int(exits[column])
    selected = rows[admitted]
    known = selected[selected.state.eq('resolved')]
    unknown = selected[~selected.state.eq('resolved')]
    cents = np.zeros(day_count, np.int64)
    stress_cents = np.zeros(day_count, np.int64)
    np.add.at(cents, known._day_position.to_numpy(int), known._net_cents.to_numpy(np.int64))
    np.add.at(stress_cents, known._day_position.to_numpy(int), known._stress_cents.to_numpy(np.int64))
    daily, stress_daily = cents.astype(float) / 100, stress_cents.astype(float) / 100
    if len(unknown):
        unknown_days = unknown._day_position.to_numpy(int)
        daily[unknown_days] = np.nan
        stress_daily[unknown_days] = np.nan
    complete = not len(unknown)
    values, stress_values = known.net_mnq.to_numpy(float), known.stop_first_net.to_numpy(float)
    stats = _stats(daily, values)
    stress_stats = _stats(stress_daily, stress_values)
    delta = selected.signal.to_numpy() - selected.original_signal.to_numpy()
    attempts_delta = rows.signal.to_numpy() - rows.original_signal.to_numpy()
    minutes = known.exit_j.to_numpy(float) - known.entry_j.to_numpy(float)
    total_cents = int(cents.sum())
    record = dict(attempted=len(e), admitted=len(selected), blocked=len(e)-len(selected),
        known_trades=len(known), unknown_trades=len(unknown), complete=complete,
        unknown_states=json.dumps(unknown.state.value_counts().to_dict(), sort_keys=True),
        known_net_subtotal=total_cents/100, net_cents=total_cents if complete else np.nan,
        dd_cents=_dd_cents(cents) if complete else np.nan,
        long_trades=int(selected.side.eq(1).sum()), short_trades=int(selected.side.eq(-1).sum()),
        exposure_minutes=float(minutes.sum()) if complete else np.nan,
        known_exposure_minutes=float(minutes.sum()),
        long_minutes_known=float(minutes[known.side.eq(1)].sum()),
        short_minutes_known=float(minutes[known.side.eq(-1)].sum()),
        earlier_attempts=int((attempts_delta<0).sum()), equal_attempts=int((attempts_delta==0).sum()),
        later_attempts=int((attempts_delta>0).sum()),
        earlier_admitted=int((delta<0).sum()), equal_admitted=int((delta==0).sum()),
        later_admitted=int((delta>0).sum()),
        collision_count=int(known.stop_target_collision.fillna(False).sum()),
        commission_known=float(known.commission_mnq.sum()), slippage_known=float(known.slippage_mnq.sum()),
        extra_cost_net=(total_cents-224*len(known))/100 if complete else np.nan,
        stop_first_net=float(stress_cents.sum())/100 if complete else np.nan,
        stop_first_dd_cents=_dd_cents(stress_cents) if complete else np.nan,
        stop_first_net_cents=int(stress_cents.sum()) if complete else np.nan,
        **stats)
    return admitted, daily, stress_daily, record, stats, stress_stats


def _ranks(frame, base_net, base_dd, net_column='net_cents', dd_column='dd_cents'):
    valid = frame.complete.to_numpy(bool)
    unknown = int((~valid).sum())
    if base_net is None or base_dd is None:
        result = dict(complete_paths=int(valid.sum()), unknown_paths=unknown,
                      baseline_unknown=True, ties_profit=None, ties_dd=None,
                      ties_joint=None)
        for name in ('profit', 'dd', 'joint'):
            result['p_'+name] = None
            result['p_'+name+'_bounds'] = [1/(N_PATHS+1), 1.]
            result['p_'+name+'_19'] = None
            result['p_'+name+'_19_bounds'] = [19/(N_PATHS+1), 1.]
            result['baseline_'+name+'_rank_bounds'] = [1, N_PATHS+1]
        return result
    profit = frame.loc[valid, net_column].to_numpy(np.int64)
    dd = frame.loc[valid, dd_column].to_numpy(np.int64)
    conditions = dict(profit=profit>=base_net, dd=dd<=base_dd,
                      joint=(profit>=base_net)&(dd<=base_dd))
    result = dict(complete_paths=int(valid.sum()), unknown_paths=unknown,
                  ties_profit=int((profit==base_net).sum()), ties_dd=int((dd==base_dd).sum()),
                  ties_joint=int(((profit==base_net)&(dd==base_dd)).sum()))
    for name, condition in conditions.items():
        numerator = 1 + int(condition.sum())
        bounds = [numerator/(N_PATHS+1), (numerator+unknown)/(N_PATHS+1)]
        result['p_'+name] = bounds[0] if not unknown else None
        result['p_'+name+'_bounds'] = bounds
        result['p_'+name+'_19'] = min(1.,19*bounds[0]) if not unknown else None
        result['p_'+name+'_19_bounds'] = [min(1.,19*x) for x in bounds]
        result['baseline_'+name+'_rank_bounds'] = [numerator,numerator+unknown]
    return result


def simulate(catalog, events, baseline_daily, outdir):
    """Save all 3,000 choices/admissions/paths from an immutable outcome catalog."""
    c,e,days,pools,base_choices = _prepare(catalog,events,baseline_daily)
    out = Path(outdir);out.mkdir(parents=True,exist_ok=False)
    base_mask, base_daily, base_stress_daily, base_record, base_stats, base_stress = _path(c,e,base_choices,len(days))
    supplied = baseline_daily.to_numpy(float)
    known = np.isfinite(base_daily)
    np.testing.assert_allclose(base_daily[known],supplied[known],rtol=0,atol=1e-7,
                               err_msg='Catalog original-clock admissions do not reconstruct BASE daily.')
    base_complete=bool(base_record['complete'])
    if base_complete and not np.isfinite(supplied).all():
        raise ValueError('A complete catalog BASE cannot match an unknown supplied daily series.')
    summary = dict(seed=SEED,paths_per_null=N_PATHS,event_count=len(e),
        baseline_complete=base_complete,baseline=base_stats,baseline_stop_first=base_stress,
        baseline_path=base_record,baseline_daily_verified=True,
        statistic_basis='Native-cost total net; exact integer cents and ties; 19p is limited family context.',
        RT_scope='Noncausal same-session risk/date-matched counterfactual; not a promotion placebo.')
    pd.DataFrame(dict(event_id=e.event_id,chosen_outcome_id=c.outcome_id.iloc[base_choices].to_numpy(),
                      admitted=base_mask)).to_csv(out/'baseline_catalog_admissions.csv',index=False)
    children=np.random.SeedSequence(SEED).spawn(3)
    for name, child in zip(NAMES,children):
        directory=out/name;directory.mkdir()
        rng=np.random.default_rng(child)
        lengths=np.array([len(pool) for pool in pools[name]],dtype=np.int64)
        draws=rng.integers(0,lengths,size=(N_PATHS,len(e)))
        choices=np.empty_like(draws)
        for column,pool in enumerate(pools[name]):choices[:,column]=pool[draws[:,column]]
        masks=np.zeros((N_PATHS,len(e)),bool)
        daily_paths=np.empty((N_PATHS,len(days)),float);stress_paths=daily_paths.copy()
        records=[]
        for trial in range(N_PATHS):
            admitted,daily,stress,record,_,_=_path(c,e,choices[trial],len(days))
            masks[trial]=admitted;daily_paths[trial]=daily;stress_paths[trial]=stress
            records.append(dict(trial=trial+1,**record))
        frame=pd.DataFrame(records)
        frame.to_csv(directory/'path_summary.csv',index=False)
        outcome_ids=c.outcome_id.to_numpy(dtype=str)[choices]
        np.savez_compressed(directory/'paths.npz',chosen_outcome_ids=outcome_ids,
            admitted_mask=masks,daily_paths=daily_paths,stop_first_daily_paths=stress_paths,
            event_ids=e.event_id.to_numpy(dtype=str),dates=days.strftime('%Y-%m-%d').to_numpy(dtype='U10'),
            trials=np.arange(1,N_PATHS+1),seed=np.array(SEED),spawn_key=np.array(child.spawn_key),
            null_name=np.array(name))
        bnet=int(base_record['net_cents']) if base_complete else None
        bdd=int(base_record['dd_cents']) if base_complete else None
        ranks=_ranks(frame,bnet,bdd)
        stress_ranks=_ranks(frame,int(base_record['stop_first_net_cents']) if base_complete else None,
                            int(base_record['stop_first_dd_cents']) if base_complete else None,
                            'stop_first_net_cents','stop_first_dd_cents')
        quantiles={}
        for key in ('net_total','admitted','known_exposure_minutes','exposure_minutes','long_trades',
                    'short_trades','earlier_admitted','equal_admitted','later_admitted','extra_cost_net','stop_first_net'):
            values=frame[key].dropna().to_numpy(float)
            quantiles[key]={str(q):float(np.quantile(values,q/100)) if len(values) else None for q in (5,50,95)}
        summary[name]=dict(**ranks,quantiles=quantiles,stop_first=stress_ranks,
            unknown_admitted_states={state:int(sum(json.loads(x).get(state,0) for x in frame.unknown_states))
                for state in sorted(set().union(*(json.loads(x) for x in frame.unknown_states)))},
            artifacts=dict(path_summary=str(directory/'path_summary.csv'),paths=str(directory/'paths.npz')))
    summary=_safe(summary)
    with (out/'summary.json').open('x') as handle:
        json.dump(summary,handle,indent=2,allow_nan=False);handle.write('\n')
    return summary


def synthetic_checks():
    """Invented catalog only; deterministic admissions, ties and unknown bounds."""
    dates=pd.DatetimeIndex(['2018-01-02','2018-01-03'])
    events=pd.DataFrame(dict(event_id=[0,1,2],signal=[540,600,1440+540],side=[1,-1,1]))
    rows=[]
    for e in events.itertuples(index=False):
        day=int(e.signal)//1440
        for clock in (540,600,660,720,780,840):
            for side in ([-1,1] if clock==int(e.signal)%1440 else [e.side]):
                signal=day*1440+clock;entry=signal+2
                net=10.01 if side==e.side else -5.24
                # First request remains open through the second signal.
                exit_j=entry+70
                rows.append(dict(outcome_id=f'{e.event_id}_{clock}_{side}',event_id=e.event_id,
                    original_signal=e.signal,signal=signal,side=side,original_side=e.side,
                    entry_j=entry,exit_j=exit_j,state='resolved',net_mnq=net,
                    commission_mnq=1.24,slippage_mnq=1.,stop_target_collision=False,
                    stop_first_net=net,entry_time=dates[day]+pd.Timedelta(minutes=clock+2),
                    deadline_j=day*1440+958))
    catalog=pd.DataFrame(rows);frozen=catalog.copy(deep=True)
    baseline=pd.Series([10.01,10.01],index=dates)
    with tempfile.TemporaryDirectory(prefix='codex_choch_paths_') as directory:
        result=simulate(catalog,events,baseline,Path(directory)/'all')
        assert result['baseline_complete'] and result['baseline_path']['admitted']==2
        for name in NAMES:
            with np.load(Path(directory)/'all'/name/'paths.npz',allow_pickle=False) as z:
                assert z['chosen_outcome_ids'].shape==(N_PATHS,3)
                assert z['admitted_mask'].shape==(N_PATHS,3)
                assert z['daily_paths'].shape==(N_PATHS,2)
                assert np.array_equal(z['daily_paths'],z['stop_first_daily_paths'])
                lookup=catalog.set_index('outcome_id')
                for trial in (0,1,999):
                    chosen=lookup.loc[z['chosen_outcome_ids'][trial]]
                    admitted=chosen[z['admitted_mask'][trial]]
                    assert np.isclose(admitted.net_mnq.sum(),z['daily_paths'][trial].sum())
                    if name=='RS':assert chosen.signal.eq(chosen.original_signal).all()
                    if name=='RD':assert chosen.signal.ge(chosen.original_signal).all()
            q=result[name];assert q['unknown_paths']==0 and q['p_profit_bounds']==[q['p_profit']]*2
            assert q['p_profit_19']==min(1.,19*q['p_profit'])
    pd.testing.assert_frame_equal(catalog,frozen)
    sample=pd.DataFrame(dict(complete=[True]*N_PATHS,net_cents=[2002]*N_PATHS,dd_cents=[0]*N_PATHS))
    ranks=_ranks(sample,2002,0)
    assert ranks['p_profit']==ranks['p_dd']==ranks['p_joint']==1.
    sample.loc[0,'complete']=False
    ranks=_ranks(sample,2002,0)
    assert ranks['p_profit'] is None and ranks['p_profit_bounds']==[1000/1001,1.]
    c,e,days,pools,choices=_prepare(catalog,events,baseline)
    c.loc[choices[0],['state','exit_j','net_mnq','stop_first_net']]=['missing_entry',np.nan,np.nan,np.nan]
    admitted,daily,stress,record,_,_=_path(c,e,choices,len(days))
    assert admitted.tolist()==[True,False,True] and not record['complete']
    assert record['unknown_trades']==1 and np.isnan(daily[0]) and np.isnan(stress[0])
    assert daily[1]==10.01
    return dict(immutable_catalog=True,baseline_reconstructed=True,one_position=True,
        all_choices_and_masks_saved=True,daily_reconstruction=True,legal_RS_RD_clocks=True,
        exact_cents_ties=True,plus_one_and_19p=True,unknown_bounds=True,missing_entry_blocks=True,
        market_data_loaded=False)


if __name__=='__main__':
    print(synthetic_checks())
