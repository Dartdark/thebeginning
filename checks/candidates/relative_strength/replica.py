"""Checker replica of RelStrength_v3 (built from RelStrength_v3.txt + spec.md only).

Bar loop over NQ 1-minute bars (Data1), as MultiCharts would: the script only runs on NQ bars,
ES (Data2) close is carried forward when ES has no bar that minute (MC behaviour), unless --skip_es_gaps.
Costs: $7.25 round turn + $5 (1 tick) per market/stop fill; limit target fills at the limit.
Usage: python3 replica.py [--start YYYYMMDD] [--skip_es_gaps] [--round_ticks] [--out file]
"""
import sys, pickle, argparse, math
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/thebeginning/analysis")

ap = argparse.ArgumentParser()
ap.add_argument("--start", type=int, default=0)
ap.add_argument("--skip_es_gaps", action="store_true")
ap.add_argument("--round_ticks", action="store_true")
ap.add_argument("--tgt_pen", type=float, default=0.0, help="target needs this many points beyond the limit")
ap.add_argument("--zmin", type=float, default=1.25)
ap.add_argument("--decide", type=int, default=900)
ap.add_argument("--seed", type=int, default=-1, help=">=0: placebo, random side on the signal days")
ap.add_argument("--out", default="/home/user/thebeginning/checks/candidates/relative_strength/trades_replica.csv")
a = ap.parse_args()
RNG = np.random.default_rng(a.seed if a.seed >= 0 else 0)

HOLF = set(int(str(x)) + 19000000 for x in """1100101 1100118 1100215 1100402 1100531 1100705 1100906 1101125 1101224 1110117 1110221 1110422
1110530 1110704 1110905 1111124 1111226 1120102 1120116 1120220 1120406 1120528 1120704 1120903 1121029 1121030 1121122 1121225 1130101 1130121
1130218 1130329 1130527 1130704 1130902 1131128 1131225 1140101 1140120 1140217 1140418 1140526 1140704 1140901 1141127 1141225 1150101 1150119
1150216 1150403 1150525 1150703 1150907 1151126 1151225 1160101 1160118 1160215 1160325 1160530 1160704 1160905 1161124 1161226 1170102 1170116
1170220 1170414 1170529 1170704 1170904 1171123 1171225 1180101 1180115 1180219 1180330 1180528 1180704 1180903 1181122 1181205 1181225 1190101
1190121 1190218 1190419 1190527 1190704 1190902 1191128 1191225 1200101 1200120 1200217 1200410 1200525 1200703 1200907 1201126 1201225 1210101
1210118 1210215 1210402 1210531 1210705 1210906 1211125 1211224 1220117 1220221 1220415 1220530 1220620 1220704 1220905 1221124 1221226 1230102
1230116 1230220 1230407 1230529 1230619 1230704 1230904 1231123 1231225 1240101 1240115 1240219 1240329 1240527 1240619 1240704 1240902 1241128
1241225 1250101 1250109 1250120 1250217 1250418 1250526 1250619 1250704 1250901 1251127 1251225 1260101 1260119 1260216 1260403 1260525 1260619
1260703 1260907 1261126 1261225""".split())
HOLE = set(int(x) + 19000000 for x in """1101126 1111125 1120703 1121123 1121224 1130703 1131129 1131224 1140703 1141128 1141224 1151127
1151224 1161125 1170703 1171124 1180703 1181123 1181224 1190703 1191129 1191224 1201127 1201224 1211126 1221125 1230703 1231124 1240703 1241129
1241224 1250703 1251128 1251224 1261127 1261224""".split())

gn = pickle.load(open("/home/user/thebeginning/scratch_data/g24.pkl", "rb"))
ge = pickle.load(open("/home/user/thebeginning/scratch_data/ge.pkl", "rb"))
# align ES rows to NQ calendar rows
ei = {d: i for i, d in enumerate(ge.dates)}
D = gn.D
ES = np.full((D, 1440), np.nan)
for i, d in enumerate(gn.dates):
    if d in ei: ES[i] = ge.c[ei[d]]

