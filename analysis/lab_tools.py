"""Lab helpers (2026-10-31, lab/README.md). The scheduled lab run calls these; they enforce the kill switch, the 5-a-day cap,
the sealed-look budget and the multiple-testing bar, and write the dashboard's Lab panel.
  python3 analysis/lab_tools.py can_run           -> 'OK' or the reason not to run (exit 1)
  python3 analysis/lab_tools.py next              -> the next queued idea ID (or nothing)
  python3 analysis/lab_tools.py bar               -> current t bar for a lab idea
  python3 analysis/lab_tools.py log '<json>'      -> append one study row (fields below) and rebuild the panel
  python3 analysis/lab_tools.py summary           -> rebuild analysis/outputs/dashboard/lab.json
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
    return sum(1 for r in (L or ledger()) if r.get("date", "")[:10] == day)


def looks_quarter(L=None, d=None):
    d = d or now().date(); q0 = dt.date(d.year, 3 * ((d.month - 1) // 3) + 1, 1).isoformat()
    return sum(int(r.get("looks", 0)) for r in (L or ledger()) if r.get("date", "")[:10] >= q0)


def ideas():
    out, cur = [], None
    for line in open(IDEAS, encoding="utf-8"):
        m = re.match(r"^## (Q\d+) · (\w+) · priority (\d)", line)
        if m: cur = dict(id=m.group(1), status=m.group(2), priority=int(m.group(3)), order=len(out)); out.append(cur)
    return out


def next_idea():
    q = [i for i in ideas() if i["status"] == "queued"]
    return min(q, key=lambda i: (i["priority"], i["order"]))["id"] if q else None


def can_run():
    if os.path.exists(STOP): return "STOPPED: lab/STOP exists (kill switch)."
    n = runs_today()
    if n >= CAP_DAY: return f"CAP: {n} studies already today (max {CAP_DAY})."
    if not next_idea(): return "EMPTY: no queued idea in lab/IDEAS.md."
    return "OK"


def bar():
    """t bar for a lab idea: Bonferroni over TIER_LIST ranked items + lab studies so far (metrics.t_threshold)."""
    sys.path.insert(0, "analysis"); import metrics as M
    from trials import parse_tier_list
    n = len(parse_tier_list()) + len(ledger())
    return n, round(M.t_threshold(n), 2)


def log(row):
    L = ledger(); row = dict(row); row.setdefault("date", now().isoformat(timespec="minutes"))
    need = {"id", "title", "stage", "verdict"}
    assert need <= set(row), f"missing {need - set(row)}"
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
                next=next_idea(), t_bar=t, n_trials=n_items, alive=alive[-20:], recent=L[-15:][::-1])
    os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(data, open(OUT, "w"), indent=1)
    return data


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    if cmd == "can_run":
        r = can_run(); print(r); sys.exit(0 if r == "OK" else 1)
    if cmd == "next": print(next_idea() or "")
    if cmd == "bar": print("N %d, t bar %.2f" % bar())
    if cmd == "log": log(json.loads(sys.argv[2])); print("logged")
    if cmd == "summary": d = summary(); print({k: d[k] for k in ("studies", "today", "queued", "next", "t_bar")})
