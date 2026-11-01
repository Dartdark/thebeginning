"""Buy gate (2026-11-01, user: 'make the gate a hard rule in code'). Before buying a new evaluation, the buying plan asks this.
Reads the dashboard data (analysis/dashboard_data.py writes it after each close):
  PAUSE      any strategy's drift alarm is on (live_vs_bt.json drift ALARM), or a live account's P&L is below the 5th
             percentile of its backtest range (montecarlo.json status LOW), or 2+ accounts failed within 10 trading days
             (a shared failure: the accounts are one bet, not many), for 7 days after the second failure (cool-off).
  PLAN ONLY  fewer than 40 live trades across the plan strategies: buy per the Nov-Dec budget plan (1 a day, 3-4 per
             payday), don't accelerate. Evidence too thin to scale beyond it.
  GO         40+ live trades, overall live edge >= 75% of the backtest, no alarm: scaling beyond the plan is allowed
             (the old 'mid-December gate', FUNDED_PLAN.md).
  python3 analysis/buy_gate.py            prints the verdict and reasons (exit 1 on PAUSE)
"""
import json, sys, datetime as dt

D = "analysis/outputs/dashboard/"
MIN_TRADES, MIN_EDGE, FAIL_WINDOW, COOL_OFF = 40, 0.75, 14, 7   # calendar days (14 ~ 10 trading days)


def load(name):
    try: return json.load(open(D + name))
    except Exception: return []


def gate():
    lv, mc, ac = load("live_vs_bt.json"), load("montecarlo.json"), load("accounts.json")
    why_pause = [f"drift ALARM on {r['strategy']}" for r in lv if str(r.get("drift", "")).upper().startswith("ALARM")]
    why_pause += [f"account {r['account']} below its backtest range (percentile {r.get('percentile')})" for r in mc
                  if str(r.get("status", "")).upper().startswith("LOW")]
    setup = json.load(open("live/expected_setup.json"))["accounts"]          # failure dates: 'closed YYYY-MM-DD'
    blown = sorted(dt.date.fromisoformat(v["status"].split()[-1]) for v in setup.values() if str(v.get("status", "")).startswith("closed"))
    for a, b in zip(blown, blown[1:]):
        until = b + dt.timedelta(days=COOL_OFF)
        if (b - a).days <= FAIL_WINDOW and dt.date.today() <= until:
            why_pause.append(f"2 accounts failed {(b - a).days} days apart ({a}, {b}): shared failure, cool-off until {until}"); break
    trades = sum(int(r.get("live_trades") or 0) for r in lv)
    pts = [(r["live_pts"], r["bt_pts"], int(r.get("live_trades") or 0)) for r in lv if r.get("live_pts") is not None and r.get("bt_pts")]
    live = sum(l * n for l, b, n in pts); bt = sum(b * n for l, b, n in pts)
    edge = live / bt if bt > 0 else None
    if why_pause: return "PAUSE", why_pause, trades, edge
    if trades < MIN_TRADES: return "PLAN ONLY", [f"{trades} live trades < {MIN_TRADES}: evidence too thin to scale past the plan"], trades, edge
    if edge is None: return "PLAN ONLY", ["live edge UNKNOWN (no backtest reference): insufficient evidence"], trades, edge   # Codex 2026-11-01 #6
    if edge < MIN_EDGE: return "PLAN ONLY", [f"live edge {edge:.0%} of backtest < {MIN_EDGE:.0%} (trade-weighted points, not dollars)"], trades, edge
    return "GO", [f"{trades} live trades, live edge {edge:.0%} of backtest, no alarm"], trades, edge


if __name__ == "__main__":
    v, why, n, e = gate()
    print(f"BUY GATE: {v} ({n} live trades" + (f", live edge {e:.0%} of backtest" if e is not None else "") + ")")
    for w in why: print("  - " + w)
    sys.exit(1 if v == "PAUSE" else 0)
