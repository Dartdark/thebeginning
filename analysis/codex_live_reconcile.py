"""Offline chart/user/broker reconciliation prototype; never writes live files or sends alerts.

Default audit pins e097c0f. Optional expected/broker CSVs must contain verified canonical account/strategy IDs,
symbol, entry_time, exit_time, side (+1/-1), qty, entry, exit; prices/times are actual, not chart bar labels.
--coverage-complete explicitly declares both optional files complete for the compared dates/accounts/strategies.
Absent that declaration, unmatched rows are unresolved, never automatically missed/extra.
ONB_ADX30 is the evaluation key; ONB is an ambiguous chart tag, not a report-version key.
--expected-report imports a validated ADX30 report using live_vs_backtest.read_trades.
No broker fills are ever inferred from a MultiCharts chart report.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from live_vs_backtest import read_trades

COLS = ["event","tag","symbol","side","contracts","entry_date","entry_time","entry_price",
        "exit_date","exit_time","exit_price","profit_usd","bar_date","bar_time"]
REPORTS = {
    "VB": "mc_reports/Backtesting Strategy Performance Report VB v1.xlsx",
    "ONB": "mc_reports/Backtesting Strategy Performance Report ONB v2.xlsx",
    "EOS": "mc_reports/Backtesting Strategy Performance Report EOS v1.xlsx",
    "MON_BR": "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx",
}
OPEN_KEY = ["tag","symbol","side","contracts","entry_date","entry_time","entry_price"]
EVALUATION_KEYS = {
    "ONB_ADX30": {
        "chart_tag": "ONB", "ADXMin": 30, "compression": "15 Minutes",
        "backtest": "mc_reports/Backtesting Strategy Performance Report ONB ADX30.xlsx",
    },
}


def validate_evaluation_report(settings, key):
    if key not in EVALUATION_KEYS:
        raise ValueError(f"Supported evaluation report keys: {list(EVALUATION_KEYS)}")
    spec = EVALUATION_KEYS[key]
    if pd.to_numeric(settings.get("ADXMin"), errors="coerce") != spec["ADXMin"]:
        raise ValueError(f"{key} requires ADXMin={spec['ADXMin']}; no ADX20 fallback")
    if str(settings.get("Compression", "")).strip().lower() != spec["compression"].lower():
        raise ValueError(f"{key} requires {spec['compression']}")
    # A disabled or enabled ML input still identifies a different report/code family.
    if "UseMLFilter" in settings or any("overnight bias ml" in str(k).lower() for k in settings):
        raise ValueError("Funded ML ONB is not evaluation ONB_ADX30")
    if not any(str(k).strip().lower() == "nq overnight bias" for k in settings):
        raise ValueError("Missing evaluation strategy identity: expected NQ Overnight Bias in Settings")


def expected_from_report(path, key, account, symbol, qty, start, end, out):
    """Import an existing backtest export only; never executes a strategy or changes live state."""
    raw = pd.read_excel(path, sheet_name="Settings", header=None)
    settings = dict(zip(raw[0].astype(str), raw[1]))
    validate_evaluation_report(settings, key)
    start, end = pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize()
    if start > end:
        raise ValueError("Start must not follow end")
    first, last = pd.to_datetime(settings.get("Start Date")), pd.to_datetime(settings.get("End Date"))
    if pd.isna(first) or pd.isna(last) or first > start or last < end + pd.Timedelta(hours=15, minutes=59):
        raise ValueError("Backtest Settings do not cover the requested complete session span")
    if symbol not in ("MNQ", "NQ") or str(settings.get("Symbol Name", "")).strip() not in ("@NQ", "@MNQ", "NQ", "MNQ"):
        raise ValueError("ONB_ADX30 adapter requires explicit NQ/MNQ root identity")
    report_sizing = str(qty) == "report"
    if report_sizing:
        if str(settings["Symbol Name"]).strip().lstrip("@") != symbol:
            raise ValueError("Report quantities require the same NQ/MNQ contract root; no automatic micro conversion")
    else:
        qty = float(qty)
        if not np.isfinite(qty) or qty <= 0 or qty != int(qty):
            raise ValueError("Expected evaluation qty must be 'report' or a confirmed positive fixed integer")
        if pd.to_numeric(settings.get("RiskPerTrade", 0), errors="raise") > 0:
            raise ValueError("Risk-sized report cannot be overwritten with fixed quantity; use same-root 'report' or canonical per-trade sizes")
    # read_trades historically truncates unmatched entry/exit rows. Refuse such exports here.
    trade_rows = pd.read_excel(path, sheet_name="List of Trades", header=2)
    types = trade_rows.Type.astype(str)
    if int(types.str.startswith("Entry").sum()) != int(types.str.startswith("Exit").sum()):
        raise ValueError("Open/unpaired chart trades: export closed round trips before reconciliation")
    x = read_trades(path)
    x = x[x.session.between(start, end)].copy()
    # Per-contract prices remain comparable across NQ/MNQ. Evaluation size is not the one-NQ report size.
    x["backtest_report_qty"] = x.qty
    x["account"], x["strategy"], x["symbol"] = str(account), key, symbol
    if not report_sizing:
        x["qty"] = qty
    output = out / "expected_from_report.csv"
    x.to_csv(output, index=False)
    json_write(out / "expected_report_manifest.json", dict(
        report=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(), key=key,
        account=str(account), symbol=symbol, expected_qty=qty, start=str(start.date()), end=str(end.date()),
        validated_fields={k:str(settings.get(k)) for k in ("ADXMin", "Compression", "Symbol Name", "Start Date", "End Date")},
        settings={k:str(v) for k,v in settings.items() if k != "nan"},
        caveat="ADX/chart/family gate only. Verify all deployed inputs/code. 'report' preserves per-trade sizes; a numeric override is valid only for confirmed fixed sizing, never a substitute for live risk sizing."))
    return output


def blob(ref, path):
    return subprocess.check_output(["git","show",f"{ref}:{path}"], stderr=subprocess.PIPE)


def json_write(path, obj):
    path.write_text(json.dumps(obj, indent=2, default=str)+"\n")


def identity(tag):
    base, _, suffix = str(tag).partition("-")
    return base, suffix or "1"  # user labels only; NOT verified broker account IDs


def dashboard_actuals(text, day):
    """Read dated dashboard table facts only; never infer executions from order/chart rows."""
    actuals = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[1] != day:
            continue
        account = re.fullmatch(r"(.+)-0?([12])", cells[0])
        if not account:
            continue
        try:
            net = float(cells[2].replace("−", "-").replace("$", "").replace(",", ""))
        except ValueError:
            continue
        label = account[2]
        if label in actuals:
            raise ValueError("Conflicting duplicate dashboard account/day facts; review source")
        actuals[label] = dict(net=net, dashboard_account=cells[0])
    return actuals


def normalized(path):
    x = pd.read_csv(path, dtype={"account":str,"strategy":str,"symbol":str})
    required = ["account","strategy","symbol","entry_time","exit_time","side","qty","entry","exit"]
    if not set(required).issubset(x):
        raise ValueError(f"Canonical CSV needs {required}")
    for k in ("account","strategy","symbol"):
        if x[k].isna().any():
            raise ValueError(f"Missing canonical {k}")
        x[k] = x[k].astype(str)
    if x.strategy.eq("ONB").any():
        raise ValueError("ONB is an ambiguous chart tag: use verified ONB_ADX30 or a distinct funded/report-version key")
    for k in ("entry_time","exit_time"):
        x[k] = pd.to_datetime(x[k])
        if x[k].isna().any() or x[k].dt.tz is not None:
            raise ValueError("Canonical timestamps must be present and normalized to naive Central time")
    for k in ("side","qty","entry","exit"):
        x[k] = pd.to_numeric(x[k], errors="raise")
        if not np.isfinite(x[k]).all():
            raise ValueError(f"Invalid numeric {k}")
    if not x.side.isin([-1,1]).all() or not ((x.qty>0)&(x.qty==x.qty.astype(int))).all() or (x.exit_time<x.entry_time).any():
        raise ValueError("Invalid side/size or exit before entry")
    x["pts"] = (x.exit-x.entry)*x.side
    x["session"] = (x.entry_time+pd.to_timedelta((x.entry_time.dt.hour>=16).astype(int),unit="D")).dt.normalize()
    x["exit_signal"] = "verified_input"
    x["signal"] = "verified_input"
    keys = ["account","strategy","symbol","entry_time","side"]
    if x.duplicated(keys).any():
        raise ValueError("Ambiguous execution keys: aggregate partial fills into round trips with order IDs first")
    return x


def canonical_comparison(expected, broker, complete, out, start=None, end=None, scope=None):
    """Date-local extension of live_vs_backtest.compare retaining fully missed dates/account scope."""
    e, b = normalized(expected), normalized(broker)
    input_counts = dict(expected=len(e), broker=len(b))
    keys = ["account","strategy","symbol"]
    if scope is not None:
        e, b = e[(e[keys]==scope).all(axis=1)], b[(b[keys]==scope).all(axis=1)]
    for label, bound in (("start", start), ("end", end)):
        if bound is not None:
            stamp = pd.Timestamp(bound).normalize()
            if label == "start":
                e, b = e[e.session>=stamp], b[b.session>=stamp]
            else:
                e, b = e[e.session<=stamp], b[b.session<=stamp]
    rows = []
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
    result = pd.DataFrame(rows, columns=list(dict.fromkeys(keys+[k for row in rows for k in row]+["status","entry_time"])))
    result.to_csv(out/"verified_execution_comparison.csv",index=False)
    json_write(out/"verified_execution_summary.json", dict(
        coverage_complete=complete, start=start, end=end, expected_rows=len(e), broker_rows=len(b),
        explicit_scope=scope, input_rows_before_scope_and_date_filters=input_counts,
        status_counts=result.status.value_counts().to_dict(),
        inputs={str(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (expected,broker)},
        notes=["Complete coverage is an explicit input declaration, not inferred from matching rows",
               "No scale/edge-ratio verdict; account/order attribution and all strategy inputs require review"]))
    return result


def audit(ref, out, start="2026-10-12", end="2026-10-21"):
    out.mkdir(parents=True,exist_ok=True)
    paths = subprocess.check_output(["git","ls-tree","-r","--name-only",ref],text=True).splitlines()
    # Previous calendar day supplies Sunday/evening context; preserve file append order.
    context_start = (pd.Timestamp(start)-pd.Timedelta(days=1)).strftime("%Y%m%d")
    end_stamp = pd.Timestamp(end).strftime("%Y%m%d")
    trade_files = [p for p in paths if p.startswith("live/trades/") and p.endswith(".csv")
                   and context_start <= Path(p).stem <= end_stamp]
    hashes = {}; source_rows=[]; data=[]
    for path in trade_files:
        b=blob(ref,path);hashes[path]=hashlib.sha256(b).hexdigest()
        x=pd.read_csv(io.BytesIO(b),header=None,names=COLS,dtype=str,keep_default_na=False)
        x["file"]=path;x["source_row"]=np.arange(1,len(x)+1)
        source_rows.append(dict(path=path,rows=len(x),exact_duplicates=int(x[COLS].duplicated().sum()),**x.event.value_counts().to_dict()))
        data.append(x)
    log=pd.concat(data,ignore_index=True) if data else pd.DataFrame(columns=COLS+["file","source_row"])
    log["strategy"]=[identity(t)[0] for t in log.tag]
    log["account_label"]=[identity(t)[1] for t in log.tag]
    log["evaluation_key"]=log.strategy.replace({"ONB":"ONB_ADX30"})
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
    for day in pd.bdate_range(start,end):
        stamp=day.strftime("%Y%m%d")
        for account in (["1","2"] if day>=pd.Timestamp("2026-10-20") else ["1"]):
            for strategy in REPORTS:
                x=log[(log.bar_date==stamp)&(log.account_label==account)&(log.strategy==strategy)]
                journal=f"journal/daily/{day.date()}.md"
                coverage.append(dict(date=str(day.date()),account_label=account,strategy=strategy,
                                     evaluation_key="ONB_ADX30" if strategy=="ONB" else strategy,
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
        eligible=None; caveat="Confirm deployed inputs before expected-trade comparisons"
        if strategy=="ONB":
            try:
                validate_evaluation_report(st,"ONB_ADX30"); eligible=True
                caveat="ADX30/family gate passed on existing export path; verify full inputs and requested date coverage"
            except ValueError as exc:
                eligible=False; caveat=str(exc)
        reports.append(dict(strategy=strategy,path=path,report_end=st.get("End Date"),last_entry=str(d.max()),
                            evaluation_key="ONB_ADX30" if strategy=="ONB" else strategy,
                            eligible_for_adx30=eligible,
                            ADXMin=st.get("ADXMin"),compression=st.get("Compression"),
                            caveat=caveat))
    for key,spec in EVALUATION_KEYS.items():
        path=spec["backtest"]
        eligible=False; caveat="ADX30 evaluation export missing; no ADX20/ML fallback"
        st={}
        if path in paths:
            report_blob=blob(ref,path); hashes[path]=hashlib.sha256(report_blob).hexdigest()
            settings=pd.read_excel(io.BytesIO(report_blob),sheet_name="Settings",header=None)
            st=dict(zip(settings[0].astype(str),settings[1]))
            try:
                validate_evaluation_report(st,key); eligible=True
                caveat="ADX30/family gate passed; verify full inputs and requested date coverage before matching"
            except ValueError as exc:
                caveat=str(exc)
        reports.append(dict(strategy=spec["chart_tag"],evaluation_key=key,path=path,
                            report_end=st.get("End Date"),ADXMin=st.get("ADXMin"),compression=st.get("Compression"),
                            eligible_for_adx30=eligible,caveat=caveat))
    pd.DataFrame(reports).to_csv(out/"backtest_coverage.csv",index=False)
    account=[]
    actual_source="original user confirmation, rounded to whole dollars"
    actuals={"1":dict(net=-575),"2":dict(net=-575)}
    dashboard_path="live/orders_20261020_21.md"
    if dashboard_path in paths:
        dashboard_blob=blob(ref,dashboard_path); hashes[dashboard_path]=hashlib.sha256(dashboard_blob).hexdigest()
        actuals.update(dashboard_actuals(dashboard_blob.decode(),"2026-10-21"))
        actual_source=dashboard_path+"; dashboard table if present, original rounded confirmation otherwise"
    for label in (("1","2") if start <= "2026-10-21" <= end else ()):
        chart_day=closed[(closed.bar_date=="20261021")&(closed.account_label==label)]
        gross=float(chart_day.chart_gross_usd.sum()) if len(chart_day) else np.nan
        net=actuals[label]["net"]
        account.append(dict(day="2026-10-21",account_label=label,chart_gross=gross,user_reported_actual_net=net,
                            actual_minus_chart=net-gross,actual_evidence=actual_source,
                            residual_explanation="unallocated fees/fill differences; broker export required"))
    pd.DataFrame(account).to_csv(out/"user_account_day_reconciliation.csv",index=False)
    health=[]
    for path in [p for p in paths if p.startswith("live/health/") and p.endswith(".csv")
                 and context_start <= Path(p).stem <= end_stamp]:
        b=blob(ref,path);hashes[path]=hashlib.sha256(b).hexdigest()
        for line in b.decode().splitlines():
            fields=line.split(",");kv=dict(f.split("=",1) for f in fields[2:] if "=" in f)
            health.append(dict(mode=fields[0],observed_at=fields[1],**kv))
    pd.DataFrame(health).to_csv(out/"health_summary_audit.csv",index=False)
    summary=dict(source_commit=ref,requested_start=start,requested_end=end,previous_day_context=True,return_trials=0,live_changes=False,
                 source_files=source_rows,unique_chart_closed_trades=len(closed),raw_open_rows=len(opened),logical_open_keys=len(logical),
                 raw_mismatch_rows=int(pos.mismatch.sum()),mismatch_bar_groups=len(states),
                 unresolved_terminal_bar_groups=sum(not s["resolved_in_same_bar"] for s in states),
                 account_day_actuals=account,slippage_measurable=False,edge_ratio_measurable=False,
                 notes=["Tags are account labels, not broker IDs","No complete independent same-day backtest/broker export",
                        "10/20 user-confirmed no-fill takes precedence","10/21 net follows dated dashboard table if present, otherwise original rounded user confirmation; per-fill attribution unknown"],source_sha256=hashes)
    json_write(out/"audit_summary.json",summary)
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--source",default="e097c0f")
    p.add_argument("--output",default="analysis/outputs/codex_live_reconcile")
    p.add_argument("--expected");p.add_argument("--broker");p.add_argument("--coverage-complete",action="store_true")
    p.add_argument("--start",default="2026-10-12");p.add_argument("--end",default="2026-10-21")
    p.add_argument("--expected-report");p.add_argument("--report-key",choices=list(EVALUATION_KEYS))
    p.add_argument("--account");p.add_argument("--symbol",choices=["NQ","MNQ"])
    p.add_argument("--expected-qty",help="'report' preserves same-root per-trade sizes; numeric override only for confirmed fixed sizing")
    p.add_argument("--compare-only",action="store_true",help="Skip historical chart audit; compare supplied verified records only")
    args=p.parse_args();out=Path(args.output).resolve()
    allowed=Path("analysis/outputs").resolve()
    if out.parent!=allowed or not out.name.startswith("codex_"):
        raise SystemExit("Output must be analysis/outputs/codex_*")
    if pd.Timestamp(args.start)>pd.Timestamp(args.end):p.error("--start must not follow --end")
    if args.expected and args.expected_report:p.error("Choose --expected CSV or --expected-report XLSX")
    if bool(args.expected or args.expected_report)!=bool(args.broker):p.error("Supply expected records and --broker together")
    if args.compare_only and not args.broker:p.error("--compare-only requires expected and broker records")
    if args.coverage_complete and not args.broker:p.error("--coverage-complete requires expected and broker records")
    if args.expected_report and any(v is None for v in (args.report_key,args.account,args.symbol,args.expected_qty)):
        p.error("Report import needs --report-key, --account, --symbol and --expected-qty")
    out.mkdir(parents=True,exist_ok=True)
    expected=args.expected
    if args.expected_report:
        expected=expected_from_report(args.expected_report,args.report_key,args.account,args.symbol,args.expected_qty,args.start,args.end,out)
    if not args.compare_only:audit(args.source,out,args.start,args.end)
    if expected:
        scope=(args.account,args.report_key,args.symbol) if args.expected_report else None
        canonical_comparison(expected,args.broker,args.coverage_complete,out,args.start,args.end,scope)
