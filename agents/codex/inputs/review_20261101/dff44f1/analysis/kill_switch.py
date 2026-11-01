"""Remote kill switch (2026-11-01, user approved; live/vps/KILL_SWITCH.md). Claude runs this when the user writes KILL or
RESUME. It adds / removes live/KILL on the work branches; the VPS relay (claude_alert_relay.ps1, every minute) then creates /
deletes C:\\TradingLogs\\KILL and sends an ntfy alert. Strategies react on their next bar (no new entries, open positions out).
  python3 analysis/kill_switch.py kill "reason"
  python3 analysis/kill_switch.py resume
  python3 analysis/kill_switch.py status
"""
import os, sys, subprocess, datetime as dt
from zoneinfo import ZoneInfo

BRANCHES = ["claude/nq-trading-strategy-params-5h9d20", "claude/quirky-noether-4dla64"]
FLAG = "live/KILL"


def run(*a):
    return subprocess.run(a, capture_output=True, text=True)


def push(msg):
    run("git", "commit", "-q", "-m", msg)
    head = run("git", "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    for b in BRANCHES + ([head] if head not in BRANCHES else []):
        r = run("git", "push", "-q", "origin", f"HEAD:{b}")
        if r.returncode: print("push failed", b, r.stderr.strip())


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    run("git", "pull", "-q", "--no-rebase", "origin", BRANCHES[0])
    if cmd == "kill":
        why = " ".join(sys.argv[2:]) or "user asked"
        open(FLAG, "w").write(f"{dt.datetime.now(ZoneInfo('America/Chicago')):%Y-%m-%d %H:%M} CT {why}\n")
        run("git", "add", FLAG); push(f"KILL switch ON: {why[:60]}")
        print("KILL sent: the VPS relay applies it within ~1-2 minutes; strategies exit on their next bar.")
    elif cmd == "resume":
        if os.path.exists(FLAG): run("git", "rm", "-q", FLAG); push("KILL switch OFF (resume)")
        print("RESUME sent: the VPS relay removes the flag within ~1-2 minutes (only a remotely made kill).")
    else:
        print("KILL is ON:", open(FLAG).read().strip() if os.path.exists(FLAG) else "OFF")
