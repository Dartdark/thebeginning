"""Checker's independent replica of Twin_Continuation.txt (MultiCharts, IOG off, 1-min, close-stamped CT).

Bar-by-bar port: at each bar the pending orders (created at the previous bar's close) are filled first, then the
script runs on the closed bar with MarketPosition after those fills; 'this bar on close' exits fill at the bar close.
Costs: $7.25 commission per round trip + $5 (1 tick) per market/stop fill; limit target at the limit, no slippage.

  python3 replica.py [key=value ...]   -> writes trades_replica.csv (or trades_replica_<tag>.csv with tag=...)
Extra (non-code) switches: limit_through=1 (target needs a 1-tick trade-through), both_stops='first'.
"""
import sys, os, pickle, math
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "analysis"))

P = dict(UseBreakout=1, UseMomentum=1, BO_TargetMult=2.0, BO_MaxStopMult=0.0, BO_ATRPeriod=14, BO_VolCap=2.0,
         BO_VolLookback=50, BO_SessionOpen=1700, BO_SessionClose=1600, BO_LastFill=1530, BO_ExitTime=1545,
         BO_PivotTF=360, MO_BasisLen=21, MO_RangeLen=14, MO_SignalLen=3, MO_Trigger=100.0, MO_WindowStart=840,
         MO_WindowEnd=930, MO_ExitTime=1450, MO_StopPoints=75.0, MO_Warmup=60, MO_FullBarsOnly=1,
         MO_AllowLong=1, MO_AllowShort=1, limit_through=0, tag="")

COMM, SLIP, PV, TICK = 7.25, 5.0, 20.0, 0.25


