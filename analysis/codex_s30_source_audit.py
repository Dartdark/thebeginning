"""S30 source/PDF arithmetic only: no prices, replay, performance or account test.

Preserve uploads in agents/codex/inputs/s30. Extract PDF text with pdftotext
-layout. Outputs label every performance figure as an unverified author claim.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "agents/codex/inputs/s30"
OUT = ROOT / "analysis/outputs/codex_s30_source_audit"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def money(s):
    return float(s.replace("$", "").replace(",", ""))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    text = (INPUT/"overview_extracted.txt").read_text().replace("\u2060", "").replace("−", "-")
    src = (INPUT/"source.txt").read_text()
    executable = re.sub(r"\{.*?\}", "", src, flags=re.S)
    inputs = re.search(r"Inputs:(.*?)Variables:",src,re.S).group(1)
    defaults = {k: v.strip() for k,v in re.findall(r"^\s*(\w+)\(\s*([^()]+?)\s*\)[,;]", inputs, re.M)}
    assert defaults == dict(SessionFirstBar="845", SessionLastBar="1500", SessionBars="26",
                           IbsEntry="0.20", IbsExit="0.80", ContractQty="1", TokyoClock="false")
    pattern = r"^\s*(20\d{2})\s+(\d+)\s+(-?\$[\d,]+)\s+(\d+)\s+(-?\$[\d,]+)\s+(\d+)\s+(-?\$[\d,]+)\s+(-?\$[\d,]+)\s*$"
    rows = []
    for y, nn, np_, en, ep, rn, rp, ap in re.findall(pattern, text, re.M):
        rows.append(dict(year=int(y),NQ_trades=int(nn),NQ_net_micro=money(np_),
                         ES_trades=int(en),ES_net_micro=money(ep),
                         RTY_trades=int(rn),RTY_net_micro=money(rp),all_three_net_micro=money(ap)))
    assert len(rows)==10 and [r["year"] for r in rows]==list(range(2017,2027))
    with (OUT/"overview_annual_claims.csv").open("w") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    headers = {}
    for market, micro in (("NQ","MNQ"),("ES","MES"),("RTY","M2K")):
        pat = rf"^\s*{market}\s*·\s*{micro}\s+(\$[\d,]+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)%\s+(\$[\d.]+)\s+(\$[\d,]+)\s+(\$[\d,]+)"
        mt=re.search(pat,text,re.M)
        assert mt, market
        net,pf,freq,win,avg,dd,closed = mt.groups()
        n=sum(r[f"{market}_trades"] for r in rows)
        headers[market]=dict(trades=n,net_micro=money(net),pf=float(pf),trades_per_year=int(freq),
                             win_percent=float(win),avg_net_micro=money(avg),
                             open_inclusive_claimed_dd_micro=money(dd),closed_dd_micro=money(closed))
    assert [headers[k]["trades"] for k in headers]==[273,260,271]
    totals={}
    for period,lo,hi in (("full",2017,2026),("2017_22",2017,2022),("2018_22",2018,2022),("2023_plus",2023,2026)):
        keep=[r for r in rows if lo<=r["year"]<=hi]
        totals[period]={market:dict(trades=sum(r[f"{market}_trades"] for r in keep),
                                  net_micro=sum(r[f"{market}_net_micro"] for r in keep))
                        for market in headers}
        for market in headers:
            t=totals[period][market]
            t["mean_from_rounded_annual_claims"]=t["net_micro"]/t["trades"]
    arithmetic={k:dict(annual_net_minus_header=totals["full"][k]["net_micro"]-v["net_micro"],
                       implied_average=v["net_micro"]/v["trades"],
                       absolute_average_rounding_error=abs(v["avg_net_micro"]-v["net_micro"]/v["trades"]),
                       positive_years=sum(r[f"{k}_net_micro"]>0 for r in rows))
                for k,v in headers.items()}
    assert all(abs(v["annual_net_minus_header"])<=2 and v["absolute_average_rounding_error"]<.01
               for v in arithmetic.values())
    flags=dict(iog_forced_false=bool(re.search(r"IntrabarOrderGeneration\s*=\s*false",executable,re.I)),
               stop_order_or_builtin_stop=bool(re.search(r"\bstop\b|\bSetStopLoss\b",executable,re.I)),
               target_or_time_exit=bool(re.search(r"SetProfitTarget|SetExitOnClose|FlatTime",executable,re.I)),
               source_roll_adjustment=bool(re.search(r"CumGap|RollGap|RollDate",executable,re.I)),
               BPV_based_contract_conversion="BigPointValue" in executable,
               entries_next_bar_market=len(re.findall(r"\bBuy\s*\(.*?next bar at market",executable)),
               exits_next_bar_market=len(re.findall(r"\bSell\s*\(.*?next bar at market",executable)),
               explicit_session_date_validation=bool(re.search(r"Counting.*Date|SampleBars.*Date",executable)))
    assert flags["iog_forced_false"] and flags["entries_next_bar_market"]==1 and flags["exits_next_bar_market"]==1
    assert not any(flags[k] for k in ("stop_order_or_builtin_stop","target_or_time_exit","source_roll_adjustment","BPV_based_contract_conversion"))
    # Power arithmetic is illustrative, not a measured variance or an extra return trial.
    power={}
    for k,v in totals["2018_22"].items():
        n=v["trades"]
        power[k]=dict(author_claimed_design_trades=n,net_mean_for_t2_as_multiple_of_SD=2/math.sqrt(n),
                      illustrative_unknown_SD_micro=500,illustrative_t2_net_mean_micro=1000/math.sqrt(n),
                      limitations="SD is assumed, not measured; trade dependence reduces effective n; multiple testing raises the bar.")
    summary=dict(operation="Uploaded document/source inspection and arithmetic only",new_strategy_return_trials=0,
                 independent_returns_reproduced=False,raw_MC_exports_supplied=False,
                 instructions_in_uploaded_documents_not_executed=True,defaults=defaults,source_flags=flags,
                 claimed_header=headers,claimed_annual_totals=totals,rounding_checks=arithmetic,
                 sum_component_header_net_micro=sum(v["net_micro"] for v in headers.values()),
                 claimed_combined_header_net_micro=65342,power_arithmetic_only=power,
                 grade_status="PDF explicitly dates B grades 2026-10-17, before roll correction; NQ grading sample274/current273",
                 roll_claim=dict(affected_trades=62,NQ=17,ES=22,RTY=23,aggregate_gap_micro=5280,
                                 estimated_gaps=["June2022","ES September2026"],verified=False),
                 decisions=dict(current_Apex_plan="DON'T TEST: multi-day hold violates existing intraday requirement",
                                personal_validation="NEEDS DATA: corrected native reports/settings and roll ledger before any new return test"))
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    # Reconcile existing published reviewer outputs only. No market data or
    # strategy return generation: these inputs are already-committed ledgers.
    snapshot=INPUT/"reviewer_snapshot"
    reviewer_manifest=json.loads((snapshot/"snapshot.json").read_text())
    trade_totals={}
    for market in ("NQ","ES"):
        tr=list(csv.DictReader((snapshot/f"python_trades_{market}.csv").open()))
        trade_totals[market]=dict(n=len(tr),net_full_contract=sum(float(r["net"]) for r in tr),
                                  first_entry=min(r["date"] for r in tr),last_exit=max(r["exit_date"] for r in tr))
        trade_totals[market]["mean_full_contract"]=trade_totals[market]["net_full_contract"]/len(tr)
    dr=list(csv.reader((snapshot/"daily_nq_es_per_micro.csv").open()))[1:]
    dates=[r[0] for r in dr]
    daily_sum=sum(float(r[1]) for r in dr)
    trade_sum=sum(r["net_full_contract"] for r in trade_totals.values())/10
    assert len({r["last_exit"] for r in trade_totals.values()})==1 and dates[-1]==trade_totals["NQ"]["last_exit"]
    checks=dict(ref=reviewer_manifest["ref"],published_trade_ledgers=trade_totals,
                published_combined_daily_rows=len(dr),first_day=dates[0],last_day=dates[-1],
                published_combined_daily_total_micro=daily_sum,
                sum_published_corrected_net_trades_micro=trade_sum,
                daily_minus_trade_net_micro=daily_sum-trade_sum,
                same_terminal_date_verified=True,
                expected_identity="A consistent completed-position MTM ledger reconciles to net trade cashflows over the same endpoints.",
                static_findings=["Trade net removes identified roll jumps and charges primary commission/slippage",
                                 "Daily MTM uses raw close differences without those adjustments",
                                 "Personal portfolio imports that gross daily S30 series without native micro fee topup",
                                 "Random-entry and holding controls retain raw roll jumps unlike candidate trade net",
                                 "Terminal open position omitted, and partial-2023 holds enter recent-exit trade metrics"])
    (OUT/"reviewer_accounting_checks.json").write_text(json.dumps(checks,indent=2)+"\n")
    manifest=dict(script_sha256=sha(Path(__file__)),
                  repo_snapshot="16dc86c",local_reviewer_ref="e7c394f",claim_source="Uploaded PDF; arithmetic checked, returns and corrections unverified",
                  python_environment="/workspace/venvs/thebeginning/bin/python")
    manifest["input_sha256"]={str(p.relative_to(ROOT)):sha(p) for p in sorted(INPUT.rglob("*")) if p.is_file()}
    manifest["current_reviewer_ref"]=reviewer_manifest["ref"]
    manifest["reviewer_source_blob_checks"]={r["name"]:hashlib.sha1(f"blob {(snapshot/r['name']).stat().st_size}\0".encode()+(snapshot/r["name"]).read_bytes()).hexdigest()==r["blob_sha"] for r in reviewer_manifest["files"]}
    manifest["uploaded_files_match_reviewer_blobs"]={name:hashlib.sha1(f"blob {(INPUT/name).stat().st_size}\0".encode()+(INPUT/name).read_bytes()).hexdigest()==expected for name,expected in
        (("source.txt","d366c62f3d89da33aec4b0d61c61817f50104dd7"),("overview.pdf","19f2415a9f2001258ff30b95fb774a01c318df30"))}
    assert all(manifest["reviewer_source_blob_checks"].values()) and all(manifest["uploaded_files_match_reviewer_blobs"].values())
    (OUT/"reproduction.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(dict(headers=headers,totals=totals,rounding=arithmetic,decisions=summary["decisions"]),indent=2))


if __name__=="__main__":
    main()
