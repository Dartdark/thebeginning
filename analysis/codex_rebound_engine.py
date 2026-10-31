"""Literal Overnight Rebound replay on the repository's close-stamped CT grid.

The uploaded PC chart is ET with ClockShiftMin=-60. This module normalizes
prices to the same intended CT clock; it retains the ET calendar Date used
by DayOfWeek/DateToJulian. No I/O, fees, cache rebuilding or return selection.
Market entry plus a stop has no same-bar target/stop path ambiguity.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from numba import njit

COLUMNS = ['day','j0','exit_day','j1','side','entry','exit','kind','pnl','mae','qty',
           'reason_code','exit_phase_code','entry_minute_adverse_px','exit_minute_adverse_px',
           'unknown_held_minutes','signal_day','signal_range','exit_range',
           'entry_submit_day','entry_submit_j','signal_id']
NCOLS = 22


@njit(cache=False)
def _put(out,n,ei,xi,side,ep,px,qty,reason,phase,worst,entry_adverse,exit_adverse,
         missing,signal_day,signal_range,exit_range,submitted_i,signal_id):
    kind = 0 if reason == 0 else 2
    out[n,:] = np.array([ei//1440,ei%1440,xi//1440,xi%1440,side,ep,px,kind,
        (px-ep)*side*20.,max(0.,(ep-worst)*side)*20.,qty,reason,phase,
        entry_adverse,exit_adverse,missing,signal_day,signal_range,exit_range,
        submitted_i//1440,submitted_i%1440,signal_id])


@njit(cache=False)
def _run(o,h,l,c,weekdays,allow,cutoff,sunday_multiplier,all_days):
    D = o.shape[0]
    out = np.empty((D+16,NCOLS))
    cash_ranges = np.full(D,np.nan)
    rtho,rthh,rthl = 0.,0.,0.
    inrth,armed = False,False
    day_range,signal_range,signal_day = 0.,0.,-1
    last_entry_et = -1
    pending_entry,pending_market = False,0
    order_qty,order_i,order_signal_day,order_range = 1.,-1,-1,0.
    side,ep,entry_i,qty = 0,0.,-1,1.
    worst,entry_adverse,entry_signal_range,entry_signal_day,entry_submit = 0.,0.,0.,-1,-1
    missing,n,last_i,last_close = 0,0,-1,np.nan
    counts = np.zeros(10,np.int64)
    # Native bars, cash closes, down days, emitted entries, delayed next-bar
    # entries, normal exits, safety exits, stop exits, suppressed warm-up orders.
    for i in range(min(D*1440,cutoff)):
        d,j = i//1440,i%1440
        oo,hh,ll,cc = o[d,j],h[d,j],l[d,j],c[d,j]
        if not (np.isfinite(oo) and np.isfinite(hh) and np.isfinite(ll) and np.isfinite(cc)):
            if side:
                missing += 1
            continue
        counts[0] += 1
        last_i,last_close = i,cc
        exited = False
        bar_adverse = oo
        if side:
            worst = min(worst,oo)
        # Market exits and stop gaps have the same open price. Preserve the
        # previously emitted market instruction as the reported exit label.
        if side and pending_market:
            if day_range>0 and oo<=ep-.5*day_range:counts[9] += 1
            _put(out,n,entry_i,i,side,ep,oo,qty,pending_market,0,worst,entry_adverse,oo,
                 missing,entry_signal_day,entry_signal_range,day_range,entry_submit,-1)
            counts[5 if pending_market == 2 else 6] += 1
            n += 1;side = 0;exited = True
        pending_market = 0
        if pending_entry and not side and not exited:
            side,ep,entry_i,qty = 1,oo,i,order_qty
            worst,entry_adverse,missing = oo,oo,0
            entry_signal_day,entry_signal_range,entry_submit = order_signal_day,order_range,order_i
            counts[4] += int(i != order_i+1)
        pending_entry = False
        if side:
            stop = ep-.5*day_range
            reason,px,phase = -1,0.,0
            if day_range > 0 and oo <= stop:
                reason,px = 0,oo
            elif day_range > 0 and ll <= stop:
                reason,px,phase = 0,stop,1
            adverse = px if reason == 0 else ll
            worst = min(worst,adverse)
            bar_adverse = min(oo,adverse)
            if i == entry_i:
                entry_adverse = bar_adverse
            if reason == 0:
                _put(out,n,entry_i,i,side,ep,px,qty,0,phase,worst,entry_adverse,bar_adverse,
                     missing,entry_signal_day,entry_signal_range,day_range,entry_submit,-1)
                counts[7] += 1
                n += 1;side = 0;exited = True
        # The strategy runs its state machine on the native bar's close.
        # Cash range changes only after the source exact15:00 close.
        if j == 511:
            rtho,rthh,rthl = oo,hh,ll
            inrth,armed = True,False
        elif inrth and 511 < j <= 900:
            rthh,rthl = max(rthh,hh),min(rthl,ll)
        if inrth and j == 900:
            down = cc < rtho
            day_range = rthh-rthl
            cash_ranges[d] = day_range
            signal_day,signal_range = d,day_range
            armed = down or all_days
            inrth = False
            counts[1] += 1
            counts[2] += int(down)
        # Source Date/DayOfWeek refer to the ET chart, not CTt. Dates diverge
        # after23:00 CT, even though normal17:01 entry dates are identical.
        et_day = d+int(j>=1380)
        et_weekday = (weekdays[d]+int(j>=1380))%7
        if armed and side == 0 and j >= 1021 and et_day != last_entry_et:
            if allow[d]:
                pending_entry = True
                order_qty = sunday_multiplier if et_weekday == 6 else 1.
                order_i,order_signal_day,order_range = i,signal_day,signal_range
                counts[3] += 1
            else:
                counts[8] += 1
            last_entry_et = et_day
            armed = False
        if side and 180 <= j < 511:
            pending_market = 2
        if side and 511 <= j <= 900:
            pending_market = 3
    state = np.array([side,entry_i,ep,qty,entry_signal_range,entry_signal_day,
                      worst,missing,last_i,last_close,pending_market,1. if pending_entry else 0.])
    return out[:n],counts,state,cash_ranges


def _frame(g,raw):
    t = pd.DataFrame(raw,columns=COLUMNS)
    for col in ['day','j0','exit_day','j1','side','kind','reason_code','exit_phase_code',
                'unknown_held_minutes','signal_day','entry_submit_day','entry_submit_j','signal_id']:
        t[col] = t[col].astype(int)
    t['date'] = pd.to_datetime(g.ts[t.day.to_numpy(int)])
    t['exit_date'] = pd.to_datetime(g.ts[t.exit_day.to_numpy(int)])
    t['cross_date'] = t.exit_day.ne(t.day)
    t['reason'] = t.reason_code.map({0:'stop',2:'time',3:'safety'})
    t['entry_phase'] = 'open'
    t['exit_phase'] = t.exit_phase_code.map({0:'open',1:'intrabar'})
    t['entry_avg_range'] = t.signal_range
    entry_wall=t.day.to_numpy()*1440+t.j0.to_numpy()-1
    exit_wall=t.exit_day.to_numpy()*1440+t.j1.to_numpy()-t.exit_phase.eq('open').to_numpy(int)
    for minute,name in [(959,'crosses_1559_ct'),(945,'crosses_1545_ct')]:
        first=(entry_wall//1440)*1440+minute
        first=np.where(first<entry_wall,first+1440,first)
        t[name]=exit_wall>first
    # Compatibility fields are unweighted per contract; qty stays separate.
    t['net'] = t.pnl-17.25
    t['native_net_per_mnq'] = t.pnl/10-2.24
    return t


def replay(g,sunday_multiplier=2,start_date=None,end_date=None,condition='down'):
    """Literal source replay, with flat1 or source-default Sunday2 quantities.

    condition='all' is an unfiltered diagnostic control, never the default.
    New order dates are bounded, while older cash bars initialize source state.
    Unclosed positions/pending orders at the end are disclosed, not liquidated.
    P&L/MAE are per1NQ and do NOT include qty. All source market entries are long.
    """
    if sunday_multiplier not in (1,2):
        raise ValueError('Only the fixed flat1/Sunday2 quantity cases are supported')
    if condition not in ('down','all'):
        raise ValueError('condition must be down or the explicit all-night control')
    dates = pd.DatetimeIndex(g.ts)
    allow = np.ones(g.D,np.bool_)
    if start_date is not None: allow &= dates>=pd.Timestamp(start_date)
    cutoff = g.D*1440
    if end_date is not None:
        end = pd.Timestamp(end_date)
        allow &= dates<=end
        cutoff = int(dates.searchsorted(end,side='right'))*1440
    raw,counts,state,schedule = _run(g.o,g.h,g.l,g.c,dates.dayofweek.to_numpy(),allow,
                                    cutoff,float(sunday_multiplier),condition=='all')
    g._codex_rebound_ranges = schedule
    g._codex_rebound_schedule_cutoff = cutoff
    t = _frame(g,raw)
    trading = np.asarray(g.trading,int)
    trading = trading[trading*1440<cutoff]
    diag = dict(native_bars=int(counts[0]),cash_closes=int(counts[1]),down_cash_days=int(counts[2]),
        emitted_entries=int(counts[3]),delayed_next_native_bar_entries=int(counts[4]),
        normal_time_exits=int(counts[5]),safety_exits=int(counts[6]),stop_exits=int(counts[7]),
        simultaneous_market_exit_stop_gap_opens=int(counts[9]),
        open_position_at_end=bool(state[0]),open_position_state=state.tolist(),
        pending_entry_at_end=bool(state[11]),missing_0831_dates=[str(dates[d].date()) for d in trading if not np.isfinite(g.o[d,511])],
        missing_1500_dates=[str(dates[d].date()) for d in trading if not np.isfinite(g.c[d,900])],
        condition=condition,sunday_multiplier=sunday_multiplier,
        clock='CT prices normalized to source ET chart minus60 minutes; ET calendar Date retained',
        next_bar='Next available native bar, never an invented clock-minute fill',
        price_rounding='Unrounded half-range distance, as in shared repo execution; MC rounding parity unverified',
        source_safety='Only03:00 morning exit and08:31-15:00 safety exist; no16:45ET/weekend guard was added')
    diag['closed_trades_crossing_1559_ct']=int(t.crosses_1559_ct.sum())
    diag['closed_trades_crossing_1545_ct']=int(t.crosses_1545_ct.sum())
    return t,diag


@njit(cache=False)
def _market_many(o,h,l,c,signals,schedule):
    out = np.empty((len(signals),NCOLS))
    closed = np.zeros(len(signals),np.bool_)
    n,D = 0,o.shape[0]
    for signal_id in range(len(signals)):
        row = signals[signal_id]
        d0,j0,side = int(row[0]),int(row[1]),int(row[2])
        initial_range,qty = row[3],row[4]
        rng = initial_range
        ei = d0*1440+j0
        ep = o[d0,j0]
        worst,entry_adverse,missing,pending = ep,ep,0,0
        for i in range(ei,D*1440):
            d,j = i//1440,i%1440
            oo,hh,ll,cc = o[d,j],h[d,j],l[d,j],c[d,j]
            if not (np.isfinite(oo) and np.isfinite(hh) and np.isfinite(ll) and np.isfinite(cc)):
                missing += 1
                continue
            worst = min(worst,oo) if side>0 else max(worst,oo)
            reason,px,phase = -1,0.,0
            stop = ep-side*.5*rng
            if pending:
                reason,px = pending,oo
            elif rng>0 and ((side>0 and oo<=stop) or (side<0 and oo>=stop)):
                reason,px = 0,oo
            elif rng>0 and ((side>0 and ll<=stop) or (side<0 and hh>=stop)):
                reason,px,phase = 0,stop,1
            adverse = px if reason>=0 else (ll if side>0 else hh)
            worst = min(worst,adverse) if side>0 else max(worst,adverse)
            if i==ei: entry_adverse=adverse
            if reason>=0:
                _put(out,n,ei,i,side,ep,px,qty,reason,phase,worst,entry_adverse,
                     adverse,missing,d0,initial_range,rng,ei-1,signal_id)
                n+=1;closed[signal_id]=True
                break
            if j==900 and np.isfinite(schedule[d]):rng=schedule[d]
            if 180<=j<511:pending=2
            if 511<=j<=900:pending=3
    return out[:n],closed


def replay_market(g,signals):
    """Matched-exit nulls [day,j0,side,signal_range,qty], keyed by signal_id.

    Market entries start at the supplied native open. Unclosed signals are
    reported in DataFrame.attrs, never silently assigned zero P&L.
    """
    signals = np.ascontiguousarray(signals,dtype=float)
    if signals.ndim!=2 or signals.shape[1]!=5:
        raise ValueError('Expected signals[day,j0,side,range,qty]')
    if not len(signals):
        t=_frame(g,np.empty((0,len(COLUMNS))));t.attrs.update(requested_signals=0,closed_signals=0,unclosed_signal_ids=[])
        return t
    d,j = signals[:,0].astype(int),signals[:,1].astype(int)
    assert np.isin(signals[:,2],[-1,1]).all() and (signals[:,3]>0).all() and (signals[:,4]>0).all()
    assert all(np.isfinite(a[d,j]).all() for a in [g.o,g.h,g.l,g.c])
    if getattr(g,'_codex_rebound_schedule_cutoff',0)<g.D*1440:
        dates=pd.DatetimeIndex(g.ts)
        _,_,_,schedule=_run(g.o,g.h,g.l,g.c,dates.dayofweek.to_numpy(),np.zeros(g.D,np.bool_),g.D*1440,1.,False)
        g._codex_rebound_ranges=schedule;g._codex_rebound_schedule_cutoff=g.D*1440
    raw,closed = _market_many(g.o,g.h,g.l,g.c,signals,g._codex_rebound_ranges)
    t=_frame(g,raw)
    t.attrs.update(requested_signals=len(signals),closed_signals=int(closed.sum()),unclosed_signal_ids=np.flatnonzero(~closed).tolist())
    return t


def synthetic_checks():
    """Small deterministic source fixtures; no historical data is accessed."""
    from types import SimpleNamespace
    dates=pd.date_range('2020-01-03',periods=5)  # Friday through Tuesday
    shape=(len(dates),1440)
    arrays=[np.full(shape,np.nan) for _ in range(4)]
    def bar(day,j,op,hi,lo,cl):
        for a,v in zip(arrays,[op,hi,lo,cl]):a[day,j]=v
    # Down Friday arms; no Friday reopen, so the source remains armed Sunday.
    bar(0,511,100,105,95,100);bar(0,900,100,104,94,99)
    bar(2,1021,100,101,99,100);bar(2,1022,100,102,99,101)
    bar(3,180,102,103,101,102);bar(3,181,103,104,102,103)
    # Monday cash up: no subsequent overnight trade.
    bar(3,511,100,104,98,101);bar(3,900,101,106,99,105)
    bar(3,1021,105,106,104,105);bar(3,1022,105,106,104,105)
    bar(4,180,105,106,104,105);bar(4,181,106,106,105,106)
    g=SimpleNamespace(o=arrays[0],h=arrays[1],l=arrays[2],c=arrays[3],D=len(dates),ts=dates.to_numpy(),trading=np.array([0,3,4]))
    one,d1=replay(g,1)
    two,d2=replay(g,2)
    assert len(one)==len(two)==1
    assert one.iloc[0].day==2 and one.iloc[0].signal_day==0
    assert one.iloc[0].j0==1022 and one.iloc[0].j1==181 and one.iloc[0].reason=='time'
    assert one.iloc[0].qty==1 and two.iloc[0].qty==2
    assert one.iloc[0].pnl==two.iloc[0].pnl==60.
    assert one.iloc[0].mae==20. and one.iloc[0].entry_minute_adverse_px==99.
    assert one.iloc[0].signal_range==11.
    assert one.iloc[0].cross_date and not one.iloc[0].crosses_1559_ct
    # Stop is active on entry bar and caps causal MAE at its own execution.
    old_low=g.l[2,1022]
    g.l[2,1022]=90.
    stopped,_=replay(g,1)
    assert stopped.iloc[0].exit==94.5 and stopped.iloc[0].mae==110.
    assert stopped.iloc[0].exit_phase=='intrabar'
    g.l[2,1022]=old_low
    # A gap below the stop pays the next native open, not the stale stop.
    bar(2,1023,90,91,89,90)
    gap,_=replay(g,1)
    assert gap.iloc[0].exit==90. and gap.iloc[0].exit_phase=='open' and gap.iloc[0].mae==200.
    for a in arrays:a[2,1023]=np.nan
    # Missing03:00 leaves no invented exit; first RTH bar emits safety next bar.
    for a in arrays:a[3,180:182]=np.nan
    bar(3,511,103,104,102,103);bar(3,512,104,105,103,104)
    safety,_=replay(g,1)
    assert safety.iloc[0].reason=='safety' and safety.iloc[0].j1==512
    # Pending entry is a nextAVAILABLEbar, even after a missing minute.
    for a in arrays:a[2,1022]=np.nan
    bar(2,1024,101,102,100,101)
    delayed,dd=replay(g,1)
    assert delayed.iloc[0].j0==1024 and dd['delayed_next_native_bar_entries']==1
    # A closed-position record is not fabricated when history ends while open.
    unfinished,du=replay(g,1,end_date='2020-01-05')
    assert len(unfinished)==0 and du['open_position_at_end']
    # Matched-exit helper retains signal IDs, detects unclosed last-day signals,
    # and handles short stop gaps using the same adverse-price convention.
    for a in arrays:a[3:, :]=np.nan
    bar(3,180,90,92,89,91);bar(3,181,91,92,90,91)
    bar(4,1100,100,101,99,100)
    signals=np.array([[2,1024,1,11,1],[4,1100,1,11,1]],float)
    null=replay_market(g,signals)
    assert len(null)==1 and null.iloc[0].signal_id==0 and null.attrs['unclosed_signal_ids']==[1]
    bar(2,1025,110,111,109,110)
    short=replay_market(g,np.array([[2,1024,-1,11,1]],float))
    assert short.iloc[0].exit==110 and short.iloc[0].mae==180.
    # An order first emitted Sunday23:00CT belongs to Monday00:00ET for
    # source DayOfWeek(Date), so SundayQty must NOT be applied to that label.
    late=[np.full(shape,np.nan) for _ in range(4)]
    def latebar(day,j,op,hi,lo,cl):
        for a,v in zip(late,[op,hi,lo,cl]):a[day,j]=v
    latebar(0,511,100,105,95,100);latebar(0,900,100,104,94,99)
    latebar(2,1380,100,101,99,100);latebar(2,1381,100,102,99,101)
    latebar(3,180,102,103,101,102);latebar(3,181,103,104,102,103)
    lategrid=SimpleNamespace(o=late[0],h=late[1],l=late[2],c=late[3],D=len(dates),ts=dates.to_numpy(),trading=np.array([0,3]))
    late_trade,_=replay(lategrid,2)
    assert len(late_trade)==1 and late_trade.iloc[0].qty==1
    # Missing every morning/cash bar defers the safety market instruction
    # beyond a later15:59 checkpoint. Cross-date alone is not the guard.
    for a in late:a[3,:]=np.nan
    latebar(3,900,102,103,101,102);latebar(3,1021,103,104,102,103)
    late_exit,_=replay(lategrid,2)
    assert late_exit.iloc[0].reason=='safety' and late_exit.iloc[0].crosses_1559_ct
    return dict(friday_signal_enters_sunday=True,source_sunday_qty_separate_from_unit_pnl=True,
        source_market_entry_and_exit_next_bar=True,up_cash_day_skipped=True,
        entry_bar_stop_causal=True,worse_open_stop_gap=True,missing_clock_exit_uses_safety=True,
        next_available_bar_order=True,unclosed_position_disclosed=True,
        null_signal_ids_and_unclosed_ids=True,short_stop_gap=True,
        intended_overnight_does_not_violate_daily_flat_checkpoint=True,
        late_et_calendar_controls_sunday_quantity=True,delayed_safety_flags_flat_checkpoint=True)
