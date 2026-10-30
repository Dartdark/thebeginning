"""Audit saved Nocturne results only: no new prices, fills or strategy definitions."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent/'outputs/codex_nocturne_20261030'
t=pd.read_csv(P/'design_trades.csv');n=pd.read_csv(P/'design_nights.csv');r=json.loads((P/'design_gate.json').read_text())
f=t[t.kept];g=t.groupby('date')
checks={
 'positive_fill_prices':bool((t[['entry','exit']]>0).all().all()),
 'two_trade_nightly_cap':bool(g.size().max()<=2),
 'one_first_leg_each_night':bool((t[t.leg==1].groupby('date').size()==1).all()),
 'all_long':bool((t.side==1).all()),
 'native_gross_identity':bool(np.allclose(t.gross_mnq,(t.exit-t.entry)*2)),
 'native_net_identity':bool(np.allclose(t.net_mnq,t.gross_mnq-1.24-.5*t.market_fills)),
 'stress_identity':bool(np.allclose(t.stress_mnq,t.net_mnq-.5*t.market_fills)),
 'source_cost_identity':bool(np.allclose(t.source_cost_mnq,t.gross_mnq-.725)),
 'night_and_trade_totals':bool(np.allclose(g.net_mnq.sum().reindex(n.date),n.net_mnq)),
 'filtered_result_total':bool(np.isclose(f.net_mnq.sum(),r['filtered']['total'])),
 'r2_gate_exact':bool((n.kept==(n.r2>=.3)).all()),
 'target_reference_identity':bool(np.allclose(t.loc[t.kind==1,'exit']-t.loc[t.kind==1,'entry'],25)),
}
for date,legs in g:
 if len(legs)==2:
  a,b=legs.sort_values('leg').iloc[0],legs.sort_values('leg').iloc[1]
  assert a.kind==1 and b.j0==((int(a.j1)+4)//5)*5+1
checks['reentry_after_target_next5bar']=True
assert all(checks.values())
out={'checks':checks,'audit_type':'CSV-only self-audit, not independent replication',
     'new_market_return_trials':0,'source_arithmetic':{'reported_total_nq':129541+36381+47434,
     'reported_oos_mean_mnq_if_same860trades':(36381+47434)/860/10,'claimed_oos_mean_mnq':9.92,
     'source_worst_night_dollars_beforecost_by_mnq':{str(q):568*2*q for q in [1,2,4,5]}}}
(P/'audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
