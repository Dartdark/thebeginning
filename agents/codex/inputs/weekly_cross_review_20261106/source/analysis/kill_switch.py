"""Remote kill switch (2026-11-01, user approved; live/vps/KILL_SWITCH.md). Claude runs this when the user writes KILL or
RESUME. It adds / removes live/KILL on the work branches; the VPS relay (claude_alert_relay.ps1, every minute) then creates /
deletes C:\\TradingLogs\\KILL and sends an ntfy alert. Strategies react on their next bar (no new entries, open positions out).
  python3 analysis/kill_switch.py kill "reason"
  python3 analysis/kill_switch.py resume
  python3 analysis/kill_switch.py status    (repo flag + the VPS's own flag from the status feed)
"""
import json, os, sys, subprocess, datetime as dt
from zoneinfo import ZoneInfo

BRANCHES = ["claude/nq-trading-strategy-params-5h9d20", "claude/quirky-noether-4dla64"]
FLAG = "live/KILL"


def run(*a):
    return subprocess.run(a, capture_output=True, text=True)


def push(msg):
    """Commit + push to every branch; True only if the commit and EVERY push succeeded (Codex review 2026-11-01 #3)."""
    c = run("git", "commit", "-q", "-m", msg)
    if c.returncode: print("COMMIT FAILED:", (c.stderr or c.stdout).strip()); return False
    head = run("git", "rev-parse", "--abbrev-ref", "HEAD").stdout.strip(); ok = True
    for b in BRANCHES + ([head] if head and head not in BRANCHES else []):
        r = run("git", "push", "-q", "origin", f"HEAD:{b}")
        if r.returncode: print("PUSH FAILED", b, r.stderr.strip()); ok = False
    r = run("git", "ls-remote", "origin", f"refs/heads/{BRANCHES[0]}"); local = run("git", "rev-parse", "HEAD").stdout.strip()
    if not r.stdout.startswith(local): print("the work branch on GitHub is not at this commit"); ok = False
    return ok


def vps_flag():
    """The VPS's own report (status feed, every 5 min): (kill_flag, snapshot time) or None if unreadable."""
    if run("git", "fetch", "-q", "origin", "vps-status").returncode: return None
    r = run("git", "show", "FETCH_HEAD:status.json")
    if r.returncode: return None
    try: d = json.loads(r.stdout.lstrip("\ufeff")); return d.get("kill_flag"), d.get("time_local")
    except Exception: return None


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if run("git", "pull", "-q", "--no-rebase", "origin", BRANCHES[0]).returncode: print("warning: pull failed")
    if cmd == "kill":
        why = " ".join(sys.argv[2:]) or "user asked"
        open(FLAG, "w").write(f"{dt.datetime.now(ZoneInfo('America/Chicago')):%Y-%m-%d %H:%M} CT {why}\n")
        run("git", "add", FLAG)
        if push(f"KILL switch ON: {why[:60]}"):
            print("KILL PUSHED (not yet confirmed on the VPS): the relay applies it within ~1-2 min; check with `status`. FLATTEN by hand now if it is urgent.")
        else: print("KILL NOT SENT: flatten by hand now (live/vps/KILL_SWITCH.md)."); sys.exit(1)
    elif cmd == "resume":
        if not os.path.exists(FLAG): print("No remote kill on the branch: nothing to resume (a kill made on the VPS is resumed there with kill.ps1 -Resume).")
        else:
            run("git", "rm", "-q", FLAG)
            if push("KILL switch OFF (resume)"): print("RESUME PUSHED (not yet confirmed): the relay clears the REMOTE latch within ~1-2 min; a local kill stays on. Check with `status`.")
            else: print("RESUME NOT SENT."); sys.exit(1)
    else:
        print("repo:", "KILL ON: " + open(FLAG).read().strip() if os.path.exists(FLAG) else "no remote kill")
        v = vps_flag()
        print("VPS:", "unreadable (status feed down?)" if v is None else f"kill flag {'ON' if v[0] else 'OFF'} at {v[1]} (VPS time; the feed updates every 5 min)")
