"""Descriptive shared-loss audit; see agents/codex/plans/book_joint_losses.md.
Run: python analysis/codex_book_joint_losses.py --grid C:/TradingVault/scratch_data/g24.pkl
Writes only analysis/outputs/codex_book_joint_losses/. Never touches live files.
"""
import argparse
import ast
import hashlib
import itertools
import json
import pickle
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_book_joint_losses'
CLI_ARGS = sys.argv[1:]
# Older shared modules read argv[1] as a cache folder during import.
sys.argv = [sys.argv[0], str(OUT / '_cache')]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics as metrics
import resampling as resampling
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
from combine_levers_test import ONB30
import bridge_monday_confirm as bridge
import dual_thrust_test as dt
import twin_continuation_test as twin
import jump_lib as jump
from jump_fade_paths import jf_trades

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_book_joint_losses'
SEED = 20261113


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def roster():
    tree = ast.parse((ROOT / 'analysis/bench150.py').read_text(encoding='utf-8'))
    node = next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'LIVE_EVAL' for t in n.targets))
    return ast.literal_eval(node.value)


def mc_end(path):
    st = pd.read_excel(path, sheet_name='Settings', header=None)
    d = dict(zip(st[0].astype(str), st[1]))
    end = pd.Timestamp(d['End Date'])
    return end.normalize() if end.hour >= 16 else end.normalize() - pd.offsets.BDay()


