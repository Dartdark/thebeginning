"""Independent workbook ledger/statistics check; no maker imports.
Run reconstruction before accessing maker artifacts. Calendar uses date/time only.
This is not independent replication of source trading signals.
"""
from pathlib import Path
import hashlib,json,platform,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_nq_day_flow6_checker'
SOURCES={
'VB':'Backtesting Strategy Performance Report VB v1.xlsx',
'ONB':'Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx',
'MON':'Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx',
'EOS':'Backtesting Strategy Performance Report EOS v1.xlsx',
'LDF':'Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx',
'NFP':'Backtesting Strategy Performance Report _ @NQ - 5 Minutes NFP Fade.xlsx'}
START=pd.Timestamp('2018-01-01'); END=pd.Timestamp('2026-10-09')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tstat(x):
 x=np.asarray(x,float)
 return float(x.mean()/(x.std(ddof=1)/np.sqrt(len(x)))) if len(x)>1 and x.std(ddof=1)>0 else None
def nw(x,lag):
 x=np.asarray(x,float);u=x-x.mean();n=len(u)
 lrv=u@u/n
 for k in range(1,min(lag,n-1)+1):lrv+=2*(1-k/(lag+1))*(u[k:]@u[:-k])/n
 return float(x.mean()/np.sqrt(lrv/n)) if lrv>0 else None
def stats(t,d):
 x=t.net.to_numpy();y=d.to_numpy();eq=np.r_[0,y.cumsum()];dd=np.maximum.accumulate(eq)-eq
 return dict(tickets=len(x),sessions=len(y),active_sessions=int((d!=0).sum()),gross=float(t.gross.sum()),commission=float(t.commission.sum()),slippage=float(t.slippage.sum()),cost=float(t.cost.sum()),net=float(x.sum()),trade_t=tstat(x),daily_iid_t=tstat(y),nw5_t=nw(y,5),nw20_t=nw(y,20),win_rate=float((x>0).mean()) if len(x) else None,trade_pf=float(x[x>0].sum()/-x[x<0].sum()) if (x<0).any() else None,max_closed_dd=float(dd.max()))
