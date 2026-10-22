"""Offline execution observations. No orders, strategy evaluation, notifications or live writes.

Called by codex_live_reconcile --execution-diagnostics. Explicit event IDs define
the sampling unit; separate account copies never create independent market events.
"""
from pathlib import Path
import hashlib
import io
import json
import subprocess

import numpy as np
import pandas as pd

from codex_live_reconcile import COLS, blob, identity, json_write

ROOT=Path(__file__).resolve().parents[1]
OFFSETS=(-5,-2,-1,0,1,2,5)
STRATEGIES=('VB','ONB_ADX30','MON_BR')
REQUIRED=('attempt_id','event_id','trading_date','strategy','account','instrument','actual_contract',
          'side','qty','filled_qty','order_type','status','reason','order_id','fill_price',
          'signal_time_utc','submission_time_utc','fill_time_utc')


def digest(b):return hashlib.sha256(b).hexdigest()


def aware(value):
    if value is None or pd.isna(value) or str(value).strip()=='':return pd.NaT
    t=pd.Timestamp(value)
    if t.tzinfo is None:raise ValueError('UTC fields require explicit timezone offsets')
    return t.tz_convert('UTC')


def read_orders(path):
    d=pd.read_csv(path,dtype=str,keep_default_na=False)
    if not set(REQUIRED).issubset(d):raise ValueError('Missing canonical order fields: '+str(sorted(set(REQUIRED)-set(d))))
    for k in ('attempt_id','event_id','trading_date','strategy'):
        if d[k].eq('').any():raise ValueError('Missing '+k)
    pd.to_datetime(d.trading_date,format='%Y-%m-%d',errors='raise')
    if d.attempt_id.duplicated().any():raise ValueError('Duplicate attempt IDs; retain unique order/execution records')
    if not d.strategy.isin(STRATEGIES).all():raise ValueError('Use VB, ONB_ADX30 or MON_BR explicitly')
    for k in ('side','qty','filled_qty'):
        d[k]=pd.to_numeric(d[k],errors='raise')
    if not d.side.isin([-1,1]).all() or not ((d.qty>0)&(d.qty%1==0)&(d.filled_qty>=0)&(d.filled_qty<=d.qty)&(d.filled_qty%1==0)).all():
        raise ValueError('Invalid side, size or filled quantity')
    if not d.status.isin(['filled','partially_filled','rejected','cancelled','missed','unresolved']).all():raise ValueError('Unsupported order status')
    d['fill_price']=pd.to_numeric(d.fill_price.mask(d.fill_price.eq('')),errors='raise')
    for k in ('signal_time_utc','submission_time_utc','fill_time_utc'):
        d[k]=pd.to_datetime([aware(v) for v in d[k]],utc=True)
    for z in d.itertuples():
        if z.status in ('rejected','cancelled','missed') and (z.filled_qty!=0 or pd.notna(z.fill_time_utc) or pd.notna(z.fill_price)):
            raise ValueError('An unfilled final status cannot carry a fill; represent partial fills explicitly')
        if z.status in ('filled','partially_filled') and (z.filled_qty<=0 or not np.isfinite(z.fill_price) or z.fill_price<=0):
            raise ValueError('Filled rows require positive actual fill price and quantity')
        clocks=[t for t in (z.signal_time_utc,z.submission_time_utc,z.fill_time_utc) if pd.notna(t)]
        if clocks!=sorted(clocks):raise ValueError('Known signal/submission/fill clocks are out of order')
    for event,g in d.groupby('event_id'):
        if any(g[c].nunique()>1 for c in ['strategy','side','trading_date']):raise ValueError('Conflicting event identity '+event)
        if g.actual_contract[g.actual_contract.ne('')].nunique()>1:raise ValueError('Different contracts need reviewed event attribution')
    if 'coverage_verified' not in d:d['coverage_verified']='false'
    d['classification']=d.status
    d.loc[d.status.eq('missed')&~d.coverage_verified.str.lower().eq('true'),'classification']='unresolved_no_fill'
    return d


