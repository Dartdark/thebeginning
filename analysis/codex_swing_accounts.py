"""Swing Target placement adapters; preparation is metadata-only, returns gated.

Reuses reviewed Anson account state machines and prepared caches read-only.
Current rosters are frozen at Claude 62e82a0. No helper __main__ is executed.
"""
from __future__ import annotations

import argparse
import ast
import gc
import importlib
import json
import os
from pathlib import Path
import pickle
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_swing_target/accounts'
SNAPSHOT = ROOT / 'agents/codex/inputs/swing_target/plan_snapshot'
REF = '62e82a0'
CACHE = ROOT / 'agents/codex/runtime/anson_plan.pkl'
CACHE_SHA = 'f5856163feab7b28315be7a3564c455d8dc8ec42429bf4cd66521817ce3fcf99'
PERSONAL_CACHE = ROOT / 'agents/codex/runtime/anson_personal_baseline.pkl'
sys.path.insert(0, str(ROOT / 'scratch_data/codex_deps'))
sys.path.insert(0, str(ROOT / 'analysis'))
os.environ.setdefault('NUMBA_CACHE_DIR', str(OUT / 'numba_cache'))
import numpy as np
import pandas as pd
import codex_anson_plan as A
import codex_anson_accounts as B
import codex_anson_personal as P
from codex_r2vault_accounts import ChronologicalCI
from codex_r2vault_personal import candidate_daily as marked_candidate_daily
import metrics as M
import resampling as R

SOURCES = (
    'funded_strategies/FUNDED_PLAN.md', 'personal_strategies/PORTFOLIO.md',
    'analysis/personal_portfolio.py', 'analysis/personal_variants.py',
    'analysis/overnight_tick_bench.py', 'analysis/outputs/personal_portfolio_output.txt',
    'agents/tasks/plan_daily_pnl.csv', 'checks/candidates/fc_2b/trades.csv',
    'checks/candidates/twin_continuation/trades.csv', 'checks/candidates/dual_thrust/trades.csv',
    'checks/candidates/kusho/python_trades_v9_rolladj.csv',
    'checks/candidates/s47_v2/python_trades_v2.csv',
    'checks/candidates/s30_ibs/daily_nq_es_per_micro.csv',
    'checks/candidates/overnight_tick/trades.csv',
    'checks/candidates/overnight_tick/python_trades.csv',
    'checks/candidates/bb_mrm/python_trades.csv',
)
COHORTS = {'2018_plus': ('2018-01-01', '2100-01-01'),
           '2018_22': ('2018-01-01', '2023-01-01'),
           '2023_plus': ('2023-01-01', '2100-01-01')}
LIMITS = [
    'Inherited CLS whole-day adverse and MOC close-based path approximations remain.',
    'Current OT funded path preserves published constant whole-night adverse value across the entire account day; it can invent simultaneous OT/RTH adverse exposure.',
    'OT order-flow source ends 2026-07-07; post-cutoff zero P&L is missing current baseline evidence, not verified no-trade activity.',
    'Inherited 150K fractional full-size bases are rounded only after cushion scaling; refs are 1500/3000.',
    'Personal preserves published daily booking (Kusho at exit, S30 daily marks), not full intraday margin/liquidation modeling.',
    'Personal plan10 commission adjustment is per nonzero P&L day and undercounts some reentries; MOC/S30 retain inherited fee approximations.',
    'Personal Twin remains the existing v1 checker marked ledger rather than an exact v2.1 ledger.',
]


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + '\n', encoding='utf-8')


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def prepare_sources():
    """Read-only Git input extraction, with no price/return calculations."""
    manifest = dict(reference=git('rev-parse', REF).decode().strip(), files={}, core_reuse=[])
    for rel in SOURCES:
        data = git('show', REF + ':' + rel)
        target = SNAPSHOT / rel
        if target.exists() and target.read_bytes() != data:
            raise ValueError('Refuse to overwrite different snapshot: ' + str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        manifest['files'][rel] = dict(git_blob=git('rev-parse', REF + ':' + rel).decode().strip(),
                                     sha256=A.file_sha(target), bytes=len(data))
    existing = json.loads((A.RUNTIME / 'manifest.json').read_text())
    for name, meta in existing['modules'].items():
        new = git('rev-parse', REF + ':' + meta['repository_path']).decode().strip()
        same = new == meta['git_blob']
        manifest['core_reuse'].append(dict(module=name, git_blob=new, unchanged=same))
        if not same:
            raise ValueError('Prepared Apex module changed: ' + name)
    for name, meta in existing['inputs'].items():
        if name == 'funded_plan.md':
            continue  # The new OT roster is explicitly applied below.
        new = git('rev-parse', REF + ':' + meta['repository_path']).decode().strip()
        if new != meta['git_blob']:
            raise ValueError('Prepared baseline input changed: ' + name)
    # Only cached Twin marks are reused in the personal upgrade. Verify its
    # source ledger and marking helper against the reviewed cache context.
    old_personal = json.loads((P.OUT/'baseline_manifest.json').read_text())
    twin_rel = 'checks/candidates/twin_continuation/trades.csv'
    if old_personal['files'][twin_rel]['git_blob'] != manifest['files'][twin_rel]['git_blob']:
        raise ValueError('Cached personal Twin source ledger changed')
    def twin_ast(path):
        tree = ast.parse(Path(path).read_text(encoding='utf-8-sig'))
        return ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='twin_marked'))
    if twin_ast(P.RUNTIME/'analysis/personal_portfolio.py') != twin_ast(SNAPSHOT/'analysis/personal_portfolio.py'):
        raise ValueError('Cached personal Twin marking helper changed')
    manifest['personal_twin_reuse'] = dict(same_ledger=True,same_marking_helper=True,
                                          reviewed_cache_sha256=A.file_sha(PERSONAL_CACHE))
    manifest.update(shared_caches_written=False, returns_computed=False, limitations=LIMITS)
    dump(SNAPSHOT / 'manifest.json', manifest)
    return manifest


