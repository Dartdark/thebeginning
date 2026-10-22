"""TEST_01 fixed-rule audit. Run from repo root: python analysis/codex_test01.py.

Prerequisite: python analysis/build_lab.py scratch_data. All strategy execution,
metrics, resampling and account simulation use repository tools. No settings fit.
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import pickle
import sys
import warnings

import numpy as np
import pandas as pd

import candidates24 as C
from grid import execute
from grid24 import jof
from param_clusters import trade_net
import metrics as M
import resampling as R
import montecarlo as MC

ROOT = Path(__file__).resolve().parents[1]
SP = ROOT / "scratch_data"
OUT = ROOT / "analysis/outputs"
SEED = 20261021
N = 5000


def tstat(x):
    x = pd.Series(x, dtype=float)
    return float(x.mean() / x.std() * np.sqrt(len(x))) if len(x) > 1 and x.std() > 0 else np.nan


def daily(t, days, claim=False):
    x = trade_net(t) - (10 if claim else 0)
    return x.groupby(pd.DatetimeIndex(t.date)).sum().reindex(days, fill_value=0.0)


def stats(t, days, claim=False):
    x = trade_net(t) - (10 if claim else 0)
    d = daily(t, days, claim)
    return dict(M.perf(d, trades=x), total=float(x.sum()), t=tstat(x),
                trade_dd=R.max_dd(x), daily_dd=R.max_dd(d))


def key(t):
    return list(zip(t.day, t.j0, t.side))


def random_drop(base, filtered, days, rng):
    """Uniform fixed-count trade deletion; aggregate to identical trading days."""
    x = trade_net(base).to_numpy()
    row = days.get_indexer(base.date)
    keep_n = len(filtered)
    if keep_n > len(base):
        return {"not_applicable": "filtered list has more trades than base"}
    ref = daily(filtered, days)
    totals, dds = [], []
    for _ in range(N):
        ix = rng.choice(len(x), keep_n, replace=False)
        d = np.bincount(row[ix], weights=x[ix], minlength=len(days))
        totals.append(d.sum())
        dds.append(R.max_dd(d))
    totals, dds = np.asarray(totals), np.asarray(dds)
    net, dd = float(ref.sum()), R.max_dd(ref)
    return dict(kept=keep_n, dropped=len(base)-keep_n, actual_total=net, actual_dd=dd,
                random_total_p5_p50_p95=np.percentile(totals, [5, 50, 95]).tolist(),
                random_dd_p5_p50_p95=np.percentile(dds, [5, 50, 95]).tolist(),
                fraction_filter_beats_profit=float(np.mean(totals < net)),
                fraction_filter_beats_dd=float(np.mean(dds > dd)),
                fraction_filter_beats_both=float(np.mean((totals < net) & (dds > dd))),
                p_random_ge_profit=float((1 + (totals >= net).sum()) / (N + 1)))


def paired_ci(delta, rng):
    x = delta.to_numpy()
    starts = rng.integers(0, len(x)-10+1, (N, int(np.ceil(len(x)/10))))
    ix = (starts[:, :, None] + np.arange(10)).reshape(N, -1)[:, :len(x)]
    totals = x[ix].sum(1)
    return dict(actual=float(x.sum()), daily_t=tstat(x),
                total_p5_p50_p95=np.percentile(totals, [5, 50, 95]).tolist(),
                p_delta_le_0=float(np.mean(totals <= 0)))


def funded(g, trades):
    """Prepare existing cache prerequisites, then use the existing funded bench."""
    import single_print_test as S
    import s_rank_gap_round2_test as G
    import cl_forced_flows_test as CL
    import funded_bootstrap as FB
    import relative_strength_test as RS
    # Module imports use argv[1] as their scratch path. Set them explicitly.
    for module in (S, G, CL, FB, RS):
        module.SP = str(SP) + "/"
    if not (SP / "single_print_sessions.pkl").exists():
        gg, sessions = S.frame()
        sessions.to_pickle(SP / "single_print_sessions.pkl")
        del gg
    if not (SP / "s_rank_gap2.pkl").exists():
        sym = G.Sym("CL")
        sym.set_rolls([])  # current confirmed CL rule does not skip roll weekends
        frame = G.sunday_frame(sym)
        pd.to_pickle({"frames": {"CL": frame}}, SP / "s_rank_gap2.pkl")
        del sym
    # plan_lab preserves the repository's conservative CL daily worst-path proxy.
    with contextlib.redirect_stdout(io.StringIO()):
        lab = FB.plan_lab(str(SP) + "/")
        FB.add_moc_mes(lab, str(SP) + "/")
    days, nq, es = RS.load()
    rs = RS.trades(days, nq, RS.signals(days, nq, es))
    rs = rs[rs.side > 0].reset_index(drop=True)
    rs["kind"] = rs.kind.map({"stop": 0, "target": 1, "flat": 2})
    lab.add("RS_L", rs)
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    flag = pd.read_pickle(SP / "single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)
    for nm in ("Base", "Combined"):
        lab.add("audit_"+nm, trades[nm])
        for suffix, mask in (("N", ~flag), ("F", flag)):
            lab.W[nm+suffix] = lab.W["audit_"+nm] * mask[:, None]
            lab.C[nm+suffix] = lab.C["audit_"+nm] * mask
    cur = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
    empty = {k: v for k, v in cur.items() if k not in ("VB_N", "VB_F")}
    plans = {"current_MC": cur, "empty_VB": empty,
             "rebuilt_Base": {**empty, "BaseN": 2, "BaseF": 1},
             "replace_Combined": {**empty, "CombinedN": 2, "CombinedF": 1},
             "add_Combined_1MNQ": {**cur, "audit_Combined": 1}}
    result = {}
    for start in ("2018-01-01", "2023-01-01"):
        print("FUNDED", start, "1000 paired 20-day circular blocks; cushion ref $1500", flush=True)
        boot = FB.Boot(lab, start=start)
        res, y1, minutes = boot.run(plans, n=1000, L=20, seed=SEED)
        rows = {}
        for nm, r in res.items():
            delta = r[:, 0] - res["current_MC"][:, 0]
            db = r[:, 3] - res["current_MC"][:, 3]
            delta_rebuild = r[:, 0] - res["rebuilt_Base"][:, 0]
            rows[nm] = dict(y1=float(y1[nm].mean()), y2=float(r[:, 0].mean()),
                            y2_p5_p95=np.percentile(r[:, 0], [5, 95]).tolist(),
                            blown=float(r[:, 3].mean()), all6=float(np.mean(r[:, 1] == 6)),
                            days6=float(np.median(np.where(r[:, 1] == 6, r[:, 2], np.inf))),
                            delta_current_y2=float(delta.mean()),
                            delta_mean_MC90=[float(delta.mean()-1.645*delta.std(ddof=1)/np.sqrt(len(delta))),
                                             float(delta.mean()+1.645*delta.std(ddof=1)/np.sqrt(len(delta)))],
                            delta_history_p5_p95=np.percentile(delta, [5, 95]).tolist(),
                            delta_blown=float(db.mean()), delta_rebuilt_y2=float(delta_rebuild.mean()))
        result[start] = rows
        print(pd.DataFrame(rows).T.to_string(), flush=True)
    print("FUNDED MODEL LIMITS: CL uses existing all-minute daily worst-loss proxy; NQ adverse-minute paths; costs scale /10;"
          " no new strategy fit. MC90 is simulation error conditional on history, not a market confidence interval.")
    return result


def main():
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    pd.set_option("display.width", 240)
    g = pickle.load(open(SP / "g24.pkl", "rb"))
    days = pd.DatetimeIndex(g.ts[g.trading])
    days = days[days >= "2018-01-01"]
    print("TEST_01; plan commit 6818838; fixed filters, no search; seed", SEED, flush=True)
    print("Python", sys.version, "numpy", np.__version__, "pandas", pd.__version__)
    print("Data", days.min(), "through", days.max(), "trading days", len(days))
    print("COST: $7.25/NQ + $5 entry and $5 non-target exit; claim convention subtracts another $10/trade.")
    print("Whole = longs only. Shorts: 0 trades, all trade metrics N/A in every period.")
    sig, kw = C.vault_break24(g)
    sig = sig[pd.DatetimeIndex(g.ts[sig.day]) >= "2018-01-01"].reset_index(drop=True)
    b = g.bars(30)
    vw, atr = g.vwap_rows(b), g.daily_atr(15)
    stretch = (b["c"][sig.day, sig.dj//30] - vw[sig.day, sig.dj//30]) <= 0.50 * atr[sig.day]
    runway = sig.dj <= jof(1230)
    signals = {"Base": sig, "Runway": sig[runway], "Stretch": sig[stretch], "Combined": sig[runway & stretch]}
    trades = {k: execute(g, s, **kw, name=k) for k, s in signals.items()}
    for nm, t in trades.items():
        assert (t.j1 >= t.j0).all() and (t.j0-1 < t.j1).all()
        assert (t.j1 <= jof(1430)).all()
        assert t.groupby("day").size().max() <= 3
        assert np.isfinite(trade_net(t)).all()
        t.to_csv(OUT / ("codex_test01_"+nm.lower()+"_trades.csv"), index=False)
    periods = {"full": days, "design": days[days.year < 2023], "holdout": days[days.year >= 2023]}
    periods.update({str(y): days[days.year == y] for y in sorted(set(days.year))})
    summary, decomposition, drops = {}, {}, {}
    rng = np.random.default_rng(SEED)
    basekeys = set(key(trades["Base"]))
    for period, ds in periods.items():
        summary[period] = {}
        for nm, t in trades.items():
            summary[period][nm] = stats(t[t.date.isin(ds)], ds)
        print("\nMETRICS", period, "whole/longs", flush=True)
        print(pd.DataFrame(summary[period]).T.round(4).to_string())
    claim = {k: stats(t, days, claim=True) for k, t in trades.items()}
    print("\nCLAIM COSTS $17.25 commission plus slippage, full:\n", pd.DataFrame(claim).T.round(4).to_string())
    print("CLAIM ARITHMETIC DD reduction", (17204-12609)/17204,
          "claimed combined DD at 2MNQ", 12609*0.2, "at 1MNQ",12609*0.1)
    for period in ("full", "design", "holdout"):
        ds = periods[period]
        base = trades["Base"][trades["Base"].date.isin(ds)]
        decomposition[period], drops[period] = {}, {}
        for nm in ("Runway", "Stretch", "Combined"):
            ft = trades[nm][trades[nm].date.isin(ds)]
            fk = set(key(ft))
            removed = base[[k not in fk for k in key(base)]]
            added = ft[[k not in basekeys for k in key(ft)]]
            x, ax = trade_net(removed), trade_net(added)
            decomposition[period][nm] = dict(removed_n=len(x), removed_total=float(x.sum()), removed_avg=float(x.mean()),
                                             removed_t=tstat(x), added_n=len(ax), added_total=float(ax.sum()),
                                             added_avg=float(ax.mean()), added_t=tstat(ax))
            drops[period][nm] = random_drop(base, ft, ds, rng)
        print("\nREMOVED/ADDED", period, json.dumps(decomposition[period], indent=2))
        print("RANDOM DROP", period, json.dumps(drops[period], indent=2), flush=True)
    cis, resamp, mc = {}, {}, {}
    for period in ("full", "holdout"):
        ds = periods[period]
        d = {nm: daily(t[t.date.isin(ds)], ds) for nm, t in trades.items() if nm in ("Base", "Combined")}
        delta = d["Combined"] - d["Base"]
        cis[period] = paired_ci(delta, rng)
        resamp[period] = {}
        print("\nPAIRED DELTA", period, cis[period], flush=True)
        for nm, dx in d.items():
            bb = R.bootstrap(dx, n=N, block=10, seed=SEED)
            pp = R.permutation(dx, n=N, seed=SEED)
            resamp[period][nm] = dict(bootstrap=bb.to_dict(), permutation=pp,
                                      p_sharpe_le_0=bb.attrs["p_sharpe_le_0"])
            print("BOOTSTRAP", period, nm, "5/50/95%, PF is DAILY\n", bb.round(4).to_string())
            print("PERMUTATION", pp, flush=True)
            mc[period+nm] = {}
            for size in (0.2, 0.8):
                tt = trades[nm][trades[nm].date.isin(ds)]
                print(MC.report(trade_net(tt), dx, size=size, label=period+" "+nm), flush=True)
                mc[period+nm][str(size)] = MC.daily_mc(dx*size, seed=1)
    # Explicit state-aware placebo: random deletion of the SAME count of candidate
    # signals as Combined, followed by the repository executor, 1,000 times.
    hs = signals["Base"][pd.DatetimeIndex(g.ts[signals["Base"].day]).year >= 2023]
    hc = signals["Combined"][pd.DatetimeIndex(g.ts[signals["Combined"].day]).year >= 2023]
    ref = summary["holdout"]["Combined"]
    replay, controls = [], {"random_time_long": [], "random_side_same_time": []}
    hc_trades = trades["Combined"][trades["Combined"].date.dt.year >= 2023]
    template = hc_trades.copy()
    early_days = C._early(g)
    # Random time retains realised trade days/counts and exits, but not signal conditions.
    # Multiple randomized entries can overlap and be skipped by the one-position engine.
    for run in range(1000):
        rs = hs.iloc[rng.choice(len(hs), len(hc), replace=False)]
        rt = execute(g, rs, **kw)
        dd = daily(rt, periods["holdout"])
        replay.append((float(dd.sum()), R.max_dd(dd), len(rt)))
        for label in controls:
            s = pd.DataFrame(dict(day=template.day.to_numpy(), dj=template.j0.to_numpy()-1,
                                  side=1, stop=75.0, target=40.0,
                                  exit_j=np.where(early_days[template.day], jof(1130), jof(1430))))
            if label == "random_side_same_time":
                s["side"] = rng.choice([-1, 1], len(s))
            else:
                s["dj"] = [rng.choice(np.arange(jof(1000), min(jof(1400), x-1)+1, 30)) for x in s.exit_j]
            ct = execute(g, s, **kw)
            controls[label].append(float(trade_net(ct).sum()))
        if (run+1) % 100 == 0:
            print("PLACEBOS", run+1, "/1000", flush=True)
    rp = np.asarray(replay)
    state = dict(random_signal_totals_p5_p50_p95=np.percentile(rp[:, 0], [5,50,95]).tolist(),
                 random_signal_dd_p5_p50_p95=np.percentile(rp[:,1], [5,50,95]).tolist(),
                 executed_count_p5_p50_p95=np.percentile(rp[:,2],[5,50,95]).tolist(),
                 beats_profit=float(np.mean(rp[:,0] < ref["total"])),
                 beats_dd=float(np.mean(rp[:,1] > ref["daily_dd"])),
                 beats_both=float(np.mean((rp[:,0] < ref["total"]) & (rp[:,1] > ref["daily_dd"]))))
    ctrl = {k: dict(total_p5_p50_p95=np.percentile(v,[5,50,95]).tolist(),
                    p_random_ge_actual=float((1+np.sum(np.asarray(v)>=ref["total"]))/1001)) for k,v in controls.items()}
    print("STATE AWARE NULL", state, "RANDOM TIME/SIDE", ctrl, flush=True)
    ntrials = len(pd.read_csv(ROOT / "TRIALS.csv")) + 3
    print("MULTIPLE TESTING: prior items + three filter variants", ntrials, "t threshold", M.t_threshold(ntrials))
    print("Strategy DSR (not incremental filter evidence)", {k: M.deflated_sharpe(trade_net(t), ntrials) for k,t in trades.items()})
    bench = funded(g, trades)
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((ROOT / "data").glob("NQ_1min*.csv"))}
    result = dict(summary=summary, claim_costs=claim, removed_added=decomposition, random_drop=drops,
                  paired_delta=cis, resampling=resamp, montecarlo=mc, state_placebo=state,
                  controls=ctrl, funded=bench, trials=ntrials, data_sha256=hashes)
    (OUT / "codex_test01_details.json").write_text(json.dumps(result, indent=2, default=float), encoding="utf-8")
    print("COMPLETE; 4 fixed configurations (3 filter trials); no holdout-driven adjustments.", flush=True)


def write_report():
    """Produce the review artifact from saved results; no new rule or parameter run."""
    from portfolio import load_mc
    z = json.loads((OUT / "codex_test01_details.json").read_text(encoding="utf-8"))
    g = pickle.load(open(SP / "g24.pkl", "rb"))
    ds = pd.DatetimeIndex(g.ts[g.trading])
    ds = ds[ds >= "2018-01-01"]
    trades = {nm: pd.read_csv(OUT / ("codex_test01_"+nm.lower()+"_trades.csv"), parse_dates=["date"])
              for nm in ("Base", "Runway", "Stretch", "Combined")}
    for nm, t in trades.items():
        assert np.allclose(t.pnl, (t.exit-t.entry)*t.side*20)
        assert np.allclose(t.net, t.pnl-7.25)
        assert (t.side == 1).all() and t.groupby("day").size().max() <= 3
        assert not t.duplicated(["day", "j0", "side"]).any()
        for period, days in (("full", ds), ("design", ds[ds.year<2023]), ("holdout", ds[ds.year>=2023])):
            actual = stats(t[t.date.isin(days)], days)
            for k in ("trades", "total", "t", "daily_dd", "trade_dd"):
                assert np.isclose(actual[k], z["summary"][period][nm][k])
            if nm != "Base":
                dec = z["removed_added"][period][nm]
                assert np.isclose(actual["total"]-z["summary"][period]["Base"]["total"],
                                  dec["added_total"]-dec["removed_total"])
    print("VALIDATION PASS: P&L arithmetic, fees, long-only, trade caps, unique entry keys, saved-period metrics and removed/new reconciliation.")
    mt = load_mc(g, "mc_reports/Backtesting Strategy Performance Report VB v1.xlsx")
    mt = mt[mt.date.isin(ds)]
    mcstats = stats(mt, ds)
    bt = trades["Base"]
    match = bt.merge(mt, on=["day", "j0", "side"], suffixes=("_py", "_mc"))
    parity = dict(mc_report=mcstats, matched_entry_keys=len(match),
                  pnl_equal_within_5=float(np.mean(np.abs(match.pnl_py-match.pnl_mc)<=5)))
    claim_periods = {p: {nm: stats(t[t.date.isin(days)], days, claim=True) for nm,t in trades.items()}
                     for p, days in (("design", ds[ds.year<2023]), ("holdout", ds[ds.year>=2023]))}
    supplementary = dict(base_report_parity=parity, claim_periods=claim_periods)
    print("SUPPLEMENTARY: report parity and claim-cost split (accounting only)")
    print(json.dumps(supplementary, indent=2))
    z["supplementary"] = supplementary
    (OUT / "codex_test01_details.json").write_text(json.dumps(z, indent=2), encoding="utf-8")

    def money(x): return ("-$" if x < 0 else "$") + f"{abs(x):,.2f}"
    def pct(x): return f"{x:.1%}"
    def band(x): return " to ".join(money(v) for v in x)
    def tab(headers, rows):
        return "\n".join(["| " + " | ".join(headers) + " |", "|"+"|".join(["---"]*len(headers))+"|"]+
                         ["| " + " | ".join(map(str,r)) + " |" for r in rows])
    s = z["summary"]
    def metric_table(periods, variants):
        rows=[]
        for p in periods:
            for nm in variants:
                a=s[p][nm]
                rows.append([p,nm,int(a["trades"]),pct(a["win"]),money(a["total"]),money(a["avg"]),
                             f'{a["t"]:.2f}',f'{a["sharpe"]:.2f}',f'{a["sortino"]:.2f}',
                             f'{a["profit_factor"]:.2f}',f'{a["calmar"]:.2f}',f'{a["ulcer"]:.2f}',money(a["daily_dd"])])
        return tab(["Period","Variant","Trades","Win","Net/NQ","Avg/NQ","t","Sharpe","Sortino","PF","Calmar","Ulcer","Daily max DD/NQ"],rows)
    removed = z["removed_added"]["holdout"]["Combined"]
    rd = z["random_drop"]["holdout"]["Combined"]
    pr = z["paired_delta"]["holdout"]
    lines=["# TEST_01: REJECT adoption of Combined",
           "Plan: `agents/codex/plans/TEST_01.md`, committed **6818838** before results. "
           "Script: `analysis/codex_test01.py`. Output: `analysis/outputs/codex_test01_output.txt`; "
           "machine-readable results: `analysis/outputs/codex_test01_details.json`; four trade CSVs alongside. "
           "Trials run: **3 filter configurations plus Base** (4 fixed configurations; no optimization).",
           "## Rule (as tested)",
           "Existing `candidates24.vault_break24` and `grid.execute`: NQ long on 30-minute close above the midnight open + "
           "0.30 times prior 15-weekday ATR and above the **30-minute-bar** midnight VWAP. Decision closes 10:00 through "
           "14:00 CT, next-minute open entry, 40-point target, 75-point stop, flat 14:30, three trades/day maximum. "
           "Early-close days retain decisions before 11:00 and flat 11:30. Combined adds decision close <=12:30 inclusive "
           "and close minus the same VWAP <=0.50 ATR. Individual filters are diagnostics, not alternative winners.",
           "Costs: $7.25/NQ round trip plus $5 per market/stop fill; target limits need a one-point trade-through and "
           "have no exit slippage. Whole strategy **equals longs**; shorts have **0 trades**, with all trade metrics, "
           "confidence intervals and placebo comparisons N/A. All dates use the same trading-day calendar, "
           f"{ds.min().date()} through {ds.max().date()}; 2026 is partial.",
           "## Results",
           "The average trade rises, but the filter reduces holdout total net and does not establish an incremental edge. "
           "The removed base trades remain profitable. The positive t of the retained strategy tests whether Vault Break "
           "makes money; it does not test whether adding this filter helps.",
           metric_table(["full","design","holdout"],["Base","Combined"]),
           "Daily metrics include zero-trade days, 252 days/year; Ulcer is percent against $50,000 starting equity. "
           "PF is per trade. Maximum drawdown above is closed daily equity; trade-sequence drawdown is shown separately below.",
           "Yearly whole/long results:",metric_table([str(y) for y in sorted(set(ds.year))],["Base","Combined"]),
           "All fixed configurations (all also appear by year in the output):",
           metric_table(["full","design","holdout"],["Runway","Stretch"]),
           "### Claim-by-claim audit",
           tab(["Claim","Finding"],[
               ["Base 1,744 / $143,396 / $82.22 / $17,204 DD / t 3.83",
                f"Not reproduced: {int(s['full']['Base']['trades']):,} / {money(s['full']['Base']['total'])} / {money(s['full']['Base']['avg'])} / daily DD {money(s['full']['Base']['daily_dd'])}, trade DD {money(s['full']['Base']['trade_dd'])} / t {s['full']['Base']['t']:.2f} at repo costs."],
               ["Combined 1,307 / $136,764 / $104.64 / $12,609 DD / t 4.09",
                f"Not reproduced: {int(s['full']['Combined']['trades']):,} / {money(s['full']['Combined']['total'])} / {money(s['full']['Combined']['avg'])} / daily DD {money(s['full']['Combined']['daily_dd'])}, trade DD {money(s['full']['Combined']['trade_dd'])} / t {s['full']['Combined']['t']:.2f}."],
               ["$17.25 commission plus 1 tick/fill",
                f"This is $10/trade above repo commission. At that convention Base = {money(z['claim_costs']['Base']['total'])}, Combined = {money(z['claim_costs']['Combined']['total'])}; claim still not reproduced. If $17.25 meant all-in market/stop costs, that is our $7.25 + two $5 slips, not $17.25 commission plus slips."],
               ["Design t 3.16 and holdout t 2.68 passed",
                f"Repo-cost Combined t = {s['design']['Combined']['t']:.2f} / {s['holdout']['Combined']['t']:.2f}; both positive, but incremental totals vs Base = {money(s['design']['Combined']['total']-s['design']['Base']['total'])} / {money(pr['actual'])}. At claimed commission t = {claim_periods['design']['Combined']['t']:.2f} / {claim_periods['holdout']['Combined']['t']:.2f}. Strategy significance is not filter validation."],
               ["Drawdown cut 26.7%",
                f"Correct arithmetic for the supplied numbers, not replicated. Our daily reduction = {pct(1-s['full']['Combined']['daily_dd']/s['full']['Base']['daily_dd'])}; trade-sequence reduction = {pct(1-s['full']['Combined']['trade_dd']/s['full']['Base']['trade_dd'])}."],
               ["2 MNQ worst DD $1,260.90, below $2,000",
                f"Wrong units: 2 MNQ = 0.20 NQ, so supplied $12,609 becomes $2,521.80. $1,260.90 is 1 MNQ. Our Combined at 2 MNQ: daily DD {money(.2*s['full']['Combined']['daily_dd'])}, trade DD {money(.2*s['full']['Combined']['trade_dd'])}. Historical DD is not a risk bound."],
               ["Chosen after testing each alone",
                "At least three filter trials; no fresh <=3-variant economic preregistration exemption. Their actual search history and original trade list were not supplied."],
               ["Late entries lack runway; stretched entries climax then retest",
                "Plausible hypotheses, not demonstrated mechanisms. Runway removes profitable holdout trades; stretch alone also lowers holdout total. No evidence here identifies a forced participant or establishes the claimed causal story."]]),
           "## Placebos and account level",
           "### Removed trades and execution state",
           tab(["Period","Filter","Removed n","Removed total","Removed avg","Removed t","New n","New total"],
               [[p,nm,v['removed_n'],money(v['removed_total']),money(v['removed_avg']),f"{v['removed_t']:.2f}",v['added_n'],money(v['added_total'])]
                for p,rr in z['removed_added'].items() for nm,v in rr.items()]),
           "The filtered execution list is not a simple subset. For Combined, skipping an earlier position can free a "
           "later entry or a daily trade slot. We reran signals through the repo executor; removed and newly enabled "
           "trades reconcile exactly to the total difference. A matched-count random deletion is therefore a thinning "
           "benchmark, supplemented by signal deletion with execution replay.",
           tab(["Period","Filter beats random profit","Beats random daily DD","Beats both"],
               [[p,pct(z['random_drop'][p]['Combined']['fraction_filter_beats_profit']),pct(z['random_drop'][p]['Combined']['fraction_filter_beats_dd']),pct(z['random_drop'][p]['Combined']['fraction_filter_beats_both'])]
                for p in ('full','design','holdout')]),
           "5,000 fixed-count deletions per configuration/period, preserving calendar order. "
           f"Holdout Combined random-profit p = {rd['p_random_ge_profit']:.3f}; 95% superiority is not met. "
           f"The paired ten-day-block bootstrap of Combined minus Base gives holdout total delta {money(pr['actual'])}, "
           f"90% interval {band([pr['total_p5_p50_p95'][0],pr['total_p5_p50_p95'][2]])}, daily t {pr['daily_t']:.2f}. "
           f"Bootstrap share delta <=0: {pct(pr['p_delta_le_0'])}; this is a resampling frequency, not a posterior probability.",
           f"State-aware holdout placebo: 1,000 uniform candidate-signal deletions, same signal count as Combined, then "
           f"`grid.execute`; beats {pct(z['state_placebo']['beats_profit'])} on profit, {pct(z['state_placebo']['beats_dd'])} "
           f"on DD, {pct(z['state_placebo']['beats_both'])} jointly. Executed counts vary: "
           f"5/50/95% = {z['state_placebo']['executed_count_p5_p50_p95']}.",
           tab(["Holdout control (1,000 runs)","Total net p5 / median / p95","p(control >= Combined)"],
               [[nm," / ".join(money(x) for x in v['total_p5_p50_p95']),f"{v['p_random_ge_actual']:.3f}"] for nm,v in z['controls'].items()]),
           "Random-time longs retain Combined's realised days/counts and randomize 30-minute decisions from 10:00 "
           "through 14:00 (through 11:00 on early-close days), with identical brackets/holiday flats. The early-day "
           "control thus permits one decision later than Base's 11:00 cutoff. Random-side control retains actual times. The executor "
           "can skip overlapping control signals. These assess the retained strategy, not its incremental filter effect.",
           "### Uncertainty and trailing drawdown",
           tab(["Holdout variant","Metric","Actual","Bootstrap p5","Bootstrap p95"],
               [[nm,k,f"{v['actual'][k]:,.3f}",f"{v['p5'][k]:,.3f}",f"{v['p95'][k]:,.3f}"]
                for nm,rs in z['resampling']['holdout'].items() for v in [rs['bootstrap']] for k in v['actual']]),
           "5,000 moving ten-day block resamples. Bootstrap PF is per day, unlike trade PF in the main table. "
           "Full-period intervals, daily-order permutations, shuffled DD percentiles, and 10,000 trade resamples "
           "are printed in the output. Whole/long resampling is identical; shorts N/A.",
           tab(["Period","Variant","Size","One-year P(EOD trail hit)","P(losing year)","One-year DD p95"],
               [[p,nm,f'{int(float(q)*10)} MNQ',pct(v['p_trail_hit']),pct(v['p_loss']),money(v['dd_p95'])]
                for p in ('full','holdout') for nm in ('Base','Combined') for q,v in z['montecarlo'][p+nm].items()]),
           "These standalone constant-size Monte Carlos use the existing $2,000 trail locking at start +$100, "
           "252 days/year and 5,000 ten-day-block paths. EOD-only breach checks omit intraday floor breaches, daily "
           "loss limits, other strategies and cushion sizing; the 8-MNQ stress is not a full evaluation pass-rate estimate.",
           "### Funded plan: additions, replacement, empty-slot control",
           "Existing Lab/Boot simulator, 1,000 paired 20-day-block histories, 500 trading days, full size from "
           "$1,500 cushion. Current plan includes report-derived VB with 2/1 MNQ single-print sizing, ONB ML, Monday, "
           "EOS, LDF, NFP, Bridge Monday, 2 MCL CL fade, 2 MES ES MOC, and 1 MNQ Relative Strength longs. "
           "Base/Combined replacements keep the same 2/1 sizing; addition is Combined 1 MNQ. Empty VB retains all other slots."]
    for p, rr in z['funded'].items():
        lines += [f"Source history from {p}:", tab(["Plan","Mean payouts 1y","Mean payouts 2y","2y history p5 / p95","Blown","Median days to 6","Delta 2y vs rebuilt Base"],
                     [[nm,money(v['y1']),money(v['y2']),band(v['y2_p5_p95']),pct(v['blown']),str(v['days6']),money(v['delta_rebuilt_y2'])] for nm,v in rr.items()])]
    lines += ["Paired mean simulation-error intervals and history-level delta bands vs current_MC are in the JSON/output. "
              "They quantify simulation variability conditional on this history; they do not establish independent "
              "future-market confidence. Compare replace_Combined with rebuilt_Base to isolate filtering from "
              "Python-versus-MultiCharts differences. Compare both with empty_VB to identify benefits merely from less exposure.",
              "## What could make this wrong",
              f"- The supplied claim has no trade list or exact dataset/version. The current VB report on common dates "
              f"contains {len(mt):,} trades, net {money(mcstats['total'])}; {len(match):,} exact day/entry-minute/side keys "
              f"match the {len(bt):,}-trade rebuild, and {pct(parity['pnl_equal_within_5'])} of these match gross P&L within $5. "
              "Report parity details are in the output. We cannot identify the claimant's exact discrepancy from headline numbers alone.",
              "- Signals use information available at the decision close; ATR is shifted to prior completed weekdays. "
              "Entry-bar stops/targets are active. The repository approximates intraminute order using OHLC; gaps, target "
              "trade-through and missing minute bars can affect fills. No tick data or MultiCharts compile was run here.",
              "- The 30-minute midnight bar can include minutes of the previous date; the Grid24 ATR uses one-minute "
              "calendar-date extremes, whereas the live source accumulates chart bars. Existing rebuild/report differences "
              "must be reconciled before any implementation. Continuous futures are not back-adjusted; roll jumps can affect ATR.",
              f"- Claimed holdout results were already visible before this audit. Combined is a fixed external selection, "
              f"not untouched original discovery. The current trial log plus our three configurations has {z['trials']} items; "
              f"the repo one-sided multiple-testing t bar is {M.t_threshold(z['trials']):.2f}. The incremental holdout t "
              "is negative. A retained-strategy DSR cannot rescue the filter.",
              "- Funded paths inherit the repo's conservative CL daily worst-loss proxy spread across the day, per-micro "
              "scaled costs and signal-level netting approximations. ES MOC and RS use the current repo rebuild rules; "
              "RS entry-bar exit delay is inherited from that separate strategy. Paired blocks preserve cross-strategy "
              "correlations within blocks but not long market regimes. No live accounts or settings were touched.",
              "## Differences between MultiCharts code and the test",
              "No Combined PowerLanguage code was written. The existing base is rebuilt with the established repo tools, "
              "with differences and report parity disclosed above. There is no basis here to change the live strategy. "
              "Keep Base; any new filter thresholds or altered time boundaries require a new registered trial and new forward evidence."]
    report = ROOT / "agents/codex/results/TEST_01.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n\n".join(lines)+"\n", encoding="utf-8")
    print("REPORT WRITTEN agents/codex/results/TEST_01.md")


if __name__ == "__main__":
    import os
    os.chdir(ROOT)
    OUT.mkdir(exist_ok=True)
    class Tee:
        def __init__(self, *streams): self.streams = streams
        def write(self, s):
            for stream in self.streams: stream.write(s); stream.flush()
        def flush(self):
            for stream in self.streams: stream.flush()
    report_only = "--report" in sys.argv
    # Imports in legacy research modules interpret argv[1] as scratch directory.
    sys.argv = [sys.argv[0]]
    if report_only:
        path = OUT / "codex_test01_output.txt"
        core = path.read_text(encoding="utf-8").split("VALIDATION PASS:", 1)[0]
        path.write_text(core, encoding="utf-8")
    with (OUT / "codex_test01_output.txt").open("a" if report_only else "w", encoding="utf-8") as log:
        with contextlib.redirect_stdout(Tee(sys.stdout, log)):
            if report_only:
                write_report()
            else:
                main()
                write_report()
