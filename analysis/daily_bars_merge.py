"""Append the VPS's daily 1-minute bars (data/live_bars/YYYYMMDD.csv, from tools/exporters/NQ_Daily_Bar_Feed.txt) to the
repo's NQ data: 08:00-15:15 CT -> data/NQ_1min_<year>.csv, the rest -> data/NQ_1min_ON_<year>.csv (the NQ_Bar_Exporter
split). Only bars newer than each file's last row are added; a day that is still in progress (no 15:15 bar yet) is
left for the next run. Prints what it added. Run by the 16:40 job (2026-10-29).
  python3 analysis/daily_bars_merge.py
"""
import glob, os
import pandas as pd

COLS = ["date", "time", "open", "high", "low", "close", "volume"]


def last_key(path):
    if not os.path.exists(path): return 0
    with open(path, "rb") as f:
        f.seek(0, 2); f.seek(max(0, f.tell() - 200)); tail = f.read().decode().strip().splitlines()[-1]
    d, t = tail.split(",")[:2]
    return int(d) * 10000 + int(t) if d.isdigit() else 0


def main():
    files = sorted(glob.glob("data/live_bars/*.csv"))
    if not files: print("no live bars yet (data/live_bars/ empty)"); return
    b = pd.concat([pd.read_csv(f, header=None, names=COLS) for f in files]).drop_duplicates(["date", "time"])
    b = b.sort_values(["date", "time"]); b["key"] = b.date * 10000 + b.time
    # keep only complete regular days: a date whose 15:15 bar is there (overnight bars before it are complete too)
    done = set(b[b.time == 1515].date)
    if not done: print("no complete day yet"); return
    b = b[b.key <= max(done) * 10000 + 1515]
    day = (b.time >= 800) & (b.time <= 1515)
    for part, mask, prefix in (("day", day, "NQ_1min_"), ("overnight", ~day, "NQ_1min_ON_")):
        x = b[mask]
        for yr, g in x.groupby(x.date // 10000):
            path = f"data/{prefix}{yr}.csv"; g = g[g.key > last_key(path)]
            if g.empty: continue
            new = not os.path.exists(path)
            g[COLS].to_csv(path, mode="a", header=new, index=False, float_format="%.2f")
            print(f"{path}: +{len(g)} {part} bars, {g.date.min()} {g.time.iloc[0]:04d} -> {g.date.max()} {g.time.iloc[-1]:04d}")


if __name__ == "__main__":
    main()
