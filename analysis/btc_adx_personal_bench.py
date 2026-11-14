"""BTC ADX longs on MBT (best version: both books ADX 40 / 50, spot signals, resting MBT stop; analysis/btc_adx_mbt_longs_stop_test.py)
against the PERSONAL book (user 2026-11-13 'how much does the best version help the personal book').
Base built locally (scratch_data/personal_P.pkl is cloud-only): analysis/personal_portfolio.py's pieces at 1 micro, minus the
forward-log / retired ones (FC2B, Kusho, S47, S30, VaultBreak), plus Noise-area longs 1 MNQ (checks/candidates/bridge_noise_15m/
trades_longs.csv, per NQ / 10) and Overnight Tick at 2 MNQ (user 2026-11-08). NOT included: CL Sunday fade's OVX sizing (2 MCL on
high-OVX weekends). BTC: $ per MBT after $2.50 + 1 tick a fill, booked on the exit day (CT), weekend exits on the next book day;
not marked to market overnight. Sizes 1 / 2 / 3 MBT per book. Add AND replace the piece it correlates with most.
Measure (bench150.personal): 1-year block MC (20-day blocks, 2,000 runs), median year $ / p95 drawdown, on 2019-26 (BTC's
window), 2019-22 and 2023+.
  tools/run_stamped.sh analysis/btc_adx_personal_bench.py > analysis/outputs/btc_adx_personal_bench_output.txt
"""
import sys, textwrap, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
print(__doc__.split("\n")[0])
src = open("analysis/personal_portfolio.py", encoding="utf-8").read()
head, body = src.split('if __name__ == "__main__":\n')
body = textwrap.dedent(body.split("    names = {")[0]).replace("print(__doc__", "pass  # print(__doc__")
ns = {}; exec(compile(head, "personal_portfolio_head", "exec"), ns); exec(compile(body, "personal_portfolio_body", "exec"), ns)
P, days, from_trades = ns["P"], ns["days"], ns["from_trades"]
P = P[[c for c in P.columns if c not in ("FC2B", "Kusho", "S47", "S30", "VaultBreak")]].copy()
nbl, _ = from_trades("checks/candidates/bridge_noise_15m/trades_longs.csv", "NoiseLongs"); P["NoiseLongs"] = nbl
P["OvernightTick"] *= 2
print(f"base pieces ({P.shape[1]}): {list(P.columns)}; days {days.min().date()} -> {days.max().date()}")

t = pd.read_csv("scratch_data/btc_adx_mbt_longs_stop_trades.csv", parse_dates=["t", "tx"])
ex = pd.DatetimeIndex(t.tx + pd.Timedelta(minutes=15)).tz_localize("UTC").tz_convert("America/Chicago").tz_localize(None).normalize()
t = t[ex <= days[-1]]; ex = ex[ex <= days[-1]]
btc = pd.Series(t.usd.to_numpy(), index=ns["to_trading_day"](ex)).groupby(level=0).sum().reindex(days, fill_value=0.0)
assert abs(btc.sum() - t.usd.sum()) < 1e-6
print(f"BTC longs: {len(t)} book trades to {days[-1].date()}, ${btc.sum() / ((t.t.max() - t.t.min()).days / 365.25):,.0f} a year per MBT per book")
cor = {c: np.corrcoef(btc[btc.index.year >= 2019], P[c][P.index.year >= 2019])[0, 1] for c in P}
top = max(cor, key=lambda c: cor[c])
print("daily corr with each piece (2019+): " + ", ".join(f"{c} {v:+.2f}" for c, v in sorted(cor.items(), key=lambda kv: -kv[1])))
print(f"corr with the whole book {np.corrcoef(btc[btc.index.year >= 2019], P.sum(axis=1)[P.index.year >= 2019])[0, 1]:+.2f}; most-overlapping piece: {top}")


def mc(x):
    d = MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1); return d["pnl_p50"], d["dd_p95"]


base = P.sum(axis=1)
V = {"book as is": base}
for k in (1, 2, 3): V[f"+ BTC longs {k} MBT a book"] = base + k * btc
for k in (1, 2): V[f"{top} -> BTC {k} MBT"] = base - P[top] + k * btc
for per, m in (("2019-26", days.year >= 2019), ("2019-22", (days.year >= 2019) & (days.year <= 2022)), ("2023+", days.year >= 2023)):
    print(f"\n{per}: {'variant':<30}{'$ a year p50':>13}{'DD p95':>10}{'ret/DD':>8}{'diff':>7}{'capital (DD/0.20)':>19}")
    r0 = None
    for nm, x in V.items():
        p50, dd = mc(x[m]); r = p50 / dd; r0 = r if r0 is None else r0
        print(f"        {nm:<30}${p50:>11,.0f} ${dd:>8,.0f} {r:7.2f} {r - r0:+6.2f} ${dd / 0.20:>16,.0f}")
