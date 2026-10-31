# NQ Day Flow Six: frozen one-variant composite

2026-10-25. Evidence: `../evidence/nq_day_flow6.md`. Commit before new composite returns.
User accepts composites. Target: net trade t, daily iid t and daily Newey-West(5) t all >=6;
NW(20) is a disclosed sensitivity. A sub-threshold result is a failed target, not permission to refit.

## Fixed rule and sources

Six unchanged strategies, one MNQ per strategy ticket, long and short settings unchanged:

| Sleeve | Report under mc_reports/ | Source |
|---|---|---|
| VB | Backtesting Strategy Performance Report VB v1.xlsx | apex_strategies/NQ_Vault_Break.txt |
| ONB | Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx | funded_strategies/NQ_Overnight_Bias_ML.txt |
| MON | Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx | funded_strategies/NQ_Monday_Long.txt |
| EOS | Backtesting Strategy Performance Report EOS v1.xlsx | funded_strategies/NQ_Expiration_Open_Short.txt |
| LDF | Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx | funded_strategies/NQ_Late_Day_Flow.txt |
| NFP | Backtesting Strategy Performance Report _ @NQ - 5 Minutes NFP Fade.xlsx | funded_strategies/NQ_NFP_Fade.txt |

This is the six intraday legs in the existing seven-leg alpha study, excluding overnight Bridge Monday.
One configuration, no leave-one-out selection, optimised risk balancing, regime gate or weight search.
VB one contract makes its current normal/flagged one/one distinction immaterial. Other current plan
differences (50K Monday replaced by OT, etc.) remain; this is not a claim to copy the adopted account plan.

Use repository `Grid24` in memory; no cache exists here and none will be saved/rebuilt unnecessarily.
Use `portfolio.load_mc` for mapping, cross-check paired raw workbook gross P&L, entry/exit date/side/quantity,
and inventory mapping/coverage exceptions. Truncate the study by source entry AND exit dates to the
fixed 2018-01-01--2026-10-09 window; report all later source rows excluded for unavailable price history.
Retain all within-window trades. Do not delete missing-price/holiday/roll events to improve returns.
Aggregate realized P&L by actual exit session; all six are intended intraday. Map overlapping legs
as virtual positions with actual target net quantity equal to the sum. Gross ticket costs are conservative;
intraminute combined fills are not verified by individual reports. Never send orders.

## Costs and statistical gate

Primary: MNQ $1.24 RT plus $0.50 per market/stop fill. Sensitivity $1.04; fixed stress four adverse
ticks per slipped fill instead of one. Reference NQ $7.25 RT, $5 per slipped fill. No scaled NQ fees.
One slipped entry per ticket; exit slips unless source target. No return-selected cost or fill convention.

Run design 2018-22 ONLY first. Cheap gate: >=300 component tickets; positive total; daily iid t>=3;
daily NW(5) t>=2.5; trade PF>=1.20; >=4 positive design years. If it fails, stop before validation/accounts.
Commit/save design summary, then run unchanged 2023--October 9, 2026 historical validation once if passed.
It is not a clean holdout: constituents, model, and related books were already selected on these years.

Report all/long/short standard repo metrics, component-ticket t, all-session daily t, NW(5), NW(20),
DSR at current item count+1 and 10,000, by year/design/validation/full. Count actual tickets, days and
maximum concurrent virtual gross/net contracts separately. Do not treat contracts as observations.
Daily ratios include non-trading sessions; prepend initial zero only for drawdown bookkeeping, not sample count.
Zero-trade side ratios N/A. Multiple-test sensitivities do not undo component selection.

## Diagnostics and account/portfolio controls, only after cheap pass

Use `resampling` 5,000 ten-session bootstrap paths and 5,000 day permutations for full/validation,
whole and sides. Use 10,000 `montecarlo.trade_mc` draws (descriptive because tickets overlap), and
5,000 one-year `montecarlo.daily_mc` paths with $2k and $4k EOD trails at the fixed whole-micro size.
Report initial-zero drawdown correctly. These EOD-only standalone risks are not account pass/payout forecasts.

Statistical placebo: 2,000 session-level sign flips of gross P&L, preserving all within-session legs
and subtracting costs unchanged. Also report long/short directions. This tests a zero-mean return null;
it is NOT a random-entry execution placebo, whose inherited component studies must be named separately.
No new filter or random-drop selection is introduced. Existing one-point-through assumptions and report
settings are documented; do not change source prices to force combined platform parity.

Personal: baseline afde088 19-leg snapshot, fee1.24; BASE, ADD one six-sleeve basket, REPLACE the six
matching baseline columns with the basket, EMPTY remove those six. Same one-MNQ executable weights,
1,000 paired 252-session ten-day blocks; preserve dependence across all legs. Report increments,
DD95, profit/DD95, correlation and candidate net on book-loss days. Starter A-D same controls, replacing
only the matching components present, adding the full composite; label changed exposure explicitly.
No fitted scale-to-DD. Current plan fee/booking differences can make REPLACE change P&L despite
matching labels; reconcile and do not present accounting cleanup as new alpha.

50K/150K evaluation/funded: first report EOD-only standalone risk. Full current-book ADD/REPLACE/EMPTY
pass/payout claims require valid joint intraday paths, including overnight baselines. Missing caches
and known causal overnight chronology gaps are explicit LIMITS; do not invent account improvement.
Current six existing components imply substantial duplication. No automatic allocation recommendation.

## Deliverables and stopping

`analysis/codex_nq_day_flow6.py`, `analysis/outputs/codex_nq_day_flow6/`,
`agents/codex/results/nq_day_flow6.md`, and a frozen specification suitable for independent review.
Preserve exact source hashes and runtime versions. Commit/push codex/work only, pull before push.
No new PowerLanguage until the implementation passes; passing individual MC reports is not a combined
manager pass. Any deployable combined version needs virtual-sleeve order ownership and independent
checks of same-symbol netting, stale exits and same-bar fills. Do not modify existing/live code.
No ranks, allocations, shared plans, root TODO, broker/VPS/API settings, purchases or messages.