def require_plan(commit, plan_path='agents/codex/plans/swing_target.md'):
    if not commit:
        raise PermissionError('Committed parent preregistration required')
    git('cat-file', '-e', commit + ':' + plan_path)
    saved = git('show',commit+':'+plan_path).decode('utf-8').replace('\r\n','\n')
    if saved != (ROOT/plan_path).read_text(encoding='utf-8').replace('\r\n','\n'):
        raise PermissionError('Working plan differs from committed preregistration')


def native_net(t, fee):
    return (t.exit - t.entry) * t.side * 2. - fee - .5 - .5 * t.kind.ne(1).astype(int)


def candidate_paths(g, trades, fee):
    """Per-MNQ same-date paths, preserving replay causal boundary extrema."""
    required = {'day','j0','j1','side','entry','exit','kind','entry_phase','exit_phase',
                'entry_minute_adverse_px','exit_minute_adverse_px'}
    if not required.issubset(trades):
        raise ValueError('Missing causal candidate fields: ' + str(required - set(trades)))
    w, r = np.zeros(g.o.shape), np.zeros(g.o.shape)
    for t in trades.itertuples():
        d, e, z, s = int(t.day), int(t.j0), int(t.j1), int(t.side)
        if s not in (-1,1) or not 0 <= e <= z < g.o.shape[1]:
            raise ValueError('Invalid candidate same-day geometry')
        if bool(getattr(t,'cross_date',False)) or int(getattr(t,'unknown_held_minutes',0)):
            raise ValueError('Incomplete/cross-date candidate trade entered Apex paths')
        if t.entry_phase not in ('open','intrabar') or t.exit_phase not in ('open','intrabar'):
            raise ValueError('Unrecognized candidate executable phase')
        end = z + int(t.exit_phase != 'open')
        price = np.array((g.l if s > 0 else g.h)[d,e:end], copy=True)
        if len(price):
            price[0] = t.entry_minute_adverse_px
            if t.exit_phase != 'open':
                price[-1] = t.exit_minute_adverse_px
            if not np.isfinite(price).all():
                raise ValueError('Unknown held minute: do not invent an adverse mark')
            if e == z and t.exit_phase != 'open' and not np.isclose(
                    t.entry_minute_adverse_px,t.exit_minute_adverse_px,rtol=0,atol=1e-8):
                raise ValueError('Same-minute candidate adverse extrema disagree')
        net = (t.exit-t.entry)*s*2. - fee - .5 - (0. if int(t.kind)==1 else .5)
        marks = (price-t.entry)*s*2. - fee - .5
        if len(marks) and t.exit_phase != 'open':
            marks[-1] = min(marks[-1],net)
        w[d,e:end] += marks
        w[d,end:] += net
        r[d,z:] += net
    return w,r


def allocations(base, context):
    vb = ('VB_N','VB_F') if context.endswith('funded') else ('VB',)
    empty = {k:v for k,v in base.items() if k not in vb}
    n = 2 if context == '150K_evaluation' else 1
    return dict(BASE=dict(base),EMPTY_VB=empty,ADD={**base,'SWING':n},REPLACE_VB={**empty,'SWING':n})


def current_funded_plans():
    plans = A.funded_plans()
    plans['50K_funded'].pop('MON_MC')
    plans['50K_funded']['OT'] = 1
    plans['150K_funded']['OT'] = 2
    return plans


def add_current_ot(lab, fee):
    """Published OT whole-night adverse proxy; do not silently upgrade it."""
    t = pd.read_csv(SNAPSHOT / 'checks/candidates/overnight_tick/python_trades.csv',parse_dates=['date'])
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    pos = pd.Series(np.arange(lab.D),index=dates)
    low, close = np.zeros(lab.D), np.zeros(lab.D)
    for x in t.itertuples():
        if x.date in pos.index:
            i = int(pos[x.date])
            low[i] = x.adv/10 - (fee-.725)
            close[i] = x.net/10 - (fee-.725)
    lab.W['OT'] = low[:,None] * np.ones((1,lab.W['VB'].shape[1]))
    lab.C['OT'] = close
    return dict(trades=len(t),last_source_date=str(t.date.max().date()),path='published constant daily adverse proxy')


