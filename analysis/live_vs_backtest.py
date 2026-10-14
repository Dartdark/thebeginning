"""Live (or sim) trading vs the backtest, trade by trade (2026-10-14).

Purpose: the account-pipeline study (analysis/account_pipeline_test.py) says to scale from 3 to 5-10 account slots only
if live results keep at least ~75% of the backtest edge. This script measures that.

Inputs: two MultiCharts Strategy Performance Reports (.xlsx, "List of Trades" sheet) for the same strategy:
  LIVE      the report of the live / sim auto-trading chart (MultiCharts: Strategy Performance Report of the real-time
            trades; export to Excel)
  BACKTEST  a backtest of the same strategy on the same symbol, re-run so it covers the live dates
The two can be on different contract sizes (e.g. live on MNQ, backtest on NQ): everything is compared in points per
contract. Matching: same session date and side, entry times within --window minutes (default 15).
Outputs (printed, and a CSV of every trade next to the live file):
  matched / missed (backtest only) / extra (live only) trades; entry and exit slippage in ticks (+ = worse than the
  backtest); points per contract live vs backtest; the edge ratio = live points / backtest points over the live
  period (missed trades count 0 live, extra trades count their live result); the decision line.
Usage:
  python3 analysis/live_vs_backtest.py LIVE.xlsx BACKTEST.xlsx [--tick 0.25] [--window 15]
  python3 analysis/live_vs_backtest.py --all live/   (pairs live/<KEY>_live.xlsx with the plan's backtest report KEY,
                                                      KEY = VB, ONB_ML2_MC, MON_MC, EOS, LDF_MC, NFP_MC, MON_BR)
  python3 analysis/live_vs_backtest.py --selftest
"""
import sys, os, glob, argparse
import numpy as np, pandas as pd

