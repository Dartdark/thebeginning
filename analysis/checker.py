"""Independent checker: fixed gates on a candidate's trade list (added 2026-10-15; the 'maker-checker' split).

The checker never sees how a candidate was found. It reads only checks/candidates/<name>/:
  spec.md       rules in plain words, instrument, costs used, mechanism, how many variants were tried, pre-registered yes/no
  trades.csv    one row per trade: date (YYYY-MM-DD), side (+1 / -1), net ($ per contract AFTER costs);
                FILTER candidates add 'kept' (1 = the filter keeps the trade, 0 = skips it) and list ALL base trades
  placebo.csv   optional: run, net -- trades of a placebo version (random side / random days ...), several runs
  meta.json     {"kind": "strategy" | "filter", "pre_registered": true/false, "variants": n}
and writes checks/candidates/<name>/checker_report.md.

Gates (all from the repo's testing standard; N = ranked items in TRIALS.csv):
  G1 significance  strategy: deflated Sharpe (per trade) at N >= 0.95, or pre-registered with <= 3 variants and t >= 2.0
                   filter:   kept - skipped t >= t_threshold(N), or pre-registered with <= 3 variants and t >= 2.0
  G2 holdout       2023-26: strategy mean > 0 with t >= 1.0 / filter kept - skipped > 0; and 2018-22 the same sign
  G3 years         strategy: >= 2/3 of years positive / filter: kept beats skipped in >= 2/3 of years
  G4 concentration strategy: still profitable without its best 5% of trades
  G5 placebo       placebo.csv given: share of placebo runs with mean >= the real mean < 0.05 (strategy);
                   filter: kept/skipped labels shuffled within each year 2,000 times, p < 0.05 (always run)
  G6 resampling    strategy: 2023+ block bootstrap P(Sharpe <= 0) < 0.20
  G7 MinTRL        trades >= the minimum track record length for the per-trade Sharpe (Minerva / Bailey & Lopez de Prado)
  G8 regime        regime composite over calendar years >= 0.60 (Minerva eq. 3)
  G9 PBO           only when variant trade lists are supplied (trades_replica_*.csv or variants/*.csv): CSCV PBO <= 0.50
Also printed: Sharpe, Sortino, profit factor, Calmar, Ulcer for all / longs / shorts (filter: kept trades and all trades),
2023+ bootstrap and drawdown permutation.
  python3 analysis/checker.py checks/candidates/<name>
"""
import sys, os, json, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def daily(x):
    d = x.groupby(x.index.normalize()).sum()
    days = pd.bdate_range(d.index.min(), d.index.max())
    return d.reindex(days, fill_value=0.0)


def n_items():
    try: return len(pd.read_csv("TRIALS.csv"))
    except Exception: return 200


