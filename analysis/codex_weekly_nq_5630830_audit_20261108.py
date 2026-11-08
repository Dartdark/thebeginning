"""Published arithmetic and invented risk paths only; no historical strategy returns."""
from pathlib import Path
import hashlib
import json
import math
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PLAN='agents/codex/plans/weekly_nq_5630830_audit_20261108.md'
CODE='analysis/codex_weekly_nq_5630830_audit_20261108.py'
for name in (PLAN,CODE):
    if subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)!=(ROOT/name).read_bytes():
        raise RuntimeError('commit exact plan/code before audit')

strategy=(1+4879.6/100)**(1/26.3)-1
market=(1+978.1/100)**(1/26.3)-1
calmar=strategy/.059
alpha_5y=1.01-(.04+.1*(.472-.04))
alpha_all=strategy-(.04+.1*(market-.04))
relative_sigma=.1/.7
cagr_5y=(1+3186.7/100)**.2-1
mean_trade=(101*4.26+13*(-1.78))/114
assert math.isclose(strategy,.1602,abs_tol=.0001)
assert math.isclose(calmar,2.72,abs_tol=.01)
assert math.isclose(alpha_5y,.9268,abs_tol=1e-10)
assert math.isclose(alpha_all,.1147,abs_tol=.0001)
assert math.isclose(relative_sigma,.14285714285714288)
assert math.isclose(cagr_5y,1.01,abs_tol=.001)
assert math.isclose(mean_trade,3.57,abs_tol=.01)
low_loss=90/100-1
close_loss=96/100-1
assert low_loss<-.05 and close_loss>-.05
def dd(prices):
    high=prices[0]; worst=0
    for p in prices:
        high=max(high,p);worst=min(worst,p/high-1)
    return worst
assert dd([100,110,120])==0
assert math.isclose(dd([100,80,120]),-.2)
inputs=ROOT/'agents/codex/inputs/weekly_nq_5630830_20261108'
result={
 'scope':'published arithmetic and synthetic risk paths only',
 'groups':{
  'annualization':{'source_total_pct':4879.6,'years':26.3,'derived_cagr':strategy,'benchmark_cagr':market,'calmar':calmar},
  'alpha':{'printed_5y_inputs_alpha':alpha_5y,'full_span_cagr_alpha':alpha_all,'author_final_alpha':.1147,
           'qualification':'Final11.47%is consistent with full-span CAGR arithmetic; printed5yinputs are not. CAGR substitution is not an authenticated periodic CAPM regression.'},
  'beta_correlation':{'author_beta':.1,'author_table_rho':.7,'implied_sigma_ratio':relative_sigma,'uncorrelated_claim_supported':False},
  'trade_claims':{'derived_5y_cagr':cagr_5y,'wins':101,'losses':13,'win_rate':101/114,'mean_trade_pct_from_rounded_inputs':mean_trade},
  'close_stop':{'synthetic_entry':100,'low':90,'close':96,'low_loss':low_loss,'close_loss':close_loss,'close_5pct_rule_triggered':False,
                'illustrative_entry_NQ_points':10000,'five_pct_price_points':500,'one_NQ_dollar_loss':10000,'one_MNQ_dollar_loss':1000},
  'path_risk':{'path_A':[100,110,120],'path_B':[100,80,120],'dd_A':dd([100,110,120]),'dd_B':dd([100,80,120]),'same_terminal_value':True}},
 'groups_completed':6,'assertions_passed':10,'economic_trials':0,'historical_returns_computed':False,'portfolio_tests_run':False,
 'strategy_admission':'FAIL: custom formulas, clocks and native ledger unresolved; no supported neutrality claim',
 'preregistration_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs.iterdir()) if p.is_file()},
 'code_sha256':hashlib.sha256((ROOT/CODE).read_bytes()).hexdigest(),'plan_sha256':hashlib.sha256((ROOT/PLAN).read_bytes()).hexdigest()}
out=ROOT/'analysis/outputs/codex_weekly_nq_5630830_20261108/audit.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
