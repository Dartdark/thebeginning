"""Manual-override log (2026-11-01, user): every time the user skips, closes early, resizes or pauses a live trade by hand,
one row in live/overrides.csv, so the Friday review can tell whether the overrides help or hurt. Claude adds the row when the
user says it in chat ("I turned VB off today", "closed ONB early at 21,340"); the result columns are filled once known
(the strategy's own outcome from the other account / the backtest list vs what actually happened).
  python3 analysis/override_log.py add DATE ACCOUNT STRATEGY ACTION "why" [actual_pnl] [strategy_pnl]
      ACTION: skip (chart off / no entry) | early_exit | resize | pause (kill switch / AA off) | other
  python3 analysis/override_log.py fill ROW actual_pnl strategy_pnl     (fill the result of row ROW, 1-based)
  python3 analysis/override_log.py summary                              (for the Friday review)
"""
import csv, os, sys

F = "live/overrides.csv"
COLS = ["date", "account", "strategy", "action", "why", "actual_pnl", "strategy_pnl"]
ACTIONS = {"skip", "early_exit", "resize", "pause", "other"}


def rows():
    return list(csv.DictReader(open(F))) if os.path.exists(F) else []


def save(R):
    with open(F, "w", newline="") as f:
        w = csv.DictWriter(f, COLS); w.writeheader(); w.writerows(R)


def summary(R=None):
    R = R if R is not None else rows()
    done = [r for r in R if r["actual_pnl"] not in ("", None) and r["strategy_pnl"] not in ("", None)]
    if not R: return "Overrides: none logged."
    diff = sum(float(r["actual_pnl"]) - float(r["strategy_pnl"]) for r in done)
    by = {}
    for r in done: by.setdefault(r["action"], []).append(float(r["actual_pnl"]) - float(r["strategy_pnl"]))
    parts = ", ".join(f"{a} {len(v)} ({'+' if sum(v) >= 0 else '-'}${abs(sum(v)):,.0f})" for a, v in sorted(by.items()))
    return (f"Overrides: {len(R)} logged, {len(done)} with results; overriding {'made' if diff >= 0 else 'cost'} "
            f"${abs(diff):,.0f} vs letting the strategy run" + (f" [{parts}]" if parts else "")
            + (f"; {len(R) - len(done)} waiting for results" if len(R) > len(done) else ""))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    R = rows()
    if cmd == "add":
        d, acct, strat, action, why = sys.argv[2:7]
        assert action in ACTIONS, f"action must be one of {sorted(ACTIONS)}"
        R.append(dict(date=d, account=acct, strategy=strat, action=action, why=why,
                      actual_pnl=sys.argv[7] if len(sys.argv) > 7 else "", strategy_pnl=sys.argv[8] if len(sys.argv) > 8 else ""))
        save(R); print(f"logged row {len(R)}")
    elif cmd == "fill":
        i = int(sys.argv[2]) - 1; R[i]["actual_pnl"], R[i]["strategy_pnl"] = sys.argv[3], sys.argv[4]; save(R); print("filled", i + 1)
    print(summary(R))