def eligible_mask(lab, eligible_dates):
    if eligible_dates is None:
        raise ValueError('Explicit complete candidate-history/day eligibility dates are required')
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    return dates.isin(pd.DatetimeIndex(eligible_dates))


def _funded(lab, fb, f50, f150, fee, eligible, out):
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    histories = {}
    for label,(lo,hi) in COHORTS.items():
        boot = fb.Boot(lab,start=lo)
        boot.days = boot.days[eligible[boot.days] & np.asarray(dates[boot.days] < hi)]
        histories[label] = np.concatenate([boot._histories(250,504,10,s) for s in (1,2,3,4)])
        np.save(out / ('histories_' + label + '.npy'),histories[label])
    rows, paired, parity = [],[],[]
    for context,F in (('50K_funded',f50),('150K_funded',f150)):
        results = {cohort:{} for cohort in histories}
        parameters = B.rules(F,context)
        for name,plan in allocations(current_funded_plans()[context],context).items():
            keys = sorted(plan)
            w,c = np.stack([lab.W[k] for k in keys]),np.stack([lab.C[k] for k in keys])
            names,q = lab._base({k:plan[k] for k in keys})
            assert names == keys
            table = B.acc.make_table(w,c,q)
            # Existing parity helper fixes250/500 horizons; preserve that engine
            # check, then score the preregistered252/504 production horizons.
            parity += B.parity_check(w,c,table,histories['2018_plus'][[0,1,17,333,999]],F,parameters,
                                     f'{fee}/{context}/{name}')
            for cohort,h in histories.items():
                results[cohort][name] = (B.run_table(table,h,252,parameters),B.run_table(table,h,504,parameters))
            print(f'Swing funded {context} {fee:.2f} {name}',flush=True)
            del w,c,table
            gc.collect()
        for cohort,raw in results.items():
            a,b = B.funded_summaries(raw,fee,context,cohort)
            rows.extend(a);paired.extend(b)
            np.savez_compressed(out / f'funded_{context}_{cohort}_{fee:.2f}.npz',
                                **{f'{k}__{h}':raw[k][i] for k in raw for i,h in enumerate((252,504))})
    pd.DataFrame(rows).to_csv(out / f'funded_summary_{fee:.2f}.csv',index=False)
    pd.DataFrame(paired).to_csv(out / f'funded_paired_{fee:.2f}.csv',index=False)
    dump(out / f'funded_parity_{fee:.2f}.json',parity)
    return rows,paired


def _evaluation(lab, scratch, fee, paths, eligible, prereg, out):
    bundle = A.evaluation_parts(scratch,preregistration_commit=prereg,authorized_returns=True,fee=fee,grid=lab.g)
    complete = np.array([s+21 <= lab.D and eligible[s:s+21].all() for s in range(lab.D)])
    last = np.full(lab.D,np.datetime64('NaT'),dtype='datetime64[ns]')
    last[:lab.D-20] = bundle.dates[20:].to_numpy(dtype='datetime64[ns]')
    masks = {k:np.asarray((bundle.dates>=lo)&(bundle.dates<hi)&(last<np.datetime64(hi)))
             for k,(lo,hi) in COHORTS.items()}
    ci = {k:ChronologicalCI(complete[mask]) for k,mask in masks.items()}
    rows,paired = [],[]
    for context,part in bundle.contexts.items():
        pp,q = part.parts,part.quantities
        bw,br = sum(pp[k][0]*q[k] for k in q),sum(pp[k][1]*q[k] for k in q)
        ew,er = bw-pp['VB'][0]*q['VB'],br-pp['VB'][1]*q['VB']
        raw = {}
        for name,plan in allocations(q,context).items():
            if name == 'BASE': w,r = bw,br
            elif name == 'EMPTY_VB': w,r = ew,er
            else:
                w0,r0 = (ew,er) if name == 'REPLACE_VB' else (bw,br)
                w,r = w0+paths[0]*plan['SWING'],r0+paths[1]*plan['SWING']
            if context.startswith('50'):
                values = [part.challenge(w,r,np.arange(s,min(s+21,lab.D)),lambda p,c,n:1.) for s in range(lab.D)]
            else:
                values = [part.challenge(w,r,s,lab.D,part.rules) for s in range(lab.D)]
            outcome = np.array([x[0] if x else '' for x in values])
            days = np.array([x[1] if x else 0 for x in values])
            raw[name] = outcome,days
            for cohort,mask in masks.items():
                ok = complete & mask
                rows.append(dict(context=context,fee=fee,cohort=cohort,config=name,starts=int(ok.sum()),
                    passed=float((outcome[ok]=='pass').mean()),failed=float((outcome[ok]=='fail').mean()),
                    timed_out=float((outcome[ok]=='time').mean()),
                    median_pass_days=float(np.median(days[ok & (outcome=='pass')]))))
            print(f'Swing evaluation {context} {fee:.2f} {name}',flush=True)
            if name not in ('BASE','EMPTY_VB'): del w,r
        for name,(o,d) in raw.items():
            for cohort,mask in masks.items():
                for ref in ('BASE','EMPTY_VB'):
                    for metric,label in (('passed','pass'),('failed','fail'),('timed_out','time')):
                        delta = (o[mask]==label).astype(float)-(raw[ref][0][mask]==label)
                        lo,hi = ci[cohort].interval(delta)
                        paired.append(dict(context=context,fee=fee,cohort=cohort,config=name,reference=ref,metric=metric,
                                           delta=float(delta[complete[mask]].mean()),lo=lo,hi=hi))
        frame = pd.DataFrame({f'{k}__{col}':v[i] for k,v in raw.items() for i,col in enumerate(('outcome','days'))},index=bundle.dates)
        frame['complete_21day_start'],frame['window_last_date'] = complete,last
        frame.to_csv(out / f'evaluation_starts_{context}_{fee:.2f}.csv',index_label='date')
        del bw,br,ew,er
        gc.collect()
    pd.DataFrame(rows).to_csv(out / f'evaluation_summary_{fee:.2f}.csv',index=False)
    pd.DataFrame(paired).to_csv(out / f'evaluation_paired_{fee:.2f}.csv',index=False)
    return rows,paired


