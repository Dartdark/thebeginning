"""SSRN6401038 source/mechanics audit. NO market returns, fitted models or account tests.

The examples are deliberately constructed algebra/clock counterexamples, not profitability trials.
"""
from pathlib import Path
from decimal import Decimal as D
import hashlib
import json
import math
import sys

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'agents/codex/inputs/straddle_buffer_6401038_20261031'
OUT=ROOT/'analysis/outputs/codex_straddle_buffer_audit_20261031'


def combined_pnl(entry, exit_wrong, close_kept, up):
    if up:
        return (close_kept-entry)+(entry-exit_wrong)
    return (entry-close_kept)+(exit_wrong-entry)


def main():
    claims={
        'evidence':'Transcribed author claims, not our backtest',
        'source_span':'2018-01-02 through2025-11-28',
        'securities':48,'source_trading_days':1989,
        'test_days_table13':484,'configurations_per_buffer':288,
        'source_train_test_fraction':[.75,.25],
        'headline_table13':[
            {'buffer':.1,'cumulative_return_pct':14051,'sharpe':14.86,'sortino':111.85,'win_pct':85.5,'max_dd_pct':-1.6,'beat_pct':100},
            {'buffer':.2,'cumulative_return_pct':2688,'sharpe':11.32,'sortino':39.13,'win_pct':75.2,'max_dd_pct':-4.1,'beat_pct':100},
            {'buffer':.3,'cumulative_return_pct':583,'sharpe':7.26,'sortino':16.10,'win_pct':65.6,'max_dd_pct':-10.6,'beat_pct':100}],
        'table6_daily_two_leg_cost_bps':[12,60],
        'table15_reported_daily_cost_bps':8,
        'prediction_accuracy_table14_pct':70.97,
        'model_random_benchmark_sharpe_page67':4.60,
        'contradictory_ml_benchmark_sharpe_page67':'exceeding19',
        'paper_max_feature_count':45,
        'table3_feature_counts':[6,1,1,1,3,1,3,3,1,1,1,2,1,1,4,2,1,3,1,1,4,2,1,1,1],
    }
    checks=[]
    for up in (True,False):
        expected=D('104')-D('99') if up else D('99')-D('104')
        values=[combined_pnl(D(e),D('99'),D('104'),up) for e in ('80','100','150')]
        assert all(v==expected for v in values)
        checks.append({'up':up,'entry_prices':[80,100,150],
                       'combined_dollar_pnl_each':[str(v) for v in values],
                       'meaning':'Equal opposite entries cancel; return denominator/capital and costs are separate.'})
    # Two hypothetical day-t+1 paths share every quote through the order decision.
    prefix=[D('100'),D('99'),D('101')]
    path_a=prefix+[D('105'),D('104')]
    path_b=prefix+[D('90'),D('92')]
    beta=D('.3')
    def final_hindsight_buy(path):return min(path)+beta*(max(path)-min(path))
    a,b=final_hindsight_buy(path_a),final_hindsight_buy(path_b)
    assert a!=b
    # Analytic IID zero-mean equal-variance Gaussian thought experiment:
    # sign(X) predicts sign(X+Y) with probability 1/2+asin(corr)/pi, corr=1/sqrt(2).
    p=.5+math.asin(1/math.sqrt(2))/math.pi
    assert abs(p-.75)<1e-12
    results={
        'scope':'Synthetic math and source consistency only; no market data loaded',
        'entry_cancellation_examples':checks,
        'identical_prefix_future_extreme_counterexample':{
            'common_prefix':[str(x) for x in prefix],
            'future_a':[str(x) for x in path_a[len(prefix):]],
            'future_b':[str(x) for x in path_b[len(prefix):]],
            'paper_final_day_up_exit_a':str(a),'paper_final_day_up_exit_b':str(b),
            'conclusion':'One prefix-only decision cannot know which final-day order level to choose.'},
        'analytic_partly_observed_target_example':{
            'assumption':'Independent equal-variance zero-mean Gaussian day-t and future returns; not market evidence',
            'known_component_sign_accuracy_for_total_two_component_sign':p,
            'future_component_direction_accuracy':.5,
            'meaning':'High accuracy against an old anchor does not establish forecast skill on remaining tradable returns.'},
        'table3_count_sum':sum(claims['table3_feature_counts']),
        'new_economic_return_definitions':0,'account_simulations':0,
    }
    manifest={'python':sys.version,'python_executable':sys.executable,
              'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(SRC.iterdir()) if p.is_file()}}
    OUT.mkdir(parents=True,exist_ok=True)
    for name,obj in [('claims.json',claims),('checks.json',results),('manifest.json',manifest)]:
        (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
