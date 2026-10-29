"""Pre-market check (2026-10-29): is every live chart ready before the 08:30 CT open? Reads today's VPS log as pushed at
08:15 CT (live/trades/YYYYMMDD.csv, the VpsHealthOpen task) and live/expected_setup.json. Per expected chart: the Apex Chart
Monitor's last ACCT row (auto-trading on, right account, chart's last bar fresh) and the logger's last POS row (strategy
position = broker position). Prints one line per problem, or 'ALL GREEN'. Run by the 08:22 CT check-in.
  python3 analysis/premarket_check.py [YYYY-MM-DD]
"""
import sys, os, json, datetime as dt
import pandas as pd

COLS = ["event", "tag", "symbol", "side", "contracts", "entry_date", "entry_time", "entry_price", "exit_date",
        "exit_time", "exit_price", "profit_usd", "bar_date", "bar_time"]


def has_sig(tag):
    """True once a chart's strategy has written a heartbeat (SIG row) in any log: stays silent until it's installed."""
    import glob
    return any(f",{tag}," in l and l.startswith("SIG,") for f in glob.glob("live/trades/*.csv") for l in open(f))


def check(day):
    cfg = json.load(open("live/expected_setup.json")); out = []
    d = day.strftime("%Y%m%d"); f = f"live/trades/{d}.csv"; h = f"live/health/{d}.csv"
    if not os.path.exists(h) or not any(l.startswith("open,") for l in open(h)):
        out.append("VPS 08:15 check-in missing (VPS down, task not run, or push failed).")
    if not os.path.exists(f):
        return out + ["No log file for today: no chart has written since midnight (MultiCharts or logger not running?)."]
    df = pd.read_csv(f, header=None, names=COLS, dtype=str)
    want = {t: [v["id"] for v in cfg["accounts"].values() if v.get("status") == "live" and v["suffix"] and t.endswith(v["suffix"])]
            for t in cfg["charts"]}
    for tag in cfg["charts"]:
        sig = df[(df.event == "SIG") & (df.tag == tag)]
        if sig.empty and has_sig(tag):
            out.append(f"{tag}: the STRATEGY wrote no heartbeat today: not compiled, removed or stopped (chart may look normal).")
        a = df[(df.event == "ACCT") & (df.tag == tag)]
        if a.empty:
            out.append(f"{tag}: no monitor line today (chart closed or monitor missing)."); continue
        r = a.iloc[-1]
        if str(r.contracts) != "1": out.append(f"{tag}: auto-trading OFF (last line {int(r.bar_time):04d}).")
        if want[tag] and r.side != want[tag][0]: out.append(f"{tag}: monitor account {r.side}, expected {want[tag][0]}.")
        if float(r.entry_price or 0) > 900: out.append(f"{tag}: chart's last bar {float(r.entry_price) / 60:.0f} min old (feed?).")
        p = df[(df.event == "POS") & (df.tag == tag)]
        if len(p) and p.iloc[-1].contracts != p.iloc[-1].profit_usd:
            out.append(f"{tag}: strategy position {p.iloc[-1].contracts} vs broker {p.iloc[-1].profit_usd}.")
    for t in sorted(set(df[df.event.isin(["POS", "ACCT", "SIG"])].tag) - set(cfg["charts"])):
        out.append(f"{t}: unexpected chart running (retired account or wrong tag).")
    return out


if __name__ == "__main__":
    day = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=5)).date()
    o = check(day)
    print("\n".join(o) if o else "ALL GREEN: every live chart has auto-trading on, the right account, a fresh feed and a matching position.")
