"""No-return feasibility and arithmetic audit of a user-uploaded QJ example.

Never imports Backtester, executes main/_credentials, authenticates, or computes
historical candidate returns. Selected pure definitions run on synthetic inputs.
"""
from pathlib import Path
from types import SimpleNamespace
import ast, argparse, hashlib, json, math
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/qj_donchian_20261030'
OUT=ROOT/'analysis/outputs/codex_qj_donchian_20261030'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,default=str)+'\n')
def definitions():
    a=ast.parse((INPUT/'uploaded.py').read_text())
    wanted={'average_true_range','size_futures_contracts','FuturesDonchianContracts'}
    body=[n for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted]
    assert {n.name for n in body}==wanted
    env={'np':np,'pd':pd,'math':math,'Backtester':object}
    exec(compile(ast.Module(body=body,type_ignores=[]),'<audited-pure-user-definitions>','exec'),env)
    return env
def arithmetic():
    OUT.mkdir(parents=True,exist_ok=True);env=definitions();f=env['size_futures_contracts'];checks={}
    def check(name,value):
        checks[name]=bool(value)
        if not value:raise AssertionError(name)
    check('zero_price_no_qty',f(nav=50000,price=0,atr=5,multiplier=2,margin=100)==0)
    check('negative_price_no_qty',f(nav=50000,price=-10,atr=5,multiplier=1000,margin=7000)==0)
    check('nan_atr_no_qty',f(nav=50000,price=100,atr=np.nan,multiplier=2,margin=100)==0)
    check('risk_cap_is_binding',f(nav=100000,price=10,atr=50,multiplier=2,margin=10)==5)
    check('notional_cap_is_binding',f(nav=100000,price=1000,atr=1,multiplier=2,margin=10)==12)
    check('reference_margin_cap_is_binding',f(nav=100000,price=10,atr=1,multiplier=2,margin=10000)==1)
    facts=json.loads((INPUT/'published_facts.json').read_text());rows=[];mismatch=[]
    for z in facts['last_positions']:
        min_nav=z['price']*z['multiplier']/.25
        rows.append(dict(symbol=z['symbol'],price=z['price'],multiplier=z['multiplier'],
            min_nav_one_contract_notional_only=min_nav,
            notional_only_ceiling_50000=math.floor(50000*.25/(z['price']*z['multiplier'])),
            notional_only_ceiling_150000=math.floor(150000*.25/(z['price']*z['multiplier'])),
            notional_only_ceiling_2000000=math.floor(2000000*.25/(z['price']*z['multiplier']))))
        expected=z['quantity']*z['price']*z['multiplier']
        mismatch.append(dict(symbol=z['symbol'],reported_market_value=z['reported_market_value'],
            signed_notional_expected=expected,multiplier_ratio=expected/z['reported_market_value']))
        check(z['symbol']+'_published_open_value_missing_multiplier',np.isclose(expected,z['reported_market_value']*z['multiplier']))
    pd.DataFrame(rows).to_csv(OUT/'sizing_bounds.csv',index=False)
    pd.DataFrame(mismatch).to_csv(OUT/'published_multiplier_check.csv',index=False)
    # Cross-asset ATR grouping compared with an independent explicit column loop.
    close=pd.DataFrame({'A':[10,11,10,14,13],'B':[80,70,90,85,100]},dtype=float)
    high=close+pd.DataFrame({'A':[1,2,3,2,1],'B':[3,4,2,5,2]})
    low=close-pd.DataFrame({'A':[2,1,1,3,1],'B':[4,2,5,2,3]})
    got=env['average_true_range'](high,low,close,window=3)
    expect=pd.DataFrame(index=close.index,columns=close.columns,dtype=float)
    for col in close:
        prev=close[col].shift()
        tr=pd.concat([high[col]-low[col],(high[col]-prev).abs(),(low[col]-prev).abs()],axis=1).max(axis=1)
        expect[col]=tr.rolling(3,min_periods=3).mean()
    check('atr_separate_assets_and_simple_mean',np.allclose(got,expect,equal_nan=True))
    # Exercise actual user order-generation on synthetic data, with an inert stub.
    C=env['FuturesDonchianContracts'];idx=pd.bdate_range('2020-01-01',periods=60)
    hh=pd.DataFrame({'X':np.full(60,100.)},index=idx);ll=hh-5;cc=hh-2
    frames={'adj_close':cc,'high':hh,'low':ll}
    obj=C();obj._atr_cache=None;obj.instruments=['X'];obj.fill_engine=SimpleNamespace(pending_orders=[])
    obj.instruments_data=SimpleNamespace(get_feature=lambda k:frames[k]);obj._contract_spec=lambda k:SimpleNamespace(multiplier=1.,margin=1.)
    orders=[];obj.order_market=lambda instrument,delta,tag:orders.append((instrument,delta,tag))
    cc.iloc[55,0]=101.;hh.iloc[55,0]=102.
    obj._compute_orders(idx[54],{'X':SimpleNamespace(close=98.)},{},10000.)
    check('55_prior_rows_required',not orders)
    obj._compute_orders(idx[55],{'X':SimpleNamespace(close=101.)},{},10000.)
    check('breakout_excludes_current_high',len(orders)==1 and orders[-1][1]>0)
    orders.clear();obj._compute_orders(idx[56],{'X':SimpleNamespace(close=98.)},{'X':2.},10000.)
    check('inside_band_carries_and_resizes_position',len(orders)==1 and orders[0][1]>0)
    orders.clear();obj._compute_orders(idx[56],{'X':SimpleNamespace(close=98.)},{},10000.)
    check('flat_inside_band_does_not_remember_direction',not orders)
    orders.clear();obj._compute_orders(idx[56],{'X':SimpleNamespace(close=94.)},{'X':2.},10000.)
    check('opposite_breakout_delta_covers_and_reverses',len(orders)==1 and orders[0][1]<-2)
    obj.fill_engine.pending_orders=[SimpleNamespace(instrument='X',is_active=True)];orders.clear()
    obj._compute_orders(idx[56],{'X':SimpleNamespace(close=94.)},{'X':2.},10000.)
    check('active_pending_order_skips_symbol',not orders)
    # Historical source positions only: arithmetic, not a rebuilt NAV or return.
    result=dict(passed=all(checks.values()),checks=checks,count=len(checks),return_trials=0,
        source_sha256=sha(INPUT/'uploaded.py'),code_sha256=sha(__file__),
        performance_status='Published claims only; no historical return replication',
        never_executed=['_credentials','main','Backtester','authenticated API'],
        source_fact_url=facts['json_url'],source_fact_snapshot_sha256=sha(INPUT/'published_facts.json'),
        limits=['Sizing bounds are necessary notional-only conditions at2025-12-31prices; ATR/margin can reduce further',
                'Reference margins are source constants, not current broker requirements',
                'Synthetic rule checks are not economic evidence or an independent backtest'])
    dump(OUT/'arithmetic_audit.json',result);print(json.dumps(result,indent=2))