def run_accounts(g, trades, prereg_commit, *, eligible_dates, fee=1.24, out=OUT,
                 scratch=ROOT/'scratch_data', plan_path='agents/codex/plans/swing_target.md'):
    require_plan(prereg_commit,plan_path)
    cross = trades.get('cross_date',pd.Series(False,index=trades.index)).astype(bool)
    if 'exit_day' in trades: cross |= trades.exit_day.ne(trades.day)
    wall_minute = trades.j1-trades.get('exit_phase',pd.Series('intrabar',index=trades.index)).eq('open').astype(int)
    if cross.any() or wall_minute.gt(959).any():
        raise ValueError('As-supplied Apex incompatibility: cross-date/after-flat position; do not delete or repair trades')
    if trades.get('unknown_held_minutes',pd.Series(0,index=trades.index)).gt(0).any():
        raise ValueError('Source contains unknown held prices; account comparison is not identifiable')
    source_manifest = prepare_sources()
    if A.file_sha(CACHE) != CACHE_SHA:
        raise ValueError('Prepared baseline changed; do not rebuild automatically')
    out = Path(out);out.mkdir(parents=True,exist_ok=True)
    with A.pinned_imports(scratch):
        with CACHE.open('rb') as stream: lab = pickle.load(stream)
        if not np.array_equal(np.asarray(g.ts),np.asarray(lab.g.ts)):
            raise ValueError('Candidate and account calendars differ')
        base_legs = list(set(A.P.CURRENT_PLAN)|{'RS','DT'})
        if fee != 1.04: lab.real_fees(fee-1.04,base_legs)
        ot = add_current_ot(lab,fee)
        eligible = eligible_mask(lab,eligible_dates)
        dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
        use = trades[trades.date.isin(dates[eligible])].copy()
        w,r = candidate_paths(g,use,fee)
        paths = w[lab.tr],r[lab.tr]
        lab.W['SWING'],lab.C['SWING'] = paths[0],paths[1][:,-1]
        np.testing.assert_allclose(lab.C['SWING'].sum(),native_net(use,fee).sum(),rtol=0,atol=1e-6)
        del w,r
        f50,f150 = importlib.import_module('funded_sim'),importlib.import_module('funded_sim150')
        fb = importlib.import_module('funded_bootstrap')
        fr,fd = _funded(lab,fb,f50,f150,fee,eligible,out)
        er,ed = _evaluation(lab,scratch,fee,paths,eligible,prereg_commit,out)
        dump(out / f'manifest_{fee:.2f}.json',dict(reference=source_manifest['reference'],preregistration=prereg_commit,
            prepared_cache_sha256=CACHE_SHA,fee=fee,rosters=current_funded_plans(),OT=ot,
            all_days=lab.D,eligible_days=int(eligible.sum()),excluded_dates=dates[~eligible].strftime('%Y-%m-%d').tolist(),
            candidate_trades=len(use),raw_trades=len(trades),limitations=LIMITS,shared_caches_written=False,
            contexts=['50K_evaluation','150K_evaluation','50K_funded','150K_funded'],
            allocation='BASE, ADD, EMPTY_VB, REPLACE_VB; 1 MNQ except 150K evaluation 2 MNQ',
            tie_policies={'50K_evaluation':'pass first','150K_evaluation':'breach first'}))
    return dict(funded=pd.DataFrame(fr),funded_paired=pd.DataFrame(fd),evaluation=pd.DataFrame(er),evaluation_paired=pd.DataFrame(ed))


