"""Antigravity's NQAlignedWeaknessShort (antigravity/jesse 2026-10-20): rebuild on our data with the Relative Strength
machinery (analysis/relative_strength_test.py: same 9:00 decision, 9:01 fill, 0.6 / 1.0 x 20-day range exits, flat 15:00),
signal = (NQ % 8:30 -> 9:00) - 1.25 x (ES %) <= -0.20% and ES % < 0, shorts only. Then: how much of it is the user's
Relative Strength short side (already traded on 150K funded / personal), and does 'ES down' improve RS shorts?
  python3 analysis/anti_nq_aligned_weakness_short_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import relative_strength_test as RS

if __name__ == "__main__":
    days, N, E = RS.load(); Z = RS.signals(days, N, E)
    rn = N["c"][:, 30] / N["c"][:, 0] - 1; re = E[:, 30] / E[:, 0] - 1      # 8:30 close -> 9:00 close
    sig = np.where(((rn - 1.25 * re) <= -0.002) & (re < 0), -9.0, np.nan)   # fake Z of -9 = short
    A = RS.trades(days, N, sig); RS.line("aligned weakness short (rebuild)", A)
    th = pd.read_csv(RS.SP + "anti/aws_trades.csv"); th["date"] = pd.to_datetime(th.date.astype(str))
    mg = th.merge(A, on="date"); print(f"   its trades.csv {len(th)} (${th.net_pnl.mean():.0f}); shared days {len(mg)}; P&L corr {mg.net_pnl.corr(mg.pnl):.2f}")
    T = RS.trades(days, N, Z); S = T[T.side < 0]
    ov = A.date.isin(S.date); print(f"   share of its days that are also Relative Strength short days: {ov.mean():.0%} ({ov.sum()} of {len(A)})")
    RS.line("   ...those shared days", A[ov]); RS.line("   ...its days that RS does not short", A[~ov])
    esd = pd.Series(re, index=pd.DatetimeIndex([pd.Timestamp(str(x)) for x in days.date]))
    S = S.assign(es_down=esd.reindex(S.date).to_numpy() < 0)
    RS.line("RS shorts, ES down 8:30-9:00", S[S.es_down]); RS.line("RS shorts, ES up", S[~S.es_down])
