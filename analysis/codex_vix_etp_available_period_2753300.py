"""Frozen, limited XIV/VIXY proxy replay. Run `selftest`, then `run`; no live connections."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

import numpy as np
import pandas as pd

import metrics
import resampling
import montecarlo

CAPITAL = 100_000.0
OUT = Path("analysis/outputs/codex_vix_etp_available_period_2753300")
PLAN = Path("agents/codex/plans/vix_etp_available_period_2753300.md")
ROOT = Path("/workspace/vix2753300_acquisition")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def target(held, basis):
    if basis > .08:
        return "XIV"
    if basis < -.08:
        return "VIXY"
    if held == "XIV" and basis >= .06:
        return held
    if held == "VIXY" and basis <= -.06:
        return held
    return "CASH"


def replay(d, spread=.0015, fee=.002, hold=None):
    cash = CAPITAL
    held, quantity, position = "CASH", 0., None
    pending = "CASH"
    fills, trades, daily = [], [], []
    for i, (day, r) in enumerate(d.iterrows()):
        attribution = {"XIV": 0., "VIXY": 0.}
        if i and held != "CASH":
            attribution[held] += quantity * (r[held + "_open"] - d.iloc[i - 1][held + "_close"])

        def sell(price, terminal=False):
            nonlocal cash, held, quantity, position
            raw = quantity * price
            spread_cost, commission = raw * spread, raw * (1 - spread) * fee
            proceeds = raw - spread_cost - commission
            attribution[held] -= spread_cost + commission
            fills.append(dict(date=day, signal_date=day if terminal else d.index[i - 1], asset=held,
                              action="SELL", timing="terminal_close" if terminal else "next_open",
                              price=price, quantity=quantity, cashflow=proceeds,
                              spread_cost=spread_cost, commission=commission))
            trades.append(dict(asset=held, entry_date=position["date"], exit_date=day,
                               entry_price=position["price"], exit_price=price, quantity=quantity,
                               gross=quantity * (price - position["price"]),
                               net=proceeds - position["cash"],
                               terminal=terminal))
            cash += proceeds
            held, quantity, position = "CASH", 0., None

        if i and pending != held:
            if held != "CASH":
                sell(float(r[held + "_open"]))
            if pending != "CASH" and i < len(d) - 1:
                held = pending
                price = float(r[held + "_open"])
                allocated = cash
                quantity = cash / (price * (1 + spread) * (1 + fee))
                raw = quantity * price
                spread_cost, commission = raw * spread, raw * (1 + spread) * fee
                attribution[held] -= spread_cost + commission
                fills.append(dict(date=day, signal_date=d.index[i - 1], asset=held, action="BUY",
                                  timing="next_open", price=price, quantity=quantity, cashflow=-cash,
                                  spread_cost=spread_cost, commission=commission))
                position = dict(date=day, price=price, cash=allocated)
                cash = 0.
        if held != "CASH":
            attribution[held] += quantity * (r[held + "_close"] - r[held + "_open"])
        if i == len(d) - 1 and held != "CASH":
            sell(float(r[held + "_close"]), terminal=True)
        nav = cash + (quantity * r[held + "_close"] if held != "CASH" else 0.)
        daily.append(dict(date=day, nav=nav, asset=held, XIV_pnl=attribution["XIV"],
                          VIXY_pnl=attribution["VIXY"], basis=r.basis,
                          front_contract=r.get("contract", "synthetic")))
        pending = hold if hold is not None else target(held, float(r.basis))
    daily = pd.DataFrame(daily).set_index("date")
    daily["pnl"] = daily.nav.diff().fillna(daily.nav.iloc[0] - CAPITAL)
    trades, fills = pd.DataFrame(trades), pd.DataFrame(fills)
    if len(trades):
        assert np.isclose(trades.net.sum(), daily.pnl.sum(), atol=1e-7)
        assert np.isclose(trades.gross.sum() - fills.commission.sum() - fills.spread_cost.sum(),
                          daily.pnl.sum(), atol=1e-7)
    assert np.allclose(daily.XIV_pnl + daily.VIXY_pnl, daily.pnl, atol=1e-7)
    if len(fills):
        assert (fills.loc[fills.timing == "next_open", "signal_date"] <
                fills.loc[fills.timing == "next_open", "date"]).all()
    return daily, trades, fills


def selftest():
    assert target("CASH", .08) == "CASH"
    assert target("CASH", -.08) == "CASH"
    assert target("XIV", .06) == "XIV"
    assert target("VIXY", -.06) == "VIXY"
    assert target("XIV", -.09) == "VIXY"
    assert target("VIXY", .09) == "XIV"
    days = pd.date_range("2018-01-01", periods=4)
    d = pd.DataFrame(dict(basis=[.1, 0., 0., 0.], XIV_open=[100., 100., 10., 10.],
                          XIV_close=[100., 100., 10., 10.], VIXY_open=100., VIXY_close=100.), index=days)
    p, t, f = replay(d, 0., 0.)
    assert p.nav.iloc[-1] == 10_000., "The old holding must bear its overnight gap"
    assert f.iloc[0].date == days[1] and f.iloc[1].date == days[2]
    d["XIV_open"] = d["XIV_close"] = 100.
    d["basis"] = [.1, -.1, 0., 0.]
    p, t, f = replay(d)
    assert len(t) == 2 and len(f) == 4
    assert p.nav.iloc[-1] < CAPITAL and (f.commission > 0).all()
    # Final-date entry is forbidden, including when first signal occurs on the penultimate session.
    d["basis"] = [0., 0., .1, 0.]
    p, t, f = replay(d)
    assert len(f) == 0 and p.nav.iloc[-1] == CAPITAL
    print("Synthetic checks PASS: strict thresholds, causal fills, gaps, switches, expenses, terminal entry guard.")


def inputs():
    xfile = ROOT / "xiv_public_table_snapshot.csv"
    x = pd.read_csv(xfile, parse_dates=["date"]).set_index("date")
    vfile = Path("data/VIXY_daily.csv")
    v = pd.read_csv(vfile, parse_dates=["date"]).set_index("date")
    days = v.loc[x.index.min():x.index.max()].index
    assert len(days) == 364 and days.equals(x.index), "Incomplete/out-of-order public XIV snapshot"
    assert np.allclose(v.loc[days, "close"], v.loc[days, "adjclose"]), "VIXY adjustment scale unresolved"
    spotfile = Path("data/VIX_daily.csv")
    spot = pd.read_csv(spotfile, parse_dates=["DATE"]).set_index("DATE")
    d = pd.DataFrame(index=days)
    for name, frame in [("XIV", x), ("VIXY", v)]:
        for col in ["open", "close"]:
            d[name + "_" + col] = frame.loc[days, col]
    d["spot"] = spot.loc[days, "CLOSE"]
    hashes = {str(p): sha(p) for p in [xfile, vfile, spotfile]}
    contracts = []
    for p in sorted((ROOT / "raw_vx").glob("VX_*.csv")):
        m = re.fullmatch(r"VX_(\d{4}-\d{2}-\d{2})\.csv", p.name)
        if not m:
            continue
        expiry = pd.Timestamp(m[1])
        if not days.min() < expiry <= days.max() + pd.Timedelta(days=40):
            continue
        t = pd.read_csv(p, parse_dates=["Trade Date"]).set_index("Trade Date")
        assert t.index.is_unique
        contracts.append((expiry, p.name, t))
        hashes[str(p)] = sha(p)
    selected = []
    for day in days:
        eligible = [(expiry, name, t) for expiry, name, t in contracts if expiry > day]
        expiry, name, t = min(eligible, key=lambda z: z[0])
        settle = float(t.loc[day, "Settle"])
        assert 0 < settle < 100, "Native scale invalid for this modern window"
        selected.append((name, expiry, settle))
    d[["contract", "expiry", "settle"]] = pd.DataFrame(selected, index=days)
    d["settle"] = d.settle.astype(float)
    assert np.isfinite(d.select_dtypes("number").to_numpy()).all()
    assert (d.select_dtypes("number") > 0).all().all()
    d["basis"] = (d.settle - d.spot) / d.spot
    return d, hashes


def describe(daily, trades):
    result = metrics.perf(daily.pnl, trades.net if len(trades) else [], capital=CAPITAL)
    returns = daily.nav.pct_change().fillna(0.)
    result.update(total_return=float(daily.nav.iloc[-1] / CAPITAL - 1),
                  cagr=float((daily.nav.iloc[-1] / CAPITAL) ** (252 / len(daily)) - 1),
                  percent_max_dd=float((daily.nav / daily.nav.cummax() - 1).min()),
                  return_sharpe=float(returns.mean() / returns.std() * np.sqrt(252)) if returns.std() else None)
    return result


def run():
    selftest()
    assert subprocess.check_output(["git", "status", "--porcelain", "--", str(PLAN), __file__], text=True) == "", "Commit plan and code before returns"
    OUT.mkdir(parents=True, exist_ok=True)
    d, hashes = inputs()
    d.to_csv(OUT / "signal_inputs.csv", index_label="date")
    runs = {}
    specs = [("switch", .0015, .002, None), ("hold_XIV", .0015, .002, "XIV"),
             ("hold_VIXY", .0015, .002, "VIXY"), ("switch_double_cost", .003, .004, None),
             ("switch_zero_cost_bridge", 0., 0., None)]
    byyear, legs = [], []
    for name, spread, fee, hold in specs:
        daily, trades, fills = replay(d, spread, fee, hold)
        daily.to_csv(OUT / f"{name}_daily.csv")
        trades.to_csv(OUT / f"{name}_trades.csv", index=False)
        fills.to_csv(OUT / f"{name}_fills.csv", index=False)
        runs[name] = describe(daily, trades)
        runs[name].update(gross_pnl=float(trades.gross.sum()), commissions=float(fills.commission.sum()),
                          spread_cost=float(fills.spread_cost.sum()), net_pnl=float(trades.net.sum()))
        if name == "switch":
            for year, frame in daily.groupby(daily.index.year):
                first_location = daily.index.get_loc(frame.index[0])
                start_nav = CAPITAL if first_location == 0 else daily.nav.iloc[first_location - 1]
                byyear.append(dict(year=int(year), pnl=float(frame.pnl.sum()),
                                   return_pct=float(frame.nav.iloc[-1] / start_nav - 1)))
            for asset in ["XIV", "VIXY"]:
                selected = trades[trades.asset == asset]
                m = metrics.perf(daily[asset + "_pnl"], selected.net, capital=CAPITAL)
                legs.append(dict(asset=asset, net_pnl=float(selected.net.sum()), **m))
            resampling.bootstrap(daily.pnl, n=5000, block=10, seed=2753300, capital=CAPITAL).to_csv(OUT / "bootstrap.csv")
            mc = montecarlo.daily_mc(daily.pnl, n=5000, block=10, seed=2753300, trail=1e100)
            mc.pop("p_trail_hit", None)
            (OUT / "descriptive_mc.json").write_text(json.dumps(mc, indent=2) + "\n")
    pd.DataFrame(byyear).to_csv(OUT / "by_year.csv", index=False)
    pd.DataFrame(legs).to_csv(OUT / "legs.csv", index=False)
    result = dict(source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                  plan_sha256=sha(PLAN), script_sha256=sha(__file__), input_sha256=hashes,
                  first=str(d.index.min().date()), last=str(d.index.max().date()), sessions=len(d),
                  economic_definitions=4, gross_accounting_counterpart=1, reference_capital=CAPITAL,
                  runs=runs, classification="Limited historical proxy; no promotion/current-account claim")
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "input_sha256"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["selftest", "run"])
    args = parser.parse_args()
    selftest() if args.mode == "selftest" else run()
