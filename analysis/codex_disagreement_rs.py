"""One frozen disagreement filter on existing RS long ledger, design2018–22 only."""
from pathlib import Path
import csv,hashlib,json,io,zipfile,xml.etree.ElementTree as ET
import numpy as np,pandas as pd
from openpyxl.utils.datetime import from_excel
from codex_s03_calendar import calendar_status
import metrics as M
from resampling import max_dd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_disagreement_rs_20261029/run_v1'
REPORT=ROOT/'mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Relative Strength.xlsx'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe(x):
 if isinstance(x,dict):return {str(k):safe(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [safe(v) for v in x]
 if isinstance(x,(np.integer,)):return int(x)
 if isinstance(x,(np.bool_,)):return bool(x)
 if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
 return x

def tstat(x):
 x=np.asarray(x,float);return float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>2 and x.std(ddof=1)>0 else np.nan

def score_month(frame):
 if len(frame)<10 or not frame[['overnight','intraday','total']].notna().all().all():return dict(score=np.nan,vol=np.nan,ret=np.nan,days=len(frame))
 sd=frame.total.std(ddof=1)
 return dict(score=float((frame.overnight.abs()+frame.intraday.abs()).mean()/sd) if sd>0 else np.nan,vol=float(sd),ret=float(np.prod(1+frame.total)-1),days=len(frame))

def make_features():
 parts=[];sources=[]
 for year in range(2017,2023):
  p=ROOT/('agents/codex/inputs/ob_v2_bench/NQ_1min_2017.csv' if year==2017 else f'data/NQ_1min_{year}.csv');d=pd.read_csv(p,usecols=['date','time','open','close']);d=d[d.date.between(20170101,20221231)]
  parts.append(d);sources.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),rows=len(d)))
 d=pd.concat(parts,ignore_index=True);groups=d.groupby(['date','time'],sort=False)
 conflicts=[]
 for key,g in d[d.duplicated(['date','time'],keep=False)].groupby(['date','time']):
  if len(g.drop_duplicates())>1:conflicts.append(key)
 d=d.drop_duplicates(['date','time']).set_index(['date','time'])
 for key in conflicts:d.loc[key,['open','close']]=np.nan
 rows=[];previous=None
 for date in pd.date_range('2017-01-01','2022-12-31'):
  status=calendar_status(date)
  if status['kind'] not in ['normal','early']:continue
  dt=int(date.strftime('%Y%m%d'));j=status['cash_close_j'];hh=int(j//60*100+j%60)
  try:o=float(d.loc[(dt,831),'open'])
  except KeyError:o=np.nan
  try:c=float(d.loc[(dt,hh),'close'])
  except KeyError:c=np.nan
  good=np.isfinite(o) and np.isfinite(c) and o>0 and c>0 and previous is not None and np.isfinite(previous) and previous>0
  rows.append(dict(date=date,open=o,close=c,previous_close=previous,
    overnight=o/previous-1 if good else np.nan,intraday=c/o-1 if good else np.nan,total=c/previous-1 if good else np.nan))
  previous=c # Missing scheduled close stays unknown for the next cash session.
 daily=pd.DataFrame(rows).set_index('date')
 monthly=pd.DataFrame({str(k):score_month(g) for k,g in daily.groupby(daily.index.to_period('M'))}).T
 monthly.index=pd.PeriodIndex(monthly.index,freq='M')
 for col in ['score','vol','ret']:
  monthly[col+'_threshold']=monthly[col].shift(1).rolling(6,min_periods=6).median()
 daily.to_csv(OUT/'cash_features.csv');monthly.to_csv(OUT/'monthly_features.csv')
 return daily,monthly,dict(files=sources,conflicting_keys=len(conflicts))

def read_ledger():
 # XML values remain strings until date metadata passes the design boundary.
 with zipfile.ZipFile(REPORT) as z:
  strings=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
  wb=ET.fromstring(z.read('xl/workbook.xml'));rid=None
  for sheet in wb.find('m:sheets',NS):
   if sheet.attrib['name']=='List of Trades':rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
  rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'));target=next(e.attrib['Target'] for e in rels if e.attrib['Id']==rid)
  path=target.lstrip('/') if target.startswith('/') else 'xl/'+target
  pending=None;rows=[];future_rows=0
  for event,row in ET.iterparse(io.BytesIO(z.read(path)),events=['end']):
   if row.tag.rsplit('}',1)[-1]!='row':continue
   cells={}
   for cell in row:
    col=''.join(c for c in cell.attrib['r'] if c.isalpha());v=cell.find('m:v',NS)
    text=v.text if v is not None else ''
    if cell.attrib.get('t')=='s':text=strings[int(text)]
    elif cell.attrib.get('t')=='inlineStr':text=''.join(cell.find('m:is',NS).itertext())
    cells[col]=text
   typ=cells.get('C','')
   if not (typ.startswith('Entry') or typ.startswith('Exit')):row.clear();continue
   date=pd.Timestamp(from_excel(float(cells['E']))).normalize()
   if not pd.Timestamp('2018-01-01')<=date<pd.Timestamp('2023-01-01'):
    future_rows+=date>=pd.Timestamp('2023-01-01');row.clear();continue
   if typ.startswith('Entry'):
    if pending is not None:raise ValueError('Unpaired source entry')
    pending=dict(date=date,side=1 if 'Long' in typ else -1,entry=float(cells['G']),contracts=float(cells['H']),reported_gross=float(cells['I']),source_id=cells['A'])
   else:
    if pending is None or pending['date']!=date:raise ValueError('Missing/crossday source entry')
    exit=float(cells['G']);target_fill=cells['D'].endswith('T')
    gross=pending['reported_gross']/pending['contracts']/10
    np.testing.assert_allclose(gross,(exit-pending['entry'])*pending['side']*2,rtol=0,atol=.02)
    rows.append(dict(**pending,exit=exit,exit_signal=cells['D'],gross_mnq=gross,commission=1.24,entry_slippage=.5,exit_slippage=0 if target_fill else .5,net=gross-1.74-(0 if target_fill else .5)))
    pending=None
   row.clear()
 if pending:raise ValueError('Unclosed source entry')
 f=pd.DataFrame(rows).sort_values('date').reset_index(drop=True)
 if f.date.duplicated().any():raise ValueError('Multiple daily RS events')
 return f,dict(path=str(REPORT.relative_to(ROOT)),sha256=sha(REPORT),future_rows_metadata_only=int(future_rows),future_financial_values_converted=0)

def main():
 OUT.mkdir(exist_ok=False)
 days,months,source=make_features();ledger,mc=read_ledger();idx=days.loc['2018':'2022'].index
 f=ledger.copy()
 for col in ['score','vol','ret']:
  values=[];threshold=[]
  for dt in f.date:
   p=dt.to_period('M')-1
   values.append(months.loc[p,col] if p in months.index else np.nan)
   threshold.append(months.loc[p,col+'_threshold'] if p in months.index else np.nan)
  f[col]=values;f[col+'_threshold']=threshold
  f[col+'_known']=np.isfinite(values)&np.isfinite(threshold)
  f[col+'_keep']=(f.side<0)|~f[col+'_known']|(f[col]>=f[col+'_threshold'])
 f['event_id']=[f'RS_{d.date()}_{i}' for i,d in enumerate(f.date)]
 f.to_csv(OUT/'all_trades_with_filter.csv',index=False)
 L=f[f.side>0].copy().reset_index(drop=True);N=len(L)
 def daily(mask,frame=L):
  x=pd.Series(0.,index=idx)
  for d,v in zip(frame.loc[mask,'date'],frame.loc[mask,'net']):
   if d not in x.index:raise ValueError('Trade date outside admitted cash calendar')
   x.loc[d]+=v
  return x
 summary=[];series={};masks={}
 for name,mask in [('BASE',np.ones(N,bool))]+[(c,L[c+'_keep'].to_numpy(bool)) for c in ['score','vol','ret']]:
  masks[name]=mask;ds=daily(mask);series[name]=ds
  for period in ['2018-22']+[str(y) for y in range(2018,2023)]:
   pm=np.ones(N,bool) if period=='2018-22' else L.date.dt.year.eq(int(period)).to_numpy()
   xs=L.loc[mask&pm,'net'];rs=L.loc[~mask&pm,'net'];bs=L.loc[pm,'net'];dsub=ds if period=='2018-22' else ds[ds.index.year==int(period)]
   summary.append(dict(model=name,period=period,base_count=len(bs),kept_count=len(xs),removed_count=len(rs),base_net=bs.sum(),kept_net=xs.sum(),removed_net=rs.sum(),delta=xs.sum()-bs.sum(),removed_average=rs.mean(),removed_t=tstat(rs),kept_t=tstat(xs),**M.perf(np.r_[0.,dsub.to_numpy()],xs)))
 pd.DataFrame(summary).to_csv(OUT/'metrics_by_year.csv',index=False)
 pd.DataFrame(series).to_csv(OUT/'daily_long_paths.csv')
 # Both-side parent retains ALL original shorts, unchanged.
 short_daily=daily(np.ones(len(f[f.side<0]),bool),f[f.side<0])
 pd.DataFrame({name:v+short_daily for name,v in series.items()}).to_csv(OUT/'daily_whole_parent_paths.csv')
 rng=np.random.default_rng(5164956);K=1000
 membership=np.empty((K,N),bool);paths=np.empty((K,len(idx)))
 primary=masks['score'];known=L.score_known.to_numpy(bool)
 strata=list(L.assign(year=L.date.dt.year,weekday=L.date.dt.weekday).groupby(['year','weekday']).groups.values())
 for rep in range(K):
  mask=~known.copy()
  for group in strata:
   group=np.asarray(group);pool=group[known[group]];count=int(primary[pool].sum())
   if count:mask[rng.choice(pool,size=count,replace=False)]=True
  membership[rep]=mask;paths[rep]=daily(mask).to_numpy()
 profit=paths.sum(1);dd=np.array([max_dd(v) for v in paths]);real_profit=series['score'].sum();real_dd=max_dd(series['score'])
 profit_p=float((1+np.sum(profit>=real_profit))/(K+1));dd_p=float((1+np.sum(dd<=real_dd))/(K+1));joint=float((1+np.sum((profit>=real_profit)&(dd<=real_dd)))/(K+1))
 np.savez_compressed(OUT/'matched_paths.npz',membership=membership,daily=paths,event_ids=L.event_id.to_numpy(str),dates=idx.astype(str).to_numpy(str))
 pd.DataFrame(dict(run=range(K),profit=profit,DD=dd)).to_csv(OUT/'matched_summary.csv',index=False)
 delta=series['score']-series['BASE'];cluster=delta.groupby(delta.index.to_period('M')).sum().reindex(pd.period_range('2018-01','2022-12',freq='M'),fill_value=0)
 draws=rng.integers(0,len(cluster),size=(5000,len(cluster)));totals=cluster.to_numpy()[draws].sum(1);ci=np.quantile(totals,[.025,.975]);np.savez_compressed(OUT/'month_cluster_bootstrap.npz',indices=draws,profit_delta=totals)
 S=pd.DataFrame(summary);row=S[(S.model=='score')&(S.period=='2018-22')].iloc[0];years=S[(S.model=='score')&(S.period!='2018-22')]
 controls={c:float(series[c].sum()-series['BASE'].sum()) for c in ['vol','ret']}
 gates=dict(removed_loses=bool(row.removed_net<0),removed_t_le_minus1=bool(row.removed_t<=-1),total_profit_improves=bool(row.delta>0),kept_t_ge2=bool(row.kept_t>=2),four_positive_years=bool((years.kept_net>0).sum()>=4),three_nonnegative_delta_years=bool((years.delta>=0).sum()>=3),matched_profit_p=profit_p<=.05,matched_DD_p=dd_p<=.05,matched_joint_p=joint<=.05,beats_both_controls=bool(all(row.delta>v for v in controls.values())),cluster_lower_positive=bool(ci[0]>0))
 result=dict(preregistration='b091f9c',phase='design2018-22',primary_evaluations=1,diagnostic_controls=2,parent='Existing MC RelativeStrength; long-filter only; shorts unchanged',native_cost='1MNQ commission1.24RT+.50entry+.50nonlimitexit',source_price_audit=source,source_ledger_audit=mc,long_trades=N,short_trades=int((f.side<0).sum()),known_feature_long_trades=int(known.sum()),unknown_retained_long_trades=int((~known).sum()),primary=row.to_dict(),control_profit_deltas=controls,matched=dict(paths=K,profit_p=profit_p,DD_p=dd_p,joint_p=joint),month_cluster_delta95=ci.tolist(),gates=gates,design_pass=all(gates.values()),historical_run=False,personal_book_bench_run=False,limits=['Immutable parent-ledger filter comparison, not new raw-spec/active-entry-protection certification','Source MC parent target/fill and entry-bar limitations retained','Monthly cluster bootstrap does not identify all longer-horizon serial uncertainty','No account gain/independent replication of stock cross-section claimed'])
 (OUT/'summary.json').write_text(json.dumps(safe(result),indent=2,allow_nan=False)+'\n')
 print(json.dumps(safe({k:result[k] for k in ['long_trades','short_trades','known_feature_long_trades','unknown_retained_long_trades','primary','control_profit_deltas','matched','month_cluster_delta95','gates','design_pass']}),indent=2))

if __name__=='__main__':main()
