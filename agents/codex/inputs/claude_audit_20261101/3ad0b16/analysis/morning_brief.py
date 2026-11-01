"""Morning brief (user 2026-11-01): one message a day, max 15 lines, of everything that ran since the last brief (default 24 h):
lab studies (with their receipts), the paper scout, Code reviewer and Codex commits, and what is waiting for the user.
Pure code, no model: reads lab/ledger.json, lab/IDEAS.md (via lab_tools), papers/SCOUT_LOG.md and git history.
  python3 analysis/morning_brief.py [hours]          print the brief
  python3 analysis/morning_brief.py [hours] --send   also send the headline line through analysis/send_alert.py (ntfy)
"""
import sys, json, re, subprocess, datetime as dt
from zoneinfo import ZoneInfo
sys.path.insert(0, "analysis")
import lab_tools as L

CT = ZoneInfo("America/Chicago")


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, errors="replace").stdout.strip()


def brief(hours=24):
    now = dt.datetime.now(CT); since = now - dt.timedelta(hours=hours); lines = []
    # lab
    rows = [r for r in L.ledger() if dt.datetime.fromisoformat(r.get("date", "1970-01-01T00:00")).replace(tzinfo=r.get("date") and
            dt.datetime.fromisoformat(r["date"]).tzinfo or CT) >= since]
    adv = [r for r in rows if r.get("stage", 0) >= 4]
    fails = [f"{r['id']} {r.get('market', '')} ({r.get('gate', '') or r.get('verdict')})" for r in rows if r.get("verdict") == "FAIL"]
    lines.append(f"LAB: {len(rows)} studies, {len(adv)} reached the Apex benches" + (f"; failed: {'; '.join(fails)[:170]}" if fails else ""))
    for r in adv:
        lines.append(f"  ** {r['id']} {r.get('title', '')}: stage {r['stage']} {r['verdict']}, t {r.get('t_design')} / {r.get('t_holdout')}; "
                     f"not verified: {', '.join(r.get('not_verified', []))[:80]}")
    s = L.summary(); lines.append(f"  queue: {s['queued']} queued, next {s['next'] or 'none'}; holdout looks this quarter {s['looks_quarter']}/{s['looks_budget']}")
    # scout
    scout = [l for l in open("papers/SCOUT_LOG.md", encoding="utf-8") if l.startswith("| 20")]
    new = [l for l in scout if l[2:12] >= since.date().isoformat() and l[2:12] <= now.date().isoformat()]
    old_rev = git("rev-list", "-1", f"--before={since.strftime('%Y-%m-%d %H:%M')}", "HEAD")
    old = set(re.findall(r"^## (Q\d+) ", git("show", f"{old_rev}:lab/IDEAS.md") if old_rev else "", re.M))
    ids = sorted({i["id"] for i in L.ideas()} - old); added = len(ids)
    lines.append(f"SCOUT: {len(new)} log lines; new ideas in the queue: {added}" + (f" ({', '.join(ids)})" if ids else ""))
    # reviewers
    since_s = since.strftime("%Y-%m-%d %H:%M")
    rev = git("log", f"--since={since_s}", "--format=%s", "--", "agents/cross_review/CODE_REVIEW_LOG.md").splitlines()
    lines.append(f"CODE REVIEW: {len(rev)} update(s)" + (f": {rev[0][:120]}" if rev else ""))
    git("fetch", "-q", "origin", "codex/work")
    cx = git("log", f"--since={since_s}", "--format=%s", "origin/codex/work").splitlines()
    lines.append(f"CODEX: {len(cx)} commit(s)" + (f", latest: {cx[0][:110]}" if cx else ""))
    # chain-broken backstop (2026-11-01): a scheduled job that silently stopped shows up here
    broken = []
    lab_any = [r for r in L.ledger() if r.get("date", "")[:10] >= since.date().isoformat()]
    if not lab_any and not __import__("os").path.exists(L.STOP) and s["queued"]: broken.append("LAB ran no study (5 runs a day expected)")
    if not new: broken.append("SCOUT logged nothing (5 runs a day expected)")
    if broken: lines.insert(0, "CHAIN BROKEN: " + "; ".join(broken))
    # buy gate (2026-11-01): PAUSE / PLAN ONLY / GO for buying new evaluations
    import buy_gate as BG
    v, why, n, e = BG.gate(); lines.insert(0 if v == "PAUSE" else len(lines), f"BUY GATE: {v}: {'; '.join(why)[:150]}")
    # waiting for the user
    wait = [f"lab idea {x}" for x in s.get("needs_user", [])] + [f"{r['id']} reached stage {r['stage']}: your call" for r in adv]
    todo = [l.strip()[6:90] for l in open("TODO.md", encoding="utf-8") if l.strip().startswith("- [ ] You")][:3]
    lines.append("WAITING ON YOU: " + ("; ".join(wait) if wait else "nothing new"))
    for t in todo: lines.append(f"  todo: {t}")
    head = (f"Morning brief {now:%m/%d}: lab {len(rows)} studies, {len(adv)} to benches; scout +{added} ideas; "
            f"{'action needed' if wait or v == 'PAUSE' else 'nothing waiting on you'}" + (" | CHAIN BROKEN" if broken else ""))
    return head, lines[:14]


if __name__ == "__main__":
    hrs = next((float(a) for a in sys.argv[1:] if a.replace(".", "").isdigit()), 24)
    head, lines = brief(hrs)
    print(head); print("\n".join(lines))
    if "--send" in sys.argv:
        subprocess.run([sys.executable, "analysis/send_alert.py", head[:199]])
