"""Checker replica of personal_strategies/ES_Dip_Buy.txt: executes the PowerLanguage bar by bar on ES 60-min bars (Central, stamped
at the close; built from the same roll-adjusted 1-min grid as the reference, from 2017-06-01), 4h candles built in code from the
1h bars, shadow position (unfiltered rule), the VIX/VIX3M filter read from data/VIX_VIX3M_ratio_mc.csv as MultiCharts' data2
(bars stamped 16:00 CT, only bars <= the current bar time visible), and the real orders (next-bar market entries, resting stop /
short limit target from the bar after the fill, market exit when the shadow is out).
  stops="1h"  : the .txt as written (shadow stops / target on the 1h bar's high / low, stop first)
  stops="1min": same rule, shadow stops walked on 1-min bars inside each hour (as the Python reference) -- isolates that difference
Run from repo root: python3 checks/candidates/mc_es_dip_buy/replica.py
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import co_oc_reversal_test as CO, roll_adjust as RA
OUT = "checks/candidates/mc_es_dip_buy/"
PV, COMM, TK = 50.0, 5.0, 12.5


def load():
    g = CO.load("ES"); c = g.c.ravel().astype(float); o = g.o.ravel().astype(float); h = g.h.ravel().astype(float); l = g.l.ravel().astype(float)
    J = RA.roll_jumps(g, "ES"); adj = np.zeros(len(c))
    for jj, jump in J.items(): adj[:jj] += jump
    ok = ~np.isnan(c)
    stamp = (pd.to_datetime(np.repeat(g.ts, 1440)) + pd.to_timedelta(np.tile(np.arange(1440), len(g.ts)), "m"))[ok]   # 1-min CLOSE stamp
    mm = pd.DataFrame({"open": o[ok] + adj[ok], "high": h[ok] + adj[ok], "low": l[ok] + adj[ok], "close": c[ok] + adj[ok], "raw_off": adj[ok]}, index=stamp)
    mm = mm[mm.index >= "2017-06-01 00:01"]
    key = mm.index.ceil("1h")                                          # MultiCharts 60-min bar = minutes stamped (T-1h, T]
    b = mm.groupby(key).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"), raw_off=("raw_off", "last"))
    return mm, b


def ratio():
    c = pd.read_csv("data/VIX_VIX3M_ratio_mc.csv")
    t = pd.to_datetime(c.Date, format="%m/%d/%Y") + pd.Timedelta(hours=16)
    return t.values, pd.to_datetime(c.Date, format="%m/%d/%Y").values, c.Close.to_numpy()


def run(mm, b, stops="1h", UseFilter=True, Qty=1, dbg=None):
    T = b.index; O, H, L, C = (b[k].to_numpy() for k in ("open", "high", "low", "close"))
    MT = mm.index.values; MH, ML, MO = mm.high.to_numpy(), mm.low.to_numpy(), mm.open.to_numpy()
    mstart = np.searchsorted(MT, (T - pd.Timedelta(hours=1)).values, side="right"); mend = np.searchsorted(MT, T.values, side="right")
    D2t, D2d, D2c = ratio(); d2_end = np.searchsorted(D2t, T.values, side="right")
    Tdate = T.normalize().values; Ttime = T.hour * 100 + T.minute
    hours = (T.values.astype("datetime64[h]").astype(np.int64))      # CK
    N1 = 0; A1 = SA1 = E18 = E40 = PC1 = 0.0
    H4B = -1; Has4 = False; H4H = H4L = H4C = 0.0; N4 = 0; PC4 = PH4 = PL4 = 0.0
    A4 = SA4 = A22 = SA22 = P4 = Q4 = SP4 = SQ4 = SDX = ADX4 = 0.0; NDX = 0; ADXok = False
    FU = FL = ST4 = 0.0; STok = False; TrUp = True
    ShIn = False; ShS = 0; ShE = ShStop = ShTgt = ShBest = 0.0; ShKeep = False; ShT = None
    shadow, real = [], []
    pos = 0; pend = []; rp = None
    for i in range(len(T)):
        # ----- engine: fills of orders sent at bar i-1 (market at the open; stop / limit inside the bar, stop checked first) -----
        if pend:
            for kind, px in pend:
                if kind == "entry" and pos == 0:
                    pos = ShS_at_send; rp = dict(et=T[i], ep=O[i], side=pos, sh=sh_id_at_send)
                elif kind == "mkt" and pos != 0:
                    real.append((rp["et"], T[i], rp["side"], rp["ep"], O[i], "mkt", rp["sh"])); pos = 0
            stop_o = [p for k, p in pend if k == "stop"]; tgt_o = [p for k, p in pend if k == "tgt"]
            if pos != 0 and stop_o:
                sp = stop_o[0]
                if (pos == 1 and L[i] <= sp) or (pos == -1 and H[i] >= sp):
                    real.append((rp["et"], T[i], pos, rp["ep"], min(O[i], sp) if pos == 1 else max(O[i], sp), "stop", rp["sh"])); pos = 0
            if pos == -1 and tgt_o and L[i] <= tgt_o[0] - 0.25:          # limit: 1 tick through
                real.append((rp["et"], T[i], pos, rp["ep"], min(O[i], tgt_o[0]), "target", rp["sh"])); pos = 0
            pend = []
        # ----- the .txt from here: 1h indicators -----
        OK = hours[i] - 1
        TR1 = H[i] - L[i] if N1 == 0 else max(H[i] - L[i], abs(H[i] - PC1), abs(L[i] - PC1))
        N1 += 1
        if N1 <= 14:
            SA1 += TR1
            if N1 == 14: A1 = SA1 / 14
        else: A1 += (TR1 - A1) / 14
        if N1 == 1: E18 = C[i]; E40 = C[i]
        else: E18 += 2 / 19 * (C[i] - E18); E40 += 2 / 41 * (C[i] - E40)
        PC1 = C[i]
        for ps4 in (1, 2, 3):
            Do4 = False
            if ps4 == 1: Do4 = Has4 and (OK // 4) != H4B
            if ps4 == 2:
                if not Has4: H4B = OK // 4; H4H = H[i]; H4L = L[i]; Has4 = True
                else: H4H = max(H4H, H[i]); H4L = min(H4L, L[i])
                H4C = C[i]
            if ps4 == 3: Do4 = Has4 and OK % 4 == 3
            if Do4:
                i4 = N4; N4 += 1
                if i4 == 0: TR4 = H4H - H4L; UpM = DnM = 0.0
                else:
                    TR4 = max(H4H - H4L, abs(H4H - PC4), abs(H4L - PC4)); UpM = H4H - PH4; DnM = PL4 - H4L
                    UpM, DnM = (UpM if (UpM > DnM and UpM > 0) else 0.0), (DnM if (DnM > UpM and DnM > 0) else 0.0)
                if i4 < 14:
                    SA4 += TR4
                    if i4 == 13: A4 = SA4 / 14
                else: A4 += (TR4 - A4) / 14
                if i4 < 22:
                    SA22 += TR4
                    if i4 == 21: A22 = SA22 / 22
                else: A22 += (TR4 - A22) / 22
                if 1 <= i4 <= 14:
                    SP4 += UpM; SQ4 += DnM
                    if i4 == 14: P4 = SP4 / 14; Q4 = SQ4 / 14
                if i4 > 14: P4 += (UpM - P4) / 14; Q4 += (DnM - Q4) / 14
                if i4 >= 14 and A4 > 0:
                    pdi = 100 * P4 / A4; ndi = 100 * Q4 / A4
                    DXv = 100 * abs(pdi - ndi) / (pdi + ndi) if pdi + ndi > 0 else 0.0
                    NDX += 1
                    if NDX <= 14:
                        SDX += DXv
                        if NDX == 14: ADX4 = SDX / 14; ADXok = True
                    else: ADX4 += (DXv - ADX4) / 14
                if i4 >= 21:
                    UB = (H4H + H4L) / 2 + 2 * A22; LB = (H4H + H4L) / 2 - 2 * A22
                    if not STok: FU = UB; FL = LB; STok = True
                    else:
                        if UB < FU or PC4 > FU: FU = UB
                        if LB > FL or PC4 < FL: FL = LB
                    if TrUp and H4C < FL: TrUp = False
                    elif (not TrUp) and H4C > FU: TrUp = True
                    ST4 = FL if TrUp else FU
                PC4 = H4C; PH4 = H4H; PL4 = H4L; Has4 = False
        if dbg is not None: dbg.append((T[i], ST4 if STok else np.nan, A4, ADX4 if ADXok else np.nan, E18, A1, N4))
        # ----- shadow -----
        ShNew = False; ShOut = False
        if ShIn:
            if stops == "1h":
                if (ShS == 1 and L[i] <= ShStop) or (ShS == -1 and H[i] >= ShStop): ShOut = True; why = "stop"; px = min(O[i], ShStop) if ShS == 1 else max(O[i], ShStop)
                elif ShS == -1 and L[i] <= ShTgt: ShOut = True; why = "target"; px = ShTgt
            else:
                for k in range(mstart[i], mend[i]):
                    if (ShS == 1 and ML[k] <= ShStop) or (ShS == -1 and MH[k] >= ShStop):
                        ShOut = True; why = "stop"; px = min(ShStop, MO[k]) if ShS == 1 else max(ShStop, MO[k]); break
                    if ShS == -1 and ML[k] <= ShTgt: ShOut = True; why = "target"; px = ShTgt; break
            if ShOut:
                ShIn = False; shadow.append((ShT, T[i], ShS, ShE, px, why, ShKeep, ShSes, ShRising))
            else:
                if ShS == 1: ShBest = max(ShBest, C[i]); ShStop = max(ShStop, min(ShBest - 3 * A4, C[i] - 0.5 * A1))
                else: ShBest = min(ShBest, C[i]); ShStop = min(ShStop, max(ShBest + 3 * A4, C[i] + 0.5 * A1))
        Sig = 0
        if STok and N4 > 14 and A4 > 0 and N1 >= 14:
            if C[i] > ST4 and C[i] < E18: Sig = 1
            elif C[i] < ST4 and ADXok and ADX4 > 22 and C[i] > E40: Sig = -1
        if (not ShIn) and Sig != 0:
            ShIn = True; ShS = Sig; ShE = C[i]; ShBest = C[i]; ShNew = True; ShT = T[i]
            if Sig == 1: ShStop = C[i] - 1.5 * A4; ShTgt = 0.0
            else: ShStop = C[i] + 0.75 * A4; ShTgt = C[i] - 2.5 * A4
            SesDate = Tdate[i] + np.timedelta64(1, "D") if Ttime[i] >= 1700 else Tdate[i]
            Rising = -1; nr = 0; R0 = RN = 0.0
            for k in range(0, 61):                                     # Date[k] of data2, newest first
                q = d2_end[i] - 1 - k
                if q < 0: break
                if nr <= 20 and D2d[q] < SesDate and D2c[q] > 0:
                    if nr == 0: R0 = D2c[q]
                    if nr == 20: RN = D2c[q]
                    nr += 1
            if nr > 20: Rising = 1 if R0 > RN else 0
            ShKeep = (not UseFilter) or Rising == 0; ShSes = SesDate; ShRising = Rising
        # ----- real orders -----
        mp = pos
        if mp != 0 and ((not ShIn) or (not ShKeep) or (mp == 1 and ShS == -1) or (mp == -1 and ShS == 1)): pend.append(("mkt", 0))
        if ShNew and ShKeep and Qty >= 1:
            pend.append(("entry", 0)); ShS_at_send = ShS; sh_id_at_send = ShT
        if mp == 1 and ShIn and ShKeep and ShS == 1: pend.append(("stop", ShStop))
        if mp == -1 and ShIn and ShKeep and ShS == -1: pend.append(("stop", ShStop)); pend.append(("tgt", ShTgt))
        # MultiCharts: an entry in the same direction while already long is ignored (one entry a direction)
        if mp != 0 and any(k == "entry" for k, _ in pend) and not any(k == "mkt" for k, _ in pend) and ShS_at_send == mp:
            pend = [x for x in pend if x[0] != "entry"]
    S = pd.DataFrame(shadow, columns=["t", "tx", "side", "e", "x", "why", "kept", "ses", "rising"])
    R = pd.DataFrame(real, columns=["entry_time", "exit_time", "side", "entry", "exit", "how", "shadow_t"])
    return S, R


def usd(pts, side, target):   # per MES, as the reference: (pts x 50 - $5 - tick in - tick out unless a limit) / 10 - $0.55
    return (side * pts * PV - COMM - TK - np.where(target, 0.0, TK)) / 10 - 0.55


globals()["ShS_at_send"] = 0; globals()["sh_id_at_send"] = None
if __name__ == "__main__":
    mm, b = load()
    print("1h bars", len(b), b.index[0], "->", b.index[-1])
    for st in ("1h", "1min"):
        S, R = run(mm, b, stops=st)
        S["usd"] = usd(S.x - S.e, S.side, S.why == "target"); R["usd"] = usd(R.exit - R.entry, R.side, R.how == "target")
        S.to_csv(OUT + f"shadow_{st}.csv", index=False); R.to_csv(OUT + f"real_{st}.csv", index=False)
        print(st, "shadow", len(S), "kept", int(S.kept.sum()), "real", len(R), "real $", round(R.usd.sum()))
