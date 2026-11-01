"""Report-only aggregation of the already-frozen design replay; no new rules/data/returns."""
from pathlib import Path
import json,sys
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_review_20261101'
sys.path.insert(0,str(ROOT/'analysis'));from metrics import perf
x=pd.read_csv(OUT/'Q003_design_trades.csv',parse_dates=['date']);rows=[]
for v,t in x.groupby('variant'):
 for nm,mask in [('whole',np.ones(len(t),bool)),('long',t.side.to_numpy()>0),('short',t.side.to_numpy()<0)]:
  z=t[mask];d=z.groupby('date').net.sum().reindex(pd.date_range('2018-01-01','2022-12-31',freq='B'),fill_value=0.)
  assert np.isclose(d.sum(),z.net.sum());m=perf(d,z.net)
  rows.append(dict(variant=int(v),side=nm,trades=len(z),win_rate=float((z.net>0).mean()),net=float(z.net.sum()),average=float(z.net.mean()),t=float(z.net.mean()/z.net.std()*np.sqrt(len(z))),**{k:float(m[k]) for k in ['sharpe','sortino','profit_factor','calmar','ulcer','max_dd']}))
(OUT/'Q003_side_metrics.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps([r for r in rows if r['variant']==1],indent=2))
