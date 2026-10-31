"""No-return source/data audit for the user's overnight TickRSV description.

Screenshots are user-supplied claims; arithmetic consistency is not validation.
This script never computes candidate signals/returns or loads a research cache.
"""
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_overnight_tickrsv_review"
SOURCE = ROOT / "agents/codex/inputs/overnight_tickrsv/source.txt"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def endpoints(path):
    """Bounded header/first/last inspection; does not prove interior coverage."""
    with path.open(newline="") as f:
        reader = csv.reader(f)
        columns, first = next(reader), next(reader)
    with path.open("rb") as f:
        f.seek(max(0, path.stat().st_size - 16384))
        lines = f.read().decode().splitlines()
    last = next(csv.reader([next(x for x in reversed(lines) if x.strip())]))
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                columns=columns, first=dict(zip(columns[:2], first[:2])),
                last=dict(zip(columns[:2], last[:2])))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    patterns = dict(nq_day="NQ_1min_20??.csv", nq_overnight="NQ_1min_ON_*.csv",
                    bridge_orderflow="OF_1min_*.csv", vix="VIX_daily.csv")
    inventory = {k: [endpoints(p) for p in sorted((ROOT / "data").glob(v))]
                 for k, v in patterns.items()}
    claims = dict(source="User-provided MultiCharts screenshots; independently unverified",
        reported_start="2017-09-12", reported_end="2026-07-07", reported_trades=547,
        reported_long=547, reported_short=0, reported_net=211405.0,
        reported_gross_profit=420280.0, reported_gross_loss=208875.0,
        reported_win_percent=59.96, reported_pf=2.01,
        reported_max_strategy_dd=16515.0, reported_max_close_to_close_dd=12820.0,
        costs_and_exact_inputs_verified=False)
    claims.update(arithmetic_net=claims["reported_gross_profit"]-claims["reported_gross_loss"],
                  arithmetic_pf=claims["reported_gross_profit"]/claims["reported_gross_loss"],
                  arithmetic_avg_trade=claims["reported_net"]/claims["reported_trades"])
    source = SOURCE.read_text()
    context = json.loads((SOURCE.parent / "context.json").read_text())
    result = dict(verdict="NEEDS DATA", source_sha256=digest(SOURCE), source_bytes=SOURCE.stat().st_size,
        code_supplied=False, description_supplied=True, return_trials=0,
        candidate_signals_computed=False, candidate_returns_computed=False,
        portfolio_simulations=0, research_caches_built=0,
        reported_default_vix_ma=20, reported_selected_vix_ma=25,
        active_stop=False, source_admits_many_tests="After many tests" in source,
        mandatory_missing=["Exact PowerLanguage source and actual report inputs",
            "Chart/feed/session/timestamp and Build volume on settings",
            "Exact-version Excel Settings and trade list, costs and roll treatment",
            "Confirmed historical original-chart UpTicks/DownTicks, or proof owned OF fields match"],
        data_inventory=inventory, inventory_limit="Header and endpoints only; not complete-window certification",
        split_volume_caution="Owned Bridge upvol/downvol are documented aggressor buy/sell volume. Their names/export via UpTicks/DownTicks do not establish parity with the described tick-direction proxy.",
        known_coverage_example="OF_1min_2020_2.csv ends 2020-06-30 at10:11ET, before that day's required flow window.",
        account_scope={k:"Not scored: exact signals/data/source unresolved; no performance inferred from another account size"
                       for k in ("50K evaluation", "150K evaluation", "50K funded", "150K funded", "Personal ladder/full portfolio")},
        account_calendar_caution="Builder brief overnight wording conflicts with funded README allowing evening-to-morning holds before15:59CT. 18:00-04:00ET equals17:00-03:00CT, and does not cross that daily flat deadline; do not reject solely for calendar-date rollover. Resolve policy before account gate.",
        screenshot_claims=claims, context=context,
        packages={p:importlib.metadata.version(p) for p in ("numpy","pandas","numba","openpyxl","scipy","scikit-learn")})
    (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
    (SOURCE.parent/"screenshot_claims.json").write_text(json.dumps(claims,indent=2)+"\n")
    print(json.dumps(dict(verdict=result["verdict"], source_sha256=result["source_sha256"],
        supplied_code=False, return_trials=0, inventory_counts={k:len(v) for k,v in inventory.items()},
        screenshot_net_arithmetic=claims["arithmetic_net"], screenshot_avg=claims["arithmetic_avg_trade"]),indent=2))


if __name__ == "__main__":
    main()