ZMIN, BETADAYS, SF, TF, ATRD = a.zmin, 20, 0.6, 1.0, 20
BARSDAY = 390; ALPHA = 2 / (BETADAYS * BARSDAY + 1)
TICK = 0.25; PV = 20.0; COMM = 7.25; SLIP = 5.0
J0, J1, JD, JF = 510, 900, (a.decide // 100) * 60 + a.decide % 100, 900

# state
cov = v1 = v2 = beta = res = 0.0; nest = 0
drng = []  # ring of last 20 ok-day ranges
prevA = None; prevB = None   # Close[1] and C2[1] (C2 carried forward on NQ bars)
lastB = np.nan
trades = []; diag = []
for i in range(D):
    date = int(gn.dates[i])
    rowA = gn.c[i]; has = ~np.isnan(rowA)
    if not has.any():
        continue
    dayok = not (date in HOLF or date in HOLE)
    newday = True
    avg = np.mean(drng) if drng else 0.0
    rhi = rlo = None; anc1 = anc2 = None; nba = 0; decided = False; sig = 0; zrel = np.nan
    pos = 0; entry = None; stop = tgt = None; ent_j = None; trade = None
    pending_entry = 0
    fullday_A = np.isfinite(gn.c[i, J0 + 1:J1 + 1]).all()
    for j in np.nonzero(has)[0]:
        cA = rowA[j]
        if not np.isnan(ES[i, j]):
            cB = ES[i, j]
        elif a.skip_es_gaps:
            cB = np.nan
        else:
            cB = lastB
        rth = J0 < j <= J1
        # --- fills at this bar (orders from previous bar) ---
        if pending_entry != 0:
            pos = pending_entry; entry = gn.o[i, j]; ent_j = j; pending_entry = 0
            trade = dict(date=date, side=pos, entry=entry, z=zrel)
            stop = entry - pos * SF * avg; tgt = entry + pos * TF * avg
            if a.round_ticks:
                stop = (math.floor(stop / TICK) if pos == 1 else math.ceil(stop / TICK)) * TICK
                tgt = (math.ceil(tgt / TICK) if pos == 1 else math.floor(tgt / TICK)) * TICK
        elif pos != 0 and avg > 0:
            o, h, l = gn.o[i, j], gn.h[i, j], gn.l[i, j]
            ex = None
            if pos == 1:
                if l <= stop: ex = ("stop", min(o, stop))
                elif h >= tgt + a.tgt_pen: ex = ("target", max(o, tgt))
            else:
                if h >= stop: ex = ("stop", max(o, stop))
                elif l <= tgt - a.tgt_pen: ex = ("target", min(o, tgt))
            if ex:
                trade.update(kind=ex[0], exit=ex[1], xj=j); trades.append(trade); pos = 0; trade = None
        # --- bar-close logic ---
        if rth and rhi is None:   # NewRTH
            rhi, rlo = gn.h[i, j], gn.l[i, j]
            anc1, anc2 = prevA, (prevB if prevB is not None else np.nan)
            nba = 0
        elif rth:
            rhi = max(rhi, gn.h[i, j]); rlo = min(rlo, gn.l[i, j])
        if rth and anc1 is not None and anc1 > 0: nba += 1
        if rth and dayok and prevA is not None and prevA > 0 and prevB is not None and prevB > 0 and cB > 0:
            rA = 1e4 * math.log(cA / prevA); rB = 1e4 * math.log(cB / prevB)
            if nest == 0:
                cov, v1, v2 = rA * rB, rA * rA, rB * rB
            else:
                cov += ALPHA * (rA * rB - cov); v1 += ALPHA * (rA * rA - v1); v2 += ALPHA * (rB * rB - v2)
            nest += 1
            if v1 > 0 and v2 > 0:
                beta = cov / v2; res = v1 - 2 * beta * cov + beta * beta * v2
        if rth and not decided and j >= JD and rhi is not None:
            decided = True
            if dayok and nba >= 1 and nest >= 5 * BARSDAY and res > 0 and anc1 and anc1 > 0 and anc2 > 0 and cB > 0:
                relx = 1e4 * math.log(cA / anc1) - beta * 1e4 * math.log(cB / anc2)
                zrel = relx / math.sqrt(res * nba)
                sig = 1 if zrel >= ZMIN else (-1 if zrel <= -ZMIN else 0)
                if a.seed >= 0 and sig != 0: sig = int(RNG.choice([-1, 1]))
                diag.append((date, zrel, beta, res, avg, fullday_A))
                if sig != 0 and pos == 0 and j < JF:
                    pending_entry = sig
        if pos != 0 and (j >= JF or j <= J0):
            trade.update(kind="flat", exit=cA, xj=j); trades.append(trade); pos = 0; trade = None
        prevA = cA
        if not np.isnan(cB): lastB = cB
        prevB = cB
    if rhi is not None and dayok:
        drng.append(rhi - rlo); drng = drng[-ATRD:]
    if pos != 0:   # carried over (should not happen)
        trade.update(kind="flat", exit=cA, xj=j); trades.append(trade)

T = pd.DataFrame(trades)
T["pts"] = T.side * (T.exit - T.entry)
T["net"] = T.pts * PV - COMM - SLIP * (1 + (T.kind != "target"))
T["date"] = pd.to_datetime(T.date.astype(str))
T = T[T.date >= "2018-01-01"]
T[["date", "side", "net", "kind", "entry", "exit", "z"]].to_csv(a.out, index=False)
pd.DataFrame(diag, columns=["date", "z", "beta", "res", "avg", "fullA"]).to_csv(a.out.replace(".csv", "_diag.csv"), index=False)
print(f"{len(T)} trades, net ${T.net.sum():,.0f}, mean ${T.net.mean():.1f}, win {np.mean(T.net>0):.3f}")
