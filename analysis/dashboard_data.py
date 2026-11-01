"""Data files for the 'Apex Live Desk' dashboard (https://claude.ai/artifact/3oqbHWqBFTrUQd95wMmuL8).
Reads live/trades/*.csv (VPS trade logger) and live/health/*.csv, plus the account facts in ACCOUNTS below, and writes
analysis/outputs/dashboard/{accounts,trades,health}.json. After a run, upload the three files to the dashboard
(Artifact asset upload, then update each dataset's url / name / updated).
  python3 analysis/dashboard_data.py
P&L is MultiCharts' gross per the logger (no fees); balances are 'last Apex balance the user reported + logged P&L since'.
"""
import glob, json, os, datetime as dt
import sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

COLS = ["event", "tag", "symbol", "side", "contracts", "entry_date", "entry_time", "entry_price", "exit_date",
        "exit_time", "exit_price", "profit_usd", "bar_date", "bar_time"]
NAMES = {"VB": "Vault Break", "ONB": "ONB ADX30", "EOS": "EOS", "MON_BR": "Bridge Monday", "ONB_ML": "ONB ML",
         "MON": "Monday Long", "LDF": "Late-Day Flow", "NFP": "NFP Fade", "MOC_MES": "ES MOC", "RS": "Relative Strength"}
# tag suffix -> account. "" = #1 (50K, -01), "-2" = #2 (50K, -02), "150" = #3 (150K No-Activation, -03)
ACCOUNTS = [
    # update last_balance / last_date whenever the user reports an Apex end-of-day balance
    dict(account="#1", id="APEX-681524-01", size="50K evaluation", status="Blown", start=50000, floor=None,
         last_balance=None, last_date="2026-10-26", note="Blown 2026-10-26; trades after that are not counted."),
    dict(account="#2", id="APEX-681524-02", size="50K evaluation", status="Trading", start=50000, floor=48764.42,
         last_balance=50764.42, last_date="2026-10-28",
         note="Balance from the Order and Position Tracker 10/28 evening. Floor assumes 10/28 is its highest end-of-day balance (peak - $2,000). 10/26 #3's 150K-size orders hit this account: logged P&L that day may not match fills."),
    dict(account="#3", id="APEX-681524-03", size="150K No-Activation", status="Blown", start=150000, floor=None,
         last_balance=147822.60, last_date="2026-10-28",
         note="Blown 2026-10-30: Apex liquidated the Overnight Bias short at 28,780 (09:38 CT) when equity touched the $146,000 floor intraday. $4,000 EOD trailing; target +$9,000. Started 10/26. Balance from the Order and Position Tracker 10/28 evening (user screenshot)."),
    dict(account="#4", id="APEX-681524-04", size="150K No-Activation", status="Trading", start=150000, floor=146000.0,
         last_balance=150000.0, last_date="2026-11-01",
         note="Bought 2026-11-01 (despite the buy gate's PAUSE: live/overrides.csv). First session 11/02. Reuses the VB150 / ONB150 / EOS150 / MON_BR150 charts."),
]
CLOSED_AFTER = {"#1": "20261026", "#3": "20261030"}
OUT = "analysis/outputs/dashboard"


def split(tag):
    tag = str(tag)
    if tag.endswith("150"): return tag[:-3], "#3"
    base, _, acct = tag.partition("-")
    return base, {"": "#1", "2": "#2"}.get(acct, "#" + acct)


