"""Tran 2026, 'From Funded to Paid' (sizing in funded prop accounts), checked on our funded bench (2026-10-14).
Paper (coin-flip trader, one trade a day, Solis Futures rules): the sizing that maximises EXPECTED withdrawals bets bold,
kills 81-90% of accounts and pays nothing in the median path; the chance of being paid and expected cash point opposite
ways; a 10% per-bet cap removes most of the gain; the binding quantity is the cushion, not nominal account size.
Here: the current funded plan (+ CL fade 2 MCL) under bolder / safer sizing - fixed size 1.0 / 1.5 / 2.0 x, and cushion
sizing f = clip(cushion / ref, 0.5, 1) with ref $2,000 / $1,500 (the user's choice) / $1,000 - reporting expected payouts AND
the chance of any payout, blown accounts and all 6 payouts within 2 years.
  python3 analysis/funded_to_paid_check.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0]); sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")
    lab = ns["lab"]
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    print(f"{'sizing':<34}{'1y exp':>9}{'2y exp':>9}{'paid any (1y)':>15}{'blown 1y/2y':>13}{'all 6 (2y)':>12}{'days to 1st':>12}")
    for nm, kw in (("fixed 1.0x (no cushion sizing)", dict(fmin=1.0, fmax=1.0, ref=1500.0)),
                   ("fixed 1.5x", dict(fmin=1.5, fmax=1.5, ref=1500.0)), ("fixed 2.0x", dict(fmin=2.0, fmax=2.0, ref=1500.0)),
                   ("cushion, full from $2,000", dict(fmin=0.5, fmax=1.0, ref=2000.0)),
                   ("cushion, full from $1,500 (chosen)", dict(fmin=0.5, fmax=1.0, ref=1500.0)),
                   ("cushion, full from $1,000", dict(fmin=0.5, fmax=1.0, ref=1000.0))):
        a, c = lab.score(plan, 250, **kw), lab.score(plan, 500, **kw)
        print(f"{nm:<34}${a['expected']:>8,.0f}${c['expected']:>8,.0f}{a['any_payout']:>15.0%}{a['blown']:>7.0%} / {c['blown']:.0%}{c['all_6']:>12.0%}{a['days_to_1st']:>12.0f}")
