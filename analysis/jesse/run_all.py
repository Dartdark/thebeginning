"""Run every current strategy through Jesse (an independent backtest engine) on our own 1-minute data, and compare trade by
trade with the MultiCharts reports (2026-10-17, user: 'run all current strategies through jesse here and see if anything
sticks out / can be improved').

Setup (not in git): a Python 3.12 venv with `pip install jesse` (Jesse 3.4; numpy 1.26 has no Python 3.13 wheel), then
  python3 analysis/jesse/build_candles.py scratch_data
  <venv>/bin/python analysis/jesse/run_all.py scratch_data [Strategy ...]
Jesse runs without its database: research.backtest is told this is not a Jesse project (it only skips storing trades).
Engine differences that are expected, not bugs: Jesse fills a market order at the decision bar's CLOSE (MultiCharts: the
next bar's open, the same price within a tick on continuous data); a stop / target fills at its price (MultiCharts with
Bar Magnifier: the same, except a bar that opens through the level fills at that open).
Output: SCRATCH/jesse_<Strategy>.csv (Jesse trades), and a comparison per strategy printed and saved by compare.py.
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jesse.helpers as jh
jh.is_jesse_project = lambda: False            # no Postgres: research mode without storing trades
import numpy as np, pandas as pd
from jesse import research

SP = os.path.abspath((sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/")) + "/"
RUNS = {  # strategy: (candle file, timeframe, point value, tick)
    "VaultBreak": ("jesse_nq.npy", "30m", 20.0, 0.25),
    "ONBias": ("jesse_nq.npy", "15m", 20.0, 0.25),
    "ONBiasADX30": ("jesse_nq.npy", "15m", 20.0, 0.25),
    "ONBiasML": ("jesse_nq.npy", "15m", 20.0, 0.25),
    "MondayLong": ("jesse_nq.npy", "5m", 20.0, 0.25),
    "ExpOpenShort": ("jesse_nq.npy", "5m", 20.0, 0.25),
    "LateDayFlow": ("jesse_nq.npy", "5m", 20.0, 0.25),
    "NFPFade": ("jesse_nq.npy", "5m", 20.0, 0.25),
    "CLSundayFade": ("jesse_cl_et.npy", "5m", 1000.0, 0.01),
    # Antigravity's GoldenCross (2026-10-17): as written (holds overnight) and Apex-flat at 15:00 CT; 1-hour bars as its report
    "GoldenCross": ("jesse_nq.npy", "1h", 20.0, 0.25),
    "GoldenCrossEOD": ("jesse_nq.npy", "1h", 20.0, 0.25),
}


def run(name):
    f, tf, pv, tick = RUNS[name]
    c = np.load(SP + f)
    sym = "CL-USD" if "cl" in f else "NQ-USD"
    config = {"starting_balance": 1e9, "fee": 0, "type": "futures", "futures_leverage": 100,
              "futures_leverage_mode": "cross", "exchange": "Custom Data", "warm_up_candles": 0}
    routes = [{"exchange": "Custom Data", "strategy": name, "symbol": sym, "timeframe": tf}]
    t0 = time.time()
    r = research.backtest(config, routes, [], {f"Custom Data-{sym}": {"exchange": "Custom Data", "symbol": sym, "candles": c}})
    rows = []
    for t in r["trades"]:
        side = 1 if t["type"] == "long" else -1
        ex = [o for o in t["orders"] if o.get("reduce_only")]
        how = (ex[-1].get("submitted_via") or ex[-1]["type"]) if ex else ""
        rows.append(dict(entry_time=pd.Timestamp(int(t["opened_at"]), unit="ms"), exit_time=pd.Timestamp(int(t["closed_at"]), unit="ms"),
                         side=side, entry=t["entry_price"], exit=t["exit_price"], how=how,
                         points=(t["exit_price"] - t["entry_price"]) * side))
    df = pd.DataFrame(rows)
    df.to_csv(SP + f"jesse_{name}.csv", index=False)
    print(f"{name}: {len(df)} trades in {time.time() - t0:.0f}s", flush=True)
    return df


if __name__ == "__main__":
    names = sys.argv[2:] or list(RUNS)
    for n in names:
        run(n)
