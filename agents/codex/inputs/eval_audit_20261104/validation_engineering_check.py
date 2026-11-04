"""Three SAME frozen validation cases, raw/fast and cash engineering only.

Final nomination588e6b precedes all canonical outcomes. Choose earliest saved
PASS for each50K guard nominee plus earliest FC2B FAIL with a DLL. No policy,
quantity, source path, selection or unobserved portfolio outcome is changed.
"""
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo
import json
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'analysis'))
import codex_eval_run_20261104 as run
import codex_eval_amended_run_20261104 as amended
import codex_eval_engine_20261104 as engine

HERE=Path(__file__).resolve().parent
FINAL='588e6b692e83154d056a3ecefca8eb1411f78d19'
AMENDMENT='e8e249b4e7c8946d517e8e4c9a4a3b4e62063e24'
ORIGINAL=amended.ORIGINAL_COMMIT
IDS=['E50_a7956dcbc05dc7c9','E50_2d2e3f2a54976449']


def close(a,b):return bool(np.isclose(float(a),float(b),rtol=1e-11,atol=1e-7,equal_nan=True))


def check_case(tape,policy,saved,role,windows,prepared):
    assert policy['account'] in (50,150) and policy['governor']==dict(risk_fraction=0.,aggregate_stop_fraction=1.,cushion_buffer=0.,target_guard=True)
    rules=engine.EOD50 if policy['account']==50 else engine.EOD150
    nominal=rules.nominal_start;target=nominal+rules.target_profit
    assert len(policy['book'])==1 and next(iter(policy['book'].values()))=={'kind':'lots','value':20}
    w=next(w for w in windows if w.start_id==saved['start_id'])
    original=tape.events;tape.events=original[(original[:,0]>=w.a)&(original[:,0]<w.b)]
    try:events=run.requested_events(tape,policy)
    finally:tape.events=original
    events[:,0]-=w.a
    pv=np.asarray(tape.metadata['point_values'],float);tick=np.asarray(tape.metadata['ticks'],float)
    fee=np.full(len(pv),.62);cutoff=np.zeros(len(tape.dates),np.int64)
    rows=np.flatnonzero(tape.cutoff);cutoff[tape.session[rows]]=tape.times[rows].astype(np.int64)
    raw,logs=engine.simulate(tape.prices[w.a:w.b],tape.times[w.a:w.b],tape.session[w.a:w.b],events,
        pv,fee,tick,cutoff,w.expiry,rules=replace(rules,target_guard=True),record_logs=True)
    status={'expired':'expire','active_at_tape_end':'unknown'}.get(raw['status_name'],raw['status_name'])
    checks={'saved_status':status==saved['status'],'saved_reason':raw['reason_name']==saved['reason']}
    fields=['cash','equity','floor','max_net_micro_exposure','fill_count','rejected_entries','trimmed_entries',
        'dll_pauses','forced_cutoff_flats','commission','source_fill_slippage','liquidation_cost','open_virtual_positions']
    for key in fields:checks['raw_fast_'+key]=close(raw[key],saved[key])
    death=w.a+int(raw['last_row']);price=tape.prices[death]
    checks['saved_terminal_clock']=close(tape.times[death],saved['last_epoch'])
    checks['raw_minimum_enclosed_by_fast']=float(saved['minimum_equity_lower_bound'])<=raw['minimum_equity']+1e-7<=float(saved['minimum_equity'])+2e-7
    checks[f'native_cap_{rules.max_micro_contracts}']=raw['max_net_micro_exposure']<=rules.max_micro_contracts
    checks['configured_initial_floor']=close(float(saved['initial_floor']),nominal-rules.trail)
    checks['actual20_micro_exposure']=raw['max_net_micro_exposure']==20
    checks['all_entry_requests20']=bool(np.all(events[events[:,4]==1,8]==20))
    source_map={(int(e[0]),int(e[1]),int(e[4])):e for e in events}
    cash=nominal;peak=nominal;floor=nominal-rules.trail;session_start=nominal;session=None;positions={}
    fees=0.;slip=0.;liquidation=0.;ledger=[];previous_row=None
    def mark(prices):
        return cash+sum((prices[p['asset']]-p['entry'])*p['side']*p['qty']*pv[p['asset']] for p in positions.values())
    def net_cost():
        net=np.zeros(len(pv))
        for p in positions.values():net[p['asset']]+=p['side']*p['qty']
        return float(np.sum(abs(net)*(fee+tick*pv)))
    def prior_equity(row):
        prices=tape.prices[w.a+previous_row+1:w.a+row]
        eq=np.full(len(prices),cash)
        for p in positions.values():eq+=(prices[:,p['asset']]-p['entry'])*p['side']*p['qty']*pv[p['asset']]
        return eq
    for n,log in enumerate(logs):
        row,tid,action=int(log[0]),int(log[1]),int(log[2]);g=w.a+row;pnow=tape.prices[g];ses=int(tape.session[g])
        if session!=ses:
            if session is not None:
                checks[f'previous_session_flat_{n}']=not positions
                peak=max(peak,cash);floor=max(floor,min(peak-rules.trail,rules.floor_cap))
            session_start=cash;session=ses
        if action in (1,-1):
            e=source_map[(row,tid,action)];a=int(e[3]);q=log[3]
            checks[f'actual_native20_{n}']=q==20 and q==int(q)
            checks[f'native_fee_{n}']=close(log[5],q*.62)
            expected=e[6]+e[5]*(1 if action==1 else -1)*(0 if e[9]==1 else tick[a])
            checks[f'native_fill_{n}']=close(log[4],expected)
            checks[f'raw_tick_grid_{n}']=close(e[6]/tick[a],round(e[6]/tick[a]))
            checks[f'one_common_asset_price_{n}']=close(pnow[a],e[6])
            fees+=q*.62;slip+=q*abs(log[4]-e[6])*pv[a]
            if action==1:
                cash-=q*.62;positions[tid]=dict(asset=a,entry=float(log[4]),side=int(e[5]),qty=int(q))
            else:
                p=positions.pop(tid);cash+=(log[4]-p['entry'])*p['side']*q*pv[a]-q*.62
        elif action==-2:
            eq=mark(pnow);cost=net_cost()
            checks[f'DLL_inclusive_cross_{n}']=eq<=session_start-rules.dll+1e-7
            checks[f'DLL_precedes_floor_{n}']=eq>floor
            checks[f'DLL_market_cost_{n}']=close(cost,log[5])
            if previous_row is not None:
                prev=prior_equity(row)
                checks[f'DLL_first_raw_cross_{n}']=bool(np.isfinite(prev).all() and np.all(prev>session_start-rules.dll))
            cash=eq-cost;liquidation+=cost;positions.clear()
            checks[f'DLL_not_snapped_threshold_{n}']=not close(cash,session_start-rules.dll)
        else:raise ValueError('Unexpected account log action')
        checks[f'independent_equity_{n}']=close(mark(pnow),log[6])
        ledger.append(dict(row=row,clock_ct=datetime.fromtimestamp(float(tape.times[g]),ZoneInfo('America/Chicago')).isoformat(),
            action=action,trade_id=tid,quantity=float(log[3]),modeled_fill=float(log[4]) if np.isfinite(log[4]) else None,
            cash=cash,equity=mark(pnow),fee_or_liquidation_cost=float(log[5])))
        previous_row=row
    # Guard/floor forced close is not a source ticket. Independently realize
    # the remaining broker NET position at the terminal common mark and costs.
    assert positions and raw['forced_cutoff_flats']==0
    preclose=mark(price);closing=net_cost();prior=prior_equity(int(raw['last_row']))
    checks['independent_EOD_floor']=close(floor,raw['floor'])
    if raw['status_name']=='pass':
        checks['guard_actual_equity_trigger']=preclose>=target+rules.target_buffer
        checks['guard_first_raw_cross']=bool(np.isfinite(prior).all() and np.all(prior<target+rules.target_buffer))
    else:
        checks['inclusive_floor_trigger']=preclose<=raw['floor']
        checks['floor_first_raw_cross']=bool(np.isfinite(prior).all() and np.all(prior>raw['floor']))
    cash=preclose-closing;liquidation+=closing;positions.clear()
    checks['terminal_market_cost_native20']=close(closing,20*(.62+.25*2))
    checks['terminal_net_cash']=close(cash,raw['cash']) and close(cash,raw['equity'])
    checks['source_fee_sum']=close(fees,raw['commission'])
    checks['source_slippage_sum']=close(slip,raw['source_fill_slippage'])
    checks['market_liquidation_sum']=close(liquidation,raw['liquidation_cost'])
    checks['flat_at_death']=raw['open_virtual_positions']==0
    checks['no_after_terminal_fills']=bool(np.all(logs[:,0]<=raw['last_row']))
    checks['post_terminal_source_events_suppressed']=int((events[:,0]>raw['last_row']).sum())>0
    checks['total_native_cost']=close(fees+slip+liquidation,saved['total_modeled_cost'])
    if raw['status_name']=='pass':checks['net_target_after_costs']=cash>=target
    else:checks['failed_floor_after_costs']=cash<=raw['floor']
    return dict(role=role,candidate_id=policy['candidate_id'],policy=policy,start_id=w.start_id,
        canonical=saved,raw=raw,checks=checks,checks_pass=all(checks.values()),independent_ledger=ledger,
        terminal=dict(preclose_equity=preclose,native_market_close_cost=closing,net_cash=cash,
            source_orders_after_terminal_suppressed=int((events[:,0]>raw['last_row']).sum())),
        cost=dict(source_fees=fees,source_slippage=slip,all_liquidation_cost=liquidation,total=fees+slip+liquidation),
        configured_rules=dict(nominal=nominal,target_balance=target,initial_floor=nominal-rules.trail,
            EOD_trail=rules.trail,DLL=rules.dll,max_net_micros=rules.max_micro_contracts,
            target_guard_buffer=rules.target_buffer))


