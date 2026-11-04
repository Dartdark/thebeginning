"""Frozen, research-only adapters for existing FC2B/ST/PT/VCS source trades.

No signals are generated and no return/account study runs at import. Execution
requires the exact committed script, config and its frozen files. Source prices
are normalized to one MNQ; historical report fills remain conditional, not tick
verification. Missing native prices remain missing and every inference is kept.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "analysis/codex_eval_extra_ledgers_20261104.py"
DEST = "agents/codex/runtime/eval_audit_20261104/ledgers"
SPECS = {
    "FC2B": dict(csv="checks/candidates/fc_2b/mc_v2_trades_all.csv",
        workbook="mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute FC 2B v2.xlsx",
        source="checks/candidates/fc_2b/FC_2B_v2.txt", bar=1, entry="open",
        stop="fixed 100 points; dynamic trail/BE changes exits, not initial risk"),
    "ST": dict(csv="checks/candidates/swing_target/mc_trades_v3.csv",
        workbook="mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Swing Target v3.xlsx",
        source="funded_strategies/NQ_Swing_Target_v3.txt", bar=1, entry="touch_inferred",
        stop="0.7 * previous 20 banked RTH ranges; source missing-15:00 fallback retained"),
    "PT": dict(csv="checks/candidates/papertrend/mc_trades_claude.csv",
        workbook="mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes PAPERTREND v2 claude.xlsx",
        source="checks/candidates/papertrend/PAPERTREND_v2_claude.txt", bar=5, entry="open",
        stop="2.0 * previous 14 RTH ranges banked at observed 15:00 only"),
    "VCS": dict(csv=None,
        workbook="mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Vol-Control Sell Flow.xlsx",
        source="funded_strategies/NQ_Vol_Control_Sell.txt", bar=5, entry="open",
        stop="0.25 * previous 15 weekday calendar TR on source five-minute chart"),
}


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def _settings(key):
    d = pd.read_excel(ROOT / SPECS[key]["workbook"], sheet_name="Settings", header=None)
    return {str(k).strip(): v for k, v in zip(d[0], d[1])}


def source_manifest():
    """Source/access/settings metadata only; this does not load source returns."""
    out = {}
    for key, spec in SPECS.items():
        files = [spec["workbook"], spec["source"]] + ([spec["csv"]] if spec["csv"] else [])
        settings = _settings(key)
        out[key] = dict(spec, files={p: sha(ROOT / p) for p in files},
            source_sampling_start=str(settings.get("Start Date")),
            source_sampling_end=str(settings.get("End Date")),
            compression=str(settings.get("Compression")),
            bar_magnifier=str(settings.get("Bar Magnifier")))
    return out


def verify_preregistration(config_path, commit):
    if not commit or len(commit) != 40:
        raise ValueError("Exact 40-character preregistration commit is required")
    cp = Path(config_path).resolve()
    cfg = json.loads(cp.read_text())
    frozen = [SCRIPT, str(cp.relative_to(ROOT)), "analysis/grid24.py"] + cfg.get("frozen_files", [])
    for name in dict.fromkeys(frozen):
        if subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=ROOT) != (ROOT / name).read_bytes():
            raise ValueError("Changed preregistered file: " + name)
    for name, expected in cfg.get("input_sha256", {}).items():
        if sha(ROOT / name) != expected:
            raise ValueError("Changed registered input: " + name)
    # Raw source ledgers/settings/code must be pinned, not merely present.
    for spec in SPECS.values():
        names = [spec["source"], spec["workbook"]] + ([spec["csv"]] if spec["csv"] else [])
        for name in names:
            if name not in cfg.get("input_sha256", {}):
                raise ValueError("Missing source hash in preregistration: " + name)
    return cfg


def _mc_timestamp(frame):
    dates = pd.to_datetime(frame["Date"])
    # Current files contain combined Date+Time. Date-only exports use Time.
    for i in frame.index:
        if dates.loc[i] == dates.loc[i].normalize() and pd.notna(frame.loc[i, "Time"]):
            value = frame.loc[i, "Time"]
            if isinstance(value, str) and ":" in value:
                try:
                    clock = pd.Timestamp(value)
                    offset = pd.Timedelta(hours=clock.hour, minutes=clock.minute, seconds=clock.second)
                except (ValueError, TypeError):
                    offset = pd.to_timedelta(value)
            elif hasattr(value, "hour"):
                offset = pd.Timedelta(hours=value.hour, minutes=value.minute, seconds=value.second)
            elif isinstance(value, (float, int)):
                offset = pd.Timedelta(days=float(value) % 1)
            else:
                raise ValueError("Unrecognized workbook time: " + str(value))
            dates.loc[i] = dates.loc[i].normalize() + offset
    return dates


def read_source_trades(key):
    spec = SPECS[key]
    if spec["csv"]:
        raw = pd.read_csv(ROOT / spec["csv"])
        for stem, datecol, timecol in [("entry_stamp", "date", "t_in"), ("exit_stamp", "exit_date", "t_out")]:
            dates = pd.to_datetime(raw[datecol]).dt.normalize()
            times = pd.to_numeric(raw[timecol], errors="raise").astype(int)
            if ((times % 100 >= 60) | (times // 100 >= 24)).any():
                raise ValueError(key + ": invalid HHMM")
            raw[stem] = dates + pd.to_timedelta(times // 100 * 60 + times % 100, unit="m")
        raw["source_qty"] = 1.
    else:
        rows = pd.read_excel(ROOT / spec["workbook"], sheet_name="List of Trades", header=2)
        rows = rows[rows["Type"].astype(str).str.startswith(("Entry", "Exit"))].copy()
        if len(rows) % 2 or not rows["Type"].astype(str).iloc[::2].str.startswith("Entry").all() or not rows["Type"].astype(str).iloc[1::2].str.startswith("Exit").all():
            raise ValueError(key + ": unpaired/unfinished workbook trade; cannot infer a flat ending")
        ent, ex = rows.iloc[::2].reset_index(drop=True), rows.iloc[1::2].reset_index(drop=True)
        raw = pd.DataFrame(dict(entry_stamp=_mc_timestamp(ent), exit_stamp=_mc_timestamp(ex),
            side=np.where(ent["Type"].str.contains("Long"), 1, -1),
            entry=ent["Price"].to_numpy(float), exit=ex["Price"].to_numpy(float),
            kind=ex["Signal"].astype(str), source_qty=ent["Contracts"].to_numpy(float)))
    required = ["entry_stamp", "exit_stamp", "entry", "exit", "side", "kind"]
    if raw[required].isna().any().any() or not raw.side.isin([-1, 1]).all():
        raise ValueError(key + ": missing source trade fields")
    if (raw.exit_stamp < raw.entry_stamp).any():
        raise ValueError(key + ": exit precedes entry")
    raw["source_row"] = np.arange(len(raw))
    return raw


def classify_exit(key, label):
    label = str(label)
    if label in {"Stop Loss", "BreakEven Stop", "Trailing Stop"}:
        return 0, False
    if label == "Profit Target":
        return 1, False
    if key == "FC2B" and label in {"FT.LX.stp", "FT.SX.stp"}:
        return 0, False
    if key == "FC2B" and label in {"FT.LX.eod", "FT.SX.eod", "FT.LX.mkt", "FT.SX.mkt"}:
        return 2, True
    if key == "ST" and label in {"ST.LX", "ST.SX", "ST.LX.hol", "ST.SX.hol"}:
        return 2, True
    if key == "PT" and label in {"PT.LX", "PT.SX"}:
        return 2, False
    if key == "PT" and label in {"PT.LX.hol", "PT.SX.hol"}:
        return 2, True
    if key == "VCS" and label == "VolCtl SX":
        return 2, False
    raise ValueError(f"{key}: unclassified source exit {label!r}")


def stop_features(grid, key, market_closures=None):
    """Past-only formula, never inferred from realized stop/BE exit prices.

    Returns estimated source risk on the owned feed plus explicit missing-bar
    counts in its lookback. A finite estimate does not prove report-feed parity.
    Source five-minute candles require every constituent minute; missing bars
    remain absent. ST's prior partial-day range is retained only with the source
    next-date-before-08:31 backstop. PT banks only an observed15:00 candle.
    """
    if key == "FC2B":
        return np.full(grid.D, 100.), np.zeros(grid.D, int)
    out, gaps = np.full(grid.D, np.nan), np.full(grid.D, -1, int)
    if key in {"ST", "PT"}:
        history = []
        n, mult = (20, .7) if key == "ST" else (14, 2.)
        for d in range(grid.D):
            if len(history) >= n:
                out[d] = mult * np.mean([x[0] for x in history[-n:]])
                gaps[d] = sum(x[1] for x in history[-n:])
            if not np.isfinite(grid.c[d, 511]) or not np.isfinite(grid.o[d, 511]):
                continue
            complete_close = np.isfinite(grid.c[d, 900])
            if complete_close:
                end = 900
            elif key == "ST" and d + 1 < grid.D:
                next_seen = np.flatnonzero(np.isfinite(grid.c[d + 1]))
                if not len(next_seen) or next_seen[0] >= 511:
                    continue
                valid = np.flatnonzero(np.isfinite(grid.c[d, 511:901]))
                if not len(valid):
                    continue
                end = int(valid[-1]) + 511
            else:
                continue
            h, l, c = grid.h[d, 511:end + 1], grid.l[d, 511:end + 1], grid.c[d, 511:end + 1]
            good = np.isfinite(grid.o[d, 511:end + 1]) & np.isfinite(h) & np.isfinite(l) & np.isfinite(c)
            # PT's first candle includes08:31..08:35; no additional range
            # enters the source five-minute RTH window outside this slice.
            if good.any():
                history.append((float(np.nanmax(h) - np.nanmin(l)), int((~good).sum())))
        return out, gaps
    if key != "VCS":
        raise ValueError(key)
    from codex_eval_paths_20261104 import source_calendar_atr, civil_closure_mask
    atr, gaps = source_calendar_atr(grid, 5, 15, 0,
        civil_closure_mask(grid, "NQ", market_closures or []))
    return .25 * atr, gaps


def _native_arrays(grid):
    return {name: getattr(grid, name).ravel() for name in ("o", "h", "l", "c")}


def _index(grid, stamp):
    stamp = pd.Timestamp(stamp)
    day = int(np.searchsorted(grid.dates, int(stamp.strftime("%Y%m%d"))))
    if day >= grid.D or grid.dates[day] != int(stamp.strftime("%Y%m%d")):
        return None
    return day * 1440 + stamp.hour * 60 + stamp.minute


def _stamp(grid, index):
    return pd.Timestamp(grid.ts[index // 1440]) + pd.Timedelta(minutes=index % 1440)


def _infer(grid, arrays, stamp, price, bar, phase, lower=0):
    end = _index(grid, stamp)
    if end is None:
        return pd.Timestamp(stamp), False, phase, False
    bar_begin = max(0, end - bar + 1)
    begin = max(bar_begin, lower)
    # ``lower`` constrains a resting order's search, never a known market clock.
    candidate = end if phase == "close" else bar_begin
    col = "c" if phase == "close" else "o"
    exact = phase in {"open", "close"} and np.isclose(arrays[col][candidate], price, rtol=0, atol=1e-7)
    if exact:
        return _stamp(grid, candidate), True, phase, True
    if phase in {"open", "close"}:
        # Market/close execution has a known clock. A matching price elsewhere
        # in the candle cannot move it before its decision or add unstated
        # latency. Preserve the expected clock and let admission mark UNKNOWN.
        return _stamp(grid, candidate), False, phase, False
    touch = np.flatnonzero((arrays["l"][begin:end + 1] <= price + 1e-7) & (arrays["h"][begin:end + 1] >= price - 1e-7))
    # Keep source time if no observed touch: never move to a different candle.
    found = bool(len(touch))
    at = begin + int(touch[0]) if found else candidate
    return _stamp(grid, at), found, "touch_inferred", False


def selftest():
    """Synthetic clock/kind checks only; no source data or returns loaded."""
    from types import SimpleNamespace
    g = SimpleNamespace(dates=np.array([20200102]), D=1,
        ts=np.array([np.datetime64("2020-01-02")]))
    a = {k: np.full(1440, np.nan) for k in ("o", "h", "l", "c")}
    # A 10:00 close order cannot move to an earlier09:57 touch of100.
    for k in a:
        a[k][597] = 100.
    a["c"][600] = 101.
    t, matched, hint, exact = _infer(g, a, "2020-01-02 10:00", 100., 5, "close")
    assert t == pd.Timestamp("2020-01-02 10:00") and not matched and hint == "close" and not exact
    # A known09:56 open cannot acquire unstated later fill latency.
    a["o"][596] = 101.
    t, matched, hint, exact = _infer(g, a, "2020-01-02 10:00", 100., 5, "open")
    assert t == pd.Timestamp("2020-01-02 09:56") and not matched and hint == "open" and not exact
    # Only a resting stop/limit is allowed to use the09:57 touch.
    t, matched, hint, exact = _infer(g, a, "2020-01-02 10:00", 100., 5, "touch_inferred")
    assert t == pd.Timestamp("2020-01-02 09:57") and matched and hint == "touch_inferred" and not exact
    # Even an entry lower-bound later in the candle cannot move its source open.
    a["o"][596] = a["o"][598] = 100.
    t, matched, hint, exact = _infer(g, a, "2020-01-02 10:00", 100., 5, "open", lower=598)
    assert t == pd.Timestamp("2020-01-02 09:56") and matched and hint == "open" and exact
    assert classify_exit("FC2B", "FT.LX.stp") == (0, False)
    assert classify_exit("ST", "BreakEven Stop") == (0, False)
    assert classify_exit("ST", "Profit Target") == (1, False)
    assert classify_exit("PT", "PT.SX") == (2, False)
    assert classify_exit("VCS", "VolCtl SX") == (2, False)
    try:
        classify_exit("FC2B", "unknown")
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown source exit accepted")
    return {"status": "PASS", "scope": "synthetic only; fixed source clocks and exit kinds; no historical data or returns"}


def normalize_key(key, grid, sampling_start=None, sampling_end=None, market_closures=None):
    """Call only from the preregistration-checked build entry point below."""
    spec, arrays = SPECS[key], _native_arrays(grid)
    risk, risk_gaps = stop_features(grid, key, market_closures)
    settings = _settings(key)
    sample_a = pd.Timestamp(settings["Start Date"])
    sample_b = pd.Timestamp(settings["End Date"])
    start = pd.Timestamp(sampling_start) if sampling_start else pd.Timestamp(grid.ts[0])
    end = pd.Timestamp(sampling_end) + pd.Timedelta(days=1) if sampling_end else pd.Timestamp(grid.ts[-1]) + pd.Timedelta(days=1)
    rows = []
    raw = read_source_trades(key)
    for r in raw.itertuples(index=False):
        if r.exit_stamp < start or r.entry_stamp >= end:
            continue
        kind, exit_open = classify_exit(key, r.kind)
        ent, entry_touch, hint, entry_exact = _infer(grid, arrays, r.entry_stamp, r.entry, spec["bar"], spec["entry"])
        ei = _index(grid, ent)
        xphase = "touch_inferred" if kind != 2 else ("open" if exit_open else "close")
        ext, exit_touch, xhint, exit_exact = _infer(grid, arrays, r.exit_stamp, r.exit, spec["bar"], xphase, ei or 0)
        xi = _index(grid, ext)
        outside = ei is None or xi is None or xi < ei
        missing = -1 if outside else int((~(np.isfinite(arrays["o"][ei:xi+1]) & np.isfinite(arrays["h"][ei:xi+1]) & np.isfinite(arrays["l"][ei:xi+1]) & np.isfinite(arrays["c"][ei:xi+1]))).sum())
        d = ei // 1440 if ei is not None else None
        minute = ext.hour * 60 + ext.minute
        session = ext.normalize() + pd.Timedelta(days=int(minute > 1020))
        source_gross = (r.exit - r.entry) * r.side * 20.
        if hasattr(r, "gross") and not np.isclose(float(r.gross), source_gross, rtol=0, atol=.011):
            raise ValueError(f"{key}: source row{r.source_row} price/gross-unit mismatch")
        rows.append(dict(key=key, market="NQ", date=session.date().isoformat(),
            entry_at=ent, exit_at=ext, j0=(ent.hour*60+ent.minute-1021)%1440,
            j1=(minute-1021)%1440, side=int(r.side), qty=1, entry=float(r.entry), exit=float(r.exit),
            kind=kind, gross=source_gross/10., fee_units=1., slippage_one_tick=.5*(1+(kind != 1)),
            missing_held_bars=missing, exit_after_1559=minute>959 and minute<=1020,
            stop_points_at_entry=float(risk[d]) if d is not None and risk_gaps[d] == 0 else np.nan,
            stop_points_owned_feed_estimate=float(risk[d]) if d is not None else np.nan,
            risk_input_missing_bars=int(risk_gaps[d]) if d is not None else -1,
            risk_formula=spec["stop"], risk_feed_parity="owned-minute formula reconstruction, not original-report-feed certification",
            entry_phase_hint=hint, exit_open=exit_open, entry_touch=entry_touch, exit_touch=exit_touch,
            source_sampling_start=sample_a.isoformat(), source_sampling_end=sample_b.isoformat(),
            source_entry_stamp=r.entry_stamp, source_exit_stamp=r.exit_stamp,
            source_exit_kind=str(r.kind), source_row=int(r.source_row), source_qty=float(r.source_qty),
            source_bar_minutes=spec["bar"], entry_phase_exact=entry_exact,
            exit_phase_exact=exit_exact, exit_phase_hint=xhint, source_feed_outside_owned_grid=outside,
            cross_account_session=(ent.normalize()+pd.Timedelta(days=int(ent.hour*60+ent.minute>1020))) != session,
            target_trade_through_1point=(bool(arrays["h"][xi]>=r.exit+1) if r.side>0 else bool(arrays["l"][xi]<=r.exit-1)) if kind==1 and xi is not None else None,
            source_inference="existing MultiCharts source tickets; native minute timing inferred from owned OHLC; no new signals"))
    return pd.DataFrame(rows)


def build(config_path, commit, grids, keys=None, output_dir=None):
    cfg = verify_preregistration(config_path, commit)
    output = ROOT / (output_dir or DEST)
    output.mkdir(parents=True, exist_ok=True)
    receipts = {}
    for key in (keys or SPECS):
        ls = cfg.get("ledgers", {}).get(key, {})
        data = normalize_key(key, grids["NQ"], ls.get("sampling_start"), ls.get("sampling_end"), cfg.get("market_closures", []))
        path = output / f"{key}_unit_ledger.csv"
        data.to_csv(path, index=False)
        receipts[key] = dict(path=str(path.relative_to(ROOT)), sha256=sha(path), rows=len(data),
            missing_risk=int(data.stop_points_at_entry.isna().sum()),
            missing_held_trades=int((data.missing_held_bars != 0).sum()),
            entry_touch_failures=int((~data.entry_touch).sum()), exit_touch_failures=int((~data.exit_touch).sum()))
    manifest = dict(preregistration_commit=commit, adapter_sha256=sha(ROOT / SCRIPT),
        sources=source_manifest(), ledgers=receipts, status="conditional OHLC/report normalization; independent economic verification pending")
    (output / "extra_ledgers_receipt.json").write_text(json.dumps(manifest, indent=2, default=str) + "\n")
    return receipts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["manifest", "selftest", "build"])
    parser.add_argument("--config")
    parser.add_argument("--prereg-commit")
    parser.add_argument("--keys", nargs="+", choices=list(SPECS))
    args = parser.parse_args()
    if args.mode == "selftest":
        print(json.dumps(selftest(), indent=2))
        return
    if args.mode == "manifest":
        print(json.dumps(source_manifest(), indent=2, default=str))
        return
    if not args.config:
        parser.error("--config required for build")
    cfg = verify_preregistration(args.config, args.prereg_commit)
    from codex_eval_paths_20261104 import _grid, _files_for_market
    grid = _grid("NQ", _files_for_market("NQ", cfg.get("market_sources", {}).get("NQ")))
    print(json.dumps(build(args.config, args.prereg_commit, {"NQ": grid}, args.keys), indent=2))


if __name__ == "__main__":
    main()
