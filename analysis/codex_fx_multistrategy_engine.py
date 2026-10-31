"""Offline FX signal/risk planner inspired by SSRN 3322717; not a backtester.

Run --demo for synthetic mechanics or --packet FILE for an audited as-of snapshot.
See agents/codex/research/fx_multistrategy/README.md for deliberate source differences.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

SYMBOLS = ("6A", "6B", "6C", "6E", "6J", "6M", "6N", "6S")
TARGET = .10
GROSS_CAP = 3.
MIN_RANK = 63
SHRINK = .05


def timestamp(value):
    t = pd.Timestamp(value)
    if pd.isna(t) or t.tzinfo is None:
        raise ValueError("All information/action clocks must be offset-aware")
    return t.tz_convert("UTC")


def number(value, name, positive=False):
    if isinstance(value, bool):
        raise ValueError(f"Invalid boolean for {name}")
    x = float(value)
    if not np.isfinite(x) or (positive and x <= 0):
        raise ValueError(f"Invalid {name}")
    return x


def required_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing {name}")
    return value


def validate(packet):
    decision = timestamp(packet["decision_at"])
    month = pd.Period(packet["rebalance_month"], freq="M")
    if pd.Period(decision.tz_localize(None), freq="M") != month:
        raise ValueError("Decision must be in the declared rebalance month")
    calendar = pd.DatetimeIndex(pd.to_datetime(packet["sessions"], format="%Y-%m-%d"))
    if len(calendar) < 316 or calendar.has_duplicates or not calendar.is_monotonic_increasing:
        raise ValueError("Need at least 316 unique ordered complete sessions")
    if not calendar.equals(calendar.normalize()) or calendar.tz is not None:
        raise ValueError("Sessions must be plain ISO dates")
    if calendar[-1].to_period("M") != month-1:
        raise ValueError("Latest complete session must be in the previous month")
    if calendar[-1].date() >= decision.date():
        raise ValueError("Formation follows the final complete session")
    if (decision.tz_localize(None).normalize()-calendar[-1]).days > 7:
        raise ValueError("Stale last observation")
    warmup = pd.Timestamp(packet["warmup_session"])
    if warmup >= calendar[0] or warmup != warmup.normalize() or warmup.tzinfo:
        raise ValueError("Warmup must be a prior plain session date")
    for name in ("calendar_provenance", "data_provenance", "commodity_index_id"):
        required_text(packet[name], name)
    for name in ("calendar_available_at", "universe_available_at"):
        if timestamp(packet[name]) > decision:
            raise ValueError(f"Future {name}")
    nav = number(packet["nav_usd"], "NAV", True)
    margin_budget = number(packet["margin_budget_usd"], "margin budget", True)
    if margin_budget > nav:
        raise ValueError("Reference margin budget exceeds NAV")
    data = pd.DataFrame(packet["observations"])
    needed = {"session", "symbol", "contract_id", "previous_close_contract_id", "previous_session",
              "close", "previous_close", "yield_1y", "yield_10y", "usd_yield_1y", "usd_yield_10y",
              "equity_index", "commodity_index", "event_at", "available_at"}
    if not needed.issubset(data):
        raise ValueError(f"Missing observation fields: {sorted(needed-set(data))}")
    data["session"] = pd.to_datetime(data.session, format="%Y-%m-%d")
    expected = pd.MultiIndex.from_product([calendar, SYMBOLS], names=["session", "symbol"])
    data = data.set_index(["session", "symbol"])
    if data.index.has_duplicates or set(data.index) != set(expected):
        raise ValueError("Incomplete/extra session or currency: no dropping or forward filling")
    data = data.reindex(expected)
    prior = dict(zip(calendar, [warmup, *calendar[:-1]]))
    events = {}
    for (session, symbol), row in data.iterrows():
        required_text(row.contract_id, "contract ID")
        if row.contract_id != row.previous_close_contract_id:
            raise ValueError("Return would cross a contract splice")
        if pd.Timestamp(row.previous_session) != prior[session]:
            raise ValueError("Previous close must belong to the prior declared session")
        event, available = timestamp(row.event_at), timestamp(row.available_at)
        if event > available or available > decision:
            raise ValueError("Observation unavailable at decision")
        if event.date() != session.date():
            raise ValueError("Daily snapshot event does not match its UTC session")
        events[(session, symbol)] = event
        for name in ("close", "previous_close", "equity_index", "commodity_index"):
            number(row[name], name, True)
        for name in ("yield_1y", "yield_10y", "usd_yield_1y", "usd_yield_10y"):
            number(row[name], name)
    # US yields and the declared common commodity index must be shared, not eight proxies.
    for name in ("usd_yield_1y", "usd_yield_10y", "commodity_index"):
        if (data[name].astype(float).groupby(level=0).nunique() != 1).any():
            raise ValueError(f"Inconsistent shared {name}")
    for symbol in SYMBOLS:
        group = data.xs(symbol,level="symbol")
        same = group.contract_id.eq(group.contract_id.shift(1))
        if not np.allclose(group.loc[same,"previous_close"].astype(float),
                           group.close.astype(float).shift(1)[same],rtol=1e-10,atol=1e-12):
            raise ValueError("Same-contract previous close does not reconcile")
    contracts = packet["reference_contracts"]
    if set(contracts) != set(SYMBOLS):
        raise ValueError("Require exactly eight reference contracts")
    action = timestamp(packet["next_action_at"])
    if action <= decision or action.tz_localize(None).to_period("M") != month+1:
        raise ValueError("Next monthly action must be in the next month")
    for symbol in SYMBOLS:
        c = contracts[symbol]
        for name in ("contract_id", "spec_provenance", "calendar_provenance"):
            required_text(c[name], name)
        for name in ("price", "multiplier", "initial_margin_usd"):
            number(c[name], name, True)
        if c["quote_currency"] != "USD":
            raise ValueError("This build requires native USD-quoted futures")
        event, available = timestamp(c["price_event_at"]), timestamp(c["price_available_at"])
        if not events[(calendar[-1], symbol)] <= event <= available <= decision:
            raise ValueError("Reference quote is stale or unavailable")
        if timestamp(c["spec_available_at"]) > decision or timestamp(c["calendar_available_at"]) > decision:
            raise ValueError("Future contract metadata")
        fill = timestamp(c["earliest_fill_at"])
        deadline = timestamp(c["delivery_or_expiry_at"])
        if not decision < fill < action < deadline:
            raise ValueError("Fill/action must precede delivery or expiry")
    return data.astype({k:float for k in needed if k in {
        "close", "previous_close", "equity_index", "commodity_index", "yield_1y",
        "yield_10y", "usd_yield_1y", "usd_yield_10y"}}), nav, margin_budget


def features(data):
    wide = lambda name: data[name].unstack("symbol").reindex(columns=SYMBOLS)
    returns = wide("close")/wide("previous_close")-1
    # Concatenated SAME-contract returns, not a raw rolled-price series.
    log_index = np.log1p(returns).cumsum()
    index = np.exp(log_index-log_index.iloc[0])
    out = {"carry_1y":wide("yield_1y")-wide("usd_yield_1y"),
           "carry_10y":wide("yield_10y")-wide("usd_yield_10y")}
    for n in (63, 252):
        out[f"momentum_{n}"] = log_index-log_index.shift(n)
        out[f"reversal_{n}"] = -np.log(index/index.rolling(n).mean())
        out[f"volatility_{n}"] = -returns.rolling(n).std(ddof=1)*np.sqrt(252)
        out[f"equity_{n}"] = np.log(wide("equity_index")/wide("equity_index").shift(n))
        out[f"commodity_{n}"] = np.log(wide("commodity_index")/wide("commodity_index").shift(n))
    return out, returns


def prior_percentile(frame):
    """Only earlier finite observations enter the rank, with exact midrank ties."""
    scores = []
    for symbol in SYMBOLS:
        x = frame[symbol].to_numpy(float)
        prior = x[:-1][np.isfinite(x[:-1])]
        if len(prior) < MIN_RANK or not np.isfinite(x[-1]):
            raise ValueError(f"Insufficient prior signal warmup for {symbol}")
        scores.append(((prior < x[-1]).sum()+.5*(prior == x[-1]).sum())/len(prior)-.5)
    return np.array(scores)


def asset_covariance(returns):
    if not np.isfinite(returns.iloc[-252:]).all().all():
        raise ValueError("Incomplete risk history")
    sigma = np.mean([returns.iloc[-n:].std(ddof=1).to_numpy() for n in (21, 63, 252)], axis=0)
    if np.any(sigma <= 1e-12):
        raise ValueError("Zero risk history")
    corr = returns.iloc[-252:].corr().to_numpy()
    corr = (1-SHRINK)*corr+SHRINK*np.eye(len(SYMBOLS))
    return corr*np.outer(sigma, sigma)*252


def risk_scale(weights, cov):
    vol = float(np.sqrt(max(0., weights@cov@weights)))
    if vol < 1e-14:
        return np.zeros_like(weights)
    w = weights*(TARGET/vol)
    gross = np.abs(w).sum()
    return w*min(1., GROSS_CAP/gross)


def signed_budget(score, cov):
    active = np.flatnonzero(np.abs(score) > 1e-12)
    w = np.zeros(len(score))
    if not len(active):
        return w
    signs = np.sign(score[active])
    b = np.abs(score[active]); b /= b.sum()
    c = cov[np.ix_(active, active)]*np.outer(signs, signs)
    c = c/np.median(np.diag(c))
    fun = lambda x: .5*x@c@x-np.dot(b, np.log(x))
    jac = lambda x: c@x-b/x
    sol = minimize(fun, np.sqrt(b/np.diag(c)), jac=jac, method="L-BFGS-B",
                   bounds=[(1e-10, None)]*len(active), options={"ftol":1e-14,"gtol":1e-9,"maxiter":5000})
    residual = np.max(np.abs(sol.x*(c@sol.x)-b))
    if not sol.success or residual > 1e-5:
        raise ValueError(f"Signed risk-budget solver failed: {sol.message}")
    w[active] = signs*sol.x
    return risk_scale(w, cov)


def combine(sleeves, cov, method):
    matrix = np.stack(list(sleeves.values()))
    active = np.flatnonzero(np.linalg.norm(matrix, axis=1) > 1e-12)
    allocations = np.zeros(len(matrix))
    if not len(active):
        return np.zeros(len(SYMBOLS)), allocations
    matrix_active = matrix[active]
    c = matrix_active@cov@matrix_active.T
    sigma = np.sqrt(np.diag(c))
    if method == "equal":
        a = np.ones(len(active))/len(active)
    elif method == "max_diversification":
        # Static current-exposure covariance; not a backtest of dynamic sleeves.
        corr = c/np.outer(sigma,sigma)+np.eye(len(active))*1e-8
        # Equivalent convex problem in volatility-weighted allocations z:
        # min z'corr z, sum(z)=1; recover a proportional to z/sigma.
        sol = minimize(lambda z:z@corr@z, np.ones(len(active))/len(active),
                       jac=lambda z:2*corr@z, method="SLSQP",
                       bounds=[(0.,1.)]*len(active), constraints=[{"type":"eq","fun":lambda a:a.sum()-1}],
                       options={"ftol":1e-12,"maxiter":2000})
        if not sol.success or abs(sol.x.sum()-1)>1e-7 or sol.x.min() < -1e-8:
            raise ValueError(f"Diversification solver failed: {sol.message}")
        a = np.maximum(sol.x,0.)/sigma; a /= a.sum()
    else:
        raise ValueError("Unknown combination mode")
    allocations[active] = a
    return risk_scale(allocations@matrix, cov), allocations


def build_plan(packet, method="max_diversification"):
    data, nav, budget = validate(packet)
    raw, returns = features(data)
    cov = asset_covariance(returns)
    scores = {k:prior_percentile(v) for k,v in raw.items()}
    sleeves = {k:signed_budget(v,cov) for k,v in scores.items()}
    ideal, allocations = combine(sleeves,cov,method)
    positions, actual = [], []
    for i, symbol in enumerate(SYMBOLS):
        c = packet["reference_contracts"][symbol]
        notional = float(c["price"])*float(c["multiplier"])
        qty = int(np.trunc(ideal[i]*nav/notional))
        weight = qty*notional/nav
        actual.append(weight)
        positions.append(dict(symbol=symbol, contract_id=c["contract_id"], ideal_weight=float(ideal[i]),
            reference_contracts=qty, rounded_weight=weight,
            reference_notional_usd=qty*notional, reference_margin_usd=abs(qty)*float(c["initial_margin_usd"]),
            earliest_fill_at=c["earliest_fill_at"], delivery_or_expiry_at=c["delivery_or_expiry_at"]))
    actual = np.array(actual)
    margin = sum(p["reference_margin_usd"] for p in positions)
    vol = float(np.sqrt(actual@cov@actual))
    if margin > budget+1e-8:
        raise ValueError("Rounded reference margin exceeds budget")
    if np.abs(actual).sum() > GROSS_CAP+1e-8 or vol > TARGET+1e-8:
        raise ValueError("Integer rounding removed hedges and breached reference risk cap")
    fingerprint = hashlib.sha256(json.dumps(packet,sort_keys=True,allow_nan=False).encode()).hexdigest()
    return dict(status="RESEARCH_REFERENCE_PLAN", source_replication=False,
        synthetic=bool(packet.get("synthetic",False)), decision_at=packet["decision_at"],
        rebalance_month=packet["rebalance_month"], next_action_at=packet["next_action_at"],
        method=method, nav_usd=nav, target_annual_volatility=TARGET, max_gross=GROSS_CAP,
        ideal_annual_volatility=float(np.sqrt(ideal@cov@ideal)), rounded_annual_volatility=vol,
        ideal_gross=float(np.abs(ideal).sum()), rounded_gross=float(np.abs(actual).sum()),
        reference_margin_usd=margin, margin_budget_usd=budget,
        all_rounded_to_zero=bool(np.all(actual==0)), positions=positions,
        signals={k:dict(zip(SYMBOLS,v.tolist())) for k,v in scores.items()},
        sleeve_allocations=dict(zip(sleeves,allocations.tolist())),
        sleeve_exposures={k:dict(zip(SYMBOLS,v.tolist())) for k,v in sleeves.items()},
        covariance=cov.tolist(), symbols=list(SYMBOLS),
        packet_sha256=fingerprint, code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        versions={"numpy":np.__version__,"pandas":pd.__version__},
        limits=["No fills, turnover, fees, rolls, collateral, NAV/P&L or return validation computed",
                "Risk and margin are as-of estimates, not future buying-power or loss guarantees",
                "All USD-quoted FX legs can share USD risk; no neutrality constraint",
                "12 unpruned sleeves and static-exposure diversification are declared research choices",
                "No Apex daily-flat conversion; no account or order connection"])


def synthetic_packet():
    """Invented numbers/contract specs for runnable mechanics; never market evidence."""
    dates = pd.bdate_range(end="2026-09-30", periods=550)
    rng = np.random.default_rng(3322717)
    r = rng.normal(0.0001,.006,(len(dates),8))
    prices = np.exp(np.cumsum(r,axis=0))
    equity = 100*np.exp(np.cumsum(rng.normal(.0002,.01,r.shape),axis=0))
    commodity = 100*np.exp(np.cumsum(rng.normal(.0001,.012,len(dates))))
    rows = []
    warmup = (dates[0]-pd.offsets.BDay()).strftime("%Y-%m-%d")
    for i,d in enumerate(dates):
        for j,symbol in enumerate(SYMBOLS):
            rows.append(dict(session=d.strftime("%Y-%m-%d"), symbol=symbol, contract_id=f"SYNTH-{symbol}",
                previous_close_contract_id=f"SYNTH-{symbol}",
                previous_session=dates[i-1].strftime("%Y-%m-%d") if i else warmup,
                close=float(prices[i,j]), previous_close=float(prices[i-1,j]) if i else 1.,
                yield_1y=float(-.5+j*.3+np.sin(i/51+j)),
                yield_10y=float(1+j*.2+np.cos(i/113+j)),
                usd_yield_1y=1.,usd_yield_10y=2., equity_index=float(equity[i,j]),
                commodity_index=float(commodity[i]), event_at=d.strftime("%Y-%m-%dT21:00:00Z"),
                available_at=d.strftime("%Y-%m-%dT22:00:00Z")))
    contracts = {s:dict(contract_id=f"SYNTH-{s}",price=float(prices[-1,j]),multiplier=10000.,
        quote_currency="USD",initial_margin_usd=1000.,price_event_at="2026-09-30T21:00:00Z",
        price_available_at="2026-09-30T22:00:00Z",spec_available_at="2024-01-01T00:00:00Z",
        calendar_available_at="2024-01-01T00:00:00Z",earliest_fill_at="2026-10-01T00:01:00Z",
        delivery_or_expiry_at="2026-12-01T00:00:00Z",spec_provenance="INVENTED",
        calendar_provenance="INVENTED") for j,s in enumerate(SYMBOLS)}
    return dict(synthetic=True, decision_at="2026-10-01T00:00:00Z",rebalance_month="2026-10",
        next_action_at="2026-11-01T00:00:00Z", nav_usd=1_000_000.,margin_budget_usd=500000.,
        sessions=dates.strftime("%Y-%m-%d").tolist(),warmup_session=warmup,observations=rows,
        reference_contracts=contracts,calendar_provenance="INVENTED WEEKDAY CALENDAR",
        data_provenance="DETERMINISTIC SYNTHETIC DATA; NOT CME",commodity_index_id="SYNTH-COMMODITY",
        calendar_available_at="2024-01-01T00:00:00Z",universe_available_at="2024-01-01T00:00:00Z")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--packet",type=Path)
    group.add_argument("--demo",action="store_true")
    parser.add_argument("--method",choices=["equal","max_diversification"],default="max_diversification")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--write-example",type=Path)
    args = parser.parse_args()
    if args.write_example and not args.demo:
        parser.error("--write-example requires --demo")
    packet = synthetic_packet() if args.demo else json.loads(args.packet.read_text())
    plan = build_plan(packet,args.method)
    args.output.write_text(json.dumps(plan,indent=2,allow_nan=False)+"\n")
    if args.write_example:
        args.write_example.write_text(json.dumps(packet,indent=2,allow_nan=False)+"\n")
    print(f"{plan['status']}; synthetic={plan['synthetic']}; output={args.output}")


if __name__ == "__main__":
    main()
