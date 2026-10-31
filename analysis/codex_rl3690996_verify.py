"""Independent cash/clock/stop invariants on invented paths, before training."""
from pathlib import Path
import json
import hashlib
import os
import numpy as np
import pandas as pd
from codex_rl3690996_core import StockBook,FuturesBook,stock_weights,technical,turbulence,ROOT,RUNTIME

os.environ.setdefault("MPLCONFIGDIR",str(RUNTIME/"matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME",str(RUNTIME/"cache"))
from codex_rl3690996_env import StockEnv,FuturesEnv
from stable_baselines3.common.env_checker import check_env

out=ROOT/"analysis/outputs/codex_rl3690996_build"
out.mkdir(parents=True,exist_ok=True)
checks={}

b=StockBook(1,capital=1000,log=True)
b.transition([1.],[10.],np.array([10.]),np.array([10.]),np.ones(1),20200102,20200103)
q=int(np.floor(1000/(10*1.0005*1.001)))
assert b.q[0]==q and b.cash>=0 and isinstance(b.q[0],np.integer)
expected=1000-q*10*1.0005*1.001
assert np.isclose(b.cash,expected)
b.transition([0.],np.array([10.]),np.array([10.]),np.array([10.]),np.ones(1),20200103,20200106)
expected+=q*10*.9995*.999
assert np.isclose(b.cash,expected) and b.q[0]==0
assert np.isclose(b.cash-1000,sum(t["net"] for t in b.closed))
assert np.isclose(1000-b.cash,b.fees+b.slip)
checks["stock_cash_integer_full_sale_fee_bridge"]=True

b=StockBook(1,capital=1000,log=True)
b.transition([1.],np.array([10.]),np.array([20.]),np.array([20.]),np.ones(1),20200102,20200103)
assert b.fills[0]["raw_price"]==20 and b.fills[0]["intended_change"]==100
assert b.q[0]==int(np.floor(1000/(20*1.0005*1.001)))
try:b.transition([0.],[20.],[20.],[20.],[1.],20200103,20200103)
except ValueError:pass
else:raise AssertionError("same-close fill admitted")
checks["stock_prior_close_target_next_open_fill_and_arrival_cash_clamp"]=True

b=StockBook(1,capital=0,log=True);b.q[0]=10;b.basis[0]=100
b.transition([1.],np.array([10.]),np.array([5.]),np.array([5.]),np.array([2.]),20200102,20200103)
assert b.q[0]==20 and np.isclose(b.equity(np.array([5.])),100) and b.fees==0 and len(b.fills)==0
checks["stock_split_value_and_basis_continuity"]=True
w=stock_weights(np.r_[1.,np.zeros(27)],28)
assert np.isclose(w[0],.1) and w.sum()<=1
assert np.isclose(stock_weights(np.ones(28),28).sum(),1)
checks["stock_weight_cap_cash_residual"]=True

flat=np.full(390,100.);p=FuturesBook(log=True)
for k in range(77):p.step(1,flat,flat,flat,flat,20.,20200103,k)
assert p.q==0 and np.isclose(p.net,-2.24) and np.isclose(p.fees,1.24) and np.isclose(p.slip,1.)
assert p.fills[0]["minute"]==516 and p.fills[-1]["minute"]==896
assert all(f["minute"]>f["decision_minute"] for f in p.fills)
checks["futures_next_minute_native_costs_and_1456_flatten"]=True

p=FuturesBook(log=True);low=flat.copy();low[5]=80.
p.step(1,flat,flat,low,flat,20.,20200103,0)
assert p.q==0 and len(p.trades)==1 and p.trades[0]["exit_minute"]==516
assert np.isclose(p.low,p.net) and p.low>-30
checks["entry_minute_stop_and_no_post_exit_bar_extreme"]=True

p=FuturesBook(log=True);p.step(1,flat,flat,flat,flat,20.,20200103,0)
opening=flat.copy();opening[10]=80.;low=flat.copy();low[10]=75.
p.step(1,opening,flat,low,flat,20.,20200103,1)
assert p.q==0 and np.isclose(p.trades[-1]["exit"],79.75)
checks["held_stop_gap_fills_worse_than_stop"]=True

p=FuturesBook(log=True)
for k in range(77):p.step(1 if k==0 else -1,flat,flat,flat,flat,20.,20200103,k)
assert p.q==0 and len(p.trades)==2 and np.isclose(p.net,-4.48)
assert np.isclose(p.net,sum(t["net"] for t in p.trades))
checks["reversal_counts_both_legs_and_reconciles_closed_cash"]=True

px=np.full(390,1000.);low=px.copy();low[5]=800.
p=FuturesBook(log=True);p.step(1,px,px,low,px,2000.,20200103,0)
assert p.latched and p.q==0 and p.net>=-250
count=len(p.fills);p.step(1,px,px,px,px,2000.,20200103,1)
assert len(p.fills)==count
checks["fee_inclusive_daily_budget_and_latch"]=True

bad=flat.copy();bad[5]=np.nan
try:FuturesBook().step(1,flat,bad,flat,flat,20.,20200103,0)
except ValueError:pass
else:raise AssertionError("missing interval admitted")
checks["missing_quote_rejection"]=True

rng=np.random.default_rng(17)
close=100*np.exp(np.cumsum(rng.normal(0,.01,(850,3)),axis=0));hi=close*1.01;lo=close*.99
features=technical(close,hi,lo);rets=pd.DataFrame(close).pct_change(fill_method=None).to_numpy()
score,threshold=turbulence(rets)
changed=close.copy();changed[650:]*=np.exp(rng.normal(0,.2,(200,3)))
f2=technical(changed,changed*1.01,changed*.99)
s2,t2=turbulence(pd.DataFrame(changed).pct_change(fill_method=None).to_numpy())
assert np.allclose(features[:650],f2[:650],equal_nan=True)
assert np.allclose(score[:650],s2[:650],equal_nan=True) and np.allclose(threshold[:650],t2[:650],equal_nan=True)
checks["future_perturbation_cannot_change_earlier_features_risk_or_thresholds"]=True

stock=dict(c=np.full((4,3),10.),o=np.full((4,3),10.),split=np.ones((4,3)),features=np.zeros((4,3,5)),
           score=np.zeros(4),threshold=np.ones(4),dates=np.array([20200102,20200103,20200106,20200107]))
futures=dict(c=np.full((2,390),100.),o=np.full((2,390),100.),h=np.full((2,390),100.),l=np.full((2,390),100.),
             features=np.zeros((2,78,5)),score=np.zeros((2,78)),threshold=np.ones((2,78)),atr=np.full(2,20.),dates=np.array([20200102,20200103]))
check_env(StockEnv(stock,[1,2,3]),warn=True,skip_render_check=True)
check_env(FuturesEnv(futures,[0,1]),warn=True,skip_render_check=True)
checks["gym_shapes_terminal_transitions_and_observation_bounds"]=True

receipt=dict(checks=checks,all_passed=all(checks.values()),synthetic_only=True,historical_returns_run=False,
    code_hashes={name:hashlib.sha256((ROOT/"analysis"/name).read_bytes()).hexdigest()
                 for name in ["codex_rl3690996_core.py","codex_rl3690996_env.py","codex_rl3690996_train.py","codex_rl3690996_verify.py"]})
(out/"mechanics.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