def load_current_personal(fee=1.24):
    """Upgrade unchanged published14 cached marks to current18, never run source main."""
    with PERSONAL_CACHE.open('rb') as stream: old = pickle.load(stream)
    days = pd.DatetimeIndex(old.index)
    raw = pd.read_csv(SNAPSHOT/'agents/tasks/plan_daily_pnl.csv',parse_dates=['date']).set_index('date')
    if not raw.index.equals(days): raise ValueError('Personal baseline calendar changed')
    frame = raw - (fee-.725)*(raw!=0)
    def book(rel,name,date_col='date'):
        t = pd.read_csv(SNAPSHOT/rel,parse_dates=[date_col])
        t = t[t[date_col] <= days[-1]].copy()
        k = np.minimum(days.searchsorted(pd.DatetimeIndex(t[date_col])),len(days)-1)
        x = t.net.to_numpy()/10-(fee-.725)
        out = pd.Series(x,index=days[k]).groupby(level=0).sum().reindex(days,fill_value=0.).rename(name)
        assert np.isclose(out.sum(),x.sum())
        return out
    frame['FC2B'] = book('checks/candidates/fc_2b/trades.csv','FC2B')
    # Cached Twin is already daily16CT-marked at1.275 RT. Replace that fee on
    # the same published exit-cost dates while preserving its price marks.
    tt = pd.read_csv(SNAPSHOT/'checks/candidates/twin_continuation/trades.csv',parse_dates=['date'])
    tt = tt[tt.date <= days[-1]]
    exit_sessions = tt.date+pd.to_timedelta((tt.exit_time_ct>1600).astype(int),unit='D')
    k = np.minimum(days.searchsorted(pd.DatetimeIndex(exit_sessions)),len(days)-1)
    credit = pd.Series(1.275-fee,index=days[k]).groupby(level=0).sum().reindex(days,fill_value=0.)
    frame['TwinContinuation'] = old.TwinContinuation + credit
    frame['OvernightTick'] = book('checks/candidates/overnight_tick/trades.csv','OvernightTick')
    frame['DualThrust'] = book('checks/candidates/dual_thrust/trades.csv','DualThrust')
    frame['Kusho'] = book('checks/candidates/kusho/python_trades_v9_rolladj.csv','Kusho','exit_date')
    frame['S47'] = book('checks/candidates/s47_v2/python_trades_v2.csv','S47')
    s30 = pd.read_csv(SNAPSHOT/'checks/candidates/s30_ibs/daily_nq_es_per_micro.csv',index_col=0,parse_dates=True).iloc[:,0]
    frame['S30'] = s30.reindex(days,fill_value=0.)
    frame['BB_MRM'] = book('checks/candidates/bb_mrm/python_trades.csv','BB_MRM')
    if len(frame.columns) != 18 or frame.isna().any().any():
        raise ValueError('Current personal18 baseline incomplete')
    return frame


def verify_published_personal():
    """Reconcile native roster/marks before applying the frozen fee scenarios."""
    original = load_current_personal(1.275).sum(axis=1)
    source = SNAPSHOT/'analysis/outputs/personal_portfolio_output.txt'
    text = source.read_text(encoding='utf-8')
    m = re.search(r'\$([\d,]+) a year \| max DD \$([\d,]+) \| worst month',text)
    if m is None: raise ValueError('Published personal summary control not located')
    annual,dd = float(original.sum()/len(original)*252),R.max_dd(original)
    assert abs(annual-float(m[1].replace(',',''))) <= .51
    assert abs(dd-float(m[2].replace(',',''))) <= .51
    expected = ast.literal_eval(re.search(r'by year: (\{[^\n]+\})',text)[1])
    year = {int(y):float(v) for y,v in original.groupby(original.index.year).sum().items()}
    assert set(year) == set(expected)
    for y,value in year.items():
        assert abs(value-float(expected[y].replace('$','').replace(',',''))) <= .51
    return dict(columns=18,fee_convention=1.275,annual=annual,max_daily_dd=dd,by_year=year,
                published_rounding_reconciled=True,source_sha256=A.file_sha(source))


def personal_configurations(frame,candidate):
    sets = {**P.STARTERS,'FULL':list(frame.columns)}
    plans,metadata = {},{}
    for group,keys in sets.items():
        base = frame[keys].sum(axis=1)
        choices = dict(BASE=base,ADD=base+candidate)
        if 'VaultBreak' in keys:
            empty = base-frame.VaultBreak
            choices.update(EMPTY_VB=empty,REPLACE_VB=empty+candidate)
        for name,x in choices.items():
            key = group+'__'+name
            plans[key] = x
            metadata[key] = dict(group=group,allocation=name,pieces=keys)
    assert len(plans) == 16
    return plans,metadata