def build_trades(g, spec):
    """Normalize the benchmark's trade sources; retain actual clock intervals."""
    rows, sources, checks = [], [], {}
    atr = g.daily_atr(15)
    risk_mult = {'ONB30': .25, 'LDF': REPORTS['LDF_MC'][1]}

    def add(k, en, ex, side, entry, exit_, net_nq, kind, book_day=None):
        en, ex = pd.Timestamp(en), pd.Timestamp(ex)
        day = ex.normalize() if book_day is None else pd.Timestamp(book_day)
        if day.dayofweek >= 5:
            day += pd.offsets.BDay()
        if isinstance(spec[k], tuple):
            rr = g.ts.searchsorted(day.to_datetime64())
            sd = risk_mult[k] * atr[rr]
            qty = np.floor(spec[k][1] / (sd * 2)) if np.isfinite(sd) and sd > 0 else 0
        else:
            qty = spec[k]
        rows.append(dict(strategy=k, entry_ts=en, exit_ts=ex, date=day, side=int(side),
                         entry=float(entry), exit=float(exit_), kind=str(kind), qty=float(qty),
                         net=float(net_nq) / 10 * qty))

    for k, path in [('ONB30', ONB30), ('LDF', REPORTS['LDF_MC'][0])]:
        print('loading', k, flush=True)
        sources.append(path)
        raw = load_mc(g, path)
        slipped = with_slippage(raw)
        for r, s in zip(raw.itertuples(), slipped.itertuples()):
            en = pd.Timestamp(g.ts[r.day]) + pd.Timedelta(minutes=int(r.j0))
            ex = pd.Timestamp(g.ts[r.day]) + pd.Timedelta(minutes=int(r.j1))
            net = (s.exit - s.entry) * s.side * 20 - 7.25
            add(k, en, ex, r.side, r.entry, r.exit, net, r.kind)

    sources.append(bridge.F)
    raw = pd.read_excel(bridge.F, sheet_name='List of Trades', header=2)
    en = raw[raw.Type.astype(str).str.startswith('Entry')].reset_index(drop=True)
    ex = raw[raw.Type.astype(str).str.startswith('Exit')].reset_index(drop=True)
    bt = bridge.load_bridge_mc(g)
    assert len(en) == len(ex) == len(bt)
    for e, x, t in zip(en.itertuples(), ex.itertuples(), bt.itertuples()):
        # Sunday 19:00 stamp represents the end of the entry chart bar. Loader
        # assumes 19:00 fill; retain this documented convention for occupancy.
        net = (t.exit - t.entry) * 20 - 7.25
        add('MON_BR', e.Date, x.Date, 1, e.Price, x.Price, net, t.kind, t.date)

    print('simulating TWIN', flush=True)
    b = twin.flatten(g)
    t = twin.simulate(b, max_stop_mult=1.0, v21=True)
    t = t[t.date >= '2018-01-01']
    for r in t.itertuples():
        add('TWIN', r.edate + pd.Timedelta(minutes=int(r.ej)),
            r.date + pd.Timedelta(minutes=int(r.xj)), r.side, r.entry, r.exit, r.net, r.kind)
    del b

    print('simulating DT', flush=True)
    days = dt.load()
    t = dt.run(days, dt.setups(days))
    for r in t.itertuples():
        en = r.date + pd.Timedelta(minutes=int(r.sig_time // 100 * 60 + r.sig_time % 100 + 1))
        ex = r.date + pd.Timedelta(minutes=int(r.exit_time // 100 * 60 + r.exit_time % 100))
        add('DT', en, ex, r.side, r.entry, r.exit, r.net, r.kind)

    print('simulating JF', flush=True)
    # Independent caches only; never mutate the supplied g24 cache or live paths.
    jump.CACHE = str(OUT / '_cache')
    Path(jump.CACHE).mkdir(exist_ok=True)
    t, market = jf_trades()
    for r in t.itertuples():
        i = np.searchsorted(market.ts, r.ts.to_datetime64())
        ex = pd.Timestamp(market.ts[i + int(r.mins) - 1])
        add('JF', r.ts, ex, r.side, r.entry, r.exit, r.net - 5.5, r.why)

    print('loading NBL', flush=True)
    path = 'analysis/outputs/bridge_noise_15m_trades_rth_longs.csv'
    sources.append(path)
    t = pd.read_csv(path, parse_dates=['date'])
    mismatch = 0
    for r in t[t.date >= '2018-01-01'].itertuples():
        rr = np.searchsorted(g.ts, r.date.to_datetime64())
        mismatch += int(rr != r.row)
        add('NBL', r.date + pd.Timedelta(minutes=int(r.j0)),
            r.date + pd.Timedelta(minutes=int(r.j1)), r.side, r.entry, r.exit,
            (r.exit - r.entry) * r.side * 20 - 7.25, r.kind)
    checks['nbl_row_mismatches_corrected_by_date'] = mismatch
    # NBL paths in bench150 do not add ticks to this CSV. Match that convention
    # here, and disclose it instead of silently changing the portfolio base.
    checks['nbl_cost_convention'] = '7.25/NQ only, same as bench150 NBL paths; no extra tick slippage'
    return pd.DataFrame(rows), sources, checks


def statistics(daily, trades, label):
    output = []
    for per, mask in periods(daily.index):
        for k in [*daily.columns, 'BOOK']:
            d = daily.loc[mask].sum(axis=1) if k == 'BOOK' else daily.loc[mask, k]
            t = trades[trades.date.isin(d.index)]
            if k != 'BOOK': t = t[t.strategy == k]
            for side, keep in [('ALL', np.ones(len(t), bool)), ('LONG', t.side > 0), ('SHORT', t.side < 0)]:
                x = t.loc[keep]
                dd = d if side == 'ALL' else x.groupby('date').net.sum().reindex(d.index, fill_value=0)
                row = metrics.perf(dd, x.net, capital=150000)
                row.update(period=per, strategy=k, side=side, series=label,
                           t_trade=x.net.mean() / x.net.std() * np.sqrt(len(x)) if len(x) > 1 else np.nan)
                output.append(row)
    return pd.DataFrame(output)


def periods(index):
    return [('ALL', np.ones(len(index), bool)), ('2018-22', index.year <= 2022), ('2023+', index.year >= 2023)]


def tail_stats(x, n):
    b = x.sum(axis=1)
    ix = np.argsort(b)[:n]
    return x[ix].mean(axis=0), ix


def daily_audit(daily):
    pair, tail, summary, nulls, bootstrap = [], [], [], [], []
    rng = np.random.default_rng(SEED)
    for period, mask in periods(daily.index):
        d = daily.loc[mask]
        x = d.to_numpy(); book = x.sum(1); lost = x < -1e-7
        for i, j in itertools.combinations(range(x.shape[1]), 2):
            active = (abs(x[:, i]) > 1e-7) & (abs(x[:, j]) > 1e-7)
            a, b = lost[active, i], lost[active, j]
            n = len(a); joint = int(np.sum(a & b))
            pair.append(dict(period=period, a=d.columns[i], b=d.columns[j], both_active=n,
                             correlation=d.iloc[:, i].corr(d.iloc[:, j]), joint_loss_days=joint,
                             p_b_loss_if_a_loss=float(b[a].mean()) if a.any() else np.nan,
                             p_b_loss_both_active=float(b.mean()) if n else np.nan,
                             joint_independent_days=float(n * a.mean() * b.mean()) if n else np.nan,
                             joint_negative_dollars=float(-np.minimum(x[lost[:, i] & lost[:, j]][:, [i, j]], 0).sum())))
        for frac in [.05, .01]:
            n = max(1, int(np.ceil(len(x) * frac))); contrib, ix = tail_stats(x, n)
            for k, c in zip(d.columns, contrib):
                tail.append(dict(period=period, fraction=frac, strategy=k, tail_days=n, mean_contribution=c,
                                 mean_book=book[ix].mean(), negative_days=int((d.loc[d.index[ix], k] < 0).sum())))
            if frac == .05:
                # Joint block sampling retains actual cross-strategy dependence.
                reps = np.empty((2000, x.shape[1]))
                for r in range(len(reps)):
                    starts = rng.integers(0, len(x), int(np.ceil(len(x) / 20)))
                    idx = ((starts[:, None] + np.arange(20)) % len(x)).ravel()[:len(x)]
                    reps[r] = tail_stats(x[idx], n)[0]
                for j, k in enumerate(d.columns):
                    bootstrap.append(dict(period=period, strategy=k,
                                          p05=np.percentile(reps[:, j], 5), p95=np.percentile(reps[:, j], 95)))
        neg = np.minimum(x, 0); pos = np.maximum(x, 0)
        worst = np.argsort(book)[:int(np.ceil(len(x) * .05))]
        summary.append(dict(period=period, days=len(d), loss_days=int((book < 0).sum()),
                            multi2_days=int((lost.sum(1) >= 2).sum()), multi3_days=int((lost.sum(1) >= 3).sum()),
                            tail5_multi2=int((lost[worst].sum(1) >= 2).sum()),
                            tail5_multi3=int((lost[worst].sum(1) >= 3).sum()),
                            tail5_gross_loss=-neg[worst].sum(), tail5_winner_offset=pos[worst].sum(),
                            tail5_mean=book[worst].mean(), min_day=book.min(), max_dd=resampling.max_dd(book)))
        groups = list(pd.Series(np.arange(len(d)), index=d.index).groupby([d.index.year, d.index.dayofweek]))
        for run in range(1000):
            y = x.copy()
            for _, group in groups:
                idx = group.to_numpy()
                for j in range(x.shape[1]): y[idx, j] = x[rng.permutation(idx), j]
            nulls.append(dict(period=period, run=run, multi2_days=int(((y < 0).sum(1) >= 2).sum()),
                              multi3_days=int(((y < 0).sum(1) >= 3).sum()),
                              tail5_mean=np.sort(y.sum(1))[:len(worst)].mean()))
    for name, data in [('pairs', pair), ('tails', tail), ('summary', summary), ('null', nulls), ('tail_bands', bootstrap)]:
        pd.DataFrame(data).to_csv(OUT / f'{name}.csv', index=False)


def drawdowns(daily):
    out = []
    for period, mask in periods(daily.index):
        d = daily.loc[mask]; x = d.sum(axis=1).to_numpy(); eq = np.r_[0., x.cumsum()]
        peak, start = 0., 0; episodes = []; trough, trough_i = 0., 0
        for i in range(1, len(eq)):
            if eq[i] >= peak:
                if trough < peak: episodes.append((start, trough_i, i, peak - trough))
                peak, start, trough, trough_i = eq[i], i, eq[i], i
            elif eq[i] < trough:
                trough, trough_i = eq[i], i
        if trough < peak: episodes.append((start, trough_i, None, peak - trough))
        for rank, (s, t, recovery, depth) in enumerate(sorted(episodes, key=lambda z: -z[3])[:10], 1):
            row = dict(period=period, rank=rank, start=str(d.index[s].date()), trough=str(d.index[t-1].date()),
                       recovery=str(d.index[recovery-1].date()) if recovery else '', depth=depth, days=t-s)
            row.update(d.iloc[s:t].sum().to_dict())
            assert np.isclose(sum(row[k] for k in d.columns), -depth)
            out.append(row)
    pd.DataFrame(out).to_csv(OUT / 'drawdowns.csv', index=False)


def clock_audit(g, trades, daily):
    """Single common minute price, real calendar intervals. Costs paid at entry.
    Arrays only in RAM; don't persist huge grids or use synthetic adverse marks.
    """
    dates = pd.DatetimeIndex(g.ts); n = len(dates) * 1440; keys = list(daily.columns)
    marks, positions = [], []; bad = 0
    close = pd.Series(g.c.ravel()).ffill().to_numpy()
    assert np.allclose((close[np.isfinite(close)] - 10000)*2 + (close[np.isfinite(close)] - 10000)*-2, 0)
    for k in keys:
        closed = np.zeros(n); opened = np.zeros(n); pos = np.zeros(n, dtype=np.float32)
        for r in trades[trades.strategy == k].itertuples():
            i = int((r.entry_ts - dates[0]).total_seconds() // 60)
            j = int((r.exit_ts - dates[0]).total_seconds() // 60)
            assert 0 <= i <= j < n
            q = r.qty; cost = (r.exit-r.entry)*r.side*2*q-r.net
            p = (close[i:j+1] - r.entry)*r.side*2*q - cost
            bad += int(np.isnan(p).sum())
            p = np.nan_to_num(p, nan=-cost)
            p[-1] = r.net
            opened[i:j] += p[:-1]; closed[j] += r.net
            pos[i:j+1] += r.side*q
        mark = closed.cumsum() + opened
        assert np.isclose(mark[-1], trades.loc[trades.strategy == k, 'net'].sum())
        marks.append(mark.reshape(-1, 1440)); positions.append(pos.reshape(-1, 1440))
    marks, positions = np.stack(marks), np.stack(positions)
    selected = np.searchsorted(g.ts, daily.index.to_numpy())
    # EOD cash mark by trading date: any Sunday closes roll into Monday naturally.
    eod = marks[:, selected, -1]
    mark_daily = np.diff(eod, axis=1, prepend=np.zeros((len(keys), 1))).T
    md = pd.DataFrame(mark_daily, index=daily.index, columns=keys)
    md.to_csv(OUT / 'close_mark_daily.csv', index_label='date')
    pairs, hourly, shocks, recovery_rows = [], [], [], []
    for period, mask in periods(daily.index):
        rows = selected[mask]; pp = positions[:, rows]; mm = marks[:, rows]
        # Include Sunday evening in Monday hourly statistics (kept separate label).
        sundays = rows - 1; sundays = sundays[pd.DatetimeIndex(g.ts[sundays]).dayofweek == 6]
        for i, j in itertools.combinations(range(len(keys)), 2):
            both = (pp[i] != 0) & (pp[j] != 0)
            pairs.append(dict(period=period, a=keys[i], b=keys[j],
                              both_minutes=int(both.sum()), same_side_minutes=int((pp[i]*pp[j] > 0).sum()),
                              opposite_minutes=int((pp[i]*pp[j] < 0).sum()),
                              overlap_fraction_of_a=float(both.sum()/max(1,(pp[i] != 0).sum())),
                              overlap_fraction_of_b=float(both.sum()/max(1,(pp[j] != 0).sum()))))
        for hour in range(24):
            sl = slice(hour*60, (hour+1)*60)
            prev = marks[:, rows, hour*60-1] if hour else marks[:, rows-1, -1]
            pnl = mm[:, :, (hour+1)*60-1] - prev
            bpnl = pnl.sum(0); p = pp[:, :, sl]
            row = dict(period=period, hour=hour, days=len(rows),
                       occupied_fraction=float(np.any(p != 0, axis=0).mean()),
                       multi_same_side_fraction=float((((p>0).sum(0)>=2) | ((p<0).sum(0)>=2)).mean()),
                       mean_abs_net_mnq=float(np.abs(p.sum(0)).mean()),
                       negative_book_hour_sum=float(-np.minimum(bpnl,0).sum()),
                       mean_book_hour=float(bpnl.mean()))
            row.update({k:float(pnl[i].sum()) for i,k in enumerate(keys)})
            hourly.append(row)
        for ii, r in enumerate(rows):
            baseline = marks[:, r-1, -1]
            rel = marks[:, r] - baseline[:, None]
            j = int(np.argmin(rel.sum(0))); piece = rel[:,j]; p = positions[:,r,j]
            row=dict(period=period,date=str(pd.Timestamp(g.ts[r]).date()),minute=j,
                     book=float(piece.sum()), losing_pieces=int((piece<0).sum()),
                     active=int((p != 0).sum()), net_mnq=float(p.sum()),
                     gross_mnq=float(abs(p).sum()), long_pieces=int((p>0).sum()), short_pieces=int((p<0).sum()))
            row.update({k:float(piece[i]) for i,k in enumerate(keys)})
            shocks.append(row)
        for r in sundays:
            rel=marks[:,r,1140:]-marks[:,r,1139,None]
            recovery_rows.append(dict(period=period,date=str(pd.Timestamp(g.ts[r]).date()),
                                      sunday_1900_2359_net=float(rel[:,-1].sum()),
                                      sunday_worst=float(rel.sum(0).min())))
    for name,data in [('overlap',pairs),('hourly',hourly),('minute_troughs',shocks),('sunday',recovery_rows)]:
        pd.DataFrame(data).to_csv(OUT / f'{name}.csv',index=False)
    checks=dict(missing_mark_minutes=bad, common_price_cancellation_pass=True,
                maximum_eod_mark_vs_exit_booking_difference=float(abs(md-daily).to_numpy().max()),
                eod_mark_vs_exit_booking_diff_days=int((abs(md-daily).max(axis=1)>1e-5).sum()))
    return md, checks


def market_audit(g,daily):
    rows=np.searchsorted(g.ts,daily.index.to_numpy()); atr=g.daily_atr(15)[rows]
    rth=g.c[rows,900]-g.o[rows,511]; first=g.c[rows,570]-g.o[rows,511]
    span=np.nanmax(g.h[rows,511:901],axis=1)-np.nanmin(g.l[rows,511:901],axis=1)
    gap=g.o[rows,511]-g.c[rows-1,900]
    tab=daily.copy();tab['BOOK']=daily.sum(axis=1);tab['rth_points']=rth
    tab['first_hour_points']=first;tab['range_over_atr']=span/atr;tab['gap_points']=gap
    tab.to_csv(OUT/'daily.csv',index_label='date')
    summaries=[]
    for per,mask in periods(daily.index):
        d=tab.loc[mask];tail=d.nsmallest(int(np.ceil(len(d)*.05)),'BOOK')
        for label,sub in [('all',d),('tail5',tail)]:
            summaries.append(dict(period=per,sample=label,days=len(sub),
                                  rth_down_fraction=float((sub.rth_points.dropna()<0).mean()),
                                  first_hour_down_fraction=float((sub.first_hour_points.dropna()<0).mean()),
                                  gap_down_fraction=float((sub.gap_points.dropna()<0).mean()),
                                  median_range_atr=float(sub.range_over_atr.median()),
                                  median_abs_rth=float(sub.rth_points.abs().median())))
    pd.DataFrame(summaries).to_csv(OUT/'market_context.csv',index=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--grid',required=True);args=p.parse_args(CLI_ARGS)
    OUT.mkdir(parents=True,exist_ok=True)
    spec=roster();print('book:',spec,flush=True)
    cfg=json.loads((ROOT/'live/expected_setup.json').read_text())
    mapping={'ONB30':'ONB','MON_BR':'MON_BR','TWIN':'TW','DT':'DT','JF':'JF','NBL':'NBL','LDF':'LDF'}
    for k,v in spec.items():
        tag=mapping[k]+'150-5';c=cfg['charts'][tag]
        if not isinstance(v,tuple): assert c['qty']==v,(tag,c,v)
    with open(args.grid,'rb') as f:g=pickle.load(f)
    print('grid:',g.ts[0],g.ts[-1],flush=True)
    trades,sources,checks=build_trades(g,spec)
    coverage={s:str(mc_end(s).date()) for s in sources if s.endswith('.xlsx')}
    end=min(pd.Timestamp(d) for d in coverage.values())
    end=min(end,pd.Timestamp(g.ts[g.trading[-1]]))
    start=pd.Timestamp('2018-03-01') # conservative: Bridge export starts 2018-02-25
    dates=pd.DatetimeIndex(g.ts[g.trading]);dates=dates[(dates>=start)&(dates<=end)]
    # Avoid undefined overnight P&L at the first boundary: omit trades entered
    # before the beginning of the audit. Existing records kept separately below.
    before=(trades.date>=start)&(trades.entry_ts<start)
    checks['boundary_trades_omitted']=int(before.sum())
    trades=trades[trades.date.isin(dates)&(trades.entry_ts>=start)].copy()
    assert (trades.exit_ts>=trades.entry_ts).all()
    assert (trades.qty>=0).all()
    daily=trades.pivot_table(index='date',columns='strategy',values='net',aggfunc='sum').reindex(index=dates,columns=list(spec),fill_value=0).fillna(0)
    assert np.isclose(daily.to_numpy().sum(),trades.net.sum())
    trades.to_csv(OUT/'trades.csv',index=False)
    daily_audit(daily);drawdowns(daily);market_audit(g,daily)
    md,clock_checks=clock_audit(g,trades,daily);checks.update(clock_checks)
    statistics(daily,trades,'realized').to_csv(OUT/'metrics.csv',index=False)
    pd.concat([daily.groupby(daily.index.year).sum(),daily.sum(axis=1).groupby(daily.index.year).sum().rename('BOOK')],axis=1).to_csv(OUT/'yearly.csv',index_label='year')
    for per,mask in periods(md.index):
        resampling.bootstrap(md.loc[mask].sum(axis=1),n=2000,block=20,seed=SEED,capital=150000).to_csv(OUT/f'book_bootstrap_{per.replace("+","on")}.csv')
    fingerprints={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources}
    provenance=dict(code_commit=git('rev-parse','HEAD'),book_source_commit='a5aeffec',roster=spec,
                    start=str(start.date()),end=str(end.date()),days=len(dates),trades=len(trades),
                    coverage=coverage,source_sha256=fingerprints,grid=str(Path(args.grid).resolve()),
                    grid_start=str(pd.Timestamp(g.ts[0]).date()),grid_end=str(pd.Timestamp(g.ts[-1]).date()),checks=checks)
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2))
    print(pd.read_csv(OUT/'summary.csv').to_string(index=False),flush=True)
    print('checks:',checks,flush=True)


if __name__=='__main__':main()