def t2m(t): return (t // 100) * 60 + t % 100
def m2t(m): m %= 1440; return (m // 60) * 100 + m % 60


def load_bars():
    import grid24  # noqa
    g = pickle.load(open(os.path.join(HERE, "..", "..", "..", "scratch_data", "g24.pkl"), "rb"))
    rows, cols = np.where(np.isfinite(g.c))
    order = np.lexsort((cols, rows))
    rows, cols = rows[order], cols[order]
    return (g.dates[rows], cols, g.o[rows, cols], g.h[rows, cols], g.l[rows, cols], g.c[rows, cols])


def run(p, bars):
    D, J, O, H, L, C = bars
    n = len(D)
    ts = pd.to_datetime(pd.Series(D).astype(str))
    MON = ts.dt.month.to_numpy(); DOM = ts.dt.day.to_numpy(); DOW = ts.dt.dayofweek.to_numpy()  # Mon=0, Fri=4
    half = ((MON == 7) & (DOM == 3)) | ((MON == 12) & (DOM == 24)) | ((MON == 11) & (DOW == 4) & (DOM >= 23) & (DOM <= 29))

    sess_start = t2m(p["BO_SessionOpen"])
    SessEndSm = (t2m(p["BO_SessionClose"]) - sess_start + 1440) % 1440
    FillEndSm = (t2m(p["BO_LastFill"]) - sess_start + 1440) % 1440
    FlatSm = (t2m(p["BO_ExitTime"]) - sess_start + 1440) % 1440
    TF = int(p["BO_PivotTF"]); ATRP = int(p["BO_ATRPeriod"]); TM = p["BO_TargetMult"]
    aP = 2 / (p["MO_BasisLen"] + 1); aO = 2 / (p["MO_SignalLen"] + 1); RL = p["MO_RangeLen"]
    TRIG = p["MO_Trigger"]; WS, WE = p["MO_WindowStart"], p["MO_WindowEnd"]; XT = p["MO_ExitTime"]; MSTP = p["MO_StopPoints"]
    VL = int(min(max(p["BO_VolLookback"], 1), 99))

    # --- BO state
    PrevSm = -1; PrevBkt = -1; PrevHIdx = -1
    SessRng = []; NSess = 0; VolRatio = 0.0; SHi = SLo = 0.0
    BarOpen = False; B15H = B15L = B15C = B15LastH = B15LastL = 0.0; B15LastSm = 0
    CanOpen = False; CurH = CurL = 0.0; NC = 0; CanH = [0.0] * 7; CanL = [0.0] * 7
    PrevC15 = 0.0; TrN = 0; TrSum = 0.0; AtrV = 0.0
    GotSwH = GotSwL = False; NewSwH = NewSwL = 0.0
    SwH = SwL = LastSwH = LastSwL = 0.0; HaveSwH = HaveSwL = False; SwHOpen = SwLOpen = False
    Armed = OkL = OkS = False; LvlL = LvlS = StpL = StpS = AtrU = 0.0; ArmTrades = 0
    # --- MO state
    SPrevBk = -1; SBkDate = 0; SOpen = False; SH = SL_ = SC = 0.0; SN = 0; SEndT = 0
    SNB = 0; SPrevC = 0.0; SatrW = 0.0; SPivot = 0.0; SOscV = SOscPrev = 0.0; SHaveOsc = SHavePrev = False
    STraded = False; SLastDate = 0
    # --- position / orders
    pos = 0; setup = None; ep = 0.0; ei = -1; total = 0; elvl = np.nan
    o_mkt_entry = 0                 # +1/-1 MO market entry for this bar
    o_bo = []                       # [(side, price)] BO stop entries
    o_exit = None                   # dict for exits of current position
    trades = []; both_hits = 0; diag = []

    def close_trade(i, px, kind):
        nonlocal pos, setup, total
        pts = (px - ep) * pos
        cost = COMM + SLIP + (0.0 if kind == "limit" else SLIP)
        trades.append((D[i], pos, pts * PV - cost, setup, D[ei], J[ei], J[i], ep, px, kind, pts, elvl))
        pos = 0; setup = None; total += 1

    for i in range(n):
        o, h, l, c = O[i], H[i], L[i], C[i]
        # ================= fills on this bar (orders from the previous bar's close) =================
        if pos != 0 and o_exit is not None:
            x = o_exit
            if x.get("mkt"):
                close_trade(i, o, "mkt")
            else:
                stp = x.get("stop"); lim = x.get("limit")
                lt = p["limit_through"] * TICK
                if pos == 1:
                    if lim is not None and o >= lim: close_trade(i, o, "limit")
                    elif stp is not None and o <= stp: close_trade(i, o, "stop")
                    elif stp is not None and l <= stp: close_trade(i, stp, "stop")
                    elif lim is not None and h >= lim + lt: close_trade(i, lim, "limit")
                else:
                    if lim is not None and o <= lim: close_trade(i, o, "limit")
                    elif stp is not None and o >= stp: close_trade(i, o, "stop")
                    elif stp is not None and h >= stp: close_trade(i, stp, "stop")
                    elif lim is not None and l <= lim - lt: close_trade(i, lim, "limit")
        o_exit = None
        if pos == 0:
            if o_mkt_entry != 0:
                pos = o_mkt_entry; setup = "MO"; ep = o; ei = i; elvl = np.nan
            elif o_bo:
                hits = []
                for side, px in o_bo:
                    if side == 1 and h >= px: hits.append((side, max(o, px), px))
                    if side == -1 and l <= px: hits.append((side, min(o, px), px))
                if hits:
                    if len(hits) == 2:
                        both_hits += 1
                        # MC intrabar path: O-H-L-C if open nearer the high, else O-L-H-C
                        first = 1 if (h - o) <= (o - l) else -1
                        hits = [x for x in hits if x[0] == first]
                    pos, ep, elvl = hits[0]; setup = "BO"; ei = i
        o_mkt_entry = 0; o_bo = []

        # ================= script on the closed bar =================
        tm = J[i]
        TimeC = m2t(tm)
        SmNow = (tm - 1 - sess_start + 2880) % 1440
        NewSess = PrevSm < 0 or SmNow < PrevSm
        Bkt = SmNow // 15; HIdx = SmNow // TF
        NewBkt = NewSess or Bkt != PrevBkt; NewCan = NewSess or HIdx != PrevHIdx
        if NewSess:
            if PrevSm >= 0 and SHi > SLo:
                SessRng.insert(0, SHi - SLo); del SessRng[100:]
                NSess += 1; VolRatio = 0.0
                if NSess > VL:
                    s = sum(SessRng[1:VL + 1])
                    if s > 0: VolRatio = SessRng[0] / (s / VL)
            SHi, SLo = h, l
        else:
            SHi = max(SHi, h); SLo = min(SLo, l)

        LateCan = NewCan and CanOpen; LateBar = NewBkt and BarOpen
        for K in (1, 2):
            if K == 1:
                DoCan, DoBar = LateCan, LateBar
            else:
                if NewCan: CurH, CurL, CanOpen = h, l, True
                else: CurH = max(CurH, h); CurL = min(CurL, l)
                if NewBkt: B15H, B15L, BarOpen = h, l, True
                else: B15H = max(B15H, h); B15L = min(B15L, l)
                B15C = c; B15LastH = h; B15LastL = l; B15LastSm = SmNow
                if SwHOpen and h >= SwH: SwHOpen = False
                if SwLOpen and l <= SwL: SwLOpen = False
                DoCan = CanOpen and ((SmNow + 1) % TF == 0 or SmNow + 1 >= SessEndSm)
                DoBar = BarOpen and (SmNow + 1) % 15 == 0
            if DoCan:
                CanOpen = False
                CanH = [CurH] + CanH[:6]; CanL = [CurL] + CanL[:6]
                NC += 1
                if NC >= 7:
                    if CanH[3] >= max(CanH[4], CanH[5], CanH[6]) and CanH[3] >= max(CanH[0], CanH[1], CanH[2]):
                        GotSwH = True; NewSwH = CanH[3]
                    if CanL[3] <= min(CanL[4], CanL[5], CanL[6]) and CanL[3] <= min(CanL[0], CanL[1], CanL[2]):
                        GotSwL = True; NewSwL = CanL[3]
            if DoBar:
                BarOpen = False
                TRv = B15H - B15L if TrN == 0 else max(B15H, PrevC15) - min(B15L, PrevC15)
                TrN += 1
                if TrN <= ATRP:
                    TrSum += TRv
                    if TrN == ATRP: AtrV = TrSum / ATRP
                else:
                    AtrV = (AtrV * (ATRP - 1) + TRv) / ATRP
                PrevC15 = B15C
                if GotSwH:
                    SwH = LastSwH = NewSwH; HaveSwH = True
                    SwHOpen = B15C < SwH and B15LastH < SwH; GotSwH = False
                if GotSwL:
                    SwL = LastSwL = NewSwL; HaveSwL = True
                    SwLOpen = B15C > SwL and B15LastL > SwL; GotSwL = False
                Armed = False
                if pos == 0 and TrN >= ATRP:
                    AtrU = AtrV
                    LvlL = SwH; StpL = LastSwL; LvlS = SwL; StpS = LastSwH
                    OkL = SwHOpen and HaveSwL and StpL < LvlL
                    OkS = SwLOpen and HaveSwH and StpS > LvlS
                    Armed = bool(p["UseBreakout"]) and (OkL or OkS) and B15LastSm < FillEndSm - 1
                    if p["BO_VolCap"] > 0 and VolRatio > p["BO_VolCap"]: Armed = False
                    ArmTrades = total
        PrevSm, PrevBkt, PrevHIdx = SmNow, Bkt, HIdx

        # ---- MO
        on_close_exit = False
        date = D[i]
        if date != SLastDate:
            STraded = False
            if SLastDate != 0 and setup == "MO": on_close_exit = True
            SLastDate = date
        SStartMin = (tm - 1 + 1440) % 1440
        SBk = SStartMin // 10
        SNewBk = SBk != SPrevBk or date != SBkDate
        SLate = SNewBk and SOpen
        SFire = 0
        for K in (1, 2):
            if K == 1:
                SDo = SLate; FH, FL, FC, FN, FEndT = SH, SL_, SC, SN, SEndT
            else:
                if SNewBk: SH, SL_, SN, SOpen, SBkDate = h, l, 1, True, date
                else: SH = max(SH, h); SL_ = min(SL_, l); SN += 1
                SC = c
                SEndT = m2t((SBk + 1) * 10)
                if SBk == 143: SEndT = 0
                SDo = SOpen and (SStartMin + 1) % 10 == 0
                FH, FL, FC, FN, FEndT = SH, SL_, SC, SN, SEndT
            if SDo:
                SOpen = False; SNB += 1
                if SNB == 1:
                    Strv = FH - FL; SatrW = Strv; SPivot = FC
                else:
                    Strv = max(FH - FL, abs(FH - SPrevC), abs(FL - SPrevC))
                    SatrW = SatrW + (Strv - SatrW) / RL
                    SPivot = SPivot + (FC - SPivot) * aP
                SPrevC = FC
                SSide = 0
                if SatrW > 0:
                    SRaw = (FC - SPivot) / (3 * SatrW) * 100
                    if not SHaveOsc:
                        SOscV = SRaw; SHaveOsc = True
                    else:
                        SOscPrev = SOscV; SHavePrev = True
                        SOscV = SOscV + (SRaw - SOscV) * aO
                    if SHavePrev:
                        if SOscV > TRIG and SOscPrev <= TRIG: SSide = 1
                        elif SOscV < -TRIG and SOscPrev >= -TRIG: SSide = -1
                if (SSide != 0 and WS <= FEndT <= WE and (not p["MO_FullBarsOnly"] or FN == 10)
                        and not STraded and not half[i] and pos == 0 and SNB >= p["MO_Warmup"]):
                    STraded = True
                    if p["UseMomentum"]:
                        if SSide == 1 and p["MO_AllowLong"]: SFire = 1
                        if SSide == -1 and p["MO_AllowShort"]: SFire = -1
                    diag.append((date, FEndT, TimeC, SSide))
        SPrevBk = SBk

        if SFire != 0:
            Armed = False; o_mkt_entry = SFire
        # MO exits
        if pos != 0 and setup == "MO":
            o_exit = {"stop": ep - MSTP if pos == 1 else ep + MSTP}
            if XT <= TimeC <= 1600: o_exit = {"mkt": True}
        # BO entries
        if Armed and (pos != 0 or total > ArmTrades): Armed = False
        if Armed and pos == 0 and SmNow + 1 < FillEndSm:
            if OkL: o_bo.append((1, LvlL))
            if OkS: o_bo.append((-1, LvlS))
        # BO exits
        if pos != 0 and setup == "BO":
            if pos == 1:
                if StpL >= ep: o_exit = {"mkt": True}
                else: o_exit = {"stop": StpL, "limit": ep + TM * AtrU if TM > 0 else None}
            else:
                if StpS <= ep: o_exit = {"mkt": True}
                else: o_exit = {"stop": StpS, "limit": ep - TM * AtrU if TM > 0 else None}
            if SmNow + 1 >= FlatSm and SmNow < SessEndSm: on_close_exit = True
        # SetExitOnClose: last bar of the session template (16:00)
        if pos != 0 and SmNow == SessEndSm - 1: on_close_exit = True
        if on_close_exit and pos != 0:
            close_trade(i, c, "close"); o_exit = None
    cols = ["date", "side", "net", "setup", "entry_d", "entry_j", "exit_j", "entry", "exit", "kind", "pts", "level"]
    T = pd.DataFrame(trades, columns=cols)
    T["date"] = pd.to_datetime(T.date.astype(str)).dt.strftime("%Y-%m-%d")
    T["entry_date"] = pd.to_datetime(T.entry_d.astype(str)).dt.strftime("%Y-%m-%d")
    T["entry_time_ct"] = T.entry_j.map(m2t); T["exit_time_ct"] = T.exit_j.map(m2t)
    T = T[["date", "side", "net", "setup", "entry_date", "entry_time_ct", "exit_time_ct", "entry", "exit", "kind", "pts", "level"]]
    T.attrs["both_hits"] = both_hits
    return T


if __name__ == "__main__":
    p = dict(P)
    for a in sys.argv[1:]:
        k, v = a.split("=")
        p[k] = v if k == "tag" else float(v)
    bars = load_bars()
    T = run(p, bars)
    T = T[T.date >= "2018-01-01"]
    fn = "trades_replica%s.csv" % ("_" + p["tag"] if p["tag"] else "")
    T.to_csv(os.path.join(HERE, fn), index=False)
    print(fn, len(T), "trades, net $%.0f, both-stop bars %d" % (T.net.sum(), T.attrs.get("both_hits", 0)))
