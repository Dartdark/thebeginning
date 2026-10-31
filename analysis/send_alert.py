"""Send an alert to the user's phone through the VPS's ntfy relay (2026-10-29, user: 'build the relay'; Claude's own push
notifications didn't reach the phone, ntfy from the VPS does). Appends one line to live/claude_alerts.txt and pushes it to
the work branches; the VPS task 'ClaudeAlertRelay' (live/vps/claude_alert_relay.ps1, every minute) forwards each new line
to ntfy, usually within 1-2 minutes.
  python3 analysis/send_alert.py "Pre-market: ONB-2 auto-trading OFF, turn it on (Flat)"
"""
import sys, subprocess, datetime as dt

BRANCHES = ["claude/nq-trading-strategy-params-5h9d20", "claude/quirky-noether-4dla64"]


def send(text):
    text = " ".join(text.split())[:300]
    now = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")
    run = lambda *a: subprocess.run(a, check=False, capture_output=True, text=True)
    run("git", "pull", "-q", "--no-rebase", "origin", BRANCHES[0])
    with open("live/claude_alerts.txt", "a") as f: f.write(f"{now} CT | {text}\n")
    run("git", "add", "live/claude_alerts.txt")
    run("git", "commit", "-q", "-m", f"alert: {text[:60]}")
    head = run("git", "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    for b in BRANCHES + ([head] if head not in BRANCHES else []):
        r = run("git", "push", "-q", "origin", f"HEAD:{b}")
        if r.returncode: print("push failed", b, r.stderr.strip())
    print("queued for the phone:", text)


if __name__ == "__main__":
    send(" ".join(sys.argv[1:]) or "test alert from Claude")
