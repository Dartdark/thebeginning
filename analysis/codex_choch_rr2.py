"""Four frozen CHoCH 1:2 variants; design first; no trading connections."""
from pathlib import Path
import argparse
import json
import os
import subprocess
from types import SimpleNamespace
import numpy as np
import pandas as pd
import codex_choch4h as core
import codex_choch4h_corrected_data as repaired
from codex_s03_calendar import calendar_status

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_choch_rr2_20261028'
SOURCE = ROOT / 'agents/codex/inputs/choch4h_corrected_20261028/local/design_source_reconciled'
os.environ['NUMBA_CACHE_DIR'] = str(OUT / 'cache/numba')


def hourly_bars(g, valid):
    expected = repaired.expected_minutes(g)
    v = valid.ravel()
    h, l, c = (getattr(g,k).ravel() for k in 'hlc')
    out = []
    for end in range(0, len(v), 60):
        start = end - 59
        if start < 0:
            continue
        mask = expected[start:end+1]
        if not mask.any():
            continue
        ok = bool((v[start:end+1] | ~mask).all() and v[end])
        out.append(dict(end=end, valid=ok,
                        high=float(np.max(h[start:end+1][mask])) if ok else np.nan,
                        low=float(np.min(l[start:end+1][mask])) if ok else np.nan,
                        close=float(c[end]) if ok else np.nan))
    return out


def intraday_window(date, minute):
    status = calendar_status(date)
    if status['kind'] not in ('normal','early'):
        return None
    flat = 690 if status['kind'] == 'early' else 958
    return flat if 540 <= minute <= flat-60 else None


