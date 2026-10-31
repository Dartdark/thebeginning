# Vault Break recent risk and brackets: TEST for a bounded diagnostic

Summary: Audit whether the reported recent weakness is unusual against the unchanged strategy's history.
Test four fixed bracket alternatives to the existing 40-point target / 75-point stop.
Historical OHLC and the saved replay end 2026-10-09; later day bars lack matching overnight exports.
Archived chart logs are incomplete and are not verified broker fills. No live-setting change is authorized.

Date: 2026-10-25. Existing strategy, not a new forced-flow hypothesis or a promotion.
Parent evidence: `results/vb_parity_stress.md`, `results/break_vb_onb.md`, `DEVELOPMENT_PROCESS.md` parameter tests.
Previous work: 720 historical parameter combinations and 314 frozen robustness stresses are disclosed context.
New planned economic models: baseline plus four bracket alternatives, committed in the accompanying plan before returns.

1. **Who/why:** The existing long-only NQ noise/VWAP breakout is an empirical price strategy. No new claim that
   someone is forced to buy NQ, or that a wider stop itself creates an edge. This work checks degradation and payoff shape.
2. **Known before entry:** The original prior ATR, midnight anchor, decision clock, position cap and holiday rules stay
   fixed. Stop/target distances below are fixed before any return calculation, not fitted to the recent losing window.
3. **Instrument:** NQ in the replay, with explicit native MNQ fee scenarios for risk illustrations. No SPY transmission claim.
4. **Data:** Existing `scratch_data/g24.pkl`, raw NQ exports, archived MC report and saved baseline ledger; no cache rebuild.
   Recent broker execution ledger and complete post-October-9 overnight data remain missing. Chart CLOSE rows cannot fill that gap.
5. **Costs/gaps:** Retain the reviewed NQ commission/slippage and one-point target trade-through. Native MNQ uses explicit
   fee scenarios; never infer its commission by dividing NQ's. Same equity exposure as the existing VB slot; no diversification claim.
6. **Power:** Roughly two months is a short diagnostic, not evidence to fit a replacement. Report actual eligible days/trades,
   matched-length historical tails and block-resampling uncertainty. Do not call a non-significant result proof of stability.
7. **Falsifiers/failure:** Recent weakness can reflect signal deterioration, unlucky sequencing, missing/rejected fills or wrong
   timing/sizing. The alternatives fail if they lose their apparent benefit on fixed historical validation or only help recently.
   Tighter stops can convert recoveries into losses; larger targets can surrender winners. Test all eligible sessions.

The optimization is a bounded screen. A five-setting grid cannot establish a broad optimal plateau or justify a live change.
Any passing case still requires execution stress, appropriate account comparisons and independent review before promotion.
