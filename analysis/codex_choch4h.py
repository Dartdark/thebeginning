"""Frozen 4h CHoCH baseline. Research only; no trading connections."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import warnings
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_choch4h_20261028'
os.environ['NUMBA_CACHE_DIR'] = str(OUT / 'cache/numba')
from grid import _walk
import metrics as M
import codex_nq_rth_gap_down as loader
from codex_hunt_v2_ldf_delta import tstat
from codex_hunt_v2_ldf_delta_design import nw_t


def signals(bars, radius):
    """Pivot values become usable only on their confirmation bar."""
    history, highs, lows, out = [], [], [], []
    trend, previous = 0, None
    consumed = set()
    for b in bars:
        if not b['valid']:
            history, highs, lows, trend, previous = [], [], [], 0, None
            continue
        history.append(b)
        changed = False
        if len(history) >= 2 * radius + 1:
            window = history[-(2 * radius + 1):]
            pivot = window[radius]
            others = window[:radius] + window[radius + 1:]
            if all(pivot['high'] > x['high'] for x in others):
                highs.append((pivot['end'], pivot['high']))
                changed = True
            if all(pivot['low'] < x['low'] for x in others):
                lows.append((pivot['end'], pivot['low']))
                changed = True
        if changed and len(highs) >= 2 and len(lows) >= 2:
            if highs[-1][1] > highs[-2][1] and lows[-1][1] > lows[-2][1]:
                trend = 1
            elif highs[-1][1] < highs[-2][1] and lows[-1][1] < lows[-2][1]:
                trend = -1
        side = 0
        if previous is not None and highs and lows:
            if trend == 1 and previous >= lows[-1][1] and b['close'] < lows[-1][1]:
                side, stop, broken = -1, highs[-1][1], lows[-1][0]
            elif trend == -1 and previous <= highs[-1][1] and b['close'] > highs[-1][1]:
                side, stop, broken = 1, lows[-1][1], highs[-1][0]
            if side and (side, broken) not in consumed:
                out.append(dict(signal=b['end'], close=b['close'], side=side,
                                stop=stop, broken_pivot=broken, radius=radius))
                consumed.add((side, broken))
                trend = side
        previous = b['close']
    return pd.DataFrame(out, columns=['signal','close','side','stop','broken_pivot','radius'])


def four_hour_bars(g, valid):
    # Full windows 17:01..21:00, 21:01..01:00, ..., 09:01..13:00 CT.
    flat = {k: getattr(g, k).ravel() for k in 'ohlc'}
    v = valid.ravel()
    bars = []
    for day in range(g.D):
        for minute in (60, 300, 540, 780, 1260):
            end = day * 1440 + minute
            start = end - 239
            if start < 0:
                continue
            dt = pd.Timestamp(g.ts[day]) + pd.Timedelta(minutes=minute)
            # These windows are entirely closed on Saturday and Sunday before 17h.
            if (dt.dayofweek == 5 or (dt.dayofweek == 6 and minute != 1260)
                    or (dt.dayofweek == 4 and minute == 1260)):
                continue
            ok = bool(v[start:end + 1].all())
            bars.append(dict(end=end, valid=ok,
                             high=float(np.max(flat['h'][start:end+1])) if ok else np.nan,
                             low=float(np.min(flat['l'][start:end+1])) if ok else np.nan,
                             close=float(flat['c'][end]) if ok else np.nan))
    return bars


def expected_minutes(g):
    n = g.D * 1440
    minutes = np.arange(n) % 1440
    days = pd.DatetimeIndex(g.ts).dayofweek.to_numpy().repeat(1440)
    # Close-labelled bars: the final pre-halt minute closes at 16:00.
    return ~(((minutes > 960) & (minutes <= 1020)) | (days == 5) |
             ((days == 4) & (minutes > 960)) | ((days == 6) & (minutes <= 1020)))


def trade_ledger(g, valid, events, timing):
    arrays = [getattr(g, k).ravel() for k in 'ohlc']
    o, h, l, c = arrays
    good = valid.ravel()
    missing = np.cumsum(expected_minutes(g) & ~good)
    rows, blocked = [], -1
    for e in events.to_dict('records'):
        j0 = int(e['signal']) + (2 if timing == 'executable' else 1)
        if j0 <= blocked or j0 >= len(o):
            continue
        entry = o[j0] if timing == 'executable' else e['close']
        if not good[j0]:
            rows.append(dict(**e, entry_j=j0, state='missing_entry'))
            continue
        side, stop = int(e['side']), float(e['stop'])
        risk = side * (entry - stop)
        if risk <= 0:
            rows.append(dict(**e, entry_j=j0, state='invalid_risk'))
            continue
        target = entry + side * risk
        if side * (o[j0] - stop) <= 0:
            end, price, kind = j0, o[j0], 0
        else:
            end, price, kind, worst = _walk(o, h, l, c, j0, len(o)-1, side, stop, target, 1.)
        blocked = int(end)
        unknown = missing[end] - (missing[j0-1] if j0 else 0)
        state = 'unresolved_missing' if unknown else ('censored_end' if kind == 2 else 'resolved')
        row = dict(**e, entry_j=j0, exit_j=int(end), entry=float(entry), exit=float(price),
                   target=float(target), risk=float(risk), kind=int(kind), state=state,
                   missing_expected_minutes=int(unknown))
        if state == 'resolved':
            row.update(gross_mnq=float(side*(price-entry)*2), commission_mnq=1.24,
                       slippage_mnq=1., net_mnq=float(side*(price-entry)*2-2.24))
        rows.append(row)
    t = pd.DataFrame(rows)
    if len(t):
        t['entry_time'] = [pd.Timestamp(g.ts[int(j)//1440]) + pd.Timedelta(minutes=int(j)%1440) for j in t.entry_j]
    return t


def daily_marks(g, t):
    daily = pd.Series(0., index=pd.bdate_range('2018-01-01', pd.Timestamp(g.ts[-1])))
    for r in t[t.state == 'resolved'].to_dict('records'):
        start, end = int(r['entry_j']), int(r['exit_j'])
        def label(j):
            d = pd.Timestamp(g.ts[j//1440])
            return d + pd.Timedelta(days=int(j%1440 > 1020))
        marks = [j for j in range((start//1440)*1440+960, end, 1440) if j >= start and np.isfinite(g.c.ravel()[j])]
        previous = r['entry']
        daily.loc[label(start)] = daily.get(label(start), 0.) - 1.12
        for j in marks + [end]:
            price = r['exit'] if j == end else g.c.ravel()[j]
            day = label(j)
            daily.loc[day] = daily.get(day, 0.) + r['side']*(price-previous)*2
            previous = price
        day = label(end)
        daily.loc[day] -= 1.12
    return daily.sort_index()


def run_design():
    dest = OUT / 'design'
    dest.mkdir(parents=True, exist_ok=False)
    paths = sorted(p for p in (ROOT/'data').glob('NQ_1min_*.csv') if int(p.stem[-4:]) <= 2022)
    assert paths and all(int(p.stem[-4:]) < 2023 for p in paths)
    loader.OUT = OUT
    g, valid, audit = loader.load_grid(paths, 'design', dest)
    bars = four_hour_bars(g, valid)
    summary = dict(source_audit=audit, full_four_hour_bars=sum(b['valid'] for b in bars),
                   invalid_expected_bars=sum(not b['valid'] for b in bars), models=[],
                   input_hashes={str(p.relative_to(ROOT)):loader.sha(p) for p in paths},
                   code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
                   configuration_count=2, inspected_economic_ledgers=4,
                   design_only=True, validation_run=False)
    pd.DataFrame(bars).to_csv(dest/'bars.csv',index=False)
    for radius in (1,2):
        events = signals(bars, radius)
        events = events[events.signal.map(lambda j: pd.Timestamp(g.ts[int(j)//1440]).year >= 2018)]
        events.to_csv(dest/f'signals_r{radius}.csv',index=False)
        for timing in ('executable','close_benchmark'):
            name = f'r{radius}_{timing}'
            t = trade_ledger(g, valid, events, timing)
            t.to_csv(dest/f'{name}_trades.csv',index=False)
            resolved = t[t.state == 'resolved'] if len(t) else pd.DataFrame(columns=['net_mnq','gross_mnq','side'])
            d = daily_marks(g,t) if len(t) else pd.Series(0.,index=pd.bdate_range('2018-01-01','2022-12-30'))
            assert np.isclose(d.sum(),resolved.net_mnq.sum())
            d.rename('net_mnq').to_csv(dest/f'{name}_daily.csv',index_label='date')
            m = M.perf(d,resolved.net_mnq)
            m.update(model=name, signal_count=len(events), resolved=len(resolved),
                     gross_total=resolved.gross_mnq.sum(), net_total=resolved.net_mnq.sum(),
                     gross_mean=resolved.gross_mnq.mean(), trade_t=tstat(resolved.net_mnq),
                     daily_NW5=nw_t(d.to_numpy()), unresolved=int((t.state!='resolved').sum()) if len(t) else 0,
                     gross_pass=bool(len(resolved) and resolved.gross_mnq.mean()>4.48))
            yearly=[]
            for year in range(2018,2023):
                dy=d[d.index.year==year]
                yearly.append(dict(year=year,net_mnq=dy.sum()))
            m['yearly']=yearly
            m['side']=[dict(side=s,**M.perf(daily_marks(g,t[(t.side==s)]),resolved.loc[resolved.side==s,'net_mnq']),
                            net_total=resolved.loc[resolved.side==s,'net_mnq'].sum(),
                            trade_t=tstat(resolved.loc[resolved.side==s,'net_mnq'])) for s in (-1,1)] if len(t) else []
            m['design_pass']=bool(m['gross_pass'] and len(resolved)>=30 and m['net_total']>0 and
                                  m['trade_t']>=2 and sum(x['net_mnq']>0 for x in yearly)>=3 and m['unresolved']==0)
            summary['models'].append(m)
    (dest/'summary.json').write_text(json.dumps(loader.safe(summary),indent=2,allow_nan=False)+'\n')
    print(json.dumps(loader.safe(summary['models']),indent=2))


def synthetic_checks():
    rng = np.random.default_rng(42)
    c = 100 + np.cumsum(rng.normal(size=400))
    bars = [dict(end=i*240,valid=True,high=float(v+1),low=float(v-1),close=float(v)) for i,v in enumerate(c)]
    checks = 0
    for radius in (1,2):
        full = signals(bars,radius)
        assert len(full)>0
        for end in range(10,len(bars),7):
            prefix = signals(bars[:end],radius)
            pd.testing.assert_frame_equal(prefix.reset_index(drop=True),full[full.signal<end*240].reset_index(drop=True), check_dtype=False)
        checks += 1
        mirror = [dict(b,high=-b['low'],low=-b['high'],close=-b['close']) for b in bars]
        opposite = signals(mirror,radius)
        assert opposite.signal.tolist() == full.signal.tolist()
        assert np.array_equal(opposite.side,-full.side)
        assert np.allclose(opposite.stop,-full.stop)
        checks += 1
        # No previously available signal can change if only future bars are changed.
        altered = [dict(b) for b in bars]
        for b in altered[200:]: b.update(high=999.,low=-999.,close=0.)
        pd.testing.assert_frame_equal(signals(altered,radius).query('signal<48000').reset_index(drop=True),
                                      full.query('signal<48000').reset_index(drop=True))
        checks += 1
    # Entry-bar stop, worse later gap and strict target-through in shared engine.
    o=np.array([100.,100.,90.]);h=np.array([101.,101.,91.]);l=np.array([94.,99.,89.]);c=np.array([99.,100.,90.])
    assert _walk(o,h,l,c,0,2,1,95.,105.,1.)[:3] == (0,95.,0)
    l[0]=99.
    assert _walk(o,h,l,c,0,2,1,95.,105.,1.)[:3] == (2,90.,0)
    h[0]=105.5
    assert _walk(o,h,l,c,0,0,1,95.,105.,1.)[2] == 2
    h[0]=106.
    assert _walk(o,h,l,c,0,0,1,95.,105.,1.)[:3] == (0,105.,1)
    checks += 4
    return dict(groups=checks,causal_prefix_checks=True,mirror_symmetry=True,
                shared_entry_stop_gap_target_checks=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--design',action='store_true',required=True)
    p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'synthetic_checks.json').write_text(json.dumps(synthetic_checks(),indent=2)+'\n')
    run_design()
