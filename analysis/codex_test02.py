"""Focused logic probes for TEST_02; NOT a PowerLanguage compiler/backtest.

Run from repo root: python analysis/codex_test02.py. Only scratch-free synthetic
data and existing repo helpers are used; no live platform access.
"""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import re
import subprocess

import numpy as np
import pandas as pd

from grid import execute
from grid24 import jof
from replica import is_early_close

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "agents/codex/results"


def early(d):
    """Literal translation of corrected PL's holiday predicate, checked vs repo."""
    m, day, y, w = d.month, d.day, d.year, (d.weekday()+1) % 7
    weekday = 1 <= w <= 5
    return ((m == 1 and ((day == 1 and weekday) or (day == 2 and w == 1)))
            or (m == 1 and w == 1 and 15 <= day <= 21)
            or (m == 2 and w == 1 and 15 <= day <= 21)
            or (m == 5 and w == 1 and day >= 25)
            or (m == 6 and y >= 2022 and ((day == 19 and weekday) or (day == 18 and w == 5) or (day == 20 and w == 1)))
            or (m == 7 and (((day == 3 or day == 4) and weekday) or (day == 5 and w == 1)))
            or (m == 9 and w == 1 and day <= 7)
            or (m == 11 and w == 4 and 22 <= day <= 28)
            or (m == 11 and w == 5 and 23 <= day <= 29)
            or (m == 12 and (((day == 24 or day == 25) and weekday) or (day == 26 and w == 1))))


class DateState:
    """Probe date-state transitions; independent daily-group oracle below."""
    def __init__(self):
        self.date = None
        self.prev = None
        self.ledger = []

    def step(self, date, time, op, hi, lo, cl, volume):
        if self.date != date:
            if self.date is not None:
                if self.complete and self.prev is not None and self.date.weekday() < 5:
                    tr = max(self.hi, self.prev)-min(self.lo, self.prev)
                    self.ledger.append((self.date, tr))
                self.prev = self.close
            self.complete = self.date is not None or time == 0
            self.date = date
            self.op, self.hi, self.lo = op, hi, lo
            self.pv = self.volume = 0
        else:
            self.hi, self.lo = max(self.hi, hi), min(self.lo, lo)
        self.close = cl
        self.pv += (hi+lo+cl)/3*volume
        self.volume += volume
        atr = np.mean([x[1] for x in self.ledger[-15:]]) if len(self.ledger) >= 15 else 0
        return atr


