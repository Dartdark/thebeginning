# R2Vault: TEST
Summary: Reconstruct the uploaded low-R² breakout and test its incremental value in all five account/plan contexts.
The PDF supplies price rules and a reported gross edge, but no independently verified forced flow or executable source.
Timezone, history template and order semantics require explicit frozen assumptions; exact author replication is unavailable.
Return trials before this sheet: zero Codex R2Vault trials; author reports two versions, total prior search unknown.

Source: `agents/codex/inputs/r2vault/source.pdf`, SHA256 `60742409a30d91902d26bdd0c15b39cb229db13f26394fc4ee86a316872da107`.
Source-only audits: `results/r2vault_source_audit.md`, `results/r2vault_plan_context.md`.
Current Claude reference: `172322e5151f45e2cbf1da4dbd9efb20ba12d1a9`; current branch codex/work.

## 1. Participants and mechanism
The hypothesized participant is a breakout buyer after a weak linear price trend, not an identified mandated buyer.
No independent position, forced hedge or dollar-flow data establish urgency. Low R² is a price statistic, not proof
of compressed volatility or stored orders. Prediction: long breakouts above a recent low-R² candle with positive
576-bar slope have positive net expectancy and can diversify the existing plan. This is a testable price hypothesis.

## 2. Information before entry
Completed observed five-minute closes determine OLS slope and R² over 576 bars. A qualifying bar replaces the vault
with that bar's high/low. A next-bar buy stop is 20% of vault range above the high, rounded up to a valid tick.
Direction and price are known before the next bar. Source session is 09:30–15:30 with timezone unstated; ET and CT
interpretations are fixed before returns. There is no measured exogenous flow size.

## 3. Transmission
Rules trade NQ directly and are scaled to MNQ by preserving points, not by retaining NQ dollar stops on a micro.
No independent futures-demand transmission claim is established. Price response can disappear after costs.

## 4. Data feasibility
| Input | Source | Coverage/timing | Availability |
|---|---|---|---|
| Rule and reported results | Archived supplied 10-page PDF | 2017–Aug2026 claimed; no code/ledger | User supplied |
| NQ OHLC | Existing scratch_data/g24.pkl, Grid24 | Observed minute bars, CT; usable RTH2018–2026-10-09 | Existing owned cache; no rebuild |
| Current plans and components | Latest Claude blobs; pinned prepared Anson baseline | Verified47 unchanged blobs at172322e | Existing research inputs |
| Personal14 daily baseline | Existing anson_personal_baseline.pkl | Published16CT daily marks | Reuse with inherited limitations |
Full-session576 observed closes are a declared reconstruction assumption. No future bars fill missing data.
Previously examined2023+ repository history is historical replication, not a fresh untouched holdout.

## 5. Costs and portfolio gaps
PDF claims $105.55/NQ average, versus ordinary two market/stop-fill costs about $20.40/NQ-equivalent at fee1.04/MNQ.
This clears only a cheap feasibility screen; claimed adjusted profit is a statistical adjustment, not costs.
Target winners avoid exit market slippage but require a one-point trade-through. Proposed geometry is75point stop,
40point target: $150/$80 perMNQ before gaps/costs. No break-even. Personal can carry; Apex must flatten.
VaultBreak is the nearest shared breakout exposure. Test all eligible events; overlap/account timing is measured later.
Do not select events based on existing plan being flat. Baseline occupancy and minute paths are already available.

## 6. Power
Author2518 trades over9.6years suggests order1300 design-period trades before reconstruction losses; unverified.
An assumed binary $800/$1500 NQ payoff with70% winners has SD about$1054; at n1300, t2 needs about$58.5 net/trade,
or about$79 gross after ordinary costs. Clustering raises the hurdle. Actual effective sample and multiple-test
threshold will be reported. This plausible-but-narrow margin warrants one bounded reproduction, not optimization.

## 7. Prior work and falsifiers
Latest source inventory finds no exact576/.030 R2Vault strategy. Existing VaultBreak shares breakout/long risk.
Reject promotion if net recent performance is weak, multiple-test gates/placebos fail, or paired account benefit is
absent. Timezone disagreement is model uncertainty, not permission to pick the winner. No parameter rescue search.

## 8. Failure and diversification
| Question | Prediction | Required evidence |
|---|---|---|
| Failure | False breaks, low-R² not a useful regime, costs consume expectancy | Net cohorts/placebos |
| Liquidity role | Buy stops consume liquidity; target limits can miss | Gap-aware replay and target trade-through |
| Loss clustering | Several75point stops/day; gaps and overnight positions | Minute adverse paths, joint losses, MTM |
| Shared losses | VaultBreak and other NQ long exposures may fail together | Correlation, joint negative days, overlap |
| Offset before breach | No assumed timely hedge | Chronological paired account replay |
One candidate position; at most3 actual entries/CTdate; no pyramiding. Max tested candidate4MNQ150K,
2MNQ50K, personal1/2MNQ. Stops do not guarantee loss caps. Unknown in-session minute gaps invalidate corresponding
Apex account days/windows. Personal uses observable stale marks with gap disclosures, not future prices.

## Decision
**TEST** — user explicitly requests reconstruction and all-plan backtesting; source is implementable with bounded,
visible assumptions. Commit the preregistration before any strategy returns. No live or plan changes authorized.
