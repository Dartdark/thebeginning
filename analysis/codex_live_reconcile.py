"""Offline chart/user/broker reconciliation prototype; never writes live files or sends alerts.

Default audit pins e097c0f. Optional expected/broker CSVs must contain verified canonical account/strategy IDs,
symbol, entry_time, exit_time, side (+1/-1), qty, entry, exit; prices/times are actual, not chart bar labels.
--coverage-complete explicitly declares both optional files complete for the compared dates/accounts/strategies.
Absent that declaration, unmatched rows are unresolved, never automatically missed/extra.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

COLS = ["event","tag","symbol","side","contracts","entry_date","entry_time","entry_price",
        "exit_date","exit_time","exit_price","profit_usd","bar_date","bar_time"]
REPORTS = {
    "VB": "mc_reports/Backtesting Strategy Performance Report VB v1.xlsx",
    "ONB": "mc_reports/Backtesting Strategy Performance Report ONB v2.xlsx",
    "EOS": "mc_reports/Backtesting Strategy Performance Report EOS v1.xlsx",
    "MON_BR": "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx",
}
OPEN_KEY = ["tag","symbol","side","contracts","entry_date","entry_time","entry_price"]


def blob(ref, path):
    return subprocess.check_output(["git","show",f"{ref}:{path}"], stderr=subprocess.PIPE)


def json_write(path, obj):
    path.write_text(json.dumps(obj, indent=2, default=str)+"\n")


def identity(tag):
    base, _, suffix = str(tag).partition("-")
    return base, suffix or "1"  # user labels only; NOT verified broker account IDs


def normalized(path):
    x = pd.read_csv(path)
    required = ["account","strategy","symbol","entry_time","exit_time","side","qty","entry","exit"]
    if not set(required).issubset(x):
        raise ValueError(f"Canonical CSV needs {required}")
    for k in ("account","strategy","symbol"):
        x[k] = x[k].astype(str)
    for k in ("entry_time","exit_time"):
        x[k] = pd.to_datetime(x[k])
    assert x.side.isin([-1,1]).all() and (x.qty>0).all()
    x["pts"] = (x.exit-x.entry)*x.side
    x["session"] = (x.entry_time+pd.to_timedelta((x.entry_time.dt.hour>=16).astype(int),unit="D")).dt.normalize()
    x["exit_signal"] = "verified_input"
    x["signal"] = "verified_input"
    keys = ["account","strategy","symbol","entry_time","side"]
    if x.duplicated(keys).any():
        raise ValueError("Ambiguous execution keys: aggregate partial fills into round trips with order IDs first")
    return x


def canonical_comparison(expected, broker, complete, out):
    """Date-local extension of live_vs_backtest.compare retaining fully missed dates/account scope."""
    e, b = normalized(expected), normalized(broker)
    rows = []
    keys = ["account","strategy","symbol"]
    for key in sorted(set(map(tuple,e[keys].to_numpy()))|set(map(tuple,b[keys].to_numpy()))):
        ex = e[(e[keys]==key).all(axis=1)].copy()
        br = b[(b[keys]==key).all(axis=1)].copy()
        if ex.empty or br.empty:
            for source, group in (("expected",ex),("broker",br)):
                for r in group.itertuples():
                    rows.append(dict(zip(keys,key),status=("missed" if source=="expected" else "extra") if complete else "unresolved_incomplete_coverage",
                                     entry_time=r.entry_time, entry_slip_ticks=np.nan, exit_slip_ticks=np.nan))
            continue
        # compare() normally limits to broker min/max dates. Widen explicitly to the expected span using
        # date-local matching instead, retaining empty broker days under the coverage declaration.
        used = set()
        for i, r in br.iterrows():
            candidate = ex[(ex.session==r.session)&(ex.side==r.side)&~ex.index.isin(used)]
            if len(candidate):
                gap = (candidate.entry_time-r.entry_time).abs()
                j = gap.idxmin()
                if gap[j]<=pd.Timedelta(minutes=15):
                    used.add(j); z=ex.loc[j]
                    tick = float(r.get("tick_size",.25)); pv=float(r.get("point_value",2.))
                    # Price multipliers are supplied/declared; never silently apply MNQ to other markets.
                    if r.symbol not in ("MNQ","NQ","MES","ES") and ("point_value" not in br or "tick_size" not in br):
                        raise ValueError("Non-equity contracts need explicit point_value and tick_size")
                    pv = float(r.get("point_value",{"MNQ":2.,"NQ":20.,"MES":5.,"ES":50.}.get(r.symbol, pv)))
                    rows.append(dict(zip(keys,key), status="wrong_size" if r.qty!=z.qty else "matched",
                                     entry_time=r.entry_time, expected_entry_time=z.entry_time, broker_qty=r.qty, expected_qty=z.qty,
                                     entry_slip_ticks=r.side*(r.entry-z.entry)/tick, exit_slip_ticks=r.side*(z.exit-r.exit)/tick,
                                     broker_gross=r.pts*pv*r.qty, expected_gross=z.pts*pv*z.qty,
                                     gross_difference=r.pts*pv*r.qty-z.pts*pv*z.qty,
                                     timing_difference_minutes=(r.entry_time-z.entry_time).total_seconds()/60))
                    continue
            rows.append(dict(zip(keys,key),status="extra" if complete else "unresolved_incomplete_coverage",entry_time=r.entry_time))
        for j,z in ex.iterrows():
            if j not in used:
                rows.append(dict(zip(keys,key),status="missed" if complete else "unresolved_incomplete_coverage",entry_time=z.entry_time))
    pd.DataFrame(rows).to_csv(out/"verified_execution_comparison.csv",index=False)


def audit(ref, out):
    out.mkdir(parents=True,exist_ok=True)
    paths = subprocess.check_output(["git","ls-tree","-r","--name-only",ref],text=True).splitlines()
    trade_files = [p for p in paths if p.startswith("live/trades/") and p.endswith(".csv")]
    hashes = {}; source_rows=[]; data=[]
    for path in trade_files:
        b=blob(ref,path);hashes[path]=hashlib.sha256(b).hexdigest()
        x=pd.read_csv(io.BytesIO(b),header=None,names=COLS,dtype=str,keep_default_na=False)
        x["file"]=path;x["source_row"]=np.arange(1,len(x)+1)
        source_rows.append(dict(path=path,rows=len(x),exact_duplicates=int(x[COLS].duplicated().sum()),**x.event.value_counts().to_dict()))
        data.append(x)
    log=pd.concat(data,ignore_index=True)
    log["strategy"]=[identity(t)[0] for t in log.tag]
    log["account_label"]=[identity(t)[1] for t in log.tag]
    closed=log[log.event=="CLOSE"].drop_duplicates(COLS).copy()
    closed["chart_points"]=(closed.exit_price.astype(float)-closed.entry_price.astype(float))*np.where(closed.side=="long",1,-1)
    closed["chart_gross_usd"]=closed.profit_usd.astype(float)
    closed["broker_fill_price"]=np.nan;closed["entry_slippage_ticks"]=np.nan;closed["backtest_gross_usd"]=np.nan
    closed["classification"]="CHART_ONLY_UNVERIFIED"
    confirmed_scope=closed.strategy.eq("VB") & closed.account_label.isin(["1","2"])
    closed.loc[confirmed_scope & closed.bar_date.eq("20261020"),"classification"]="MISSED_USER_CONFIRMED_NO_FILL"
    closed.loc[confirmed_scope & closed.bar_date.eq("20261021"),"classification"]="FILLED_USER_CONFIRMED_DAY_ONLY"
    closed["execution_evidence"]="chart strategy ledger; user confirms day status; no broker execution export"
    closed.to_csv(out/"chart_trade_audit.csv",index=False)
    opened=log[log.event=="OPEN"]
    logical=opened.groupby(OPEN_KEY,dropna=False).size().rename("raw_open_rows").reset_index()
    logical["duplicate_open_notifications"]=logical.raw_open_rows-1
    logical.to_csv(out/"open_notification_audit.csv",index=False)
    pos=log[log.event=="POS"].copy()
    pos["strategy_qty"]=pos.contracts.astype(float);pos["broker_qty"]=pos.profit_usd.astype(float)
    pos["mismatch"]=pos.strategy_qty!=pos.broker_qty
    states=[]
    for key,g in pos.groupby(["bar_date","tag","bar_time"],sort=False):
        if not g.mismatch.any():continue
        r=g.iloc[-1]
        states.append(dict(day=key[0],tag=key[1],bar_time=key[2],raw_mismatch_rows=int(g.mismatch.sum()),
                           terminal_strategy_qty=r.strategy_qty,terminal_broker_qty=r.broker_qty,
                           resolved_in_same_bar=not bool(r.mismatch),
                           status="transient_resolved; elapsed seconds unknown" if not r.mismatch else "unresolved; requires broker/account confirmation"))
    pd.DataFrame(states).to_csv(out/"position_mismatch_audit.csv",index=False)
    pos.groupby(["bar_date","tag"],sort=False).tail(1).to_csv(out/"last_position_rows.csv",index=False)
    coverage=[]
    for day in pd.bdate_range("2026-10-12","2026-10-21"):
        stamp=day.strftime("%Y%m%d")
        for account in (["1","2"] if day>=pd.Timestamp("2026-10-20") else ["1"]):
            for strategy in REPORTS:
                x=log[(log.bar_date==stamp)&(log.account_label==account)&(log.strategy==strategy)]
                journal=f"journal/daily/{day.date()}.md"
                coverage.append(dict(date=str(day.date()),account_label=account,strategy=strategy,
                                     log_rows=len(x),chart_closes=int((x.event=="CLOSE").sum()),journal_present=journal in paths,
                                     independent_expected_status="unavailable" if strategy!="MON_BR" or day>pd.Timestamp("2026-10-13") else "no entry in covered report; version check required",
                                     actual_status="user confirms no fill" if stamp=="20261020" and strategy=="VB" else
                                     "user confirms filled day" if stamp=="20261021" and strategy=="VB" else
                                     "user confirms broker-liquidated trade" if stamp=="20261019" and strategy=="VB" else
                                     "unknown; no log is not proof of no trade"))
    pd.DataFrame(coverage).to_csv(out/"daily_account_strategy_coverage.csv",index=False)
    reports=[]
    for strategy,path in REPORTS.items():
        b=blob(ref,path);hashes[path]=hashlib.sha256(b).hexdigest()
        settings=pd.read_excel(io.BytesIO(b),sheet_name="Settings",header=None)
        st=dict(zip(settings[0].astype(str),settings[1].astype(str)))
        entries=pd.read_excel(io.BytesIO(b),sheet_name="List of Trades",header=2,usecols=["Type","Date"])
        d=pd.to_datetime(entries.loc[entries.Type.astype(str).str.startswith("Entry"),"Date"])
        reports.append(dict(strategy=strategy,path=path,report_end=st.get("End Date"),last_entry=str(d.max()),
                            ADXMin=st.get("ADXMin"),compression=st.get("Compression"),
                            caveat="ADX20 report is not live ADX30" if strategy=="ONB" else "Confirm deployed inputs before expected-trade comparisons"))
    pd.DataFrame(reports).to_csv(out/"backtest_coverage.csv",index=False)
    account=[]
    for label in ("1","2"):
        gross=float(closed[(closed.bar_date=="20261021")&(closed.account_label==label)].chart_gross_usd.sum())
        account.append(dict(day="2026-10-21",account_label=label,chart_gross=gross,user_reported_actual_net=-575,
                            actual_minus_chart=-575-gross,residual_explanation="unallocated fees/fill differences; broker export required"))
    pd.DataFrame(account).to_csv(out/"user_account_day_reconciliation.csv",index=False)
    health=[]
    for path in [p for p in paths if p.startswith("live/health/") and p.endswith(".csv")]:
        b=blob(ref,path);hashes[path]=hashlib.sha256(b).hexdigest()
        for line in b.decode().splitlines():
            fields=line.split(",");kv=dict(f.split("=",1) for f in fields[2:] if "=" in f)
            health.append(dict(mode=fields[0],observed_at=fields[1],**kv))
    pd.DataFrame(health).to_csv(out/"health_summary_audit.csv",index=False)
    summary=dict(source_commit=ref,return_trials=0,live_changes=False,
                 source_files=source_rows,unique_chart_closed_trades=len(closed),raw_open_rows=len(opened),logical_open_keys=len(logical),
                 raw_mismatch_rows=int(pos.mismatch.sum()),mismatch_bar_groups=len(states),
                 unresolved_terminal_bar_groups=sum(not s["resolved_in_same_bar"] for s in states),
                 account_day_actuals=account,slippage_measurable=False,edge_ratio_measurable=False,
                 notes=["Tags are account labels, not broker IDs","No complete independent same-day backtest/broker export",
                        "10/20 user-confirmed no-fill takes precedence","10/21 user confirms -575 each; per-fill prices/fees unknown"],source_sha256=hashes)
    json_write(out/"audit_summary.json",summary)
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--source",default="e097c0f")
    p.add_argument("--output",default="analysis/outputs/codex_live_reconcile")
    p.add_argument("--expected");p.add_argument("--broker");p.add_argument("--coverage-complete",action="store_true")
    args=p.parse_args();out=Path(args.output).resolve()
    allowed=Path("analysis/outputs").resolve()
    if out.parent!=allowed or not out.name.startswith("codex_"):
        raise SystemExit("Output must be analysis/outputs/codex_*")
    audit(args.source,out)
    if bool(args.expected)!=bool(args.broker):raise SystemExit("Supply both --expected and --broker, or neither")
    if args.expected:canonical_comparison(args.expected,args.broker,args.coverage_complete,out)
