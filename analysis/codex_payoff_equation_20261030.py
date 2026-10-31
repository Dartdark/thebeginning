"""Deterministic arithmetic/source-note audit, not a market-return test."""
from pathlib import Path
from statistics import NormalDist
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/payoff_equation_20261030'
OUT=ROOT/'analysis/outputs/codex_payoff_equation_20261030'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    source=json.loads((INPUT/'source_observations.json').read_text());rows=[]
    for r in source['illustrative_rows']:
        e=r['p']*r['R']-(1-r['p']);assert math.isclose(e,r['claimed_normalized_expectancy'],abs_tol=1e-12)
        rows.append(dict(**r,verified_normalized_expectancy=e,break_even_p=1/(1+r['R'])))
    table=[dict(realized_payoff_ratio=R,break_even_win_fraction=1/(1+R))for R in (.5,1,2,3,5)]
    # Explicit invented gross W/L/c example, separate from after-cost net stats.
    p=.2;win=500;loss=100;cost=5
    gross=p*win-(1-p)*loss;net=gross-cost
    assert math.isclose(net,15)
    pbe=(loss+cost)/(win+loss);assert math.isclose(pbe,.175)
    # A higher payoff ratio and modestly lower win rate need not improve edge.
    before=.6*1-(1-.6);after=.55*1.1-(1-.55);assert after<before
    high_win_low_R=.75*.5-(1-.75);assert high_win_low_R>0
    # Wilson interval for an invented10wins/50IIDtrades, with R assumed known.
    n=50;k=10;phat=k/n;z=NormalDist().inv_cdf(.975);den=1+z*z/n
    center=(phat+z*z/(2*n))/den
    half=z*math.sqrt(phat*(1-phat)/n+z*z/(4*n*n))/den
    lo,hi=center-half,center+half;assert lo<1/6<hi
    result=dict(scope='deterministic arithmetic and illustrative sampling check only',new_strategy_return_trials=0,
        source_rows=rows,breakeven_table=table,
        cost_example=dict(gross_p=p,gross_average_win=win,gross_average_loss=loss,cost_per_trade=cost,
            gross_expectancy=gross,net_expectancy=net,cost_adjusted_break_even_win_fraction=pbe),
        higher_R_counterexample=dict(before_p=.6,before_R=1,before_expectancy=before,
            after_p=.55,after_R=1.1,after_expectancy=after),
        profitable_R_below_one_example=dict(p=.75,R=.5,normalized_expectancy=high_win_low_R),
        last50_IID_illustration=dict(wins=k,n=n,win_fraction=phat,Wilson95=[lo,hi],assumed_known_R=5,
            breakeven_win_fraction=1/6,interval_clears_breakeven=False,
            limit='Illustrative probability interval, not actual trades or a test of estimated payoff stability'),
        five_losses_in_a_preselected_block_probability=.8**5,
        Odean_published_proportion_ratio=.148/.098,
        cases_are_constructed_not_observed=True,no_account_or_plan_change=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'math_checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (OUT/'manifest.json').write_text(json.dumps(dict(script_sha256=sha(__file__),
        files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p))for p in INPUT.glob('*.json')],
        result_sha256=sha(OUT/'math_checks.json')),indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