def main():
    df = pd.concat([pd.read_csv(f, header=None, names=COLS, dtype=str) for f in sorted(glob.glob("live/trades/*.csv"))])
    df = df[df.event == "CLOSE"].drop_duplicates()
    rows = []
    for r in df.itertuples():
        strat, acct = split(r.tag)
        if acct in CLOSED_AFTER and r.exit_date > CLOSED_AFTER[acct]: continue
        d = f"{r.exit_date[:4]}-{r.exit_date[4:6]}-{r.exit_date[6:]}"
        rows.append(dict(trade_id=f"{acct}-{r.tag}-{r.entry_date}-{r.entry_time}", date=d, account=acct,
                         strategy=NAMES.get(strat, strat), side=r.side, contracts=int(r.contracts),
                         entry_time=f"{int(r.entry_time) // 100:02d}:{int(r.entry_time) % 100:02d}",
                         exit_time=f"{int(r.exit_time) // 100:02d}:{int(r.exit_time) % 100:02d}",
                         entry=float(r.entry_price), exit=float(r.exit_price), pnl=float(r.profit_usd)))
    trades = sorted(rows, key=lambda x: (x["date"], x["entry_time"], x["account"]))
    # real balances from the Apex Chart Monitor's ACCT rows (net worth as Rithmic reports it), when installed
    allrows = pd.concat([pd.read_csv(f, header=None, names=COLS, dtype=str) for f in sorted(glob.glob("live/trades/*.csv"))])
    acct_rows = allrows[allrows.event == "ACCT"]
    live_bal = {}
    for r in acct_rows.itertuples():
        # Rithmic sends NetWorth 0 for Apex accounts; Equity = the balance (matches the Order and Position Tracker, 2026-10-29)
        nw = float(r.entry_date or 0) or float(r.entry_time or 0)
        if nw > 0: live_bal[r.side] = (f"{r.bar_date[:4]}-{r.bar_date[4:6]}-{r.bar_date[6:]}", nw)
    accts = []
    for a in ACCOUNTS:
        if a["id"] in live_bal and a["status"] != "Blown":
            a = dict(a, last_date=live_bal[a["id"]][0], last_balance=live_bal[a["id"]][1],
                     note=a["note"] + " Balance from Rithmic (Apex Chart Monitor).")
        since = sum(t["pnl"] for t in trades if t["account"] == a["account"] and t["date"] > a["last_date"])
        est = None if a["last_balance"] is None else round(a["last_balance"] + since, 2)
        accts.append(dict(a, logged_since=round(since, 2), est_balance=est,
                          room=None if est is None or a["floor"] is None else round(est - a["floor"], 2),
                          trades=sum(t["account"] == a["account"] for t in trades),
                          net_logged=round(sum(t["pnl"] for t in trades if t["account"] == a["account"]), 2)))
    health = []
    for f in sorted(glob.glob("live/health/*.csv")):
        for line in open(f):
            p = line.strip().split(",")
            kv = dict(x.split("=", 1) for x in p[2:] if "=" in x and not x.startswith("last_reject"))
            health.append(dict(check=f"{p[1]} {p[0]}", time=p[1], mode=p[0], mc_processes=int(kv.get("mc_processes", 0)),
                               disk_free_gb=float(kv.get("disk_free_gb", 0)), log_rows=int(kv.get("log_rows_today", 0)),
                               push_errors=int(kv.get("push_errors", 0)),
                               rejected=int(kv["rejected_today"]) if "rejected_today" in kv else None))
    import re, vps_health
    checks = []
    for day in sorted({os.path.basename(f)[:8] for f in glob.glob("live/trades/*.csv") + glob.glob("live/health/*.csv")})[-10:]:
        d = dt.date(int(day[:4]), int(day[4:6]), int(day[6:]))
        for i, line in enumerate(vps_health.check(d)):
            text = line.lstrip("- ").strip()
            alert = text.startswith("**")
            checks.append(dict(check_id=f"{d} {i + 1:02d}", date=str(d), level="Alert" if alert else "Note",
                               item=re.sub(r"\*\*|`", "", text)))
    checks.sort(key=lambda c: c["check_id"], reverse=True)
    os.makedirs(OUT, exist_ok=True)
    for name, data in (("accounts", accts), ("trades", trades), ("health", health), ("checks", checks)):
        json.dump(data, open(f"{OUT}/{name}.json", "w"), indent=1)
    print(f"{len(trades)} trades, {len(health)} health rows; written {OUT}/ at {dt.datetime.now():%Y-%m-%d %H:%M}")
    for a in accts: print(a["account"], a["status"], a["est_balance"], a["room"], a["trades"], a["net_logged"])


if __name__ == "__main__":
    main()
    # the three backtest panels (Monte Carlo range, edge per strategy, missed-trade alarm) need accounts.json first
    import runpy
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "live_panels.py"), run_name="__main__")
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "account_tools.py"), run_name="__main__")
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_tools.py"), run_name="__main__")   # lab_stats / lab_studies
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_bars_merge.py"), run_name="__main__")
