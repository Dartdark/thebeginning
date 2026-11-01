"""Lab helpers (2026-10-31, lab/README.md). The scheduled lab run calls these; they enforce the kill switch, the 5-a-day cap,
the sealed-look budget and the multiple-testing bar, and write the dashboard's Lab panel.
  python3 analysis/lab_tools.py can_run           -> 'OK' or the reason not to run (exit 1)
  python3 analysis/lab_tools.py next              -> the next queued idea ID (or nothing)
  python3 analysis/lab_tools.py bar               -> current t bar for a lab idea
  python3 analysis/lab_tools.py log '<json>'      -> append one study row (fields below) and rebuild the panel
  python3 analysis/lab_tools.py summary           -> rebuild analysis/outputs/dashboard/lab.json
  python3 analysis/lab_tools.py dupcheck 'w1 w2'  -> TIER_LIST rows ranked C / D / F containing every word (queue-time check)
Harness rules in code (2026-11-01, user: 'build all 4'):
  - an idea is only runnable with a '- tier_check:' line (who checked TIER_LIST, the words used, the result);
  - ERROR rows need error_class; 'missing_data' / 'too_few_events' are not retried, 'code_error' / 'timeout' once; an idea with
    2 ERROR rows is held for the user (needs_user in the panel);
  - every logged row carries a receipt: verified / not_verified / risks (lists; empty only when true).
Study row: id, title, market, stage (0-5 reached), verdict (PASS / FAIL / BLOCKED / ERROR), gate (the gate that failed, or ''),
t_design, t_holdout, looks (holdout openings in this study, 0 or 1), tier, lesson, follow_ups (list of IDs).
"""
import sys, os, re, json, datetime as dt
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
LEDGER, IDEAS, STOP = "lab/ledger.json", "lab/IDEAS.md", "lab/STOP"
CAP_DAY, LOOKS_QUARTER = 5, 40
OUT = "analysis/outputs/dashboard/lab.json"


def ledger():
    return json.load(open(LEDGER)) if os.path.exists(LEDGER) else []


def now():
    return dt.datetime.now(CT)


def runs_today(L=None, day=None):
    day = day or now().date().isoformat()
    # BLOCKED rows (skipped before any testing) do not count toward the cap (lab/README.md)
    return sum(1 for r in (L or ledger()) if r.get("date", "")[:10] == day and r.get("verdict") != "BLOCKED")


