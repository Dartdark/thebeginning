"""Same-case engineering reproduction of the frozen original FC2B50K policy.

Choose only the earliest saved2018design case with accepted fills for the
original0.50trail-risk FC2B policy. Reproduce raw/fast parity and independently
reconcile source fees/slippage, cash, DLL fills, first crossings and EOD floor.
No signal variant, new definition, corrected tape or2023outcome is generated.
"""
from dataclasses import replace
from pathlib import Path
import json
import sys
from zoneinfo import ZoneInfo
from datetime import datetime

import numpy as np

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'analysis'))
import codex_eval_run_20261104 as run
import codex_eval_engine_20261104 as engine

HERE=Path(__file__).resolve().parent
PREREG='a087708b13697df4c3dd0b0814f98cb53a2b254a'
POLICY_ID='E50_2436d1f22f21ef54'
CSV=run.DEFAULT_RUNTIME/'design_initial/main/fresh'/f'{POLICY_ID}.csv'


def close(a,b):return bool(np.isclose(float(a),float(b),rtol=1e-11,atol=1e-7,equal_nan=True))


def main():
    for name in run.IMPLEMENTATION+['agents/codex/inputs/eval_audit_20261104/config.json']:
        run.verify_file_at_commit(ROOT/name,PREREG)
    cases=run.read_cases(CSV)
    original=next(r for r in sorted(cases,key=lambda r:r['start_id'])
        if r['start_year']==2018 and float(r['fill_count'] or 0)>0)
    assert original['cost_scenario']=='main' and original['initial_state']=='fresh'
    registry=run.read_json(run.BASE/'policies.json')
    policy=next(p for p in registry['candidates'] if p['candidate_id']==POLICY_ID)
    assert policy['book']=={'FC2B':{'kind':'risk','value':1000.}}
    assert policy['governor']==dict(risk_fraction=0.,aggregate_stop_fraction=1.,cushion_buffer=0.,target_guard=False)
    tape,prepared=run.load_tape(run.DEFAULT_RUNTIME/'tape',run.DEFAULT_CONFIG,PREREG)
    w=next(w for w in run.make_windows(tape,'design') if w.start_id==original['start_id'])
    assert w.year==2018 and datetime.fromtimestamp(w.expiry,ZoneInfo('America/Chicago')).year==2018
    source=tape.events[(tape.events[:,0]>=w.a)&(tape.events[:,0]<w.b)]
    original_events=tape.events;tape.events=source
    try:events=run.requested_events(tape,policy)
    finally:tape.events=original_events
    events[:,0]-=w.a
    pv=np.asarray(tape.metadata['point_values'],float);ticks=np.asarray(tape.metadata['ticks'],float)
    fee=np.full(len(pv),.62);cutoff=np.zeros(len(tape.dates),np.int64)
    at=np.flatnonzero(tape.cutoff);cutoff[tape.session[at]]=tape.times[at].astype(np.int64)
    raw,logs=engine.simulate(tape.prices[w.a:w.b],tape.times[w.a:w.b],tape.session[w.a:w.b],
        events,pv,fee,ticks,cutoff,w.expiry,rules=replace(engine.EOD50,target_guard=False),record_logs=True)
    mapped={'expired':'expire','active_at_tape_end':'unknown'}.get(raw['status_name'],raw['status_name'])
    checks={'canonical_status':mapped==original['status'],'canonical_reason':raw['reason_name']==original['reason']}
    fields=['cash','equity','floor','max_net_micro_exposure','fill_count','rejected_entries','trimmed_entries',
        'dll_pauses','forced_cutoff_flats','commission','source_fill_slippage','liquidation_cost','open_virtual_positions']
    for k in fields:checks['raw_fast_'+k]=close(raw[k],original[k])
    checks['same_death_clock']=close(tape.times[w.a+int(raw['last_row'])],original['last_epoch'])
    checks['fast_bound_encloses_raw_minimum']=float(original['minimum_equity_lower_bound'])<=raw['minimum_equity']+1e-7
    checks['fast_visited_minimum_not_below_raw']=float(original['minimum_equity'])>=raw['minimum_equity']-1e-7
    by_event={(int(e[0]),int(e[1]),int(e[4])):e for e in events}
    cash=50000.;peak=50000.;floor=48000.;session_start=50000.;current=None
    positions={};source_fee=0.;source_slip=0.;liquidation=0.;ledger=[];previous_row=None
    def mark(price):
        return cash+sum((price[p['asset']]-p['entry'])*p['side']*p['quantity']*pv[p['asset']]
            for p in positions.values())
    for n,log in enumerate(logs):
        row,tid,action=int(log[0]),int(log[1]),int(log[2]);global_row=w.a+row
        price=tape.prices[global_row];ses=int(tape.session[global_row]);before=cash
        if current!=ses:
            if current is not None:
                checks[f'flat_previous_session_{n}']=not positions
                peak=max(peak,cash);floor=max(floor,min(peak-2000.,53000.))
            session_start=cash;current=ses
        if action in (-1,1):
            e=by_event[(row,tid,action)];asset=int(e[3]);qty=log[3]
            checks[f'integer_quantity_{n}']=qty==int(qty) and qty>0
            checks[f'native_fee_{n}']=close(log[5],qty*.62)
            expected=e[6]+e[5]*(1 if action==1 else -1)*(0 if e[9]==1 else ticks[asset])
            checks[f'source_fill_{n}']=close(log[4],expected)
            source_fee+=qty*.62;source_slip+=qty*abs(log[4]-e[6])*pv[asset]
            if action==1:
                checks[f'known_stop_{n}']=np.isfinite(e[7]) and e[7]>0
                checks[f'native_risk_request_{n}']=e[8]==np.floor(1000./(e[7]*pv[asset]))
                checks[f'admitted_request_{n}']=qty==e[8]
                cash-=qty*.62
                positions[tid]=dict(asset=asset,entry=float(log[4]),side=int(e[5]),quantity=int(qty))
            else:
                p=positions.pop(tid)
                checks[f'own_exit_quantity_{n}']=qty==p['quantity']
                cash+=(log[4]-p['entry'])*p['side']*qty*pv[asset]-qty*.62
        elif action==-2:
            # Frozen core's DLL log reports market liquidation. Recompute its
            # equity and cost from common prices and our own source-fill book.
            equity=mark(price);net=np.zeros(len(pv))
            for p in positions.values():net[p['asset']]+=p['side']*p['quantity']
            cost=float(np.sum(abs(net)*(fee+ticks*pv)))
            checks[f'dll_threshold_{n}']=equity<=session_start-1000.+1e-7
            checks[f'dll_not_floor_{n}']=equity>floor
            checks[f'dll_market_cost_{n}']=close(cost,log[5])
            if previous_row is not None and row>previous_row+1:
                prices=tape.prices[w.a+previous_row+1:global_row]
                eq=np.full(len(prices),cash)
                for p in positions.values():eq+=(prices[:,p['asset']]-p['entry'])*p['side']*p['quantity']*pv[p['asset']]
                checks[f'dll_first_crossing_{n}']=bool(np.isfinite(eq).all() and np.all(eq>session_start-1000.))
            cash=equity-cost;liquidation+=cost;positions.clear()
        else:raise ValueError('Unexpected event log classification')
        checks[f'account_equity_{n}']=close(mark(price),log[6])
        epoch=float(tape.times[global_row])
        ledger.append(dict(row=row,trade_id=tid,action=action,quantity=float(log[3]),fill=None if not np.isfinite(log[4]) else float(log[4]),
            clock_ct=datetime.fromtimestamp(epoch,ZoneInfo('America/Chicago')).isoformat(),cash_before=before,
            cash_after=cash,equity_after=mark(price),source_or_liquidation_fee=float(log[5])))
        previous_row=row
    checks['no_unlogged_cutoff_flat']=raw['forced_cutoff_flats']==0
    checks['final_book_flat']=not positions and raw['open_virtual_positions']==0
    checks['final_cash_reconciles']=close(cash,raw['cash'])
    peak=max(peak,cash);floor=max(floor,min(peak-2000.,53000.))
    checks['EOD_floor_reconciles']=close(floor,raw['floor'])
    checks['source_commission_reconciles']=close(source_fee,raw['commission'])
    checks['source_slippage_reconciles']=close(source_slip,raw['source_fill_slippage'])
    checks['DLL_liquidations_reconcile']=close(liquidation,raw['liquidation_cost'])
    checks['DLL_log_count']=sum(r['action']==-2 for r in ledger)==raw['dll_pauses']
    checks['no_accepted_fill_after_account_death']=bool(np.all(logs[:,0]<=raw['last_row']))
    checks['total_cost_reconciles']=close(source_fee+source_slip+liquidation,original['total_modeled_cost'])
    receipt=dict(scope='Same original FC2B50K risk0.50 policy; earliest saved2018design case with fills; same-rule raw reproduction, not another variant/definition or2023look.',
        preregistration_commit=PREREG,canonical_csv=str(CSV.relative_to(ROOT)),canonical_csv_sha256=run.sha(CSV),
        prepared_receipt=prepared,policy=policy,start_id=w.start_id,canonical_result=original,raw_result=raw,
        checks=checks,checks_pass=all(checks.values()),independent_cash_ledger=ledger,
        cost_reconciliation=dict(source_commission=source_fee,source_slippage=source_slip,DLL_liquidation_cost=liquidation,total=source_fee+source_slip+liquidation),
        limits=['Common OHLC path/source-fill insertion is conditional, not real tick/broker chronology or native MultiCharts trade matching.',
            'Reviewer wrote the core; independent ledger arithmetic and raw/fast comparison do not replace separate economic/source implementation review.',
            'Only one previously completed2018case reproduced; no2023account outcomes, new quantities, amended overlay, selection or strategy variants.'])
    run.atomic_json(HERE/'actual_fills_engineering_review.json',receipt)
    status='PASS' if receipt['checks_pass'] else 'FAIL'
    (HERE/'actual_fills_engineering_review.md').write_text(f'''# Actual-fill account engineering reproduction: {status}

Summary: Reproduced the same original FC2B50K risk0.50 policy on{w.start_id}, its earliest saved2018design case with fills.
{sum(checks.values())}/{len(checks)}checks passed against the saved fast outcome and an independent event cash ledger.
{int(raw['fill_count'])}source fills and{int(raw['dll_pauses'])}DLL market liquidations reconcile; costs total${source_fee+source_slip+liquidation:.2f}.
Outcome{mapped}:cash/equity${raw['cash']:.2f},EODfloor${raw['floor']:.2f}; no changed quantity, rule or2023account outcome.
This verifies conditional-tape engineering identities, not native MultiCharts matching or strategy profitability.

Exact policy`{POLICY_ID}`was already counted and completed under original preregistration`{PREREG}`.
The retrospective case choice is only earliest2018with fills, to exercise fees and liquidation; no return/side/date
optimization follows. It uses target_guard=False, nominal50Kstart, unchanged$1,000source-risk requests, integer
micros, RT$1.24fees and one adverse tick per market/stop fill. No corrected DT overlay is used.

Source commission${source_fee:.2f},source slippage${source_slip:.2f},DLL liquidation costs${liquidation:.2f}
reconcile with the saved total. Every accepted source fill is checked against its raw event/reference price,
side, native point value, source-known stop and integer request. The independent cash ledger reproduces
each logged account equity, final realized cash and the highest-EOD floor. DLL entries are checked against
the current session's realized/unrealized loss threshold, their first crossing on the same raw shared-price
tape and prevailing-market closing costs. Account-death timing matches the saved case; later source trades
do not accrue to that account. The raw minimum is compared with the fast visited minimum/conservative bound.

Reproduce with`actual_fills_engineering_check.py`; full checks, timestamps and ledger are in
`actual_fills_engineering_review.json`. Raw/fast parity and independent arithmetic on one fixed modeled path
are not independent market evidence. Real quote chronology, source/settings acceptance and native matching
remain conditional; the core's author performed this reproduction. Claude/economic verification stays pending.
''')
    print(json.dumps(dict(status=status,checks=len(checks),source_fills=int(raw['fill_count']),
        DLL_market_flats=int(raw['dll_pauses']),total_cost=source_fee+source_slip+liquidation,outcome=mapped)))
    if not receipt['checks_pass']:raise SystemExit(1)


if __name__=='__main__':main()
