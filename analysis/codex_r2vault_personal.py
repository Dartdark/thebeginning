"""R2Vault fill-specific MTM and all21 frozen personal comparisons (a973f07).

Extends existing personal benchmark only for stop-entry/limit-exit costs,
intraminute timestamps and terminal open positions. No market data at import.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pickle
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"agents/codex/runtime/or_pullback_python"))
sys.path.insert(0,str(ROOT/"analysis"))
import numpy as np
import pandas as pd
import codex_anson_personal as P

PREREG="a973f0779b6e10d9c3c29adc6748ed5eba0d5f92"
OUT=ROOT/"analysis/outputs/codex_r2vault/personal"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def authorize():
    subprocess.run(["git","-C",str(ROOT),"cat-file","-e",PREREG+":agents/codex/plans/r2vault.md"],check=True)


def is_open_phase(phase):
    return str(phase).lower() in ("open","0","0.0")


def event_time(g,row,j,phase="open"):
    # Any intraminute phase is later than its open; fraction is only used to
    # resolve the16:00 session boundary, not to fabricate tick timestamps.
    return pd.Timestamp(g.ts[int(row)])+pd.Timedelta(minutes=int(j)-1,seconds=0 if is_open_phase(phase) else 30)


def session_index(days,stamp):
    stamp=pd.Timestamp(stamp)
    date=stamp.normalize()
    if stamp>date+pd.Timedelta(hours=16):
        date+=pd.Timedelta(days=1)
    k=int(days.searchsorted(date))
    if k>=len(days):
        raise ValueError("Event falls after benchmark session calendar")
    return k


def target_exit(reason):
    return str(reason).lower() in ("target","tp","profit_target","limit")


def candidate_daily(g,trades,days,fee=1.275,open_positions=None):
    """Book observed16CT marks, entry-reserved RTfee and variable exit slip.

    All prices stay raw. Last personal session ends at its observed16CTclose;
    positions exiting later are valued there as unrealized, not liquidated.
    Returned total reconciles closed fills and this terminal valuation.
    """
    days=pd.DatetimeIndex(days)
    if not days.is_monotonic_increasing or days.has_duplicates:
        raise ValueError("Invalid benchmark calendar")
    cutoff=days[-1].normalize()+pd.Timedelta(hours=16)
    row_lookup={pd.Timestamp(d).normalize():i for i,d in enumerate(g.ts)}
    out=np.zeros(len(days))
    records=[]
    items=[(r,False) for r in trades.to_dict("records")]
    if open_positions is not None and len(open_positions):
        items.extend((r,True) for r in open_positions.to_dict("records"))
    expected=0.
    nclosed=nterminal=nignored=0
    for no,(t,unclosed) in enumerate(items):
        er,ej=int(t.get("entry_row",t.get("day",-1))),int(t["entry_j"])
        et=event_time(g,er,ej,t.get("entry_phase","open"))
        if et>cutoff:
            nignored+=1
            continue
        entry=float(t["entry"])
        side=int(t.get("side",1))
        actual_exit=None
        if not unclosed:
            xr,xj=int(t.get("exit_row",t.get("day",-1))),int(t["exit_j"])
            actual_exit=event_time(g,xr,xj,t.get("exit_phase","open"))
            if actual_exit<et:
                raise ValueError("Exit before entry")
        closed=actual_exit is not None and actual_exit<=cutoff
        if closed:
            endstamp=actual_exit
            endpoint=float(t["exit"])
            reason=t.get("exit_reason",t.get("reason",""))
            is_target=target_exit(reason) or (not reason and int(t.get("kind",-1))==1)
            exit_slip=0. if is_target else .5
            nclosed+=1
        else:
            # The endpoint must be observed before the benchmark ends. Search
            # backward, preserving stale marks and never borrowing a later bar.
            endstamp=endpoint=None
            for date in reversed(days):
                row=row_lookup.get(date.normalize())
                if row is None:
                    continue
                js=np.flatnonzero(np.isfinite(g.c[row,:961]))
                if len(js):
                    j=int(js[-1])
                    markstamp=pd.Timestamp(g.ts[row])+pd.Timedelta(minutes=j)
                    if markstamp>et:
                        endstamp,endpoint=markstamp,float(g.c[row,j])
                        break
            if endpoint is None:
                # An entry exactly at terminal16open has no subsequent close;
                # book entry price and known incurred cost, no invented move.
                endstamp,endpoint=et,entry
            exit_slip=0.
            nterminal+=1
        a,b=session_index(days,et),session_index(days,endstamp)
        out[a]-=float(fee)+.5
        last=entry
        for k in range(a,b):
            date=days[k]
            row=row_lookup.get(date.normalize())
            if row is None:
                records.append(dict(trade_index=no,date=str(date.date()),status="no_calendar_row"))
                continue
            js=np.flatnonzero(np.isfinite(g.c[row,:961]))
            if not len(js):
                records.append(dict(trade_index=no,date=str(date.date()),status="no_observed_close_at_or_before16"))
                continue
            j=int(js[-1])
            stamp=pd.Timestamp(g.ts[row])+pd.Timedelta(minutes=j)
            if stamp<=et or stamp>=endstamp:
                continue
            price=float(g.c[row,j])
            money=(price-last)*side*2.
            out[k]+=money
            records.append(dict(trade_index=no,date=str(date.date()),status="observed_mark",mark_j=j,
                                minutes_before16=960-j,price=price,pnl_micro=money))
            last=price
        out[b]+=(endpoint-last)*side*2.-exit_slip
        expected+=(endpoint-entry)*side*2.-fee-.5-exit_slip
        records.append(dict(trade_index=no,date=str(days[b].date()),status="executed_exit" if closed else "terminal_unrealized",
                            price=endpoint,entry_cost_session=str(days[a].date()),exit_slippage=exit_slip))
    np.testing.assert_allclose(out.sum(),expected,rtol=0,atol=1e-6)
    return pd.Series(out,index=days,name="R2Vault"),pd.DataFrame(records),dict(
        closed_trades=nclosed,terminal_valuations=nterminal,entries_after_calendar=nignored,
        net_sum=float(out.sum()),expected_net=float(expected),roundtrip_fee_reserved_at_entry=fee,
        entry_slippage=.5,target_exit_slippage=0.,other_exit_slippage=.5,
        terminal_calendar_cutoff=str(cutoff),mark_rule="last observed close<=16CT; no later price substitution",
        boundary_rule="openj961 belongs oldsession; intraminutej961 belongs nextsession")


def fixtures():
    ts=pd.date_range("2026-10-02",periods=4,freq="D")
    g=SimpleNamespace(ts=ts.to_numpy(),c=np.full((4,1440),np.nan))
    g.c[0,960]=105.
    g.c[0,961]=999.
    g.c[3,960]=109.
    days=pd.DatetimeIndex([ts[0],ts[3]])
    t=pd.DataFrame([dict(entry_row=0,exit_row=3,entry_j=600,exit_j=600,entry=100.,exit=110.,
                         side=1,exit_reason="target",entry_phase="intra",exit_phase="intra")])
    x,marks,_=candidate_daily(g,t,days)
    np.testing.assert_allclose(x,[8.225,10.],rtol=0,atol=1e-12)
    assert 999. not in marks.price.to_list()
    t["exit_reason"]="stop"
    x,_,_=candidate_daily(g,t,days)
    np.testing.assert_allclose(x,[8.225,9.5],rtol=0,atol=1e-12)
    assert session_index(days,event_time(g,0,961,"open"))==0
    assert session_index(days,event_time(g,0,961,"intra"))==1
    boundary=t.copy()
    boundary.loc[0,["entry_j","entry_phase","exit_reason"]]=[961,"open","target"]
    x,_,_=candidate_daily(g,boundary,days)
    np.testing.assert_allclose(x,[-1.775,20.],rtol=0,atol=1e-12)
    boundary.loc[0,"entry_phase"]="intrabar"
    x,_,_=candidate_daily(g,boundary,days)
    np.testing.assert_allclose(x,[0.,18.225],rtol=0,atol=1e-12)
    opened=t.drop(columns=["exit","exit_row","exit_j","exit_reason","exit_phase"])
    x,_,audit=candidate_daily(g,t.iloc[:0],days,open_positions=opened)
    np.testing.assert_allclose(x,[8.225,8.],rtol=0,atol=1e-12)
    assert audit["terminal_valuations"]==1
    return dict(no_future_price_mark=True,closure_carry=True,stop_vs_limit_cost=True,
                phase_aware16boundary=True,terminal_unrealized_reconciles=True,fee_reserved_at_entry=True)


def joint_losses(frame,candidate):
    """Daily diversification description; no claim about pre-breach offsets."""
    rows=[]
    sets={**P.STARTERS,"FULL":list(frame.columns),"VB":["VaultBreak"]}
    for period,lo,hi in (("2018_22","2018-01-01","2023-01-01"),
                         ("2023_plus","2023-01-01","2100-01-01"),
                         ("2025_plus","2025-01-01","2100-01-01"),
                         ("2018_plus","2018-01-01","2100-01-01")):
        mask=(frame.index>=lo)&(frame.index<hi)
        x=candidate[mask]
        for name,keys in sets.items():
            b=frame.loc[mask,keys].sum(axis=1)
            joint=(x<0)&(b<0)
            rows.append(dict(period=period,baseline=name,days=len(x),correlation=x.corr(b),
                candidate_nonzero_days=int((x!=0).sum()),base_negative_days=int((b<0).sum()),
                joint_negative_days=int(joint.sum()),candidate_sum_on_base_negative=float(x[b<0].sum()),
                candidate_sum_on_joint_negative=float(x[joint].sum()),
                baseline_sum_on_joint_negative=float(b[joint].sum()),
                timing_scope="16CTdaily marks; no inference that offsets precede intraday breach"))
    return pd.DataFrame(rows)


def run(args):
    authorize()
    OUT.mkdir(parents=True,exist_ok=True)
    fixture=fixtures()
    with open(ROOT/"agents/codex/runtime/anson_personal_baseline.pkl","rb") as f:
        frame=pickle.load(f)
    reference=P.baseline_reference(frame)
    if not reference["rounding_match"]:
        raise ValueError("Baseline does not reconcile")
    with open(ROOT/"scratch_data/g24.pkl","rb") as f:
        g=pickle.load(f)
    manifest=dict(preregistration=PREREG,baseline_reference=reference,fixtures=fixture,
                  baseline_cache_sha256=sha(ROOT/"agents/codex/runtime/anson_personal_baseline.pkl"),
                  context_inventory_sha256=sha(ROOT/"analysis/outputs/codex_r2vault/context_inventory.json"),
                  inherited_limitations=P.LIMITATIONS,models={})
    for name in args.models.split(","):
        ledger=ROOT/"analysis/outputs/codex_r2vault/replay"/(name+"_trades.csv")
        t=pd.read_csv(ledger)
        op=ledger.with_name(name+"_open_positions.csv")
        opened=pd.read_csv(op) if op.exists() and op.stat().st_size>2 else None
        dest=OUT/name
        dest.mkdir(exist_ok=True)
        candidate,marks,money=candidate_daily(g,t,frame.index,open_positions=opened)
        candidate.to_csv(dest/"candidate_daily.csv",index_label="date")
        marks.to_csv(dest/"marks.csv",index=False)
        joint_losses(frame,candidate).to_csv(dest/"joint_losses.csv",index=False)
        money.update(ledger_sha256=sha(ledger),model=name)
        (dest/"mark_manifest.json").write_text(json.dumps(money,indent=2)+"\n")
        manifest["models"][name]=money
        if name in ("et_raw","ct_raw") and not args.marks_only:
            print("Personal21configs starting "+name,flush=True)
            P.benchmark(frame,candidate,dest)
            print("Personal21configs complete "+name,flush=True)
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--models",default="et_raw,ct_raw,et_apex,ct_apex,et_daily_reset_raw")
    ap.add_argument("--marks-only",action="store_true")
    run(ap.parse_args())