def tracker_entries(text, timezone=None):
    """Exact six entry rows from the hand transcription; no account or clock inference."""
    rows=[]
    for line in text.splitlines():
        c=[v.strip().replace('**','') for v in line.strip().strip('|').split('|')]
        if len(c)!=13 or c[4]!='VaultBreak entry, market':continue
        number=c[0];mmdd,clock=c[1].split();day='2026-'+mmdd.replace('/','-')
        generated=day+' '+clock
        status_raw=c[2]
        status_time=('2026-'+status_raw.split()[0].replace('/','-')+' '+status_raw.split()[1]
                     if '/' in status_raw else day+' '+status_raw)
        status=c[8].lower();filled=status=='filled'
        contract=c[3] if not c[3].startswith('@') else ''
        # One reviewed decision slot across chart/account copies, not rounded arbitrary executions.
        slot=clock[:5].replace(':','')
        event=f'VB_{day}_{slot}_tracker_decision'
        to_utc=lambda t:pd.Timestamp(t).tz_localize(timezone,ambiguous='raise',nonexistent='raise').tz_convert('UTC').isoformat() if timezone else ''
        price_raw=c[11]
        price_parts=price_raw.replace(',','').split()
        price=float(price_parts[0]) if filled else ''
        if filled and len(price_parts)>1:
            numerator,denominator=price_parts[1].split('/')
            price+=float(numerator)/float(denominator)
        rows.append(dict(attempt_id='tracker_row_'+number,event_id=event,trading_date=day,strategy='VB',account='',
          visible_account_prefix='APEX-681524 (suffix clipped)',instrument=c[3],actual_contract=contract,
          side=1 if c[5]=='Buy' else -1,qty=int(c[6]),filled_qty=int(c[7]),order_type='market',status=status,
          reason='',reason_availability='not transcribed; mapping diagnosis is contextual evidence',order_id=c[12],
          fill_price=price,fill_price_raw=price_raw,signal_time_utc='',submission_time_utc='',
          fill_time_utc=to_utc(status_time) if filled else '',order_generated_time_raw=generated,
          status_time_raw=status_time,broker_fill_time_raw=status_time if filled else '',
          generated_to_status_ms=(pd.Timestamp(status_time)-pd.Timestamp(generated)).total_seconds()*1000,
          clock_zone=timezone or 'VPS displayed clock; timezone unverified',clock_verified=bool(timezone),
          source_row=number,source='live/orders_20261020_21.md',coverage_verified=False,
          generated_time_utc=to_utc(generated)))
    if len(rows)!=6:raise ValueError('Unexpected tracker transcription: expected six entry rows; review parser')
    return pd.DataFrame(rows)


def load_bars(path):
    if not path:return None
    d=pd.read_csv(path,keep_default_na=False)
    cols=['bar_close_time_utc','symbol','actual_contract','open','high','low','close']
    if not set(cols).issubset(d):raise ValueError('Bars need '+str(cols))
    d['bar_close_time_utc']=pd.to_datetime([aware(v) for v in d.bar_close_time_utc],utc=True)
    if d.bar_close_time_utc.isna().any() or ((d.bar_close_time_utc.dt.second!=0)|(d.bar_close_time_utc.dt.microsecond!=0)).any():raise ValueError('Bars must have exact UTC minute close timestamps')
    for c in ['open','high','low','close']:d[c]=pd.to_numeric(d[c],errors='raise')
    p=d[['open','high','low','close']].to_numpy()
    if not(np.isfinite(p).all() and (p>0).all() and (d.high>=p.max(1)).all() and (d.low<=p.min(1)).all()):raise ValueError('Invalid bar OHLC')
    if d.duplicated(['symbol','actual_contract','bar_close_time_utc']).any():raise ValueError('Ambiguous duplicate minute bars')
    return d


def window_sample(anchor,offset,bars,contract):
    base=dict(target_time_utc='',sample_time_utc='',sample_lag_seconds=np.nan,price=np.nan,symbol='',
              actual_contract='',benchmark_kind='',availability='unavailable_anchor_clock')
    if pd.isna(anchor):return base
    target=anchor+pd.Timedelta(minutes=offset);base['target_time_utc']=target.isoformat()
    local=target.tz_convert('America/Chicago')
    if local.dayofweek==5 or (local.dayofweek==6 and local.hour<17):
        base['availability']='unavailable_weekend_preopen';return base
    if bars is None or bars.empty:
        base['availability']='unavailable_minute_bars';return base
    # Completed minute close at or before the requested instant. Never nearest/future or Friday carry-forward.
    expected=target.floor('min')
    candidates=bars[bars.bar_close_time_utc.eq(expected)]
    root='MNQ' if contract.startswith('MNQ') else 'NQ' if contract.startswith('NQ') else ''
    exact=candidates[candidates.actual_contract.eq(contract)&candidates.symbol.eq(root)] if contract else candidates.iloc[:0]
    proxy=candidates[candidates.symbol.eq('NQ')&candidates.actual_contract.eq('')]
    if len(exact)==1:chosen=exact.iloc[0];kind='same_contract_minute_close'
    elif len(proxy)==1:chosen=proxy.iloc[0];kind='NQ_continuous_price_proxy'
    else:base['availability']='unavailable_exact_minute_or_ambiguous_contract';return base
    base.update(sample_time_utc=chosen.bar_close_time_utc.isoformat(),sample_lag_seconds=(target-chosen.bar_close_time_utc).total_seconds(),
       price=float(chosen.close),symbol=chosen.symbol,actual_contract=chosen.actual_contract,
       benchmark_kind=kind,availability='observed_completed_minute_close')
    return base


