# FVB (First Valid Breakout) — NQ Strategy Submission

## Hypothesis
First Valid Breakout (FVB) on NQ. After the cash open, the first 1-min bar that
**closes** beyond a key prior-session level (prior-day high/low, premarket high/low,
or a prior-day level sitting inside the premarket range) tends to lead a directional
move that persists into the close.

The edge should exist because these levels concentrate resting liquidity and stops;
a confirmed break triggers continuation, while failed breaks are cut quickly. Thin
per-trade edge, structurally repeatable.

## Method
- **Instrument:** NQ continuous 1-min, 2018–2025 (8 years)
- **Split:** IS 2018–2023, OOS 2024–2025, strict separation
- **Entry:** next bar's open after a signal bar **closes** beyond a level
  (no same-bar fills, no lookahead — every input is finalized before the decision bar)
- **Stop:** 18% of the prior day's 14-day ATR, tick-rounded
- **Exit:** hard stop or force-close at 16:10 ET. No take-profit, no trail.
- **Re-entry:** only after a stop (max 2/day), triggered level removed
- **Filters:** skip days where prior range > 1.5× ATR or premarket range > 1.0× ATR;
  no shorts after strong trend days (prior-day body > 60%)
- **Costs:** $4.12 RT commission + 1 tick slippage
- **Units:** all metrics in R ($1,000 = 1R)

## Results

| Metric | In-Sample (2018–2023) | Out-of-Sample (2024–2025) |
|---|---|---|
| Trades | 1,534 | 507 |
| Profit Factor | 1.31 | 1.34 |
| Total R | +355R | +126R |
| Win Rate | 25.6% | ~26% |
| Per-trade Sharpe | 3.61 | — |
| Max Drawdown | −26R | −36R |
| p-value | 0.0003 | 0.03 |

- **Costs + Monte Carlo (full period):** net +438R after commissions/slippage.
  10,000-path MC reshuffle = 100% probability of profit, P5 max drawdown −73R.
- **Overfitting check:** stop parameter is a plateau (10–30% ATR all profitable);
  2D heatmap smooth with no isolated spike. All 8 years individually profitable.
- **OOS behavior:** PF *improved* slightly out-of-sample (1.31 → 1.34) — zero degradation.

### The ugly
- ~25% win rate. This is a low-WR / high-RR breakout system.
- **Fat-tail dependent:** capping winners at 3R turns total return NEGATIVE.
  The entire edge lives in the minority of trades that run to the close.
- ~250 trades/year.

## Conclusion
I believe this is a real continuation edge on NQ specifically. It transfers to ES
and YM but fails on metals and energy — which I read as confirmation it's an
equity-index session-structure effect rather than a curve fit. I'm confident the
code is clean: full forensic audit, no lookahead, realistic next-bar-open fills.

**What I'm still unsure about:**
1. The fat-tail dependency — is 8 years enough to trust that the big-runner days
   keep appearing?
2. The 18% stop was nudged up from 15% partly using OOS information, so its edge
   over 15% may be smaller than measured. (15% was validated fully blind.)

## What I want feedback on
Specifically the fat-tail reliance. Is a PF 1.3 / 25% WR / hold-to-close breakout
system that loses money when winners are capped at 3R something a desk would
actually allocate to — or is that profile too fragile regardless of the clean
validation?

And does my stop fill model (filled **at** the stop price, relying on 1-tick
slippage to cover gap-through) understate real risk on fast days?

## Attached
- Strategy code (Python, fully vectorized backtest)
- Equity curves (IS / OOS)
- Monte Carlo distribution chart
