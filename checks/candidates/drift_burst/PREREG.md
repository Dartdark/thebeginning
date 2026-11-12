# Drift-burst fade + order-flow turn (user 2026-11-12: combination 1 of 3)

Written 2026-11-12 BEFORE any return of this rule was computed. Papers: Christensen, Oomen & Renò, "The drift burst hypothesis"
(arXiv 2601.08974; engine) and Cont, Kukanov & Stoikov, "The price impact of order book events" (arXiv 1011.6402; ingredient).

- **Who pays (mechanism):** liquidity. A drift burst is a run of one-sided demand for immediacy that market makers absorb at a
  concession (Grossman-Miller 1988; Huang-Wang 2009); the price gives part of it back once the flow stops. The paper finds 65-78%
  of 5-minute reversals after the burst PEAK on CME futures 2012-17 (gold 78.1%, crude 71.3%), stronger after negative, high-volume
  bursts. The peak is only known afterwards: the tradeable question is how much reversal is left when the turn is CONFIRMED.
  Ingredient: price change is driven by order-flow imbalance at the best quotes (Cont et al.): if the aggressor flow has already
  turned against the burst, the one-sided demand has stopped.
- **Statistic (paper eq. 14, 1-minute bars, no pre-averaging):** r_i = 1-min log return; left exponential kernel K(x) = exp(x), x <= 0;
  mu_t = (1/h) sum K((t_i-1 - t)/h) r_i, sigma2_t = (1/h') sum K((t_i-1 - t)/h') r_i^2, h = 5 min, h' = 25 min (paper's bandwidths);
  T_t = sqrt(h / K2) mu_t / sigma_t, K2 = 1/2. Reset after any gap > 10 min; no value in the first 25 minutes after a reset.
  Contract-switch minutes (overnight_round.roll_minutes) get r = 0.
- **Event:** |T| crosses c = 4.5 (the paper's second critical value) from below; re-armed only after |T| < 2. Window 01:00-15:00 in
  the file clock (paper: 01:00-15:15 CT); NQ also 17:00-01:00 excluded.
- **Entries (fade = -sign(T); next bar's open, market):**
  - A first cross: on the crossing bar.
  - **B peak-confirmed (primary):** after the crossing, the first bar where |T| <= running max |T| since the crossing - 1.0, within
    15 minutes (else no trade).
  - **C (NQ only, 08:30-15:00 CT, data/OF_1min_* to 2026-07-07):** B + the confirming bar's aggressor delta (upvol - downvol, last 2
    bars summed) has the fade's sign: the order flow has turned.
- **Exits:** stop at the burst extreme (highest high for a short / lowest low for a long from 5 minutes before the crossing to the
  entry bar) + 1 tick; out at the close of the 5th bar after entry (the paper's 5-minute horizon). Information only: 15 / 30 minutes.
- **Markets:** GC, CL (the paper's highlighted), ES, NQ. Costs $7.25 NQ / $5 ES, GC, CL a contract + 1 tick per market / stop fill.
- **Variants judged:** B on GC, B on CL, C on NQ (3). A, B on ES / NQ, and the longer exits are information.
- **Bars:** design 2018-22: t >= 2.0, PF >= 1.15, >= 80 trades; holdout 2023+ (one look): same sign, t >= 1.5, PF >= 1.1; random-time
  placebo with the same exits (p < 0.05). Reference: the paper's look-ahead measure (reversal from the true peak) on our data.
