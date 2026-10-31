"""Independent audit of the frozen Calvados design ledgers; no new strategy.

Reconstruct equity from completed-trade intervals, and compare saved decisions
with explicit past-only settlement slices. Never import or modify the runner.
"""
from pathlib import Path
import hashlib
import json
import subprocess

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "agents/codex/inputs/calvados_2379985_20261030"
OUTPUT = ROOT / "analysis/outputs/codex_calvados_2379985_20261030"
PRIMARY = ROOT / "analysis/codex_calvados_2379985_20261030.py"
PLAN = ROOT / "agents/codex/plans/calvados_2379985_20261030.md"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def same_date(a, b):
    return (pd.isna(a) and pd.isna(b)) or a == b


def close(a, b):
    return bool(np.isclose(a, b, rtol=1e-10, atol=1e-7, equal_nan=True))


def run():
    checks = {}

    def require(name, condition):
        checks[name] = bool(condition)
        if not condition:
            raise AssertionError(name)

    result = json.loads((OUTPUT / "design_result.json").read_text())
    manifest = json.loads((INPUT / "panel_manifest.json").read_text())
    gate = json.loads((INPUT / "data_gate.json").read_text())
    calendar = pd.DatetimeIndex(pd.read_csv(INPUT / "cfe_calendar.csv", parse_dates=["date"]).date)
    positions = {d: i for i, d in enumerate(calendar)}
    design_dates = calendar[(calendar >= "2018-01-01") & (calendar <= "2022-12-31")]
    spot = pd.read_csv(gate["spot_path"], parse_dates=["DATE"]).set_index("DATE").CLOSE
    raw = {}
    for item in manifest["files"]:
        require("raw_hash:" + item["expiry"], sha(item["path"]) == item["sha256"])
        raw[pd.Timestamp(item["expiry"])] = pd.read_csv(item["path"], parse_dates=["Trade Date"]).set_index("Trade Date").sort_index()
    require("primary_hash", sha(PRIMARY) == result["code_sha256"])
    require("plan_hash", sha(PLAN) == result["plan_sha256"])
    for path in [PRIMARY, PLAN]:
        blob = subprocess.check_output(["git", "show", result["plan_commit"] + ":" + path.relative_to(ROOT).as_posix()], cwd=ROOT)
        require("preregistered_blob:" + path.name, hashlib.sha256(blob).hexdigest() == sha(path))
    for name, digest in result["input_sha256"].items():
        require("input_hash:" + name, sha(INPUT / name) == digest)
    require("spot_hash", sha(gate["spot_path"]) == result["spot_sha256"])
    for name, digest in result["shared_code_sha256"].items():
        require("shared_hash:" + name, sha(ROOT / "analysis" / name) == digest)

    trades = pd.read_csv(OUTPUT / "design_trades.csv", parse_dates=["entry_date", "exit_date", "entry_decision", "expiry"])
    daily = pd.read_csv(OUTPUT / "design_daily.csv", parse_dates=["date", "held_expiry"]).set_index("date")
    decisions = pd.read_csv(OUTPUT / "design_decisions.csv", parse_dates=["date", "current_expiry", "next_expiry"]).set_index("date")
    marks = pd.read_csv(OUTPUT / "design_marks.csv", parse_dates=["date", "expiry"]).set_index("date")
    require("daily_dates", daily.index.equals(design_dates))
    require("decision_dates", decisions.index.equals(design_dates[:-1]))
    require("mark_dates", marks.index.equals(design_dates))
    require("only_short_one_contract", ((trades.side == -1) & (trades.qty == 1)).all())
    require("nonempty_positive_holding_intervals", (trades.entry_date < trades.exit_date).all())
    require("single_position_intervals", (trades.entry_date.iloc[1:].reset_index(drop=True) >= trades.exit_date.iloc[:-1].reset_index(drop=True)).all())

    def tts(expiry, day):
        return positions[expiry] - positions[day]

    score_cache = {}

    def score(expiry, day):
        key = (expiry, day)
        if key not in score_cache:
            history = raw[expiry].loc[:day].tail(11)
            require("past_window:" + str(key), len(history) == 11 and history.index[-1] == day and history.index.max() <= day)
            # Explicit 11-mark window, rather than the primary rolling method.
            dates = calendar[positions[day] - 10:positions[day] + 1]
            require("consecutive_window:" + str(key), history.index.equals(dates))
            sigma = np.sqrt(np.dot(np.diff(history.Settle.to_numpy()), np.diff(history.Settle.to_numpy())) / 10.)
            score_cache[key] = (float(history.Settle.iloc[-1]) - float(spot.loc[day])) / (sigma * tts(expiry, day))
        return score_cache[key]

    for i, trade in trades.iterrows():
        require(f"entry_ref:{i}", close(trade.entry_ref, raw[trade.expiry].loc[trade.entry_date, "Open"]))
        require(f"exit_ref:{i}", close(trade.exit_ref, raw[trade.expiry].loc[trade.exit_date, "Open"]))
        require(f"entry_clock:{i}", positions[trade.entry_date] == positions[trade.entry_decision] + 1)
        require(f"entry_decision_identity:{i}", decisions.loc[trade.entry_decision, "next_expiry"] == trade.expiry)
        require(f"entry_score:{i}", close(trade.entry_score, score(trade.expiry, trade.entry_decision)) and trade.entry_score > .12)
        gross = (trade.entry_ref - trade.exit_ref) * 1000.
        require(f"trade_accounting:{i}", all([close(trade.gross, gross), close(trade.fees, 10.), close(trade.slippage, 100.), close(trade.net, gross - 110.), close(trade.stress_net, gross - 210.)]))

    reconstructed = []
    previous = 0.
    for i, day in enumerate(design_dates):
        active = trades[(trades.entry_date <= day) & (trades.exit_date > day)]
        require("at_most_one_held:" + str(day.date()), len(active) <= 1)
        expiry = active.iloc[0].expiry if len(active) else pd.NaT
        closed_cash = float(trades.loc[trades.exit_date <= day, "net"].sum()) - 55. * len(active)
        unrealized = float((active.iloc[0].entry_ref - raw[expiry].loc[day, "Settle"]) * 1000.) if len(active) else 0.
        equity = closed_cash + unrealized
        saved = daily.loc[day]
        require("equity_ledger:" + str(day.date()), close(saved.equity, equity) and close(saved.net, equity - previous))
        require("held_identity:" + str(day.date()), same_date(saved.held_expiry, expiry) and same_date(marks.loc[day, "expiry"], expiry))
        require("cash_marks:" + str(day.date()), close(marks.loc[day, "closed_cash"], closed_cash) and close(marks.loc[day, "unrealized"], unrealized))
        require("spot_flag:" + str(day.date()), bool(saved.spot_available) == (day in spot.index))
        if i == 0 or i == len(design_dates) - 1:
            require("boundary_flat:" + str(day.date()), pd.isna(expiry))
        else:
            require("prior_decision_target:" + str(day.date()), same_date(decisions.iloc[i - 1].next_expiry, expiry))
        reconstructed.append(equity)
        previous = equity
        if day not in decisions.index:
            continue
        record = decisions.loc[day]
        require("decision_current_identity:" + str(day.date()), same_date(record.current_expiry, expiry))
        require("decision_spot_flag:" + str(day.date()), bool(record.fresh_spot) == (day in spot.index))
        if day not in spot.index:
            require("known_missing_spot_only", day == pd.Timestamp("2018-12-05"))
            expected = pd.NaT if pd.notna(expiry) and tts(expiry, day) < 10 else expiry
            require("missing_spot_policy", same_date(record.next_expiry, expected) and pd.isna(record.chosen_score) and pd.isna(record.own_score))
            continue
        eligible = [(score(e, day), e) for e in raw if 15 <= tts(e, day) <= 93]
        best_score, best_expiry = sorted(eligible, key=lambda x: (-x[0], x[1]))[0]
        own = score(expiry, day) if pd.notna(expiry) else np.nan
        needs_entry_decision = pd.isna(expiry) or tts(expiry, day) < 10 or own < .10
        expected = best_expiry if needs_entry_decision and best_score > .12 else (pd.NaT if needs_entry_decision else expiry)
        expected_score = best_score if pd.notna(expected) and not same_date(expected, expiry) else own
        require("decision_rule:" + str(day.date()), same_date(record.next_expiry, expected) and close(record.own_score, own) and close(record.chosen_score, expected_score))

    equity = np.asarray(reconstructed)
    peak = np.maximum.accumulate(np.r_[0., equity])[1:]
    drawdown = peak - equity
    trough = int(np.argmax(drawdown))
    peak_before = int(np.argmax(np.r_[0., equity[:trough + 1]])) - 1
    max_dd = float(drawdown[trough])
    require("total_reconciliation", close(trades.net.sum(), daily.net.sum()) and close(equity[-1], result["metrics"]["total"]))
    require("gross_and_cost_bridge", all([close(trades.gross.sum(), result["metrics"]["gross"]), close(trades.fees.sum(), result["metrics"]["fees"]), close(trades.slippage.sum(), result["metrics"]["slippage"]), close(trades.stress_net.sum(), result["metrics"]["stress_total"])]))
    require("max_drawdown", close(max_dd, result["metrics"]["max_dd"]))
    require("reported_trade_count", len(trades) == result["metrics"]["trades"])
    years = daily.net.groupby(daily.index.year).sum()
    require("year_totals", all(close(value, result["year_net"][str(year)]) for year, value in years.items()))
    require("failed_gate_stops", result["passed"] is False and result["preferred_hedged_tested"] is False and result["account_comparisons_run"] is False)
    null = pd.read_csv(OUTPUT / "design_random_side.csv")
    require("random_side_receipt", len(null) == 1000 and close((1 + (null.total >= daily.net.sum()).sum()) / 1001., result["random_side_p"]))

    worst_trade = trades.loc[trades.net.idxmin()].to_dict()
    worst_day = daily.net.idxmin()
    local_dates = design_dates[max(0, positions[worst_day] - positions[design_dates[0]] - 1):positions[worst_day] - positions[design_dates[0]] + 2]
    spot_check = daily.loc[local_dates].reset_index().to_dict("records")
    special = daily.loc["2018-12-04":"2018-12-06"].reset_index().to_dict("records")
    terminal = daily.tail(3).reset_index().to_dict("records")

    def safe(value):
        if isinstance(value, dict):
            return {k: safe(v) for k, v in value.items()}
        if isinstance(value, list):
            return [safe(v) for v in value]
        if value is pd.NaT or (isinstance(value, float) and not np.isfinite(value)):
            return None
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        if isinstance(value, (np.integer, np.floating, np.bool_)):
            return value.item()
        return value

    output = dict(scope="Independent implementation/accounting audit of the existing frozen 2018–2022 outcome only; no new economic variant or later returns",
                  all_checks_passed=all(checks.values()), checks_run=len(checks), defects=[],
                  preregistration_commit=result["plan_commit"], primary_sha256=sha(PRIMARY), checker_sha256=sha(__file__),
                  design_output_sha256={p.name: sha(p) for p in sorted(OUTPUT.glob("design_*")) if p.is_file()},
                  dates=len(daily), decisions=len(decisions), closed_trades=len(trades),
                  independently_reconstructed=dict(gross=float(trades.gross.sum()), net=float(trades.net.sum()), fees=float(trades.fees.sum()), slippage=float(trades.slippage.sum()), stress_net=float(trades.stress_net.sum()), maximum_marked_drawdown=max_dd,
                                                   drawdown_peak_date=design_dates[peak_before] if peak_before >= 0 else "initial", drawdown_trough_date=design_dates[trough]),
                  worst_trade=worst_trade, worst_daily_mark_date=worst_day, worst_daily_mark_window=spot_check,
                  december5_window=special, terminal_window=terminal,
                  limitations=["Primary/source-data equality and executable fill quality remain unverified.", "Daily settlement marks do not verify intraday margin or liquidation risk.", "The preferred ES-hedged strategy and later/account outcomes were not tested.", "This is a separate implementation audit by a collaborating agent, not external independent economic verification."])
    (OUTPUT / "checks.json").write_text(json.dumps(safe(output), indent=2, allow_nan=False) + "\n")
    print(json.dumps(safe({k: output[k] for k in ["all_checks_passed", "checks_run", "closed_trades", "independently_reconstructed", "worst_trade", "worst_daily_mark_date", "december5_window", "terminal_window"]}), indent=2, allow_nan=False))


if __name__ == "__main__":
    run()
