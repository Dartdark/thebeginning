"""IFT_NQ5_Flow_Signal: user's MultiCharts report (2026-10-28) at our costs.
Legs grouped into positions by entry time; cost per contract $7.25 + 1 tick ($5) entry + 1 tick on stop / market exits
(TP limit exits no slippage). By year, longs / shorts, 2023 onward, t on positions."""
import sys, collections, math, openpyxl
sys.path.insert(0, 'analysis')
F = 'mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes IFT NQ5.xlsx'
rows = list(openpyxl.load_workbook(F, read_only=True, data_only=True)['List of Trades'].iter_rows(values_only=True))[3:]
pos = collections.OrderedDict()
i = 0
while i + 1 < len(rows):
    e, x = rows[i], rows[i + 1]; i += 2
    if e[0] is None: continue
    side = 'L' if e[2] == 'EntryLong' else 'S'
    q, p = e[7], e[8]
    tp = 'TP' in str(x[3])
    cost = q * (7.25 + 5 + (0 if tp else 5))
    k = (e[4], e[6], side)
    d = pos.setdefault(k, {'side': side, 'date': e[4], 'gross': 0, 'net': 0, 'q': 0})
    d['gross'] += p; d['net'] += p - cost; d['q'] += q
P = list(pos.values())
def st(xs, lab):
    n = len(xs)
    if n < 2: print(f'{lab:14s} n={n}'); return
    m = sum(xs) / n; sd = math.sqrt(sum((v - m) ** 2 for v in xs) / (n - 1))
    gp = sum(v for v in xs if v > 0); gl = -sum(v for v in xs if v < 0)
    eq = mx = dd = 0
    for v in xs: eq += v; mx = max(mx, eq); dd = max(dd, mx - eq)
    print(f'{lab:14s} n={n:4d} net=${sum(xs):9,.0f} avg=${m:7.1f} t={m/sd*math.sqrt(n):5.2f} PF={gp/max(gl,1):4.2f} maxDD=${dd:8,.0f}')
print('Positions at 2 NQ, net of costs (gross in brackets for all)')
st([p['gross'] for p in P], 'ALL gross')
st([p['net'] for p in P], 'ALL net')
for s in 'LS': st([p['net'] for p in P if p['side'] == s], 'longs' if s == 'L' else 'shorts')
st([p['net'] for p in P if p['date'].year >= 2023], '2023+ net')
for s in 'LS': st([p['net'] for p in P if p['side'] == s and p['date'].year >= 2023], ('longs' if s == 'L' else 'shorts') + ' 2023+')
for y in range(2017, 2027):
    st([p['net'] for p in P if p['date'].year == y], str(y))
