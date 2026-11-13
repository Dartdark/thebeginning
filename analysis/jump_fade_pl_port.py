"""Line-by-line Python port of apex_strategies/NQ_Jump_Fade.txt (2026-11-12): proves the PowerLanguage logic (streaming ring buffers,
late-closed 5-min buckets) reproduces the research score (analysis/jump_lib.py) and trades (analysis/jump_morning_fade.py).
Compares: J on every 5-min bar, the signal list, and the trades (same 1-min fill engine, analysis/jump_study.trades).
  tools/run_stamped.sh analysis/jump_fade_pl_port.py > analysis/outputs/jump_fade_pl_port_output.txt
"""
import sys, math, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_lib as L, jump_study as S

K, KMIN, SLEN, SMIN, NLEN, NMIN = 276, 138, 60, 20, 5520, 1380
print(__doc__.split("\n")[0])
m = L.minute(); ts = m.ts.to_numpy(); hi, lo, cl = m.high.to_numpy(), m.low.to_numpy(), m.close.to_numpy()
mins = (m.ts.dt.hour * 60 + m.ts.dt.minute).to_numpy(); jul = (m.ts.dt.normalize().to_numpy().astype("datetime64[D]").astype(np.int64))
prod = np.zeros(K); pok = np.zeros(K, bool); psum = 0.0; pcnt = 0; ppos = 0
sx = np.zeros((288, SLEN)); sok = np.zeros((288, SLEN), bool); spos = np.zeros(288, int); ssum = np.zeros(288); scnt = np.zeros(288, int)
nv = np.zeros(NLEN); nok = np.zeros(NLEN, bool); nsum = 0.0; ncnt = 0; npos = 0
cur = -1; pend = False; have = False; prevc = 0.0; prevkey = -1; aprev = 0.0; aprevok = False
BH = BL = BC = 0.0; BN = 0; BEND = 0; out = []
for i in range(len(ts)):
    mm = int(mins[i]); endm = mm if mm % 5 == 0 else mm - mm % 5 + 5; key = int(jul[i]) * 1440 + endm; fin = None
    if key != cur:
        if pend: fin = (cur, BEND, BH, BL, BC, BN, True)
        cur = key; BEND = endm % 1440; BH, BL, BC, BN = hi[i], lo[i], cl[i], 1; pend = True
    else:
        BH = max(BH, hi[i]); BL = min(BL, lo[i]); BC = cl[i]; BN += 1
    if mm % 5 == 0 and fin is None:
        fin = (cur, BEND, BH, BL, BC, BN, False); pend = False
    if fin is None or fin[5] < 3: continue
    fkey, fend, fh, fl, fc, fn, late = fin
    rok = have and fkey - prevkey <= 10; r = fc - prevc if rok else 0.0; a = abs(r)
    sigok = pcnt >= KMIN and psum > 0; sig = math.sqrt(math.pi / 2 * psum / pcnt) if sigok else 0.0
    ppos = (ppos + 1) % K
    if pok[ppos]: psum -= prod[ppos]; pcnt -= 1
    if rok and aprevok: prod[ppos] = a * aprev; pok[ppos] = True; psum += prod[ppos]; pcnt += 1
    else: prod[ppos] = 0.0; pok[ppos] = False
    aprev, aprevok = a, rok
    xok = rok and sigok; x = a / sig if xok else 0.0; sl = fend // 5
    frok = scnt[sl] >= SMIN; fraw = ssum[sl] / scnt[sl] if frok else 0.0
    sp = (spos[sl] + 1) % SLEN; spos[sl] = sp
    if sok[sl, sp]: ssum[sl] -= sx[sl, sp]; scnt[sl] -= 1
    if xok: sx[sl, sp] = x; sok[sl, sp] = True; ssum[sl] += x; scnt[sl] += 1
    else: sx[sl, sp] = 0.0; sok[sl, sp] = False
    npos = (npos + 1) % NLEN
    if nok[npos]: nsum -= nv[npos]; ncnt -= 1
    if frok: nv[npos] = fraw; nok[npos] = True; nsum += fraw; ncnt += 1
    else: nv[npos] = 0.0; nok[npos] = False
    J = np.nan
    if frok and ncnt >= NMIN and nsum > 0 and sigok and rok:
        f = fraw / (nsum / ncnt)
        if f > 0: J = r / (sig * f)
    prevc, have, prevkey = fc, True, fkey
    out.append((fkey, fend, J, fh - fl, r, late, i))
P = pd.DataFrame(out, columns=["key", "end", "J", "rng", "r", "late", "i_last"])
P["ts"] = pd.to_datetime(P.key // 1440, unit="D") + pd.to_timedelta(P.key % 1440, unit="m")
b = L.bars(); B = b[["ts", "J"]].merge(P[["ts", "J", "late"]], on="ts", how="outer", suffixes=("_py", "_pl"), indicator=True)
both = B[B._merge == "both"]; ok = both.J_py.notna() & both.J_pl.notna()
print(f"5-min bars: research {len(b):,}, port {len(P):,}, matched {len(both):,}; closed late in the port: {int(P.late.sum()):,}")
print(f"J on matched bars with both defined ({ok.sum():,}): max |diff| {np.abs(both.J_py - both.J_pl)[ok].max():.2e}, "
      f"corr {np.corrcoef(both.J_py[ok], both.J_pl[ok])[0, 1]:.6f}; defined in one only: {int((both.J_py.notna() != both.J_pl.notna()).sum())}")
hh = lambda t: pd.DatetimeIndex(t).hour
sig_py = set(b.ts[(b.J.abs() > 3) & np.isin(b.ts.dt.hour, [7, 8, 9]) & (b.ts.dt.year >= 2018)])
sig_pl = set(P.ts[(P.J.abs() > 3) & np.isin(hh(P.ts), [7, 8, 9]) & (P.ts.dt.year >= 2018)])
print(f"signal bars 2018+: research {len(sig_py)}, port {len(sig_pl)}, both {len(sig_py & sig_pl)}, research only {len(sig_py - sig_pl)}, port only {len(sig_pl - sig_py)}")
M = S.Mkt(); yr = b.ts.dt.year.to_numpy(); sgn = np.sign(b.r).fillna(0).to_numpy()
Jpl = b[["ts"]].merge(P[["ts", "J"]], on="ts", how="left").J.to_numpy()
mk = lambda J: (yr >= 2018) & (np.abs(np.nan_to_num(J)) > 3) & np.isin(b.ts.dt.hour.to_numpy(), [7, 8, 9])
t_py = S.trades(b, M, mk(b.J.to_numpy()), -sgn, "rng", 1.5, tp=0.3, hold=240); t_pl = S.trades(b, M, mk(Jpl), -sgn, "rng", 1.5, tp=0.3, hold=240)
print(S.summ(t_py, "research trades")); print(S.summ(t_pl, "port trades"))
same = t_py.merge(t_pl, on="ts", suffixes=("", "_pl")); print(f"identical entry minutes {len(same)} of {len(t_py)} / {len(t_pl)}; same net on those: {np.mean(np.isclose(same.net, same.net_pl)):.1%}")
lt = set(P.ts[P.late]); print(f"signal bars closed late (entry one minute later in MultiCharts): {len(sig_pl & lt)} of {len(sig_pl)}")
