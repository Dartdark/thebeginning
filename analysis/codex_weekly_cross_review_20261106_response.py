"""Post-read deciding checks: source scope, risk-budget arithmetic and proposed fee patch.

No actual market returns, account simulations, live files or external actions.
"""
from pathlib import Path
from types import SimpleNamespace
import ast
import difflib
import hashlib
import json
import math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'agents/codex/inputs/weekly_cross_review_20261106'
SRC=BASE/'source'


def functions(text,names,env):
    tree=ast.parse(text)
    nodes=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
    assert {n.name for n in nodes}==set(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen_or_proposed_helper','exec'),env)
    return env


def main():
    rows=[]
    for account,cushion,qty,risk in [('3',1822.60,8,2456.),('2',931.34,3,1062.),('4',1939.60,7,2478.)]:
        per=risk/qty
        q=min(qty,math.floor(.9*cushion/per))
        rows.append(dict(account=account,recorded_cushion=cushion,recorded_quantity=qty,
                         recorded_nominal_stop_risk=risk,stop_risk_per_MNQ=per,
                         proposed_90pct_quantity=q,nominal_stop_risk_at_cap=q*per,
                         illustrative_stop_plus_RT2_24=q*(per+2.24),
                         note='Arithmetic on recorded trade budgets, not a counterfactual fill, survival probability or account replay.'))
    assert [r['proposed_90pct_quantity'] for r in rows]==[5,2,4]
    patch=[];checks=[]
    jof=lambda t:t//100*60+t%100
    common=dict(np=np,pd=pd,J0=jof(831),J1=jof(1500),JE=jof(1459),TICK=.25)
    for name,names in [('long_after_green_test.py',{'one','run'}),('daily_reversal_bertola_test.py',{'trades'})]:
        path='analysis/'+name
        text=(SRC/path).read_text();assert text.count('2 * comm')==1
        fixed=text.replace('2 * comm','comm')
        patch.extend(difflib.unified_diff(text.splitlines(keepends=True),fixed.splitlines(keepends=True),
                                        fromfile='a/'+path,tofile='b/'+path,n=1))
        before=functions(text,names,dict(common));after=functions(fixed,names,dict(common))
        for symbol,pv,comm,expected in [('NQ',20.,7.25,-17.25),('ES',50.,5.,-30.)]:
            for stopped in [False,True]:
                shape=(202,1440)
                g=SimpleNamespace(trading=np.arange(202),ts=pd.date_range('2018-01-01',periods=202),
                                  o=np.full(shape,100.),h=np.full(shape,100.),l=np.full(shape,100.),c=np.full(shape,100.))
                day=0 if name.startswith('long') else 200
                if stopped:g.l[day,jof(1500)+1]=99.
                invoke=lambda env:env['run'](g,pv,comm,[0]) if name.startswith('long') else env['trades'](g,pv,comm,.25,'A','always_long')
                a,b=invoke(before),invoke(after)
                assert len(a)==len(b)==1 and a.iloc[0]['kind']==b.iloc[0]['kind']
                assert math.isclose(float(b.iloc[0]['net']-a.iloc[0]['net']),comm,abs_tol=1e-10)
                if not stopped:assert math.isclose(float(b.iloc[0]['net']),expected,abs_tol=1e-10)
                checks.append(dict(helper=name,symbol=symbol,fixture='stop' if stopped else 'flat',
                                   original_net=float(a.iloc[0]['net']),proposed_net=float(b.iloc[0]['net']),
                                   corrected_fixed_RT_charge=comm,entry_exit_decisions_changed=False))
    trials=json.loads((ROOT/'agents/codex/inputs/noise15_20261103/trials.json').read_text())
    report=(ROOT/'agents/codex/results/noise15_20261103.md').read_text()
    assert 'N15_LITERAL_GLOBEX' in json.dumps(trials) and 'N15_PROTECTED_GLOBEX' in json.dumps(trials)
    assert 'user-confirmed NQ15-minute full Globex' in report
    late=json.loads((BASE/'late_source_receipt.json').read_text())
    for item in late['source_files']:
        assert hashlib.sha256((BASE/'post_read_source'/item['path']).read_bytes()).hexdigest()==item['sha256']
    cap_text=(BASE/'post_read_source/analysis/cushion_cap_bench.py').read_text()
    cap_run=functions(cap_text,{'run'},{'np':np})['run']
    late_cases=[]
    for label,st,dd,dll,target,w in [
        ('50K',50000.,2000.,1000.,3000.,[[0.,2500.],[-2100.,-2100.],[-1100.,-1100.],[0.,3000.]]),
        ('150K',150000.,4000.,2000.,9000.,[[0.,7000.],[-3000.,-3000.],[-2500.,-2500.],[0.,7000.]])]:
        w=np.array(w)
        got=cap_run({'fixture':(w,w.copy())},{'fixture':1.},{},0,4,
                    dict(st=st,dd=dd,dll=dll,lock=st+100,tgt=target),'none',0)
        assert got==('pass',4,0,0)
        late_cases.append(dict(account=label,legacy_cap_result=got,
                               note='Invented pre-target floor counterexample, not a historical return test.'))
    assert 'min(bal - r["dd"], r["lock"])' in cap_text
    assert 'min(s + 21, D)' in cap_text
    assert 'A = np.nan_to_num(atr[trr], nan=1e12)' in cap_text
    unknown_atr_quantity=float(np.floor(1100/(.25*np.nan_to_num(np.array([np.nan]),nan=1e12)*2))[0])
    assert unknown_atr_quantity==0
    assert 'ORDER = ("ONB30", "VB", "EOS")' in cap_text and cap_text.count('ORDER')==1
    # run() iterates q insertion order. Show its effect without loading a real trade or return.
    q_order_checks=[]
    for order in [('VB','ONB30'),('ONB30','VB')]:
        qq=dict.fromkeys(order,1.)
        prices={x:(np.zeros((21,1)),np.zeros((21,1))) for x in qq}
        prices['VB'][1][0,0]=3000.
        result_case=cap_run(prices,qq,dict.fromkeys(qq,np.full(21,1500.)),0,21,
                            dict(st=50000.,dd=2000.,dll=1000.,lock=50100.,tgt=3000.),'combined',0)
        q_order_checks.append(dict(insertion_order=order,result=result_case))
    assert q_order_checks[0]['result'][0]=='pass' and q_order_checks[1]['result'][0]=='time'
    funded=(BASE/'post_read_source/analysis/cushion_cap_funded.py').read_text()
    funded_out=(BASE/'post_read_source/analysis/outputs/cushion_cap_funded_vb2_output.txt').read_text()
    ast.parse(funded)
    assert 'Apex 50K PA' in funded and 'if k != "CLS"' in funded
    assert 'pnl = -dll' in funded and 'min(bal - MLL, LOCK)' in funded
    assert "'VB_N': 2" in funded_out
    assert 'blown  8.1%' in funded_out and 'blown  2.3%' in funded_out
    assert 'payouts $ 12,408' in funded_out and 'payouts $ 12,387' in funded_out
    result=dict(scope='Post-read routine arithmetic/scope/proposed-source checks only',market_return_tests=0,
                economic_definitions=0,actual_account_survival_replay=False,
                risk_cap_arithmetic=rows,
                risk_cap_qualification='Stop/cost/gap/concurrency and later losses still matter; new historical0.9cap outcomes need valid inputs and bounded committed registration. Neither legacy nor new audit proves an optimal plan.',
                noise_scope='Codex N15 literal/protected full-Globex only; no RTH-anchor test in that protocol. This does not endorse the distinct RTH-anchor B result or erase previous noise-family history.',
                proposed_fee_patch_cases=checks,
                late_cap_source_head=late['post_read_head'],late_cap_pretarget_fixture_cases=late_cases,
                late_cap_unknown_ATR_quantity=unknown_atr_quantity,
                late_cap_combined_insertion_order_fixtures=q_order_checks,
                late_cap_qualification='Attributed new historical results are not independently rerun. The source retains capped evaluation floors, 21-session expiry, threshold DLL cash and unknown-ATR zero sizing. Combined allocation follows q insertion order, despite unused ONB-first ORDER declaration. Policies use absolute buffers 0/200, not the weekly 0.9 proposal.',
                funded_update_head=late['funded_update_head'],
                funded_source_scope='Source/output inspection only. 50K PA model, CLS excluded, initial VB=3 output and later VB=2 output. No independent funded replay; PA floor locking is legitimate in this preset, distinct from the evaluation defect.',
                funded_VB2_attributed_model_results=dict(bootstrap_2y_baseline_blown_pct=8.1,
                    bootstrap_2y_piece_cap_blown_pct=2.3,bootstrap_2y_payouts_baseline=11778,
                    bootstrap_2y_payouts_piece_cap=11747,chronological_2y_blown_pct_both=1.5,
                    chronological_2y_payouts_baseline=12408,chronological_2y_payouts_piece_cap=12387),
                funded_qualification='Not a full current-book/150K/account execution verification. Overlapping starts and block-resampled histories are dependent model scenarios. DLL threshold-fill assumption, native coverage, registration and live-cushion clock remain unresolved; source adoption is not reviewer approval.',
                fee_patch_scope='Two research helpers only; source proposal not installed or applied to Claude branch, not a strategy-rule rescue. No historical metric recomputed.')
    return result,''.join(patch)


if __name__=='__main__':
    result,patch=main()
    out=ROOT/'agents/codex/proposals/weekly_20261106_commission.patch'
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(patch)
    print(json.dumps(result,indent=2))