def windows(orders,bars):
    rows=[]
    for z in orders.itertuples():
        for basis in ['signal','fill']:
            anchor=getattr(z,basis+'_time_utc')
            for offset in OFFSETS:
                v=window_sample(anchor,offset,bars,z.actual_contract)
                if basis=='fill' and z.filled_qty==0:v['availability']='unavailable_no_fill'
                rows.append(dict(attempt_id=z.attempt_id,event_id=z.event_id,basis=basis,offset_minutes=offset,**v))
    return pd.DataFrame(rows,columns=['attempt_id','event_id','basis','offset_minutes','target_time_utc',
      'sample_time_utc','sample_lag_seconds','price','symbol','actual_contract','benchmark_kind','availability'])


def quote_costs(orders,path):
    quotes=pd.read_csv(path,keep_default_na=False) if path else pd.DataFrame()
    if path:
        required=['attempt_id','basis','quote_time_utc','bid','ask','symbol','actual_contract','freshness_verified']
        if not set(required).issubset(quotes):raise ValueError('Quotes need '+str(required))
        quotes['quote_time_utc']=pd.to_datetime([aware(v) for v in quotes.quote_time_utc],utc=True)
        for c in ('bid','ask'):quotes[c]=pd.to_numeric(quotes[c],errors='raise')
        if not quotes.basis.isin(['signal','submission','fill']).all():raise ValueError('Quote basis must be signal/submission/fill')
        if not set(quotes.attempt_id).issubset(set(orders.attempt_id)):raise ValueError('Unattributed quote attempt ID')
    rows=[]
    for z in orders.itertuples():
        r=dict(attempt_id=z.attempt_id,event_id=z.event_id,quoted_spread_submission_ticks=np.nan,
               quoted_spread_fill_ticks=np.nan,effective_fill_cost_vs_mid_ticks=np.nan,
               signed_signal_to_fill_mid_move_ticks=np.nan,total_fill_vs_signal_mid_ticks=np.nan,
               availability='unavailable_contemporaneous_same_contract_quotes')
        mids={}
        for basis in ['signal','submission','fill']:
            tm=getattr(z,basis+'_time_utc')
            if quotes.empty or pd.isna(tm):continue
            root='MNQ' if z.actual_contract.startswith('MNQ') else 'NQ' if z.actual_contract.startswith('NQ') else ''
            q=quotes[quotes.attempt_id.eq(z.attempt_id)&quotes.basis.eq(basis)&quotes.symbol.eq(root)&
                     quotes.actual_contract.eq(z.actual_contract)&quotes.actual_contract.ne('')]
            q=q[q.freshness_verified.astype(str).str.lower().eq('true')&q.quote_time_utc.le(tm)&
                q.quote_time_utc.ge(tm-pd.Timedelta(seconds=1))]
            if len(q)!=1:continue
            v=q.iloc[0]
            if not(np.isfinite([v.bid,v.ask]).all() and v.bid>0 and v.ask>v.bid):continue
            mids[basis]=(v.bid+v.ask)/2
            if basis in ['submission','fill']:r['quoted_spread_'+basis+'_ticks']=(v.ask-v.bid)/.25
        if 'fill' in mids and z.filled_qty>0:
            r['effective_fill_cost_vs_mid_ticks']=z.side*(z.fill_price-mids['fill'])/.25
            r['availability']='fill_quote_observed; other components may remain unavailable'
            if 'signal' in mids:
                r['signed_signal_to_fill_mid_move_ticks']=z.side*(mids['fill']-mids['signal'])/.25
                r['total_fill_vs_signal_mid_ticks']=z.side*(z.fill_price-mids['signal'])/.25
        rows.append(r)
    return pd.DataFrame(rows,columns=['attempt_id','event_id','quoted_spread_submission_ticks','quoted_spread_fill_ticks',
      'effective_fill_cost_vs_mid_ticks','signed_signal_to_fill_mid_move_ticks','total_fill_vs_signal_mid_ticks','availability'])


