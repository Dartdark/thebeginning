"""VPS health check for the journal (2026-10-21). Reads the POS rows the Apex Trade Logger writes (strategy position vs the
broker's position for that strategy, on every change and every 30 minutes) from live/trades/YYYYMMDD.csv, and the VPS
health lines from live/health/YYYYMMDD.csv (written by live/vps/push_trade_logs.ps1 at 08:15 and 16:10 CT). Flags:
  MISMATCH  a chart's strategy position differs from the broker's position for it (the 'chart thinks it is long' problem)
  STALE     no heartbeat from a chart for > 70 minutes between 08:30 and 15:00 CT (frozen chart / dropped feed)
  VPS       MultiCharts not running, disk < 5 GB, push errors, or the morning / evening check missing
Called by analysis/journal_trades.py (the 16:40 CT job), so nothing has to be started by hand.
  python3 analysis/vps_health.py [YYYY-MM-DD]
"""
import sys, os, re, datetime as dt
import pandas as pd

COLS = ["event", "tag", "symbol", "side", "contracts", "entry_date", "entry_time", "entry_price", "exit_date",
        "exit_time", "exit_price", "profit_usd", "bar_date", "bar_time"]


def mins(t): t = int(t); return t // 100 * 60 + t % 100


def setup_check(df, day, path="live/expected_setup.json"):
    """Compare the day's log with live/expected_setup.json: every live chart heartbeats, no unknown chart, entry sizes
    as planned (catches a chart left on, a copied chart with old inputs, a size typo) (2026-10-29)."""
    import json
    if not os.path.exists(path): return []
    cfg = json.load(open(path)); charts = cfg["charts"]; retired = set(cfg.get("retired_tags", [])); out = []
    seen = set(df[df.event == "POS"].tag)
    if day.weekday() < 5:
        for t in charts:
            if t not in seen: out.append(f"- **SETUP {t}**: no heartbeat today: chart closed, logger missing, or auto-trading off?")
    for t in sorted(seen - set(charts)):
        if t in retired:
            out.append(f"- **RETIRED {t}**: chart of a closed account is still running (orders get rejected, rejection alarms drown real ones): turn its auto-trading off / close it on the VPS.")
        else:
            out.append(f"- **SETUP {t}**: unknown chart tag (not in live/expected_setup.json): typo in the logger Tag, or a new chart?")
    for r in df[df.event == "OPEN"].itertuples():
        c = charts.get(r.tag)
        if c is None: continue
        q = int(float(r.contracts))
        if c.get("qty") is not None and q != c["qty"]:
            out.append(f"- **SIZE {r.tag}**: entered {q} contracts at {int(r.entry_time):04d}, plan is {c['qty']}. Check the strategy inputs.")
        elif c.get("qty") is None and q > c.get("max_qty", 1e9):
            out.append(f"- **SIZE {r.tag}**: entered {q} contracts, above the {c['max_qty']} ceiling. Check the risk input.")
    out += monitor_check(df, day, cfg)
    return out


