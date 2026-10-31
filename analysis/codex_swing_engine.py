"""Literal Swing Target source replay plus the separately authorized BE rule.

Extends the repository minute-close/OHLC path convention for resting stop
entries and intrabar breakeven, which grid.execute does not support. No I/O,
cache construction, fees or parameter selection. No source files are changed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from numba import njit


COLUMNS = ['day', 'j0', 'exit_day', 'j1', 'side', 'entry', 'exit', 'kind', 'pnl',
           'mae', 'qty', 'reason_code', 'entry_phase_code', 'exit_phase_code',
           'entry_minute_adverse_px', 'exit_minute_adverse_px',
           'unknown_held_minutes', 'entry_avg_range', 'exit_avg_range']


@njit(cache=False)
def _put(out, n, entry_i, exit_i, side, ep, px, reason, worst, entry_phase,
         exit_phase, entry_adverse, exit_adverse, missing, entry_avg, exit_avg):
    kind = 1 if reason == 1 else (2 if reason == 2 else 0)
    out[n, :] = np.array([entry_i // 1440, entry_i % 1440, exit_i // 1440,
        exit_i % 1440, side, ep, px, kind, (px - ep) * side * 20.,
        max(0., (ep - worst) * side) * 20., 1., reason, entry_phase,
        exit_phase, entry_adverse, exit_adverse, missing, entry_avg, exit_avg])


@njit(cache=False)
def _run(o, h, l, c, allow, cutoff, breakeven, through, path_mode):
    D, J = o.shape
    out = np.empty((D + 16, 19))
    range_schedule = np.full(D, np.nan)
    dh, dl = np.zeros(60), np.zeros(60)
    nd = 0
    inrth = False
    armed = False
    traded = False
    dayh, dayl, href, lref, avg = 0., 0., 0., 0., 0.
    totaltrades, tt0 = 0, 0
    pending_entry, pending_market = False, False
    order_hi, order_lo = 0., 0.
    side, ep, entry_i, entry_phase = 0, 0., -1, 0
    worst, entry_adverse, entry_avg = 0., 0., 0.
    be, missing, n = False, 0, 0
    counters = np.zeros(8, np.int64)
    # counters: native bars, stored sessions, armed opens, early disarms,
    # ambiguous double-level bars, gap entries, finite bars held >=16:00,
    # source entry orders emitted outside the allowed observation interval.
    last_i, last_c = -1, np.nan
    for i in range(min(D * J, cutoff)):
        d, j = i // 1440, i % 1440
        oo, hh, ll, cc = o[d,j], h[d,j], l[d,j], c[d,j]
        if not (np.isfinite(oo) and np.isfinite(hh) and np.isfinite(ll) and np.isfinite(cc)):
            if side:
                missing += 1
            continue
        counters[0] += 1
        last_i, last_c = i, cc
        bar_adverse = oo if side else np.nan
        if side:
            worst = min(worst, oo) if side > 0 else max(worst, oo)
        exited = False
        # A next-bar market exit has priority at the same open. A simultaneous
        # stop gap has the same price/cost category, not an invented better fill.
        if side and pending_market:
            _put(out,n,entry_i,i,side,ep,oo,2,worst,entry_phase,0,
                 entry_adverse,oo,missing,entry_avg,avg)
            n += 1; totaltrades += 1; side = 0; exited = True
        pending_market = False
        entry_live = pending_entry and not exited and side == 0
        pending_entry = False
        if entry_live and hh >= order_hi and ll <= order_lo:
            counters[4] += 1
        # Gap-through stop entries fill at the open, never at a stale level.
        if entry_live and (oo >= order_hi or oo <= order_lo):
            side = 1 if oo >= order_hi else -1
            ep, entry_i, entry_phase = oo, i, 0
            worst, entry_adverse, bar_adverse = ep, ep, ep
            entry_avg, missing, be = avg, 0, False
            counters[5] += int((side > 0 and oo > order_hi) or (side < 0 and oo < order_lo))
            entry_live = False
            traded = True
        # Protective orders active before this bar use the last source-calculated
        # AvgRng. A carried position can get a changed distance after 08:31.
        if side and not exited:
            sp = ep if be else ep - side * .7 * avg
            tp = ep + side * .35 * avg
            reason, px = -1, 0.
            if (side > 0 and oo <= sp) or (side < 0 and oo >= sp):
                reason, px = (3 if be else 0), oo
            elif (side > 0 and oo >= tp + through) or (side < 0 and oo <= tp - through):
                reason, px = 1, tp
            elif breakeven and ((oo - ep) * side >= .3 * entry_avg):
                be = True
            if reason >= 0:
                _put(out,n,entry_i,i,side,ep,px,reason,worst,entry_phase,0,
                     entry_adverse,bar_adverse,missing,entry_avg,avg)
                n += 1; totaltrades += 1; side = 0; exited = True
        # Same convention as grid._walk: nearer high first, ties high first.
        high_first = hh - oo <= oo - ll
        if path_mode == 1:
            high_first = not high_first
        path = np.array([oo, hh, ll, cc]) if high_first else np.array([oo, ll, hh, cc])
        for segment in range(3):
            a, b = path[segment], path[segment + 1]
            if not side and entry_live and not exited:
                entered = False
                if b >= a and a <= order_hi <= b:
                    side, ep, entered = 1, order_hi, True
                elif b <= a and b <= order_lo <= a:
                    side, ep, entered = -1, order_lo, True
                if entered:
                    entry_i, entry_phase = i, 1
                    worst, entry_adverse, bar_adverse = ep, ep, ep
                    entry_avg, missing, be = avg, 0, False
                    entry_live = False
                    traded = True
                    a = ep
            if not side or exited:
                continue
            reason, px = -1, 0.
            sp = ep if be else ep - side * .7 * avg
            tp = ep + side * .35 * avg
            favorable = (b - a) * side >= 0
            if favorable:
                if breakeven and (b - ep) * side >= .3 * entry_avg:
                    be = True
                trigger = tp + side * through
                if (b - trigger) * side >= 0 and (trigger - a) * side >= 0:
                    reason, px = 1, tp
                # No adverse excursion is added by this monotone favorable leg.
            else:
                if (b - sp) * side <= 0 and (sp - a) * side <= 0:
                    reason, px = (3 if be else 0), sp
                end = px if reason >= 0 else b
                worst = min(worst, end) if side > 0 else max(worst, end)
                bar_adverse = min(bar_adverse, end) if side > 0 else max(bar_adverse, end)
                if i == entry_i:
                    entry_adverse = min(entry_adverse, end) if side > 0 else max(entry_adverse, end)
            if reason >= 0:
                _put(out,n,entry_i,i,side,ep,px,reason,worst,entry_phase,1,
                     entry_adverse,bar_adverse,missing,entry_avg,avg)
                n += 1; totaltrades += 1; side = 0; exited = True
        if side and j >= 960:
            counters[6] += 1
        # Literal source close-time state updates, including exact-boundary bugs.
        if j == 511:
            inrth, traded, tt0 = True, False, totaltrades
            dayh, dayl = hh, ll
            armed = False
            if nd >= 20 and nd >= 2:
                href, lref = max(dh[0], dh[1]), min(dl[0], dl[1])
                avg = 0.
                for k in range(20):
                    avg += dh[k] - dl[k]
                avg /= 20
                armed = oo <= href and oo >= lref and hh <= href and ll >= lref
                if armed:
                    counters[2] += 1
            range_schedule[d] = avg
        elif inrth:
            dayh, dayl = max(dayh, hh), min(dayl, ll)
        if totaltrades > tt0 or side:
            traded = True
        if inrth and armed and j <= 525 and (hh > href or ll < lref):
            armed = False
            counters[3] += 1
        if inrth and armed and not traded and side == 0 and 525 <= j <= 869:
            if allow[d]:
                pending_entry, order_hi, order_lo = True, href, lref
            else:
                counters[7] += 1
        if side and 899 <= j <= 900:
            pending_market = True
        if inrth and j == 900:
            for k in range(59,0,-1):
                dh[k], dl[k] = dh[k-1], dl[k-1]
            dh[0], dl[0] = dayh, dayl
            nd += 1
            counters[1] += 1
            inrth, armed = False, False
    open_state = np.array([side,entry_i,ep,entry_avg,worst,missing,last_i,last_c],np.float64)
    return out[:n], counters, open_state, range_schedule


def replay(g, breakeven=False, through=1., start_date=None, end_date=None, path_mode=0):
    """Return closed trades and diagnostics without loading/rebuilding any data.

    Full cached bars initialize source history. New orders are enabled only on
    dates >=start_date and <=end_date. Processing stops after end_date; an open
    position is disclosed and never liquidated by an invented research exit.
    Endpoints are inclusive calendar dates. Price offsets retain the repository
    engine's floating-point distances (not a claim about MC tick rounding).
    """
    dates = pd.DatetimeIndex(g.ts)
    allow = np.ones(g.D, dtype=np.bool_)
    if start_date is not None:
        allow &= dates >= pd.Timestamp(start_date)
    cutoff = g.D * 1440
    if end_date is not None:
        end = pd.Timestamp(end_date)
        allow &= dates <= end
        cutoff = int(dates.searchsorted(end, side='right')) * 1440
    raw, count, opened, range_schedule = _run(g.o,g.h,g.l,g.c,allow,cutoff,bool(breakeven),float(through),int(path_mode))
    g._codex_swing_range_schedule = range_schedule
    g._codex_swing_schedule_cutoff = cutoff
    t = _frame(g, raw)
    trading = np.asarray(g.trading, int)
    trading = trading[trading * 1440 < cutoff]
    missing_open = trading[~np.isfinite(g.o[trading,511])]
    missing_store = trading[~np.isfinite(g.c[trading,900])]
    diag = dict(native_bars=int(count[0]), stored_sessions=int(count[1]), armed_opens=int(count[2]),
        early_disarmed=int(count[3]), double_level_minutes=int(count[4]), gap_entries=int(count[5]),
        finite_held_minutes_at_or_after_1600=int(count[6]),
        open_position_at_end=bool(opened[0]), open_position_state=opened.tolist(),
        missing_0831_dates=[str(dates[i].date()) for i in missing_open],
        missing_1500_dates=[str(dates[i].date()) for i in missing_store],
        closed_cross_date_trades=int(t.cross_date.sum()), path_mode=int(path_mode),
        breakeven_trigger=.30 if breakeven else None,
        price_rounding='Unrounded distances, same as repository grid engine; MC parity unverified',
        pending_orders='Next available native bar; OCO canceled on first entry',
        source_session='Full cached CME proxy, exact source 0831/1500 state boundaries')
    return t, diag


def _frame(g, raw):
    t = pd.DataFrame(raw, columns=COLUMNS)
    ints = ['day','j0','exit_day','j1','side','kind','reason_code','entry_phase_code','exit_phase_code','unknown_held_minutes']
    for col in ints:
        t[col] = t[col].astype(int)
    t['date'] = pd.to_datetime(g.ts[t.day.to_numpy()])
    t['exit_date'] = pd.to_datetime(g.ts[t.exit_day.to_numpy()])
    t['cross_date'] = t.exit_day.ne(t.day)
    t['reason'] = t.reason_code.map({0:'stop',1:'target',2:'time',3:'breakeven'})
    for col in ['entry_phase','exit_phase']:
        t[col] = t[col+'_code'].map({0:'open',1:'intrabar'})
    t['net'] = t.pnl - 7.25 - 5. * (1 + t.kind.ne(1).astype(int))
    t['native_net_per_mnq'] = t.pnl / 10 - 1.24 - .5 * (1 + t.kind.ne(1).astype(int))
    return t


@njit(cache=False)
def _market_many(o,h,l,c,signals,range_schedule,breakeven,through,path_mode):
    out = np.empty((len(signals),19))
    n = 0
    D = o.shape[0]
    for row in signals:
        day,j0,side = int(row[0]),int(row[1]),int(row[2])
        avg = row[3]
        entry_i = day * 1440 + j0
        ep, entry_avg = o[day,j0], avg
        worst, entry_adverse = ep, ep
        missing, be, pending_market = 0,False,False
        for i in range(entry_i,D*1440):
            d,j = i//1440,i%1440
            oo,hh,ll,cc = o[d,j],h[d,j],l[d,j],c[d,j]
            if not (np.isfinite(oo) and np.isfinite(hh) and np.isfinite(ll) and np.isfinite(cc)):
                missing += 1
                continue
            bar_adverse = oo
            worst = min(worst,oo) if side > 0 else max(worst,oo)
            reason,px,phase = -1,0.,0
            sp = ep if be else ep-side*.7*avg
            tp = ep+side*.35*avg
            if pending_market:
                reason,px = 2,oo
            elif (side > 0 and oo <= sp) or (side < 0 and oo >= sp):
                reason,px = (3 if be else 0),oo
            elif (side > 0 and oo >= tp+through) or (side < 0 and oo <= tp-through):
                reason,px = 1,tp
            elif breakeven and (oo-ep)*side >= .3*entry_avg:
                be=True
            if reason < 0:
                high_first = hh-oo <= oo-ll
                if path_mode == 1:
                    high_first = not high_first
                path = np.array([oo,hh,ll,cc]) if high_first else np.array([oo,ll,hh,cc])
                for s in range(3):
                    a,b=path[s],path[s+1]
                    sp=ep if be else ep-side*.7*avg
                    tp=ep+side*.35*avg
                    if (b-a)*side >= 0:
                        if breakeven and (b-ep)*side >= .3*entry_avg:
                            be=True
                        trigger=tp+side*through
                        if (b-trigger)*side >= 0 and (trigger-a)*side >= 0:
                            reason,px=1,tp
                    else:
                        if (b-sp)*side <= 0 and (sp-a)*side <= 0:
                            reason,px=(3 if be else 0),sp
                        end=px if reason>=0 else b
                        worst=min(worst,end) if side>0 else max(worst,end)
                        bar_adverse=min(bar_adverse,end) if side>0 else max(bar_adverse,end)
                        if i==entry_i:
                            entry_adverse=min(entry_adverse,end) if side>0 else max(entry_adverse,end)
                    if reason>=0:
                        phase=1
                        break
            if reason>=0:
                _put(out,n,entry_i,i,side,ep,px,reason,worst,0,phase,entry_adverse,
                     bar_adverse,missing,entry_avg,avg)
                n+=1
                break
            if 899<=j<=900:
                pending_market=True
            if j==511 and np.isfinite(range_schedule[d]):
                avg=range_schedule[d]
    return out[:n]


def replay_market(g, signals, breakeven=False, through=1., path_mode=0):
    """Independent matched-exit placebo signals [day,j0,side,entry AvgRng].

    Market entries start at the supplied native bar's open. Source range
    recomputation, BE path, target-through and 14:59 next-bar exits are retained.
    Signals are separate null experiments; mutual overlap is not netted here.
    The in-memory feature schedule is reused without rebuilding a cache.
    """
    sig=np.ascontiguousarray(signals,dtype=float)
    if len(sig)==0:
        return _frame(g,np.empty((0,19)))
    d,j=sig[:,0].astype(int),sig[:,1].astype(int)
    assert np.isfinite(g.o[d,j]).all() and np.isfinite(g.h[d,j]).all()
    assert np.isfinite(g.l[d,j]).all() and np.isfinite(g.c[d,j]).all()
    assert (sig[:,3]>0).all() and np.isin(sig[:,2],[-1,1]).all()
    if getattr(g,'_codex_swing_schedule_cutoff',0)<g.D*1440:
        _,_,_,schedule=_run(g.o,g.h,g.l,g.c,np.zeros(g.D,np.bool_),g.D*1440,
                           False,float(through),int(path_mode))
        g._codex_swing_range_schedule=schedule
        g._codex_swing_schedule_cutoff=g.D*1440
    raw=_market_many(g.o,g.h,g.l,g.c,sig,g._codex_swing_range_schedule,
                     bool(breakeven),float(through),int(path_mode))
    return _frame(g,raw)


def synthetic_checks():
    """Small deterministic fixtures; never opens the research history."""
    from types import SimpleNamespace
    D = 23
    shape = (D,1440)
    o,h,l,c = [np.full(shape,np.nan) for _ in range(4)]
    # Twenty completed source sessions establish prior high110/low90, avg20.
    for d in range(20):
        o[d,511]=100; h[d,511]=110; l[d,511]=90; c[d,511]=100
        o[d,900]=100; h[d,900]=100; l[d,900]=100; c[d,900]=100
    for d in range(20,D):
        for j in [511,525,526,527,899,900]:
            o[d,j]=100; h[d,j]=100; l[d,j]=100; c[d,j]=100
    # Entry at110; no use of the pre-entry low95. Later high116.5 arms BE,
    # but fails target+through118. Exit at110 on the causal subsequent decline.
    o[20,526],h[20,526],l[20,526],c[20,526]=100,116.5,95,109
    for j in [527,899,900]:
        o[20,j]=109; h[20,j]=109; l[20,j]=108; c[20,j]=109
    # An early break disarms the next day, regardless of later recovery.
    h[21,525]=111
    # Final gap opens above the standing level and must pay the worse open.
    o[22,526]=120; h[22,526]=122; l[22,526]=119; c[22,526]=121
    ts=pd.date_range('2020-01-01',periods=D).to_numpy()
    g=SimpleNamespace(o=o,h=h,l=l,c=c,D=D,ts=ts,trading=np.arange(D))
    a, da=replay(g,False)
    b, db=replay(g,True)
    assert len(a)==2 and len(b)==2
    assert a.iloc[0].entry==110 and b.iloc[0].entry==110
    assert b.iloc[0].reason=='breakeven' and b.iloc[0].exit==110
    assert b.iloc[0].mae==0 and b.iloc[0].entry_minute_adverse_px==110
    assert a.iloc[-1].entry==120 and da['gap_entries']>=1
    assert not a.day.eq(21).any()
    assert a.groupby('day').size().max()==1 and b.groupby('day').size().max()==1
    # Inclusive14:29 decision submits into the14:30-labeled native bar.
    z=[x.copy() for x in [o,h,l,c]]
    for x in z:
        x[20:]=np.nan
        for j in [511,525,869,870,899,900]:
            x[20,j]=100
    z[1][20,870]=112
    late=SimpleNamespace(o=z[0],h=z[1],l=z[2],c=z[3],D=D,ts=ts,trading=np.arange(D))
    q,_=replay(late)
    assert len(q)==1 and q.iloc[0].j0==870 and q.iloc[0].j1==900
    # Orders are for the next available native bar, not an assumed clock slot.
    for x in z:
        x[20,869:]=np.nan
        x[20,528]=120; x[20,899]=120; x[20,900]=120
    q,_=replay(late)
    assert len(q)==1 and q.iloc[0].j0==528 and q.iloc[0].entry==120
    # No15:00 storage/flat repair: keep the source's holiday carry behavior.
    z=[x.copy() for x in [o,h,l,c]]
    for x in z:
        x[20,899:]=np.nan
        x[21,:]=np.nan
        x[22,:]=np.nan
        for j in [511,525,899,900]:
            x[21,j]=100
    carry=SimpleNamespace(o=z[0],h=z[1],l=z[2],c=z[3],D=D,ts=ts,trading=np.arange(D))
    q,dq=replay(carry)
    assert len(q)==1 and q.iloc[0].cross_date and q.iloc[0].exit_day==21
    assert dq['stored_sessions']==21 and str(pd.Timestamp(ts[20]).date()) in dq['missing_1500_dates']
    # Market-null helper respects through1: touch is insufficient.
    for x in z:
        x[20:]=np.nan
        for j in [511,525,526,527,899,900]:
            x[20,j]=110
    z[1][20,526]=117.75
    market=SimpleNamespace(o=z[0],h=z[1],l=z[2],c=z[3],D=D,ts=ts,trading=np.arange(D))
    sig=np.array([[20,526,1,20.]],float)
    q=replay_market(market,sig)
    assert q.iloc[0].reason=='time'
    z[1][20,526]=118.
    q=replay_market(market,sig)
    assert q.iloc[0].reason=='target' and q.iloc[0].exit==117.
    # Fixed alternative minute path changes an ambiguous exit, not the rule.
    z[0][20,526]=100;z[1][20,526]=110;z[2][20,526]=80;z[3][20,526]=100
    q0=replay_market(market,sig,path_mode=0)
    q1=replay_market(market,sig,path_mode=1)
    assert q0.iloc[0].reason=='target' and q1.iloc[0].reason=='stop'
    return dict(causal_stop_entry=True, pre_entry_low_excluded=True,
                causal_breakeven=True, early_break_disarms=True,gap_entry_worse_open=True,
                one_entry_per_day=True, inclusive_last_decision=True,
                next_available_bar_orders=True, missing1500_preserves_source_carry=True,
                target_through_one_point=True, alternative_path_is_adverse_diagnostic=True)

