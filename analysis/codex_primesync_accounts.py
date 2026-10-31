"""Frozen PrimeSync account-placement comparisons; no entry/exit optimization."""
import sys,json,pickle,contextlib,io,hashlib
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'analysis'))
import codex_current_payout_timing as B
import codex_primesync as PS
import metrics as M
OUT=ROOT/'analysis/outputs/codex_primesync_accounts'
INPUT=ROOT/'agents/codex/inputs/primesync_accounts'
PLAN='2ecbaa2da48a3445ef5b71587b63d6444904df70'

def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,default=str)+'\n')
def interval(x):
 rng=np.random.default_rng(2711);x=np.asarray(x);return np.percentile([x[rng.integers(0,len(x),len(x))].mean() for _ in range(2000)],[5,95]).tolist()

def candidate(lab,market,k):
 rows=[]
 for period in ['design','recent']:
  t=pd.read_csv(PS.OUT/f'{period}_{market}_{k}_exit0_trades.csv',parse_dates=['date']);rows.append(t)
 t=pd.concat(rows).sort_values(['date','entry_j']).reset_index(drop=True)
 grid=lab.g if market=='NQ' else pickle.load(open(ROOT/'scratch_data/ge.pkl','rb'))
 dates=pd.DatetimeIndex(lab.g.ts[lab.tr]);pos={d:i for i,d in enumerate(dates)};gpos={pd.Timestamp(d):i for i,d in enumerate(grid.ts)}
 w=np.zeros((lab.D,1440));r=np.zeros_like(w);pv=2 if market=='NQ' else 5;counts=np.zeros(lab.D);used=[]
 for z in t.itertuples():
  if z.date not in pos:continue
  d=pos[z.date];gd=gpos[z.date];e=z.entry;side=z.side;stop=-z.risk
  targets=np.ceil(z.risk*np.array([1.5,2.5,4.5])/.25-1e-10)*.25
  lastnet=z.net/z.qty
  for j in range(z.entry_j,z.exit_j+1):
   o,h,l,c=(getattr(grid,n)[gd,j] for n in 'ohlc');points=(o,h,l,c) if h-o<=o-l else (o,l,h,c)
   low=0.;done=False
   for ix,px in enumerate(points):
    u=side*(px-e)
    if u<=stop:
     actual=(px if ix==0 else e+side*stop)-side*.25;low=min(low,side*(actual-e)*pv-1.04);done=True;break
    low=min(low,u*pv-.52)
    if u>=targets[1]:stop=max(stop,targets[0])
    elif u>=targets[0]:stop=max(stop,0.)
    if u>=targets[2]+1:done=True;break
   if done and j!=z.exit_j:raise AssertionError('Replayed exit time differs from frozen trade ledger')
   if j==z.exit_j:
    w[d,j]+=min(low,lastnet);w[d,j+1:]+=lastnet;r[d,j:]+=lastnet
   else:w[d,j]+=low
  counts[d]+=1;used.append(dict(date=z.date,net=lastnet))
 # Each completed trade's cash persists in all subsequent minutes.
 expected=pd.DataFrame(used).groupby('date').net.sum().reindex(dates,fill_value=0.).to_numpy()
 np.testing.assert_allclose(r[:,-1],expected,atol=1e-8)
 np.testing.assert_allclose(w[:,-1],expected,atol=1e-8)
 return w, r, counts

def personal_base():
 meta=json.loads((INPUT/'source_manifest.json').read_text());files={x['original']:ROOT/x['local'] for x in meta['sources']}
 ns={};exec(meta['personal_source'].split('if __name__ == "__main__":')[0],ns)
 p=pd.read_csv(files['agents/tasks/plan_daily_pnl.csv'],parse_dates=['date']).set_index('date');p=p-.55*(p!=0);days=p.index
 def csv(key):return pd.read_csv(files['checks/candidates/'+key],parse_dates=['date'])
 def series(t):
  t=t[t.date<=days[-1]];idx=np.minimum(days.searchsorted(pd.DatetimeIndex(t.date)),len(days)-1)
  return pd.Series(t.net.to_numpy()/10-.55,index=days[idx]).groupby(level=0).sum().reindex(days,fill_value=0.)
 p['FC2B']=series(csv('fc_2b/trades.csv'))
 p['Twin']=ns['twin_marked'](days,path=str(files['checks/candidates/twin_continuation/trades.csv']))
 for name,path in [('OT','overnight_tick/trades.csv'),('DT','dual_thrust/trades.csv'),('S47','s47_v2/python_trades_v2.csv'),('ST','swing_target/mc_trades_v3.csv'),('PT','papertrend/mc_trades_claude.csv')]:p[name]=series(csv(path))
 ku=csv('kusho/python_trades_v9_rolladj.csv');ku['date']=pd.to_datetime(ku.exit_date);p['Kusho']=series(ku)
 p['S30']=pd.read_csv(files['checks/candidates/s30_ibs/daily_nq_es_per_micro.csv'],index_col=0,parse_dates=True).iloc[:,0].reindex(days,fill_value=0.)
 assert len(p.columns)==19
 return p

