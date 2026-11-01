"""Live-guard helpers (2026-10-30), shared by premarket_check.py and the Friday review.
floors()   Apex EOD trailing floor per live account from the Chart Monitor's equity (ACCT rows in live/trades), the same rule
           as watchdog.ps1 section 2d: floor = min(peak end-of-day equity - trail, lock) since the account started.
versions() Code-version stamps: the HB_Ver string in every strategy file that writes a heartbeat, vs the version each live
           chart's strategy writes in its SIG rows (field 4). An old paste shows up as a missing or different version.
stale_versions() Repo files edited (git) after the date in their HB_Ver: the version wasn't bumped.
  python3 analysis/live_guard.py          (prints all three)
"""
import glob, json, os, re, subprocess
import pandas as pd

COLS = ["event", "tag", "symbol", "side", "contracts", "entry_date", "entry_time", "entry_price", "exit_date",
        "exit_time", "exit_price", "profit_usd", "bar_date", "bar_time"]
FILES = sorted(glob.glob("apex_strategies/*.txt") + glob.glob("funded_strategies/*.txt"))


def floors(day=None, cfg=None):
    """{account name: dict(id, equity, floor, room, max_stop, peak, date)} from ACCT rows up to day (YYYYMMDD)."""
    cfg = cfg or json.load(open("live/expected_setup.json")); out = {}
    for name, v in cfg["accounts"].items():
        if v.get("status") != "live" or "start" not in v: continue
        eod = {}
        for f in sorted(glob.glob("live/trades/2*.csv")):
            d = os.path.basename(f)[:8]
            if d < v["started"] or (day and d > day): continue
            rows = [l.split(",") for l in open(f) if l.startswith("ACCT,") and f",{v['id']}," in l]
            eq = [float(r[6]) for r in rows if r[6] and float(r[6]) > 0]
            if eq: eod[d] = eq[-1]
        if not eod: continue
        last = max(eod); peak = max([v["start"]] + [e for d, e in eod.items() if d < last])
        floor = min(peak - v["trail"], v["lock"])
        out[name] = dict(id=v["id"], date=last, equity=eod[last], peak=peak, floor=floor, room=round(eod[last] - floor, 2),
                         max_stop=v["max_stop"])
    return out


def versions():
    """{file stem: 'stem date'} for every strategy file with a heartbeat version."""
    out = {}
    for f in FILES:
        m = re.search(r'HB_Ver\(\s*"([^"]+)"\s*\)', open(f, encoding="utf-8", errors="ignore").read())
        if m and not m.group(1).startswith("<"): out[os.path.splitext(os.path.basename(f))[0]] = m.group(1)
    return out


def chart_versions(df, charts):
    """Problems: chart strategies writing no version (old paste) or a version that differs from the repo file."""
    repo = versions(); old, out = [], []
    for tag in charts:
        s = df[(df.event == "SIG") & (df.tag == tag)]
        if s.empty: continue
        ver = str(s.iloc[-1].side) if pd.notna(s.iloc[-1].side) else ""
        if not ver: old.append(tag); continue
        stem = ver.split(" ")[0]
        pend = json.load(open("live/expected_setup.json")).get("pending_install", {})
        if stem in repo and repo[stem] != ver and repo[stem].split(" ")[-1] in pend:
            continue                                      # update not installed yet on purpose (user muted it, 2026-11-01)
        if stem in repo and repo[stem] != ver:
            out.append(f"{tag}: runs {ver}, the repo has {repo[stem]}: paste the new code.")
    if old: out.append(f"Code version not stamped on {len(old)} chart(s) ({', '.join(old)}): repaste their strategies once (weekend).")
    return out


def stale_versions():
    """Repo strategy files committed after the date in their HB_Ver (forgot to bump)."""
    out = []
    for stem, ver in versions().items():
        f = next(x for x in FILES if os.path.splitext(os.path.basename(x))[0] == stem)
        d = subprocess.run(["git", "log", "-1", "--format=%cs", "--", f], capture_output=True, text=True).stdout.strip()
        if d and d > ver.split(" ")[-1]: out.append(f"{f}: changed {d}, version still {ver}: bump HB_Ver.")
    return out


if __name__ == "__main__":
    for k, v in floors().items(): print(k, v)
    print(versions()); print(stale_versions())
