"""150K FUNDED book: what each piece contributes, and one-at-a-time resize (user 2026-11-13: 'improve the funded book's big pieces';
resize rule after VB's retirement 11/12 — the funded book was never resized). Base = bench150.LIVE_FUNDED (the documented 150K funded
plan: 50K table x 1.5 + MOC 3 MES + RS 1 + DT 2 + OT 2 + Twin 2; VB out). Each piece at 0 (= its contribution), x0.5 and x1.5.
Funded bench: 600 paired 2-year histories (20-day blocks), cushion sizing; '2y $' = payouts within 2 years (cap $20,500 x 1? see bench),
'beats' = share of histories where the variant pays more than the base. OT trades end 2026-07-07 (order-flow data).
  tools/run_stamped.sh analysis/funded_resize150.py > analysis/outputs/funded_resize150_output.txt
"""
import sys; sys.path.insert(0, "analysis")
import bench150 as BN
print(__doc__.split("\n")[0])
ctx = BN.setup(); B = BN.LIVE_FUNDED; print(f"LIVE_FUNDED = {B}")
def sc(v, k): return ("risk", round(v[1] * k / 50) * 50) if isinstance(v, tuple) else v * k
V = {}
for k, v in B.items():
    V[f"{k} -> 0 (contribution)"] = {a: b for a, b in B.items() if a != k}
    for m in (0.5, 1.5): V[f"{k} x{m} ({sc(v, m)})"] = {**B, k: sc(v, m)}
BN.funded_bench(ctx, V)
