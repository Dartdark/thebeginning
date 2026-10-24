"""Frozen standalone diagnostics and re-executed null controls for ORPullback.

No file is read and no backtest runs at import. Call run_diagnostics only after
the portfolio preregistration has been committed. Money values in trades/stats
are per NQ; micro-sized Monte Carlo and dollar conversions are explicit.
"""
from __future__ import annotations

from pathlib import Path
import io
import json
import subprocess

import numpy as np
import pandas as pd
from numba import njit

import metrics as M
import resampling as R
import montecarlo as MC

PIN = "a67035be4189b493098c80f1def979348520fd5d"
PERIODS = {
    "2018_22": ("2018-01-01", "2023-01-01"),
    "2023_plus": ("2023-01-01", "2100-01-01"),
    "2018_plus": ("2018-01-01", "2100-01-01"),
    "2021_plus_descriptive": ("2021-01-01", "2100-01-01"),
}


def tstat(x):
    x = np.asarray(x, float)
    return float(x.mean() / x.std(ddof=1) * np.sqrt(len(x))) if len(x) > 1 and x.std(ddof=1) > 0 else np.nan


def net_trades(trades, fee=1.04):
    """Common money-only slippage, preserving source bracket geometry."""
    t = trades.copy()
    t["date"] = pd.to_datetime(t.date)
    t["slips"] = 1 + (t.kind != 1).astype(int)
    t["net_nq"] = t.gross_points * 20 - fee * 10 - t.slips * 5
    t["net_mnq"] = t.net_nq / 10
    return t


def trial_counts():
    raw = subprocess.check_output(["git", "show", PIN + ":TRIALS.csv"])
    tbl = pd.read_csv(io.BytesIO(raw))
    return dict(pinned_ranked_items=len(tbl), pinned_variants=int(tbl.variants.sum()),
                new_strategy_variants=2, dsr_n_items=len(tbl)+2,
                t_threshold=M.t_threshold(len(tbl)+2), author_search_count="unknown")


def standard_stats(trades, dates, n_items):
    rows = []
    periods = dict(PERIODS)
    for year in sorted(set(dates.year)):
        if year >= 2018:
            periods[str(year)] = (f"{year}-01-01", f"{year+1}-01-01")
    for period, (lo, hi) in periods.items():
        calendar = dates[(dates >= lo) & (dates < hi)]
        for side, sign in (("both", 0), ("long", 1), ("short", -1)):
            t = trades[(trades.date >= lo) & (trades.date < hi)]
            if sign:
                t = t[t.side == sign]
            daily = t.groupby("date").net_nq.sum().reindex(calendar, fill_value=0.)
            row = M.perf(daily, trades=t.net_nq)
            row.update(period=period, side=side, t=tstat(t.net_nq), total_nq=t.net_nq.sum(),
                       total_mnq=t.net_mnq.sum(), avg_mnq=t.net_mnq.mean(),
                       days=len(calendar), dsr_items=M.deflated_sharpe(t.net_nq, n_items),
                       t_daily=tstat(daily), max_dd_including_start=R.max_dd(daily))
            rows.append(row)
    return pd.DataFrame(rows)


@njit(cache=True)
def _exit_one(o, h, l, c, entry_j, side, flat_j, delay):
    """Raw close-entry exit geometry, matching frozen replay stop-first logic."""
    entry = c[entry_j]
    stop = entry - side*50.
    target = entry + side*100.
    for j in range(entry_j + delay, flat_j + 1):
        stop_hit = l[j] <= stop if side > 0 else h[j] >= stop
        target_hit = h[j] >= target+1. if side > 0 else l[j] <= target-1.
        gap = o[j] <= stop if side > 0 else o[j] >= stop
        if gap:
            return j, (o[j]-entry)*side, 0
        if stop_hit:
            return j, -50., 0
        if target_hit:
            price = max(o[j], target) if side > 0 else min(o[j], target)
            return j, (price-entry)*side, 1
    return flat_j, (c[flat_j]-entry)*side, 2


@njit(cache=True)
def _event_matrix(o, h, l, c, rows, flats, delay, entry_minutes):
    """Precompute fixed exits for every eligible placebo event, without selection."""
    n, m = len(rows), len(entry_minutes)
    ex = np.full((n, m, 2), -1, np.int64)
    points = np.zeros((n, m, 2))
    kinds = np.zeros((n, m, 2), np.int64)
    for d in range(n):
        row, flat = rows[d], flats[d]
        for k in range(m):
            ent = entry_minutes[k]
            if ent >= flat:
                continue
            for s in range(2):
                side = 1 if s else -1
                jx, pnl, kind = _exit_one(o[row], h[row], l[row], c[row], ent, side, flat, delay)
                ex[d,k,s], points[d,k,s], kinds[d,k,s] = jx, pnl, kind
    return ex, points, kinds


