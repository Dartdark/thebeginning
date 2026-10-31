# Evidence sheet 1: Late-Day Flow sized by the leveraged-ETF dollar flow, not the price move
Verdict: **NEEDS DATA (free or cheap), then TEST.** Rank 1.

1. **Who trades and why.** Daily-reset leveraged / inverse Nasdaq-100 ETFs (TQQQ 3x, SQQQ −3x, QLD 2x, QID −2x) must
   restore their leverage every day. The rebalance is L(L−1) x AUM x the day's index return, in the direction of the
   move for both long and inverse funds, executed by the funds' swap / futures counterparties near the close (Cheng &
   Madhavan 2009; Shum et al. 2016). Counter-view: Ivanov & Lenkey (Fed 2014 / J. Financial Markets 2018) find
   same-day creations / redemptions offset much of it, leaving a late-day effect that is economically insignificant.
2. **Direction, size, timing known in advance?** Direction = sign of the day's move (known at 14:00 CT). Size =
   Σ L(L−1) x AUM x return: on a 2% NDX day with TQQQ ~$27bn, SQQQ ~$3bn, QLD ~$7bn ≈ $3.2bn + $0.7bn + $0.3bn ≈ **$4bn**.
   NQ trades a median **$24bn** in 14:00-15:00 CT (2023-25, our 1-min volume). AUM is known from the prior day's
   shares outstanding. Timing: last ~30-60 min.
3. **Reaches NQ?** Yes: swap dealers hedge in NQ / QQQ / the stocks. No proxy market.
4. **What separates it from momentum?** AUM. Late-Day Flow (in the plan) uses only the price move (≥ 0.4 ATR at 14:00).
   TQQQ's AUM grew ~5-7x from 2018 to 2025, so the same % move implies very different dollar flow. If the flow drives
   LDF, LDF trades should earn more when predicted flow / NQ last-hour volume is high, at the same move size. If not,
   LDF's edge is something else (useful to know) and Ivanov & Lenkey are right.
   **Data:** daily shares outstanding + NAV for TQQQ, SQQQ, QLD, QID 2018-26. Not in the repo. Sources to check:
   ProShares fund pages (Documents & Downloads, daily holdings / NAV files), SEC N-PORT (monthly), a vendor.
   Cost: free to low. Also optional: daily creations / redemptions (from changes in shares outstanding) to test the
   Ivanov-Lenkey offset.
5. **Beats costs in a gap?** It doesn't add a new slot: it re-sizes LDF (already MultiCharts-confirmed, $95 per NQ
   net, t 3.5, 895 trades). No extra costs. Could matter for sizing: e.g. LDF 1 MNQ on low-flow days, 3 on high-flow.
6. **Power.** One pre-registered test inside LDF's 895 trades: net $ by tercile of predicted flow / last-hour NQ
   volume, controlling for move size. LDF per-trade sd ≈ $810 per NQ → top-vs-bottom tercile difference needs
   ≈ $130 for t 2. LDF averages $95, so the effect must be large (e.g. top $150 / bottom $20). Borderline but
   realistic IF flow is the mechanism; a null is also informative.
7. **Already tested?** LDF itself (A tier), LDF order-flow filter (TIER_LIST), LETF overnight reversal (F). The AUM /
   dollar-flow version is not in TIER_LIST or `analysis/` (`letf_rebalance_test.py` uses price only).
