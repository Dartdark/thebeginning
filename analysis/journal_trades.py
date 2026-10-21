"""Fill the day's journal note with the live trades logged on the VPS (Apex Trade Logger -> live/trades/YYYYMMDD.csv).
Writes / replaces the block between the auto-trades markers in journal/daily/YYYY-MM-DD.md (creates the note from the
template if it doesn't exist yet). Facts only: fills and MultiCharts' gross P&L; the user's own lines stay untouched.
  python3 analysis/journal_trades.py [YYYY-MM-DD]      (default: today, Central time)
"""
import sys, glob, os, datetime as dt
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

COLS = ["event", "tag", "symbol", "side", "contracts", "entry_date", "entry_time", "entry_price", "exit_date",
        "exit_time", "exit_price", "profit_usd", "bar_date", "bar_time"]
NAMES = {"VB": "Vault Break", "ONB": "ONB ADX30", "EOS": "EOS", "MON_BR": "Bridge Monday", "ONB_ML": "ONB ML",
         "MON": "Monday Long", "LDF": "Late-Day Flow", "NFP": "NFP Fade", "MOC_MES": "ES MOC", "CLS": "CL Sunday fade", "RS": "Relative Strength"}
START, END = "<!-- auto-trades:start -->", "<!-- auto-trades:end -->"


def name(tag):
    """VB -> Vault Break; VB-2 -> Vault Break (acct 2): tags may carry an account suffix."""
    base, _, acct = str(tag).partition("-")
    return NAMES.get(base, base) + (f" (acct {acct})" if acct else "")


def hhmm(x):
    x = int(x); return f"{x // 100:02d}:{x % 100:02d}"


def load(day):
    files = sorted(glob.glob("live/trades/*.csv"))
    lo = (day - dt.timedelta(days=4)).strftime("%Y%m%d"); hi = day.strftime("%Y%m%d")
    files = [f for f in files if lo <= os.path.basename(f)[:8] <= hi]
    if not files: return pd.DataFrame(columns=COLS)
    df = pd.concat([pd.read_csv(f, header=None, names=COLS, dtype=str) for f in files], ignore_index=True)
    return df.drop_duplicates()


def block(day, df):
    d = day.strftime("%Y%m%d")
    closed = df[(df.event == "CLOSE") & (df.bar_date == d)].copy()
    opens = df[(df.event == "OPEN") & (df.bar_date == d)]
    lines = [START, "## Trades (auto, from the VPS trade log; gross, before commissions)", ""]
    if closed.empty and opens.empty:
        lines += ["No trades logged today. (If a strategy should have traded, check its chart, auto-trading and the VPS.)"]
    else:
        lines += ["| Strategy | Side | Contracts | Entry (CT) | Exit (CT) | Points | P&L $ |", "|---|---|---|---|---|---|---|"]
        tot = 0.0
        for r in closed.itertuples():
            pts = (float(r.exit_price) - float(r.entry_price)) * (1 if r.side == "long" else -1)
            pnl = float(r.profit_usd); tot += pnl
            ed = "" if r.entry_date == d else f"{r.entry_date[4:6]}/{r.entry_date[6:]} "
            lines.append(f"| {name(r.tag)} | {r.side} | {r.contracts} | {ed}{hhmm(r.entry_time)} @ {r.entry_price} | "
                         f"{hhmm(r.exit_time)} @ {r.exit_price} | {pts:+.2f} | {pnl:+,.2f} |")
        lines += ["", f"**Day total (closed trades, gross): ${tot:+,.2f}**"]
        keys = set(zip(closed.tag, closed.entry_date, closed.entry_time))
        still = [r for r in opens.itertuples() if (r.tag, r.entry_date, r.entry_time) not in keys]
        if still:
            lines.append("")
            for r in still:
                late = int(r.bar_time) >= 1559 and dt.datetime.strptime(d, "%Y%m%d").weekday() < 5
                lines.append(f"- {'**CHECK: still open after 15:59 CT?** ' if late else 'Opened, not closed today: '}"
                             f"{name(r.tag)} {r.side} {r.contracts} @ {r.entry_price} ({hhmm(r.entry_time)} CT)")
    try:
        import vps_health; lines += vps_health.block(day)
    except Exception as e:                       # the health check must never block the journal
        lines += ["", f"### Health (auto)", "", f"- health check failed: {e}"]
    lines += ["", "Balance: the Apex end-of-day balance goes in the Accounts table below (the log has no account balance).", END]
    return "\n".join(lines)


def main():
    day = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else \
        (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=5)).date()          # Central (CDT); close enough for a date
    path = f"journal/daily/{day.isoformat()}.md"
    b = block(day, load(day))
    if os.path.exists(path):
        s = open(path).read()
        if START in s and END in s:
            s = s[:s.index(START)] + b + s[s.index(END) + len(END):]
        else:
            first, _, rest = s.partition("\n"); s = first + "\n\n" + b + "\n" + rest
    else:
        t = open("journal/templates/Daily.md").read()
        t = t.replace("{{date:YYYY-MM-DD}}", day.isoformat()).replace("{{date:dddd}}", day.strftime("%A"))
        first, _, rest = t.partition("\n"); s = first + "\n\n" + b + "\n" + rest
    open(path, "w").write(s)
    print(f"wrote {path}"); print(b)


if __name__ == "__main__":
    main()