def reconstruct():
 OUT.mkdir(parents=True,exist_ok=True);rows=[];src=[];hashes={}
 for sleeve,fn in SOURCES.items():
  p=ROOT/'mc_reports'/fn;hashes[str(p.relative_to(ROOT))]=sha(p)
  a=pd.read_excel(p,sheet_name='List of Trades',header=2)
  e=a[a.Type.astype(str).str.startswith('Entry')].reset_index(drop=True)
  z=a[a.Type.astype(str).str.startswith('Exit')].reset_index(drop=True)
  assert len(e)==len(z),(sleeve,len(e),len(z))
  for i,(en,ex) in enumerate(zip(e.to_dict('records'),z.to_dict('records'))):
   et=pd.Timestamp(en['Date']);xt=pd.Timestamp(ex['Date']);side=1 if en['Type']=='EntryLong' else -1
   assert ex['Type']==('ExitLong' if side==1 else 'ExitShort')
   assert en['Contracts']==ex['Contracts']
   if START<=et.normalize()<=END and START<=xt.normalize()<=END:assert xt>=et
   q=float(en['Contracts']);gross=(float(ex['Price'])-float(en['Price']))*side*2
   reported=float(en['Profit ($)'])/q/10
   assert abs(gross-reported)<1e-8,(sleeve,i,gross,reported)
   target='profit' in str(ex['Signal']).lower() or 'target' in str(ex['Signal']).lower()
   slip=0.5*(1+int(not target));commission=1.24;cost=commission+slip
   session=(xt+pd.Timedelta(hours=7)).normalize()
   keep=START<=et.normalize()<=END and START<=xt.normalize()<=END
   rows.append(dict(sleeve=sleeve,ticket=int(en['Trade #']),entry_datetime=et,exit_datetime=xt,entry_price=en['Price'],exit_price=ex['Price'],source_qty=q,side=side,exit_signal=ex['Signal'],target=target,session=session,gross=gross,commission=commission,slippage=slip,cost=cost,net=gross-cost,keep=keep,cross_date=et.normalize()!=xt.normalize(),after_flat_deadline=(xt.hour*60+xt.minute)>959,entry_after17=(et.hour>=17)))
  src.append(dict(sleeve=sleeve,raw_tickets=len(e)))
 all_t=pd.DataFrame(rows);all_t.to_csv(OUT/'all_raw_tickets.csv',index=False);t=all_t[all_t.keep].copy()
 # Raw day calendar identical to Grid24's time-only eligibility; no OHLC values read.
 time_rows=pd.concat([pd.read_csv(p,usecols=['date','time']) for p in sorted((ROOT/'data').glob('NQ_1min_20*.csv'))])
 time_rows['date']=pd.to_datetime(time_rows['date'].astype(str),format='%Y%m%d')
 day_max=time_rows.groupby('date').time.max();cal=day_max[(day_max>=1100)&(day_max.index.dayofweek<5)].index
 cal=cal[(cal>=START)&(cal<=END)]
 omitted_raw_dates=day_max[(day_max<1100)&(day_max.index>=START)&(day_max.index<=END)]
 missing=sorted(set(t.session)-set(cal));assert not missing,missing
 d=t.groupby('session').net.sum().reindex(cal,fill_value=0)
 t.to_csv(OUT/'tickets.csv',index=False);pd.DataFrame({'date':cal,'net':d.values}).to_csv(OUT/'daily.csv',index=False)
 by=[]
 for label,lo,hi in [('full',START,END),('design',START,pd.Timestamp('2022-12-31')),('validation',pd.Timestamp('2023-01-01'),END)]+[(str(y),pd.Timestamp(y,1,1),min(END,pd.Timestamp(y,12,31))) for y in range(2018,2027)]:
  for sgn,sgnvalue in [('all',None),('long',1),('short',-1)]:
   tt=t[t.session.between(lo,hi)]
   if sgnvalue is not None:tt=tt[tt.side==sgnvalue]
   cc=cal[(cal>=lo)&(cal<=hi)];dy=tt.groupby('session').net.sum().reindex(cc,fill_value=0)
   by.append(dict(era=label,side=sgn,**stats(tt,dy)))
 pd.DataFrame(by).to_csv(OUT/'statistics.csv',index=False)
 summary=[]
 for sleeve in SOURCES:
  a=all_t[all_t.sleeve==sleeve];b=t[t.sleeve==sleeve]
  summary.append(dict(sleeve=sleeve,raw_tickets=len(a),kept=len(b),excluded_before=int((~a.keep & (a.entry_datetime<START)).sum()),excluded_after=int((~a.keep & ((a.entry_datetime.dt.normalize()>END)|(a.exit_datetime.dt.normalize()>END))).sum()),targets=int(b.target.sum()),cross_date=int(b.cross_date.sum()),late_exit=int(b.after_flat_deadline.sum()),source_qty=list(a.source_qty.unique()),gross=b.gross.sum(),commission=b.commission.sum(),slippage=b.slippage.sum(),cost=b.cost.sum(),net=b.net.sum()))
 pd.DataFrame(summary).to_csv(OUT/'sources.csv',index=False)
 t[t.cross_date|t.after_flat_deadline].to_csv(OUT/'carry_and_late_exit.csv',index=False)
 # Stamped position concurrency, exits before entries at ties. Not an intraminute fill proof.
 events=[]
 for r in t.itertuples():
  events.extend([(r.entry_datetime,1,r.side,r.sleeve,r.ticket),(r.exit_datetime,-1,-r.side,r.sleeve,r.ticket)])
 events.sort(key=lambda x:(x[0],x[1]))
 gross=net=0;mxg=mxn=0;ev=[]
 for tm,dg,dn,s,id_ in events:
  gross+=dg;net+=dn;mxg=max(mxg,gross);mxn=max(mxn,abs(net));ev.append(dict(time=tm,delta_gross=dg,delta_net=dn,gross=gross,net=net,sleeve=s,ticket=id_))
 pd.DataFrame(ev).to_csv(OUT/'stamped_position_events.csv',index=False)
 audit=dict(created_utc=pd.Timestamp.now(tz='UTC').isoformat(),independence='Before maker script or output access',scope='Independent raw-workbook ledger/statistics reconstruction; not source-signal replication',python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sources=hashes,checker_sha256=sha(Path(__file__)),calendar_rule='Raw NQ day files date/time only, max time >=1100 and Monday-Friday; realized exit timestamp +7h floor to date',calendar_sessions=len(cal),omitted_early_raw_dates={str(k):int(v) for k,v in omitted_raw_dates.items()},max_stamped_gross=mxg,max_abs_stamped_net=mxn,full=by[0],source_summary=summary)
 (OUT/'independent_snapshot.json').write_text(json.dumps(audit,indent=2,default=lambda x:float(x)))
 print(json.dumps(audit,indent=2,default=lambda x:float(x)))
