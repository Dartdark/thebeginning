"""Diagnose prepared source clocks and raw input completeness, not returns.

Do not repair the frozen tape, change sizing/selection or simulate accounts.
DT counts use already prepared source metadata; the availability audit is
limited to2018 raw records needed for the first design ONB30 signal.
"""
from pathlib import Path
from types import SimpleNamespace
import json
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis"))
import codex_eval_paths_20261104 as paths
import codex_eval_run_20261104 as run

HERE = Path(__file__).resolve().parent
PREREG = "a087708b13697df4c3dd0b0814f98cb53a2b254a"


def main():
    config = run.read_json(HERE / "config.json")
    for file in ["analysis/codex_eval_paths_20261104.py", "analysis/dual_thrust_test.py",
                 "analysis/codex_portfolio_audit_prepare.py", "agents/codex/inputs/eval_audit_20261104/config.json"]:
        run.verify_file_at_commit(ROOT / file, PREREG)
    tape = ROOT / "agents/codex/runtime/eval_audit_20261104/tape"
    trades = pd.read_csv(tape / "trades.csv")
    quality = pd.read_csv(tape / "quality.csv")
    dt = trades[trades.key == "DT"]
    phase_bad = quality[(quality.key == "DT") & quality.issue.str.startswith("exit quote")]
    dtbad = dt[dt.trade_id.isin(phase_bad.trade_id)]
    dtflat = dt[dt.kind == 2]
    # Known2018 clock example: compare declared ledger OPEN exit against
    # the frozen builder's CLOSE-phase check, not a revised account outcome.
    raw_files = [ROOT / "data/NQ_1min_2018.csv", ROOT / "data/NQ_1min_ON_2018.csv"]
    for file in raw_files:
        assert run.sha(file) == config["input_sha256"][str(file.relative_to(ROOT))]
    raw = pd.concat([pd.read_csv(p) for p in raw_files]).drop_duplicates(["date", "time"])
    quote = raw[(raw.date == 20180411) & (raw.time == 1456)].iloc[0]
    example = dt[(dt.exit_at == "2018-04-11 14:56:00") & (dt.kind == 2)].iloc[0]
    assert example.exit == quote.open and example.exit != quote.close
    dt_receipt = dict(total=len(dt), kind_counts=dt.kind.value_counts().to_dict(),
        exit_phase_unknown_rows=len(phase_bad), exit_phase_unknown_kind_counts=dtbad.kind.value_counts().to_dict(),
        flat_kind2_count=len(dtflat), flat_exit_clocks=dtflat.exit_at.str[-8:].value_counts().to_dict(),
        flat_phase_mismatches=int((dtbad.kind == 2).sum()),
        target_phase_unknown=int((dtbad.kind == 1).sum()),
        explanation="Source flat uses next observed bar open; prior adapter default exit_open=False collapsed flat into kind2 and frozen builder checks close. Target-through failures are separate, unchanged.",
        example=dict(date="2018-04-11", bar_close_label="14:56", ledger_exit=float(example.exit),
            raw_open=float(quote.open), raw_close=float(quote.close), source_exit_open_flag=bool(example.exit_open),
            missing_held_bars=int(example.missing_held_bars)),
        frozen_source_sha256={p:run.sha(ROOT / p) for p in ["analysis/dual_thrust_test.py",
            "analysis/codex_portfolio_audit_prepare.py", "analysis/outputs/codex_portfolio_audit_20261031/DT_unit_ledger.csv"]})
    # Rebuild COMPLETENESS ONLY, not ATR values. The mean/source-day range is
    # not recomputed. All closure rules are the original committed ones.
    raw = raw[raw.date < 20180402]
    days = pd.date_range("2018-01-01", "2018-04-01")
    D = len(days); valid = np.zeros((D, 1440), bool); close_observed = valid.copy()
    row = days.searchsorted(pd.to_datetime(raw.date.astype(str)))
    col = (raw.time // 100 * 60 + raw.time % 100).to_numpy()
    valid[row, col] = np.isfinite(raw[["open", "high", "low", "close"]]).all(axis=1).to_numpy()
    close_observed[row, col] = np.isfinite(raw.close)
    closed = paths.civil_closure_mask(SimpleNamespace(ts=days.to_numpy(), D=D), "NQ", config["market_closures"])
    k = 15
    ok = (valid | closed) & ~(valid & closed)
    def candles(a, reduce):
        padded = np.r_[np.zeros(k-1, bool), a.ravel()]
        padded = np.r_[padded, np.zeros((-len(padded)) % k, bool)].reshape(-1, k)
        return reduce(padded, axis=1)[:D*96].reshape(D, 96)
    complete = candles(ok, np.all); observed = candles(close_observed, np.any)
    history = []
    for d, date in enumerate(days):
        seen = np.flatnonzero(observed[d])
        if date.dayofweek < 5 and len(seen):
            history.append((d, seen[0], seen[-1]))
    bad = []
    for d, first, last in history[-15:]:
        for j in range(first, last + 1):
            if complete[d, j]:
                continue
            indexes = np.arange(d*1440 + j*k - (k-1), d*1440 + j*k + 1)
            missing = indexes[(~valid.ravel()[indexes]) & (~closed.ravel()[indexes])]
            contradiction = indexes[(valid.ravel()[indexes]) & (closed.ravel()[indexes])]
            def labels(indexes):
                return [(days[int(i)//1440] + pd.Timedelta(minutes=int(i)%1440)).isoformat() for i in indexes]
            bad.append(dict(date=str(days[d].date()), close_label=f"{j*k//60:02}:{j*k%60:02}",
                missing_expected_open_minutes=labels(missing), observed_closed_contradictions=labels(contradiction)))
    onb = trades[(trades.key == "ONB30") & (trades.entry_at == "2018-04-02 10:31:00")].iloc[0]
    assert len(bad) == int(onb.risk_input_missing_bars) == 31
    atr_receipt = dict(signal="ONB30 2018-04-02 10:31", compression_minutes=k,
        prior15_stored_dates=[str(days[d].date()) for d, _, _ in history[-15:]],
        incomplete_source_candles=len(bad), expected_open_missing_minutes=sum(len(b["missing_expected_open_minutes"]) for b in bad),
        observed_closed_contradiction_minutes=sum(len(b["observed_closed_contradictions"]) for b in bad),
        incomplete_candles_at1715=sum(b["close_label"] == "17:15" for b in bad),
        known_stop_is_NaN=bool(pd.isna(onb.stop_points_at_entry)),
        bad_candles=bad,
        conclusion="The first31-incomplete-candle risk gate independently reproduces from raw quote availability and frozen closures. Ten17:15candles lack17:01; other missing expected-open minutes remain. This is not solely a time-exit phase flag or an inferred holiday closure. No missing price/extreme was filled, and no source risk/returns were recomputed.")
    receipt = dict(preregistration_commit=PREREG, scope="Prepared source/clock and raw input availability diagnosis only; no new account outcomes or economic definitions.",
        prepared_artifact_sha256={n:run.sha(tape/n) for n in ["prepare_receipt.json", "trades.csv", "quality.csv"]},
        DT=dt_receipt, ONB_first_design_risk=atr_receipt,
        limits=["The frozen study retains original UNKNOWN outcomes; this diagnostic does not authorize an uncommitted repair.",
                "A source-open correction needs its own checked amendment and source-match receipt, preserving all original definitions/results.",
                "An absent expected-open minute does not establish its unobserved high/low or its effect on source ATR. Diagnostic owned-feed stop estimates are not admitted risk values.",
                "No2023account outcomes were inspected or computed. DT source metadata counts span the prepared source history without account-performance analysis."])
    run.atomic_json(HERE / "postexecution_source_diagnosis.json", receipt)
    (HERE / "postexecution_source_diagnosis.md").write_text(f"""# Postexecution source diagnosis: adapter error and genuine input gaps differ

Summary: DT has390kind2flat exits checked against the wrong minute phase in the frozen adapter.
Source logic uses next-bar OPEN; the prepared ledger wrongly leaves exit_open=False, so the builder demands CLOSE.
Separately, first-design ONB30 risk rejects31incomplete15-minute lookback candles, reproduced from raw availability.
That includes10candles missing17:01 plus other expected-open holes; it is not explained away as a holiday or a phase flag.
No frozen input, selection, account result or strategy was repaired by this diagnosis.

DT contains1,521trades:712stops,408targets and401kind2flat exits. Its446exit-phase UNKNOWN rows
comprise390flat phase mismatches and56target-through failures; the latter also have their own quality issue,
so they are not another56independent quote absences. Of401flat exits,400are stamped14:56and1at14:57.
Only11happen to match OPEN and CLOSE. On2018-04-11the14:56ledger exit6592equals the owned OPEN6592;
the same minute CLOSE is6588.25and missing_held_bars=0. This establishes an adapter-phase defect for that example.
Source`dual_thrust_test.py:65`returns the next observed bar's OPEN after the14:55flatten trigger.
Prior`codex_portfolio_audit_prepare.py:133`maps the time but drops this OPEN semantic through its default flag.

For ONB30on2018-04-02the source15-date risk bank covers2018-03-09through2018-03-29.
The31incomplete source candles contain{atr_receipt['expected_open_missing_minutes']}missing expected-open native minutes
and{atr_receipt['observed_closed_contradiction_minutes']}observed-in-closed contradictions under the frozen schedule.
The10incomplete17:15candles include an absent17:01bar: raw data onMarch12and14start at17:02.
The other21bad candles contain additional overnight/closing holes. No ATR value, trade return or account outcome
was recomputed. A missing minute's extrema cannot be inferred from neighboring bars to certify sizing.

Reproduction:`postexecution_source_diagnosis.py`; exact counts, minute lists and hashes:
`postexecution_source_diagnosis.json`. The frozen original results remain intact. A causal factual adapter
correction needs a checked amendment, new reproducible tape receipt and separately labeled corrected-model
results; it does not authorize risk-gap weakening or selecting a more favorable path.
""")
    print(json.dumps(dict(DT_flat_phase_mismatches=390, DT_target_unknown=56,
        ONB_incomplete_candles=len(bad), missing_expected_open_minutes=atr_receipt["expected_open_missing_minutes"])))


if __name__ == "__main__":
    main()
