"""Three dashboard panels from the backtest + the live logs (2026-10-29, user: 'build all three').
Writes analysis/outputs/dashboard/{montecarlo,live_vs_bt,silence}.json for the 'Apex Live Desk' dashboard.

1. montecarlo  Each live account's P&L since it started vs the backtest: every window of the same number of trading days
               (2023 onward) of the evaluation set at the account's size (VB 8 / ONB ADX30 $1,100 / Bridge 2 / EOS $500 MNQ;
               150K x 2.5), MultiCharts trade lists + $7.25 / NQ + 1 tick a fill. Percentile of the live result, the
               p5-p95 range, and the 21-day (one month) range. Below p10 two months running -> review (FRIDAY_REVIEW.md).
2. live_vs_bt  Per strategy (account #2's chart, the longest-running set): live points per contract (logger gross minus
               $1.04 per MNQ round trip = 0.52 pt) vs the backtest's 2023+ average (net, per contract), edge ratio, and the
               drift alarm (live_vs_backtest.py's CUSUM on % return per trade). Few trades = wide noise: the decision
               needs ~40 trades (mid-December gate).
3. silence     Missed-trade alarm without daily data: for each strategy, the trading days since the live chart's last
               trade (or since the chart started) and the backtest probability of going that long with no trade (2023+).
               Below 2% -> SILENT: check that the chart is really trading (auto-trading, inputs, data).
  python3 analysis/live_panels.py [SCRATCH_DIR]     (rebuilds the backtest cache when scratch_data exists, else uses
  analysis/outputs/dashboard/bt_cache.json)
"""
import sys, os, json, pickle, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from live_vs_backtest import drift_calibrate, cusum_down

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
OUT = "analysis/outputs/dashboard"
NAMES = {"VB": "Vault Break", "ONB30": "Overnight Bias ADX30", "MON_BR": "Bridge Monday Long", "EOS": "EOS"}
LOGTAG = {"VB": "VB", "ONB30": "ONB", "MON_BR": "MON_BR", "EOS": "EOS"}
# live accounts: start date and balance; the current balance comes from accounts.json (analysis/dashboard_data.py, run first)
ACCTS = [dict(account="#2", size="50K", mult=1.0, start="2026-10-20", start_bal=50000.0),
         dict(account="#3", size="150K", mult=2.5, start="2026-10-26", start_bal=150000.0),
         dict(account="#4", size="150K", mult=2.5, start="2026-11-02", start_bal=150000.0)]
COLS = ["event", "tag", "symbol", "side", "contracts", "entry_date", "entry_time", "entry_price", "exit_date",
        "exit_time", "exit_price", "profit_usd", "bar_date", "bar_time"]