def compare():
 import ast,itertools
 maker=ROOT/'analysis/outputs/codex_nq_day_flow6'
 t=pd.read_csv(OUT/'tickets.csv',parse_dates=['entry_datetime','exit_datetime','session'])
 mt=pd.concat([pd.read_csv(maker/f'{phase}_trades.csv') for phase in ['design','validation']],ignore_index=True)
 for c in ['source_entry_stamp','source_exit_stamp','date']:mt[c]=pd.to_datetime(mt[c])
 keys=['sleeve','entry_datetime','exit_datetime']
 mt=mt.rename(columns={'source_entry_stamp':'entry_datetime','source_exit_stamp':'exit_datetime'})
 merged=t.merge(mt,on=keys,how='outer',suffixes=('_ind','_maker'),indicator=True,validate='one_to_one')
 assert (merged._merge=='both').all()
 maps={'side':'side','entry_price':'entry','exit_price':'exit','source_qty':'source_contracts','gross':'gross_micro','cost':'cost_micro','net':'net_micro'}
 differences={}
 for ind,m in maps.items():
  a=ind+'_ind' if ind in mt.columns and ind not in keys else ind
  b=m+'_maker' if m in t.columns and m not in keys else m
  differences[ind]=float(np.max(np.abs(merged[a]-merged[b])))
  assert differences[ind]<1e-8,(ind,differences[ind])
 assert (merged.session==merged.date).all()
 daily=pd.read_csv(OUT/'daily.csv',parse_dates=['date']).set_index('date').net
 md=pd.concat([pd.read_csv(maker/f'{phase}_daily.csv',parse_dates=['date']) for phase in ['design','validation']]).set_index('date').total
 assert daily.index.equals(md.index)
 daily_diff=float(np.max(np.abs(daily-md)));assert daily_diff<1e-8
 ms=pd.read_csv(maker/'metrics.csv');is_=pd.read_csv(OUT/'statistics.csv')
 periods={'design':'2018-22','validation':'2023+','full':'full'};metric_map={'tickets':'trades','sessions':'days','net':'total','gross':'gross','cost':'costs','trade_t':'t_trade','daily_iid_t':'t_daily','nw5_t':'t_nw5','nw20_t':'t_nw20','max_closed_dd':'max_dd'}
 errors=[]
 for r in is_.to_dict('records'):
  period=periods.get(r['era'],r['era']);matched=ms[(ms.period.astype(str)==period)&(ms.side==r['side'])]
  if matched.empty:continue
  mr=matched.iloc[0]
  for a,b in metric_map.items():
   err=abs(float(r[a])-float(mr[b]));assert err<1e-6,(period,r['side'],a,err)
   errors.append(dict(period=period,side=r['side'],metric=a,absolute_difference=err))
 pd.DataFrame(errors).to_csv(OUT/'maker_metric_differences.csv',index=False)
 # Independent fixed stress arithmetic, using the reconstructed gross ledger.
 stress=[]
 for label,fee,mult in [('primary',1.24,1),('fee_1.04',1.04,1),('four_ticks',1.24,4)]:
  st=t.copy();st['commission']=fee;st['slippage']=t.slippage*mult;st['cost']=st.commission+st.slippage;st['net']=st.gross-st.cost
  dy=st.groupby('session').net.sum().reindex(daily.index,fill_value=0)
  stress.append(dict(case=label,**stats(st,dy)))
 pd.DataFrame(stress).to_csv(OUT/'cost_sensitivity.csv',index=False)
 # Extract only the post-reconstruction reference class, with no maker imports or runs.
 tree=ast.parse((ROOT/'analysis/codex_nq_day_flow6.py').read_text())
 node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='VirtualSleeves')
 ns={'REPORTS':SOURCES};exec(compile(ast.Module(body=[node],type_ignores=[]),'<maker VirtualSleeves>','exec'),ns)
 cls=ns['VirtualSleeves'];count=0
 for pos in itertools.product([-1,0,1],repeat=6):
  for sleeve in SOURCES:
   for desired in [-1,0,1]:
    obj=cls();obj.position=dict(zip(SOURCES,pos));old=sum(pos);delta=obj.target(sleeve,desired)
    assert delta==sum(obj.position.values())-old and abs(sum(obj.position.values()))<=6
    count+=1
 obj=cls();obj.target('ONB',-1);obj.target('ONB',0);obj.target('ONB',-1)
 stale_delta=obj.target('ONB',0)
 result=dict(checker_sha256=sha(Path(__file__)),compared_after_independent_snapshot=True,ticket_rows=len(merged),ticket_max_abs_difference=differences,daily_sessions=len(daily),daily_max_abs_difference=daily_diff,metric_rows=len(errors),reference_target_transitions_checked=count,delayed_exit_after_reentry_delta=stale_delta,delayed_exit_after_reentry_target=sum(obj.position.values()),reference_limit='No generation/order ID, actual-position feedback, partial-fill/rejection/cancel handling, or platform integration; delayed previous-ticket exit can flatten a new same-sleeve position.',stress_full=stress)
 (OUT/'maker_comparison.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 if '--compare' in sys.argv:compare()
 else:reconstruct()