@njit(cache=True)
def _null_matrix(ex, money, entries, sides, event_counts, period_masks):
    n, nd, _ = entries.shape
    totals = np.zeros((n, period_masks.shape[0]))
    counts = np.zeros((n, period_masks.shape[0]), np.int64)
    for rep in range(n):
        for d in range(nd):
            last_exit = -1
            for e in range(event_counts[d]):
                k, s = entries[rep,d,e], sides[rep,d,e]
                minute = 535 + k*5
                if minute < last_exit:
                    continue
                last_exit = ex[d,k,s]
                for p in range(period_masks.shape[0]):
                    if period_masks[p,d]:
                        totals[rep,p] += money[d,k,s]
                        counts[rep,p] += 1
    return totals, counts


def placebos(g, trades, audit, timing, n=1000):
    """Randomise observed event side/time, then replay brackets and overlap.

    Event-day counts and direction/time templates are fixed before drawing.
    A changed first exit may overlap a later scheduled close entry; the later
    event is skipped, never moved using future information. Hence null samples
    can contain fewer trades. This is disclosed alongside the return test.
    """
    t = net_trades(trades)
    t = t[pd.to_datetime(t.date) >= "2018-01-01"].sort_values(["day", "entry_j"])
    eligible = audit[audit.status == "eligible"].set_index("gridrow")
    rows = t.day.drop_duplicates().to_numpy(int)
    flats = eligible.loc[rows, "scheduled_flat_j"].to_numpy(int)
    mins = np.arange(535, 871, 5, dtype=np.int64)  # 08:55..14:30 close stamps
    delay = 1 if timing == "reported_rule" else 6
    ex, points, kinds = _event_matrix(g.o, g.h, g.l, g.c, rows, flats, delay, mins)
    money = points*20 - 10.4 - (1+(kinds != 1))*5
    # Catch any discrepancy between the independent event walker and actual ledger.
    groups = [t[t.day == d] for d in rows]
    checked = 0
    for i, group in enumerate(groups):
        for r in group.itertuples():
            k, s = (int(r.entry_j)-535)//5, int(r.side > 0)
            if not (ex[i,k,s] == int(r.exit_j) and kinds[i,k,s] == r.kind
                    and np.isclose(points[i,k,s], r.gross_points, rtol=0, atol=1e-10)):
                raise AssertionError(f"Placebo walker differs from replay at {r.date}/{r.entry_j}/{r.side}")
            checked += 1
    periods = {k:v for k,v in PERIODS.items() if k != "2021_plus_descriptive"}
    event_counts = np.array([len(group) for group in groups],dtype=np.int64)
    fixed_entries = np.zeros((len(groups),2),np.int64)
    fixed_sides = np.zeros_like(fixed_entries)
    for i, group in enumerate(groups):
        fixed_entries[i,:len(group)] = (group.entry_j.to_numpy(int)-535)//5
        fixed_sides[i,:len(group)] = (group.side.to_numpy(int)>0).astype(int)
    group_dates = pd.DatetimeIndex([group.date.iloc[0] for group in groups])
    period_masks = np.array([(group_dates>=lo)&(group_dates<hi) for lo,hi in periods.values()])
    all_rows, summary = [], []
    for control, seed in (("random_side",848), ("random_time",849)):
        rng = np.random.default_rng(seed)
        if control == "random_side":
            entries = np.broadcast_to(fixed_entries,(n,)+fixed_entries.shape).copy()
            sides = rng.integers(0,2,(n,len(groups),2))
        else:
            available = np.array([(mins<flat).sum() for flat in flats])
            entries = np.empty((n,len(groups),2),np.int64)
            entries[:,:,0] = (rng.random((n,len(groups)))*available).astype(int)
            # Draw the second index from K-1 choices and skip the first index:
            # uniform sampling without replacement, never conditioned on exits.
            second = (rng.random((n,len(groups)))*(available-1)).astype(int)
            entries[:,:,1] = second+(second>=entries[:,:,0])
            two = event_counts==2
            entries[:,two,:] = np.sort(entries[:,two,:],axis=2)
            sides = np.broadcast_to(fixed_sides,(n,)+fixed_sides.shape).copy()
        total_draws, count_draws = _null_matrix(ex,money,entries,sides,event_counts,period_masks)
        draws = []
        for p,period in enumerate(periods):
            for iteration in range(n):
                draws.append(dict(control=control, iteration=iteration, period=period,
                                  total_nq=total_draws[iteration,p],trades=count_draws[iteration,p]))
        df = pd.DataFrame(draws)
        all_rows.append(df)
        for period,(lo,hi) in periods.items():
            x = df[df.period == period]
            real = t[(t.date>=lo)&(t.date<hi)]
            summary.append(dict(control=control, period=period, real_total_nq=real.net_nq.sum(),
                                real_trades=len(real), null_total_p5=x.total_nq.quantile(.05),
                                null_total_p50=x.total_nq.median(), null_total_p95=x.total_nq.quantile(.95),
                                p_null_ge_real=(1+int((x.total_nq>=real.net_nq.sum()).sum()))/(n+1),
                                null_trades_min=x.trades.min(), null_trades_mean=x.trades.mean(),
                                null_trades_max=x.trades.max(), iterations=n, walker_parity_checks=checked))
    return pd.DataFrame(summary), pd.concat(all_rows, ignore_index=True)


