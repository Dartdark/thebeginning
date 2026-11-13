# Replication: overnight long on Nasdaq-100 futures

**Source.** Blose, Gondhalekar & Kort (2018) found gold's return comes overnight, with negative daytime returns. A
practitioner note adapted it to NQ: long at the 17:05 CT reopen, out at 07:20 CT, only when the last two sessions' 5-minute
closes fit a straight line (R² ≥ 0.3); 25-point target, one re-entry after a target, no stop. The note reported t 5.10 in
development and 3.09 / 1.58 in two out-of-sample periods, from roughly 7.3 million configurations searched.

**Who pays (claimed):** a risk premium for holding through the less liquid overnight session.

**How I tested it.** The rule exactly as given, on 1-minute NQ 2017–2026, with $7.25 commission plus 1 tick slippage per
market fill ($20/point), a target that fills only on a 1-point trade-through, and contract-roll nights dropped. Same
period split as the author.

| Period | Nights | Avg / night | t | PF |
|---|---|---|---|---|
| Design 2017 – Oct 2022 | 792 | $107 | 2.78 | 1.31 |
| Out of sample 1: to 2023 | 196 | $105 | 1.41 | 1.27 |
| **Out of sample 2: 2024 +** | **448** | **$42** | **0.47** | **1.07** |

(`overnight_nq.py`, standalone version. My main research pipeline gives the same picture: t 2.55 / 1.59 / 0.75 on 805 /
200 / 444 nights; the small differences come from simpler roll detection here.)

**Verdict: rejected for trading.**
1. **The edge decayed:** t 2.8 in design, about 0.5 since 2024: the McLean-Pontiff pattern of published effects fading.
2. **The R² filter adds little:** without it, all nights earn about a third as much at t ≈ 1, so most of the claimed edge
   is a plain overnight premium, not the filter.
3. **It can't be made safe:** with no stop, the worst single night lost $11,402 per contract, far beyond a prop account's
   $2,000-4,000 drawdown limit. Adding a stop at 0.5 × ATR turns 2024+ negative (t −0.15).
4. **Selection:** ~7.3 million configurations searched; a t of 5 from that many tries is roughly what noise produces.

**What I'd need to change my mind:** a version with a bounded loss that holds t ≥ 2 on data after 2024.

Run: `python3 overnight_nq.py 'NQ_1min_*.csv'` (data not included) or `python3 overnight_nq.py --selftest`.