def personal_benchmark(frame,candidate,out):
    plans,meta = personal_configurations(frame,candidate)
    rows,effects,historical = [],[],[]
    days = pd.DatetimeIndex(frame.index)
    periods = {**COHORTS,**{str(y):(f'{y}-01-01',f'{y+1}-01-01') for y in sorted(days.year.unique())}}
    for name,x in plans.items():
        for period,(lo,hi) in periods.items():
            d = x[(days>=lo)&(days<hi)]
            # Initial zero is explicit: an opening loss counts in drawdown.
            p = M.perf(np.r_[0.,d.to_numpy()],d[d!=0])
            p.update(config=name,period=period,total=float(d.sum()),days=len(d),**meta[name])
            historical.append(p)
    for cohort,(lo,hi) in COHORTS.items():
        mask = (days>=lo)&(days<hi)
        idx = P.histories(int(mask.sum()),n=1000,horizon=252,block=10,seed=20261025)
        np.save(out/f'personal_histories_{cohort}.npy',idx)
        raw = {}
        for name,x in plans.items():
            profit,dd = P.simulate_daily(x[mask].to_numpy(),idx)
            raw[name] = profit,dd
            rows.append(dict(cohort=cohort,config=name,profit_mean=profit.mean(),profit_p5=np.percentile(profit,5),
                profit_p50=np.median(profit),profit_p95=np.percentile(profit,95),p_losing_year=(profit<=0).mean(),
                dd_p50=np.median(dd),dd_p95=np.percentile(dd,95),capital_20pct=np.percentile(dd,95)/.2,
                median_profit_over_dd95=np.median(profit)/max(np.percentile(dd,95),1e-9),**meta[name]))
        for name,(p,d) in raw.items():
            group = meta[name]['group']
            refs = [group+'__BASE'] + ([group+'__EMPTY_VB'] if group in ('C','D','FULL') else [])
            for ref in refs:
                bp,bd = raw[ref]
                annual_lo,annual_hi = P.historical_annual_effect_interval(
                    (plans[name]-plans[ref])[mask].to_numpy(),seed=20261025,n=5000,block=10)
                plo,phi = P.paired_mean_interval(p-bp,seed=20261025,n=5000)
                dlo,dhi = P.paired_mean_interval(d-bd,seed=20261025,n=5000)
                effects.append(dict(cohort=cohort,config=name,reference=ref,mean_profit_delta=(p-bp).mean(),
                    simulation_mean_profit_lo=plo,simulation_mean_profit_hi=phi,mean_dd_delta=(d-bd).mean(),
                    simulation_mean_dd_lo=dlo,simulation_mean_dd_hi=dhi,
                    historical_annual_mean_lo=annual_lo,historical_annual_mean_hi=annual_hi,
                    dd95_delta=np.percentile(d,95)-np.percentile(bd,95)))
        np.savez_compressed(out/f'personal_{cohort}.npz',**{name+'__'+label:value[i]
                            for name,value in raw.items() for i,label in enumerate(('profit','dd'))})
    summary,effect,hist = pd.DataFrame(rows),pd.DataFrame(effects),pd.DataFrame(historical)
    summary.to_csv(out/'mc_summary.csv',index=False)
    effect.to_csv(out/'paired_effects.csv',index=False)
    hist.to_csv(out/'historical_summary.csv',index=False)
    return summary,effect,hist


def check_personal_outputs(out):
    """Rebook saved daily portfolios/history indices; no new model/history draws."""
    out = Path(out)
    frame = pd.read_csv(out/'baseline_daily18.csv',index_col=0,parse_dates=True)
    candidate = pd.read_csv(out/'candidate_daily.csv',index_col=0,parse_dates=True).iloc[:,0]
    plans,metadata = personal_configurations(frame,candidate)
    assert len(plans) == 16 and len(frame.columns) == 18
    summary = pd.read_csv(out/'mc_summary.csv')
    effects = pd.read_csv(out/'paired_effects.csv')
    days = pd.DatetimeIndex(frame.index)
    checked = paired = 0
    for cohort,(lo,hi) in COHORTS.items():
        mask = (days>=lo)&(days<hi)
        idx = np.load(out/f'personal_histories_{cohort}.npy')
        raw = np.load(out/f'personal_{cohort}.npz')
        assert idx.shape == (1000,252) and (idx>=0).all() and (idx<int(mask.sum())).all()
        for name,x in plans.items():
            values = x[mask].to_numpy()[idx]
            cumulative = values.cumsum(axis=1)
            peak = np.maximum.accumulate(np.c_[np.zeros(len(idx)),cumulative],axis=1)[:,1:]
            profit,dd = cumulative[:,-1],(peak-cumulative).max(axis=1)
            np.testing.assert_allclose(profit,raw[name+'__profit'],rtol=0,atol=1e-6)
            np.testing.assert_allclose(dd,raw[name+'__dd'],rtol=0,atol=1e-6)
            row = summary[(summary.cohort==cohort)&(summary.config==name)].iloc[0]
            np.testing.assert_allclose([row.profit_mean,row.profit_p50,row.dd_p95],
                [profit.mean(),np.median(profit),np.percentile(dd,95)],rtol=0,atol=1e-6)
            checked += 1
        for r in effects[effects.cohort==cohort].itertuples():
            profit = raw[r.config+'__profit']-raw[r.reference+'__profit']
            dd = raw[r.config+'__dd']-raw[r.reference+'__dd']
            np.testing.assert_allclose([r.mean_profit_delta,r.mean_dd_delta],[profit.mean(),dd.mean()],rtol=0,atol=1e-6)
            paired += 1
    result = dict(daily_roster_and_fixed_allocations=True,current_18_columns=True,configurations=16,
        independent_saved_MC_rebooked_rows=checked,paired_mean_rows_reconciled=paired,
        initial_zero_in_drawdown=True,new_return_models=0,new_history_draws=0,
        reviewer='Adapter author self-check, not independent source/parity certification')
    dump(out/'saved_output_checks.json',result)
    return result