def trade_monte_carlo(ledgers):
    """Repository trade bootstrap, separate from the more relevant account paths."""
    rows = []
    for timing, raw in ledgers.items():
        t = net_trades(raw)
        for side, sign in (("both",0),("long",1),("short",-1)):
            sub = t if not sign else t[t.side==sign]
            for period in ("2018_plus","2023_plus"):
                lo,hi = PERIODS[period]
                x = sub[(sub.date>=lo)&(sub.date<hi)].net_nq.to_numpy()
                for size in (1,2):
                    row = MC.trade_mc(x*size/10,n=5000,seed=848)
                    row.update(timing=timing,side=side,period=period,size_mnq=size,
                               iterations=5000,caveat="Trade bootstrap ignores day dependence; account test uses whole-day blocks")
                    rows.append(row)
    return pd.DataFrame(rows)


def verify_account_outputs(out):
    """Independent arithmetic reconciliation of every published funded row."""
    out = Path(out)
    summary = pd.read_csv(out/"funded_summary.csv")
    arrays = {(fee,cohort):np.load(out/f"funded_results_{fee:.2f}_{cohort}.npz")
              for fee in (1.04,1.24) for cohort in ("2018_plus","2023_plus")}
    cols = ("year1","year1_p5","year1_p95","year2","year2_p5","year2_p95","blown","all6","days6")
    for row in summary.itertuples():
        z = arrays[(row.fee,row.cohort)]
        a,b = z[row.config+"__250"],z[row.config+"__500"]
        actual = [a[:,0].mean(),np.percentile(a[:,0],5),np.percentile(a[:,0],95),
                  b[:,0].mean(),np.percentile(b[:,0],5),np.percentile(b[:,0],95),
                  b[:,3].mean(),(b[:,1]==6).mean(),np.median(np.where(b[:,1]==6,b[:,2],np.inf))]
        np.testing.assert_allclose(actual,[getattr(row,c) for c in cols],rtol=0,atol=1e-10)
    parity = []
    for f in sorted(out.glob("funded_parity_*.json")):
        parity.extend(json.loads(f.read_text()))
    if len(parity) != 160 or not all(x["exact"] for x in parity):
        raise AssertionError("Expected160 exact simulator checks")
    evaluation = pd.read_csv(out/"evaluation_summary.csv")
    np.testing.assert_allclose(evaluation.passed+evaluation.failed+evaluation.timed_out,1.,rtol=0,atol=1e-12)
    record = dict(funded_rows_reconciled=len(summary),funded_fields_per_row=len(cols),
                  exact_simulator_checks=len(parity),all_simulator_checks_exact=True,
                  evaluation_rows=len(evaluation),evaluation_outcome_shares_sum_to_one=True,
                  arithmetic_tolerance=1e-10,review_status="PASS WITH CONCERNS",
                  concerns=["16 excluded sessions include March2020 stress dates",
                            "original author MultiCharts parity not established",
                            "fullcalendar saved baseline close, not identical",
                            "inherited CL/MOC path approximations"])
    (out/"independent_output_audit.json").write_text(json.dumps(record,indent=2)+"\n")
    return record


