"""Synthetic account-rule/path checks only. No historical prices or returns."""
from dataclasses import replace
from pathlib import Path
import ast,json,subprocess
import numpy as np
from codex_eval_engine_20261104 import simulate,EOD50,EOD150,EvalRules

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'agents/codex/inputs/eval_audit_20261104/engine_fixtures.json'

def event(row,tid=0,key=0,asset=0,action=1,side=1,raw=100.,stop=10.,qty=1,kind=0):
    return [row,tid,key,asset,action,side,raw,stop,qty,kind]

def go(prices,events=(),rules=None,fee=0.,slip=0.,sessions=None,times=None,cutoffs=None,**kw):
    prices=np.asarray(prices,dtype=float)
    if prices.ndim==1:prices=prices[:,None]
    n,a=prices.shape
    if sessions is None:sessions=np.zeros(n,dtype=int)
    if times is None:times=np.arange(n,dtype=np.int64)*60
    if cutoffs is None:cutoffs=np.zeros(max(sessions)+1,dtype=np.int64)
    return simulate(prices,times,sessions,np.asarray(events).reshape(-1,10),np.full(a,2.),
        np.full(a,fee),np.full(a,slip),cutoffs,10**12,
        rules=rules or replace(EOD50,target_guard=False),**kw)

def bounds(prices,nodes):
    prices=np.asarray(prices,dtype=float)
    if prices.ndim==1:prices=prices[:,None]
    mins=[];maxs=[];missing=[]
    for a,b in zip(nodes[:-1],nodes[1:]):
        seg=prices[a+1:b+1]
        mins.append(np.nanmin(seg,axis=0));maxs.append(np.nanmax(seg,axis=0));missing.append(~np.isfinite(seg).all(axis=0))
    return dict(node_rows=nodes,segment_min=np.array(mins),segment_max=np.array(maxs),segment_missing=np.array(missing))

def legacy_function(path,name,constants):
    src=subprocess.check_output(['git','show','13e29ca7b45daabeb0ed2d8c286448610f594dab:'+path],cwd=ROOT,text=True)
    node=next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name==name)
    namespace={'np':np,**constants};exec(compile(ast.Module(body=[node],type_ignores=[]),path,'exec'),namespace)
    return namespace[name]

