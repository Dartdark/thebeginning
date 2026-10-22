# Codex test grades (Claude, 2026-10-22)

Both tests run blind on `codex/tests` (repo before Claude's VB Combined review). Answer key: Claude's review
`agents/results/VB_COMBINED_REVIEW.md`.

| Test | Result | Notes |
|---|---|---|
| 01 Filter claim (VB Combined) | **PASS, all 6 key points** | Plan committed 21 min before results (6818838); REJECT; 2023+ −$13.2k vs base; removed trades +$43 (t 1.2); random-removal placebo incl. re-executed signals (beyond the key); 2 MNQ = $2,522; selection / holdout-gate problem; funded bench add / replace / empty-slot; MC parity 1,700 trades. Numbers identical to Claude's rebuild. Weakness: very long report. |
| 02 Code review (VB Combined PowerLanguage) | **PASS, all 7 key points** | Plan first (6fdb195); 30-min ATR CRITICAL; unprotected entry bar CRITICAL (+ Rithmic stop-guard fallback); holiday CRITICAL; trade counter MAJOR (correctly notes it is latent until the exits are fixed); warm-up, Ticks vs Volume, NumContracts; NO look-ahead; double midnight reset harmless (exact reasoning); corrected code with SetStopLoss / per-date ATR / holiday flat, disclosed as uncompiled. Slight over-severity: next-bar-open time exit rated MAJOR. |

Verdict: adopted as strategy builder from 2026-10-22, on branch `codex/work`, Claude checks every result before it
reaches TIER_LIST or the plan. Ask for a 5-line summary at the top of each report.
Side finding to recheck (Friday review): its funded bench had 'no VB at all' at 2y $12,132 vs current $12,062, blown
5.1% vs 7.0%, but 297 vs 257 days to 6 payouts (within noise; seen before).