def main():
 OUT.mkdir(parents=True,exist_ok=True);fund=[];evalu=[];person=[];checks=[]
 personal=personal_base()
 with B.pinned(ROOT/'scratch_data'):
  import funded_bootstrap as fb,funded_sim as f50,funded_sim150 as f150
  import codex_ob_v2_accounts as acc,portfolio as pf,funded_lab as fl,build_lab as bl
  import combine_levers_test as cl,plan_150k_test as ev
  lab,base,_,_=B.build_lab(ROOT/'scratch_data')
  for n in lab.C:lab.real_fees(1.04-(.50 if n=='MOC_MES' else .725),[n])
  dates=pd.DatetimeIndex(lab.g.ts[lab.tr]);hist=np.concatenate([fb.Boot(lab)._histories(250,500,20,s) for s in [1,2,3,4]])
  ep=B.evaluation_paths(lab,1.04)
  old=pf.COST;pf.COST=10.4
  vbw,vbr=[a[lab.tr]/10 for a in pf.paths(lab.g,fl.with_slippage(pf.load_mc(lab.g,bl.REPORTS['VB'][0])))];pf.COST=old
  idx=np.random.default_rng(2710).integers(0,len(dates),(1000,13));idx=((idx[:,:,None]+np.arange(20))%len(dates)).reshape(1000,-1)[:,:252]
  for market,k in [('NQ',15),('NQ',30),('ES',15),('ES',30)]:
   name=f'{market}{k}';cw,cr,ct=candidate(lab,market,k);lab.W['PS']=cw;lab.C['PS']=cr[:,-1]
   for which,mod,ref in [(50,f50,1500.),(150,f150,3000.)]:
    b=base[which];empty={x:y for x,y in b.items() if x not in ['VB_N','VB_F']}
    plans={'BASE':b,'ADD':{**b,'PS':1},'EMPTY_VB':empty,'REPLACE_VB':{**empty,'PS':1}};raw={}
    acct=np.array([mod.START,mod.MLL,mod.LOCK,mod.SAFETY,mod.MIN_DAY,mod.MIN_DAYS,which],float)
    for label,plan in plans.items():
     keys=sorted(plan);_,q=lab._base({x:plan[x] for x in keys});w=np.stack([lab.W[x] for x in keys]);c=np.stack([lab.C[x] for x in keys]);table=acc.make_table(w,c,q)
     got=B.run_lookup(table,hist[17],acct,ref)
     exp=mod.run_pa_sized(np.ascontiguousarray(w[:,hist[17]]),np.ascontiguousarray(c[:,hist[17]]),np.ascontiguousarray(q[:,hist[17]]),0,500,0.,True,.5,1.,ref,np.ones(6));np.testing.assert_array_equal(got,exp)
     raw[label]=(np.stack([B.run_lookup(table,h[:250],acct,ref) for h in hist]),np.stack([B.run_lookup(table,h,acct,ref) for h in hist]));del w,c,table
    for label,(y1,y2) in raw.items():
     delta=y1[:,0]-raw['BASE'][0][:,0];lo,hi=interval(delta)
     fund.append(dict(context=name,account=which,config=label,year1=y1[:,0].mean(),year2=y2[:,0].mean(),blown=y2[:,3].mean(),days6=B.event_quantile(np.where(y2[:,1]==6,y2[:,2],-1),.5),delta_year1=delta.mean(),lo=lo,hi=hi))
    for label,ww,rr in [('BASE',ep[which][0],ep[which][1]),('ADD',ep[which][0]+cw,ep[which][1]+cr),('EMPTY_VB',ep[which][0]-vbw*(8 if which==50 else 20),ep[which][1]-vbr*(8 if which==50 else 20)),('REPLACE_VB',ep[which][0]-vbw*(8 if which==50 else 20)+cw,ep[which][1]-vbr*(8 if which==50 else 20)+cr)]:
     res=[cl.challenge(ww,rr,np.arange(s,s+21),lambda a,b,c:1.) if which==50 else ev.evaluation(ww,rr,s,len(dates),ev.R150) for s in range(len(dates)-20)]
     outcome=np.array([r[0] for r in res]);
     for cohort,mask in [('all',np.ones(len(res),bool)),('recent',dates[:len(res)].year>=2023)]:evalu.append(dict(context=name,account=which,config=label,cohort=cohort,pass_rate=np.mean(outcome[mask]=='pass'),starts=int(mask.sum())))
   pp=personal.reindex(dates).fillna(0.);pc=cr[:,-1]-.235*ct;total=pp.sum(axis=1).to_numpy();vb=pp['VaultBreak'].to_numpy()
   for label,x in [('BASE',total),('ADD',total+pc),('EMPTY_VB',total-vb),('REPLACE_VB',total-vb+pc)]:
    xx=x[idx];eq=xx.cumsum(1);dd=-(eq-np.maximum.accumulate(np.maximum(eq,0),axis=1)).min(1);dd95=np.percentile(dd,95);annual=xx.sum(1).mean()
    person.append(dict(context=name,config=label,annual=annual,dd95=dd95,capital=dd95/.2,return_dd=annual/dd95,sharpe=x.mean()/x.std(ddof=1)*np.sqrt(252)))
   print('done',name,flush=True)
   pd.DataFrame(fund).to_csv(OUT/'funded.csv',index=False);pd.DataFrame(evalu).to_csv(OUT/'evaluations.csv',index=False);pd.DataFrame(person).to_csv(OUT/'personal.csv',index=False)
 dump(OUT/'manifest.json',dict(plan=PLAN,contexts=4,n=1000,block=20,seeds=[1,2,3,4],coverage=[str(dates[0]),str(dates[-1])],parity='32 context/account/config direct checks',candidate_size='1micro on frozen eligible entries',personal_source=json.loads((INPUT/'source_manifest.json').read_text())['ref'],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limitations=['MC parity absent','Personal inherited19-piece booking/cost approximations retained','No fresh holdout; context selection exploratory']))

if __name__=='__main__':main()
