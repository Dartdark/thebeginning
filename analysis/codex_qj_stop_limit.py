"""Disconnected, synthetic order tests of the pasted QJ example and pinned engine.

No credentials, API client, source main(), historical prices, parameter search
or strategy-return test. The original strategy class is extracted with AST;
the reviewed public FillEngine/Order/slippage/commission modules run unchanged.
"""
from pathlib import Path
import ast,hashlib,importlib,json,sys,types
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/qj_stop_limit_20261030'
OUT=ROOT/'analysis/outputs/codex_qj_stop_limit_20261030'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_reviewed_modules():
    frozen=json.loads((INPUT/'frozen_hashes.json').read_text())
    for rel,digest in frozen.items():assert sha(ROOT/rel)==digest,rel
    # Bypass package __init__/SDK imports entirely. Only these four reviewed
    # pure execution modules are imported. No authentication helper is loaded.
    assert 'backtester' not in sys.modules
    for name,rel in [('backtester','backtester'),('backtester.execution','backtester/execution')]:
        package=types.ModuleType(name);package.__path__=[str(INPUT/'upstream'/rel)]
        sys.modules[name]=package
    order=importlib.import_module('backtester.execution.order_types')
    engine=importlib.import_module('backtester.execution.fill_engine')
    slip=importlib.import_module('backtester.execution.slippage')
    fee=importlib.import_module('backtester.execution.commission')
    return order,engine,slip,fee