def ledger(g, valid, events, timing, intraday):
    o,h,l,c = (getattr(g,k).ravel() for k in 'ohlc')
    good = valid.ravel()
    missing = np.cumsum(repaired.expected_minutes(g) & ~good)
    rows, blocked = [], -1
    for e in events.to_dict('records'):
        signal = int(e['signal'])
        minute, day = signal%1440, signal//1440
        flat = intraday_window(pd.Timestamp(g.ts[day]), minute) if intraday else None
        if intraday and flat is None:
            continue
        start = signal + (2 if timing == 'executable' else 1)
        deadline = day*1440+flat if intraday else len(o)-1
        if start <= blocked or start >= len(o) or start >= deadline:
            continue
        side, stop = int(e['side']), float(e['stop'])
        if not good[start]:
            if intraday:
                blocked = deadline
            else:
                hits = np.flatnonzero(good[start:] & ((h[start:]>=stop) if side<0 else (l[start:]<=stop)))
                blocked = start+int(hits[0]) if len(hits) else len(o)-1
            rows.append(dict(**e,entry_j=start,state='missing_entry'))
            continue
        entry = float(o[start] if timing == 'executable' else e['close'])
        risk = side*(entry-stop)
        if risk <= 0:
            rows.append(dict(**e,entry_j=start,state='invalid_risk'))
            continue
        target = entry+side*2*risk
        if side*(o[start]-stop) <= 0:
            end, price, kind = start, o[start], 0
        else:
            end,price,kind,_ = core._walk(o,h,l,c,start,deadline-1 if intraday else deadline,
                                          side,stop,target,1.)
        if intraday and kind == 2:
            end,price = deadline,o[deadline]
        blocked = int(end)
        unknown = int(missing[end]-(missing[start-1] if start else 0))
        if unknown or not np.isfinite(price):
            state = 'unresolved_missing'
        elif kind == 2 and not intraday:
            state = 'censored_end'
        else:
            state = 'resolved'
        row = dict(**e,entry_j=start,exit_j=int(end),entry=entry,exit=float(price),
                   risk=float(risk),target=float(target),kind=int(kind),state=state,
                   missing_expected_minutes=unknown)
        if state == 'resolved':
            row.update(gross_mnq=float(side*(price-entry)*2),commission_mnq=1.24,
                       slippage_mnq=1.,net_mnq=float(side*(price-entry)*2-2.24))
        rows.append(row)
    result = pd.DataFrame(rows)
    for column in ('state','side','gross_mnq','net_mnq','risk'):
        if column not in result:
            result[column] = np.nan
    for column,jcol in [('entry_time','entry_j'),('exit_time','exit_j')]:
        if jcol in result:
            result[column] = [pd.NaT if not np.isfinite(j) else pd.Timestamp(g.ts[int(j)//1440])+
                              pd.Timedelta(minutes=int(j)%1440) for j in result[jcol]]
    return result


def measurements(g,t,name,raw_signals,eligible_signals):
    known = t[t.state=='resolved']
    daily = core.daily_marks(g,t)
    assert np.isclose(daily.sum(),known.net_mnq.sum())
    m = core.M.perf(daily,known.net_mnq)
    m.update(model=name,raw_signals=raw_signals,eligible_signals=eligible_signals,
             net_total=float(known.net_mnq.sum()),gross_total=float(known.gross_mnq.sum()),
             gross_mean=float(known.gross_mnq.mean()),trade_t=core.tstat(known.net_mnq),
             daily_NW5=core.nw_t(daily.to_numpy()),state_counts=t.state.value_counts().to_dict(),
             unresolved=int(t.state.isin(['missing_entry','unresolved_missing']).sum()),
             censored=int(t.state.eq('censored_end').sum()),
             gross_pass=bool(len(known) and known.gross_mnq.mean()>4.48))
    m['years'] = [dict(year=year,net_mnq=float(daily[daily.index.year==year].sum())) for year in range(2018,2023)]
    m['sides'] = []
    for side in [-1,1]:
        st=t[t.side==side]; sk=known[known.side==side]
        sd=core.daily_marks(g,st)
        m['sides'].append(dict(side=side,**core.M.perf(sd,sk.net_mnq),
                               net_total=float(sk.net_mnq.sum()),trade_t=core.tstat(sk.net_mnq)))
    m['risk_points_quantiles'] = known.risk.quantile([0,.5,.95,1]).to_dict()
    m['economic_gate'] = bool(m['gross_pass'] and len(known)>=30 and m['net_total']>0 and
                              m['trade_t']>=2 and sum(v['net_mnq']>0 for v in m['years'])>=3)
    m['complete_data_gate'] = m['unresolved']==0
    m['design_pass'] = m['economic_gate'] and m['complete_data_gate']
    return m,daily


def checks():
    assert intraday_window('2021-06-28',540)==958
    assert intraday_window('2021-06-28',840)==958
    assert intraday_window('2021-06-28',900) is None
    assert intraday_window('2024-11-29',600)==690
    assert intraday_window('2024-11-29',660) is None
    assert intraday_window('2021-01-18',540) is None
    dates=pd.date_range('2021-06-25','2021-06-28')
    g=SimpleNamespace(D=len(dates),dates=dates.strftime('%Y%m%d').astype(int).to_numpy(),ts=dates.to_numpy())
    expected=repaired.expected_minutes(g).reshape(g.D,1440)
    for k in 'ohlc': setattr(g,k,np.where(expected,100.,np.nan))
    g.h=g.h+1;g.l=g.l-1
    bars=hourly_bars(g,expected)
    assert not any(b['end']%1440==1020 for b in bars)
    assert all(b['valid'] for b in bars)
    for day in [0,3]:assert any(b['end']==day*1440+960 and b['valid'] for b in bars)
    bad=expected.copy();bad[3,542]=False
    assert not next(b for b in hourly_bars(g,bad) if b['end']==3*1440+600)['valid']
    event=pd.DataFrame([dict(signal=3*1440+540,close=100.,side=1,stop=95.,radius=1,broken_pivot=0)])
    deadline=958;entry=542
    g.o[3,deadline]=103.;g.h[3,deadline]=104.;g.l[3,deadline]=102.;g.c[3,deadline]=103.
    result=ledger(g,expected,event,'executable',True).iloc[0]
    assert result.state=='resolved' and result.kind==2 and result.exit==103. and result.target==110.
    assert result.exit_j==3*1440+deadline and np.isclose(result.net_mnq,3.76)
    g.h[3,entry]=111.
    result=ledger(g,expected,event,'executable',True).iloc[0]
    assert result.kind==1 and result.exit==110.
    g.h[3,entry]=101.;g.l[3,entry]=94.
    result=ledger(g,expected,event,'executable',True).iloc[0]
    assert result.kind==0 and result.exit==95.
    g.l[3,entry]=99.;g.o[3,entry+1]=92.;g.l[3,entry+1]=91.;g.h[3,entry+1]=93.
    result=ledger(g,expected,event,'executable',True).iloc[0]
    assert result.kind==0 and result.exit==92.
    result=ledger(g,bad,event,'executable',True).iloc[0]
    assert result.state=='missing_entry'
    return dict(shared_core=core.synthetic_checks(),calendar=repaired.calendar_checks(),
                hourly_expected_minutes=True,intraday_and_early_close=True,
                target_2R=True,planned_exit_open=True,entry_stop_and_gap=True,unknown_entry=True)


def run():
    dest=OUT/'design';dest.mkdir(parents=True,exist_ok=False)
    files=sorted((SOURCE/'data').glob('NQ_1min_*.csv'))
    assert len(files)==11 and all(int(p.stem[-4:])<=2022 for p in files)
    previous=json.loads((ROOT/'analysis/outputs/codex_choch4h_corrected_20261028/design/summary.json').read_text())
    hashes={f'data/{p.name}':core.loader.sha(p) for p in files}
    assert hashes==previous['input_hashes'], 'Data changed from reconciled RR1 run'
    core.loader.ROOT=SOURCE;core.loader.OUT=OUT
    g,valid,audit=core.loader.load_grid(files,'design',dest)
    allbars={4:core.four_hour_bars(g,valid),1:hourly_bars(g,valid)}
    summary=dict(models=[],source_audit=audit,input_hashes=hashes,design_only=True,
                 implementation_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                 configurations=4,inspected_ledgers=8,cumulative_structural_configurations=6,
                 prior_rr1_preserved=True,validation_run=False)
    for hours in [4,1]:
        bars=allbars[hours]
        summary[f'h{hours}_bar_coverage']=dict(valid=sum(b['valid'] for b in bars),invalid=sum(not b['valid'] for b in bars))
        for radius in [1,2]:
            events=core.signals(bars,radius)
            events=events[events.signal.map(lambda j: pd.Timestamp(g.ts[int(j)//1440]).year>=2018)].copy()
            eligible=events if hours==4 else events[events.signal.map(lambda j: intraday_window(pd.Timestamp(g.ts[int(j)//1440]),int(j)%1440) is not None)]
            events.to_csv(dest/f'h{hours}_r{radius}_signals.csv',index=False)
            for timing in ['executable','close_benchmark']:
                name=f'h{hours}_r{radius}_{timing}'
                t=ledger(g,valid,eligible,timing,hours==1)
                t.to_csv(dest/f'{name}_trades.csv',index=False)
                m,d=measurements(g,t,name,len(events),len(eligible))
                d.rename('net_mnq').to_csv(dest/f'{name}_daily.csv',index_label='date')
                summary['models'].append(m)
    (dest/'summary.json').write_text(json.dumps(core.loader.safe(summary),indent=2,allow_nan=False)+'\n')
    print(json.dumps(core.loader.safe(summary['models']),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'checks.json').write_text(json.dumps(core.loader.safe(checks()),indent=2)+'\n')
    if args.design:run()