def save_reproduction(out, ledger, prereg, fee):
    out = Path(out)
    dump(out/'reproduction.json',dict(preregistration=prereg,plan_path='agents/codex/plans/swing_target.md',fee=fee,
        source_ledger=str(Path(ledger).resolve().relative_to(ROOT)),ledger_sha256=A.file_sha(ledger),
        script_sha256=A.file_sha(Path(__file__)),python=sys.executable,
        snapshot_manifest_sha256=A.file_sha(SNAPSHOT/'manifest.json'),
        cached_personal_Twin_sha256=A.file_sha(PERSONAL_CACHE),
        configurations=16,bootstrap=dict(n=1000,horizon=252,block=10,seed=20261025),
        historical_annual_interval=dict(level=.95,n=5000,block=10,seed=20261025),
        simulation_precision_interval=dict(level=.95,n=5000,seed=20261025),
        no_Apex_limits=True,shared_caches_written=False,source_models=2,
        no_candidate_trade_exclusions=True,limitations=LIMITS))


def run_personal(g, trades, prereg_commit, *, fee=1.24, out=OUT.parent/'personal',open_positions=None,
                 plan_path='agents/codex/plans/swing_target.md'):
    require_plan(prereg_commit,plan_path)
    source_manifest = prepare_sources()
    out = Path(out);out.mkdir(parents=True,exist_ok=True)
    dump(out/'baseline_reconciliation.json',verify_published_personal())
    frame = load_current_personal(fee)
    days = pd.DatetimeIndex(frame.index)
    def renamed(z):
        if z is None: return None
        return z.rename(columns={a:b for a,b in {'day':'entry_row','exit_day':'exit_row','j0':'entry_j','j1':'exit_j'}.items()
                                 if a in z and b not in z}).copy()
    t = renamed(trades)
    if 'exit_row' not in t: t['exit_row'] = t.entry_row
    daily,marks,money = marked_candidate_daily(g,t,days,fee=fee,open_positions=renamed(open_positions))
    marks.to_csv(out/'candidate_marks.csv',index=False)
    frame.to_csv(out/'baseline_daily18.csv',index_label='date')
    daily.to_csv(out/'candidate_daily.csv',index_label='date')
    summary,effects,historical = personal_benchmark(frame,daily,out)
    portfolios,_ = personal_configurations(frame,daily)
    joint = []
    for group in (*P.STARTERS,'FULL'):
        base = portfolios[group+'__BASE']
        loss = base<0
        joint.append(dict(group=group,correlation=daily.corr(base),baseline_loss_days=int(loss.sum()),
                          joint_loss_days=int((loss&(daily<0)).sum()),candidate_net_on_baseline_loss_days=float(daily[loss].sum())))
    pd.DataFrame(joint).to_csv(out/'joint_losses.csv',index=False)
    dump(out/'manifest_swing.json',dict(reference=source_manifest['reference'],preregistration=prereg_commit,fee=fee,
        current_personal_columns=list(frame),configurations=16,limitations=LIMITS,shared_caches_written=False,
        daily_booking='Candidate at observed16CT marks, including cross-date trades; published baseline marking conventions retained',
        candidate_bookkeeping=money,bootstrap=dict(histories=1000,horizon=252,block=10,seed=20261025),
        fee_repricing='Plan10 per nonzero day; exact per trade on closed extra ledgers; Twin fee credit on published exit date; S30 unchanged'))
    check_personal_outputs(out)
    return dict(summary=summary,effects=effects,historical=historical)