def main():
    for name in run.IMPLEMENTATION+['agents/codex/inputs/eval_audit_20261104/config.json']:
        run.verify_file_at_commit(ROOT/name,ORIGINAL)
    for name in amended.AMENDMENT_FILES:run.verify_file_at_commit(ROOT/name,AMENDMENT)
    run.verify_file_at_commit(amended.FINAL,FINAL)
    frozen=run.read_json(amended.FINAL);nominees={p['candidate_id']:p for p in frozen['nominees']}
    args=SimpleNamespace(runtime=run.DEFAULT_RUNTIME,config=run.DEFAULT_CONFIG,commit=AMENDMENT)
    tape,prepared=amended.load_overlay(args);windows=run.make_windows(tape,'validation')
    results=[];inputs={}
    for cid in IDS:
        file=run.DEFAULT_RUNTIME/'validation_amended/main/fresh'/f'{cid}.csv'
        checks=run.read_json(file.with_suffix('.json'));assert run.sha(file)==checks['csv_sha256']
        rows=sorted(run.read_cases(file),key=lambda r:r['start_id'])
        cases=[('earliest_saved_pass',next(r for r in rows if r['status']=='pass'))]
        if cid==IDS[1]:cases.append(('earliest_saved_fail_with_DLL',next(r for r in rows if r['status']=='fail' and float(r['dll_pauses'])>0)))
        inputs[str(file.relative_to(ROOT))]=run.sha(file)
        for role,row in cases:results.append(check_case(tape,nominees[cid],row,role,windows,prepared))
    passed=all(r['checks_pass'] for r in results);n=sum(len(r['checks']) for r in results)
    receipt=dict(status='PASS' if passed else 'FAIL',scope='Three previously saved frozen-final validation cases; same-definition raw engineering rewalk only, not selection or additional strategy trials.',
        original_preregistration=ORIGINAL,amendment_preregistration=AMENDMENT,final_nomination_commit=FINAL,
        committed_nomination_sha256=run.sha(amended.FINAL),prepared_overlay_receipt=prepared,
        canonical_csv_sha256=inputs,cases=results,engineering_checks=n,
        limits=['Market target guard is a frozen prospective account-market-flatten counterfactual, not verified installed MultiCharts guard behavior or latency.',
            'Common OHLC phase/source-fill chronology remains conditional. These standalone one-asset cases do not independently test opposing-sleeve collisions; synthetic core tests cover that engineering identity.',
            'Reviewer authored core; independent cash/cost arithmetic and raw/fast parity do not replace independent source/economic implementation or native matching.',
            'Selection was already frozen; case choices conditioned on saved PASS/DLL/failure solely exercise engineering and are not representative pass-rate evidence.',
            'Baseline risk-sized accounts remain mostly UNKNOWN; their identification bounds cannot establish nominee superiority.'])
    run.atomic_json(HERE/'validation_engineering_review.json',receipt)
    lines=[f"# Frozen validation engineering review: {receipt['status']}",'',
        'Summary: Reproduced three already saved final-nominee account cases with the exact committed overlay/rules.',
        f'{n}checks cover native20MNQ, source costs, first DLL/target/floor crossings, account death and raw/fast parity.',
        'Two market-guard passes retain at least$3,000net after closing costs; one failed case retains its modeled DLL gap/floor loss.',
        'No new strategy definition, quantity, source repair, nomination or validation-wide rerun was made.',
        'Conditional OHLC fills and market-guard latency remain unverified; baseline UNKNOWN cannot establish superiority.','',
        f'Final nomination`{FINAL}`was committed before canonical2023+outcomes. Main costs are$1.24RT/native micro plus one adverse tick per market/stop side. All three use frozen20MNQallocation requests, broker cap60micros, guard=True.','',
        '|Policy / start|Saved result|Preclose equity|Native closing cost|Net terminal equity|',
        '|---|---|---:|---:|---:|']
    for r in results:lines.append(f"|{next(iter(r['policy']['book']))} / {r['start_id']}|{r['canonical']['status']}|${r['terminal']['preclose_equity']:,.2f}|${r['terminal']['native_market_close_cost']:,.2f}|${r['terminal']['net_cash']:,.2f}|")
    lines+=['','Each source order uses the same asset price across the book. Native integer requests, commissions, adverse tick fills and real market liquidation costs reconcile with a separately maintained cash ledger. First-crossing checks rewalk the identical common-price tape. Source orders after terminal PASS/FAIL remain suppressed; no post-death profit is added. The failed case is not snapped to its daily loss threshold. Fast visited minima/conservative bounds enclose each raw modeled minimum.','',
        'This is engineering reproduction of selected saved cases, not independent market evidence. The shared OHLC ordering, source-fill phases and modeled fractional timestamps are not actual tick chronology. These single-sleeve cases do not demonstrate live opposite-sleeve netting. The reviewer wrote the core, and native MultiCharts trade matching, actual guard installation, fills/latency and independent economic verification remain pending. Baseline UNKNOWN identification bounds prevent a demonstrated superiority claim.','',
        'Full checks/ledger/hash receipts:`validation_engineering_review.json`; bounded reproduction:`validation_engineering_check.py`.']
    (HERE/'validation_engineering_review.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(status=receipt['status'],cases=len(results),checks=n,failed_checks={r['candidate_id']+'/'+r['start_id']:[k for k,v in r['checks'].items() if not v] for r in results})))
    if not passed:raise SystemExit(1)


def append_150k():
    """Add one saved150Kcase without re-executing the three50Kchecks."""
    file=HERE/'validation_engineering_review.json';review=run.read_json(file)
    cid='E150_d789eb79de196ae7'
    if any(r['candidate_id']==cid for r in review['cases']):
        raise ValueError('150K engineering case already retained; no duplicate rewalk')
    for name in run.IMPLEMENTATION+['agents/codex/inputs/eval_audit_20261104/config.json']:
        run.verify_file_at_commit(ROOT/name,ORIGINAL)
    for name in amended.AMENDMENT_FILES:run.verify_file_at_commit(ROOT/name,AMENDMENT)
    run.verify_file_at_commit(amended.FINAL,FINAL)
    policy=next(p for p in run.read_json(amended.FINAL)['nominees'] if p['candidate_id']==cid)
    csv=run.DEFAULT_RUNTIME/'validation_amended/main/fresh'/f'{cid}.csv'
    assert run.sha(csv)==run.read_json(csv.with_suffix('.json'))['csv_sha256']
    saved=next(r for r in sorted(run.read_cases(csv),key=lambda r:r['start_id']) if r['status']=='pass')
    args=SimpleNamespace(runtime=run.DEFAULT_RUNTIME,config=run.DEFAULT_CONFIG,commit=AMENDMENT)
    tape,prepared=amended.load_overlay(args)
    result=check_case(tape,policy,saved,'earliest_saved150K_pass',run.make_windows(tape,'validation'),prepared)
    expected=dict(nominal=150000.,target_balance=159000.,initial_floor=146000.,EOD_trail=4000.,DLL=2000.,max_net_micros=120,target_guard_buffer=50.)
    result['checks']['explicit150Krules']=result['configured_rules']==expected
    result['checks_pass']=all(result['checks'].values());previous_checks=review['engineering_checks']
    review['cases'].append(result);review['engineering_checks']+=len(result['checks'])
    review['scope']='Four previously saved frozen-final validation cases; same-definition raw engineering rewalk only, not selection or additional strategy trials.'
    review['canonical_csv_sha256'][str(csv.relative_to(ROOT))]=run.sha(csv)
    review['status']='PASS' if all(r['checks_pass'] for r in review['cases']) else 'FAIL'
    run.atomic_json(file,review)
    report=HERE/'validation_engineering_review.md';text=report.read_text().replace('Reproduced three already saved','Reproduced four already saved')
    text=text.replace(f'{previous_checks}checks cover native20MNQ',f"{review['engineering_checks']}checks cover native20MNQ")
    text=text.replace('Two market-guard passes','Three market-guard passes').replace('All three use frozen20MNQallocation requests, broker cap60micros','The three50Kcases use frozen20MNQallocation requests, broker cap60micros')
    text+=f"""
150K extension (one additional same-rule raw rewalk; earlier three cases were not repeated):
FC2Bguard20MNQ, earliest saved PASS starting{saved['start_id']}, preclose${result['terminal']['preclose_equity']:,.2f}
less${result['terminal']['native_market_close_cost']:,.2f}native liquidation cost =${result['terminal']['net_cash']:,.2f}.
Its initial floor is$146,000; actual highest-EOD floor at termination is${result['raw']['floor']:,.2f},
independently reconciled. Explicit150Kconfiguration: target$159,000, trail$4,000,DLL$2,000,max120micros;
the admitted position is20MNQ. Source commission${result['cost']['source_fees']:.2f},source slippage${result['cost']['source_slippage']:.2f},
market closing cost${result['cost']['all_liquidation_cost']:.2f}reconcile to${result['cost']['total']:.2f}.
This PASS case has zero DLL triggers;150KDLL$2,000is a verified frozen configuration rather than an
exercised150Kliquidation claim. Prior50Kcases exercise market DLL gaps and failure chronology.
All{len(result['checks'])}additional checks pass. Append reproduction flag:`--append-150k`;
run the default three-case script first when reproducing from an empty review directory.
"""
    report.write_text(text)
    print(json.dumps(dict(status=review['status'],additional_checks=len(result['checks']),total_checks=review['engineering_checks'],
        start=saved['start_id'],net_cash=result['raw']['cash'],floor=result['raw']['floor'])))
    if not result['checks_pass']:raise SystemExit(1)


if __name__=='__main__':
    if sys.argv[1:]==['--append-150k']:append_150k()
    elif not sys.argv[1:]:main()
    else:raise SystemExit('Only optional --append-150k is supported')
