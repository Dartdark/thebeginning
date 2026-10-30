"""Four account tools for the 'Apex Live Desk' dashboard (2026-10-29, user: 'build all four').
Run after analysis/dashboard_data.py (needs accounts.json, trades.json and bt_cache.json in analysis/outputs/dashboard/).
Writes cushion.json, calendar.json, slippage.json, pass_odds.json there.

1. cushion    Room above the trailing floor vs the largest single-trade loss the set can take (VB stop 75 pts x size, or a
              risk-sized strategy's risk). THIN = room below one full stop: one losing trade can end the account.
2. calendar   The next 35 days' events that need action: EOS days (third Fridays), CME half-days, the MNQ roll (12/10),
              each evaluation's time limit.
3. slippage   Bracket exits from the logger vs their exact level: Vault Break targets (+40 pts, limit) and stops (-75 pts,
              stop-market). Ticks worse than the level; the backtest assumes 1 tick on stops, 0 on targets.
4. pass_odds  Chance each evaluation reaches its target before its floor in the days it has left: 5,000 paths of 5-day
              blocks of the backtest's daily P&L (evaluation set at the account's size, 2023+), EOD trailing floor (locks
              at start + $100), Apex daily loss limit not modelled. A guide, not a promise.
  python3 analysis/account_tools.py
"""
import os, json, datetime as dt
import numpy as np, pandas as pd

OUT = "analysis/outputs/dashboard"
# evaluation rules per live account (keep in step with dashboard_data.ACCOUNTS / live_panels.ACCTS)
EVALS = {"#2": dict(mult=1.0, target=53000.0, trail=2000.0, start_bal=50000.0, deadline=None,
                    max_loss={"Vault Break (8 MNQ, 75 pts)": 1200.0, "Overnight Bias (risk)": 1100.0})}   # #3 blown 2026-10-30
HALF_DAYS = {"2026-11-26": "Thanksgiving: CME closed for equities RTH", "2026-11-27": "Day after Thanksgiving: early close 12:15 CT",
             "2026-12-24": "Christmas Eve: early close 12:15 CT", "2026-12-25": "Christmas: closed",
             "2027-01-01": "New Year: closed", "2027-01-18": "MLK Day: early close", "2027-02-15": "Presidents' Day: early close"}
ROLL = {"2026-12-10": "MNQ roll: Symbol Mapping MNQZ6 -> MNQH7 after the close (all @MNQ lines)"}


def today():
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=5)).date()


def cushion(accts):
    out = []
    for a in accts:
        e = EVALS.get(a["account"])
        if not e or a["room"] is None: continue
        worst = max(e["max_loss"].values()); which = max(e["max_loss"], key=e["max_loss"].get)
        out.append(dict(account=a["account"], balance=a["est_balance"], floor=a["floor"], room=a["room"], worst_trade=worst,
                        worst_strategy=which, stops_left=round(a["room"] / worst, 2),
                        status="THIN - one full stop ends it" if a["room"] < worst else ("WATCH" if a["room"] < 1.5 * worst else "OK")))
    return out


def calendar(t0):
    ev = []
    for i in range(0, 36):
        d = t0 + dt.timedelta(days=i); s = str(d)
        if d.weekday() == 4 and 15 <= d.day <= 21:
            ev.append(dict(date=s, event="EOS day: short at the 8:30 open, out by 10:00 (EOS charts on, auto-trading green)"))
        if s in HALF_DAYS: ev.append(dict(date=s, event=HALF_DAYS[s] + "; strategies use their early-close times"))
        if s in ROLL: ev.append(dict(date=s, event=ROLL[s]))
        for k, e in EVALS.items():
            if e["deadline"] == s: ev.append(dict(date=s, event=f"Account {k}: evaluation time limit (last day to reach the target)"))
    for x in ev: x["days_away"] = (dt.date.fromisoformat(x["date"]) - t0).days; x["key"] = x["date"] + " " + x["event"][:20]
    return ev


def slippage(trades):
    rows = []
    for t in trades:
        if not t["strategy"].startswith("Vault Break"): continue
        pts = (t["exit"] - t["entry"]) * (1 if t["side"] == "long" else -1)
        if abs(pts - 40) <= 3: kind, ticks = "target", (40 - pts) / 0.25
        elif abs(pts + 75) <= 6: kind, ticks = "stop", (-75 - pts) / 0.25
        else: continue
        rows.append(dict(kind=kind, ticks=ticks, account=t["account"]))
    out = []
    for kind, assumed in (("target", 0), ("stop", 1)):
        r = [x["ticks"] for x in rows if x["kind"] == kind]
        if r:
            out.append(dict(exit_type=f"Vault Break {kind}", fills=len(r), avg_ticks_worse=round(float(np.mean(r)), 2),
                            worst_ticks=round(float(max(r)), 2), backtest_assumes=assumed,
                            status="WORSE than backtest" if np.mean(r) > assumed + 0.5 else "OK"))
    return out


def pass_odds(accts, t0, n=5000, block=5, seed=1):
    C = json.load(open(f"{OUT}/bt_cache.json")); daily = np.array(list(C["daily"].values()))
    rng = np.random.default_rng(seed); out = []
    for a in accts:
        e = EVALS.get(a["account"])
        if not e or a["est_balance"] is None: continue
        if e["deadline"]: days = int(np.busday_count(str(t0 + dt.timedelta(days=1)), str(dt.date.fromisoformat(e["deadline"]) + dt.timedelta(days=1))))
        else: days = 60
        hits = blown = 0
        for _ in range(n):
            bal, floor, peak = a["est_balance"], a["floor"], a["est_balance"]
            path = np.concatenate([daily[s:s + block] for s in rng.integers(0, len(daily) - block, days // block + 1)])[:days] * e["mult"]
            for x in path:
                bal += x
                if bal >= e["target"]: hits += 1; break
                if bal <= floor: blown += 1; break
                if bal > peak: peak = bal; floor = min(max(floor, peak - e["trail"]), e["start_bal"] + 100)
        out.append(dict(account=a["account"], balance=a["est_balance"], target=e["target"], floor=a["floor"], days_left=days,
                        pass_pct=round(hits / n * 100, 1), blow_pct=round(blown / n * 100, 1),
                        open_pct=round((n - hits - blown) / n * 100, 1)))
    return out


def alerts():
    """Bold lines for the 16:40 journal / push: thin cushion, an event tomorrow."""
    o = []
    for c in json.load(open(f"{OUT}/cushion.json")) if os.path.exists(f"{OUT}/cushion.json") else []:
        if c["status"].startswith("THIN"):
            o.append(f"- **CUSHION {c['account']}**: ${c['room']:,.0f} above the floor, less than one full stop (${c['worst_trade']:,.0f}, {c['worst_strategy']}).")
    for e in json.load(open(f"{OUT}/calendar.json")) if os.path.exists(f"{OUT}/calendar.json") else []:
        if e["days_away"] in (0, 1): o.append(f"- **CALENDAR {e['date']}**: {e['event']}")
    return o


def main():
    accts = json.load(open(f"{OUT}/accounts.json")); trades = json.load(open(f"{OUT}/trades.json")); t0 = today()
    for name, data in (("cushion", cushion(accts)), ("calendar", calendar(t0)), ("slippage", slippage(trades)),
                       ("pass_odds", pass_odds(accts, t0))):
        json.dump(data, open(f"{OUT}/{name}.json", "w"), indent=1)
        for x in data: print(name, x)


if __name__ == "__main__":
    main()
