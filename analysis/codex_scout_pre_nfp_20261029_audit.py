"""Recover a JSON receipt from frozen design CSVs after numpy.bool_ serialization failed.

No price reads, signal changes or new fills. Original implementation stays frozen.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import metrics as M

OUT = Path(__file__).resolve().parent / 'outputs/codex_scout_pre_nfp_20261029'
t = pd.read_csv(OUT/'design_trades.csv', parse_dates=['date'])
d = pd.read_csv(OUT/'design_daily.csv', index_col=0).iloc[:, 0]
y = pd.read_csv(OUT/'design_years.csv')
c = pd.read_csv(OUT/'design_controls.csv').iloc[:, 0]
assert len(t) == 55 and np.isclose(d.sum(), t.net_mes.sum())
assert np.allclose(t.net_es, (t.exit-t.entry)*50-30)
assert np.allclose(t.net_mes, (t.exit-t.entry)*5-3.74)
assert np.allclose(t.stress_mes, t.net_mes-2.5)
rng=np.random.default_rng(3387173)
boot=[]
for _ in range(2000):
    years=rng.choice(np.arange(2018,2023),5,replace=True)
    values=np.concatenate([t.loc[t.date.dt.year==year,'net_mes'].to_numpy() for year in years])
    boot.append(float(values.mean()))
ci=np.percentile(boot,[5,95])
p=float((1+(c>=t.net_mes.mean()).sum())/1001)
def metric(column):
    daily=d.copy()
    # Linear cost bridge preserves dates and all zero-exposure days.
    if column!='net_mes':
        # Compute the same calendar from the saved daily index, never new prices.
        daily=pd.Series(0.,index=pd.to_datetime(d.index))
        grouped=t.groupby('date')[column].sum()
        daily.loc[grouped.index]=grouped
    m=M.perf(daily,t[column]);x=t[column]
    m.update(t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))),total=float(x.sum()))
    return m
m=metric('net_mes')
gates=dict(min_40_trades=len(t)>=40,positive_native_net=m['avg']>0,t_at_least_2=m['t']>=2,
           four_positive_years=int((y.total>0).sum())>=4,year_bootstrap_low_positive=ci[0]>0,
           matched_placebo_p_le_05=p<=.05,two_tick_each_fill_stress_positive=t.stress_mes.mean()>0)
result=dict(phase='design',period='2018-2022',native_size='1 MES',metrics_mes=m,
            metrics_es=metric('net_es'),gross_es=metric('gross_es'),placebo_p=p,
            placebo_average_net_mes=float(c.mean()),mean_net_mes_ci90=ci.tolist(),
            stress_mean_mes=float(t.stress_mes.mean()),gates={k:bool(v) for k,v in gates.items()},
            passed=bool(all(gates.values())),long_only=True,shorts='No short rule registered or run',
            recent_tested=False,accounts_tested=False,engineering_recovery='CSV-only; numpy.bool_ JSON serialization failure; no rerun or rule changes')
(OUT/'design_gate.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result,indent=2,allow_nan=False))
