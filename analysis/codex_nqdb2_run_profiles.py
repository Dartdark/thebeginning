"""Reproduce the five preregistered NQDB2 streams without opening a later period.

PYTHONPATH=analysis /workspace/venvs/thebeginning/bin/python \
    analysis/codex_nqdb2_run_profiles.py --design --prereg-sha <SHA>

The recent-period command additionally requires a saved gate JSON containing
``passed: true`` and the same ``prereg_sha``. The root reporting script writes
that gate after assessing every frozen Stage 1 condition.
"""

import argparse
import hashlib
import json
from pathlib import Path
import pickle
import platform
import time

import numpy as np
import pandas as pd

from codex_nqdb2_replay import prepare_features, run, synthetic_checks


PREREG_SHA = "eb7b8b07fd54e8083a13b04f25d1c5b59c68a00b"
SOURCE_SHA256 = "648e15c16cad8c4eae5f10cea7cd78fe01e1cf37be1c63f33df2abcc4a1fabdf"
PROFILES = {
    "S0": dict(apex_safe=False, veto_mode=0, slip_ticks=1.0),
    "S1": dict(apex_safe=False, veto_mode=1, slip_ticks=1.0),
    "A0": dict(apex_safe=True, veto_mode=0, slip_ticks=1.0),
    "A1": dict(apex_safe=True, veto_mode=1, slip_ticks=1.0),
    "E1": dict(apex_safe=True, veto_mode=1, slip_ticks=3.0),
}


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False, default=str) + "\n")


def _summary(t):
    x = t.net.to_numpy(float)
    sd = x.std(ddof=1) if len(x) > 1 else np.nan
    trade_t = float(x.mean() / sd * np.sqrt(len(x))) if sd > 0 else None
    by_year = t.groupby(pd.DatetimeIndex(t.date).year).net.sum()
    return dict(trades=len(t), total_net=float(x.sum()),
                mean_net=float(x.mean()) if len(x) else None,
                win_rate=float((x > 0).mean()) if len(x) else None,
                trade_t=trade_t, positive_years=int((by_year > 0).sum()),
                annual_net={str(y): float(value) for y, value in by_year.items()})


def run_profiles(*, stage, prereg_sha, gate_file=None,
                 cache_path="scratch_data/g24.pkl",
                 output_dir="analysis/outputs/codex_nqdb2_test"):
    if prereg_sha != PREREG_SHA:
        raise ValueError("preregistration SHA does not match the frozen test")
    if stage not in ("design", "recent"):
        raise ValueError("stage must be design or recent")
    if stage == "recent":
        if gate_file is None:
            raise ValueError("recent replay requires a saved passing design gate")
        gate = json.loads(Path(gate_file).read_text())
        if gate.get("passed") is not True or gate.get("prereg_sha") != PREREG_SHA:
            raise ValueError("gate must explicitly pass and match the preregistration SHA")
    source_path = Path("agents/codex/inputs/nqdb2/source.txt")
    source_hash = sha256(source_path)
    if source_hash != SOURCE_SHA256:
        raise ValueError("uploaded source differs from the frozen source hash")
    started = time.perf_counter()
    checks = synthetic_checks()
    cache_path = Path(cache_path)
    cache_hash = sha256(cache_path)
    with cache_path.open("rb") as stream:
        g = pickle.load(stream)
    years = (2018, 2022) if stage == "design" else (2023, pd.Timestamp(g.ts[-1]).year)
    end = pd.Timestamp(years[1] + 1, 1, 1)
    feature_start = time.perf_counter()
    features = prepare_features(g, end=end)
    feature_seconds = time.perf_counter() - feature_start
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    summaries = {}
    for profile, parameters in PROFILES.items():
        profile_start = time.perf_counter()
        trades, profile_features = run(g, years=years, features=features,
                                      allow_post2022=stage == "recent", **parameters)
        elapsed = time.perf_counter() - profile_start
        ledger_path = output / f"{stage}_{profile}.csv"
        orders_path = output / f"{stage}_{profile}_orders.csv"
        trades.to_csv(ledger_path, index=False)
        trades.attrs["orders"].to_csv(orders_path, index=False)
        if profile == "A1":
            profile_features.to_pickle(output / f"{stage}_features.pkl")
        expected = ((trades.raw_exit - trades.raw_entry) * trades.side * 20.0
                    - 7.25 - trades.slippage_usd)
        error = float(np.abs(expected - trades.net).max()) if len(trades) else 0.0
        summary = _summary(trades)
        audit = dict(
            stage=stage, profile=profile, prereg_sha=PREREG_SHA,
            years=list(map(int, years)), parameters=parameters, elapsed_seconds=elapsed,
            cache_path=str(cache_path), cache_sha256=cache_hash,
            source_sha256=source_hash, net_already_final=True,
            commission_per_NQ=7.25, commission_total=float(7.25 * len(trades)),
            slippage_total=float(trades.slippage_usd.sum()),
            target_through_points=1.0, declared_session_end=2400,
            volume_proxy="total exported volume; not MC up-volume parity",
            censored=trades.attrs["censored"], censored_positions=len(trades.attrs["censored"]),
            order_counts=trades.attrs["orders"].status.value_counts().to_dict(),
            ledger_net_reconciliation_max_abs=error,
            cross_date_trades=int(trades.carry.sum()),
            first_entry=str(trades.date.min()) if len(trades) else None,
            last_exit=str(trades.exit_date.max()) if len(trades) else None,
            ledger_sha256=sha256(ledger_path), order_ledger_sha256=sha256(orders_path),
            **summary,
        )
        if not np.isfinite(error) or error > 1e-7:
            raise AssertionError(f"{profile} raw/slipped ledger does not reconcile")
        _json(output / f"{stage}_{profile}_audit.json", audit)
        summaries[profile] = audit
        print(f"{stage} {profile}: n={summary['trades']} net=${summary['total_net']:,.2f} "
              f"positive_years={summary['positive_years']} t={summary['trade_t']} "
              f"censored={audit['censored_positions']} seconds={elapsed:.2f}", flush=True)
    manifest = dict(
        stage=stage, prereg_sha=PREREG_SHA, years=list(map(int, years)),
        cache_path=str(cache_path), cache_sha256=cache_hash,
        cache_first_date=str(pd.Timestamp(g.ts[0])), cache_last_date=str(pd.Timestamp(g.ts[-1])),
        source_sha256=source_hash, python=platform.python_version(),
        numpy=np.__version__, pandas=pd.__version__,
        feature_seconds=feature_seconds, feature_rows=len(features),
        elapsed_seconds=time.perf_counter() - started, synthetic_checks=checks,
        gate_path=str(gate_file) if gate_file is not None else None,
        gate_sha256=sha256(gate_file) if gate_file is not None else None,
        profiles={name: {k: value[k] for k in ("trades", "total_net", "trade_t", "positive_years", "censored_positions")}
                  for name, value in summaries.items()},
    )
    _json(output / f"{stage}_manifest.json", manifest)
    return summaries


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--design", action="store_true")
    group.add_argument("--recent", action="store_true")
    parser.add_argument("--prereg-sha", required=True)
    parser.add_argument("--gate-file")
    parser.add_argument("--cache", default="scratch_data/g24.pkl")
    parser.add_argument("--output", default="analysis/outputs/codex_nqdb2_test")
    args = parser.parse_args()
    run_profiles(stage="design" if args.design else "recent", prereg_sha=args.prereg_sha,
                 gate_file=args.gate_file, cache_path=args.cache, output_dir=args.output)
