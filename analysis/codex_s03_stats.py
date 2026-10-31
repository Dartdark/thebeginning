"""Standard metrics and frozen gates for already authorized S03 profile ledgers.

Does not run strategies or open a later period. Price cache is read only for
the established common calendar. Separate intraday audits gate account work.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pickle

import numpy as np
import pandas as pd

import metrics as M

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_s03_noisearea"
PREREG = "d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad"
PLAN_SHA = "ec135137d244afc7d24ca53f62bc77936e07d5e64259757d85dcc20ce3d2d879"
PROFILES = ("V2", "V1", "C2", "E2")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()


def clean(v):
    if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [clean(x) for x in v]
    if isinstance(v,np.integer):return int(v)
    if isinstance(v,(float,np.floating)):return float(v) if np.isfinite(v) else None
    if isinstance(v,np.bool_):return bool(v)
    if isinstance(v,(Path,pd.Timestamp)):return str(v)
    return v


def dump(path,value):
    Path(path).write_text(json.dumps(clean(value),indent=2,allow_nan=False)+"\n")


def tstat(x):
    x=np.asarray(x,float)
    return float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std(ddof=1)>0 else np.nan


def daily(t,dates):
    if not (t.day==t.exit_day).all():
        raise ValueError("Cross-date trade requires explicit MTM, not exit-day grouping")
    d=t.assign(date=pd.to_datetime(t.date)).groupby("date").net.sum().reindex(dates,fill_value=0.0)
    if not np.isclose(d.sum(),t.net.sum(),atol=1e-6):
        raise ValueError("Daily/calendar/trade mismatch; trade may fall outside canonical calendar")
    return d


def summarize(stage,out=OUT):
    if stage not in ("design","recent"):raise ValueError(stage)
    with (ROOT/"scratch_data/g24.pkl").open("rb") as f:g=pickle.load(f)
    lo,hi=(2018,2022) if stage=="design" else (2023,2026)
    idx=pd.DatetimeIndex(g.ts[g.trading]);idx=idx[(idx.year>=lo)&(idx.year<=hi)]
    rows,years,ledgers,audits=[],[],{},{}
    for p in PROFILES:
        t=pd.read_csv(out/f"{stage}_{p}.csv")
        ledgers[p]=t
        audits[p]=json.loads((out/f"{stage}_{p}_audit.json").read_text())
        for name,tt in (("whole",t),("long",t[t.side>0]),("short",t[t.side<0])):
            d=daily(tt,idx);d.rename("net_NQ").to_csv(out/f"{stage}_{p}_{name}_daily.csv",index_label="date")
            m=M.perf(d,tt.net);m.update(profile=p,period=stage,side=name,net=tt.net.sum(),
                t=tstat(tt.net),gross=tt.pnl.sum(),commission=7.25*len(tt),slippage=tt.slippage_usd.sum(),
                unknown_held_minutes=int(tt.unknown_held_minutes.sum()),
                subminute_stops=int(((tt.j0==tt.j1)&(tt.kind==0)).sum()))
            rows.append(m)
            dates=pd.to_datetime(tt.date)
            for year in range(lo,hi+1):
                sub=tt[dates.dt.year==year];dd=d[d.index.year==year]
                m=M.perf(dd,sub.net);m.update(profile=p,period=stage,side=name,year=year,
                    net=sub.net.sum(),t=tstat(sub.net))
                years.append(m)
        recon=(t.raw_exit-t.raw_entry)*t.side*20-7.25-t.slippage_usd
        np.testing.assert_allclose(recon,t.net,rtol=0,atol=1e-7)
    frame,annual=pd.DataFrame(rows),pd.DataFrame(years)
    frame.to_csv(out/f"{stage}_metrics.csv",index=False)
    annual.to_csv(out/f"{stage}_yearly.csv",index=False)
    if stage=="design":
        t=ledgers["V2"];a=audits["V2"]
        y=annual[(annual.profile=="V2")&(annual.side=="whole")]
        c=a.get("censored",[])
        nc=len(c) if isinstance(c,list) else int(a.get("censored_positions",0))
        checks=dict(minimum100=len(t)>=100,net_positive=t.net.sum()>0,t_at_least2=tstat(t.net)>=2,
            three_positive_years=(y.net>0).sum()>=3,stress_positive=ledgers["E2"].net.sum()>0,
            zero_censoring=nc==0)
        gate=dict(preregistration_commit=PREREG,prereg_commit=PREREG,prereg_sha=PREREG,
            prereg_sha256=PLAN_SHA,candidate="S03NoiseArea_v2",checks=checks,
            statistical_conditions_passed=all(checks.values()),implementation_checks_clear=False,
            design_gate_passed=False,passed=False,status="PENDING_INDEPENDENT_CHECK",
            account_run_authorized=False,allow_personal=False,
            note="Independent design audit must clear before opening recent history; account gates separate.")
        dump(out/"design_gate.json",gate)
    dump(out/f"{stage}_summary.json",dict(prereg=PREREG,metrics=rows,yearly=years,audits=audits,
        daily_trade_reconciliation=True,source_parity="Declared reconstruction; no tick/author-engine confirmation"))
    print(frame[frame.side=="whole"][["profile","trades","avg","net","t","profit_factor","max_dd","unknown_held_minutes"]].to_string(index=False))
    print(annual[(annual.profile=="V2")&(annual.side=="whole")][["year","trades","net","t"]].to_string(index=False))
    if stage=="design":print((out/"design_gate.json").read_text())


def certify_design(out=OUT):
    path=out/"design_gate.json"
    g=json.loads(path.read_text())
    p=out/"diagnostics_design/diagnostics_summary.json"
    a=json.loads(p.read_text())
    if g["preregistration_commit"]!=PREREG or a["prereg_commit"]!=PREREG:
        raise ValueError("Preregistration mismatch")
    if not all(g["checks"].values()) or not a["all_independent_audits_passed"]:
        raise PermissionError("Frozen design conditions/checker fail")
    g.update(implementation_checks_clear=True,design_gate_passed=True,passed=True,status="PASS",
        independent_design_audit=str(p.relative_to(ROOT)),independent_design_audit_sha256=digest(p),
        note="Frozen statistical design gate and independent all-feature/trade audit pass. Stop improvement, placebos and account path eligibility are separate tests; no rule retuning.")
    dump(path,g)
    print("Design gate certified; account permissions remain false")


def account_gate(out=OUT):
    g=json.loads((out/"design_gate.json").read_text())
    tables=[pd.read_csv(out/f"{s}_V2.csv").assign(stage=s) for s in ("design","recent")]
    t=pd.concat(tables,ignore_index=True)
    t.to_csv(out/"candidate_V2.csv",index=False)
    gaps=pd.concat([pd.read_csv(out/f"{s}_V2_unknown_held_minutes.csv").assign(stage=s)
                    for s in ("design","recent")],ignore_index=True)
    gaps.to_csv(out/"candidate_held_gaps.csv",index=False)
    days=pd.concat([pd.read_csv(out/f"{s}_V2_day_audit.csv").assign(stage=s)
                    for s in ("design","recent")],ignore_index=True)
    missing=days[(days.calendar_kind=="normal")&(days.missing_cash_minutes>0)]
    missing.to_csv(out/"candidate_normal_calendar_gaps.csv",index=False)
    audits=[json.loads((out/f"{s}_V2_audit.json").read_text()) for s in ("design","recent")]
    counts=dict(censored_positions=sum(a["censored_position_count"] for a in audits),
        unknown_held_minutes=len(gaps),unknown_account_days=gaps.date.nunique(),
        unknown_held_dates=gaps.date.nunique(),
        apex_carry_violations=int(t.carry.sum()),unmatched_orders=sum(a["unmatched_order_count"] for a in audits),
        delayed_orders=sum(a["delayed_order_count"] for a in audits),
        calendar_unknown_native_minutes=int(missing.missing_cash_minutes.sum()),
        calendar_missing_native_minutes=int(missing.missing_cash_minutes.sum()),
        normal_calendar_gap_dates=len(missing),normal_no_cash_dates=int(missing.no_cash_data.sum()))
    recent=t[t.stage=="recent"]
    # The frozen VWAP explicitly permits flat, nonscheduled-minute gaps.
    # Do not turn those into a stricter post-return rule. Mandatory decision /
    # entire-session gaps and unknown held prices remain hard blockers.
    structural_path=out/"accounts/native_coverage_audit.json"
    structural=json.loads(structural_path.read_text()) if structural_path.exists() else None
    if structural:
        fatal=[d for d in structural["days"] if d["classification"] in (
            "missing_scheduled_decision_unclassified_closure","missing_entire_normal_cash_session")]
        fatal_dates={d["date"] for d in fatal}
        counts["unknown_account_days"]=len(fatal_dates|set(gaps.date))
        counts["source_calendar_blocking_dates"]=len(fatal)
        counts["flat_nonscheduled_gap_dates_allowed"]=structural["classification_counts"].get(
            "flat_nondecision_gap_observed_only_VWAP_allowed",0)
        counts["calendar_unknown_native_minutes"]=int(missing[missing.date.isin(fatal_dates)].missing_cash_minutes.sum())
        full=not fatal and not structural["omitted_weekday_dates"]
    else:
        full=counts["normal_no_cash_dates"]==0 and len(missing)==0
    eligible=bool(g["design_gate_passed"] and recent.net.sum()>0 and full and
                  counts["censored_positions"]==0 and counts["apex_carry_violations"]==0 and
                  counts["unmatched_orders"]==0)
    audit=dict(preregistration_commit=PREREG,prereg_sha256=PLAN_SHA,trades=len(t),
        all_native_dates_covered=True,full_calendar_complete=full,personal_path_eligible=eligible,
        complete=eligible,execution_rule_reconciliation=True,**counts,
        gap_note="Full-price path and input coverage are distinct from matching the observed-bar replay. Calendar gap classifications are refined in accounts/native_coverage_audit.json; observed held gaps alone block this gate.",
        held_gap_dates=sorted(gaps.date.unique().tolist()),
        ledger_sha256=digest(out/"candidate_V2.csv"),strategy_returns_altered=False)
    dump(out/"candidate_audit.json",audit)
    gate=dict(status="PASS" if eligible else "BLOCKED_DATA",candidate="S03NoiseArea_v2",
        preregistration_commit=PREREG,prereg_sha256=PLAN_SHA,
        design_gate_passed=bool(g["design_gate_passed"]),implementation_checks_clear=True,
        recent_net_positive=bool(recent.net.sum()>0),account_run_authorized=eligible,allow_personal=eligible,
        full_calendar_complete=full,all_native_dates_covered=True,**counts,
        candidate_ledger_sha256=digest(out/"candidate_V2.csv"),candidate_audit_sha256=digest(out/"candidate_audit.json"),
        account_simulations_run=0,personal_simulations_run=0,
        blocked_reason=None if eligible else "Registered Stage3 requires zero unknown held prices and complete source calendar; no imputation or trade removal.")
    dump(out/"candidate_gate.json",gate)
    print(json.dumps(clean(gate),indent=2))


def finalize(out=OUT):
    context=json.loads((ROOT/"agents/codex/inputs/s03_noisearea/trials_context.json").read_text())
    n=context["ranked_items_before_test"]+1
    rows=[]
    for profile in PROFILES:
        t=pd.concat([pd.read_csv(out/f"{s}_{profile}.csv") for s in ("design","recent")],ignore_index=True)
        date=pd.to_datetime(t.date)
        for side,sign in (("whole",0),("long",1),("short",-1)):
            tt=t if sign==0 else t[t.side==sign]
            dd=pd.concat([pd.read_csv(out/f"{s}_{profile}_{side}_daily.csv",index_col=0,parse_dates=True).iloc[:,0]
                          for s in ("design","recent")]).sort_index()
            for label,mask in (("2018_plus",np.ones(len(tt),bool)),
                    ("design",pd.to_datetime(tt.date).dt.year<=2022),
                    ("recent",pd.to_datetime(tt.date).dt.year>=2023),
                    ("post_source_extension",pd.to_datetime(tt.date)>=pd.Timestamp("2026-07-08"))):
                sub=tt[mask]
                if label=="design":ds=dd[dd.index.year<=2022]
                elif label=="recent":ds=dd[dd.index.year>=2023]
                elif label=="post_source_extension":ds=dd[dd.index>="2026-07-08"]
                else:ds=dd
                m=M.perf(ds,sub.net)
                m.update(profile=profile,side=side,period=label,net=sub.net.sum(),t=tstat(sub.net),
                    dsr=M.deflated_sharpe(sub.net,n) if len(sub)>=10 else None,
                    dsr_four_profile_sensitivity=M.deflated_sharpe(sub.net,n+3) if len(sub)>=10 else None,
                    t_bar=M.t_threshold(n))
                rows.append(m)
    pd.DataFrame(rows).to_csv(out/"all_metrics.csv",index=False)
    ledger=[]
    for p in PROFILES:
        for stage in ("design","recent"):
            x=pd.read_csv(out/f"{stage}_{p}.csv")
            ledger.append(dict(profile=p,stage=stage,prereg_commit=PREREG,selected_before_returns=p=="V2",
                trades=len(x),net=x.net.sum(),rule_or_parameter_changed=False,
                source_selection_warning="Author supplied at least12 previous stop variants; this is seen-history replication"))
    pd.DataFrame(ledger).to_csv(out/"trial_ledger.csv",index=False)
    # Prespecified actual/stress micro fees applied to the SAME observed
    # candidate fills; this is arithmetic, not a funded/personal simulation.
    t=pd.concat([pd.read_csv(out/f"{s}_V2.csv") for s in ("design","recent")],ignore_index=True)
    costs=[]
    for fee in (1.04,1.24):
        for label,mask in (("2018_plus",np.ones(len(t),bool)),
                ("design",pd.to_datetime(t.date).dt.year<=2022),
                ("recent",pd.to_datetime(t.date).dt.year>=2023)):
            tt=t[mask]
            for side,sub in (("whole",tt),("long",tt[tt.side>0]),("short",tt[tt.side<0])):
                x=sub.net/10+0.725-fee
                gp,gl=x.clip(lower=0).sum(),-x.clip(upper=0).sum()
                costs.append(dict(profile="V2",period=label,side=side,fee_MNQ_RT=fee,
                    quantity_MNQ=1,trades=len(x),net_MNQ=x.sum(),avg_MNQ=x.mean(),t=tstat(x),
                    profit_factor=gp/gl if gl>0 else None,
                    method="Existing research net/10 + original .725 fee credit - actual micro fee; slippage retained; no account simulation"))
    pd.DataFrame(costs).to_csv(out/"candidate_micro_fee_sensitivity.csv",index=False)
    print(pd.DataFrame(rows).query("profile=='V2' and side=='whole'")[["period","trades","net","avg","t","dsr","profit_factor","max_dd"]].to_string(index=False))
    print(pd.DataFrame(costs).query("period=='recent' and side=='whole'")[["fee_MNQ_RT","avg_MNQ","t","profit_factor"]].to_string(index=False))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage",choices=("design","recent"))
    p.add_argument("--out",type=Path,default=OUT)
    p.add_argument("--certify-design",action="store_true")
    p.add_argument("--account-gate",action="store_true")
    p.add_argument("--finalize",action="store_true")
    a=p.parse_args()
    if a.certify_design:certify_design(a.out)
    elif a.account_gate:account_gate(a.out)
    elif a.finalize:finalize(a.out)
    elif a.stage:summarize(a.stage,a.out)
    else:p.error("Select stage or gate/finalization action")


if __name__=="__main__":main()
