"""Independent synthetic implementation review; never loads market data."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scratch_data/codex_deps'),str(ROOT/'analysis')]
import numpy as np
import pandas as pd
from codex_orb30_ema import simulate


def main():
    tests={}
    def run(bars,rr=1.85,mode=0,side=1,path=0):
        a=[np.full((1,1440),np.nan) for _ in range(4)]
        for j,values in bars.items():
            for x,v in zip(a,values):x[0,j]=v
        z,_=simulate(*a,np.array([100.]),np.array([90.]),np.array([True]),rr,np.array([541]),956,mode,path,side)
        return z
    flat=(100,100,100,100)
    z=run({540:(90,200,80,100),541:(99,99,98,99),956:flat})
    tests['no_or_bar_entry']=len(z)==0
    z=run({541:(91,101,90,100),956:flat})
    tests['pre_entry_low_excluded']=len(z)==1 and z[0,6]==0
    z=run({541:(100,101,89,95),542:(100,120,100,120),956:flat})
    tests['entry_bar_stop_and_one_trade']=len(z)==1 and z[0,6]==2 and z[0,4]==90
    z=run({541:(100,119.25,100,119),956:flat})
    tests['target_requires_full_point_through']=z[0,6]==0
    z=run({541:(100,119.5,100,119),956:flat})
    tests['target_one_point_through_fills']=z[0,6]==1 and z[0,4]==118.5
    z=run({541:(100,101,99,100),542:(85,90,80,85),956:flat})
    tests['worse_open_stop_gap']=z[0,6]==2 and z[0,4]==85
    z=run({541:(105,134,104,130),956:flat})
    tests['entry_gap_updates_risk_target']=z[0,3]==105 and z[0,5]==15 and z[0,4]==132.75
    z=run({541:(99,99,98,99),956:(105,120,90,100)})
    tests['flatten_cancels_before_entry']=len(z)==0
    z=run({541:(100,101,99,100)})
    tests['missing_flatten_not_fabricated']=len(z)==1 and z[0,11]==1 and np.isnan(z[0,4])
    z=run({541:(100,130,99,125),956:flat},rr=0.)
    tests['no_target_stays_to_flatten']=z[0,6]==0 and z[0,2]==956
    z=run({541:(100,111,99,110),956:flat},mode=1,side=-1)
    tests['mirrored_short_market_stop']=z[0,6]==2 and z[0,4]==110
    z=run({541:(91,111,80,110),956:flat},mode=2,side=-1)
    tests['matched_short_trigger_excludes_pre_entry_low']=z[0,3]==100 and z[0,6]==2 and z[0,4]==110
    z=run({541:(91,111,80,110),956:flat},mode=2,side=1)
    tests['matched_long_trigger_phase']=z[0,3]==100 and z[0,6]==0
    z=run({541:(100,101,99,100),956:(85,85,85,85)})
    tests['flatten_open_in_mae']=z[0,8]==15
    assert all(tests.values()),tests
    # Mathematical check: a correctly re-compounded contiguous subperiod
    # cannot have larger relative DD than the encompassing return path.
    rng=np.random.default_rng(2731)
    for _ in range(100):
        r=rng.normal(.05,.8,500)
        eq=np.r_[1,np.cumprod(1+.01*r)]
        dd=lambda a:float((1-a/np.maximum.accumulate(a)).max())
        cut=int(rng.integers(1,450));sub=eq[cut:]/eq[cut]
        assert dd(sub)<=dd(eq)+1e-12
        assert abs(dd(sub)-dd(sub*100000))<1e-12
    tests['compound_subperiod_bound_100_paths']=True
    tests['no_real_data_returns_executed']=True
    # Independent arithmetic mirror of generated PL complete-M30 counter.
    # This checks the intended midnight behavior, not PL compilation/runtime.
    def count_m30(labels):
        previous=None;lastminute=-1;count=0;completed=[]
        for date in labels:
            minute=date.hour*60+date.minute
            if previous is None:count=0
            elif not ((date.date()==previous.date() and minute==lastminute+1) or
                      ((date.normalize()-previous.normalize()).days==1 and lastminute==1439 and minute==0)):
                count=0
            if minute%30==1:count=0
            count+=1
            if minute%30==0:
                if count==30:completed.append(date)
                count=0
            previous=date;lastminute=minute
        return completed
    labels=pd.date_range('2026-01-02 23:31',periods=60,freq='min')
    tests['pl_counter_includes_midnight_bar']=len(count_m30(labels))==2
    tests['pl_counter_rejects_gap_bar']=len(count_m30(labels.delete(14)))==1
    tests={k:bool(v) for k,v in tests.items()}
    out=ROOT/'analysis/outputs/codex_orb30_ema'
    out.mkdir(parents=True,exist_ok=True)
    (out/'independent_synthetic_review.json').write_text(json.dumps(tests,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(tests,indent=2))


if __name__=='__main__':main()
