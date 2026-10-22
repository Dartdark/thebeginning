# Claude's review: VB parity + stress (f7f0e8e) and the ES Keltner screen (9c73935)

Written by Claude, 2026-10-22.

## 1. VB parity and stress: accepted. VB is as robust as ONB; no change
- **Parity solved under the original gate:** with the 1-tick target rule, 1,736 / 1,743 MC entries match (99.6%),
  matched gross P&L identical to the cent, correlation 1.000. The amendment was registered first (efcd75e) and the
  1-tick rule was used only for parity. Done exactly as asked.
- **Stress (1-point research rule):** noise, indicators, timing and execution all BEND; joint ±10% jitter MIXED
  (2023+ median Sharpe 0.58 vs 1.26, 99% profitable). Same pattern as ONB, same reading: the jitter moves the
  session clock (first entry 09:00-11:00, flat 13:00-15:30), so it tests other strategies, not small errors.
- Entering one bar (30 min) later weakens 2023+ (Sharpe 0.62). Live VB enters at the next bar's open after the
  decision, so that case doesn't describe live risk. It does say the signal decays within 30 minutes: a rejected or
  missed order should not be re-sent late (consistent with the 10/20 rejection, which was correctly left alone).
- Side note: our 1-point research rule understates VB by about $7 a trade vs MultiCharts ($82 vs $89 per NQ,
  2018-26). Conservative; it stays the standard.

## 2. ES Keltner: F for this version (a legitimate exploratory test)
- **Correction:** the user asked Codex to fill in the missing settings with its own choices to see whether a strategy
  came out of it. So testing it was right; my first version of this review blamed Codex for it, wrongly.
- The result is clean: the chosen rule loses before costs (gross −$27.50 a trade, t −4.2, both sides, every year),
  and Codex stopped at the design gate without searching for a better setting. That was the right stop.
- What it covers: 30-min daytime bars, flat 15:00, momentum 20 / 20, threshold 50 (which reduces to 'close crosses
  its 5-bar SMA'). It doesn't cover Davey's own overnight version with his settings, so the personal-account idea
  stays open until those arrive.

## Message for Codex
```
Reviews: agents/codex/results/REVIEW_vb_parity_and_keltner.md (claude branch).
VB parity + stress accepted (99.6% at 1 tick; jitter MIXED like ONB; no change). Good work.
ES Keltner: ranked F for your chosen version; clean test and the right stop at the design gate. (My first note blamed
you for guessing settings; the user had asked for exactly that. Withdrawn.) Davey's own overnight version stays open.
Next: nothing new queued. Stay on live reconciliation (Friday export arrives 10/23).
```
