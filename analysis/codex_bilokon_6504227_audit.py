"""Finite constructed mathematical checks for SSRN6504227; no market-return test."""
import hashlib
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'agents/codex/inputs/bilokon_6504227'


def utility(x):
    return max(F(-1),min(F(1),x))


def main():
    histories=[]
    markov=[]
    for a0 in itertools.product((0,1),repeat=2):
        for next_actions in itertools.product((0,1),repeat=2):
            # Realized history has only two possible paths; these specify each path's next action.
            history_value=sum((utility(a0[z])+utility(next_actions[z]*[F(-2,5),F(1,2)][z]))/2
                              for z in (0,1))
            histories.append((history_value,a0,next_actions))
            # At time1Z1=0: the reduced-state policy can remember only its own a0.
            markov_value=sum((utility(a0[z])+utility(next_actions[a0[z]]*[F(-2,5),F(1,2)][z]))/2
                            for z in (0,1))
            markov.append((markov_value,a0,next_actions))
    h=max(histories); m=max(markov)
    assert h[0]==F(5,4) and m[0]==F(21,20) and h[0]-m[0]==F(1,5)
    assert F(1)+(F(1,2)-F(2,5))/2==m[0]
    # This does not violate MarkovZ. It violates the stronger, unstated reward-sufficiency condition:
    # E[u(X2)|Z0,Z1] differs from E[u(X2)|Z1], the latter being .05 in both histories.
    lam,adv=F(1,10),F(1,20)
    actions={}
    for previous in (0,1):
        q={a:a*adv-lam*int(a!=previous) for a in (0,1)}
        actions[str(previous)]={'action':max(q,key=q.get),'q':{str(k):float(v) for k,v in q.items()}}
    assert actions['0']['action']==0 and actions['1']['action']==1
    # Conditional X supports are disjoint, but utility-optimal active label is constant.
    joint={(0,F(1,2)):F(7,20),(0,F(-1,2)):F(3,20),(1,F(1,5)):F(1,2)}
    marginal={x:sum(p for (z0,x0),p in joint.items() if x0==x) for _,x in joint}
    mi=sum(float(p)*math.log2(float(p/(F(1,2)*marginal[x]))) for (z,x),p in joint.items())
    expected=[F(7,10)*utility(F(1,2))+F(3,10)*utility(F(-1,2)),utility(F(1,5))]
    assert expected==[F(1,5),F(1,5)] and math.isclose(mi,1.)
    ties=[utility(F(a)*0) for a in (0,1)]
    assert ties==[0,0]
    paths=list(BASE.iterdir())
    result={
        'scope':'CONSTRUCTED THEORY CHECKS; NOT MARKET DATA OR TRADING RETURNS',
        'source_written':'2026-04-01','source_posted':'2026-04-20','source_pages':4,
        'market_return_trials':0,'strategy_code_built':False,
        'literal_state_sufficiency_check':{
            'Z0':'equal-probability bit','Z1_Z2':0,'X1':1,'X2_given_Z0':{'0':-.4,'1':.5},
            'switch_cost':0,'terminal_reward':0,'utility':'clamp(x,-1,1)',
            'history_adapted_value':float(h[0]),'reduced_state_markov_value':float(m[0]),
            'gap':float(h[0]-m[0]),
            'missing_assumption':'Expected reward conditional on allowed history must depend only on the chosen state; MarkovZ and a regular conditional law alone do not imply that',
            'status':'Finite counterexample under literal stated assumptions; independent formal review pending'},
        'utility_not_distribution_sufficiency':{
            'expected_active_utility_each_state':[float(v) for v in expected],
            'optimal_action_both_states':1,'I_Z_X_bits':mi,'I_constant_action_X_bits':0.,
            'interpretation':'Optimal binary control need not preserve the conditional PnL distribution; minimal predictive sufficiency is not established by the reward objective'},
        'hysteresis':{'lambda':float(lam),'dynamic_pre_switch_advantage':float(adv),
            'by_previous_action':actions,'on_from_off':'D > lambda','stay_on_from_on':'D > -lambda',
            'boundary_ties':'Require an explicit tie rule unless excluded by the no-tie assumption'},
        'zero_reward_zero_cost_ties':{'off_value':float(ties[0]),'on_value':float(ties[1]),
            'interpretation':'Illustrates the explicitly conditional uniqueness result, not a counterexample to strict separation'},
        'hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()},
        'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    out=ROOT/'analysis/outputs/codex_bilokon_6504227/source_audit.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'mathematical_fixture_checks':4,'history_value':float(h[0]),'markov_value':float(m[0]),
                      'I_Z_X_bits':mi,'market_return_trials':0}))


if __name__=='__main__':
    main()
