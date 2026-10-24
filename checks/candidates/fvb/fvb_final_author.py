"""
FVB Strategy — Final Production Backtest
==========================================
First Valid Breakout: morning breakout of prior-day / premarket levels,
hold to close with ATR-based stop.

Auto-discovers all instruments in DATA_DIR.
Runs full IS+OOS with costs ($4.12 RT + 1 tick slippage).
Produces per-instrument equity curve PNG + trades CSV,
cross-instrument summary table + overlay chart.

LOCKED CONFIG (validated Phase 1-7 on NQ):
  stop_frac       = 0.18  (18% of 14-day ATR)
  entry_window    = 120   (9:30-11:30 ET for equity indices)
  max_trades/day  = 2     (re-entry only after stop)
  VP2 threshold   = 0.03  (3% ATR confluence)
  VP2 size mult   = 1.5x  (cosmetic — affects weighted R only)

Usage:
  python fvb_final.py

To change periods, costs, or instruments, edit the CONFIGURE section below.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import os, sys, glob, time, shutil, warnings
warnings.filterwarnings("ignore")


# ════════════════════════════════════════════════════════════
# CONFIGURE
# ════════════════════════════════════════════════════════════
DATA_DIR       = r"C:\Market Data"
WARMUP_START   = "2017-11-01"
IS_START       = "2018-01-01"
IS_END         = "2023-12-31"
OOS_START      = "2024-01-01"
OOS_END        = "2025-12-31"

COMMISSION_RT  = 4.12       # dollars per round-trip per contract
SLIPPAGE_TICKS = 1          # ticks per side (applied both sides)

# Set to a list of tickers to restrict, or None to run all found files
TICKER_FILTER  = None       # e.g. ["NQ", "ES", "YM"]


# ════════════════════════════════════════════════════════════
# LOCKED PARAMETERS
# ════════════════════════════════════════════════════════════
STOP_FRAC              = 0.18
ENTRY_WINDOW           = 120      # minutes from RTH open
MAX_PRIOR_RANGE_ATR    = 1.5
MAX_PM_RANGE_ATR       = 1.0
STRONG_TREND_THRESHOLD = 0.60
MAX_TRADES_PER_DAY     = 2
VP_VALUE_AREA_PCT      = 0.70
VP2_THRESHOLD          = 0.03
VP2_SIZE_MULT          = 1.5


# ════════════════════════════════════════════════════════════
# INSTRUMENT SPECS
# ════════════════════════════════════════════════════════════
# tick = minimum price increment
# dpp  = dollar value per full point move (1 contract)
# rth_start/end, pm_start/end, night_start = minutes from midnight ET
# force_close = EOD exit time (minutes from midnight ET)
INST_SPECS = {
    # ── Equity indices ───────────────────────────────────────
    "NQ":  {"tick": 0.25,   "dpp": 20.0,    "rth_start": 570, "rth_end": 975, "force_close": 970, "pm_start": 240, "pm_end": 570, "night_start": 1080},
    "ES":  {"tick": 0.25,   "dpp": 50.0,    "rth_start": 570, "rth_end": 975, "force_close": 970, "pm_start": 240, "pm_end": 570, "night_start": 1080},
    "YM":  {"tick": 1.0,    "dpp": 5.0,     "rth_start": 570, "rth_end": 975, "force_close": 970, "pm_start": 240, "pm_end": 570, "night_start": 1080},
    "RTY": {"tick": 0.10,   "dpp": 50.0,    "rth_start": 570, "rth_end": 975, "force_close": 970, "pm_start": 240, "pm_end": 570, "night_start": 1080},
    # ── Micros ───────────────────────────────────────────────
    "MNQ": {"tick": 0.25,   "dpp": 2.0,     "rth_start": 570, "rth_end": 975, "force_close": 970, "pm_start": 240, "pm_end": 570, "night_start": 1080},
    "MES": {"tick": 0.25,   "dpp": 5.0,     "rth_start": 570, "rth_end": 975, "force_close": 970, "pm_start": 240, "pm_end": 570, "night_start": 1080},
    "M2K": {"tick": 0.10,   "dpp": 5.0,     "rth_start": 570, "rth_end": 975, "force_close": 970, "pm_start": 240, "pm_end": 570, "night_start": 1080},
    # ── Metals (COMEX) ───────────────────────────────────────
    "GC":  {"tick": 0.10,   "dpp": 100.0,   "rth_start": 510, "rth_end": 810, "force_close": 800, "pm_start": 240, "pm_end": 510, "night_start": 1080},
    "SI":  {"tick": 0.005,  "dpp": 5000.0,  "rth_start": 510, "rth_end": 810, "force_close": 800, "pm_start": 240, "pm_end": 510, "night_start": 1080},
    "HG":  {"tick": 0.0005, "dpp": 25000.0, "rth_start": 510, "rth_end": 810, "force_close": 800, "pm_start": 240, "pm_end": 510, "night_start": 1080},
    "PL":  {"tick": 0.10,   "dpp": 50.0,    "rth_start": 510, "rth_end": 810, "force_close": 800, "pm_start": 240, "pm_end": 510, "night_start": 1080},
    "MGC": {"tick": 0.10,   "dpp": 10.0,    "rth_start": 510, "rth_end": 810, "force_close": 800, "pm_start": 240, "pm_end": 510, "night_start": 1080},
    # ── Energy (NYMEX) ───────────────────────────────────────
    "CL":  {"tick": 0.01,   "dpp": 1000.0,  "rth_start": 540, "rth_end": 870, "force_close": 860, "pm_start": 240, "pm_end": 540, "night_start": 1080},
    "NG":  {"tick": 0.001,  "dpp": 10000.0, "rth_start": 540, "rth_end": 870, "force_close": 860, "pm_start": 240, "pm_end": 540, "night_start": 1080},
    "MCL": {"tick": 0.01,   "dpp": 100.0,   "rth_start": 540, "rth_end": 870, "force_close": 860, "pm_start": 240, "pm_end": 540, "night_start": 1080},
    # ── Bonds (CBOT) ─────────────────────────────────────────
    "ZB":  {"tick": 1/32,   "dpp": 1000.0,  "rth_start": 500, "rth_end": 900, "force_close": 890, "pm_start": 240, "pm_end": 500, "night_start": 1080},
    "ZN":  {"tick": 1/64,   "dpp": 1000.0,  "rth_start": 500, "rth_end": 900, "force_close": 890, "pm_start": 240, "pm_end": 500, "night_start": 1080},
    "ZF":  {"tick": 1/128,  "dpp": 1000.0,  "rth_start": 500, "rth_end": 900, "force_close": 890, "pm_start": 240, "pm_end": 500, "night_start": 1080},
}


# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════
def round_tick(price, tick):
    return round(round(price / tick) * tick, 10)


def compute_vp(highs, lows, volumes):
    """Volume profile → (POC, VAH, VAL)."""
    valid = volumes > 0
    if valid.sum() < 5:
        return np.nan, np.nan, np.nan
    dh = highs[valid].max(); dl = lows[valid].min(); dr = dh - dl
    if dr <= 0:
        return np.nan, np.nan, np.nan
    bs = max(1.0, dr / 200); nb = int(np.ceil(dr / bs)) + 1
    if nb < 3:
        return np.nan, np.nan, np.nan
    be = np.linspace(dl, dh, nb + 1); bc = (be[:-1] + be[1:]) / 2
    bv = np.zeros(nb)
    for i in range(len(highs)):
        if not valid[i]:
            continue
        lo_b = max(0, int((lows[i] - dl) / bs))
        hi_b = min(nb - 1, int((highs[i] - dl) / bs))
        cnt = hi_b - lo_b + 1
        if cnt > 0:
            bv[lo_b:hi_b + 1] += volumes[i] / cnt
    tv = bv.sum()
    if tv <= 0:
        return np.nan, np.nan, np.nan
    pi = np.argmax(bv); poc = bc[pi]; va = bv[pi]; li = pi; hi_i = pi
    while va / tv < VP_VALUE_AREA_PCT:
        cl = li > 0; ch = hi_i < nb - 1
        if not cl and not ch:
            break
        lv = bv[li - 1] if cl else -1; hv = bv[hi_i + 1] if ch else -1
        if lv >= hv:
            li -= 1; va += bv[li]
        else:
            hi_i += 1; va += bv[hi_i]
    return poc, be[hi_i + 1], be[li]


def discover_instruments(data_dir, ticker_filter=None):
    """Find all data files matching the naming convention."""
    pattern = os.path.join(data_dir, "*_full_1min_continuous_absolute_adjusted*.txt")
    files = glob.glob(pattern)
    instruments = []
    skipped = []
    for f in sorted(files):
        ticker = os.path.basename(f).split("_full_")[0].upper()
        if ticker_filter and ticker not in ticker_filter:
            continue
        if ticker in INST_SPECS:
            instruments.append((ticker, f))
        else:
            skipped.append(ticker)
    return instruments, skipped


# ════════════════════════════════════════════════════════════
# BACKTEST ENGINE (one instrument)
# ════════════════════════════════════════════════════════════
def run_instrument(ticker, filepath, spec, out_dir):
    """Complete IS+OOS backtest for one instrument. Returns result dict or None."""
    tick = spec["tick"]; dpp = spec["dpp"]
    slip_pts = SLIPPAGE_TICKS * tick * 2
    fc = spec["force_close"]
    entry_cutoff = spec["rth_start"] + ENTRY_WINDOW

    t0 = time.time()

    # ── Load & label ─────────────────────────────────────────
    df = pd.read_csv(filepath, header=None,
        names=["datetime", "open", "high", "low", "close", "volume"],
        parse_dates=["datetime"],
        dtype={"open": np.float64, "high": np.float64, "low": np.float64,
               "close": np.float64, "volume": np.int64})
    df.sort_values("datetime", inplace=True)
    df.reset_index(drop=True, inplace=True)

    h = df["datetime"].dt.hour.values
    m = df["datetime"].dt.minute.values
    tm = h * 60 + m

    ns = spec["night_start"]; pm_s = spec["pm_start"]
    pm_e = spec["pm_end"]; rth_e = spec["rth_end"]

    sess = np.full(len(df), "other", dtype="U10")
    sess[(tm >= ns) | (tm < pm_s)]     = "night"
    sess[(tm >= pm_s) & (tm < pm_e)]   = "premarket"
    sess[(tm >= pm_e) & (tm < rth_e)]  = "rth"
    sess[(tm >= rth_e) & (tm < ns)]    = "post"
    df["session"] = sess; df["time_min"] = tm

    cal = df["datetime"].dt.normalize()
    df["trading_date"] = (cal + pd.to_timedelta(np.where(tm >= ns, 1, 0), unit="D")).dt.date

    sd = pd.Timestamp(WARMUP_START).date()
    ed = pd.Timestamp(OOS_END).date()
    df = df[(df["trading_date"] >= sd) & (df["trading_date"] <= ed)].copy()
    df.reset_index(drop=True, inplace=True)

    # ── Build daily stats ────────────────────────────────────
    run_date = pd.Timestamp(IS_START).date()
    tdates = sorted(df["trading_date"].unique())

    rth = df[df["session"] == "rth"]
    rgrp = rth.groupby("trading_date")
    rst = rgrp.agg(rh=("high", "max"), rl=("low", "min"),
                   ro=("open", "first"), rc=("close", "last"))
    rst["rng"] = rst["rh"] - rst["rl"]
    rst["br"] = abs(rst["rc"] - rst["ro"]) / rst["rng"].replace(0, np.nan)
    rst["atr"] = rst["rng"].rolling(14, min_periods=14).mean()

    pm = df[df["session"] == "premarket"]
    pgrp = pm.groupby("trading_date")
    if len(pgrp) == 0:
        return None
    pst = pgrp.agg(ph=("high", "max"), pl=("low", "min"))
    pst["prng"] = pst["ph"] - pst["pl"]

    pre = df[df["session"].isin(["night", "premarket"])]
    vp2 = {}
    for td, g in pre.groupby("trading_date"):
        vp2[td] = compute_vp(g["high"].values, g["low"].values, g["volume"].values)

    rbars = {}
    for td, g in rgrp:
        b = g[["open", "high", "low", "close", "time_min", "volume"]].values
        if len(b) >= 5:
            rbars[td] = b

    # ── Build packets ────────────────────────────────────────
    packets = []
    for i, td in enumerate(tdates):
        if td < run_date or td not in rbars or len(rbars[td]) < 10 or td not in pst.index:
            continue
        pkt = {"td": td, "bars": rbars[td],
               "pmh": pst.loc[td, "ph"], "pml": pst.loc[td, "pl"],
               "pmrng": pst.loc[td, "prng"]}
        v = vp2.get(td, (np.nan, np.nan, np.nan))
        pkt["vpoc"], pkt["vvah"], pkt["vval"] = v

        prev = [d for d in tdates[:i] if d in rst.index]
        if prev:
            p = prev[-1]
            pkt["pdh"] = rst.loc[p, "rh"]; pkt["pdl"] = rst.loc[p, "rl"]
            pkt["pbr"] = rst.loc[p, "br"]; pkt["atr"] = rst.loc[p, "atr"]
            if pd.notna(pkt["atr"]) and pkt["atr"] > 0:
                pkt["pra"] = rst.loc[p, "rng"] / pkt["atr"]
                pkt["pmra"] = pkt["pmrng"] / pkt["atr"]
            else:
                pkt["pra"] = pkt["pmra"] = np.nan
        else:
            pkt["pdh"] = pkt["pdl"] = pkt["pbr"] = pkt["atr"] = np.nan
            pkt["pra"] = pkt["pmra"] = np.nan
        packets.append(pkt)

    if len(packets) < 50:
        return None

    # ── Strategy ─────────────────────────────────────────────
    trades = []
    for pkt in packets:
        atr = pkt["atr"]
        if pd.isna(atr) or atr <= 0:
            continue
        if pd.notna(pkt["pra"]) and pkt["pra"] > MAX_PRIOR_RANGE_ATR:
            continue
        if pd.notna(pkt["pmra"]) and pkt["pmra"] > MAX_PM_RANGE_ATR:
            continue
        pmh, pml = pkt["pmh"], pkt["pml"]
        if pd.isna(pmh) or pd.isna(pml) or pmh <= pml:
            continue

        sd_pts = round_tick(STOP_FRAC * atr, tick)
        if sd_pts <= 0:
            continue

        bars = pkt["bars"]; nb = len(bars)
        pdh = pkt["pdh"]; pdl = pkt["pdl"]
        pbr = pkt["pbr"]
        strong = pd.notna(pbr) and pbr >= STRONG_TREND_THRESHOLD

        # Classify structural / gap
        pdh_in = pd.notna(pdh) and pdh > pml and pdh < pmh
        pdl_in = pd.notna(pdl) and pdl > pml and pdl < pmh
        gap_up = pd.notna(pdh) and pdh < pml
        gap_dn = pd.notna(pdl) and pdl > pmh

        # Build levels
        lvls = []
        if gap_up or gap_dn:
            lvls.append(("pm_high_break", pmh, 1))
            lvls.append(("pm_low_break", pml, -1))
        else:
            if pdh_in and pd.notna(pdh):
                lvls.append(("structural_pdh", pdh, 1))
            if pdl_in and pd.notna(pdl):
                lvls.append(("structural_pdl", pdl, -1))
            if pd.notna(pdh) and not pdh_in:
                lvls.append(("pdh_break", pdh, 1))
            if pd.notna(pdl) and not pdl_in:
                lvls.append(("pdl_break", pdl, -1))
            el = [l[1] for l in lvls if l[2] == 1]
            es = [l[1] for l in lvls if l[2] == -1]
            if pmh not in el:
                lvls.append(("pm_high_break", pmh, 1))
            if pml not in es:
                lvls.append(("pm_low_break", pml, -1))
        if not [l for l in lvls if l[2] == 1]:
            lvls.append(("pm_high_break", pmh, 1))
        if not [l for l in lvls if l[2] == -1]:
            lvls.append(("pm_low_break", pml, -1))

        active = list(lvls)
        t_today = 0; scan = 0

        while t_today < MAX_TRADES_PER_DAY:
            found = False
            for j in range(scan, nb - 1):
                if found:
                    break
                bc_j, bt_j = bars[j, 3], bars[j, 4]
                if bt_j >= entry_cutoff:
                    break
                for sn, lv, d in active:
                    hit = (d == 1 and bc_j > lv) or (d == -1 and bc_j < lv)
                    if not hit:
                        continue
                    if d == -1 and strong:
                        continue

                    # VP2 confluence
                    has_vp2 = False
                    if atr > 0:
                        thr = VP2_THRESHOLD * atr
                        for vv in [pkt["vvah"], pkt["vval"], pkt["vpoc"]]:
                            if pd.notna(vv) and abs(lv - vv) <= thr:
                                has_vp2 = True; break
                    sz = VP2_SIZE_MULT if has_vp2 else 1.0

                    ep = round_tick(bars[j + 1, 0], tick)
                    sp = round_tick(ep - sd_pts, tick) if d == 1 else round_tick(ep + sd_pts, tick)

                    # Walk trade
                    rr = 0.0; ex = "eod_close"; pts = 0.0; xbar = nb - 1
                    for k in range(j + 1, nb):
                        bh, bl, bcc, bt = bars[k, 1], bars[k, 2], bars[k, 3], bars[k, 4]
                        if d == 1 and bl <= sp:
                            rr = (sp - ep) / sd_pts; pts = sp - ep
                            ex = "stop"; xbar = k; break
                        if d == -1 and bh >= sp:
                            rr = (ep - sp) / sd_pts; pts = ep - sp
                            ex = "stop"; xbar = k; break
                        if bt >= fc:
                            pts = (bcc - ep) * d; rr = pts / sd_pts
                            ex = "eod_close"; xbar = k; break
                    else:
                        pts = (bars[-1, 3] - ep) * d; rr = pts / sd_pts

                    cr = COMMISSION_RT / (sd_pts * dpp)
                    sr = slip_pts / sd_pts
                    nr = rr - cr - sr

                    trades.append({
                        "trading_date": pkt["td"],
                        "direction": "long" if d == 1 else "short",
                        "entry_type": sn,
                        "entry_price": round(ep, 6),
                        "stop_price": round(sp, 6),
                        "stop_dist": round(sd_pts, 6),
                        "pnl_rr": round(rr, 4),
                        "net_rr": round(nr, 4),
                        "pnl_points": round(pts, 6),
                        "exit_reason": ex,
                        "atr": round(atr, 4),
                        "trade_num": t_today + 1,
                        "vp2": has_vp2,
                        "size_mult": sz,
                    })

                    t_today += 1; found = True
                    if ex == "stop" and t_today < MAX_TRADES_PER_DAY:
                        scan = xbar + 1
                        active = [l for l in active if l[1] != lv]
                    else:
                        t_today = MAX_TRADES_PER_DAY
                    break
            if not found:
                break

    elapsed = time.time() - t0
    if len(trades) == 0:
        return None

    # ── Metrics ──────────────────────────────────────────────
    tdf = pd.DataFrame(trades)
    tdf["year"] = tdf["trading_date"].apply(lambda d: d.year)
    oos_date = pd.Timestamp(OOS_START).date()

    def met(rrs, yrs):
        n = len(rrs)
        if n == 0:
            return dict(n=0, pf=0, wr=0, exp=0, total_r=0, ann_r=0,
                        avg_win=0, avg_loss=0, dd=0, sharpe=0, t_stat=0, p_val=1)
        ws = rrs[rrs > 0].sum(); ls = abs(rrs[rrs < 0].sum())
        pf = ws / ls if ls > 0 else float("inf")
        cum = np.cumsum(rrs); dd = (cum - np.maximum.accumulate(cum)).min()
        wr = (rrs > 0).sum() / n * 100; exp = rrs.mean()
        aw = rrs[rrs > 0].mean() if (rrs > 0).any() else 0
        al = rrs[rrs < 0].mean() if (rrs < 0).any() else 0
        sh = (exp / rrs.std()) * np.sqrt(n) if n > 1 and rrs.std() > 0 else 0
        ts, pv = stats.ttest_1samp(rrs, 0) if n > 1 else (0, 1.0)
        return dict(n=n, pf=pf, wr=wr, exp=exp, total_r=rrs.sum(),
                    ann_r=rrs.sum() / yrs if yrs > 0 else 0,
                    avg_win=aw, avg_loss=al, dd=dd, sharpe=sh, t_stat=ts, p_val=pv)

    isy = (pd.Timestamp(IS_END) - pd.Timestamp(IS_START)).days / 365.25
    oosy = (pd.Timestamp(OOS_END) - pd.Timestamp(OOS_START)).days / 365.25
    toty = (pd.Timestamp(OOS_END) - pd.Timestamp(IS_START)).days / 365.25

    is_m = met(tdf.loc[tdf["trading_date"] < oos_date, "net_rr"].values, isy)
    oos_m = met(tdf.loc[tdf["trading_date"] >= oos_date, "net_rr"].values, oosy)
    all_m = met(tdf["net_rr"].values, toty)

    # By year
    ydata = {}
    for yr in sorted(tdf["year"].unique()):
        sub = tdf[tdf["year"] == yr]["net_rr"].values
        sw = (sub > 0).sum()
        sws = sub[sub > 0].sum(); sls = abs(sub[sub < 0].sum())
        spf = sws / sls if sls > 0 else float("inf")
        ydata[yr] = {"n": len(sub), "wr": sw / len(sub) * 100, "pf": spf, "r": sub.sum(),
                     "dd": (np.cumsum(sub) - np.maximum.accumulate(np.cumsum(sub))).min()}

    # ── Equity curve PNG ─────────────────────────────────────
    tp = tdf.copy(); tp["cum_r"] = tp["net_rr"].cumsum()
    tp["date"] = pd.to_datetime(tp["trading_date"])

    fig, axes = plt.subplots(3, 1, figsize=(16, 10), height_ratios=[3, 1, 1], facecolor="#1a1a2e")
    for ax in axes:
        ax.set_facecolor("#1a1a2e")
        ax.tick_params(colors="#cccccc", labelsize=8)
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
        for s in ["bottom", "left"]:
            ax.spines[s].set_color("#444466")

    oi = tp[tp["trading_date"] >= oos_date].index
    bd = oi[0] if len(oi) > 0 else len(tp)
    x = np.arange(len(tp))

    axes[0].plot(x[:bd], tp["cum_r"].values[:bd], color="#00ff88", linewidth=1.2)
    if bd < len(tp):
        axes[0].plot(x[bd - 1:], tp["cum_r"].values[bd - 1:], color="#44aaff", linewidth=1.2)
        axes[0].axvline(bd, color="#ffaa00", linewidth=1.5, linestyle="--", alpha=0.8)
    axes[0].fill_between(x[:bd], 0, tp["cum_r"].values[:bd], alpha=0.10, color="#00ff88")
    if bd < len(tp):
        axes[0].fill_between(x[bd:], 0, tp["cum_r"].values[bd:], alpha=0.10, color="#44aaff")
    axes[0].set_ylabel("Cumulative R", color="#cccccc")
    axes[0].set_title(f"{ticker} FVB — IS+OOS (net of costs, stop={STOP_FRAC*100:.0f}% ATR)",
                      color="#ffffff", fontsize=13, fontweight="bold")
    axes[0].grid(axis="y", alpha=0.15, color="#666666")
    nl = min(12, len(tp))
    lp = np.linspace(0, len(tp) - 1, nl, dtype=int)
    axes[0].set_xticks(lp)
    axes[0].set_xticklabels([str(tp.iloc[i]["trading_date"]) for i in lp],
                             rotation=45, ha="right", fontsize=6, color="#999999")

    tp["month"] = tp["date"].dt.to_period("M")
    monthly = tp.groupby("month")["net_rr"].sum()
    mc = ["#44aaff" if p.to_timestamp().date() >= oos_date and monthly[p] >= 0
          else ("#ff4466" if monthly[p] < 0 else "#00ff88") for p in monthly.index]
    axes[1].bar(range(len(monthly)), monthly.values, color=mc, alpha=0.8, width=0.8)
    axes[1].set_ylabel("Monthly R", color="#cccccc", fontsize=9)
    axes[1].axhline(0, color="#444466", linewidth=0.5)

    tp["week"] = tp["date"].dt.to_period("W")
    weekly = tp.groupby("week")["net_rr"].sum()
    wc = ["#44aaff" if p.to_timestamp().date() >= oos_date and weekly[p] >= 0
          else ("#ff4466" if weekly[p] < 0 else "#00ff88") for p in weekly.index]
    axes[2].bar(range(len(weekly)), weekly.values, color=wc, alpha=0.7, width=0.9)
    axes[2].set_ylabel("Weekly R", color="#cccccc", fontsize=9)
    axes[2].axhline(0, color="#444466", linewidth=0.5)

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, f"equity_{ticker}.png"), dpi=150,
                bbox_inches="tight", facecolor="#1a1a2e")
    plt.close(fig)

    # Save trades
    tdf.to_csv(os.path.join(out_dir, f"trades_{ticker}.csv"), index=False)

    return {"ticker": ticker, "elapsed": elapsed, "packets": len(packets),
            "is": is_m, "oos": oos_m, "all": all_m, "years": ydata}


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    test_num = 1
    base = "FVB Final Backtest"
    while os.path.exists(os.path.join(base, f"test_{test_num}")):
        test_num += 1
    out_dir = os.path.join(base, f"test_{test_num}")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("FVB STRATEGY — FINAL PRODUCTION BACKTEST")
    print("=" * 70)
    print(f"  Data:    {DATA_DIR}")
    print(f"  IS:      {IS_START} → {IS_END}")
    print(f"  OOS:     {OOS_START} → {OOS_END}")
    print(f"  Stop:    {STOP_FRAC*100:.0f}% ATR")
    print(f"  Window:  {ENTRY_WINDOW} min")
    print(f"  Costs:   ${COMMISSION_RT:.2f} RT + {SLIPPAGE_TICKS} tick slippage")
    print(f"  Max T/D: {MAX_TRADES_PER_DAY}")
    if TICKER_FILTER:
        print(f"  Filter:  {TICKER_FILTER}")
    print("=" * 70)

    instruments, skipped = discover_instruments(DATA_DIR, TICKER_FILTER)
    if skipped:
        print(f"\n  Skipped (no spec): {', '.join(skipped)}")
    if not instruments:
        print(f"\n  ERROR: No data files found in {DATA_DIR}"); sys.exit(1)
    print(f"\n  Found {len(instruments)} instruments: {', '.join(t for t, _ in instruments)}\n")

    results = []
    for idx, (ticker, fpath) in enumerate(instruments):
        print(f"[{idx + 1}/{len(instruments)}] {ticker}...", end="", flush=True)
        r = run_instrument(ticker, fpath, INST_SPECS[ticker], out_dir)
        if r is None:
            print(f" ⚠ skipped (insufficient data)")
            continue
        results.append(r)
        im = r["is"]; om = r["oos"]
        print(f" ✓ {r['elapsed']:.1f}s | "
              f"IS: {im['n']} tr PF {im['pf']:.2f} R {im['total_r']:+.0f} | "
              f"OOS: {om['n']} tr PF {om['pf']:.2f} R {om['total_r']:+.0f}")
        for yr, yd in sorted(r["years"].items()):
            per = "IS " if yr <= 2023 else "OOS"
            print(f"    {yr} ({per}): {yd['n']:4d} tr | WR {yd['wr']:5.1f}% | "
                  f"PF {yd['pf']:.2f} | R {yd['r']:+7.1f} | DD {yd['dd']:+.1f}")

    if not results:
        print("\n  No instruments produced trades."); sys.exit(1)

    # ── Cross-instrument summary ─────────────────────────────
    print(f"\n{'='*115}")
    print("CROSS-INSTRUMENT SUMMARY (net of costs)")
    print(f"{'='*115}")
    print(f"  {'Tkr':<5} {'IS n':>6} {'IS PF':>6} {'IS R':>8} {'IS/yr':>7} {'IS DD':>7} "
          f"{'OOS n':>6} {'OOS PF':>7} {'OOS R':>8} {'OOS/yr':>7} {'OOS DD':>7} {'p':>7}")
    print(f"  {'─'*111}")

    for r in results:
        im = r["is"]; om = r["oos"]
        print(f"  {r['ticker']:<5} {im['n']:>6} {im['pf']:>6.2f} {im['total_r']:>+8.1f} "
              f"{im['ann_r']:>+7.1f} {im['dd']:>+7.1f} "
              f"{om['n']:>6} {om['pf']:>7.2f} {om['total_r']:>+8.1f} "
              f"{om['ann_r']:>+7.1f} {om['dd']:>+7.1f} {om['p_val']:>7.4f}")

    print(f"  {'─'*111}")
    tir = sum(r["is"]["total_r"] for r in results)
    tor = sum(r["oos"]["total_r"] for r in results)
    tin = sum(r["is"]["n"] for r in results)
    ton = sum(r["oos"]["n"] for r in results)
    print(f"  {'TOTAL':<5} {tin:>6} {'':>6} {tir:>+8.1f} {'':>7} {'':>7} "
          f"{ton:>6} {'':>7} {tor:>+8.1f}")
    print(f"{'='*115}")

    # ── Overlay chart ────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(16, 8), facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    ax.tick_params(colors="#cccccc")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]:
        ax.spines[s].set_color("#444466")

    colors = ["#00ff88", "#44aaff", "#ff4466", "#ffaa00", "#aa66ff",
              "#ff66aa", "#66ffaa", "#ff8844", "#4488ff", "#88ff44",
              "#ffff66", "#66ffff", "#ff6644", "#6644ff", "#44ff66"]
    for i, r in enumerate(results):
        t = pd.read_csv(os.path.join(out_dir, f"trades_{r['ticker']}.csv"))
        c = t["net_rr"].cumsum().values
        ax.plot(range(len(c)), c, color=colors[i % len(colors)], linewidth=1.5, alpha=0.85,
                label=f"{r['ticker']} ({r['all']['total_r']:+.0f}R)")

    ax.set_xlabel("Trade #", color="#cccccc", fontsize=11)
    ax.set_ylabel("Cumulative R", color="#cccccc", fontsize=11)
    ax.set_title(f"FVB — All Instruments (stop={STOP_FRAC*100:.0f}% ATR, net of costs)",
                 color="#ffffff", fontsize=14, fontweight="bold")
    ax.legend(fontsize=9, facecolor="#1a1a2e", edgecolor="#444466",
              labelcolor="#cccccc", ncol=2, loc="upper left")
    ax.grid(axis="y", alpha=0.15, color="#666666")
    ax.axhline(0, color="#444466", linewidth=0.5, linestyle="--")
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "all_instruments_overlay.png"),
                dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close(fig)

    # ── Save summary CSV ─────────────────────────────────────
    rows = []
    for r in results:
        rows.append({
            "ticker": r["ticker"],
            **{f"is_{k}": round(v, 4) if isinstance(v, float) else v
               for k, v in r["is"].items()},
            **{f"oos_{k}": round(v, 4) if isinstance(v, float) else v
               for k, v in r["oos"].items()},
        })
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "summary.csv"), index=False)

    # ── Save metrics TXT ─────────────────────────────────────
    with open(os.path.join(out_dir, "metrics.txt"), "w") as f:
        f.write(f"FVB Strategy — Final Production Backtest\n")
        f.write(f"Stop: {STOP_FRAC*100:.0f}% ATR | Window: {ENTRY_WINDOW}m\n")
        f.write(f"Costs: ${COMMISSION_RT:.2f} RT + {SLIPPAGE_TICKS} tick slippage\n")
        f.write(f"Period: {IS_START} → {OOS_END}\n\n")
        for r in results:
            f.write(f"{'='*50}\n{r['ticker']}\n{'='*50}\n")
            for label, m in [("IS", r["is"]), ("OOS", r["oos"]), ("ALL", r["all"])]:
                f.write(f"\n{label}:\n")
                f.write(f"  Trades:     {m['n']}\n")
                f.write(f"  WR:         {m['wr']:.1f}%\n")
                f.write(f"  PF:         {m['pf']:.2f}\n")
                f.write(f"  Total R:    {m['total_r']:+.1f}\n")
                f.write(f"  Annual R:   {m['ann_r']:+.1f}\n")
                f.write(f"  Exp:        {m['exp']:+.4f}\n")
                f.write(f"  Max DD:     {m['dd']:+.1f}\n")
                f.write(f"  Sharpe:     {m['sharpe']:.2f}\n")
                f.write(f"  T-stat:     {m['t_stat']:.2f}\n")
                f.write(f"  P-value:    {m['p_val']:.4f}\n")
            f.write(f"\nBY YEAR:\n")
            for yr, yd in sorted(r["years"].items()):
                per = "IS " if yr <= 2023 else "OOS"
                f.write(f"  {yr} ({per}): {yd['n']:4d} tr | WR {yd['wr']:5.1f}% | "
                        f"PF {yd['pf']:.2f} | R {yd['r']:+7.1f}\n")
            f.write("\n")

    shutil.copy2(__file__, os.path.join(out_dir, os.path.basename(__file__)))

    print(f"\nOutputs → {out_dir}")
    print(f"  Per-instrument: equity_TICKER.png + trades_TICKER.csv")
    print(f"  Combined:       all_instruments_overlay.png")
    print(f"  Summary:        summary.csv + metrics.txt")


if __name__ == "__main__":
    main()