def synthetic_checks():
    from types import SimpleNamespace
    g = SimpleNamespace(o=np.full((1,10),100.),l=np.full((1,10),99.),h=np.full((1,10),101.))
    g.l[0,2],g.l[0,5] = 1.,1.
    row = dict(day=0,j0=2,j1=5,side=1,entry=100.,exit=110.,kind=1,
        entry_phase='intrabar',exit_phase='intrabar',entry_minute_adverse_px=100.,exit_minute_adverse_px=108.)
    w,r = candidate_paths(g,pd.DataFrame([row]),1.24)
    np.testing.assert_allclose(w[0,2],-1.74)
    np.testing.assert_allclose(w[0,5],14.26)
    np.testing.assert_allclose(r[0,5:],18.26)
    # An open exit excludes every later high/low of its minute.
    row.update(side=-1,exit=90.,entry_phase='open',exit_phase='open',entry_minute_adverse_px=101.)
    g.h[0,5] = 1000.
    w,r = candidate_paths(g,pd.DataFrame([row]),1.24)
    np.testing.assert_allclose(w[0,5:],18.26)
    row.update(exit=110.,kind=0)
    w,r = candidate_paths(g,pd.DataFrame([row]),1.24)
    np.testing.assert_allclose(w[0,5:],-22.24)
    assert allocations({'VB':8,'ONB':1},'150K_evaluation')['REPLACE_VB'] == {'ONB':1,'SWING':2}
    assert allocations({'VB_N':2,'VB_F':1,'ONB':1},'150K_funded')['REPLACE_VB'] == {'ONB':1,'SWING':1}
    names = set().union(*[set(v) for v in P.STARTERS.values()])
    names |= {'MondayLong','LateDayFlow','FC2B','OvernightTick','DualThrust','Kusho','S47','S30','BB_MRM'}
    assert len(names) == 18
    frame = pd.DataFrame(1.,index=pd.bdate_range('2020-01-01',periods=50),columns=sorted(names))
    candidate = pd.Series(2.,index=frame.index)
    configs,_ = personal_configurations(frame,candidate)
    np.testing.assert_array_equal(configs['FULL__REPLACE_VB'],configs['FULL__BASE']-frame.VaultBreak+candidate)
    # Cross-date source carries remain personal trades and are marked before16CT.
    dates = pd.DatetimeIndex(['2020-01-06','2020-01-07'])
    gg = SimpleNamespace(ts=dates,c=np.full((2,1440),np.nan))
    gg.c[0,960],gg.c[0,961] = 105.,1000.
    z = pd.DataFrame([dict(entry_row=0,exit_row=1,entry_j=900,exit_j=600,entry_phase='open',exit_phase='intrabar',
                          side=1,entry=100.,exit=110.,kind=1)])
    daily,_,money = marked_candidate_daily(gg,z,dates,fee=1.24)
    np.testing.assert_allclose(daily,[8.26,10.],rtol=0,atol=1e-9)
    return dict(causal_boundary_extrema=True,short_open_exit_excludes_later_high=True,
                native_target_and_stop_costs=True,fixed_context_sizes=True,
                personal16_fixed_configs=True,crossdate_personal_marks_exclude_after16=True)


def write_operational_limits(gate_path=OUT.parent/'cheap_gate.json'):
    gate = json.loads(Path(gate_path).read_text())
    rows,details = [],[]
    for model in gate['models']:
        path = OUT.parent/(model['model']+'_trades.csv')
        t = pd.read_csv(path)
        bad = t.cross_date.astype(bool)|t.apex_flat_violation.astype(bool)
        if not bad.any():
            raise ValueError('This operational-stop writer requires actual source violations')
        details.extend(t.loc[bad,['date','exit_date','j0','j1','entry_phase','exit_phase','reason','unknown_held_minutes']]
                       .assign(model=model['model']).to_dict('records'))
        for context in ('50K_evaluation','150K_evaluation','50K_funded','150K_funded'):
            rows.append(dict(model=model['model'],context=context,status='REJECT_AS_SUPPLIED',
                account_bench_run=False,source_flat_or_closure_violations=int(bad.sum()),
                missing_held_minutes=int(t.unknown_held_minutes.sum()),
                missing_minutes_outside_crossdate=int(t.loc[~t.cross_date.astype(bool),'unknown_held_minutes'].sum()),
                reason='Positions cross holiday/session closures and the Apex flat boundary. No deletion, cutoff repair or hypothetical valid benchmark.'))
    target = OUT.parent/'apex_operational_limits.json'
    dump(target,dict(preregistration=gate['plan_commit'],contexts=rows,violating_trades=details,
         gap_interpretation='All unobserved held-minute spans are inside holiday carries; their closure/feed partition is not independently certified. They are not1201 independently established feed-loss minutes.',
         fixed_calendar_policy='Neither invalid trades nor their source dates were removed to obtain a passing Apex result.',
         shared_caches_written=False))
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--personal',action='store_true')
    parser.add_argument('--operational-only',action='store_true')
    parser.add_argument('--check-personal',type=Path)
    parser.add_argument('--ledger',type=Path)
    parser.add_argument('--prereg')
    parser.add_argument('--fee',type=float,default=1.24)
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    if args.prepare:
        print(json.dumps(prepare_sources(),indent=2))
    elif args.operational_only:
        print(write_operational_limits())
    elif args.check_personal:
        print(json.dumps(check_personal_outputs(args.check_personal),indent=2))
    elif args.personal:
        if not args.ledger or not args.prereg:
            parser.error('--personal requires --ledger and --prereg')
        require_plan(args.prereg)
        with (ROOT/'scratch_data/g24.pkl').open('rb') as stream: grid = pickle.load(stream)
        t = pd.read_csv(args.ledger,parse_dates=['date','exit_date'])
        out = args.out or OUT.parent/'personal'/args.ledger.stem.replace('_trades','')/f'fee_{args.fee:.2f}'
        result = run_personal(grid,t,args.prereg,fee=args.fee,out=out)
        save_reproduction(out,args.ledger,args.prereg,args.fee)
        full = result['summary'][result['summary'].config.str.startswith('FULL__')]
        print(full.to_string(index=False),flush=True)
        print('Personal comparison complete: '+str(out),flush=True)
    else:
        parser.error('Use --prepare, --personal, --operational-only, or the gated functions')
