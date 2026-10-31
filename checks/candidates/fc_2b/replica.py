"""Checker replica of FC 2B v2 (Flow-Confirmed Opening Drive), rebuilt from FC_2B_v2.txt alone.

Bar convention: data/NQ_1min_*.csv times are bar-close stamps (as in MultiCharts), Central time. The chart is the
08:30-15:00 CT day session, so only bars stamped 08:31-15:00 are used.
  Opening range   bars 08:31-09:00; signal on the first bar stamped >= 09:00; entry at the next bar's open.
  Flow ratio      sum V*(C-O)/max(H-L, 1 tick) / sum V; z vs the previous min(count, 60) ratios (population sd),
                  needs >= 20 previous days; long if OR close > OR open and z >= 1, short if < and z <= -1.
  Exits (v2)      backstop SetStopLoss at entry -/+ 100 pts from the entry bar on; from the bar after entry a stop at
                  max(entry-100, hh-150, entry+4 ticks once High >= entry+66) (mirror for shorts), hh starting at the
                  signal bar's close; if that stop is through the bar close -> market exit next open; flatten at the
                  next open after the bar stamped >= 14:58 (11:30 on the CME holiday half-days of the code's list).
  v1 exits        (--v1) no backstop, no through-the-close guard, no holiday flatten; SetExitOnClose at the session's
                  last bar close.
  Costs           $7.25 + 1 tick ($5) per fill (entry market + exit stop/market) = $17.25 a round trip.
  --randside=SEED placebo: trade the same signal days with a random side.
  --scale=REF     stop and trail scaled by entry price / REF (points at REF), a robustness check.
  --upvol         replace volume by an up-tick volume proxy (volume on up bars only) to see the sensitivity of z.
  python3 checks/candidates/fc_2b/replica.py [--v1] [--out FILE]
"""
import sys, glob, numpy as np, pandas as pd

PV, TICK, COST = 20.0, 0.25, 7.25 + 2 * 0.25 * 20.0
V1 = "--v1" in sys.argv
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
P = dict(ZMin=1.0, ZLookback=60, MinWarmup=20, SL=100.0, Trail=150.0, BER=0.66, ExitTime=1458, Early=1130)
for a in sys.argv:
    if a.startswith("--") and "=" in a and a[2:].split("=")[0] in P:
        k, v = a[2:].split("="); P[k] = type(P[k])(float(v))


RS = None
REF = next((float(a.split("=")[1]) for a in sys.argv if a.startswith("--scale=")), None)   # stop/trail scaled to price/REF
for a in sys.argv:
    if a.startswith("--randside="): RS = np.random.default_rng(int(a.split("=")[1]))


def early_close(d):
    m, dd, dow, y = d.month, d.day, d.isoweekday() % 7, d.year      # MC DayOfWeek: 0 = Sunday .. 6 = Saturday
    wk = 1 <= dow <= 5
    return ((m == 1 and ((dd == 1 and wk) or (dd == 2 and dow == 1)))
            or (m == 1 and dow == 1 and 15 <= dd <= 21) or (m == 2 and dow == 1 and 15 <= dd <= 21)
            or (m == 5 and dow == 1 and dd >= 25)
            or (m == 6 and y >= 2022 and ((dd == 19 and wk) or (dd == 18 and dow == 5) or (dd == 20 and dow == 1)))
            or (m == 7 and (((dd == 3 or dd == 4) and wk) or (dd == 5 and dow == 1)))
            or (m == 9 and dow == 1 and dd <= 7)
            or (m == 11 and dow == 4 and 22 <= dd <= 28) or (m == 11 and dow == 5 and 23 <= dd <= 29)
            or (m == 12 and (((dd == 24 or dd == 25) and wk) or (dd == 26 and dow == 1))))


def load():
    df = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/NQ_1min_20*.csv")) if "_ON_" not in f])
    df = df[(df.time > 830) & (df.time <= 1500)].sort_values(["date", "time"]).reset_index(drop=True)
    if "--upvol" in sys.argv:
        df["volume"] = np.where(df.close > df.open, df.volume, np.where(df.close == df.open, df.volume / 2, 0.0))
    return df


