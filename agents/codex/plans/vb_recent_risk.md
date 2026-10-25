# Vault Break recent drawdown and bounded bracket screen

Date: 2026-10-25. Commit before computing new recent summaries or alternative returns.
Evidence: `agents/codex/evidence/vb_recent_risk.md`.
User authorized both recent backtest/account audit and an optimization check. No orders, live strategy changes, VPS,
broker settings, API keys, cache rebuild, PR #2 or other-agent branch changes.

## Questions and source boundary

1. Is the last roughly two calendar months' unchanged-strategy drawdown unusual against earlier history?
2. Do archived actual-account records establish agreement with the backtest? Missing coverage stays unknown.
3. Does a prespecified smaller stop or larger target produce a material, stable improvement on design and validation?

Requested recent window: **2026-08-25 through 2026-10-25**, inclusive. Use all observed eligible sessions, retaining
2026-10-09 as the currently verified complete-history cutoff. Do not zero-fill unobserved later sessions.
Report August/September/October separately, labeling partial months. A secondary 42-session window ending at the
complete cutoff may be shown, explicitly distinguished from the user's requested window.
Historical data/parameters have previously been examined; 2023+ is historical validation, not fresh holdout.

Use existing Grid24 and the reviewed VB accelerated replay/engine without editing their sources. Reproduce the
one-point research baseline trade-by-trade against the saved ledger before alternatives. Use the existing .25-point
parity ledger / MC report as a reference sensitivity only. No fill convention may be selected by its returns.
If new local raw data lacks overnight history needed for midnight anchors/ATR, inventory it but do not patch it
into the complete cache or invent missing data. Hash used inputs. Do not overwrite prior ledgers or shared caches.

Read archived chart/order reports only. Deduplicate exact repeated chart rows within tags, then show account copies
separately. Do not add account copies as independent market signals, equate chart labels with broker clocks,
infer missing fees, or treat strategy-chart CLOSE rows as proof of executed broker exits.

## Fixed economic models: five total, four alternatives

All use original entries, midnight ATR/VWAP, 10:00 first decision, last/flat 14:30 CT, early-close handling and max 3/day.
Exits and re-entry sequences must be recomputed for each bracket; do not reuse baseline entries after an altered exit.

| ID | Target points | Stop points | Prior reason |
|---|---:|---:|---|
| BASE | 40 | 75 | Existing reference |
| S60 | 40 | 60 | Moderately reduce loss per stop |
| S50 | 40 | 50 | Larger stop reduction, with recovery/win-rate tradeoff |
| T50 | 50 | 75 | Modestly increase full-win size |
| T60 | 60 | 75 | Larger reward target; previously investigated, not a novel discovery |

No extra indicator, timing, side, threshold, day-of-week, volatility, stop-management or sizing variants.
Costs: per NQ $7.25 round-trip plus one adverse tick at market entry and market/stop exit; no extra slip on target exits.
Target requires one full point through, with existing gap/path semantics. Native-MNQ risk illustration uses $2/point,
one adverse tick per market/stop fill, explicit RT-fee scenarios $1.04 and $1.24, never scaled mini commissions.
These fee scenarios are inherited research assumptions, not verified current-account charges.

## Recent degradation diagnostic

Compute trades, win rate, average win/loss, payoff ratio, net/trade, PF, t, daily standard metrics, stop/target/time-exit
shares, maximum losing streak, in-window trade/EOD drawdown and drawdown carried into the window from the prior peak.
All=long; short results explicitly N/A. No isolated subperiod is a new eligible filter.

Compare the observed N-session net and in-window EOD drawdown with every earlier N-session window ending before
2026-08-25. Show 2018-22 reference and all pre-window reference separately; overlapping-window ranks are descriptive.
Also use 5,000 ten-session block-bootstrap paths from each earlier pool, fixed seed 20261025, at the same N.
Report lower-tail net and upper-tail drawdown frequencies and a 90% bootstrap interval for recent-minus-prior mean.

- **Unusually weak / investigate deterioration:** lower-tail net <=5% and upper endpoint of the recent-minus-prior
  mean interval <0. This is conditional historical evidence, not proof of permanent edge loss.
- **Within historical range / inconclusive on deterioration:** neither net nor drawdown is in its adverse 5% tail.
- **WATCH:** other cases, or missing data prevents a current-account conclusion.

Account execution conclusions require complete verified fills for the actual compared dates/strategy/account. If absent,
say so and list exact missing inputs. Never treat incomplete archived logs as a healthy or deteriorating full account.

## Design-first optimization gates

Run BASE and all four alternatives on **2018-22 first**. Log all settings/failures and save the design gate before
running any alternative on 2023+. A cheap-screen survivor needs positive net, trade t>=2, PF>=1.20, >=4/5 positive
design years, and Calmar at least BASE. It must also meet one of:

- trade-level max DD <=85% of BASE with total net >=95% of BASE; or
- total net >=115% of BASE with trade-level max DD <=105% of BASE.

Trade and EOD DD both reported; the gate uses trade DD so intraday stopped trades are not hidden by a later recovery.
No survivor => stop optimization after the cheap screen. Do not select a recent-window winner as a rescue.
For ranking context use the repo's top-20% / normalized-cluster medoid method and fixed 2018-20, 2019-21, 2020-22
fold summaries. With only five settings the top set may contain one setting; it cannot establish plateau stability.
No grid expansion or chosen setting follows from a singleton cluster.

Only survivors receive one 2023+ historical-validation replay, with full/year/side metrics, 5,000-run ten-day
bootstrap/permutation summaries, paired bootstrap of improvement versus BASE, and the same 42-session/recent slices.
Require positive validation net and paired improvement in the same design objective; recent improvement alone is insufficient.
Report multiple testing against prior strategy trial count plus these four alternatives, including DSR / t threshold.
Repeatability of former settings is not fresh independent evidence.

## Conditional later checks

Only a survivor that retains its improvement on validation and the three design folds can advance to fixed execution
stress (extra tick and stricter target-through), random-entry/side controls, Monte Carlo at native micro sizes and
account replacement comparisons using existing funded/evaluation tools. Log stress scenarios separately from economic
models; none can be selected as a better strategy. Compare existing plan, VB replacement, addition and empty VB slot
where applicable. A conditional gate failure stops those expensive checks and is itself a completed negative screen.
No trading-plan or code change without independent review and a concrete supported benefit.

## Deliverables

`analysis/codex_vb_recent_risk.py`, new outputs under `analysis/outputs/codex_vb_recent_risk/`, and concise
`agents/codex/results/vb_recent_risk.md` with Summary <=5 lines. Include coverage/provenance, exact tail definitions,
monthly/recent tables, gross vs costs, win/loss arithmetic, all trials, optimization stop reasons and applicability limits.
Use ordinary plot files for equity/drawdown and recent historical comparisons if they aid interpretation.
Commit/push only `codex/work`; give Claude the result path.