def main():
    O,E,S,C=load_reviewed_modules()
    class Features:
        def __init__(self):self.frames={}
        def get_feature(self,key):return self.frames[key]
    class Base:
        def __init__(self,**kwargs):
            self.instruments=['SPY'];self.instruments_data=Features();self.entry=100.
        def get_average_entry_price(self,inst):return self.entry
    tree=ast.parse((INPUT/'source.py').read_text())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='StopLimitProtection')
    namespace=dict(Backtester=Base,pd=pd,Order=O.Order,OrderSide=O.OrderSide,OrderType=O.OrderType)
    exec(compile(ast.Module(body=[cls],type_ignores=[]),'archived_source_class','exec'),namespace)
    Strategy=namespace['StopLimitProtection'];events=[]
    def engine(**kwargs):return E.FillEngine(slippage=S.FixedBpsSlippage(bps=5),
        commission=C.PerShareCommission(cost_per_share=.005,min_per_order=1),**kwargs)
    def bar(date='2020-02-03',o=100,h=101,l=99,c=100,v=1000):
        return O.BarData(pd.Timestamp(date),o,h,l,c,v)
    def context(strategy,signal,pos,date='2020-02-03',b=None):
        date=pd.Timestamp(date);b=b or bar(date)
        for name,value in [('SMA_20_close',101. if signal else 99.),('SMA_50_close',100.)]:
            strategy.instruments_data.frames[name]=pd.DataFrame({'SPY':[value]},index=[date])
        strategy._compute_orders(date,{'SPY':b},{'SPY':pos},100000.)
    def order_summary(e):return [dict(type=o.order_type.value,side=o.side.value,quantity=o.quantity,
        remaining=o.remaining_qty,status=o.status.value,stop=o.stop_price,limit=o.limit_price,
        activated=o._limit_activated)for o in e.order_history]
    def fill_summary(fills):return [dict(side=f.side.value,quantity=f.quantity,price=f.fill_price,
        commission=f.commission,slippage=f.slippage)for f in fills]
    def record(name,**kwargs):events.append(dict(scenario=name,expectation_reproduced=True,**kwargs))

    # 1. Entry is not a bracket; protection appears after the entry day's close.
    e=engine();s=Strategy();s.fill_engine=e
    context(s,1,0);assert len(e.pending_orders)==1 and e.pending_orders[0].order_type==O.OrderType.MARKET
    fills=e.process_bar('SPY',bar('2020-02-04',o=100,h=101,l=90,c=92))
    assert len(fills)==1 and fills[0].side==O.OrderSide.BUY and not e.pending_orders
    s.entry=fills[0].fill_price
    context(s,1,fills[0].quantity,'2020-02-04',bar('2020-02-04',o=100,h=101,l=90,c=92))
    assert len(e.pending_orders)==1 and e.pending_orders[0].order_type==O.OrderType.STOP_LIMIT
    record('entry_day_protection_delay',entry_fill=fill_summary(fills),entry_day_low=90.,
           protective_order_earliest_bar='2020-02-05',orders=order_summary(e))

    # 2. The protective-order branch consumes a bearish crossover, and prev
    # becomes zero. Keeping the bearish signal on the next callback cannot retry.
    e=engine();s=Strategy();s.fill_engine=e;s._prev_signal['SPY']=1
    context(s,0,100);assert e.pending_orders[0].order_type==O.OrderType.STOP_LIMIT
    context(s,0,100,'2020-02-04')
    assert len(e.order_history)==1 and all(o.order_type!=O.OrderType.MARKET for o in e.order_history)
    record('bearish_cross_consumed_while_arming',orders=order_summary(e),prev_signal=s._prev_signal['SPY'])

    # 3. A triggered sell stop-limit can remain pending through a further fall.
    e=engine();o=O.Order('SPY',O.OrderSide.SELL,100,O.OrderType.STOP_LIMIT,stop_price=96,limit_price=95.5)
    e.submit(o);f1=e.process_bar('SPY',bar(o=90,h=94,l=85,c=88))
    f2=e.process_bar('SPY',bar('2020-02-04',o=87,h=90,l=80,c=81))
    assert not f1 and not f2 and o._limit_activated and o.is_active
    record('gap_below_limit_no_fill',orders=order_summary(e),held_quantity=100,lowest_observed_price=80,
           fill_count=0,limit_is_not_a_maximum_loss=True)

    # 4. Once activated, a later recovery can fill the resting limit. Slippage
    # is clamped to the limit; commissions still reduce net sale proceeds.
    f=e.process_bar('SPY',bar('2020-02-05',o=94,h=96,l=93,c=95))
    assert len(f)==1 and f[0].fill_price==95.5 and f[0].commission==1
    record('later_recovery_limit_fill',fills=fill_summary(f),
           net_sale_per_share=f[0].fill_price-f[0].commission/f[0].quantity)

    # 5. A synchronous rejection is ignored by the strategy's boolean flag.
    e=engine(pre_submit_check=lambda order:'synthetic protective rejection')
    s=Strategy();s.fill_engine=e;s._prev_signal['SPY']=1
    context(s,1,100);context(s,1,100,'2020-02-04')
    assert len(e.order_history)==1 and e.order_history[0].status==O.OrderStatus.REJECTED
    assert not e.pending_orders and s._has_stop_limit['SPY']
    record('rejected_protection_flag_not_reconciled',orders=order_summary(e),has_stop_flag=True,retry_count=0)

    # 6. Ordinary bearish exit cancels active protection before a market sell.
    e=engine();s=Strategy();s.fill_engine=e;s._prev_signal['SPY']=1
    context(s,1,100);context(s,0,100,'2020-02-04')
    assert e.order_history[0].status==O.OrderStatus.CANCELLED
    assert len(e.pending_orders)==1 and e.pending_orders[0].order_type==O.OrderType.MARKET
    record('ordinary_bearish_exit_cancels_protection',orders=order_summary(e))

    # 7. Partial protection: cancel remaining stop and market-sell actual held
    # remainder. The upstream cumulative per-order commission charges minimum
    # once on this partial order, rather than once per partial fill.
    e=engine(max_volume_participation=.01);e.process_bar('SPY',bar())
    s=Strategy();s.fill_engine=e;s._prev_signal['SPY']=1
    context(s,1,100)
    f=e.process_bar('SPY',bar('2020-02-04',o=95,h=97,l=94,c=96))
    assert len(f)==1 and f[0].quantity==10 and e.pending_orders[0].remaining_qty==90
    context(s,0,90,'2020-02-04')
    assert len(e.pending_orders)==1 and e.pending_orders[0].quantity==90
    assert e.pending_orders[0].order_type==O.OrderType.MARKET
    record('partial_exit_cancels_remainder_and_uses_actual_position',fills=fill_summary(f),orders=order_summary(e))

    # 8. A stopped-out long waits for a fresh crossover; continuing above the
    # SMA does not re-enter. This is the source rule, not an alpha improvement.
    e=engine();s=Strategy();s.fill_engine=e;s._prev_signal['SPY']=1;s._has_stop_limit['SPY']=True
    context(s,1,0);assert not e.order_history and not s._has_stop_limit['SPY']
    context(s,0,0,'2020-02-04');context(s,1,0,'2020-02-05')
    assert len(e.order_history)==1 and e.pending_orders[0].side==O.OrderSide.BUY
    record('flat_above_sma_waits_for_new_cross',orders=order_summary(e))

    OUT.mkdir(parents=True,exist_ok=True)
    result=dict(scope='synthetic execution mechanics only',scenario_count=len(events),scenarios=events,
        historical_backtest_run=False,economic_definitions=0,scout_budget_changed=False,
        no_credentials_helper_or_main_executed=True,engine_version_parity_with_published_run=False,
        independent_verification='pending',source_hashes=json.loads((INPUT/'frozen_hashes.json').read_text()))
    (OUT/'synthetic_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ('scenarios','source_hashes')},indent=2))

if __name__=='__main__':main()
