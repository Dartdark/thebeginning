"""Jump Fade v3 (volume filter vz >= 2, MC-verified 11/12) on the 150K evaluation WITHOUT VB (user 2026-11-12: 'does it help the eval
if so im making the decision to add it rn. whats the harm'): (1) fresh-eval pass rate (bench150 engine, 21 days) at 1 / 2 MNQ,
(2) account #5 FROM ITS STATE NOW: balance $147,998, EOD floor $146,000 (trailing $4,000), target $159,000, DLL $2,000, horizons
20 and 60 trading days, every historical start day; fail = intraday touch of the floor. (3) the lead's own worst day / streak.
  tools/run_stamped.sh analysis/jump_fade_v3_eval_now.py > analysis/outputs/jump_fade_v3_eval_now_output.txt
  ... novol > analysis/outputs/jump_fade_v2_eval_now_output.txt   (v2 = no volume filter)
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_lib as L, jump_study as S, bench150 as BN
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
EXTRA = 0.55
print(__doc__.split("\n")[0])
b = L.bars(); M = S.Mkt(); yr = b.ts.dt.year.to_numpy(); sgn = np.sign(b.r).fillna(0).to_numpy()
mask = (yr >= 2018) & (b.J.abs().to_numpy() > 3) & np.isin(b.ts.dt.hour.to_numpy(), [7, 8, 9]) & ((b.vz.to_numpy() >= 2) | ('novol' in sys.argv))
print('VERSION:', 'v2 (no volume filter)' if 'novol' in sys.argv else 'v3 (vz >= 2)')
T = S.trades(b, M, mask, -sgn, "rng", 1.5, tp=0.3, hold=240); ix = np.searchsorted(M.ts, T.ts.to_numpy())
print(f"v3 trades {len(T)}, ${T.net.mean():.1f} per NQ, per MNQ ${T.net.mean() / 10 - EXTRA:.2f}; worst trade per MNQ ${T.net.min() / 10 - EXTRA:,.0f}")
ctx = BN.setup(); g = ctx["g"]; trr = ctx["trr"]; dts = ctx["dts"]; tpos = pd.Series(np.arange(len(trr)), index=dts)
W = np.zeros((ctx["D"], 1440)); R = np.zeros((ctx["D"], 1440)); hi, lo = M.arr[1], M.arr[2]
for t, e in zip(T.itertuples(), ix):
    day = pd.Timestamp(t.ts).normalize()
    if day not in tpos.index: continue
    r = tpos[day]; n = int(t.mins); mins = pd.DatetimeIndex(M.ts[e:e + n]); js = mins.hour * 60 + mins.minute
    if (mins.normalize() != day).any(): continue
    cost = t.gross - t.net; adv = ((lo[e:e + n] if t.side > 0 else hi[e:e + n]) - t.entry) * t.side * 20 - cost
    adv[-1] = t.net if t.why == "tgt" else min(adv[-1], t.net)
    W[r, js] += adv; W[r, js[-1] + 1:] += t.net; R[r, js[-1]:] += t.net
W, R = W / 10, R / 10
fee = np.zeros(ctx["D"]); np.add.at(fee, [tpos[pd.Timestamp(x).normalize()] for x in T.ts if pd.Timestamp(x).normalize() in tpos.index], EXTRA)
W -= fee[:, None]; R -= fee[:, None]
ctx["Wb"] = ctx["Wb"] - 2 * ctx["P"]["JF"][0]; ctx["Rb"] = ctx["Rb"] - 2 * ctx["P"]["JF"][1]
print("BASE = bench150 LIVE_EVAL minus JF (re-added below as the candidate): ONB30 $2,750 risk, EOS $1,250 risk, MON_BR 5, Twin 2, DT 2")
d = R[:, -1]; act = d != 0
print(f"lead per MNQ: days traded {act.sum()}, worst day ${d.min():,.0f}, worst intraday ${W.min():,.0f}, worst 5-day sum ${pd.Series(d).rolling(5).sum().min():,.0f}")
print("\n== (1) fresh 150K evaluation, 21 days (bench150 engine)")
BN.eval_bench(ctx, {f"+ v3 {k} MNQ": (k * W, k * R) for k in (1, 2)})

def now(Wx, Rx, s, H, bal=147998.08, floor=146000.0, tgt=159000.0, dd=4000.0, dll=2000.0):
    D = len(Wx)
    if s + H > D: return None
    for dd_ in range(s, s + H):
        w, rr = Wx[dd_], Rx[dd_]; lim = max(floor, bal - dll)
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + rr >= tgt)[0]; jp = win[0] if len(win) else len(w)
        if jp < jb: return "pass"
        if jb < len(w):
            if lim == floor: return "fail"
            bal = lim
        else: bal += rr[-1]
        floor = max(floor, bal - dd)
    return "open"
yrs = ctx["yr"]; ok = (yrs >= 2018) & (dts <= "2026-09-01")
print("\n== (2) account #5 from today's state ($1,998 above the floor, $11,002 to the target)")
for H in (20, 60):
    base = np.array([now(ctx["Wb"], ctx["Rb"], s, H) for s in range(ctx["D"])], dtype=object); v = ok & (base != None)
    line = f"   {H} days: base pass {np.mean(base[v] == 'pass'):.1%} fail {np.mean(base[v] == 'fail'):.1%}"
    for k in (1, 2):
        o = np.array([now(ctx["Wb"] + k * W, ctx["Rb"] + k * R, s, H) for s in range(ctx["D"])], dtype=object)
        dlt = (o[v] == "pass").astype(float) - (base[v] == "pass").astype(float)
        rng = np.random.default_rng(1); nb = int(np.ceil(len(dlt) / 60)); st = rng.integers(0, len(dlt), (2000, nb))
        mm = dlt[((st[:, :, None] + np.arange(60)) % len(dlt)).reshape(2000, -1)[:, :len(dlt)]].mean(axis=1)
        line += f" | +{k} MNQ pass {np.mean(o[v] == 'pass'):.1%} ({dlt.mean():+.1%}, band {np.percentile(mm, 5):+.1%}/{np.percentile(mm, 95):+.1%}) fail {np.mean(o[v] == 'fail'):.1%}"
    print(line, flush=True)