def check(cdir):
    meta = json.load(open(os.path.join(cdir, "meta.json")))
    T = pd.read_csv(os.path.join(cdir, "trades.csv"), parse_dates=["date"]).sort_values("date")
    T = T[T.date >= "2018-01-01"].set_index("date")
    N = n_items(); pre = bool(meta.get("pre_registered")) and int(meta.get("variants", 99)) <= 3
    y = T.index.year; hold = y >= 2023; out = []; G = {}
    out.append(f"# Checker report: {os.path.basename(cdir.rstrip('/'))}\n")
    out.append(f"kind {meta['kind']}, pre-registered {meta.get('pre_registered')}, variants {meta.get('variants')}, "
               f"N (ranked items in TRIALS.csv) {N}, t_threshold(N) {M.t_threshold(N):.2f}\n")
    if meta["kind"] == "strategy":
        x = T.net; t = tstat(x); dsr = M.deflated_sharpe(x, N)
        G["G1 significance"] = (dsr >= 0.95) or (pre and t >= 2.0), f"t {t:.2f}, PSR {M.psr(x):.3f}, DSR(N={N}) {dsr:.3f}"
        a, b = x[~hold], x[hold]
        G["G2 holdout"] = (b.mean() > 0 and tstat(b) >= 1.0 and a.mean() > 0), f"2018-22 ${a.mean():.1f} (t {tstat(a):.2f}), 2023-26 ${b.mean():.1f} (t {tstat(b):.2f})"
        by = x.groupby(y).sum(); G["G3 years"] = (by > 0).mean() >= 2 / 3, f"{(by > 0).sum()}/{len(by)} years positive: " + ", ".join(f"{k} ${v:,.0f}" for k, v in by.items())
        cut = x.sort_values().iloc[:int(len(x) * 0.95)]
        G["G4 concentration"] = cut.sum() > 0, f"without the best 5% of trades: ${cut.sum():,.0f} total (${cut.mean():.1f} a trade) vs ${x.sum():,.0f}"
        pf = os.path.join(cdir, "placebo.csv")
        if os.path.exists(pf):
            P = pd.read_csv(pf); pm = P.groupby("run").net.mean()
            G["G5 placebo"] = np.mean(pm >= x.mean()) < 0.05, f"{len(pm)} placebo runs, mean ${pm.mean():.1f}; share >= real ${x.mean():.1f}: {np.mean(pm >= x.mean()):.3f}"
        else:
            G["G5 placebo"] = False, "no placebo.csv supplied (required for a strategy)"
        d = daily(x); bt = R.bootstrap(d[d.index >= "2023-01-01"], 2000)
        G["G6 resampling"] = bt.attrs["p_sharpe_le_0"] < 0.20, f"2023+ P(Sharpe <= 0) {bt.attrs['p_sharpe_le_0']:.3f}"
        rows = {"all": (daily(x), x)}
        for nm, s in (("longs", 1), ("shorts", -1)):
            xs = x[T.side == s]
            if len(xs) >= 5: rows[nm] = (daily(xs).reindex(rows["all"][0].index, fill_value=0.0), xs)
    else:
        k = T.kept.astype(bool); x = T.net
        dif = lambda m: x[m & k].mean() - x[m & ~k].mean()
        tv = (x[k].mean() - x[~k].mean()) / np.sqrt(x[k].var() / k.sum() + x[~k].var() / (~k).sum())
        G["G1 significance"] = (tv >= M.t_threshold(N)) or (pre and tv >= 2.0), f"kept ${x[k].mean():.1f} (n {k.sum()}) vs skipped ${x[~k].mean():.1f} (n {(~k).sum()}), t {tv:.2f}"
        G["G2 holdout"] = dif(hold) > 0 and dif(~hold) > 0, f"kept - skipped: 2018-22 ${dif(~hold):+.1f}, 2023-26 ${dif(hold):+.1f}"
        yy = pd.Series({yr: dif(y == yr) for yr in sorted(set(y))})
        G["G3 years"] = (yy > 0).mean() >= 2 / 3, f"kept beats skipped in {(yy > 0).sum()}/{len(yy)} years: " + ", ".join(f"{a} {b:+.0f}" for a, b in yy.items())
        rng = np.random.default_rng(1); real = x[k].mean() - x[~k].mean(); kv = k.to_numpy(); sims = []
        for _ in range(2000):
            kk = kv.copy()
            for yr in set(y):
                m = np.where(y == yr)[0]; kk[m] = rng.permutation(kk[m])
            sims.append(x[kk].mean() - x[~kk].mean())
        G["G5 placebo"] = np.mean(np.array(sims) >= real) < 0.05, f"labels shuffled within years (2,000): p {np.mean(np.array(sims) >= real):.4f}"
        xk = x[k]
        bt = R.bootstrap(daily(xk)[lambda d: d.index >= "2023-01-01"], 2000)
        G["G6 resampling"] = bt.attrs["p_sharpe_le_0"] < 0.20, f"kept trades 2023+ P(Sharpe <= 0) {bt.attrs['p_sharpe_le_0']:.3f}"
        idx = daily(x).index
        rows = {"all trades": (daily(x), x), "kept": (daily(xk).reindex(idx, fill_value=0.0), xk)}
        for nm, s in (("kept longs", 1), ("kept shorts", -1)):
            xs = xk[T.side[k] == s]
            if len(xs) >= 5: rows[nm] = (daily(xs).reindex(idx, fill_value=0.0), xs)
    # ---- Minerva gates (2026-10-15): MinTRL, regime stability (calendar years), PBO over variants if supplied
    xs = T.net if meta["kind"] == "strategy" else T.net[T.kept.astype(bool)]
    mt = M.min_trl(xs); G["G7 MinTRL"] = len(xs) >= mt, f"{len(xs)} trades vs MinTRL {mt:.0f}"
    rho, srw = M.regime_rho(daily(xs)); G["G8 regime stability"] = rho >= 0.60, f"rho {rho:.2f} (yearly Sharpe {', '.join(f'{k} {v:.1f}' for k, v in srw.items())})"
    import glob as _g
    vf = sorted(_g.glob(os.path.join(cdir, "trades_replica_*.csv"))) + sorted(_g.glob(os.path.join(cdir, "variants", "*.csv")))
    if len(vf) >= 3:
        cols = {"base": daily(xs)}
        for f in vf:
            v = pd.read_csv(f, parse_dates=["date"]); v = v[v.date >= "2018-01-01"].set_index("date")
            cols[os.path.basename(f)] = daily(v.net)
        Rm = pd.DataFrame(cols).fillna(0.0); pb = M.pbo(Rm)
        G["G9 PBO"] = pb <= 0.50, f"CSCV over {Rm.shape[1]} variants, 16 blocks: PBO {pb:.2f}"
    out.append("| Gate | Result | Detail |\n|---|---|---|")
    for g, (ok, txt) in G.items(): out.append(f"| {g} | {'PASS' if ok else 'FAIL'} | {txt} |")
    n_fail = sum(not ok for ok, _ in G.values())
    out.append(f"\n**Gates: {len(G) - n_fail}/{len(G)} pass -> {'PASS' if n_fail == 0 else 'FAIL'}**\n")
    out.append("## Standard metrics\n```\n" + M.table(rows) + "\n```")
    b, p = R.report({k_: v[0][v[0].index >= "2023-01-01"] for k_, v in rows.items()}, n=2000)
    out.append("## 2023+ bootstrap\n```\n" + b + "\n```\n## 2023+ drawdown permutation\n```\n" + p + "\n```")
    rep = "\n".join(out); open(os.path.join(cdir, "checker_report.md"), "w").write(rep)
    return rep, n_fail == 0


if __name__ == "__main__":
    rep, ok = check(sys.argv[1]); print(rep)
