"""Frozen Vault Break recent-risk diagnostic and design-first bracket screen.

Uses existing research caches/engines read-only. No broker, credentials, live writes
or data-cache rebuilding. Run with the already installed bundled Python 3.12.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import pickle
import subprocess
import sys
import warnings

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_vb_recent_risk'
sys.path.insert(0, str(ROOT / 'scratch_data/codex_deps'))
sys.path.insert(0, str(ROOT / 'analysis'))
os.environ['NUMBA_CACHE_DIR'] = str(OUT / 'numba_cache')
import numpy as np
import pandas as pd
import codex_break_vb_onb as B
import metrics as M
import resampling as R
import montecarlo as MC
import param_clusters as PC
from live_vs_backtest import read_trades
from codex_live_reconcile import COLS

PLAN = 'agents/codex/plans/vb_recent_risk.md'
SEED = 20261025
START, ASOF = pd.Timestamp('2026-08-25'), pd.Timestamp('2026-10-25')
MODELS = {'BASE': (40., 75.), 'S60': (40., 60.), 'S50': (40., 50.),
          'T50': (50., 75.), 'T60': (60., 75.)}
SAVED = ROOT / 'analysis/outputs/codex_vb_parity_stress'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + '\n', encoding='utf-8')


def prereg():
    committed = subprocess.check_output(['git', 'show', 'HEAD:' + PLAN], cwd=ROOT).decode('utf-8')
    assert committed.replace('\r\n', '\n') == (ROOT / PLAN).read_text(encoding='utf-8').replace('\r\n', '\n')
    return subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', PLAN], cwd=ROOT, text=True).strip()


def load_grid():
    warnings.filterwarnings('ignore', message='All-NaN slice encountered')
    warnings.filterwarnings('ignore', message='invalid value encountered in divide')
    with (ROOT / 'scratch_data/g24.pkl').open('rb') as f:
        g = B.ControlledGrid(pickle.load(f))
    return g, pd.DatetimeIndex(g.ts[g.trading])[pd.DatetimeIndex(g.ts[g.trading]).year >= 2018]


def replay(g, name, lo='2018-01-01', hi='2027-01-01', slips=1, through=1.):
    p = dict(B.VB, tp_pts=MODELS[name][0], sl_pts=MODELS[name][1])
    signals, _ = B.vault_break24(g, **p)
    times = pd.DatetimeIndex(g.ts[signals.day.to_numpy()])
    signals = signals[(times >= lo) & (times < hi)]
    early = B._early(g)
    last = np.where(early, B.minute(p['early_last']), B.minute(p['last']))
    days = signals.day.to_numpy()
    sig = np.c_[days, signals.dj, signals.stop, signals.target,
                np.minimum(signals.exit_j, g.last_j[days]), last[days]]
    return B.frame(B.vb_engine(g.o, g.h, g.l, g.c, np.ascontiguousarray(sig, float),
                              p['max_trades'], through, 0), g, slips)


def daily(t, days):
    return t.groupby('date').net.sum().reindex(days, fill_value=0.)


def streak(x):
    best = current = 0
    for value in x:
        current = current + 1 if value < 0 else 0
        best = max(best, current)
    return best


def measure(t, days, name='', period=''):
    t = t[t.date.isin(days)]
    x = t.net.to_numpy(float)
    d = daily(t, days)
    if not len(days):
        return dict(model=name, period=period, trades=0)
    d0 = pd.concat([pd.Series([0.], index=[days[0] - pd.Timedelta(days=1)]), d])
    m = M.perf(d0, t.net)
    winners, losers = x[x > 0], x[x < 0]
    aw = float(winners.mean()) if len(winners) else np.nan
    al = float(-losers.mean()) if len(losers) else np.nan
    m.update(model=name, period=period, side='all/long', sessions=len(days),
             first_date=str(days[0].date()), last_date=str(days[-1].date()),
             gross=float(t.pnl.sum()), total=float(x.sum()), total_cost=float((t.pnl - t.net).sum()),
             t=float(x.mean() / x.std(ddof=1) * np.sqrt(len(x))) if len(x) > 1 and x.std(ddof=1) else np.nan,
             average_win=aw, average_loss=al, payoff_ratio=aw / al if al > 0 else np.nan,
             realized_breakeven_win_rate=al / (aw + al) if aw > 0 and al > 0 else np.nan,
             max_trade_dd=R.max_dd(x) if len(x) else 0., longest_losing_streak=streak(x),
             stop_count=int(t.kind.eq(0).sum()), target_count=int(t.kind.eq(1).sum()),
             time_count=int(t.kind.eq(2).sum()))
    return m


def period_rows(t, days, name):
    rows = []
    groups = [('2018-22', days[days.year <= 2022]), ('2023+', days[days.year >= 2023]),
              ('all', days), ('requested_partial', days[(days >= START) & (days <= ASOF)]),
              ('last42_available', days[-42:])]
    groups += [(str(y), days[days.year == y]) for y in sorted(set(days.year))]
    for label, ds in groups:
        if len(ds):
            rows.append(measure(t, ds, name, label))
    return rows


def bootstrap_recent(t, days):
    recent_days = days[(days >= START) & (days <= ASOF)]
    recent = daily(t, recent_days)
    n = len(recent)
    if n < 10:
        raise ValueError('Insufficient recent sessions for registered block length')
    pools = {'design_2018_2022': days[days.year <= 2022], 'all_pre_window': days[days < START]}
    result = []
    for number, (label, pool_days) in enumerate(pools.items()):
        pool = daily(t, pool_days)
        # Reuse the repository's block generator; first N columns have the registered horizon.
        paths = R.fan_paths(pool, n=5000, block=10, seed=SEED + number)
        horizon = paths[:, :n]
        draws_net = horizon[:, -1]
        draws_dd = MC._maxdd(horizon)
        recent_paths = R.fan_paths(recent, n=5000, block=10, seed=SEED + 100 + number)
        delta = recent_paths[:, -1] / n - paths[:, -1] / len(pool)
        actual_net, actual_dd = float(recent.sum()), R.max_dd(recent)
        empirical = []
        x = pool.to_numpy(float)
        for j in range(len(x) - n + 1):
            w = x[j:j + n]
            empirical.append(dict(pool=label, first=str(pool_days[j].date()),
                                  last=str(pool_days[j + n - 1].date()),
                                  net=float(w.sum()), max_dd=R.max_dd(w)))
        e = pd.DataFrame(empirical)
        e.to_csv(OUT / ('historical_windows_' + label + '.csv'), index=False)
        net_tail = float((1 + (draws_net <= actual_net).sum()) / (len(draws_net) + 1))
        dd_tail = float((1 + (draws_dd >= actual_dd).sum()) / (len(draws_dd) + 1))
        ci = np.percentile(delta, [5, 50, 95]).tolist()
        verdict = ('unusually weak; investigate deterioration' if net_tail <= .05 and ci[2] < 0
                   else 'within historical range; deterioration inconclusive' if net_tail > .05 and dd_tail > .05
                   else 'WATCH')
        result.append(dict(pool=label, sessions=n, actual_net=actual_net, actual_max_dd=actual_dd,
                           earlier_pool_sessions=len(pool), bootstrap_runs=5000, block_sessions=10,
                           bootstrap_net_p5_p50_p95=np.percentile(draws_net, [5, 50, 95]).tolist(),
                           bootstrap_dd_p5_p50_p95=np.percentile(draws_dd, [5, 50, 95]).tolist(),
                           net_lower_tail_frequency=net_tail, dd_upper_tail_frequency=dd_tail,
                           recent_minus_prior_daily_mean_90ci=ci,
                           historical_window_count=len(e), overlapping_window_net_lower_fraction=float(e.net.le(actual_net).mean()),
                           overlapping_window_dd_upper_fraction=float(e.max_dd.ge(actual_dd).mean()),
                           historical_verdict=verdict, current_account_verdict='INSUFFICIENT VERIFIED FILLS'))
    eq = daily(t, days).cumsum()
    peak = np.maximum.accumulate(np.maximum(eq.to_numpy(), 0))
    context = pd.DataFrame(dict(date=days, daily=daily(t, days).to_numpy(), equity=eq.to_numpy(),
                                eod_drawdown=peak - eq.to_numpy()))
    context.to_csv(OUT / 'baseline_equity_daily.csv', index=False)
    carry = context[context.date.ge(START)]
    prior = context[context.date.lt(START)]
    dump('recent_diagnostic.json', dict(requested_start=str(START.date()), requested_end=str(ASOF.date()),
        available_end=str(days[-1].date()), missing_after_cutoff=True, requested_observed_sessions=n,
        carried_drawdown_at_window_start=float(prior.eod_drawdown.iloc[-1]),
        maximum_carried_eod_drawdown_inside_window=float(carry.eod_drawdown.max()),
        ending_carried_eod_drawdown=float(carry.eod_drawdown.iloc[-1]), comparisons=result,
        caution='Conditional historical comparisons, not independent p-values or proof of permanent deterioration.'))


def archive_audit():
    rows, sources = [], []
    for path in sorted((ROOT / 'live/trades').glob('2026*.csv')):
        with path.open(newline='', encoding='utf-8-sig') as stream:
            for number, row in enumerate(csv.reader(stream), 1):
                if len(row) != len(COLS):
                    raise ValueError('Unsupported archived chart log width')
                r = dict(zip(COLS, row))
                if r['tag'] not in ('VB', 'VB-2'):
                    continue
                r.update(source=path.relative_to(ROOT).as_posix(), source_line=number)
                rows.append(r)
        sources.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path)))
    frame = pd.DataFrame(rows)
    keys = [c for c in COLS]
    exact = frame.drop_duplicates(keys) if len(frame) else frame
    closed = exact[exact.event.eq('CLOSE')].copy() if len(exact) else exact
    if len(closed):
        for c in ['contracts', 'entry_price', 'exit_price', 'profit_usd']:
            closed[c] = pd.to_numeric(closed[c])
        closed['gross_from_prices'] = (closed.exit_price - closed.entry_price) * 2 * closed.contracts
        closed['gross_arithmetic_matches'] = np.isclose(closed.gross_from_prices, closed.profit_usd)
    closed.to_csv(OUT / 'archived_chart_closes.csv', index=False)
    groups = []
    for tag, z in closed.groupby('tag') if len(closed) else []:
        groups.append(dict(tag=tag, observed_close_rows=len(z), gross_chart_sum=float(z.profit_usd.sum()),
                           verified_broker_pnl=None, coverage_complete=False))
    events = ['entry_date', 'entry_time', 'entry_price']
    dump('archived_account_audit.json', dict(raw_vb_chart_rows=len(frame), deduplicated_chart_rows=len(exact),
         close_rows=len(closed), observed_market_entry_labels=len(closed.drop_duplicates(events)) if len(closed) else 0,
         copies_are_not_independent=True, chart_tags=groups, sources=sources, complete_broker_fills=False,
         verdict='Cannot diagnose actual account drawdown/edge ratio from incomplete chart logs',
         limitations=['Only October 20-21 chart files are present', 'No verified broker exit ledger or fees',
                      'Chart labels are not verified submission/fill clocks',
                      'Prior order audit includes a rejected event; do not classify its chart CLOSE as an executed loss']))


def mc_export_audit(days):
    """Supplementary stored chart backtest only; no broker execution inference."""
    report = ROOT / 'mc_reports/Backtesting Strategy Performance Report _ @NQ - 30 Minutes NQ Vault Break SP.xlsx'
    raw = pd.read_excel(report, sheet_name='Settings', header=None)
    settings = dict(zip(raw[0].astype(str), raw[1]))
    assert float(settings['TargetPts']) == 40 and float(settings['StopPts']) == 75
    assert float(settings['FlaggedContracts']) == -1 and float(settings['NumContracts']) == 1
    x = read_trades(report)
    x['date'] = x.session
    x['pnl'] = x.pts * 20
    signal = x.exit_signal.astype(str)
    x['kind'] = np.where(signal.str.contains('Stop'), 0, np.where(signal.str.contains('Profit|Target'), 1, 2))
    x['net'] = x.pnl - 7.25 - (1 + x.kind.ne(1).astype(int)) * 5
    end = pd.Timestamp(settings['End Date'])
    complete_end = end.normalize() - pd.Timedelta(days=1) if end.hour * 60 + end.minute < 870 else end.normalize()
    x = x[x.date.le(complete_end)]
    # Settings End Date is not proof of native-bar coverage. Never zero-fill
    # extra weekdays beyond the verified replay calendar from a report setting.
    ext_days = days[(days >= START) & (days <= complete_end)]
    # A no-trade final session is valid; coverage comes from Settings, not last trade.
    if complete_end < days[-1]:
        raise ValueError('Supplementary report is older than the baseline cache')
    x.to_csv(OUT / 'stored_mc_unfiltered_sp_trades.csv', index=False)
    dump('stored_mc_export_audit.json', dict(path=report.relative_to(ROOT).as_posix(), sha256=sha(report),
         settings_end=str(end), settings_nominal_session_cutoff=str(complete_end.date()),
         last_observed_trade_date=str(x.date.max().date()), verified_calendar_cutoff=str(days[-1].date()),
         extended_calendar_verified=False,
         settings={k:str(settings.get(k)) for k in ['TargetPts','StopPts','NumContracts','FlaggedContracts','Compression']},
         recent=measure(x, ext_days, 'stored_MC_unfiltered_SP', 'report_only_recent'),
         caveat='Stored strategy-chart backtest, not broker fills. No zero-filled extension or raw replay after Oct 9.'))


def synthetic():
    assert R.max_dd([10, -4, -8, 7]) == 12
    assert R.max_dd([-7, 3]) == 7
    assert streak([2,-1,-2,0,-1]) == 2
    # Same entry with an earlier exit changes the later eligible-entry count.
    o = np.full((1, 1440), 100.)
    h, l, c = o.copy(), o.copy(), o.copy()
    l[0,602] = 40.
    h[0,632] = 141.
    sig = np.array([[0,600,75,40,870,870], [0,630,75,40,870,870]], float)
    a = B.vb_engine(o,h,l,c,sig,3,1.,0)
    sig[:,2] = 50
    b = B.vb_engine(o,h,l,c,sig,3,1.,0)
    assert len(a) == 1 and len(b) == 2
    dump('synthetic_checks.json', dict(initial_loss_counts_in_dd=True, trade_streak_resets_on_zero=True,
         bracket_change_recomputes_reentries=True, no_cross_account_copy_inflation=True))


def design():
    plan_commit = prereg()
    synthetic()
    g, days = load_grid()
    t = replay(g, 'BASE')
    saved = pd.read_csv(SAVED / 'research_1point_trades.csv', parse_dates=['date'])
    columns = ['day','j0','j1','side','entry','exit','kind','pnl','net']
    assert len(t) == len(saved)
    np.testing.assert_allclose(t[columns], saved[columns], rtol=0, atol=1e-8)
    assert t.date.reset_index(drop=True).equals(saved.date.reset_index(drop=True))
    t.to_csv(OUT / 'BASE_trades.csv', index=False)
    missing=[]
    for r in t.itertuples():
        native=np.logical_and.reduce([np.isfinite(getattr(g,c)[r.day,r.j0:r.j1+1]) for c in 'ohlc'])
        if not native.all():
            missing.append(dict(date=str(r.date.date()),entry_minute=r.j0,exit_minute=r.j1,
                                missing_held_minutes=int((~native).sum())))
    pd.DataFrame(missing,columns=['date','entry_minute','exit_minute','missing_held_minutes']).to_csv(OUT/'missing_held_minutes.csv',index=False)
    metrics = period_rows(t, days, 'BASE')
    ddays = days[days.year <= 2022]
    design_rows = [measure(t, ddays, 'BASE', '2018-22')]
    folds = []
    for name in MODELS:
        z = t[t.date.dt.year.le(2022)].copy() if name == 'BASE' else replay(g, name, hi='2023-01-01')
        if name != 'BASE':
            assert z.date.dt.year.le(2022).all()
            z.to_csv(OUT / (name + '_design_trades.csv'), index=False)
            design_rows.append(measure(z, ddays, name, '2018-22'))
        for lo, hi in [(2018,2020),(2019,2021),(2020,2022)]:
            folds.append(measure(z, ddays[(ddays.year>=lo)&(ddays.year<=hi)], name, f'{lo}-{hi}'))
    d = pd.DataFrame(design_rows)
    base = d[d.model.eq('BASE')].iloc[0]
    decisions = []
    for name in MODELS:
        z = t[t.date.dt.year.le(2022)] if name == 'BASE' else pd.read_csv(OUT/(name+'_design_trades.csv'),parse_dates=['date'])
        row = d[d.model.eq(name)].iloc[0]
        positive_years = int((z.groupby(z.date.dt.year).net.sum() > 0).sum())
        risk = row.max_trade_dd <= .85*base.max_trade_dd and row.total >= .95*base.total
        reward = row.total >= 1.15*base.total and row.max_trade_dd <= 1.05*base.max_trade_dd
        gates = dict(positive=row.total>0, t2=row.t>=2, pf120=row.profit_factor>=1.2,
                     four_positive_years=positive_years>=4, calmar_not_worse=row.calmar>=base.calmar,
                     material_risk_or_reward=risk or reward)
        decisions.append(dict(model=name, target=MODELS[name][0], stop=MODELS[name][1],
                     positive_design_years=positive_years, gates={k:bool(v) for k,v in gates.items()},
                     risk_objective=bool(risk), reward_objective=bool(reward),
                     survives=bool(name!='BASE' and all(gates.values()))))
    d['target'] = [MODELS[n][0] for n in d.model]
    d['stop'] = [MODELS[n][1] for n in d.model]
    cluster, members = PC.cluster_top(d,['target','stop'],'calmar',top=.2,k=1)
    cluster.to_csv(OUT/'design_cluster_context.csv',index=False)
    members.to_csv(OUT/'design_top20_members.csv',index=False)
    pd.DataFrame(folds).to_csv(OUT/'design_folds.csv',index=False)
    d.to_csv(OUT/'design_metrics.csv',index=False)
    pd.DataFrame(metrics).to_csv(OUT/'baseline_metrics.csv',index=False)
    monthly=[]
    for month in pd.period_range('2026-01','2026-10',freq='M'):
        ds=days[days.to_period('M')==month]
        if len(ds):monthly.append(measure(t,ds,'BASE',str(month)))
    pd.DataFrame(monthly).to_csv(OUT/'baseline_2026_monthly.csv',index=False)
    bootstrap_recent(t,days)
    archive_audit()
    mc_export_audit(days)
    inputs=['scratch_data/g24.pkl',str((SAVED/'research_1point_trades.csv').relative_to(ROOT)),
            'analysis/grid.py','analysis/grid24.py','analysis/candidates24.py','analysis/codex_break_vb_onb.py',
            'analysis/codex_vb_recent_risk.py','analysis/metrics.py','analysis/resampling.py','analysis/montecarlo.py']
    manifest=dict(plan_commit=plan_commit, interpreter=sys.executable, python=sys.version,
        versions={k:importlib.metadata.version(k) for k in ['numpy','pandas','numba','scipy','openpyxl']},
        first_cache_date=str(g.dates[0]),last_complete_date=str(days[-1].date()),
        caches_rebuilt=False, packages_installed=False, baseline_trade_for_trade_pass=True,
        hashes={p:sha(ROOT/p) for p in inputs}, alternatives=4,economic_models=5,
        prior_search_context='720 parameter combinations and 314 robustness stresses; previously seen historical data')
    dump('manifest.json',manifest)
    dump('design_gate.json',dict(plan_commit=plan_commit, phase='DESIGN COMPLETE BEFORE ALTERNATIVE VALIDATION',
         models=decisions, survivors=[r['model'] for r in decisions if r['survives']],
         cluster_context_only=True, full_bench_allowed=False))
    print(d[['model','trades','win','total','profit_factor','max_trade_dd','calmar','t']].to_string(index=False),flush=True)
    print('Survivors:',[r['model'] for r in decisions if r['survives']],flush=True)


def validation():
    prereg()
    gate=json.loads((OUT/'design_gate.json').read_text())
    manifest=json.loads((OUT/'manifest.json').read_text())
    assert all(sha(ROOT/p)==v for p,v in manifest['hashes'].items())
    if not gate['survivors']:
        dump('validation_gate.json',dict(status='STOP: no design survivor',validation_alternative_replays=0,
              full_account_bench_run=False, no_recent_rescue=True))
        print('Stopped after the registered design gate; no alternative validation or full bench.')
        return
    g,days=load_grid()
    base=pd.read_csv(OUT/'BASE_trades.csv',parse_dates=['date'])
    rows=[]; verdicts=[]
    for name in gate['survivors']:
        t=replay(g,name,lo='2023-01-01')
        t.to_csv(OUT/(name+'_validation_trades.csv'),index=False)
        complete=pd.concat([pd.read_csv(OUT/(name+'_design_trades.csv'),parse_dates=['date']),t],ignore_index=True)
        rows.extend(period_rows(complete,days,name))
        vdays=days[days.year>=2023]
        delta=daily(t,vdays)-daily(base,vdays)
        R.bootstrap(daily(t,vdays),n=5000,block=10,seed=SEED).to_csv(OUT/(name+'_validation_bootstrap.csv'))
        dump(name+'_validation_permutation.json',R.permutation(daily(t,vdays),n=5000,seed=SEED))
        paths=R.fan_paths(delta,n=5000,block=10,seed=SEED)
        ci=np.percentile(paths[:,-1]/len(vdays)*252,[5,50,95]).tolist()
        bm,tm=measure(base,vdays,'BASE','2023+'),measure(t,vdays,name,'2023+')
        decision=next(r for r in gate['models'] if r['model']==name)
        same_risk=tm['max_trade_dd']<=.85*bm['max_trade_dd'] and tm['total']>=.95*bm['total']
        same_reward=tm['total']>=1.15*bm['total'] and tm['max_trade_dd']<=1.05*bm['max_trade_dd']
        same_objective=(decision['risk_objective'] and same_risk) or (decision['reward_objective'] and same_reward)
        folds=pd.read_csv(OUT/'design_folds.csv')
        z=folds[folds.model.eq(name)].merge(folds[folds.model.eq('BASE')],on='period',suffixes=('_new','_base'))
        fold_pass=bool((z.total_new>0).all() and (z.calmar_new>=z.calmar_base).all())
        verdicts.append(dict(model=name,positive_validation=tm['total']>0,
            same_material_objective=bool(same_objective),all_three_design_fold_calmar_not_worse=fold_pass,
            paired_annual_net_delta_90ci=ci,
            proceeds_to_conditional_checks=bool(tm['total']>0 and same_objective and fold_pass)))
    pd.DataFrame(rows).to_csv(OUT/'validation_metrics.csv',index=False)
    dump('validation_gate.json',dict(models=verdicts,validation_alternative_replays=len(verdicts),
         conditional_survivors=[v['model'] for v in verdicts if v['proceeds_to_conditional_checks']],
         full_account_bench_run=False))
    print(json.dumps(verdicts,indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=['design','validation'],required=True)
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'.gitignore').write_text('numba_cache/\n',encoding='utf-8')
    design() if args.phase=='design' else validation()