def run(df):
    D = df.date.to_numpy(); T = df.time.to_numpy(); O = df.open.to_numpy(); H = df.high.to_numpy()
    L = df.low.to_numpy(); C = df.close.to_numpy(); V = df.volume.to_numpy().astype(float)
    bd = V * (C - O) / np.maximum(H - L, TICK)
    flow = []; trades = []; sigs = []
    pos = 0; ep = 0.0; hh = ll = 0.0; be = False; ent_i = -1
    pend = None              # pending order for the next bar: ('entry', dir) / ('mkt', tag) / ('stop', price, tag)
    cur = None; orO = orC = 0.0; orN = 0; orD = orV = 0.0; done = False; dayexit = P["ExitTime"]
    n = len(df)
    for i in range(n):
        newday = i == 0 or D[i] != D[i - 1]
        # ---------------- fills at this bar (orders placed at the previous bar's close)
        if pend is not None:
            if pend[0] == "entry":
                pos = pend[1]; ep = O[i]; ent_i = i; pend = None
                f = ep / REF if REF else 1.0; SLx, TRx = P["SL"] * f, P["Trail"] * f
            elif pos != 0:
                px = None
                if pend[0] == "mkt": px, tag = O[i], pend[1]
                elif pend[0] == "stop":
                    s = pend[1]; tag = pend[2]
                    if pos == 1 and L[i] <= s: px = min(O[i], s)
                    if pos == -1 and H[i] >= s: px = max(O[i], s)
                elif pend[0] == "both":     # market EOD order + stop order on the same bar: market fills at the open
                    px, tag = O[i], pend[1]
                if px is not None:
                    trades.append((D[ent_i], pos, ep, px, tag, T[ent_i], T[i], D[i])); pos = 0
                pend = None
        # backstop SetStopLoss: active on every bar in position incl. the entry bar (v2 only)
        if not V1 and pos != 0:
            s = ep - pos * SLx
            if (pos == 1 and L[i] <= s) or (pos == -1 and H[i] >= s):
                px = min(O[i], s) if pos == 1 else max(O[i], s)
                if i == ent_i: px = s           # entry bar: the open is the entry, so the stop fills at its price
                trades.append((D[ent_i], pos, ep, px, "backstop", T[ent_i], T[i], D[i])); pos = 0
        # ---------------- bar-close logic (the PowerLanguage script)
        if newday:
            orN = 0; orD = orV = 0.0; done = False
            d = pd.Timestamp(str(D[i]))
            dayexit = P["Early"] if (not V1 and early_close(d)) else P["ExitTime"]
        if 830 < T[i] <= 900:
            if orN == 0: orO = O[i]
            orC = C[i]; orN += 1; orD += bd[i]; orV += V[i]
        if not done and T[i] >= 900 and orN > 0:
            done = True
            ratio = orD / max(orV, 1.0)
            warm = len(flow) >= P["MinWarmup"]
            k = min(len(flow), int(P["ZLookback"])); z = 0.0
            if k >= 2:
                b = np.array(flow[-k:]); mu = b.mean(); vr = (b * b).mean() - mu * mu
                if vr > 0: z = (ratio - mu) / np.sqrt(vr)
            flow.append(ratio)
            dr = 1 if orC > orO else (-1 if orC < orO else 0)
            ok = warm and dr != 0 and pos == 0 and ((dr == 1 and z >= P["ZMin"]) or (dr == -1 and z <= -P["ZMin"]))
            sigs.append((D[i], ratio, z, dr, int(ok)))
            if ok and RS is not None: dr = int(RS.choice([-1, 1]))       # placebo: same days, random side
            if ok:
                be = False
                if dr == 1: hh = C[i]
                else: ll = C[i]
                pend = ("entry", dr)
        if pos == 1 and i != -1:
            hh = max(hh, H[i]); st = ep - SLx
            if P["Trail"] > 0: st = max(st, hh - TRx)
            if P["BER"] > 0:
                if not be and H[i] >= ep + P["BER"] * SLx: be = True
                if be: st = max(st, ep + 4 * TICK)
            pend = ("mkt", "LX.mkt") if (not V1 and st >= C[i]) else ("stop", st, "LX.stp")
        if pos == -1:
            ll = min(ll, L[i]); st = ep + SLx
            if P["Trail"] > 0: st = min(st, ll + TRx)
            if P["BER"] > 0:
                if not be and L[i] <= ep - P["BER"] * SLx: be = True
                if be: st = min(st, ep - 4 * TICK)
            pend = ("mkt", "SX.mkt") if (not V1 and st <= C[i]) else ("stop", st, "SX.stp")
        if T[i] >= dayexit and pos != 0:
            pend = ("both", "eod") if pend is not None and pend[0] == "stop" else ("mkt", "eod")
        # v1 SetExitOnClose: flat at the close of the session's last bar
        if V1 and pos != 0 and (i == n - 1 or D[i + 1] != D[i]):
            trades.append((D[ent_i], pos, ep, C[i], "eoc", T[ent_i], T[i], D[i])); pos = 0; pend = None
    t = pd.DataFrame(trades, columns=["date", "side", "entry", "exit", "kind", "t_in", "t_out", "exit_date"])
    t["date"] = pd.to_datetime(t.date.astype(str)); t["exit_date"] = pd.to_datetime(t.exit_date.astype(str))
    t["gross"] = (t.exit - t.entry) * t.side * PV; t["net"] = t.gross - COST
    s = pd.DataFrame(sigs, columns=["date", "ratio", "z", "dir", "ok"]); s["date"] = pd.to_datetime(s.date.astype(str))
    return t, s


if __name__ == "__main__":
    t, s = run(load())
    out = OUT or ("checks/candidates/fc_2b/replica_v1_trades.csv" if V1 else "checks/candidates/fc_2b/replica_trades.csv")
    t.to_csv(out, index=False); s.to_csv(out.replace("trades", "signals") if "trades" in out else out + ".signals.csv", index=False)
    x = t[t.date >= "2018-01-01"]
    print(f"{out}: {len(x)} trades 2018+, net ${x.net.sum():,.0f}, avg ${x.net.mean():.1f}, by kind {x.kind.value_counts().to_dict()}")
    print(x.groupby(x.date.dt.year).net.agg(["count", "sum", "mean"]).round(0).to_string())
