"""Checker's replica of PAPERTREND v2 (NQ), built from spec.md only.
  python3 checks/candidates/papertrend/replica.py
Writes trades_replica.csv (roll days dropped), trades_replica_keeprolls.csv, placebo.csv (random side, same days/times)
in this folder, and ../papertrend_replica/{trades.csv, meta.json, placebo.csv}.
"""
import sys, os, pickle, json, shutil, warnings; warnings.filterwarnings("ignore")
ROOT = "/home/user/thebeginning"; sys.path.insert(0, ROOT + "/analysis"); os.chdir(ROOT)
import numpy as np, pandas as pd
from grid24 import jof

HERE = ROOT + "/checks/candidates/papertrend"
PV, TICK, COST = 20.0, 0.25, 7.25 + 2 * 5.0

g = pickle.load(open("scratch_data/g24.pkl", "rb"))
D = g.D; O, H, L, C = g.o, g.h, g.l, g.c
j831, j1455, j1500 = jof(831), jof(1455), jof(1500)
marks = [jof(t) for t in (845, 900, 915, 930, 945, 1000, 1015, 1030, 1045, 1100, 1115, 1130, 1145, 1200, 1215, 1230,
                          1245, 1300, 1315, 1330, 1345, 1400)]
assert marks[0] == jof(845) and marks[-1] == jof(1400) and len(marks) == 22

# full sessions: weekday rows with both the 14:55 and 15:00 bars (and an 08:31 open)
ts = pd.DatetimeIndex(g.ts)
rows = [r for r in range(D) if ts[r].dayofweek < 5 and not np.isnan(C[r, j1455]) and not np.isnan(C[r, j1500])]
sess = []
for r in rows:
    seg_h, seg_l = H[r, j831:j1500 + 1], L[r, j831:j1500 + 1]
    o = O[r, j831]
    if np.isnan(o):                                  # 08:31 bar missing: use first RTH open, flag it
        k = np.where(~np.isnan(O[r, j831:j1500 + 1]))[0]; o = O[r, j831 + k[0]]; miss = True
    else: miss = False
    sess.append(dict(row=r, date=ts[r], O=o, rng=np.nanmax(seg_h) - np.nanmin(seg_l), C=C[r, j1500], miss831=miss))
S = pd.DataFrame(sess)
S["atr"] = S.rng.rolling(14).mean().shift(1)              # previous 14 full sessions
S["yr"] = S.rng.shift(1); S["max7"] = S.rng.rolling(7).max().shift(1)
S["skip"] = S.yr >= S.max7
S["pc"] = S.C.shift(1); S["gap"] = S.O - S.pc
S["prow"] = S.row.shift(1)

# rolls (spec: analysis/s_rank_gap_round2_test.rolls_index on Sym("NQ"))
import s_rank_gap_round2_test as SR
SY = SR.Sym("NQ", g); rb, info = SR.rolls_index(SY); SY.set_rolls(rb)
rb = np.array(sorted(rb))
print(f"rolls found: {len(rb)}  first {info[:3]} last {info[-3:]}")


def has_roll(prow, row):
    a = int(prow) * 1440 + j1500 + 1; b = int(row) * 1440 + j831   # bars after prev 15:00 close .. today's 08:31 bar
    return bool(((rb >= a) & (rb <= b)).any())


out = []
for i, s in S.iterrows():
    if i < 14 or pd.isna(s.atr) or s.date < pd.Timestamp("2017-01-01"): continue
    if s.skip or s.gap == 0 or pd.isna(s.gap): continue
    r = int(s.row); up, dn = s.O + 0.5 * s.atr, s.O - 0.5 * s.atr; side = 1 if s.gap > 0 else -1
    sig = None
    for m in marks:
        c = C[r, m]
        if np.isnan(c): continue
        if (side > 0 and c > up) or (side < 0 and c < dn): sig = m; break
    if sig is None: continue
    k = np.where(~np.isnan(O[r, sig + 1:j1455 + 1]))[0]
    if not len(k): continue
    je = sig + 1 + k[0]; entry = O[r, je]; ex = C[r, j1455]
    gross = side * (ex - entry) * PV
    path = C[r, je:j1455 + 1]; lo = (L if side > 0 else H)[r, je:j1455 + 1]
    mae = np.nanmin(side * (lo - entry)) * PV - COST
    out.append(dict(date=s.date.strftime("%Y-%m-%d"), row=r, side=side, sig=sig, je=je, entry=entry, exit=ex,
                    gross=gross, net=gross - COST, mae=mae, roll=has_roll(s.prow, r), late_entry=je != sig + 1,
                    miss831=s.miss831))
T = pd.DataFrame(out)
print(f"trades (2017+, roll days kept): {len(T)}, roll days {T.roll.sum()}, late entries {T.late_entry.sum()}, "
      f"missing 08:31 bar {T.miss831.sum()}")
T.to_csv(HERE + "/trades_replica_keeprolls.csv", index=False)
TR = T[~T.roll].drop(columns="roll"); TR.to_csv(HERE + "/trades_replica.csv", index=False)
print(f"trades (roll days dropped): {len(TR)}  2018+: {(TR.date >= '2018-01-01').sum()}")

# placebo: random side on the same days, same entry bar and exit bar
rng = np.random.default_rng(20261024); pl = []
diff = (TR.exit - TR.entry).to_numpy() * PV
for run in range(500):
    sd = rng.choice([-1, 1], len(TR)); pl.append(pd.DataFrame(dict(run=run, date=TR.date, net=sd * diff - COST)))
P = pd.concat(pl); P = P[P.date >= "2018-01-01"]; P[["run", "net"]].to_csv(HERE + "/placebo.csv", index=False)

RD = ROOT + "/checks/candidates/papertrend_replica"; os.makedirs(RD, exist_ok=True)
TR.to_csv(RD + "/trades.csv", index=False); TR.to_csv(RD + "/trades_replica.csv", index=False)
shutil.copy(HERE + "/meta.json", RD + "/meta.json"); shutil.copy(HERE + "/placebo.csv", RD + "/placebo.csv")