def event_summary(d):
    rows=[]
    for event,g in d.groupby('event_id',sort=True):
        known=g.account[g.account.ne('')].unique()
        rows.append(dict(event_id=event,trading_date=g.trading_date.iloc[0],strategy=g.strategy.iloc[0],
          market_event_count=1,order_attempt_rows=len(g),known_accounts=len(known),
          account_assignment_complete=bool(g.account.ne('').all()),filled_order_rows=int((g.filled_qty>0).sum()),
          rejected_order_rows=int(g.status.eq('rejected').sum()),classification=';'.join(sorted(g.classification.unique())),
          any_verified_signal_clock=bool(g.signal_time_utc.notna().any()),
          any_verified_fill_clock=bool(g.fill_time_utc.notna().any())))
    return pd.DataFrame(rows,columns=['event_id','trading_date','strategy','market_event_count','order_attempt_rows',
      'known_accounts','account_assignment_complete','filled_order_rows','rejected_order_rows','classification',
      'any_verified_signal_clock','any_verified_fill_clock'])


def chart_rows(ref,start,end,paths,hashes):
    rows=[];coverage=[]
    for day in pd.date_range(pd.Timestamp(start)-pd.Timedelta(days=1),end):
        path='live/trades/'+day.strftime('%Y%m%d')+'.csv'
        exists=path in paths;coverage.append(dict(day=day.strftime('%Y-%m-%d'),path=path,file_present=exists,complete_coverage=False))
        if not exists:continue
        b=blob(ref,path);hashes[path]=digest(b)
        x=pd.read_csv(io.BytesIO(b),names=COLS,dtype=str,keep_default_na=False)
        x=x[x.event.isin(['OPEN','CLOSE'])].copy()
        for source_row,z in x.iterrows():
            base,label=identity(z.tag);strategy='ONB_ADX30' if base=='ONB' else base
            if strategy not in STRATEGIES:continue
            rows.append(dict(source_file=path,source_row=source_row+1,event=z.event,strategy=strategy,tag=z.tag,
              account_label=label,account_verified=False,symbol=z.symbol,entry_date=z.entry_date,
              chart_entry_time=z.entry_time,chart_entry_price=z.entry_price,contracts=z.contracts,
              chart_bar_date=z.bar_date,chart_bar_time=z.bar_time,execution_verified=False))
    cols=['source_file','source_row','event','strategy','tag','account_label','account_verified','symbol','entry_date',
          'chart_entry_time','chart_entry_price','contracts','chart_bar_date','chart_bar_time','execution_verified']
    raw=pd.DataFrame(rows,columns=cols)
    key=['event','strategy','tag','entry_date','chart_entry_time','chart_entry_price','contracts']
    return raw,raw.drop_duplicates(key),pd.DataFrame(coverage)


