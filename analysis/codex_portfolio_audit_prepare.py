"""Normalize existing portfolios into native-micro ledgers and Apex-session paths.

No new signal definition or search. Sources are pinned; unsupported paths stay unknown.
"""
import sys
sys.dont_write_bytecode = True
from codex_portfolio_audit_config import *
import gc
import pickle
import subprocess
import numpy as np
import pandas as pd

os.environ.setdefault("NUMBA_CACHE_DIR", str(RUNTIME/"numba"))
os.environ.setdefault("MPLCONFIGDIR", str(RUNTIME/"matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(RUNTIME/"cache"))
sys.path.insert(0, str(SOURCE/"analysis"))
sys.argv = [__file__, str(SCRATCH), "library"]
os.chdir(SOURCE)
assert subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() == SOURCE_COMMIT
subprocess.check_call(["git", "-C", str(ROOT), "cat-file", "-e", PLAN_COMMIT+":agents/codex/plans/portfolio_audit_20261031.md"])
from grid24 import jof
from build_lab import REPORTS

RUNTIME.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
grids = {s: pickle.load(open(SCRATCH/f, "rb")) for s, f in [("NQ", "g24.pkl"), ("ES", "ge.pkl"), ("CL", "cl.pkl")]}
g = grids["NQ"]
days = pd.DatetimeIndex(g.ts[g.trading]); days = days[(days>=START)&(days<=END)]
pos = {d:i for i,d in enumerate(days)}
issues, coverage, inputs, ledgers = [], [], {}, {}


def receipt(relative):
    p = SOURCE/relative
    inputs[relative] = dict(sha256=sha(p), bytes=p.stat().st_size)
    return p


def stamp(date, minute):
    return pd.Timestamp(date).normalize()+pd.Timedelta(minutes=int(minute))


def session(t):
    # A bar closing17:01 first belongs to the new17:00 Apex session.
    t = pd.Timestamp(t)
    return t.normalize()+pd.Timedelta(days=int(t.hour*60+t.minute>1020))


def coord(t):
    return (pd.Timestamp(t).hour*60+pd.Timestamp(t).minute-1021)%1440


def record(key, market, t, source, *, exit_open=False):
    z = t.copy()
    z["key"], z["market"], z["source"] = key, market, source
    if "qty" not in z: z["qty"] = 1.
    if "exit_open" not in z: z["exit_open"] = exit_open
    z["session"] = z.exit_at.map(session)
    z["entry_session"] = z.entry_at.map(session)
    z = z[(z.session>=START)&(z.session<=END)].reset_index(drop=True)
    ledgers[key] = z
    coverage.append(dict(key=key, market=market, source=source, trades=len(z),
                         first_entry=z.entry_at.min(), last_exit=z.exit_at.max()))
    return z


def mc(key, path, *, holiday=None):
    path = str(path); raw = pd.read_excel(receipt(path), sheet_name="List of Trades", header=2)
    en = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    assert len(en)==len(ex)
    st = pd.read_excel(SOURCE/path, sheet_name="Settings", header=None)
    settings = {str(k):str(v) for k,v in zip(st.iloc[:,0], st.iloc[:,1])}
    comp = settings.get("Compression", "5 Minutes")
    bar = int(comp.split()[0]) if "Minute" in comp else 5
    rows=[]
    for i in range(len(en)):
        et, xt = pd.Timestamp(en.Date[i]), pd.Timestamp(ex.Date[i])
        if str(ex.Signal[i]).lower()=="open":
            issues.append(dict(key=key, entry=et, exit=xt, issue="explicit open-position placeholder, not a closed trade")); continue
        if holiday and holiday(et):
            issues.append(dict(key=key, entry=et, exit=xt, issue="excluded by current source's explicit holiday skip")); continue
        side=1 if "Long" in str(en.Type[i]) else -1
        sig=str(ex.Signal[i]); kind=0 if "Stop" in sig else 1 if ("Profit" in sig or "Target" in sig) else 2
        ep, xp = float(en.Price[i]), float(ex.Price[i])
        # Same deterministic first-touch inference as repository portfolio.load_mc, extended across calendar dates.
        a=et-pd.Timedelta(minutes=bar-1); b=xt
        def touch(start, end, price):
            for tm in pd.date_range(start, end, freq="min"):
                d=np.searchsorted(g.dates,int(tm.strftime("%Y%m%d"))); j=tm.hour*60+tm.minute
                if d<g.D and g.dates[d]==int(tm.strftime("%Y%m%d")) and g.l[d,j]-1e-8<=price<=g.h[d,j]+1e-8:
                    return tm, True
            return start, False
        a, matched=touch(a,et,ep)
        if kind!=2: b, xm=touch(max(xt-pd.Timedelta(minutes=bar-1),a),xt,xp)
        else: xm=True
        if not matched or not xm:
            issues.append(dict(key=key,entry=et,exit=xt,issue="report price not touched in inferred chart-bar interval"))
        rows.append(dict(entry_at=a,exit_at=b,side=side,entry=ep,exit=xp,kind=kind,
                         entry_touch=matched,exit_touch=xm,report_entry=et,report_exit=xt))
    record(key,"NQ",pd.DataFrame(rows),path)
    (OUT/(key+"_settings.json")).write_text(json.dumps(settings,indent=2)+"\n")


mapping={"VB":"VB","ONBML":"ONB_ML2_MC","EOS":"EOS","LDF":"LDF_MC","MON":"MON_MC","NFP":"NFP_MC"}
for key,k in mapping.items():
    hol = (lambda t:t.dayofweek==0 and (t.month,t.day) in [(7,3),(12,24)]) if key=="MON" else None
    if key=="NFP":
        from dateutil.easter import easter
        hol=lambda t:t.normalize()==pd.Timestamp(easter(t.year))-pd.Timedelta(days=2)
    mc(key,REPORTS[k][0],holiday=hol)
mc("ONB30","mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx")
mc("BRIDGE","mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx")

flags=pd.read_pickle(SCRATCH/"single_print_sessions.pkl").flag.reindex(days)
unknown_flags=days[flags.isna() & days.isin(ledgers["VB"].session)]
for d in unknown_flags:
    issues.append(dict(key="VB_N/VB_F",entry=d,exit=d,issue="missing single-print size flag on a recorded VB trade day"))
for nm,mask in [("VB_F",flags.eq(True)), ("VB_N",flags.eq(False))]:
    z=ledgers["VB"].copy(); m=z.session.map(mask).fillna(False)
    record(nm,"NQ",z[m],"VB ledger + existing single_print_sessions.pkl")

# Exact existing RS raw ledger; map dates instead of trusting cache row numbers.
rs=pd.read_csv(SCRATCH/"rs_trades.csv",parse_dates=["date"])
rs["entry_at"]=[stamp(d,j) for d,j in zip(rs.date,rs.j0)]
rs["exit_at"]=[stamp(d,j) for d,j in zip(rs.date,rs.j1)]
rs["kind"]=rs.kind.map({"stop":0,"target":1,"flat":2})
record("RS","NQ",rs,"owned cached relative_strength_test fixed-rule ledger")

import dual_thrust_test as DT
dd=DT.load(); dt=DT.run(dd,DT.setups(dd)); del dd
dt["entry_at"]=[stamp(d,jof(h)+1) for d,h in zip(dt.date,dt.sig_time)]
dt["exit_at"]=[stamp(d,jof(h)) for d,h in zip(dt.date,dt.exit_time)]
dt["kind"]=dt.kind.map({"stop":0,"target":1,"flat":2,"close":2})
record("DT","NQ",dt,"analysis/dual_thrust_test.py fixed v4 defaults")

import t_oneside_test as T
tt=T.build(g,T.days(g),stop=True,cells=False);tt=tt[tt.cell=="T"].copy()
tt["entry_at"]=[stamp(d,j) for d,j in zip(tt.date,tt.j0)]
tt["exit_at"]=[stamp(d,j+int(k==2)) for d,j,k in zip(tt.date,tt.j1,tt.kind)]
tt["exit_open"]=tt.kind==2
record("TOS","NQ",tt,"analysis/t_oneside_test.py T-only with existing note stop")

# Existing OT signals; recover native prices and clock from the fixed source rule, not daily extrema proxies.
ot=pd.read_csv(receipt("checks/candidates/overnight_tick/python_trades.csv"),parse_dates=["date"])
oi=[]
for r in ot.itertuples():
    d=np.searchsorted(g.dates,int(r.date.strftime("%Y%m%d")))
    if d>=g.D:continue
    e,x=g.o[d-1,jof(1706)],g.o[d,jof(301)]
    assert np.isclose((x-e-.5)*20-7.25,r.net),"OT fixed-ledger price identity failed"
    oi.append(dict(entry_at=stamp(g.ts[d-1],jof(1706)),exit_at=stamp(g.ts[d],jof(301)),
                   side=1,entry=e,exit=x,kind=2,exit_open=True))
record("OT","NQ",pd.DataFrame(oi),"owned OT signals, source1706-open/0301-open prices",exit_open=True)

# CL existing Sunday up-gap fade. Preserve the original fixed signal and fill algorithm.
cl=grids["CL"];fr=pickle.load(open(SCRATCH/"s_rank_gap2.pkl","rb"))["frames"]["CL"]
O,H,C=cl.o.ravel(),cl.h.ravel(),pd.Series(cl.c.ravel()).ffill().to_numpy();cr=[]
for r in fr.itertuples():
    if not r.ok or not(r.gA>=.1):continue
    a=int(r.sun)*1440+jof(1706);b=int(r.mon)*1440+jof(900)
    if not np.isfinite(O[a]):continue
    e=O[a];sp=e-.01+.75*r.atr;hit=np.where(H[a:b+1]>=sp)[0]
    j=b; x=C[b]; kind=2
    if len(hit):
        j=a+hit[0];x=sp if j==a or not np.isfinite(O[j]) else max(O[j],sp);kind=0
    cr.append(dict(entry_at=stamp(cl.ts[a//1440],a%1440),exit_at=stamp(cl.ts[j//1440],j%1440),
                   side=-1,entry=e,exit=x,kind=kind))
record("CLS","CL",pd.DataFrame(cr),"existing CL Sunday signal frame and fixed bench fill rule")

# ES MOC fixed source rule; unwind its embedded one-tick fills before applying native costs.
import s_rank_es_round1_test as ER
ge=grids["ES"];tr=ge.trading[pd.DatetimeIndex(ge.ts[ge.trading])>=START]
atr=ge.daily_atr(15)[tr];cf=pd.Series(ge.c.ravel()).ffill().to_numpy()
mv=cf[tr*1440+jof(1450)]-cf[tr*1440+jof(1400)]
m=(ge.last_j[tr]>=jof(1500))&(abs(mv)>=.3*atr)&(mv!=0)
mt=ER.trades(ge,tr[m],np.sign(mv[m]).astype(int),jof(1451),jof(1500),.25*atr[m]).reset_index(drop=True)
mt["entry"]-=mt.side*.25;mt["exit"]+=mt.side*.25
mt["entry_at"]=[stamp(d,j) for d,j in zip(mt.date,mt.j0)]
mt["exit_at"]=[stamp(d,j) for d,j in zip(mt.date,mt.j1)]
record("MOC","ES",mt,"existing ES MOC fixed .3ATR trigger/.25ATR stop")


def prices_for_session(grid,d):
    r=np.searchsorted(grid.dates,int(d.strftime("%Y%m%d")))
    if r==0 or r>=grid.D or grid.dates[r]!=int(d.strftime("%Y%m%d")):
        return {c:np.full(1440,np.nan) for c in ["o","h","l","c"]}
    return {c:np.r_[getattr(grid,c)[r-1,1021:],getattr(grid,c)[r,:1021]] for c in ["o","h","l","c"]}


def build_unit(key,z):
    D=len(days);W=np.zeros((D,1440));R=np.zeros_like(W);Q=np.zeros_like(W)
    F=np.zeros_like(W);S=np.zeros_like(W);G=np.zeros(D);N=np.zeros(D);L=np.zeros(D);short=np.zeros(D)
    valid=np.ones(D,bool);known=np.ones(D,bool); rows=[];pv,tick=MARKETS[z.market.iloc[0]]
    if key in ["VB_N","VB_F"]:
        valid[days.isin(unknown_flags)]=False
        known[days.isin(unknown_flags)]=False
    for r in z.itertuples():
        if r.session not in pos:continue
        d=pos[r.session];a,b=coord(r.entry_at),coord(r.exit_at)
        if r.entry_session!=r.session or b<a:
            valid[d]=False;known[d]=False
            if r.entry_session in pos:
                valid[pos[r.entry_session]]=False;known[pos[r.entry_session]]=False
            issues.append(dict(key=key,entry=r.entry_at,exit=r.exit_at,issue="crosses Apex17:00 session; current ledger/source parity unresolved"));continue
        p=prices_for_session(grids[r.market],r.session)
        q=float(r.qty);slips=1+int(r.kind!=1);gross=(r.exit-r.entry)*r.side*pv*q
        trade_fee=q;trade_slip=slips*tick*pv*q
        # W0 contains price risk/gross only. Fee and slippage accumulators are independent, native dollars.
        adverse=p["l"][a:b+1] if r.side>0 else p["h"][a:b+1]
        missing=int((~np.isfinite(adverse)).sum())
        if missing or not np.isfinite(r.entry) or not np.isfinite(r.exit):valid[d]=False
        if not np.isfinite(r.entry) or not np.isfinite(r.exit):known[d]=False
        if hasattr(r,"entry_touch") and (not r.entry_touch or not r.exit_touch):
            valid[d]=False;known[d]=False
        if missing:issues.append(dict(key=key,entry=r.entry_at,exit=r.exit_at,issue="missing held-minute adverse quote",missing=missing))
        path=(np.nan_to_num(adverse,nan=r.entry)-r.entry)*r.side*pv*q
        if r.kind==0 or r.exit_open:path[-1]=gross
        else:path[-1]=min(path[-1],gross)
        W[d,a:b+1]+=path;W[d,b+1:]+=gross
        R[d,b:]+=gross;Q[d,a:b+int(not r.exit_open)]+=r.side*q
        # Half of RT commission each side; cumulative fee factor multiplies the scenario RT fee.
        F[d,a:]+=.5*q;F[d,b:]+=.5*q
        S[d,a:]+=tick*pv*q;S[d,b:]+=(slips-1)*tick*pv*q
        G[d]+=gross;N[d]+=q
        L[d]+=gross if r.side>0 else 0;short[d]+=gross if r.side<0 else 0
        rows.append(dict(key=key,market=r.market,date=r.session,entry_at=r.entry_at,exit_at=r.exit_at,
                         j0=a,j1=b,side=r.side,qty=q,entry=r.entry,exit=r.exit,kind=int(r.kind),
                         gross=gross,fee_units=q,slippage_one_tick=trade_slip,missing_held_bars=missing,
                         exit_after_1559=bool(r.exit_at.hour*60+r.exit_at.minute>959 and r.exit_at.hour<17)))
    np.savez_compressed(RUNTIME/(key+".npz"),W=W,R=R,Q=Q,F=F,S=S,G=G,N=N,L=L,short=short,valid=valid,known=known)
    frame=pd.DataFrame(rows);frame.to_csv(OUT/(key+"_unit_ledger.csv"),index=False)
    print(key,len(frame),"valid sessions",int(valid.sum()),flush=True)
    assert np.allclose(R[:,-1],G)
    assert np.allclose(F[:,-1],N)
    del W,R,Q,F,S;gc.collect()


for k,t in ledgers.items():build_unit(k,t)
np.savez_compressed(RUNTIME/"dates_atr.npz",dates=days.strftime("%Y%m%d").astype(int).to_numpy(),
                    atr=g.daily_atr(15)[np.searchsorted(g.dates,days.strftime("%Y%m%d").astype(int))])
pd.DataFrame(coverage).to_csv(OUT/"source_coverage.csv",index=False)
pd.DataFrame(issues).to_csv(OUT/"coverage_issues.csv",index=False)
dump(OUT/"preparation.json",dict(source_commit=SOURCE_COMMIT,plan_commit=PLAN_COMMIT,first=days[0],last=days[-1],
    sessions=len(days),inputs=inputs,cache_inputs={p:sha(SCRATCH/p) for p in ["g24.pkl","ge.pkl","cl.pkl",
    "rs_trades.csv","s_rank_gap2.pkl","single_print_sessions.pkl"]},
    code={p.name:sha(p) for p in (ROOT/"analysis").glob("codex_portfolio_audit_*.py")},
    limits=["report intrabar first-touch clocks are inferred", "NQ/ES/CL continuous proxies for micro executions",
    "per-strategy adverse extrema are a conservative overlap approximation", "no source certification for missing held bars",
    "current code/report settings and holiday parity need independent review"] ))
