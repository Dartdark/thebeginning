"""Send an alert to the user's phone through the VPS's ntfy relay (2026-10-29, user: 'build the relay'; Claude's own push
notifications didn't reach the phone, ntfy from the VPS does). Appends one line to live/claude_alerts.txt and pushes it to
the work branches; the VPS task 'ClaudeAlertRelay' (live/vps/claude_alert_relay.ps1, every minute) forwards each new line
to ntfy, usually within 1-2 minutes.
  python3 analysis/send_alert.py "Pre-market: ONB-2 auto-trading OFF, turn it on (Flat)"
"""
import sys, subprocess, datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT = Path(__file__).resolve().parents[1]

BRANCHES = ["claude/nq-trading-strategy-params-5h9d20", "claude/quirky-noether-4dla64"]


def send(text):
    text = " ".join(text.split())[:300]
    if not text:
        raise ValueError("An alert message is required")
    now = dt.datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %H:%M")
    def run(*args):
        return subprocess.run(args, check=True, capture_output=True, text=True, cwd=ROOT)
    head = run("git", "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if not head.startswith("claude/"):
        raise RuntimeError("Alert publisher must run on the designated Claude branch")
    if run("git", "diff", "--cached", "--name-only").stdout.strip():
        raise RuntimeError("Finish the staged commit before publishing an alert")
    run("git", "pull", "-q", "--no-rebase", "origin", BRANCHES[0])
    with (ROOT / "live/claude_alerts.txt").open("a", encoding="utf-8") as f:
        f.write(f"{now} CT | {text}\n")
    run("git", "add", "live/claude_alerts.txt")
    run("git", "commit", "-q", "-m", f"alert: {text[:60]}", "--only", "--", "live/claude_alerts.txt")
    for branch in BRANCHES + ([head] if head not in BRANCHES else []):
        run("git", "push", "-q", "origin", f"HEAD:{branch}")
    print("queued on GitHub for the phone relay (delivery not confirmed):", text)


if __name__ == "__main__":
    send(" ".join(sys.argv[1:]))