KEYS = {"VB": "Backtesting Strategy Performance Report VB v1.xlsx",
        "ONB_ML2_MC": "Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx",
        "EOS": "Backtesting Strategy Performance Report EOS v1.xlsx",
        "MON_MC": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx",
        "LDF_MC": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx",
        "NFP_MC": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NFP Fade.xlsx",
        "MON_BR": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx"}


def read_trades(path):
    raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
    t = raw["Type"].astype(str)
    ent = raw[t.str.startswith("Entry")].reset_index(drop=True); ex = raw[t.str.startswith("Exit")].reset_index(drop=True)
    n = min(len(ent), len(ex)); ent, ex = ent.iloc[:n], ex.iloc[:n]
    et = pd.to_datetime(ent["Date"]); xt = pd.to_datetime(ex["Date"])
    side = np.where(ent["Type"].astype(str).str.contains("Long"), 1, -1)
    q = ent["Contracts"].astype(float).to_numpy()
    out = pd.DataFrame(dict(entry_time=et, exit_time=xt, side=side, entry=ent["Price"].astype(float).to_numpy(),
                            exit=ex["Price"].astype(float).to_numpy(), qty=q, signal=ent["Signal"].astype(str).to_numpy(),
                            exit_signal=ex["Signal"].astype(str).to_numpy()))
    # session date: trades entered after 16:00 CT belong to the next session (Sunday / evening entries)
    out["session"] = (out.entry_time + pd.to_timedelta((out.entry_time.dt.hour >= 16).astype(int), unit="D")).dt.normalize()
    out["pts"] = (out.exit - out.entry) * out.side
    return out


def compare(live, bt, tick=0.25, window=15):
    lo, hi = live.session.min(), live.session.max()
    bt = bt[(bt.session >= lo) & (bt.session <= hi)].reset_index(drop=True)
    used = set(); rows = []
    for i, r in live.iterrows():
        c = bt[(bt.session == r.session) & (bt.side == r.side)]
        c = c[~c.index.isin(used)]
        if len(c):
            dt = (c.entry_time - r.entry_time).abs()
            j = dt.idxmin()
            if dt[j] <= pd.Timedelta(minutes=window):
                used.add(j); b = bt.loc[j]
                rows.append(dict(status="matched", session=r.session, side=r.side, live_entry_time=r.entry_time, bt_entry_time=b.entry_time,
                                 live_entry=r.entry, bt_entry=b.entry, live_exit=r.exit, bt_exit=b.exit,
                                 entry_slip_ticks=r.side * (r.entry - b.entry) / tick, exit_slip_ticks=r.side * (b.exit - r.exit) / tick,
                                 live_pts=r.pts, bt_pts=b.pts, live_exit_signal=r.exit_signal, bt_exit_signal=b.exit_signal))
                continue
        rows.append(dict(status="extra (live only)", session=r.session, side=r.side, live_entry_time=r.entry_time, live_entry=r.entry,
                         live_exit=r.exit, live_pts=r.pts, bt_pts=0.0, live_exit_signal=r.exit_signal))
    for j, b in bt.iterrows():
        if j not in used:
            rows.append(dict(status="missed (backtest only)", session=b.session, side=b.side, bt_entry_time=b.entry_time, bt_entry=b.entry,
                             bt_exit=b.exit, live_pts=0.0, bt_pts=b.pts, bt_exit_signal=b.exit_signal))
    return pd.DataFrame(rows).sort_values("session").reset_index(drop=True), bt


def report(name, live, bt, tick=0.25, window=15, csv=None):
    T, btp = compare(live, bt, tick, window)
    m = T[T.status == "matched"]
    print(f"\n=== {name}: live {len(live)} trades ({live.session.min().date()} .. {live.session.max().date()}), backtest {len(btp)} in the same period")
    print(f"   matched {len(m)}, missed (backtest only) {int((T.status.str.startswith('missed')).sum())}, extra (live only) {int((T.status.str.startswith('extra')).sum())}")
    if len(m):
        print(f"   slippage vs backtest, ticks (+ = worse): entry mean {m.entry_slip_ticks.mean():+.2f} (median {m.entry_slip_ticks.median():+.1f}),"
              f" exit mean {m.exit_slip_ticks.mean():+.2f} (median {m.exit_slip_ticks.median():+.1f})")
        diff_exit = (m.live_exit_signal != m.bt_exit_signal).mean()
        print(f"   matched trades: live {m.live_pts.mean():+.2f} pts / contract vs backtest {m.bt_pts.mean():+.2f}; different exit signal on {diff_exit:.0%}")
    tot_b, tot_l = T.bt_pts.sum(), T.live_pts.sum()
    ratio = tot_l / tot_b if tot_b != 0 else np.nan
    print(f"   total points per contract: live {tot_l:+.2f} vs backtest {tot_b:+.2f} -> edge ratio {ratio:.2f}")
    n = len(btp)
    if n < 40: verdict = f"too early ({n} backtest trades; judge after ~40)"
    elif tot_b <= 0: verdict = "backtest itself is flat or negative over this period: judge on slippage and matching, not the ratio"
    elif ratio >= 0.75: verdict = "OK to scale (edge ratio >= 0.75)"
    elif ratio >= 0.5: verdict = "hold the current number of accounts (0.5-0.75); look at slippage and missed trades"
    else: verdict = "stop scaling and investigate (edge ratio < 0.5)"
    print(f"   decision: {verdict}")
    if csv: T.to_csv(csv, index=False); print(f"   trade-by-trade file: {csv}")
    return T, ratio


def selftest():
    path = KEYS["LDF_MC"]; bt = read_trades(path)
    live = bt[bt.session >= "2025-01-01"].copy()
    rng = np.random.default_rng(1)
    live = live.drop(live.sample(frac=0.05, random_state=1).index)               # 5% missed
    live["entry"] = live.entry + live.side * 0.25 * rng.integers(0, 3, len(live))  # 0-2 ticks worse entries
    live["pts"] = (live.exit - live.entry) * live.side; live["qty"] = 10
    T, r = report("self-test (LDF backtest vs a perturbed copy of itself)", live, bt)
    m = T[T.status == "matched"]
    assert abs(m.entry_slip_ticks.mean() - 1.0) < 0.2 and (T.status.str.startswith("missed")).mean() > 0.03, "self-test failed"
    print("   self-test OK (expected entry slippage ~+1 tick, ~5% missed)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("live", nargs="?"); ap.add_argument("backtest", nargs="?")
    ap.add_argument("--tick", type=float, default=0.25); ap.add_argument("--window", type=int, default=15)
    ap.add_argument("--all"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.all:
        res = {}
        for k, btpath in KEYS.items():
            f = os.path.join(a.all, f"{k}_live.xlsx")
            if os.path.exists(f) and os.path.exists(btpath):
                _, res[k] = report(k, read_trades(f), read_trades(btpath), a.tick, a.window, csv=f.replace(".xlsx", "_vs_backtest.csv"))
        print("\nEdge ratios:", {k: round(v, 2) for k, v in res.items()})
    else:
        report(os.path.basename(a.live), read_trades(a.live), read_trades(a.backtest), a.tick, a.window,
               csv=a.live.replace(".xlsx", "_vs_backtest.csv"))
