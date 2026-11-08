"""Pre-push check (2026-11-01, harness rule: 'instructions become infrastructure'). Run before every push; exit 1 = don't push.
Checks the rules CLAUDE.md states in words:
  1. up to date: the work branch on origin has no commits missing locally (pull first);
  2. no model IDs in the commits being pushed (messages and added lines);
  3. after pushing: the three branches (work, quirky-noether, the session's designated branch) point at the same commit.
  python3 tools/prepush_check.py [designated-branch]        (before push)
  python3 tools/prepush_check.py --after [designated-branch] (after push: branch sync)
Install as a git hook in a clone (optional): printf '#!/bin/sh\npython3 tools/prepush_check.py\n' > .git/hooks/pre-push && chmod +x .git/hooks/pre-push
"""
import re, subprocess, sys

WORK, MIRROR = "claude/nq-trading-strategy-params-5h9d20", "claude/quirky-noether-4dla64"
MODEL_ID = re.compile(r"\bclaude-(opus|sonnet|haiku|fable)-\d|\b(opus|sonnet|haiku|fable)[ -]?\d+(\.\d+)?\b", re.I)
ALLOWED = ("Co-Authored-By: Claude",)          # the commit attribution trailer is required by the session rules


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, errors="replace").stdout.strip()


def before(branches):
    bad = []
    git("fetch", "-q", "origin", WORK)
    behind = git("rev-list", "--count", f"HEAD..origin/{WORK}")
    if behind and behind != "0": bad.append(f"{behind} commit(s) on origin/{WORK} not pulled: git pull --no-rebase origin {WORK}")
    rng = f"origin/{WORK}..HEAD"
    for line in git("log", "--format=%h %B", rng).splitlines():
        if MODEL_ID.search(line) and not line.strip().startswith(ALLOWED): bad.append(f"model ID in commit message: {line[:100]}")
    for line in git("diff", rng, "--unified=0", "--", ".", ":!data", ":!papers", ":!mc_reports", ":!scratch_data").splitlines():
        if line.startswith("+") and not line.startswith("+++") and MODEL_ID.search(line) and "prepush_check" not in line:
            bad.append(f"model ID in an added line: {line[:100]}")
    return bad


def after(branches):
    for b in branches: git("fetch", "-q", "origin", b)
    heads = {b: git("rev-parse", f"origin/{b}") for b in branches}
    return [] if len(set(heads.values())) == 1 else [f"branches differ: " + ", ".join(f"{b} {h[:7]}" for b, h in heads.items())]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--after"]
    branches = [WORK, MIRROR] + args
    bad = after(branches) if "--after" in sys.argv else before(branches)
    print("\n".join("PREPUSH: " + b for b in bad) if bad else "PREPUSH: OK")
    sys.exit(1 if bad else 0)