def monitor_check(df, day, cfg):
    """ACCT rows from the Apex Chart Monitor signal (2026-10-29): account binding typed, auto-trading on, feed alive,
    Rithmic reporting the balance. Only during RTH 08:30-15:00 CT on weekdays; silent until the monitor is installed."""
    out = []
    if day.weekday() < 5:
        import glob
        ever = {l.split(",")[1] for f in glob.glob("live/trades/*.csv") for l in open(f) if l.startswith("SIG,")}
        sig = df[df.event == "SIG"].copy(); sig["m"] = sig.bar_time.map(mins)
        for tag in cfg["charts"]:
            g = sig[(sig.tag == tag) & (sig.m >= mins(830)) & (sig.m <= mins(1500))]
            if g.empty:
                out.append(f"- **STRATEGY {tag}**: no heartbeat from the strategy during RTH: not compiled / removed / stopped. It could not trade.")
            else:
                edges = [mins(830)] + sorted(g.m) + [mins(1500)]
                gap = max(b - a for a, b in zip(edges, edges[1:]))
                if gap > 70: out.append(f"- **STRATEGY {tag}**: a {gap}-minute gap in the strategy's heartbeat during RTH.")
    a = df[df.event == "ACCT"].copy()
    if a.empty or day.weekday() >= 5: return out
    a["m"] = a.bar_time.map(mins); a = a[(a.m >= mins(830)) & (a.m <= mins(1500))]
    ids = {v["id"] for v in cfg["accounts"].values() if v.get("status") == "live"}
    for tag, g in a.groupby("tag", sort=False):
        if tag not in cfg["charts"]: continue
        acct = str(g.side.iloc[-1])
        want = [v["id"] for v in cfg["accounts"].values() if v.get("status") == "live" and v["suffix"] and tag.endswith(v["suffix"])]
        if acct not in ids or (want and acct != want[0]):
            out.append(f"- **ACCOUNT {tag}**: monitor AccountName is '{acct}', this chart belongs to {want[0] if want else 'a live account'}. "
                       "Check the strategy's Auto Trading gear account too (MULTICHARTS_PITFALLS.md, copied charts).")
        route = str(g.exit_date.iloc[-1]) if "exit_date" in g and str(g.exit_date.iloc[-1]) not in ("nan", "") else ""
        wid = cfg["accounts"].get(cfg["charts"][tag].get("account", ""), {}).get("id")
        if route and wid and route != wid:   # route_account = GetAccountID (2026-11-01): where orders really go
            out.append(f"- **ROUTING {tag}**: the chart SENDS ORDERS TO {route}, should be {wid}. Fix its Auto Trading gear account.")
        off = g[g.contracts.astype(float) == 0]
        if len(off): out.append(f"- **AUTO-TRADING OFF {tag}** at {', '.join(f'{int(t):04d}' for t in off.bar_time.unique()[:6])} CT: the strategy could not trade.")
        old = g[g.entry_price.astype(float) > 600]
        if len(old): out.append(f"- **FEED {tag}**: the chart's last bar was over 10 min old at {', '.join(f'{int(t):04d}' for t in old.bar_time.unique()[:6])} CT (data feed / Rithmic quiet).")
        if ((g.entry_date.astype(float) == 0) & (g.entry_time.astype(float) == 0)).all(): out.append(f"- {tag}: Rithmic reports no balance for {acct} (NetWorth and Equity 0): the dashboard keeps the reported balance.")
    return out


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
            for tag, g in pos.groupby("tag", sort=False):
                # rows are in write order. Only the LAST row counts as an open mismatch: a mismatch that a later row
                # resolves is the broker position updating a moment after the fill (Codex live audit, 2026-10-22)
                last = g.iloc[-1]
                if last.s != last.b:
                    out.append(f"- **MISMATCH {tag}** (still open at the last row, {int(last.bar_time):04d} CT): strategy "
                               f"{int(last.s):+d}, broker {int(last.b):+d}. Check the account; with it flat, auto-trading off / on "
                               "(MULTICHARTS_PITFALLS.md).")
                else:
                    bad = g[g.s != g.b]
                    if bad.bar_time.nunique() > 1:
                        out.append(f"- Mismatch {tag} seen in {bad.bar_time.nunique()} bars ({', '.join(f'{int(t):04d}' for t in bad.bar_time.unique())}), "
                                   "resolved by the last row (informational).")
                rth = sorted(g[(g.m >= mins(830)) & (g.m <= mins(1500))].m)
                edges = [mins(830)] + rth + [mins(1500)]
                gap = max(b - a for a, b in zip(edges, edges[1:]))
                if day.weekday() < 5 and gap > 70:
                    out.append(f"- **STALE {tag}**: a {gap}-minute gap in its heartbeat between 08:30 and 15:00 CT (frozen chart or feed?).")
        out += setup_check(df, day)
    elif day.weekday() < 5:
        out.append("- No trade-log file for today on the VPS push (logger, C:\\TradingLogs or the 16:10 push task?).")
    # contract roll weeks: the mapping must move to the next contract (MULTICHARTS_PITFALLS.md roll checklist)
    if day.month in (3, 6, 9, 12) and 4 <= day.day <= 14:
        nxt = {3: "M", 6: "U", 9: "Z", 12: "H"}[day.month]; yr = (day.year + (1 if day.month == 12 else 0)) % 10
        out.append(f"- Roll week: by Thursday move Symbol Mapping @MNQ (and @MES) to the {nxt}{yr} contract (e.g. MNQ{nxt}{yr}) after the close.")
    h = f"live/health/{d}.csv"
    if os.path.exists(h):
        rows = [l.strip().split(",") for l in open(h) if l.strip()]
        modes = {r[0] for r in rows}
        for r in rows:
            kv = dict(x.split("=", 1) for x in r[2:] if "=" in x)
            if kv.get("mc_processes", "1") == "0": out.append(f"- **VPS ({r[0]} {r[1]}): MultiCharts not running.**")
            if float(kv.get("disk_free_gb", "99")) < 5: out.append(f"- VPS ({r[0]}): only {kv['disk_free_gb']} GB free on C:.")
            if kv.get("push_errors", "0") not in ("0", ""): out.append(f"- VPS: {kv['push_errors']} lines in push_errors.txt.")
            if kv.get("rejected_today", "0") not in ("0", ""):
                m = kv.get("last_reject", ""); hint = " Looks like Symbol Mapping (order sent as @MNQ): fix it in File > Broker Profiles > Symbol Mapping." if ("@MNQ" in m or "@MES" in m or "Invalid" in m) else ""
                # the VPS count is a text match over MultiCharts' logs: trust it only if the last line is from today AND
                # reads like an order rejection (10/21: 'Influence PercentChange not found' from 10/20 was counted)
                ld = re.search(r"(\d{2})\.(\d{2})\.(\d{4})/", m)
                stale = ld is not None and dt.date(int(ld.group(3)), int(ld.group(2)), int(ld.group(1))) != day
                orderish = re.search(r"reject|invalid", m, re.I) is not None
                if stale or not orderish:
                    out.append(f"- Log lines matched as rejections ({r[0]}): {kv['rejected_today']}, but the last one "
                               f"{'is from an earlier day' if stale else 'is not an order rejection'} (`{m[:90]}`): "
                               "probably noise; confirm in the Order and Position Tracker if unsure.")
                else:
                    out.append(f"- **REJECTED ORDERS ({r[0]}): {kv['rejected_today']} rejection lines in MultiCharts' logs today**, last: `{m}`.{hint}")
        if day.weekday() < 5 and "open" not in modes: out.append("- VPS morning check (08:15) did not report today.")
    elif day.weekday() < 5:
        out.append("- No VPS health line today (the updated push script installs itself at its next 16:10 run).")
    if day == (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=5)).date():   # account tools: thin cushion, events
        try:
            import account_tools; out += account_tools.alerts()
        except Exception as e:
            out.append(f"- account tools not run: {e}")
    al = f"live/health/{d}_alerts.txt"
    if os.path.exists(al):
        for l in open(al):
            if l.strip(): out.append(f"- Watchdog log (delivery status is in the entry): {l.strip()}")
    return out


def block(day):
    o = check(day)
    return ["", "### Health (auto)", ""] + (o if o else ["- All clear: positions match the broker, heartbeats regular, VPS OK."])


if __name__ == "__main__":
    day = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=5)).date()
    print("\n".join(block(day)))
