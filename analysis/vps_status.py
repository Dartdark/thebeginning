"""Read the VPS status snapshot (2026-11-01; written by live/vps/status_push.ps1 every 5 min to branch 'vps-status').
  python3 analysis/vps_status.py [out_dir]   fetch, print status.json + trade-log tail
screen.jpg (from screen_push.ps1, if installed): open it with the Read tool to see the desktop."""
import json, os, subprocess, sys, datetime as dt
out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/vps_status"
run = lambda *a, **k: subprocess.run(["git", *a], capture_output=True, **k)
if run("fetch", "-q", "origin", "vps-status").returncode: sys.exit("no vps-status branch yet (task not installed or never pushed)")
os.makedirs(out, exist_ok=True)
for f in ("status.json", "trades_tail.csv", "alerts_tail.txt", "screen.jpg", "screen_status.txt"):
    r = run("show", f"FETCH_HEAD:{f}")
    if r.returncode == 0: open(os.path.join(out, f), "wb").write(r.stdout)
s = json.load(open(os.path.join(out, "status.json"), encoding="utf-8-sig"))
print(f"VPS time {s['time_local']} ({s['tz']}); boot {s['boot']}; disk {s['disk_free_gb']} GB; KILL flag {s['kill_flag']}")
age = dt.datetime.now() - dt.datetime.fromisoformat(s["time_local"])
for x in s.get("processes") or []: print(f"  proc {x['name']} '{x.get('title')}' started {x['started']} tcp {x['tcp_established']} responding {x['responding']}")
if not s.get("processes"): print("  NO MultiCharts process running")
for t in s.get("tasks") or []: print(f"  task {t['task']}: {t.get('last_run')} result {t.get('last_result', '')}")
tail = os.path.join(out, "trades_tail.csv")
# routing check (2026-11-01): latest ACCT row per tag; route_account (col 9, GetAccountID) vs live/expected_setup.json
cfg = json.load(open("live/expected_setup.json")); last = {}
if os.path.exists(tail):
    for r in (l.strip().split(",") for l in open(tail, errors="replace")):
        if r[0] == "ACCT" and len(r) > 8: last[r[1]] = r
print("routing (VERIFIED only where route_account is filled; empty = old monitor or auto-trading off):")
for tag, ch in cfg["charts"].items():
    want = cfg["accounts"].get(ch.get("account", ""), {}).get("id"); r = last.get(tag)
    if not r: print(f"  {tag:<10} no ACCT row in the tail"); continue
    route = r[8].strip()
    v = "OK" if route == want else ("UNKNOWN (no route_account)" if not route else f"WRONG: sends to {route}")
    print(f"  {tag:<10} want {want}  route {route or '-':<16} {v}; monitor AccountName {r[3]}{'' if r[3] == want else ' (WRONG)'}; auto {r[4]}")
if os.path.exists(tail): print("trade log (last 15):\n" + "".join(open(tail, errors="replace").readlines()[-15:]))
for f in ("screen_status.txt", "screen.jpg"):
    if os.path.exists(os.path.join(out, f)): print(f"{f}: {os.path.join(out, f)}" + (" -> " + open(os.path.join(out, f)).read().strip() if f.endswith("txt") else ""))