def run(ref,out,start,end,orders_input=None,bars_input=None,quotes_input=None,tracker_timezone=None):
    commit=subprocess.check_output(['git','rev-parse',ref],text=True).strip()
    paths=set(subprocess.check_output(['git','ls-tree','-r','--name-only',commit],text=True).splitlines())
    source='live/orders_20261020_21.md';b=blob(commit,source);hashes={source:digest(b)}
    if orders_input:
        d=read_orders(orders_input);hashes[str(orders_input)]=digest(Path(orders_input).read_bytes())
    else:
        seed=tracker_entries(b.decode(),tracker_timezone)
        seed.to_csv(out/'tracker_entries_transcribed.csv',index=False)
        d=read_orders(out/'tracker_entries_transcribed.csv')
    d=d[d.trading_date.ge(start)&d.trading_date.le(end)].copy()
    d.to_csv(out/'entry_attempts.csv',index=False)
    events=event_summary(d);events.to_csv(out/'market_events.csv',index=False)
    bars=load_bars(bars_input)
    for path in [bars_input,quotes_input]:
        if path:hashes[str(path)]=digest(Path(path).read_bytes())
    w=windows(d,bars);w.to_csv(out/'entry_windows.csv',index=False)
    costs=quote_costs(d,quotes_input);costs.to_csv(out/'execution_cost_components.csv',index=False)
    moves=[]
    for z in d.itertuples():
        q=w[w.attempt_id.eq(z.attempt_id)&w.basis.eq('fill')].set_index('offset_minutes')
        for h in [1,2,5]:
            valid=q.loc[0,'availability']==q.loc[h,'availability']=='observed_completed_minute_close'
            consistent=q.loc[0,'benchmark_kind']==q.loc[h,'benchmark_kind'] and q.loc[0,'actual_contract']==q.loc[h,'actual_contract']
            value=z.side*(q.loc[h,'price']-q.loc[0,'price'])/.25 if valid and consistent else np.nan
            moves.append(dict(attempt_id=z.attempt_id,event_id=z.event_id,horizon_minutes=h,signed_market_move_ticks=value,
             benchmark_kind=q.loc[h,'benchmark_kind'],availability='descriptive_bar_close_movement' if np.isfinite(value) else 'unavailable',
             delayed_strategy_pnl_computed=False))
    pd.DataFrame(moves).to_csv(out/'post_entry_market_movement.csv',index=False)
    raw,unique,coverage=chart_rows(commit,start,end,paths,hashes)
    raw.to_csv(out/'chart_entry_evidence_raw.csv',index=False);unique.to_csv(out/'chart_entry_evidence_unique.csv',index=False)
    coverage.to_csv(out/'chart_file_coverage.csv',index=False)
    weekly=[]
    for day in pd.date_range(start,end,freq='D'):
        daystr=day.strftime('%Y-%m-%d')
        for strategy in STRATEGIES:
            e=events[events.trading_date.eq(daystr)&events.strategy.eq(strategy)]
            weekly.append(dict(day=daystr,strategy=strategy,observed_market_events=len(e),
              filled_market_events=int(e.filled_order_rows.gt(0).sum()),rejected_market_events=int(e.rejected_order_rows.gt(0).sum()),
              order_attempt_rows=int(e.order_attempt_rows.sum()),coverage='partial_observed_evidence' if len(e) else 'unresolved_coverage',
              spread_measurable=False,signal_to_fill_measurable=False,nearby_prices_measurable=False))
    # Counts/measurements above describe this source week. Optional samples receive explicit per-attempt availability.
    week=pd.DataFrame(weekly)
    for i,z in week.iterrows():
        ids=set(d.loc[d.trading_date.eq(z.day)&d.strategy.eq(z.strategy),'attempt_id'])
        cc=costs[costs.attempt_id.isin(ids)];ww=w[w.attempt_id.isin(ids)]
        week.loc[i,'spread_measurable']=bool(cc.quoted_spread_fill_ticks.notna().any() or cc.quoted_spread_submission_ticks.notna().any())
        week.loc[i,'signal_to_fill_measurable']=bool(cc.total_fill_vs_signal_mid_ticks.notna().any())
        week.loc[i,'nearby_prices_measurable']=bool(ww.price.notna().any())
    week.to_csv(out/'weekly_coverage.csv',index=False)
    # Metadata only, not a strategy cache/backtest. Preserve separate day/night coverage.
    data=[]
    for path in ['data/NQ_1min_2026.csv','data/NQ_1min_ON_2026.csv']:
        if path not in paths:continue
        bb=blob(commit,path);hashes[path]=digest(bb)
        xx=pd.read_csv(io.BytesIO(bb),usecols=['date','time'])
        data.append(dict(path=path,first_date=int(xx.date.min()),last_date=int(xx.date.max()),
          covers_requested_week=bool(xx.date.max()>=int(end.replace('-',''))),benchmark='NQ continuous proxy; not actual MNQ bid/ask'))
    pd.DataFrame(data).to_csv(out/'owned_minute_data_coverage.csv',index=False)
    summary=dict(source_commit=commit,start=start,end=end,distinct_market_events=len(events),order_attempt_rows=len(d),
      filled_market_events=int(events.filled_order_rows.gt(0).sum()),rejected_market_events=int(events.rejected_order_rows.gt(0).sum()),
      known_account_attributions=int(d.account.ne('').sum()),window_observations=int(w.price.notna().sum()),
      return_trials=0,entry_rules_changed=False,live_changes=False,complete_week=False,
      tracker_timezone=tracker_timezone or 'unverified; UTC conversion refused',
      notes=['Order Generated is a platform timestamp, not verified broker submission/receipt',
       'Tracker status time is a fill time only on filled records; rejection update is not a fill',
       'Two accounts or order copies sharing a reviewed event ID count once; distinct IDs do not establish statistical independence',
       'Chart bar labels remain distinct from signal/real execution clocks; no 30-minute time correction',
       'No expected entry inferred from missing files or POS-only logs',
       'Logger sidecar proposal gives chart-observation quotes, not submission/fill quotes',
       'No delayed-entry P&L or spread filter tested'],source_sha256=hashes)
    json_write(out/'diagnostics_summary.json',summary)
    print(json.dumps({k:summary[k] for k in ['source_commit','distinct_market_events','order_attempt_rows','filled_market_events','rejected_market_events','window_observations','complete_week']},indent=2))
    return summary
