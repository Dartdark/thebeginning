"""NQ push-reversal engine + entropy gate. Pre-registered: checks/candidates/push_reversal/PREREG.md (2026-11-11).
  python analysis/push_reversal_test.py [holdout]   -> analysis/outputs/push_reversal_output.txt
Without 'holdout' only 2018-2022 is reported (gate 1). With it, the single 2023+ look is printed too.
"""
import sys, glob, os, numpy as np, pandas as pd
HOLD = 'holdout' in sys.argv
PT, COST, TICK = 20.0, 7.25 + 2 * 5.0, 0.25
fs = sorted(f for f in glob.glob('data/NQ_1min_20*.csv') if '2017' not in f or True)
d = pd.concat([pd.read_csv(f) for f in fs if '_ON_' not in f], ignore_index=True)
d = d[(d.time >= 831) & (d.time <= 1500)].sort_values(['date', 'time'])
days = [(k, g) for k, g in d.groupby('date')]

def ent(x):
    s = np.sign(np.diff(x)).astype(int) + 1
    p = np.bincount(s[:-1] * 3 + s[1:], minlength=9) / max(1, len(s) - 1)
    p = p[p > 0]; return -(p * np.log(p)).sum()

def run(L=60, Z=2.0, side=1, H=60, kstop=1.0, rnd=None, only=None):
    hist, out = [], []
    for j, (dt, g) in enumerate(days):
        c, o, h, l, t = (g[x].to_numpy() for x in ('close', 'open', 'high', 'low', 'time'))
        ch = c[L:] - c[:-L] if len(c) > L else np.array([])
        if len(hist) >= 20 and len(c) > L + 5:
            sd = np.std(np.concatenate(hist[-20:]))
            idx = np.arange(L, len(c) - 1); win = (t[idx] >= 931) & (t[idx] <= 1430)
            z = (c[idx] - c[idx - L]) / sd
            if rnd is not None:
                if only is not None and dt not in only: hist.append(ch); continue
                cand = idx[win]; i = rnd.choice(cand) if len(cand) else None
            else:
                hit = idx[win & ((z <= -Z) if side > 0 else (z >= Z))]; i = hit[0] if len(hit) else None
            if i is not None:
                e = o[i + 1]; stop = e - side * kstop * sd; ex, why = None, 'time'
                last = min(i + H, len(c) - 1, np.searchsorted(t, 1555, side='right') - 1)
                for k in range(i + 1, last + 1):
                    if (side > 0 and l[k] <= stop) or (side < 0 and h[k] >= stop):
                        ex, why = stop - side * TICK, 'stop'; break
                if ex is None: ex = c[last]
                out.append(dict(date=dt, yr=dt // 10000, side=side, net=side * (ex - e) * PT - COST,
                                move=abs(c[last] - e), E=ent(c[max(0, i - 30):i + 1]), why=why, t=t[i]))
        hist.append(ch)
    return pd.DataFrame(out)

def line(x, lab):
    if len(x) < 5: print(f'{lab:<30} n {len(x)}'); return
    n = x.net; pf = n[n > 0].sum() / max(1, -n[n < 0].sum())
    print(f'{lab:<30} n {len(n):4d} win {np.mean(n > 0):5.1%} ${n.mean():7.1f} PF {pf:4.2f} t {n.mean() / n.std() * np.sqrt(len(n)):5.2f} total ${n.sum():,.0f}')

base = run()
D = base[base.yr <= 2022]
print('=== Gate 1: design 2018-2022, primary (long, L60, z<=-2, H60, stop 1 sd)')
line(D, 'primary longs')
print('by year:', '  '.join(f'{y} ${g.net.sum():,.0f} ({len(g)})' for y, g in D.groupby('yr')))
print('exits', D.why.value_counts().to_dict())
rng = np.random.default_rng(1); only = set(D.date); pm = []
for r in range(200):
    p = run(rnd=rng, only=only); pm.append(p[p.yr <= 2022].net.mean())
pm = np.array(pm); print(f'placebo random time same days (200 draws): mean ${pm.mean():.1f}, p = {np.mean(pm >= D.net.mean()):.3f}')
sh = run(side=-1); line(sh[sh.yr <= 2022], 'control: mirror shorts z>=+2')
print('--- neighbours (information only)')
for L in (30, 120): t_ = run(L=L); line(t_[t_.yr <= 2022], f'L{L}')
for Z in (1.5, 2.5): t_ = run(Z=Z); line(t_[t_.yr <= 2022], f'z{Z}')
print('--- entropy ingredient (design)')
q = D.E.quantile(0.3); lo, hi = D[D.E <= q], D[D.E > q]
print(f'low-entropy |move| {lo.move.mean():.1f} pt vs rest {hi.move.mean():.1f} pt (ratio {lo.move.mean() / hi.move.mean():.2f})')
line(lo, 'low entropy (gate on)'); line(hi, 'rest')
if HOLD:
    print('=== Gate 2: ONE LOOK at 2023+'); Hd = base[base.yr >= 2023]; line(Hd, 'primary longs 2023+')
    line(Hd[Hd.E <= q], 'low entropy 2023+')
