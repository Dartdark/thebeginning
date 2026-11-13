"""Post-audit descriptive detail; no rule selection or portfolio changes.
Reconstruct only actual minute positions, timing and a calendar-day $2k
close-marked crossing (diagnostic, not an Apex evaluation simulator).
"""
import hashlib
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'analysis/outputs/codex_book_joint_losses'
sys.path.insert(0,str(ROOT/'analysis'))
import grid24  # pickle class


def main():
    with open(sys.argv[1],'rb') as f:g=pickle.load(f)
    t=pd.read_csv(P/'trades.csv',parse_dates=['date','entry_ts','exit_ts'])
    daily=pd.read_csv(P/'daily.csv',index_col='date',parse_dates=True)
    keys=['ONB30','MON_BR','TWIN','DT','JF','NBL','LDF']
    n=g.D*1440;cl=pd.Series(g.c.ravel()).ffill().to_numpy()
    closed=np.zeros((len(keys),n));opened=np.zeros_like(closed)
    pos=np.zeros((len(keys),n),dtype=np.float32)
    missing=0
    origin=pd.Timestamp(g.ts[0])
    for r in t.itertuples():
        k=keys.index(r.strategy);i=int((r.entry_ts-origin).total_seconds()/60);j=int((r.exit_ts-origin).total_seconds()/60)
        cost=(r.exit-r.entry)*r.side*2*r.qty-r.net
        opened[k,i:j]=(cl[i:j]-r.entry)*r.side*2*r.qty-cost
        closed[k,j]+=r.net;pos[k,i:j+1]+=r.side*r.qty
        missing+=int(np.isnan(g.c.ravel()[i:j+1]).sum())
    mark=closed.cumsum(axis=1)+opened
    assert np.allclose(mark[:,-1],t.groupby('strategy').net.sum().reindex(keys))
    checks={'raw_nan_minutes_inside_trades':missing}
    raw_check=[]
    for year in range(2018,2027):
        fs=[ROOT/f'data/NQ_1min_{year}.csv',ROOT/f'data/NQ_1min_ON_{year}.csv']
        x=pd.concat([pd.read_csv(f,usecols=['date','time','close']) for f in fs if f.exists()]).drop_duplicates(['date','time'])
        ri=np.searchsorted(g.dates,x.date.to_numpy());ji=(x.time//100*60+x.time%100).to_numpy()
        valid=ri<g.D
        a=g.c[ri[valid],ji[valid]];b=x.close.to_numpy()[valid]
        raw_check.append(dict(year=year,rows=int(valid.sum()),mismatch=int((~np.isclose(a,b,equal_nan=True)).sum())))
    pd.DataFrame(raw_check).to_csv(P/'grid_csv_check.csv',index=False)
    assert all(x['mismatch']==0 for x in raw_check)
    rows=np.searchsorted(g.ts,daily.index.to_numpy());cross=[];trough=[];session=[]
    for r,day in zip(rows,daily.index):
        baseline=mark[:,r*1440-1];z=mark[:,r*1440:(r+1)*1440]-baseline[:,None]
        b=z.sum(0);hit=np.flatnonzero(b<=-2000);jj=int(b.argmin())
        ix=hit[0] if len(hit) else None
        if ix is not None:
            p=pos[:,r*1440+ix]
            row=dict(date=day,minute=int(ix),book=float(b[ix]),active=int((p!=0).sum()),
                     losers=int((z[:,ix]<0).sum()),net_mnq=float(p.sum()),gross_mnq=float(abs(p).sum()))
            row.update({k:float(z[kidx,ix]) for kidx,k in enumerate(keys)})
            row.update({k+'_pos':float(p[kidx]) for kidx,k in enumerate(keys)})
            cross.append(row)
        # Also put true 17:00-16:00 session losses on the following weekday.
        # Excludes the 16:00-17:00 maintenance interval. Uses next trading day,
        # so Sunday->Monday and Friday evening->Monday if any data exists.
        i=(r-1)*1440+1020;j=r*1440+960
        zsession=mark[:,i:j+1]-mark[:,i-1,None]
        net_session=zsession[:,-1]
        session.append(dict(date=day,BOOK=float(net_session.sum()),**dict(zip(keys,net_session))))
        losing=z[:,jj]<0;p=pos[:,r*1440+jj]
        trough.append(dict(date=day,minute=jj,book=float(b[jj]),
                           negative_from_active=float(-np.minimum(z[:,jj],0)[p!=0].sum()),
                           negative_from_closed=float(-np.minimum(z[:,jj],0)[p==0].sum()),
                           losing_active=int((losing&(p!=0)).sum()),losing_closed=int((losing&(p==0)).sum())))
    pd.DataFrame(cross).to_csv(P/'dll_crossings.csv',index=False)
    pd.DataFrame(trough).to_csv(P/'trough_active_vs_closed.csv',index=False)
    sess=pd.DataFrame(session).set_index('date');sess.to_csv(P/'session_daily.csv')
    st=[]
    for label,d in [('2018-22',sess[sess.index.year<=2022]),('2023+',sess[sess.index.year>=2023])]:
        tail=d.nsmallest(int(np.ceil(len(d)*.05)),'BOOK')
        st.append(dict(period=label,days=len(d),tail_days=len(tail),tail_mean=tail.BOOK.mean(),
                       multi2=int(((tail[keys]<0).sum(1)>=2).sum()),**tail[keys].mean().to_dict()))
    pd.DataFrame(st).to_csv(P/'session_tails.csv',index=False)
    # Fixed standard-cost sensitivity for NBL, not a fitted strategy variant.
    extra=t[t.strategy=='NBL'].copy()
    extra['extra_cost']=extra.qty*.5*np.where(extra.kind=='target',1,2)
    dd=daily[keys].copy();dd['NBL']-=extra.groupby('date').extra_cost.sum().reindex(dd.index,fill_value=0)
    cs=[]
    for label,mask in [('2018-22',dd.index.year<=2022),('2023+',dd.index.year>=2023)]:
        d=dd.loc[mask];tail=d.loc[d.sum(1).nsmallest(int(np.ceil(len(d)*.05))).index]
        cs.append(dict(period=label,total_nbl=dd.loc[mask,'NBL'].sum(),tail_book=tail.sum(1).mean(),
                       tail_nbl=tail.NBL.mean(),tail_onb=tail.ONB30.mean()))
    pd.DataFrame(cs).to_csv(P/'nbl_standard_cost_sensitivity.csv',index=False)
    # State the historical risk-sizing discrepancy as a convention, not a fix.
    cfg=json.loads((ROOT/'live/expected_setup.json').read_text());cap=[]
    for k,tag in [('ONB30','ONB150-5'),('LDF','LDF150-5')]:
        sub=t[t.strategy==k];limit=cfg['charts'][tag]['max_qty']
        cap.append(dict(strategy=k,metadata_max_qty=limit,historical_max_qty=sub.qty.max(),
                        historical_trades_above_metadata_limit=int((sub.qty>limit).sum())))
    pd.DataFrame(cap).to_csv(P/'size_conventions.csv',index=False)
    # Compact scientific figure: descriptive correlations and tail dollars.
    recent=daily[daily.index.year>=2023]
    tails=pd.read_csv(P/'tails.csv');tail=tails[(tails.period=='2023+')&(tails.fraction==.05)].set_index('strategy')
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    corr=recent[keys].corr();im=axes[0].imshow(corr,vmin=-1,vmax=1,cmap='RdBu_r')
    axes[0].set_xticks(range(len(keys)),keys,rotation=45,ha='right');axes[0].set_yticks(range(len(keys)),keys)
    for i in range(len(keys)):
        for j in range(len(keys)):axes[0].text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',fontsize=8,color='white' if abs(corr.iloc[i,j])>.65 else 'black')
    axes[0].set_title('Daily P&L correlations');fig.colorbar(im,ax=axes[0],shrink=.6)
    axes[1].barh(keys,tail.loc[keys,'mean_contribution'],color='#b84a48');axes[1].invert_yaxis()
    axes[1].set_title('Average contribution on worst 5% of days');axes[1].set_xlabel('Dollars at current research sizes');axes[1].axvline(0,color='black',lw=.6)
    fig.suptitle('Current evaluation book | 2023 to Oct 12, 2026\nUnconstrained strategy P&L; not account outcomes',fontsize=12)
    fig.savefig(P/'joint_losses.png',dpi=160);plt.close(fig)
    checks['normalized_trade_hash']=hashlib.sha256((P/'trades.csv').read_bytes()).hexdigest()
    (P/'detail_checks.json').write_text(json.dumps(checks,indent=2))
    print('detail checks',checks)
    print('session tails',pd.DataFrame(st).to_string(index=False))


if __name__=='__main__':main()