def main():
    cache = "analysis/outputs/dashboard/bt_cache.json"
    if os.path.exists(SP + "g24.pkl"):
        from portfolio import load_mc, paths
        from funded_lab import with_slippage
        from build_lab import REPORTS
        from bridge_monday_confirm import load_bridge_mc
        import combine_levers_test as CL
        g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading
        dates = pd.DatetimeIndex(g.ts[trr]).normalize()
        T = {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, CL.ONB30)),
             "MON_BR": load_bridge_mc(g), "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}
        risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))
        q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
        daily = np.zeros(len(trr))
        for k, t in T.items():
            w, r = paths(g, t); daily += r[trr][:, -1] / 10 * q[k]
        C = {"daily": {str(d.date()): float(v) for d, v in zip(dates, daily) if d >= pd.Timestamp("2023-01-01")}, "bt": {}}
        for k, t in T.items():
            d = pd.DatetimeIndex(g.ts[t["day"].to_numpy()]).normalize(); keep = d >= "2023-01-01"; bt = t[keep]
            C["bt"][k] = {"day": [str(x.date()) for x in d[keep]], "pts": ((bt.exit - bt.entry) * bt.side - 7.25 / 20).round(4).tolist(),
                          "entry": bt.entry.astype(float).tolist()}
        json.dump(C, open(cache, "w"))      # small; lets the 16:40 job run without rebuilding scratch_data
    else:
        C = json.load(open(cache))
    ser = pd.Series(C["daily"]); ser.index = pd.DatetimeIndex(ser.index)
    BT = {k: pd.DataFrame(v).assign(day=lambda x: pd.DatetimeIndex(x.day)) for k, v in C["bt"].items()}
    bdays = lambda a, b: int(np.busday_count(a, np.datetime64(b) + 1))

    # 1. Monte Carlo / window percentile
    mc = []
    cur = {r["account"]: r for r in json.load(open(f"{OUT}/accounts.json"))}
    for a in ACCTS:
        c = cur[a["account"]]
        asof = max(c["last_date"], max((t["date"] for t in json.load(open(f"{OUT}/trades.json")) if t["account"] == a["account"]), default=c["last_date"]))
        n = bdays(a["start"], asof); live = c["est_balance"] - a["start_bal"]
        if n < 1:   # not started yet (2026-11-01: #4 read as 'below its range' before its first day and tripped the buy gate)
            mc.append(dict(account=a["account"], size=a["size"], days=0, live_pnl=0.0, percentile=None, status="NOT STARTED")); continue
        win = ser.rolling(n).sum().dropna() * a["mult"]; m21 = ser.rolling(21).sum().dropna() * a["mult"]
        pct = float((win < live).mean() * 100)
        mc.append(dict(account=a["account"], size=a["size"], days=n, live_pnl=round(live, 2), percentile=round(pct, 1),
                       p5=round(win.quantile(.05)), p25=round(win.quantile(.25)), p50=round(win.quantile(.5)),
                       p75=round(win.quantile(.75)), p95=round(win.quantile(.95)),
                       m21_p5=round(m21.quantile(.05)), m21_p50=round(m21.quantile(.5)), m21_p95=round(m21.quantile(.95)),
                       status="LOW (below p10)" if pct < 10 else "OK"))

    # live trades from the VPS logger
    df = pd.concat([pd.read_csv(f, header=None, names=COLS, dtype=str) for f in sorted(glob.glob("live/trades/*.csv"))])
    cl = df[df.event == "CLOSE"].drop_duplicates()
    last_day = max(os.path.basename(f)[:8] for f in glob.glob("live/trades/*.csv"))
    last_day = f"{last_day[:4]}-{last_day[4:6]}-{last_day[6:]}"

    lvb, sil = [], []
    for k, bt in BT.items():
        tag = LOGTAG[k] + "-2"
        lv = cl[cl.tag == tag].copy()
        lv["pts"] = (lv.exit_price.astype(float) - lv.entry_price.astype(float)) * np.where(lv.side == "long", 1, -1) - 0.52
        lv["ret"] = lv.pts / lv.entry_price.astype(float) * 100
        bt_d = pd.DatetimeIndex(bt.day); bt_pts = bt.pts
        row = dict(strategy=NAMES[k], live_trades=len(lv), live_pts=round(float(lv.pts.mean()), 1) if len(lv) else None,
                   bt_pts=round(float(bt_pts.mean()), 1), bt_trades_per_year=round(len(bt) / ((bt_d.max() - bt_d.min()).days / 365.25), 1))
        row["edge_ratio"] = round(row["live_pts"] / row["bt_pts"], 2) if len(lv) and row["bt_pts"] else None
        if len(lv):
            ref = (bt_pts / bt.entry * 100).to_numpy(); horizon = max(20, int(round(row["bt_trades_per_year"])))
            m, s, h, med = drift_calibrate(ref, horizon, n=1000)
            cur = float(cusum_down(lv.ret.to_numpy(), m, s)[-1])
            row.update(cusum=round(cur, 2), alarm_at=round(h, 2),
                       drift="ALARM" if cur >= h else ("WATCH" if cur >= h / 2 else "OK"))
        else:
            row.update(cusum=None, alarm_at=None, drift="no trades yet")
        lvb.append(row)

        # 3. silence: trading days with no trade, and how rare that is in the backtest
        since = lv.exit_date.max() if len(lv) else "20261020"
        since = f"{since[:4]}-{since[4:6]}-{since[6:]}"
        gap = bdays(since, last_day) - (1 if len(lv) else 0)
        traded = pd.Series(1, index=bt_d).groupby(level=0).sum().reindex(ser.index, fill_value=0)
        p = float((traded.rolling(max(gap, 1)).sum().dropna() == 0).mean() * 100) if gap > 0 else 100.0
        sil.append(dict(strategy=NAMES[k], last_live_trade=since if len(lv) else "none since 2026-10-20", quiet_days=gap,
                        bt_chance_pct=round(p, 1), status="SILENT - check the chart" if p < 2 else ("WATCH" if p < 10 else "OK")))

    os.makedirs(OUT, exist_ok=True)
    for name, data in (("montecarlo", mc), ("live_vs_bt", lvb), ("silence", sil)):
        json.dump(data, open(f"{OUT}/{name}.json", "w"), indent=1)
    for x in mc + lvb + sil: print(x)


if __name__ == "__main__":
    main()