def looks_quarter(L=None, d=None):
    d = d or now().date(); q0 = dt.date(d.year, 3 * ((d.month - 1) // 3) + 1, 1).isoformat()
    return sum(int(r.get("looks", 0)) for r in (L or ledger()) if r.get("date", "")[:10] >= q0)


def ideas():
    out, cur = [], None
    for line in open(IDEAS, encoding="utf-8"):
        m = re.match(r"^## (Q\d+) · (\w+) · priority (\d)", line)
        if m: cur = dict(id=m.group(1), status=m.group(2), priority=int(m.group(3)), order=len(out), tier_check=False, who_pays="",
                         payer=""); out.append(cur)
        elif cur is not None and line.startswith("- tier_check:"): cur["tier_check"] = True
        elif cur is not None and line.startswith("- who_pays:"):
            w = line.split(":", 1)[1].strip().lower(); cur["who_pays"] = next((k for k in PAYERS if w.startswith(k)), "")
    return out


# 'Who is paying you, and why do they keep paying?' (user 2026-11-01, after Ruuj's quant roadmap): every idea names its
# source of return; 'no one I can name' is noise and is never queued.
PAYERS = ("risk premium", "behavioral", "structural", "information")


RETRY_ONCE, NO_RETRY = {"code_error", "timeout"}, {"missing_data", "too_few_events"}
ERROR_CLASSES = RETRY_ONCE | NO_RETRY | {"other"}


def held(i, L=None):
    """Why an idea may not run again ('' = free): no TIER_LIST check, a non-retryable error, or 2 errors (user decides)."""
    if not i["tier_check"]: return "no tier_check line (grep TIER_LIST first: lab_tools.py dupcheck)"
    if not i.get("who_pays"): return "no '- who_pays:' line naming risk premium / behavioral / structural / information (and who)"
    errs = [r for r in (L if L is not None else ledger()) if r.get("id") == i["id"] and r.get("verdict") == "ERROR"]
    if len(errs) >= 2: return "2 errors: held for the user"
    if errs and errs[-1].get("error_class") not in RETRY_ONCE: return f"error '{errs[-1].get('error_class')}' is not retried"
    return ""


def dupcheck(words):
    """TIER_LIST rows in tiers C / D / F that contain every word (case-insensitive)."""
    ws, tier, out = [w.lower() for w in words.split()], None, []
    for line in open("TIER_LIST.md", encoding="utf-8"):
        m = re.match(r"^## ([SABCDF]\+?)\s*$", line.strip())
        if m: tier = m.group(1); continue
        if tier in ("C", "D", "F") and line.startswith("| ") and all(w in line.lower() for w in ws):
            out.append(f"{tier}: {line[2:160].strip()}")
    return out


def next_idea():
    L = ledger(); q = [i for i in ideas() if i["status"] == "queued" and not held(i, L)]
    return min(q, key=lambda i: (i["priority"], i["order"]))["id"] if q else None


def can_run():
    if os.path.exists(STOP): return "STOPPED: lab/STOP exists (kill switch)."
    n = runs_today()
    if n >= CAP_DAY: return f"CAP: {n} studies already today (max {CAP_DAY})."
    if not next_idea():
        L = ledger(); h = [f"{i['id']} ({held(i, L)})" for i in ideas() if i["status"] == "queued" and held(i, L)]
        return "EMPTY: no runnable queued idea in lab/IDEAS.md." + (" Held: " + "; ".join(h) if h else "")
    return "OK"


def bar():
    """t bar for a lab idea: Bonferroni over TIER_LIST ranked items + lab studies so far (metrics.t_threshold)."""
    sys.path.insert(0, "analysis"); import metrics as M
    from trials import parse_tier_list
    n = len(parse_tier_list()) + len(ledger())
    return n, round(M.t_threshold(n), 2)


def log(row):
    L = ledger(); row = dict(row); row.setdefault("date", now().isoformat(timespec="minutes"))
    need = {"id", "title", "stage", "verdict", "verified", "not_verified", "risks"}
    assert need <= set(row), f"missing {need - set(row)} (every row needs a receipt: verified / not_verified / risks)"
    if row["verdict"] == "ERROR":
        assert row.get("error_class") in ERROR_CLASSES, f"ERROR rows need error_class in {sorted(ERROR_CLASSES)}"
    if row.get("looks", 0) and looks_quarter(L) + int(row["looks"]) > LOOKS_QUARTER:
        raise SystemExit(f"sealed-look budget spent ({LOOKS_QUARTER} a quarter): ask the user")
    L.append(row); json.dump(L, open(LEDGER, "w"), indent=1); summary(L)


def summary(L=None):
    L = L if L is not None else ledger(); I = ideas()
    n_items, t = bar() if os.path.exists("TIER_LIST.md") else (0, 0)
    alive = [r for r in L if r.get("verdict") == "PASS" or (r.get("stage", 0) >= 3 and r.get("verdict") != "FAIL")]
    data = dict(updated=now().isoformat(timespec="minutes"), state="stopped" if os.path.exists(STOP) else "running",
                studies=len(L), today=runs_today(L), cap=CAP_DAY, looks_quarter=looks_quarter(L), looks_budget=LOOKS_QUARTER,
                passed_stage={s: sum(1 for r in L if r.get("stage", 0) >= s) for s in range(1, 6)},
                queued=sum(1 for i in I if i["status"] == "queued"), blocked=sum(1 for i in I if i["status"] == "blocked"),
                next=next_idea(), needs_user=[f"{i['id']}: {held(i, L)}" for i in I if i["status"] == "queued" and held(i, L)], t_bar=t, n_trials=n_items, alive=alive[-20:], recent=L[-15:][::-1])
    os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(data, open(OUT, "w"), indent=1)
    # dashboard tables (Apex Live Desk 'Strategy lab' panel): one stats row + one row per study, newest first
    stats = {k: data[k] for k in ("state", "studies", "today", "cap", "queued", "blocked", "looks_quarter", "looks_budget",
                                  "t_bar", "updated")}
    stats.update(key="lab", next=data["next"] or "", **{f"stage{s}": n for s, n in data["passed_stage"].items()})
    json.dump([stats], open(OUT.replace("lab.json", "lab_stats.json"), "w"), indent=1)
    cols = ("id", "date", "title", "market", "stage", "verdict", "gate", "t_design", "t_holdout", "tier")
    rows = [{c: r.get(c) for c in cols} | {"key": f"{r.get('id', '')} {r.get('date', '')}"} for r in L[::-1][:60]]
    json.dump(rows, open(OUT.replace("lab.json", "lab_studies.json"), "w"), indent=1)
    return data


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    if cmd == "can_run":
        r = can_run(); print(r); sys.exit(0 if r == "OK" else 1)
    if cmd == "next": print(next_idea() or "")
    if cmd == "dupcheck": print("\n".join(dupcheck(sys.argv[2])) or "no C/D/F row contains all of: " + sys.argv[2])
    if cmd == "bar": print("N %d, t bar %.2f" % bar())
    if cmd == "log": log(json.loads(sys.argv[2])); print("logged")
    if cmd == "summary": d = summary(); print({k: d[k] for k in ("studies", "today", "queued", "next", "t_bar")})
