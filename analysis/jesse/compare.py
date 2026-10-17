"""Jesse vs MultiCharts, trade by trade (2026-10-17). Reads SCRATCH/jesse_<Strategy>.csv (run_all.py) and the strategy's
MultiCharts report, over the report's own date range.
  python3 analysis/jesse/compare.py [SCRATCH_DIR] [Strategy ...]
Per strategy: trades in each, days traded by both / only one, same side, entry and exit price differences, P&L per trade
(gross, and net of $7.25 + 1 tick per market / stop fill, as the testing standard), by year, and the largest mismatches.
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
R = "Backtesting Strategy Performance Report "
REPORTS = {  # strategy: (report, point value, tick, cost per fill)
    "VaultBreak": (R + "VB v1.xlsx", 20.0, 0.25, 7.25),
    "ONBias": (R + "ONB v2.xlsx", 20.0, 0.25, 7.25),
    "ONBiasADX30": (R + "_ @NQ - 15 Minutes NQ Overnight Bias.xlsx", 20.0, 0.25, 7.25),
    "ONBiasML": (R + "_ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx", 20.0, 0.25, 7.25),
    "MondayLong": (R + "_ @NQ - 5 Minutes NQ Monday Longs.xlsx", 20.0, 0.25, 7.25),
    "ExpOpenShort": (R + "EOS v1.xlsx", 20.0, 0.25, 7.25),
    "LateDayFlow": (R + "_ @NQ - 5 Minutes Late Day Flow.xlsx", 20.0, 0.25, 7.25),
    "NFPFade": (R + "_ @NQ - 5 Minutes NFP Fade.xlsx", 20.0, 0.25, 7.25),
    "CLSundayFade": (R + "_ CL - 5 Minutes CL Sunday Gap.xlsx", 1000.0, 0.01, 7.25),
    "ESMOCFollow": (R + "_ @ES - 5 Minutes ES MOC Follow.xlsx", 50.0, 0.25, 5.0),
}


def mc_trades(path):
    raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
    ent = raw[raw["Type"].astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = raw[raw["Type"].astype(str).str.startswith("Exit")].reset_index(drop=True)
    n = min(len(ent), len(ex)); ent, ex = ent.iloc[:n], ex.iloc[:n]
    side = np.where(ent["Type"].astype(str).str.contains("Long"), 1, -1)
    sig = ex["Signal"].astype(str)
    return pd.DataFrame(dict(entry_time=pd.to_datetime(ent["Date"]), exit_time=pd.to_datetime(ex["Date"]), side=side,
                             entry=ent["Price"].astype(float).to_numpy(), exit=ex["Price"].astype(float).to_numpy(),
                             target=sig.str.contains("Profit|Target").to_numpy(),
                             points=(ex["Price"].astype(float).to_numpy() - ent["Price"].astype(float).to_numpy()) * side))


def net(df, pv, tick, cost):
    slips = 1 + (~df["target"]).astype(int)
    return df.points * pv - 2 * cost - slips * tick * pv


def summary(x):
    x = pd.Series(x).dropna()
    if len(x) == 0: return "n 0"
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return f"n {len(x):4d}  avg ${x.mean():6.0f}  PF {pf:4.2f}  win {np.mean(x > 0):4.0%}  t {x.mean() / x.std() * np.sqrt(len(x)):4.1f}"


def compare(name, out):
    path, pv, tick, cost = REPORTS[name]
    m = mc_trades(path)
    j = pd.read_csv(SP + f"jesse_{name}.csv", parse_dates=["entry_time", "exit_time"])
    lo, hi = m.entry_time.min().normalize(), m.entry_time.max().normalize() + pd.Timedelta(days=1)
    j = j[(j.entry_time >= lo) & (j.entry_time < hi)].reset_index(drop=True)
    for d in (m, j):
        d["day"] = d.entry_time.dt.normalize(); d["k"] = d.groupby("day").cumcount()
    mm = m.merge(j.drop(columns=[c for c in ('how',) if c in j]), on=["day", "k"], how="outer", suffixes=("_mc", "_j"), indicator="src")
    both = mm[mm.src == "both"]
    same_side = (both.side_mc == both.side_j).mean() if len(both) else np.nan
    de = (both.entry_j - both.entry_mc).abs() / tick; dx = (both.exit_j - both.exit_mc).abs() / tick
    dp = (both.points_j - both.points_mc) * pv
    jn = j.points * pv - 2 * cost - 2 * tick * pv          # Jesse: no exit-type label, 2 slips on every trade (conservative)
    mn_same = m.points * pv - 2 * cost - 2 * tick * pv
    L = [f"\n=== {name}  ({path.replace(R, '')}; {lo.date()} .. {(hi - pd.Timedelta(days=1)).date()})",
         f"   trades: MultiCharts {len(m)}, Jesse {len(j)}; same day and order {len(both)} "
         f"(only MC {int((mm.src == 'left_only').sum())}, only Jesse {int((mm.src == 'right_only').sum())}); same side {same_side:.1%}",
         f"   matched trades: entry within 1 tick {np.mean(de <= 1):.1%} (median {de.median():.0f} ticks), exit within 1 tick {np.mean(dx <= 1):.1%}, "
         f"P&L within $50 {np.mean(dp.abs() <= 50):.1%}, P&L corr {np.corrcoef(both.points_mc, both.points_j)[0, 1]:.3f}",
         f"   gross per contract  MC    {summary(m.points * pv)}",
         f"                       Jesse {summary(j.points * pv)}",
         f"   net, 2 slips each   MC    {summary(mn_same)}",
         f"                       Jesse {summary(jn)}",
         "   by year (gross $, MC / Jesse): " + " | ".join(
             f"{y} {a:,.0f}/{b:,.0f}" for y, a, b in pd.DataFrame({"a": (m.points * pv).groupby(m.entry_time.dt.year).sum(),
                                                                       "b": (j.points * pv).groupby(j.entry_time.dt.year).sum()}).fillna(0).itertuples())]
    big = both.assign(dp=dp).reindex(dp.abs().sort_values(ascending=False).index).head(5)
    for r in big.itertuples():
        L.append(f"      {r.day.date()} #{r.k}: MC {'L' if r.side_mc > 0 else 'S'} {r.entry_mc:.2f}->{r.exit_mc:.2f} ({r.exit_time_mc:%H:%M})  "
                 f"Jesse {'L' if r.side_j > 0 else 'S'} {r.entry_j:.2f}->{r.exit_j:.2f} ({r.exit_time_j:%H:%M})  diff ${r.dp:,.0f}")
    only = mm[mm.src != "both"].head(8)
    for r in only.itertuples():
        L.append(f"      only {'MC' if r.src == 'left_only' else 'Jesse'}: {r.day.date()} #{r.k}")
    s = "\n".join(L); print(s, flush=True); out.append(s)
    return m, j, both


if __name__ == "__main__":
    out = []
    for n in sys.argv[2:] or list(REPORTS):
        try:
            compare(n, out)
        except FileNotFoundError as e:
            print(f"{n}: missing {e.filename}")
