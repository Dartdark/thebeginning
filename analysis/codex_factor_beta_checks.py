"""Independent spot checks of beta clocks, ledgers and fixed costs."""
from pathlib import Path
import json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_factor_beta_sessions';DATA=ROOT/'scratch_data/factor_sessions'
d=pd.read_csv(OUT/'daily.csv',parse_dates=['date']);s=pd.read_csv(OUT/'monthly_selections.csv',parse_dates=['fit_through'])
m=json.loads((OUT/'manifest.json').read_text());checks={}
assert d.date.max()<pd.Timestamp('2023-01-01') and m['recent_opened'] is False
checks['recent_not_opened']=True
assert (s.fit_through.dt.to_period('M')<pd.PeriodIndex(s.month,freq='M')).all()
checks['fit_before_trade_month']=True
assert not s.duplicated(['month','ticker']).any() and (s.groupby(['month','leg']).size()==20).all()
checks['disjoint_20_name_legs']=True
np.testing.assert_allclose(d.net,d.gross-d.cost-d.borrow,atol=1e-12)
np.testing.assert_allclose(d.long_net+d.short_net,d.net,atol=1e-12)
np.testing.assert_allclose(d.cost,d.gross_notional*.0004,atol=1e-12)
np.testing.assert_allclose(d.stress_net,d.gross-d.gross_notional*.001-d.borrow,atol=1e-12)
checks['cash_and_cost_identities']=True
for (mode,sizing,year),g in d.groupby(['mode','sizing',d.date.dt.year]):
    y=pd.read_csv(OUT/'years.csv');r=y[(y['mode']==mode)&(y.sizing==sizing)&(y.year==year)].iloc[0]
    np.testing.assert_allclose(g.net.sum()*100000,r.net,atol=1e-7)
checks['daily_year_reconciliation']=True
px=pd.read_parquet(DATA/'prices.parquet',filters=[('date','>=',pd.Timestamp('2017-01-01')),('date','<=',pd.Timestamp('2022-12-31'))],columns=['date','ticker','adj_close'])
wide=px.pivot(index='date',columns='ticker',values='adj_close').reindex(index=pd.DatetimeIndex(px.loc[px.ticker=='SPY','date'].sort_values()))
ret=wide.pct_change(fill_method=None)
for row in s.iloc[np.linspace(0,len(s)-1,8,dtype=int)].itertuples():
    j=ret.index.get_loc(row.fit_through);train=ret.iloc[max(1,j-251):j+1][['SPY',row.ticker]].dropna()
    fit=np.linalg.lstsq(np.c_[np.ones(len(train)),train.SPY],train[row.ticker],rcond=None)[0][1]
    np.testing.assert_allclose(fit,row.beta,rtol=1e-10,atol=1e-10)
checks['eight_independent_beta_OLS_checks']=True
assert m['variants']==2
for x in json.loads((OUT/'summary.json').read_text()):
    assert isinstance(x['passes'],bool) and not x['passes']
    assert x['unresolved_days']>0 and not x['gates']['no_unresolved']
checks['fail_closed_on_missing_selected_prices']=True
(OUT/'engineering_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
