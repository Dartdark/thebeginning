"""Four account tools for the 'Apex Live Desk' dashboard (2026-10-29, user: 'build all four').
Run after analysis/dashboard_data.py (needs accounts.json, trades.json and bt_cache.json in analysis/outputs/dashboard/).
Writes cushion.json, calendar.json, slippage.json, pass_odds.json there.

1. cushion    Room above the trailing floor vs the largest single-trade loss the set can take (VB stop 75 pts x size, or a
              risk-sized strategy's risk). THIN = room below one full stop: one losing trade can end the account.
2. calendar   The next 35 days' events that need action: EOS days (third Fridays), CME half-days, the MNQ roll (12/10),
              each evaluation's time limit.
3. slippage   Bracket exits from the logger vs their exact level: Vault Break targets (+40 pts, limit) and stops (-75 pts,
              stop-market). Ticks worse than the level; the backtest assumes 1 tick on stops, 0 on targets.
5. payouts    Funded accounts (FUNDED below): Apex payout readiness from the Chart Monitor's end-of-day equity: qualifying
              days (profit >= $350 150K / $250 50K) since the last payout, the consistency rule (best day < 50% of the profit
              since), and the balance needed (safety level + the next payout's cap). Alert when a payout can be requested.
4. pass_odds  Chance each evaluation reaches its target before its floor in the days it has left: 5,000 paths of 5-day
              blocks of the backtest's daily P&L (evaluation set at the account's size, 2023+), EOD trailing floor (locks
              at start + $100), Apex daily loss limit not modelled. A guide, not a promise.
  python3 analysis/account_tools.py
"""
import os, glob, json, datetime as dt
import numpy as np, pandas as pd

OUT = "analysis/outputs/dashboard"
# evaluation rules per live account (keep in step with dashboard_data.ACCOUNTS / live_panels.ACCTS)
EVALS = {"#5": dict(mult=2.5, target=159000.0, trail=4000.0, start_bal=150000.0, deadline=None,
                    max_loss={"Overnight Bias (risk)": None})}   # VB removed 2026-11-11   # #2-#4 removed 2026-11-10
# 2026-11-13 (alerts review: the journal still said $2,750 after ONB went to $3,500): a None stop is read from
# live/expected_setup.json accounts.<name>.max_stop, the same number the VPS watchdog uses (one source of truth)
try:
    _acc = json.load(open("live/expected_setup.json"))["accounts"]
    for _n, _e in EVALS.items():
        for _k, _v in _e["max_loss"].items():
            if _v is None: _e["max_loss"][_k] = float(_acc.get(_n, {}).get("max_stop") or 0) or 3500.0
except Exception:
    for _e in EVALS.values():
        for _k, _v in _e["max_loss"].items(): _e["max_loss"][_k] = _v or 3500.0
# funded accounts (2026-10-30): add each one when it passes; payouts = [(date, amount)] as requested from Apex
FUNDED = {}   # e.g. "#4": dict(id="APEX-xxxxxx-04", size="150K", funded="2026-12-02", payouts=[])
PAYOUT_RULES = {"150K": dict(start=150_000.0, safe=154_100.0, qday=350.0, caps=[2500.0, 3000.0, 3000.0, 3000.0, 4000.0, 5000.0]),
                "50K": dict(start=50_000.0, safe=52_100.0, qday=250.0, caps=[1500.0, 1500.0, 2000.0, 2500.0, 2500.0, 3000.0])}
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


def payout_status(eod, rules, funded, payouts):
    """eod: {YYYYMMDD: end-of-day equity} since funding; payouts: [(YYYY-MM-DD, amount)]. Returns the readiness dict."""
    paid = {d.replace("-", ""): a for d, a in payouts}; n = len(payouts)
    last = max(paid) if paid else funded.replace("-", "")
    days = sorted(eod); prev = rules["start"]; pnl = []
    for d in days:
        p = eod[d] - prev + paid.get(d, 0.0); prev = eod[d]
        if d > last: pnl.append(p)
    bal = eod[days[-1]] if days else rules["start"]
    since = sum(pnl); best = max(pnl) if pnl else 0.0; qual = sum(x >= rules["qday"] for x in pnl)
    if n >= 6: return dict(payouts_done=n, status="DONE: all 6 payouts taken (account closes)")
    cap = rules["caps"][n]; need = rules["safe"] + cap
    ok = dict(balance=bal >= need, days=qual >= 5, profit=since > 0, consistency=since > 0 and best < 0.5 * since)
    return dict(payouts_done=n, next_cap=cap, balance=round(bal, 2), balance_needed=need, short_by=round(max(0.0, need - bal), 2),
                qualifying_days=int(qual), profit_since=round(since, 2), best_day=round(best, 2),
                best_day_pct=round(best / since * 100, 1) if since > 0 else None,
                ready=all(ok.values()), missing=[k for k, v in ok.items() if not v])


def payouts():
    out = []
    for name, a in FUNDED.items():
        eod = {}
        for f in sorted(glob.glob("live/trades/2*.csv")):
            d = os.path.basename(f)[:8]
            if d < a["funded"].replace("-", ""): continue
            eq = [float(r[6]) for r in (l.split(",") for l in open(f) if l.startswith("ACCT,")) if len(r) > 6 and r[3] == a["id"] and r[6]]
            eq = [e for e in eq if e > 0]
            if eq: eod[d] = eq[-1]
        out.append(dict(account=name, id=a["id"], size=a["size"], **payout_status(eod, PAYOUT_RULES[a["size"]], a["funded"], a["payouts"])))
    return out


def alerts():
    """Bold lines for the 16:40 journal / push: thin cushion, an event tomorrow."""
    o = []
    for c in json.load(open(f"{OUT}/cushion.json")) if os.path.exists(f"{OUT}/cushion.json") else []:
        if c["status"].startswith("THIN"):
            o.append(f"- **CUSHION {c['account']}**: ${c['room']:,.0f} above the floor, less than one full stop (${c['worst_trade']:,.0f}, {c['worst_strategy']}).")
    for p in json.load(open(f"{OUT}/payouts.json")) if os.path.exists(f"{OUT}/payouts.json") else []:
        if p.get("ready"):
            o.append(f"- **PAYOUT {p['account']}**: can request ${p['next_cap']:,.0f} now (balance ${p['balance']:,.0f}, {p['qualifying_days']} qualifying days, best day {p['best_day_pct']}% of the profit). Request it in the Apex dashboard, then tell Claude.")
    for e in json.load(open(f"{OUT}/calendar.json")) if os.path.exists(f"{OUT}/calendar.json") else []:
        if e["days_away"] in (0, 1): o.append(f"- **CALENDAR {e['date']}**: {e['event']}")
    return o


def main():
    accts = json.load(open(f"{OUT}/accounts.json")); trades = json.load(open(f"{OUT}/trades.json")); t0 = today()
    for name, data in (("cushion", cushion(accts)), ("calendar", calendar(t0)), ("slippage", slippage(trades)),
                       ("pass_odds", pass_odds(accts, t0)), ("payouts", payouts())):
        json.dump(data, open(f"{OUT}/{name}.json", "w"), indent=1)
        for x in data: print(name, x)


if __name__ == "__main__":
    main()