def run_diagnostics(g, replays, out, run_nulls=True):
    """Run committed diagnostics on already-built, frozen replay results."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    counts = trial_counts()
    all_dates = pd.DatetimeIndex(g.ts[g.trading])
    all_dates = all_dates[all_dates >= "2018-01-01"]
    summaries, nulls, mc_rows = [], [], []
    for timing, result in replays.items():
        eligible = pd.DatetimeIndex(pd.to_datetime(result.audit.loc[result.audit.status=="eligible","date"]))
        dates = all_dates[all_dates.isin(eligible)]
        t = net_trades(result.trades)
        t.to_csv(out/f"{timing}_net_trades.csv", index=False)
        # Preserve the preregistered complete-session universe. An excluded
        # unknown session is not a zero-return day. This makes MC adjacency
        # conditional on coverage and must be disclosed in the report.
        for fee in (1.04,1.24):
            f = net_trades(result.trades, fee)
            stats = standard_stats(f, dates, counts["dsr_n_items"])
            stats.insert(0,"fee_micro",fee)
            stats.insert(0,"timing",timing)
            summaries.append(stats)
        for side, sign in (("both",0),("long",1),("short",-1)):
            sub = t if not sign else t[t.side==sign]
            daily = sub.groupby("date").net_nq.sum().reindex(dates,fill_value=0.)
            h = daily[daily.index >= "2023-01-01"]
            boot = R.bootstrap(h,n=5000,block=10,seed=848)
            boot.to_csv(out/f"{timing}_{side}_2023_bootstrap.csv")
            for period in ("2018_plus","2023_plus"):
                lo,hi = PERIODS[period]
                day = daily[(daily.index>=lo)&(daily.index<hi)]
                for size in (1,2):
                    dm = MC.daily_mc(day.to_numpy()*size/10,horizon=252,n=5000,block=10,seed=848)
                    dm.update(timing=timing,side=side,period=period,size_mnq=size,
                              caveat="EOD-only standalone trail; joint account uses intraday adverse paths")
                    mc_rows.append(dm)
        if run_nulls:
            sm, draws = placebos(g,result.trades,result.audit,timing)
            sm.insert(0,"timing",timing)
            draws.to_csv(out/f"{timing}_null_draws.csv",index=False)
            nulls.append(sm)
    stats = pd.concat(summaries,ignore_index=True)
    stats.to_csv(out/"standard_stats.csv",index=False)
    pd.DataFrame(mc_rows).to_csv(out/"standalone_mc.csv",index=False)
    trade_monte_carlo({k:v.trades for k,v in replays.items()}).to_csv(out/"trade_mc.csv",index=False)
    if nulls:
        pd.concat(nulls,ignore_index=True).to_csv(out/"placebo_summary.csv",index=False)
    (out/"trial_counts.json").write_text(json.dumps(counts,indent=2)+"\n")
    return stats


if __name__ == "__main__":
    import argparse
    import pickle
    from codex_or_pullback_replay import replay, ReplayResult, TIMING_MODES
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch",default="scratch_data")
    parser.add_argument("--out",default="analysis/outputs/codex_or_pullback_portfolio/diagnostics")
    args = parser.parse_args()
    # Explicit guard: the exact preregistration must exist in committed history.
    subprocess.check_call(["git","cat-file","-e","1ad4306:agents/codex/plans/or_pullback_portfolio.md"])
    with open(Path(args.scratch)/"g24.pkl","rb") as f:
        grid = pickle.load(f)
    td = pd.DatetimeIndex(grid.ts[grid.trading])
    design = grid.trading[(td>="2018-01-01")&(td<"2023-01-01")]
    historical = grid.trading[td>="2023-01-01"]
    results = {}
    for mode in TIMING_MODES:
        a = replay(grid,mode,rows=design)
        print(mode,"design",len(a.trades),flush=True)
        b = replay(grid,mode,rows=historical)
        print(mode,"2023+",len(b.trades),flush=True)
        result = ReplayResult(pd.concat([a.trades,b.trades],ignore_index=True),
                              pd.concat([a.audit,b.audit],ignore_index=True),a.spec,
                              pd.concat([a.events,b.events],ignore_index=True))
        results[mode] = result
    stats = run_diagnostics(grid,results,args.out)
    print(stats[(stats.side=="both")&(stats.fee_micro==1.04)&stats.period.isin(PERIODS)]
          [["timing","period","trades","avg_mnq","t","dsr_items","sharpe"]].to_string(index=False),flush=True)