def main():
    checks={}
    r,_=go([100.,101.,102.],[event(0),event(2,action=-1,raw=102.)],fee=.62,slip=.25)
    assert np.isclose(r['cash'],50001.76) and np.isclose(r['commission'],1.24)
    checks['native_fees_and_market_slippage']=r['cash']
    r,_=go([100.,1600.],[event(0),event(1,action=-1,raw=1600.)],fee=.62,slip=.25)
    assert r['status_name']=='active_at_tape_end' and np.isclose(r['cash'],52997.76)
    checks['gross_target_without_net_target_does_not_pass']=True
    r,_=go([100.,1602.],[event(0)],rules=replace(EOD50,target_buffer=0.),fee=.62,slip=.25)
    assert r['status_name']=='pass' and np.isclose(r['cash'],53001.76)
    checks['target_flatten_charges_real_costs']=r['cash']
    r,_=go([100.,1600.81],[event(0)],rules=replace(EOD50,target_buffer=0.),fee=.62,slip=.25)
    assert r['status_name']=='active_at_tape_end' and np.isclose(r['cash'],52999.38)
    checks['target_guard_cost_below_net_target_does_not_pass']=True
    r,_=go([3000.,2000.],[event(0,raw=3000.)])
    assert r['status_name']=='fail' and r['reason_name']=='intraday_floor'
    checks['inclusive_floor_touch_fails']=True
    r,_=go([3000.,2050.,3100.],[event(0,raw=3000.)])
    assert r['dll_pauses']==1 and r['cash']==48100. and r['status_name']=='active_at_tape_end'
    checks['dll_gap_fills_current_quote_not_threshold']=r['cash']
    r,_=go([3000.,2050.75],[event(0,raw=3000.)],fee=.62,slip=.25,initial_floor=48100.)
    assert r['status_name']=='fail' and r['reason_name']=='post_liquidation_floor'
    checks['dll_liquidation_can_cross_account_floor']=r['cash']
    rules=EvalRules(1000.,500.,100.,1000.,60,1500.,0.,False)
    ev=[event(0),event(1,action=-1,raw=250.),event(2,tid=1,raw=100.),event(3,tid=1,action=-1,raw=50.)]
    r,_=go([100.,250.,100.,50.],ev,rules=rules,sessions=[0,0,1,1])
    assert r['floor']==1200. and r['status_name']=='fail'
    checks['eval_floor_does_not_stop_at_start_plus_100']=r['floor']
    ev=[event(0,tid=0),event(0,tid=1,side=-1),event(3,tid=0,action=-1),event(3,tid=1,side=-1,action=-1)]
    r,_=go([100.,50.,150.,100.],ev)
    assert r['minimum_equity']==50000. and r['cash']==50000.
    checks['opposite_sleeves_mark_one_common_asset_price']=True
    ev=[event(0,tid=0),event(1,tid=1,side=-1,raw=110.)]
    r,_=go([100.,110.,np.nan],ev)
    assert r['status_name']=='active_at_tape_end' and r['equity']==50020.
    checks['offset_locked_basis_known_even_without_later_quote']=True
    ev=[event(0,tid=0),event(1,tid=1,side=-1,raw=1600.)]
    r,_=go([100.,1600.],ev)
    assert r['status_name']=='pass' and r['cash']==53000. and r['open_virtual_positions']==0
    checks['broker_net_flat_locked_profit_meets_target']=True
    ev=[event(0,tid=0),event(1,tid=1,side=-1,raw=1601.62)]
    r,_=go([100.,1601.62],ev,rules=EOD50,fee=.62,slip=.25)
    assert r['status_name']=='pass' and np.isclose(r['cash'],53001.) and r['liquidation_cost']==0
    checks['net_flat_target_includes_source_costs_not_guard_buffer']=True
    r,log=go([100.,101.],[event(0,qty=61),event(1,action=-1,raw=101.,qty=61)],record_logs=True)
    assert r['rejected_entries']==1 and r['fill_count']==0 and r['cash']==50000.
    checks['contract_excess_rejects_order_without_account_failure']=True
    r,log=go([100.,101.],[event(0,qty=20,stop=50.),event(1,action=-1,raw=101.)],
        fee=.62,slip=.25,risk_fraction=.25,aggregate_stop_fraction=.50,record_logs=True)
    assert r['trimmed_entries']==1 and log[0,3]==4
    checks['floor_governor_integer_quantity']=int(log[0,3])
    # Existing position consumes reserve; no later unknown-stop sleeve is invented.
    r,log=go([100.,101.],[event(0,tid=0,qty=20,stop=50.),event(0,tid=1,key=1,qty=20,stop=np.nan),
        event(1,tid=0,action=-1,raw=101.)],fee=.62,slip=.25,risk_fraction=.25,
        aggregate_stop_fraction=.50,record_logs=True)
    assert r['rejected_entries']==1 and len(log[log[:,3]==0])==1
    checks['unknown_stop_not_sized_from_future_outcome']=True
    # With a tight remaining DLL room, risk quantity is capped even with ample life cushion.
    rule=replace(EOD50,dll=100.,target_guard=False)
    r,log=go([100.,101.],[event(0,qty=20,stop=50.),event(1,action=-1,raw=101.)],rules=rule,
        risk_fraction=.5,aggregate_stop_fraction=.75,record_logs=True)
    assert log[0,3]==1
    checks['governor_also_reserves_daily_loss_room']=True
    r,_=go([100.,np.nan],[event(0)])
    assert r['status_name']=='unknown' and r['reason_name']=='missing_held_price'
    checks['missing_active_price_is_unknown']=True
    r,_=go([np.nan,np.nan])
    assert r['status_name']=='active_at_tape_end' and r['cash']==50000.
    checks['flat_missing_quote_is_not_imputed_return']=True
    r,_=go([np.nan,np.nan],[event(0,qty=0),event(1,action=-1,qty=0)])
    assert r['status_name']=='active_at_tape_end' and r['rejected_entries']==0
    checks['unallocated_key_does_not_require_missing_source_quote']=True
    r,_=go([100.,101.],[event(0,raw=np.nan),event(1,action=-1,raw=np.nan)])
    assert r['status_name']=='unknown' and r['reason_name']=='source_fill_does_not_match_event_price'
    checks['relevant_nan_raw_fill_is_account_unknown_not_wrapper_exception']=True
    r,_=go([np.nan,np.nan],[event(0,qty=0,raw=np.nan),event(1,action=-1,qty=0,raw=np.nan)])
    assert r['status_name']=='active_at_tape_end' and r['rejected_entries']==0
    checks['unallocated_nan_raw_fill_does_not_block_other_portfolios']=True
    r,_=go([100.,101.],[event(0,raw=101.)])
    assert r['status_name']=='unknown' and r['reason_name']=='source_fill_does_not_match_event_price'
    checks['market_fill_must_match_event_reference']=True
    r,_=go([100.,101.,102.],[event(0),event(2,action=-1,raw=102.)],cutoffs=np.array([60]))
    assert r['forced_cutoff_flats']==1 and r['cash']==50002. and r['open_virtual_positions']==0
    checks['known_daily_cutoff_flattens_and_blocks_later_source_exit']=True
    r,_=go([100.,1600.81],[event(0)],fee=.62,slip=.25,cutoffs=np.array([60]))
    assert r['status_name']=='active_at_tape_end' and np.isclose(r['cash'],52999.38)
    checks['cutoff_cost_below_net_target_does_not_pass']=True
    r,_=go([100.,1601.],[event(0)],rules=EOD50,cutoffs=np.array([60]))
    assert r['status_name']=='pass' and r['forced_cutoff_flats']==1
    checks['cutoff_realized_target_counts_below_guard_buffer']=True
    r,_=go([100.,101.],[event(0,qty=0)])
    assert r['rejected_entries']==0 and r['fill_count']==0
    checks['zero_allocation_is_not_broker_rejection']=True
    r,_=go([100.,101.],[event(0)],times=np.array([0,120]),cutoffs=np.array([60]))
    assert r['status_name']=='unknown' and r['reason_name']=='late_flat_deadline'
    checks['missing_cutoff_quote_not_backfilled']=True
    try:go([100.,101.],[event(0,qty=1.5)]);raise AssertionError('Fractional quantity accepted')
    except ValueError:checks['fractional_quantity_rejected']=True
    # Source exits occur before discretionary entries at a shared event, no false cap rejection.
    rules=replace(EOD50,max_micro_contracts=1,target_guard=False)
    ev=[event(0,tid=0),event(1,tid=1,raw=101.),event(1,tid=0,action=-1,raw=101.)]
    r,log=go([100.,101.],ev,rules=rules,record_logs=True)
    assert log[1,2]==-1 and log[2,2]==1 and r['rejected_entries']==0
    checks['same_time_source_exit_before_entry']=True
    ev=[event(0,action=-1),event(0)]
    r,log=go([100.,101.],ev,fee=.62,slip=.25,record_logs=True)
    assert r['open_virtual_positions']==0 and r['fill_count']==2 and np.isclose(r['cash'],49997.76)
    assert log[0,2]==1 and log[1,2]==-1
    checks['same_phase_own_roundtrip_closes_after_own_entry']=True
    #100independently generated synthetic tapes verify acceleration against raw walking.
    rng=np.random.default_rng(1144)
    for _ in range(100):
        p=np.r_[100.,100.+np.cumsum(rng.normal(0,2.,49))]
        ev=[event(0,qty=5),event(49,action=-1,raw=p[-1])]
        nodes=np.array([0,49]);options=bounds(p,nodes)
        rules=EvalRules(50000.,80.,100.,50.,60,50080.,0.,True)
        a,la=go(p,ev,rules=rules,record_logs=True);b,lb=go(p,ev,rules=rules,record_logs=True,**options)
        for k in ['status','reason','last_row','cash','equity','floor','max_net_micro_exposure','fill_count','dll_pauses']:
            assert np.isclose(a[k],b[k],equal_nan=True),(k,a,b)
        np.testing.assert_allclose(la,lb,equal_nan=True)
    checks['segment_skip_matches_raw_100_synthetic_tapes']=True
    p=np.array([100.,100.1,100.2,100.3]);ev=[event(0),event(3,action=-1,raw=p[-1])]
    a,_=go(p,ev,**bounds(p,np.array([0,3])))
    assert a['skipped_raw_rows']==2
    checks['safe_segment_actually_skips_raw_rows']=True
    withlogs,ll=go([100.,101.],[event(0),event(1,action=-1,raw=101.)],record_logs=True)
    nologs,nl=go([100.,101.],[event(0),event(1,action=-1,raw=101.)],record_logs=False)
    assert withlogs['cash']==nologs['cash'] and len(nl)==0 and len(ll)==2
    checks['disabled_logs_same_outcome_and_zero_log_rows']=True
    # Reproduce two inherited-engine defects by compiling only the reviewed function.
    base=dict(START=50000.,TARGET=3000.,MLL=2000.,DLL=1000.,LOCK=100.,MAXD=21)
    challenge=legacy_function('analysis/combine_levers_test.py','challenge',base)
    evaluation=legacy_function('analysis/plan_150k_test.py','evaluation',{})
    W=np.zeros((21,2));R=W.copy();W[0,1]=-1000.;R[0,1]=3000.
    old=challenge(W,R,np.arange(21),lambda p,c,n:1.)
    conservative=evaluation(W,R,0,21,dict(st=50000.,dd=2000.,dll=1000.,lock=50100.,tgt=3000.))
    assert old==('pass',1) and conservative==('time',21)
    checks['inherited_50K_150K_tie_difference']={'50K_function':old,'150K_function_with50Kparameters':conservative}
    W=np.zeros((21,2));R=W.copy();W[0,1]=R[0,1]=2500.;W[1:3,1]=R[1:3,1]=-1000.;W[3,1]=R[3,1]=2500.
    old=challenge(W,R,np.arange(21),lambda p,c,n:1.)
    corrected=legacy_function('analysis/combine_levers_test.py','challenge',{**base,'LOCK':3000.})(W,R,np.arange(21),lambda p,c,n:1.)
    assert old==('pass',4) and corrected==('fail',3)
    checks['inherited_PA_lock_can_change_eval_outcome']={'PA_lock':old,'eval_lock':corrected}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({'scope':'Synthetic account checks only; no historical strategy returns.',
        'checks':checks,'count':len(checks)},indent=2)+'\n')
    print(f'{len(checks)}synthetic account/path checks PASS;100fast/raw fixtures;zero historical returns.')

if __name__=='__main__':main()
