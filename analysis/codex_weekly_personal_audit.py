"""Routine source/ledger reconciliation for 2026-10-23 weekly cross-review.

No new strategy backtest, signal, resampling, Monte Carlo or capital estimate.
The inputs are exact, pinned, previously published source and trade ledgers.
Default: use locally archived inputs and the repository's price timestamps.
Published reproduction: --source-root /path/to/read-only-checkout-at-52a6543
uses that checkout for both original source paths and price timestamps.
"""
import argparse
import csv
from datetime import date
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "agents/codex/inputs/weekly_cross_review_20261023/personal"
OUTPUT = INPUT / "routine_check_results.json"
SUMMARY = ROOT / "analysis/outputs/codex_weekly_personal_audit/summary.json"
REF = "52a6543589941455b775d46dfc23dcfbf16ec188"


def rows(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path,
                        help=f"Read-only repository checkout at {REF}; default is local archived inputs")
    args = parser.parse_args()
    source_root = args.source_root.resolve() if args.source_root else INPUT
    price_root = args.source_root.resolve() if args.source_root else ROOT
    source_paths = (
        "analysis/personal_portfolio.py", "personal_strategies/Twin_Continuation.txt",
        "checks/candidates/twin_continuation/spec.md", "checks/candidates/twin_continuation/trades.csv",
        "agents/tasks/plan_daily_pnl.csv",
    )
    portfolio = (source_root/source_paths[0]).read_text()
    twin_source = (source_root/source_paths[1]).read_text()
    spec = (source_root/source_paths[2]).read_text()
    twin = rows(source_root/source_paths[3])
    calendar = {r["date"] for r in rows(source_root/source_paths[4])}
    assert "Twin Continuation v2.1" in portfolio
    assert 'checks/candidates/twin_continuation/trades.csv' in portfolio
    assert 'date (exit date)' in spec
    assert 'user\'s code, unchanged' in spec
    assert 'UseHolidayTimes( true )' in twin_source
    assert 'EarlyFlatten( 1130 )' in twin_source
    assert 'If HolFlat Then Begin' in twin_source
    assert 'SHalfDay = IsEarlyClose' in twin_source
    selected = ("date", "entry_date", "setup", "side", "entry_time_ct", "exit_time_ct", "net")
    holiday_dates = {"2018-05-28", "2018-11-23", "2021-09-06", "2024-07-04"}
    holiday_carries = [r for r in twin if r["entry_date"] in holiday_dates and r["entry_date"] < r["date"]]
    assert len(twin) == 1074 and len(holiday_carries) == 4
    assert any(r["entry_date"] == "2024-07-04" and r["setup"] == "MO" for r in holiday_carries)
    present = {d: False for d in holiday_dates}
    for year in sorted({d[:4] for d in holiday_dates}):
        path = price_root/f"data/NQ_1min_{year}.csv"
        with path.open() as f:
            for row in csv.DictReader(f):
                d = row["date"][:4]+"-"+row["date"][4:6]+"-"+row["date"][6:]
                if d in present and int(row["time"]) == 1130:
                    present[d] = True
    assert all(present.values())
    dropped = [r for r in twin if r["date"] not in calendar]
    evening = [r for r in twin if int(r["exit_time_ct"]) > 1700]
    assert len(dropped) == 9 and len(evening) == 34
    raw_micro = sum(float(r["net"])/10 for r in dropped)
    net_micro = sum(float(r["net"])/10-.55 for r in dropped)
    out = dict(
        ref=REF, operation="Source/previously published ledger arithmetic; no new strategy returns",
        new_strategy_return_trials=0, input_count=len(twin),
        input_version_claim="personal_portfolio.py calls this Twin Continuation v2.1",
        actual_ledger_spec="unchanged original source, date=calendar exit date",
        holiday_carries=[{k:r[k] for k in selected} for r in holiday_carries],
        holiday_carry_net_micro=sum(float(r["net"])/10 for r in holiday_carries),
        holiday_1130_bar_present=present,
        dropped_twin_rows=[{k:r[k] for k in selected} for r in dropped],
        dropped_rows=len(dropped), dropped_gross_scaled_net_micro=raw_micro,
        dropped_after_portfolio_own_extra_fee_micro=net_micro,
        dropped_sunday_count=sum(date.fromisoformat(r["date"]).weekday()==6 for r in dropped),
        evening_exit_rows=len(evening), evening_exit_net_micro=sum(float(r["net"])/10 for r in evening),
        evening_exit_date_stays_same_calendar_day=True,
        no_corrected_portfolio_or_capital_computed=True,
        consequence="Starter/full capital ladders use a superseded Twin ledger and calendar-date bucketing; corrected magnitude unknown.",
        minimal_check="Use the exact proposed version, map evening/Sunday/holiday exits to the declared futures trading date, reconcile its full net to included daily net, then recompute the existing portfolio risk without changing entry rules.",
        input_sha256={p:hashlib.sha256((source_root/p).read_bytes()).hexdigest()
                      for p in source_paths},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out,indent=2)+"\n")
    compact = {k:v for k,v in out.items() if k not in ("holiday_carries", "dropped_twin_rows")}
    compact["input_paths_relative_to"] = "original repository tree at ref"
    compact["raw_trade_rows_included"] = False
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(compact,indent=2)+"\n")
    print(json.dumps({k:out[k] for k in ('input_count','holiday_carry_net_micro','dropped_rows',
                     'dropped_after_portfolio_own_extra_fee_micro','evening_exit_rows','new_strategy_return_trials')},indent=2))


if __name__ == "__main__":
    main()
