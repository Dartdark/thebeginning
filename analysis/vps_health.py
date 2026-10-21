"""VPS health check for the journal (2026-10-21). Reads the POS rows the Apex Trade Logger writes (strategy position vs the
broker's position for that strategy, on every change and every 30 minutes) from live/trades/YYYYMMDD.csv, and the VPS
health lines from live/health/YYYYMMDD.csv (written by live/vps/push_trade_logs.ps1 at 08:15 and 16:10 CT). Flags:
  MISMATCH  a chart's strategy position differs from the broker's position for it (the 'chart thinks it is long' problem)
  STALE     no heartbeat from a chart for > 70 minutes between 08:30 and 15:00 CT (frozen chart / dropped feed)
  VPS       MultiCharts not running, disk < 5 GB, push errors, or the morning / evening check missing
Called by analysis/journal_trades.py (the 16:40 CT job), so nothing has to be started by hand.
  python3 analysis/vps_health.py [YYYY-MM-DD]
"""
import sys, os, datetime as dt
import pandas as pd

COLS = ["event", "tag", "symbol", "side", "contracts", "entry_date", "entry_time", "entry_price", "exit_date",
        "exit_time", "exit_price", "profit_usd", "bar_date", "bar_time"]


def mins(t): t = int(t); return t // 100 * 60 + t % 100


def check(day):
    d = day.strftime("%Y%m%d"); out = []
    f = f"live/trades/{d}.csv"
    if os.path.exists(f):
        df = pd.read_csv(f, header=None, names=COLS, dtype=str)
        pos = df[df.event == "POS"].copy()
        if pos.empty:
            out.append("- Health rows not active yet: recompile the updated Apex Trade Logger once (outside market hours).")
        else:
            pos["s"] = pos.contracts.astype(float); pos["b"] = pos.profit_usd.astype(float); pos["m"] = pos.bar_time.map(mins)
            for tag, g in pos.groupby("tag"):
                bad = g[g.s != g.b]
                if len(bad):
                    r = bad.iloc[-1]
                    out.append(f"- **MISMATCH {tag}** at {int(r.bar_time):04d} CT: strategy {int(r.s):+d}, broker {int(r.b):+d}. "
                               "Check the account; with it flat, auto-trading off / on (MULTICHARTS_PITFALLS.md).")
                rth = sorted(g[(g.m >= mins(830)) & (g.m <= mins(1500))].m)
                edges = [mins(830)] + rth + [mins(1500)]
                gap = max(b - a for a, b in zip(edges, edges[1:]))
                if day.weekday() < 5 and gap > 70:
                    out.append(f"- **STALE {tag}**: a {gap}-minute gap in its heartbeat between 08:30 and 15:00 CT (frozen chart or feed?).")
    elif day.weekday() < 5:
        out.append("- No trade-log file for today on the VPS push (logger, C:\\TradingLogs or the 16:10 push task?).")
    h = f"live/health/{d}.csv"
    if os.path.exists(h):
        rows = [l.strip().split(",") for l in open(h) if l.strip()]
        modes = {r[0] for r in rows}
        for r in rows:
            kv = dict(x.split("=", 1) for x in r[2:] if "=" in x)
            if kv.get("mc_processes", "1") == "0": out.append(f"- **VPS ({r[0]} {r[1]}): MultiCharts not running.**")
            if float(kv.get("disk_free_gb", "99")) < 5: out.append(f"- VPS ({r[0]}): only {kv['disk_free_gb']} GB free on C:.")
            if kv.get("push_errors", "0") not in ("0", ""): out.append(f"- VPS: {kv['push_errors']} lines in push_errors.txt.")
        if day.weekday() < 5 and "open" not in modes: out.append("- VPS morning check (08:15) did not report today.")
    elif day.weekday() < 5:
        out.append("- No VPS health line today (the updated push script installs itself at its next 16:10 run).")
    return out


def block(day):
    o = check(day)
    return ["", "### Health (auto)", ""] + (o if o else ["- All clear: positions match the broker, heartbeats regular, VPS OK."])


if __name__ == "__main__":
    day = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=5)).date()
    print("\n".join(block(day)))