def inventory(data):
    OUT.mkdir(parents=True,exist_ok=True);summary=[];allrows=[];hashes=[]
    for market in ['ES','NQ','CL','GC']:
        files=[]
        for y in range(2017,2023):
            for stem in ([market+'_1min_',market+'_1min_ON_'] if market=='NQ' else [market+'_1min_']):
                p=Path(data)/f'{stem}{y}.csv'
                if p.exists():files.append(p)
        raw=pd.concat([pd.read_csv(p,usecols=['date','time']) for p in files],ignore_index=True)
        dup=int(raw.duplicated(['date','time']).sum());raw=raw.drop_duplicates(['date','time'])
        day=pd.to_datetime(raw.date.astype(str),format='%Y%m%d');j=raw.time//100*60+raw.time%100
        mask=(j<=960)|(j>1020)
        label=day+pd.to_timedelta((j>1020).astype(int),unit='D')
        elapsed=np.where(j>1020,j-1020,j+420)
        valid=mask & label.between('2018-01-02','2022-12-30') & (label.dt.dayofweek<5)
        f=pd.DataFrame({'date':label[valid],'minute':elapsed[valid]})
        r=f.groupby('date').minute.agg(['count','min','max']).reset_index();r['market']=market
        r.to_csv(OUT/f'{market}_timestamp_sessions.csv',index=False);allrows.append(r)
        fields=set().union(*(set(pd.read_csv(p,nrows=0).columns) for p in files))
        summary.append(dict(market=market,session_labels=len(r),opening_minute_present=int((r['min']==1).sum()),
            standard_close_present=int((r['max']==1380).sum()),duplicates=dup,
            first=str(r.date.min().date()),last=str(r.date.max().date()),
            contract_id_column_present=bool(fields&{'contract','contract_id','symbol','instrument'}),
            adjustment_or_roll_fields_present=bool(fields&{'roll','adjustment','adjustment_factor','roll_price'})))
        for p in files:hashes.append(dict(path=str(p),sha256=sha(p)))
    pd.DataFrame(summary).to_csv(OUT/'inventory_summary.csv',index=False)
    result=dict(no_price_columns_parsed_or_candidate_returns_computed=True,assumed_clock='17:01prevdate through16:00sessiondate, CT; not Yahoo or native contract clock parity',
        market_summary=summary,inputs=hashes,
        data_gate='NEEDS DATA: no executable contract roll chain or source dataset; timestamp gaps require explicit handling',
        no_full_2017_NQ_day_file=not (Path(data)/'NQ_1min_2017.csv').exists(),
        common_dates=len(set.intersection(*[set(r.date) for r in allrows])),
        own_returns_computed=False,account_simulations_run=False)
    dump(OUT/'inventory.json',result);print(json.dumps({k:v for k,v in result.items() if k!='inputs'},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['arithmetic','inventory']);p.add_argument('--data',default='/workspace/thebeginning/data');a=p.parse_args()
    arithmetic() if a.phase=='arithmetic' else inventory(a.data)
