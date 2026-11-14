"""Checker replica of personal_strategies/BTC_ADX_Longs.txt (+ PS_UTCOffsetCT): executes the PowerLanguage bar by bar.
data2 = Coinbase spot 1-min (Central, stamped at close) compressed to 15m on LOCAL close stamps (as MultiCharts would),
data1 = CME BTC 1-min (ratio roll-adjusted, as the reference) compressed to 15m on local close stamps.
Modes: MC   = faithful (first calc at data1 bar 3000, ScanMax 2900 catch-up limit)
       WARM = every spot bar processed before the first MBT bar (indicators warmed from the first spot bar, as Python)
Writes paper_<mode>.csv, real_<mode>.csv.  Run from repo root: python3 checks/candidates/mc_btc_adx_longs/replica.py
"""
import glob, math, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
OUT = "checks/candidates/mc_btc_adx_longs/"


def local15(d, extra=()):
    ts = pd.to_datetime(d.date.astype(str) + d.time.astype(str).str.zfill(4), format="%Y%m%d%H%M")
    d = d.assign(key=ts.dt.ceil("15min"))
    agg = dict(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"))
    for e in extra: agg[e] = (e, "last")
    return d.groupby("key", sort=True).agg(**agg)


def utc_off(dt):
    """PS_UTCOffsetCT as written: hours to add to Central to get UTC"""
    Yr, Mo, Dy, tv = dt.year, dt.month, dt.day, dt.hour * 100 + dt.minute
    dow = lambda y, m, dd: (pd.Timestamp(y, m, dd).weekday() + 1) % 7      # PL: Sunday = 0
    ds = 1 + (7 - dow(Yr, 3, 1)) % 7 + 7; de = 1 + (7 - dow(Yr, 11, 1)) % 7
    if 3 < Mo < 11: return 5
    if Mo == 3 and (Dy > ds or (Dy == ds and tv >= 200)): return 5
    if Mo == 11 and (Dy < de or (Dy == de and tv < 200)): return 5
    return 6


def minutes(idx): return idx.values.astype("datetime64[m]").astype(np.int64)


def load_spot():
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/BTCUSD_spot_1min_*.csv"))])
    g = local15(d)
    off = np.array([utc_off(t) for t in g.index])
    return g, minutes(g.index) + off * 60


def load_fut():
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/BTC_1min_*.csv"))])
    ts = pd.to_datetime(d.date.astype(str) + d.time.astype(str).str.zfill(4), format="%Y%m%d%H%M")
    d = d.assign(ct=ts).drop_duplicates("ct").sort_values("ct").reset_index(drop=True)
    brk = np.flatnonzero(d.ct.diff().dt.total_seconds().to_numpy() >= 1800)       # same roll removal as the reference loader
    gap = d.open.to_numpy()[brk] / d.close.to_numpy()[brk - 1] - 1
    B = pd.DataFrame(dict(j=brk, gap=gap, ts=d.ct.to_numpy()[brk])); med = B.gap.abs().median(); f = np.ones(len(d))
    for _, gg in B[(B.ts.dt.day >= 15)].groupby([B.ts.dt.year, B.ts.dt.month]):
        k = gg.gap.abs().idxmax()
        if abs(gg.at[k, "gap"]) > 4 * med: f[:int(gg.at[k, "j"])] *= 1 + gg.at[k, "gap"]
    for c in ("open", "high", "low", "close"): d[c] = d[c] * f
    d["f"] = f
    return local15(d, extra=("f",))


def run(mode, spot, fut, BookQty=1, ScanMax=2900, MBB=3000, fix_ready=False, fix_mono=False, unadj=False):
    S, CKs = spot; F = fut
    SO, SH, SL, SC = (S[k].to_numpy() for k in ("open", "high", "low", "close")); Sloc = S.index.values
    FO, FH, FL, FC, FF = (F[k].to_numpy() for k in ("open", "high", "low", "close", "f")); Floc = F.index.values
    if unadj: FO, FH, FL, FC = FO / FF, FH / FF, FL / FF, FC / FF
    st = dict(LastKey=-1e18, HB=-1, HOp=0, HHi=0, HLo=0, HCl=0, HasH=False, NH=0, PrevC=0, PrevH=0, PrevL=0, A14=0, A10=0, P14=0, Q14=0,
              SA=0, SA10=0, SP=0, SQ=0, ADXv=0, SDX=0, FU=0, FL=0, STv=0, TrUp=True, STok=False, BBW=100, C4B=-1, L4C=0, Has4=False,
              N4=0, EMA4=0, ND=0, VR=0, NextId=0)
    CB = [0.0] * 21; DC = [0.0] * 122
    BkOn = [False] * 3; BkS = [0] * 3; BkStop = [0.0] * 3; BkPt = [0.0] * 3; BkTp = [0.0] * 3; BkHalf = [False] * 3
    BkT = [0] * 3; BkR = [0.0] * 3; BkId = [0] * 3; info = [None] * 3
    RState = [0] * 3; RealId = [0] * 3; StopId = [0] * 3; RR = [0.0] * 3; RStop = [0.0] * 3; StopLive = [False] * 3
    paper, real, openreal, whyp = [], [], [None] * 3, [None] * 3

    def fin_hour():
        i0 = st["NH"]; st["NH"] += 1
        HHi, HLo, HCl = st["HHi"], st["HLo"], st["HCl"]
        if i0 == 0: TRv = HHi - HLo; UpM = 0.0; DnM = 0.0
        else:
            PrevC = st["PrevC"]; TRv = max(HHi - HLo, abs(HHi - PrevC), abs(HLo - PrevC))
            UpM = HHi - st["PrevH"]; DnM = st["PrevL"] - HLo
            v2 = UpM if (UpM > DnM and UpM > 0) else 0.0; v3 = DnM if (DnM > UpM and DnM > 0) else 0.0; UpM, DnM = v2, v3
        if 1 <= i0 <= 14: st["SA"] += TRv; st["SP"] += UpM; st["SQ"] += DnM
        if i0 == 14: st["A14"] = st["SA"] / 14; st["P14"] = st["SP"] / 14; st["Q14"] = st["SQ"] / 14
        if i0 > 14: st["A14"] += (TRv - st["A14"]) / 14; st["P14"] += (UpM - st["P14"]) / 14; st["Q14"] += (DnM - st["Q14"]) / 14
        if 1 <= i0 <= 10: st["SA10"] += TRv
        if i0 == 10: st["A10"] = st["SA10"] / 10
        if i0 > 10: st["A10"] += (TRv - st["A10"]) / 10
        if i0 >= 14 and st["A14"] > 0:
            pdi = 100 * st["P14"] / st["A14"]; ndi = 100 * st["Q14"] / st["A14"]
            DXv = 100 * abs(pdi - ndi) / (pdi + ndi) if pdi + ndi > 0 else 0.0
            if i0 <= 27: st["SDX"] += DXv
            if i0 == 27: st["ADXv"] = st["SDX"] / 14
            if i0 > 27: st["ADXv"] += (DXv - st["ADXv"]) / 14
        if i0 >= 10:
            UB = (HHi + HLo) / 2 + 3 * st["A10"]; LB = (HHi + HLo) / 2 - 3 * st["A10"]
            if not st["STok"]: st["FU"] = UB; st["FL"] = LB; st["STok"] = True
            else:
                if UB < st["FU"] or st["PrevC"] > st["FU"]: st["FU"] = UB
                if LB > st["FL"] or st["PrevC"] < st["FL"]: st["FL"] = LB
            if st["TrUp"] and HCl < st["FL"]: st["TrUp"] = False
            elif (not st["TrUp"]) and HCl > st["FU"]: st["TrUp"] = True
            st["STv"] = st["FL"] if st["TrUp"] else st["FU"]
        for k in range(19, 0, -1): CB[k] = CB[k - 1]
        CB[0] = HCl
        if st["NH"] >= 20:
            smb = sum(CB[:20]) / 20; sqb = sum((x - smb) ** 2 for x in CB[:20]); st["BBW"] = 100 * 4 * math.sqrt(sqb / 20) / smb
        st["PrevC"] = HCl; st["PrevH"] = HHi; st["PrevL"] = HLo
        HB = st["HB"]
        for q4 in (1, 2, 3):
            Do4 = False
            if q4 == 1: Do4 = st["Has4"] and (HB // 4) != st["C4B"]
            if q4 == 2: st["C4B"] = HB // 4; st["L4C"] = HCl; st["Has4"] = True
            if q4 == 3: Do4 = st["Has4"] and HB % 4 == 3
            if Do4:
                st["N4"] += 1
                st["EMA4"] = st["L4C"] if st["N4"] == 1 else st["EMA4"] + 2 / 201 * (st["L4C"] - st["EMA4"])
                if (st["C4B"] * 4) % 24 == 16:
                    for k in range(120, 0, -1): DC[k] = DC[k - 1]
                    DC[0] = st["L4C"]; st["ND"] += 1
                    if st["ND"] >= 121:
                        lr = [math.log(DC[k] / DC[k + 1]) for k in range(120)]
                        m1 = sum(lr[:20]) / 20; m2 = sum(lr) / 120
                        s1 = sum((x - m1) ** 2 for x in lr[:20]); s2 = sum((x - m2) ** 2 for x in lr)
                        st["VR"] = math.sqrt(s1 / 19) / math.sqrt(s2 / 119) if s2 > 0 else 0.0
                st["Has4"] = False
        st["HasH"] = False

    def spot_bar(j):
        ck = int(CKs[j]); ok = ck - 15; oh, hh, ll, cc = SO[j], SH[j], SL[j], SC[j]
        he = (ok % 60 == 45)
        for ps in (1, 2, 3):
            DoFin = False
            if ps == 1: DoFin = st["HasH"] and (ok // 60) != st["HB"]
            if ps == 2:
                if not st["HasH"]: st["HB"] = ok // 60; st["HOp"] = oh; st["HHi"] = hh; st["HLo"] = ll; st["HasH"] = True
                else:
                    if hh > st["HHi"]: st["HHi"] = hh
                    if ll < st["HLo"]: st["HLo"] = ll
                st["HCl"] = cc
            if ps == 3: DoFin = he and st["HasH"]
            if DoFin: fin_hour()
        lt = 0
        if he and st["N4"] >= 200: lt = 1 if cc > st["EMA4"] else -1
        gHit = False

        def close(b, why): BkOn[b] = False; paper.append(info[b] + (ok, why))
        if BkOn[1] or BkOn[2]:
            gs = BkS[1] if BkOn[1] else BkS[2]
            if gs == 1: g = min(BkStop[b] for b in (1, 2) if BkOn[b]) * 0.99; gHit = ll <= g
            else: g = max(BkStop[b] for b in (1, 2) if BkOn[b]) * 1.01; gHit = hh >= g
            if gHit:
                for b in (1, 2):
                    if BkOn[b]: close(b, "guard")
        if not gHit:
            for b in (1, 2):
                if BkOn[b]:
                    s = BkS[b]
                    if (s == 1 and ll <= BkStop[b]) or (s == -1 and hh >= BkStop[b]): close(b, "stop")
                    elif (s == 1 and hh >= BkTp[b]) or (s == -1 and ll <= BkTp[b]): close(b, "tp")
                    else:
                        if (not BkHalf[b]) and ((s == 1 and hh >= BkPt[b]) or (s == -1 and ll <= BkPt[b])): BkHalf[b] = True
                        emax = he and lt == -s
                        if ok - BkT[b] >= 240 * 60 or emax: close(b, "ema" if emax else "time")
            Ready = he and st["NH"] >= 61 and st["N4"] >= 200 and st["STok"] and (st["ND"] >= 121 or not fix_ready)
            if Ready:
                side = lt
                if (cc > st["STv"] and lt != 1) or (cc <= st["STv"] and lt != -1): side = 0
                if st["BBW"] >= 15: side = 0
                if side != 0 and st["ND"] >= 121 and st["VR"] >= 1.5: side = 0
                net = sum(BkS[b] for b in (1, 2) if BkOn[b])
                if side != 0 and net * side >= 0:
                    for b in (1, 2):
                        lvl = 40 if b == 1 else 50
                        if (not BkOn[b]) and st["ADXv"] > lvl:
                            st["NextId"] += 1; A14 = st["A14"]
                            BkOn[b] = True; BkS[b] = side; BkStop[b] = cc - side * 2.5 * A14; BkPt[b] = cc + side * 1.5 * A14
                            BkTp[b] = cc + side * 8 * A14; BkHalf[b] = False; BkT[b] = ok; BkR[b] = 2.5 * A14 / cc; BkId[b] = st["NextId"]
                            info[b] = (ok, side, lvl, cc, BkR[b], st["NextId"])
        st["LastKey"] = ck

    p_end = np.searchsorted(Sloc, Floc, side="right")       # data2 bars with a local stamp <= this data1 bar's stamp
    first = MBB if mode == "MC" else 0
    if mode == "WARM":
        for j in range(p_end[first]): spot_bar(j)
    pend = []
    for i in range(first, len(Floc)):
        O, H, L, C = FO[i], FH[i], FL[i], FC[i]
        for kind, b, px in pend:                              # the engine: fills of the orders sent at bar i-1
            if kind == "buy": openreal[b] = dict(et=Floc[i], ep=O, fac=FF[i], id=RealId[b])
            elif kind == "mkt":
                real.append((openreal[b]["et"], Floc[i], b, openreal[b]["ep"], O, openreal[b]["fac"], whyp[b], openreal[b]["id"])); openreal[b] = None
            elif kind == "stop" and L <= px:
                real.append((openreal[b]["et"], Floc[i], b, openreal[b]["ep"], min(O, px), openreal[b]["fac"], "stop", openreal[b]["id"])); openreal[b] = None
        pend = []
        for b in (1, 2):                                      # the .txt from here
            if RState[b] == 2 and StopLive[b] and L <= RStop[b]: RState[b] = 0; StopId[b] = RealId[b]
            if RState[b] == 1: RState[b] = 2; RStop[b] = O * (1 - RR[b]); StopLive[b] = False
        jnew = p_end[i] - 1; j = jnew
        while j >= 0 and (jnew - j) <= ScanMax and CKs[j] > st["LastKey"]: j -= 1
        for jj in range(j + 1, jnew + 1):
            if fix_mono and CKs[jj] <= st["LastKey"]: continue
            spot_bar(jj)
        for b in (1, 2):
            WantId = BkId[b] if (BkOn[b] and BkS[b] == 1) else 0
            if RState[b] == 2 and RealId[b] != WantId:
                if WantId > 0: RealId[b] = WantId; RR[b] = BkR[b]; RStop[b] = C * (1 - RR[b]); openreal[b]["kept"] = openreal[b].get("kept", 0) + 1
                else: pend.append(("mkt", b, 0)); whyp[b] = "out"; RState[b] = 0
            if RState[b] == 2 and (not StopLive[b]) and L <= RStop[b]:
                pend.append(("mkt", b, 0)); whyp[b] = "entrybar_guard"; RState[b] = 0; StopId[b] = RealId[b]
            if RState[b] == 0 and WantId > 0 and WantId != RealId[b] and WantId != StopId[b]:
                RealId[b] = WantId
                if BookQty >= 1: pend.append(("buy", b, 0)); RState[b] = 1; RR[b] = BkR[b]
            if RState[b] == 2: pend.append(("stop", b, RStop[b])); StopLive[b] = True
    P = pd.DataFrame(paper, columns=["t_min", "side", "book", "e", "R", "id", "tx_min", "why"])
    P["t"] = pd.to_datetime(P.t_min, unit="m"); P["tx"] = pd.to_datetime(P.tx_min, unit="m")
    Rl = pd.DataFrame(real, columns=["entry_time", "exit_time", "bookslot", "entry", "exit", "fac", "why", "id"])
    return P, Rl


MULT, TICK, COMM = 0.1, 5.0, 2.5
def usd(R): return ((R.exit - TICK) - (R.entry + TICK)) / R.entry * (R.entry / R.fac) * MULT - COMM


if __name__ == "__main__":
    spot = load_spot(); fut = load_fut()
    print("spot 15m bars", len(spot[0]), "fut 15m bars", len(fut))
    for mode in ("MC", "WARM"):
        P, Rl = run(mode, spot, fut)
        Rl["pnl"] = usd(Rl)
        P.to_csv(OUT + f"paper_{mode}.csv", index=False); Rl.to_csv(OUT + f"real_{mode}.csv", index=False)
        print(mode, "paper trades", len(P), "real trades", len(Rl), "real $", round(Rl.pnl.sum()), "first real", Rl.entry_time.min())
