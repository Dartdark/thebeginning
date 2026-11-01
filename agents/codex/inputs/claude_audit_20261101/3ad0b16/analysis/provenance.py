"""Result provenance (2026-11-01, review gap #5: results shifted when the data was extended). One line that pins a result to
the exact code and data it came from: git commit (+ 'dirty' when uncommitted changes exist), and per market the data files'
date range and a short fingerprint (sha256 of file names + sizes, cheap; changes whenever a file is added or extended).
  python3 analysis/provenance.py                 print the stamp (all markets in data/)
  python3 analysis/provenance.py NQ ES           only these markets
  tools/run_stamped.sh <script> [args] > out.txt  runs a script with the stamp as the output's first line
In code: `import provenance; print(provenance.stamp(["NQ"]))`; analysis/lab_tools.log() adds it to every ledger row.
"""
import glob, hashlib, os, re, subprocess, sys


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()


def last_line(path):
    with open(path, "rb") as f:
        f.seek(0, 2); n = f.tell(); f.seek(max(0, n - 300))
        return f.read().decode(errors="replace").strip().splitlines()[-1]


def market(sym):
    files = sorted(glob.glob(f"data/{sym}_1min_*.csv"))
    if not files: return None
    h = hashlib.sha256("|".join(f"{os.path.basename(f)}:{os.path.getsize(f)}" for f in files).encode()).hexdigest()[:8]
    first = open(files[0]).readlines()[1].split(",")[0]; last = last_line(files[-1]).split(",")[0]
    return f"{sym} {first}-{last} #{h}"


def stamp(syms=None):
    syms = syms or sorted({m.group(1) for f in glob.glob("data/*_1min_*.csv") if (m := re.match(r"data/([A-Z0-9]+)_1min_", f))})
    dirty = " dirty" if git("status", "--porcelain", "--", "analysis", "apex_strategies", "funded_strategies") else ""
    data = "; ".join(x for x in (market(s) for s in syms) if x)
    return f"[provenance] code {git('rev-parse', '--short', 'HEAD')}{dirty} | data {data}"


if __name__ == "__main__":
    print(stamp(sys.argv[1:] or None))