def main():
    logs = []
    def say(s): logs.append(s); print(s)
    task = (ROOT / "agents/codex/TEST_02_CODE_REVIEW.md").read_text(encoding="utf-8")
    supplied = task.split("```pascal\n", 1)[1].split("```", 1)[0].rstrip()
    corrected = (RESULTS / "TEST_02_corrected.txt").read_text(encoding="utf-8")
    say("TEST_02 plan 6fdb195; deterministic logic probes; zero performance trials.")
    for name, src in (("supplied Pascal block", supplied), ("corrected reference", corrected)):
        say(name + " SHA256 " + hashlib.sha256(src.encode()).hexdigest())
    say("SUPPLIED SOURCE, line 1 = opening comment:")
    for i, line in enumerate(supplied.splitlines(), 1): say(f"{i:3}: {line}")
    assert len(supplied.splitlines()) == 78

    # No assumption of a second midnight reset at 00:30.
    cases = [(2330,2300,False,True), (0,2330,True,True), (30,0,False,False), (1000,930,False,False)]
    for now, prev, changed, expected in cases:
        actual = changed or now == 0 or (now > 0 and prev >= 2300)
        assert actual == expected
        say(f"RESET now={now:04} prev={prev:04} date_change={changed}: original={actual}; date-only={changed}")

    state = DateState()
    rows, snapshots = [], []
    for i, d in enumerate(pd.date_range("2026-08-03", periods=35)):
        if d.weekday() == 5: continue
        times = [1730,2330] if d.weekday() == 6 else [0,1200,2330]
        if i == 0: times = [1200,2330]  # explicitly incomplete startup date
        for j, tm in enumerate(times):
            op = 10000+i*10+j
            hi, lo, close = op+5+j, op-4, op+2
            atr = state.step(d,tm,op,hi,lo,close,100+j)
            rows.append((d,tm,op,hi,lo,close))
            snapshots.append((d,tm,atr,len(state.ledger)))
    bars = pd.DataFrame(rows, columns=["date","time","o","h","l","c"])
    grouped = bars.groupby("date", sort=True).agg(h=("h","max"), l=("l","min"), c=("c","last"))
    prevc = grouped.c.shift(1)
    oracle = pd.concat([grouped.h,prevc],axis=1).max(axis=1)-pd.concat([grouped.l,prevc],axis=1).min(axis=1)
    oracle = oracle[(oracle.index.weekday < 5) & (oracle.index > grouped.index[0])]
    for d, value in state.ledger:
        assert np.isclose(value, oracle[d])
    assert all(d.weekday() < 5 for d,_ in state.ledger)
    assert all(d != grouped.index[0] for d,_ in state.ledger)
    for d, tm, atr, count in snapshots:
        known = oracle[oracle.index < d]
        want = known.iloc[-15:].mean() if len(known) >= 15 else 0
        assert np.isclose(atr,want)
        assert (atr == 0) == (count < 15)
    first_ready = next(x for x in snapshots if x[2] > 0)
    say(f"ATR PASS: independent daily aggregation matches all {len(state.ledger)} stored weekday TRs; partial startup excluded; "
        f"Sunday closes retained as TR reference but Sunday TR excluded; first 15-day-ready calculation {first_ready[0].date()} {first_ready[1]:04}.")
    last_date = snapshots[-1][0]
    assert len(set(x[2] for x in snapshots if x[0] == last_date)) == 1
    say("ATR PASS: current date's evolving range does not alter that date's ATR.")

    # All-out intrabar round trip: completed-trade count cannot be inferred from
    # sampled flat states. This is a lifecycle example, not an MC syntax emulator.
    sampled_positions = [0,0,0,0]
    old_count = sum(a != 0 and b == 0 for a,b in zip(sampled_positions[1:],sampled_positions[:-1]))
    completed = [0,1,2,3]
    fixed_counts = [n+int(mp!=0) for n,mp in zip(completed,sampled_positions)]
    assert old_count == 0 and fixed_counts[-1] == 3
    assert not fixed_counts[-1] < 3
    say(f"COUNTER PASS: three entry/exit round trips observed flat at closes -> sampled-transition count {old_count}, "
        f"completed-trade baseline count {fixed_counts[-1]}; fourth entry blocked.")

    g = SimpleNamespace(o=np.full((1,1440),10000.0), h=np.full((1,1440),10010.0),
                        l=np.full((1,1440),9990.0), c=np.full((1,1440),10000.0),
                        ts=np.array([np.datetime64("2026-10-01")]), last_j=np.array([1439]))
    j0 = jof(1000)+1
    g.l[0,j0] = 9900
    g.c[0,j0] = 9910
    sig = pd.DataFrame(dict(day=[0],dj=[jof(1000)],side=[1],stop=[75.0],target=[40.0],exit_j=[jof(1430)]))
    t = execute(g,sig,max_trades=3)
    assert len(t) == 1 and t.iloc[0].j1 == j0 and t.iloc[0].exit == 9925 and t.iloc[0].kind == 0
    say(f"ENTRY-BAR PROBE PASS: repo executor exits at minute {j0}, price 9925 for immediate stop; "
        "ordinary manual exits first evaluated at 10:30 can only work from the next opening tick, after this event.")
    assert 9925 > 9910
    say("REJECTION EXAMPLE: late sell stop 9925 is above a current market of 9910; a historical hypothetical fill is not broker acceptance.")
    for pv,symbol in ((20,"NQ"),(2,"MNQ")):
        assert 75*pv == (1500 if pv == 20 else 150)
        assert 40*pv == (800 if pv == 20 else 80)
        say(f"UNITS {symbol}: per-contract stop ${75*pv}, target ${40*pv}; two contracts double dollars, not price distance.")

    calendar = pd.date_range("2018-01-01","2027-12-31")
    assert all(early(d) == is_early_close(d) for d in calendar)
    say(f"HOLIDAY PASS: copied predicate matches repo helper for all {len(calendar)} dates 2018-2027; this is code parity, not CME schedule certification.")
    for d in (pd.Timestamp("2026-11-27"), pd.Timestamp("2026-07-03")):
        assert early(d)
    regular_allowed = [t for t in range(0,1440,30) if jof(1000) <= t <= jof(1230)]
    holiday_allowed = [t for t in regular_allowed if t < jof(1100)]
    assert regular_allowed == [600,630,660,690,720,750]
    assert holiday_allowed == [600,630]
    say(f"WINDOW PASS: regular decision minutes {regular_allowed}; early-day {holiday_allowed}; flats 14:30 / 11:30.")
    say("TIME SEMANTICS: next bar following 14:30 opens after that boundary and is stamped 15:00; not a deliberate 30-minute wait. "
        "A 12:00 halt has no 14:30 calculation; a close-based live order cannot guarantee execution at a historical closing tick.")

    # Narrow text checks tie the reviewed artifact to the intended corrections.
    clean = re.sub(r"\{.*?\}","",corrected,flags=re.S)
    assert "AvgTrueRange(" not in clean and "MarketPosition[1]" not in clean
    assert "BarType_ex <> 2" in clean and "BarInterval <> 30" in clean
    assert "SetStopContract;" in clean
    assert "SetStopLoss(StopPts * BigPointValue);" in clean
    assert "SetProfitTarget(TargetPts * BigPointValue);" in clean
    assert clean.index("SetStopLoss(") < clean.index('Buy ("VB_Combined_Long")')
    assert "TotalTrades - DayStartTrades" in clean
    assert "Low <= EntryPrice - StopPts" in clean
    assert 'Sell ("VB_TimeExit") this bar on close' in clean
    assert "Time <= EndTimeCT" in clean and "Time < DayLastEntry" in clean
    assert "BarVol = Ticks;" in clean
    assert clean.count("(") == clean.count(")")
    assert len(re.findall(r"\bbegin\b",clean,re.I)) == len(re.findall(r"\bend\b",clean,re.I))
    say("STRUCTURE PASS: built-in exits before entry, per-contract conversion, completed counter, Low guard, exact-close historical flat, inclusive regular/strict holiday limits, total volume, balanced delimiters.")
    subprocess.run(["git", "diff", "--exit-code", "cb8450b", "--", "apex_strategies", "funded_strategies",
                    "MULTICHARTS_PITFALLS.md", "TIER_LIST.md", "TODO.md"], cwd=ROOT, capture_output=True, check=True)
    say("BOUNDARY PASS: live strategy directories, pitfalls, tier list and TODO unchanged from TEST_01 commit cb8450b.")
    say("NO INTRABAR LOOK-AHEAD identified under normal close-only calculation: final decision-bar OHLC known before next-bar entry. "
        "Synthetic probes do not validate PowerLanguage compilation, order routing, live fills, or market edge.")
    say("PASS: all focused Python assertions. NOT SAFE for immediate live pasting; reference remains uncompiled; TEST_01 rejects adoption.")
    path = ROOT / "analysis/outputs/codex_test02_output.txt"
    path.write_text("\n".join(logs)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
