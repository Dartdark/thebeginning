"""Preregistered monthly VRP feasibility proxy. Offline; no trading connections.

Audit computes lagged features and data coverage only. Return modes require a
committed exact implementation and frozen preregistration. No parameter options.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np
import pandas as pd

from grid24 import Grid24
from roll_adjust import roll_jumps
import metrics as M
from codex_s03_calendar import calendar_status, synthetic_checks as calendar_checks
from codex_hunt_v2_ldf_delta import tstat
from codex_hunt_v2_ldf_delta_design import nw_t

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_vrp_monthly_proxy_20261029'
PLAN = 'agents/codex/plans/vrp_monthly_proxy_20261029.md'
PREREG = '1f444c6'
NAMES = ['P', 'H', 'B', 'I', 'R']
COST, STRESS = 3.74, 11.24
SEED = 1783624
TARGET_MONTHS = (1, 2, 4, 5, 7, 8, 10, 11)
PRIMARY_ONLY = False
AMENDMENT = 'agents/codex/research/vrp_monthly_proxy_pre_return_amendment.md'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe(x):
    if isinstance(x, dict): return {str(k): safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [safe(v) for v in x]
    if isinstance(x, np.generic): return safe(x.item())
    if isinstance(x, float) and not np.isfinite(x): return None
    return x


def dump(path, x):
    Path(path).write_text(json.dumps(safe(x), indent=2, allow_nan=False) + '\n')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def verify():
    assert git('branch', '--show-current') == 'codex/work'
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', PREREG, 'HEAD'], cwd=ROOT)
    assert subprocess.check_output(['git', 'show', PREREG + ':' + PLAN], cwd=ROOT) == (ROOT / PLAN).read_bytes()
    rel = str(Path(__file__).relative_to(ROOT))
    assert subprocess.check_output(['git', 'show', 'HEAD:' + rel], cwd=ROOT) == Path(__file__).read_bytes()
    if PRIMARY_ONLY:
        assert subprocess.check_output(['git', 'show', 'HEAD:' + AMENDMENT], cwd=ROOT) == (ROOT/AMENDMENT).read_bytes()


def first_cash(month):
    for d in pd.date_range(month.start_time, month.end_time, freq='D'):
        if calendar_status(d)['kind'] in ('normal', 'early'):
            return d
    raise ValueError('No cash session')


def cash_dates(a, b):
    return [d for d in pd.date_range(a, b, freq='D')
            if calendar_status(d)['kind'] in ('normal', 'early')]


def signal_flags(frame):
    """No fitted values; trailing medians exclude the current feature month."""
    f = frame.copy()
    for key in ['vrp', 'iv', 'rv']:
        f[key + '_median12'] = f[key].shift(1).rolling(12, min_periods=12).median()
    f['common_known'] = f[['iv', 'rv', 'vrp_median12', 'iv_median12', 'rv_median12']].notna().all(axis=1)
    f['P'] = f.vrp > 0
    f['H'] = f.vrp > f.vrp_median12
    f['B'] = True
    f['I'] = f.iv > f.iv_median12
    f['R'] = f.rv < f.rv_median12
    return f


def feature_grid(phase):
    years = range(2017, 2023) if phase == 'design' else range(2022, 2027)
    directory = OUT / 'cache' / phase
    directory.mkdir(parents=True, exist_ok=True)
    paths = [ROOT / f'data/ES_1min_{y}.csv' for y in years]
    for p in paths:
        link = directory / p.name
        if not link.exists(): link.symlink_to(p)
        assert link.resolve() == p.resolve()
    assert sorted(p.name for p in directory.glob('ES*.csv')) == sorted(p.name for p in paths)
    grid = Grid24(str(directory / 'ES*.csv'), night_pattern='')
    return grid, paths


def corrected_level(level, j, jumps):
    return level + sum(v for k, v in jumps.items() if j < k)


def features(g, phase, dest):
    vix = pd.read_csv(ROOT / 'data/VIX_daily.csv', parse_dates=['DATE']).set_index('DATE')
    cutoff = pd.Timestamp('2022-12-31') if phase == 'design' else pd.Timestamp(g.ts[-1])
    vix = vix.loc[vix.index <= cutoff]
    assert vix.index.is_unique
    gdates = pd.DatetimeIndex(g.ts)
    pos = {d: i for i, d in enumerate(gdates)}
    months = pd.period_range(gdates[0], min(cutoff, gdates[-1]), freq='M')
    records, holes, rolls = [], [], []
    for month in months:
        dates = cash_dates(month.start_time, month.end_time)
        final = dates[-1]
        if final not in pos:
            records.append(dict(month=str(month), iv=np.nan, rv=np.nan, vrp=np.nan, reason='unfinished_feature_month'))
            continue
        row = pos[final]
        # Complete-month feature uses only the prefix known at its final cash close.
        po, pc = g.o[:row+1].copy(), g.c[:row+1].copy()
        end_j = calendar_status(final)['cash_close_j']
        po[-1, end_j+1:] = np.nan
        pc[-1, end_j+1:] = np.nan
        prefix = SimpleNamespace(o=po, c=pc, ts=g.ts[:row+1])
        jumps = roll_jumps(prefix, 'ES')
        for j, value in jumps.items():
            if pd.Timestamp(g.ts[int(j)//1440]).to_period('M') == month:
                rolls.append(dict(feature_month=str(month), j=int(j), jump=float(value), known_through=str(final)))
        values = []
        month_holes = []
        for d in dates:
            if d not in pos:
                month_holes.append(dict(month=str(month), date=str(d.date()), kind='missing_cash_day'))
                continue
            r = pos[d]
            end = calendar_status(d)['cash_close_j']
            js = np.arange(515, end+1, 5)
            entries = [(r*1440+511, g.o[r,511], 'open')]
            entries += [(r*1440+int(j), g.c[r,j], 'close5') for j in js]
            previous = d - pd.Timedelta(days=1)
            while calendar_status(previous)['kind'] not in ('normal', 'early'):
                previous -= pd.Timedelta(days=1)
            if previous not in pos:
                month_holes.append(dict(month=str(month), date=str(d.date()), kind='missing_prior_cash_day'))
                continue
            pr = pos[previous]
            pj = calendar_status(previous)['cash_close_j']
            entries.insert(0, (pr*1440+pj, g.c[pr,pj], 'prior_close'))
            adjusted = []
            for j, px, kind in entries:
                if not np.isfinite(px) or px <= 0:
                    month_holes.append(dict(month=str(month), date=str(d.date()), j=int(j), kind=kind))
                adjusted.append(corrected_level(px, j, jumps))
            # Each cash-day path includes one overnight return, followed by all intraday intervals.
            if np.isfinite(adjusted).all() and min(adjusted) > 0:
                values.extend(np.diff(np.log(adjusted)) ** 2)
        iv = (float(vix.at[final, 'CLOSE']) / 100) ** 2 / 12 if final in vix.index else np.nan
        rv = float(np.sum(values)) if not month_holes else np.nan
        holes.extend(month_holes)
        records.append(dict(month=str(month), iv=iv, rv=rv, vrp=iv-rv,
                            cash_days=len(dates), observed_intervals=len(values),
                            feature_available_at=str(final.date())+' 17:00 America/Chicago',
                            reason='known' if np.isfinite(iv-rv) else 'missing_feature'))
    f = pd.DataFrame(records).set_index('month')
    # Calendar month rows remain in place; no history compression over unknown values.
    assert list(f.index) == [str(m) for m in months]
    f = signal_flags(f)
    f.to_csv(dest / 'features.csv')
    pd.DataFrame(holes).to_csv(dest / 'feature_holes.csv', index=False)
    pd.DataFrame(rolls).to_csv(dest / 'feature_roll_corrections.csv', index=False)
    return f


def opportunities(g, f, phase, dest, returns=False):
    pos = {pd.Timestamp(d): i for i, d in enumerate(g.ts)}
    years = range(2018, 2023) if phase == 'design' else range(2023, 2027)
    last = pd.Timestamp(g.ts[-1])
    periods = pd.period_range(f'{years.start}-01', f'{years.stop-1}-12', freq='M')
    events, rows, holes = [], [], []
    dailies = {name: {} for name in NAMES}
    for month in periods:
        if month.month not in TARGET_MONTHS: continue
        entry_day, exit_day = first_cash(month), first_cash(month+1)
        if exit_day > last: continue   # no completed full holding period at the source boundary
        signal_month = str(month-1)
        if signal_month not in f.index:
            rows.append(dict(month=str(month), state='missing_feature_month'))
            continue
        z = f.loc[signal_month]
        standalone = bool(np.isfinite(z.vrp))
        common = bool(np.isfinite([z.iv,z.rv]).all()) if PRIMARY_ONLY else bool(z.common_known)
        disposition = dict(month=str(month), signal_month=signal_month, p_standalone_known=standalone,
                           state='common_known' if common else 'unknown_history',
                           entry_time=str(entry_day.date())+' 08:30 America/Chicago',
                           exit_time=str(exit_day.date())+' 08:30 America/Chicago')
        rows.append(disposition)
        if not common: continue
        er, xr = pos.get(entry_day), pos.get(exit_day)
        if er is None or xr is None:
            holes.append(dict(month=str(month), kind='entry_or_exit_day'))
            continue
        entry, exit_ = g.o[er,511], g.o[xr,511]
        marks = []
        for day in cash_dates(entry_day, exit_day-pd.Timedelta(days=1)):
            r = pos.get(day)
            j = calendar_status(day)['cash_close_j']
            if r is None or not np.isfinite(g.c[r,j]):
                holes.append(dict(month=str(month), kind='daily_mark', date=str(day.date())))
            else:
                marks.append((day, g.c[r,j]))
        if not np.isfinite([entry,exit_]).all():
            holes.append(dict(month=str(month), kind='scheduled_open'))
            continue
        if not returns: continue
        gross = float((exit_-entry)*5.)
        ev = dict(month=str(month), entry_date=str(entry_day.date()), exit_date=str(exit_day.date()),
                  entry=float(entry), exit=float(exit_), gross=gross, commission=1.24,
                  slippage=2.50, net=gross-COST, stress_net=gross-STRESS, side=1,
                  vrp=float(z.vrp), iv=float(z.iv), rv=float(z.rv))
        ev.update({name:bool(z[name]) for name in NAMES})
        events.append(ev)
        for name in NAMES:
            # Keep flat dates at zero. Entry/exit costs assigned to actual cash dates.
            book = dailies[name]
            for d,_ in marks: book.setdefault(d, 0.)
            book.setdefault(exit_day,0.)
            if not bool(z[name]): continue
            previous = entry
            book[entry_day] = book.get(entry_day,0.) - COST/2
            for d,px in marks + [(exit_day, exit_)]:
                book[d] = book.get(d,0.) + float((px-previous)*5.)
                previous = px
            book[exit_day] -= COST/2
    pd.DataFrame(rows).to_csv(dest / 'eligibility.csv', index=False)
    pd.DataFrame(holes).to_csv(dest / 'holding_endpoint_holes.csv', index=False)
    known = sum(r['state']=='common_known' for r in rows)
    summary = dict(target_months=len(rows), common_known=known, unknown=len(rows)-known,
                   holding_endpoint_holes=len(holes), passed=known>=30 and not holes)
    if phase=='validation': summary['passed'] = known>=15 and not holes
    dump(dest / 'data_gate.json', summary)
    return pd.DataFrame(events), dailies, summary


def daily_frame(g, phase, books):
    start = pd.Timestamp('2018-01-01') if phase=='design' else pd.Timestamp('2023-01-01')
    stop = min(pd.Timestamp('2022-12-31') if phase=='design' else pd.Timestamp(g.ts[-1]), pd.Timestamp(g.ts[-1]))
    days = pd.DatetimeIndex(cash_dates(start,stop))
    d = pd.DataFrame(0., index=days, columns=NAMES)
    for name,book in books.items():
        for date,value in book.items():
            assert date in d.index
            d.at[date,name] = value
    d.index.name='date'
    return d


def metrics(events, daily):
    rows=[]
    for name in NAMES:
        for year in ['all', *sorted(daily.index.year.unique())]:
            dm = np.ones(len(daily),bool) if year=='all' else daily.index.year==year
            em = np.ones(len(events),bool) if year=='all' else pd.to_datetime(events.entry_date).dt.year==year
            selected=events[em & events[name]]
            for side in ['all','long','short']:
                e = selected if side!='short' else selected.iloc[:0]
                days = daily.loc[dm,name] if side!='short' else daily.loc[dm,name]*0
                v=M.perf(days,e.net,capital=50_000)
                # Shared perf omits initial zero from DD; include it explicitly for path metrics below.
                eq=np.r_[0,days.cumsum().to_numpy()]
                dd=eq-np.maximum.accumulate(eq)
                v['max_dd']=float(-dd.min())
                v['calmar']=float(v['annual']/v['max_dd']) if v['max_dd'] else np.nan
                v['ulcer']=float(np.sqrt(np.mean((100*dd/(50_000+np.maximum.accumulate(eq)))**2)))
                v.update(name=name,year=year,side=side,total=float(e.net.sum()),gross=float(e.gross.sum()),
                         commission=float(len(e)*1.24),slippage=float(len(e)*2.50),
                         stress_total=float(e.stress_net.sum()),t=tstat(e.net))
                rows.append(v)
    return pd.DataFrame(rows)


def filter_tests(events, daily):
    results=[]
    dates=pd.to_datetime(events.entry_date)
    rng=np.random.default_rng(SEED)
    # Month-level accounting includes opening marks in the next month; random ledgers reconstruct those overlaps.
    # Preserve the event daily paths by allocating a baseline book per original monthly event.
    for name in [x for x in ['P','H','I','R'] if x in NAMES]:
        keep=events[name].to_numpy(bool)
        removed=events.loc[~keep,'net']
        n=int(keep.sum())
        actual_net=float(events.loc[keep,'net'].sum())
        x=daily[name].to_numpy()
        actual_dd=float(-np.min(np.r_[0,x.cumsum()]-np.maximum.accumulate(np.r_[0,x.cumsum()])))
        totals=[]; dds=[]
        for _ in range(1000):
            pick=np.zeros(len(events),bool)
            pick[rng.choice(len(events),n,replace=False)]=True
            total=float(events.loc[pick,'net'].sum())
            # Nonoverlapping monthly allocation blocks; next-month exit and entry share a day.
            random_daily=np.zeros(len(daily))
            for i in np.flatnonzero(pick):
                random_daily += EVENT_PATHS[i]
            eq=np.r_[0,random_daily.cumsum()]
            totals.append(total);dds.append(float(-np.min(eq-np.maximum.accumulate(eq))))
        dif=events.net.where(keep,0)-events.net
        fraction=float(np.mean((actual_net>np.array(totals)) & (actual_dd<np.array(dds))))
        rt=tstat(removed)
        results.append(dict(name=name,selected=n,removed=len(removed),net=actual_net,
                            base_net=float(events.net.sum()),removed_avg=float(removed.mean()),removed_t=rt,
                            paired_month_nw3_t=nw_t(dif.to_numpy(),lag=3),random_draws=1000,
                            random_joint_profit_dd_beaten=fraction,actual_dd=actual_dd,
                            random_net_mean=float(np.mean(totals)),random_dd_median=float(np.median(dds)),
                            passed=bool(n>=15 and events.loc[keep,'gross'].mean()>2*COST
                                        and actual_net>0 and (tstat(events.loc[keep,'net']) or -999)>=2
                                        and actual_net>events.net.sum() and len(removed)>1
                                        and removed.mean()<0 and rt is not None and rt<=-1
                                        and fraction>=.9)))
    return pd.DataFrame(results)


EVENT_PATHS=[]


def event_paths(g,events,daily):
    paths=[];pos={pd.Timestamp(v):i for i,v in enumerate(g.ts)}
    for e in events.to_dict('records'):
        x=pd.Series(0.,index=daily.index)
        entry,exit_=pd.Timestamp(e['entry_date']),pd.Timestamp(e['exit_date'])
        previous=e['entry'];x.at[entry]-=COST/2
        for day in cash_dates(entry,exit_-pd.Timedelta(days=1)):
            px=g.c[pos[day],calendar_status(day)['cash_close_j']]
            x.at[day]+=(px-previous)*5;previous=px
        x.at[exit_]+=(e['exit']-previous)*5-COST/2
        np.testing.assert_allclose(x.sum(),e['net'],atol=1e-8)
        paths.append(x.to_numpy())
    return paths


def synthetic():
    count=calendar_checks()
    f=pd.DataFrame({'iv':np.arange(1,27,dtype=float),'rv':np.ones(26)},index=pd.period_range('2000-01',periods=26,freq='M').astype(str))
    f['vrp']=f.iv-f.rv
    a=signal_flags(f)
    f.iloc[-1,0]=1e9;f.iloc[-1,2]=1e9
    b=signal_flags(f)
    pd.testing.assert_frame_equal(a.iloc[:-1],b.iloc[:-1]);count+=1
    assert np.isclose(a.iloc[12].vrp_median12,np.median(np.arange(12)));count+=1
    f.iloc[2,2]=np.nan
    c=signal_flags(f)
    assert not c.iloc[13].common_known and c.iloc[15].common_known;count+=1
    assert corrected_level(100,1,pd.Series({3:10}))==110
    assert corrected_level(112,4,pd.Series({3:10}))==112;count+=2
    assert (511//60,511%60)==(8,31)
    assert first_cash(pd.Period('2023-01'))==pd.Timestamp('2023-01-03');count+=2
    assert all(m not in TARGET_MONTHS for m in [3,6,9,12]);count+=1
    marks=[100,110,105,120];net=sum(np.diff(marks))*5-COST
    assert np.isclose(net,(120-100)*5-COST);count+=1
    assert np.isclose(.25*5*2+1.24,COST) and np.isclose(4*.25*5*2+1.24,STRESS);count+=1
    return dict(passed=True,checks=count,market_data=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['synthetic','audit','design','validation'])
    parser.add_argument('--primary-only',action='store_true')
    args=parser.parse_args()
    if args.mode=='synthetic': print(json.dumps(synthetic()));return
    global PRIMARY_ONLY,NAMES
    PRIMARY_ONLY=args.primary_only
    if PRIMARY_ONLY: NAMES=['P','B']
    verify()
    phase='validation' if args.mode=='validation' else 'design'
    if phase=='validation':
        gate=json.loads((OUT/('primary_design' if PRIMARY_ONLY else 'design')/'economic_gate.json').read_text())
        assert gate['passed_candidates'], 'Frozen design gate did not authorize validation'
        authorization=ROOT/'agents/codex/research/vrp_monthly_proxy_validation_authorization.md'
        assert authorization.exists()
        assert subprocess.check_output(['git','show','HEAD:'+str(authorization.relative_to(ROOT))],cwd=ROOT)==authorization.read_bytes()
    dest=OUT/(('primary_' if PRIMARY_ONLY else '')+args.mode)
    dest.mkdir(parents=True,exist_ok=False)
    started=datetime.now(timezone.utc).isoformat()
    g,paths=feature_grid(phase)
    f=features(g,phase,dest)
    _,_,gate=opportunities(g,f,phase,dest,returns=False)
    manifest=dict(preregistration_commit=git('rev-parse',PREREG),code_commit=git('rev-parse','HEAD'),
                  script_sha256=sha(__file__),started_utc=started,phase=phase,mode=args.mode,
                  files={str(p.relative_to(ROOT)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths+[ROOT/'data/VIX_daily.csv']},
                  dependencies={p:sha(ROOT/p) for p in ['analysis/grid24.py','analysis/roll_adjust.py','analysis/metrics.py','analysis/codex_s03_calendar.py','analysis/codex_hunt_v2_ldf_delta.py','analysis/codex_hunt_v2_ldf_delta_design.py']},
                  versions={k:importlib.metadata.version(k) for k in ['numpy','pandas','scipy']},
                  source_parity=False,actual_native_mes_fills=False,mes_size=1,point_value=5,rt_cost=COST,stress_rt_cost=STRESS,
                  candidate_definitions=1 if PRIMARY_ONLY else 2,nonselectable_controls=1 if PRIMARY_ONLY else 3,seed=SEED,
                  primary_only_amendment=AMENDMENT if PRIMARY_ONLY else None,
                  vix_values_used_through='2022-12-31' if phase=='design' else str(pd.Timestamp(g.ts[-1]).date()),
                  target_quarterly_roll_months_excluded=True)
    if args.mode=='audit' or not gate['passed']:
        manifest['return_ledgers_evaluated']=0
        manifest['verdict']='AUDIT_ONLY' if args.mode=='audit' else 'STOP_DATA_GATE'
        dump(dest/'manifest.json',manifest);print(json.dumps(safe(dict(data_gate=gate,verdict=manifest['verdict']))));return
    events,books,_=opportunities(g,f,phase,dest,returns=True)
    daily=daily_frame(g,phase,books)
    for name in NAMES:
        np.testing.assert_allclose(daily[name].sum(),events.loc[events[name],'net'].sum(),atol=1e-8)
    global EVENT_PATHS
    EVENT_PATHS=event_paths(g,events,daily)
    for name in NAMES:
        reference=np.sum([EVENT_PATHS[i] for i in np.flatnonzero(events[name])],axis=0) if events[name].any() else np.zeros(len(daily))
        np.testing.assert_allclose(reference,daily[name],atol=1e-8)
    events.to_csv(dest/'monthly_ledger.csv',index=False)
    daily.to_csv(dest/'daily.csv')
    metrics(events,daily).to_csv(dest/'metrics.csv',index=False)
    filters=filter_tests(events,daily)
    filters.to_csv(dest/'filter_controls.csv',index=False)
    passed=filters.loc[filters.name.isin(['P','H']) & filters.passed,'name'].tolist()
    if phase=='validation':
        allowed=json.loads((OUT/('primary_design' if PRIMARY_ONLY else 'design')/'economic_gate.json').read_text())['passed_candidates']
        passed=[x for x in passed if x in allowed]
    dump(dest/'economic_gate.json',dict(passed_candidates=passed,verdict='PASS_SCREEN' if passed else 'REJECT_PROXY',
                                      validation_authorized=bool(passed) if phase=='design' else False))
    manifest.update(return_ledgers_evaluated=len(NAMES),verdict='PASS_SCREEN' if passed else 'REJECT_PROXY',
                    reconciliation=True,finished_utc=datetime.now(timezone.utc).isoformat())
    dump(dest/'manifest.json',manifest)
    print(filters.to_string(index=False));print(json.dumps(dict(verdict=manifest['verdict'],passed=passed)))


if __name__=='__main__':main()
