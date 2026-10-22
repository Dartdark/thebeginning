# Late-Day Flow asset-weighted sizing — exploratory preregistration

Summary: Freeze one 1/2/3 MNQ sizing rule against the current 2 MNQ LDF before inspecting flow-conditioned returns.
Use prior fund assets and lagged NQ liquidity; ranks and controls address momentum and secular growth.
Run 2018-22 first; any failed gate stops without 2023+ returns or a funded simulation.
Publication/revision uncertainty is accepted for an exploratory D-1 screen with mandatory D-2 stress.
Amended before returns per review 075254b: later start if warmup absent, momentum controls, dated snapshots.

Date: 2026-10-22. Branch: `codex/work`. Source audit: Claude `c23fc02`; review: `075254b`.
Evidence: `agents/codex/evidence/ldf_flow_sizing.md` (TEST, exploratory only).
The user's 2026-10-22 instruction adopts the review's three changes and authorizes the design screen.

## Question, mechanism and scope

Does fund-asset-weighted reset capacity relative to expected liquidity improve existing LDF sizing beyond
its price signal? Under a fixed-capital approximation, daily resets produce same-direction demand
`K*r`, where `K=sum[L*(L-1)*A]`. Counterparties may hedge in NQ/QQQ. Offset by fund capital flows,
pre-hedging, execution elsewhere and anticipatory price adjustment can eliminate the proposed effect.
No claim of observable residual orders or forced directional futures execution is made.

This is an LDF replacement/upgrade, not an independent strategy. Do not alter entries, directions,
stops, exits, calendars or another funded line. Include ALL existing LDF entries, not only roster-flat dates.
An optional full-sample descriptive mechanism study is outside this protocol; do not run it first or use
its findings to select this rule. Previously seen 2023+ history is a replication period, not pristine validation.

## Frozen baseline and inputs

- Current 50K roster from accepted marginal study: VB normal/flagged 2/1 MNQ; ONB ML v2 $400 risk;
  Monday 1 MNQ; EOS $700; LDF 2 MNQ; NFP $500; Bridge Monday 1 MNQ; CL Sunday 2 MCL;
  ES MOC **2 MES**; Relative Strength longs 1 MNQ. Cushion factor 0.5-1, reference $1,500.
- LDF source: `mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx`.
  Existing rule: >=0.4 lagged ATR RTH move at 14:00, follow next bar, stop 0.25 lagged ATR,
  time exit 14:30 CT. MC entry/exit mapping and fills stay identical to the accepted loader.
- Freeze hashes of that report, the four fund blobs at `c23fc02`, NQ raw files/cache and the actual
  baseline script before execution. Reconcile baseline entries with the accepted report before proceeding.
  Reuse configured `/workspace/venvs/thebeginning/bin/python`, existing Grid24 and lab caches.
  Do not silently rebuild caches or substitute an unreviewed reconstructed strategy.
- Historical evaluation ends at the last common available NQ/LDF date, capped at 2026-10-09.
  Newer issuer rows cannot enlarge the futures evaluation period. 2017 inputs may warm up features only.

## Data gate before strategy returns

Inventory may read fund NAV/assets/shares and MC entry dates only; it must not read strategy P&L or build signals.
Verify units, splits, duplicates, positive assets, NAV*shares identity, calendar gaps and current snapshot hashes.
Reconcile missing fund rows with the historical US cash calendar; closed-market days are not data failures.
Do not assert unusual share changes are capital flows without checking corporate actions.

Per accepted review 075254b, D-1 assets plus mandatory two-NAV-session lag stress suffice to run an
**exploratory design screen**. Historical publication times/revisions remain unverified; do not label the
snapshot proven point-in-time or the result validated for trading. Two-session lag does not solve revisions.
Begin archiving dated raw fund snapshots now, with UTC storage/retrieval time, source URL and SHA256.
Distinguish a fresh issuer download from a copy of Claude's supplied git snapshot; a stored git copy cannot
masquerade as our observation of the issuer's publication time. Forward records must identify what actually
arrived before each decision. A historical pass remains WATCH pending review and prospective evidence.

## Pre-return amendment: warmup and momentum (review 075254b)

The 2017 file currently present is **overnight only**. No 2017 daytime volume is assumed. At registration,
neither local HEAD nor review 075254b contains `data/NQ_1min_2017.csv`. The user may export it separately;
this run selects the allowed **later-start alternative** so its absence does not force a coverage rejection.
Do not splice in a later-arriving export after outcomes are opened or silently rerun the full 2018 design.

Construct market inputs over 2018-22 only (plus earlier available observations), without LDF outcomes.
The evaluation begins at the **first US cash session with primary and lag-stress scores AND finite
trailing-63/252-session NQ returns**, and ends 2022-12-31. Count all earlier original 2018-22 LDF entries as
warmup exclusions, never as losses or unavailable-score fallback trades in the selected later window.
Do not evaluate their P&L. The 252-session control needs a full daytime year; expect the start in 2019.
Record the exact resulting start and support before opening any LDF return.

Use the installed `exchange_calendars` XNYS schedule for sessions, mourning days and official half-day closes.
Momentum controls are known at day-D decision: `C_s/C_(s-63)-1` and `C_s/C_(s-252)-1`, where s is D's previous
cash session and C is NQ's minute close at that session's official US cash close (15:00 CT, 12:00 on half days).
Require all 64/253 close observations respectively; no fill of missing closes. These continuous-contract price
ratios are trend proxies, not roll-adjusted investable returns; identify this limitation and flag roll-window volume.
Before outcomes, report Pearson/Spearman correlations of the rolling H percentile rank with both controls,
group-year counts, control means by low/middle/high, score coverage and roll-Thursday/Friday volume diagnostics.
Save that return-free checkpoint separately before evaluating strategy P&L.

The later window replaces gate 1's five-design-year representation requirement with representation in **every
calendar year in the registered evaluation window**. Retain >=90% score coverage and >=100 entries in each
extreme group. Gates 2/3 retain >=3 positive years, now out of the years actually evaluated. No lowered numerical
significance, return, cost or placebo hurdle. List the reduced sample and updated power estimate openly.
No parameter or start date is selected from LDF outcomes; a failed support gate stops without outcomes.

## One primary score, fixed before any outcome inspection

All dates and bar stamps use America/Chicago. At the established day-D 14:00 decision:

1. Let s be the most recent completed US cash-session date strictly before D. For each fund use direct
   AUM from s, not today's NAV, same-day shares, or today's creations/redemptions. An unexplained missing
   expected-session row in any fund makes the candidate score unavailable. Never backfill.
2. `K_D = 6*A_TQQQ,s + 12*A_SQQQ,s + 2*A_QLD,s + 6*A_QID,s`.
3. For each of the preceding 20 complete, regular cash sessions, compute NQ notional
   `V_s = sum[20 * close_minute * volume_minute]` for minute bars closing **14:01 through 15:00**.
   Require all 60 minute prices/volumes finite, prices positive and total volume positive. Skip known half days.
   Use the most recent 20 valid sessions from at most 40 preceding cash sessions; otherwise unavailable.
   `Vhat_D = median(V_s)`. Never use D's realized future volume or returns.
4. `H_D = 0.01*K_D / Vhat_D`: estimated reset notional per fixed 1% move divided by expected NQ liquidity.
   This intentionally holds the move size fixed: H is not total-day flow or an additional price-momentum signal.
   It avoids needing unavailable point-in-time NDX/QQQ intraday observations or overnight continuous-futures returns.
5. Compute the 1/3 and 2/3 linear-interpolated quantiles of H over the preceding **252 cash sessions**,
   excluding D; require >=126 valid scores. Low if strictly below lower quantile, high if strictly above upper,
   otherwise middle (ties middle). No whole-sample quantiles. Scores need no LDF trade on their historical date.
6. Primary base quantity: **low 1 MNQ / middle 2 / high 3**. Unavailable score: **2 MNQ**, with explicit reason.
   Mandatory lag stress repeats the exact algorithm using the second-most-recent cash-session asset row at
   each historical decision. No reoptimization. Both versions use the same completed historical volume windows.

Only accepted LDF positions are resized; the existing LDF side supplies direction. No trade on a new date.
Rolling ranks are part of the frozen rule, not a retrospective fit. Log actual absolute RTH return,
move/lagged-ATR, side and year for confounding checks. These use observations available at the entry decision.

## Configuration and trial budget — five configurations, no search

| ID | LDF base quantity before cushion rounding | Purpose |
|---|---|---|
| B | 2 | Accepted baseline |
| R | 1/2/3 from primary H; missing 2 | Sole selectable replacement |
| S | Same rule with two-NAV-session asset lag | Mandatory timing stress; never a fallback winner |
| A | 2 + R, i.e. 3/4/5; missing 4 | Required addition comparison, diagnostic only |
| E | 0 | Empty-slot control |

Conservatively record R, S and A as three nonbaseline configurations if evaluated, including failures;
report B/E as controls and separately disclose every placebo. Only R can advance. A duplicates LDF
exposure and is not diversification; it cannot rescue R. No alternate thresholds, ranks, directions,
lookbacks, fund subsets, exits, size maps or side filters. Each later modification needs a new dated plan/trial.
Return trials at registration: **0**. Do not modify the shared trials log; give Claude the local ledger.

## Cheap 2018-22 design screen and hard stop

First count eligible entries and extreme groups without returns. The inventory gives the exact accepted
design entry count and IID planning hurdles assuming $810 per-NQ trade SD from Claude's earlier sheet.
For n_high/n_low, the t=2 mean-gap hurdle is `2*810*sqrt(1/n_high+1/n_low)`; approximate 80% power uses
2.8 instead of 2. These are optimistic bounds, not estimates from these groups or proof of adequate power.
At ~450-500 total entries the required high/low difference is ~180-190 per NQ just to reach t=2.

Execute only the 2018-01-01 through 2022-12-31 screen, after the evidence gate permits it. Require ALL:

1. Valid primary scores on >=90% of baseline design entries; >=100 high and >=100 low entries, each represented
   in all five design years. Otherwise insufficient support: stop, never rescue by adding 2023+.
2. Primary resized LDF has positive total net, mean gross per NQ-equivalent round trip >=1.5*$17.25,
   and positive net in >=3/5 design years. Compute costs on every contract, not per trade irrespective of size.
3. Paired fixed-size incremental P&L `delta_i=(q_R,i-2)*net_NQ,i/10` has positive total, positive totals in >=3/5
   years and t>=2 using a Newey-West covariance with **5 trading-day lags**, on the full design daily series
   including zero-trade days. Also report the ordinary trade t and a paired 20-day block-bootstrap 90% interval;
   its lower bound must be >0. Resampling interval uses 5,000 replicates, seed 2026102201.
4. Confound-adjusted high-minus-low contrast >0 with robust t>=2: OLS of per-NQ trade net on intercept,
   high/low indicators (middle reference), absolute RTH percentage move, absolute move/lagged ATR,
lagged ATR/entry reference price, **trailing 63- and 252-session NQ returns**, side and calendar-year fixed
effects. Test high coefficient minus low.
   Newey-West 5 entry-observation lags; also show unadjusted group counts/SD/means and condition diagnostics.
   Singular/rank-deficient design or absent within-year contrast means no demonstrated incremental information.
5. Match randomized size assignments within **year x side x move/ATR tercile x trailing-63-return tercile**;
   each tercile dimension uses that design year's eligible signal values independently, without outcomes.
   Tercile boundaries use only
   that design year's signal values, never outcomes, for this placebo only. Preserve each cell's exact counts
   of 1/2/3 quantities; keep unavailable-score fallback fixed. Use 2,000 permutations, seed 2026102202.
   Require one-sided plus-one p<=.05 on total paired incremental net AND no worse design max DD than
   the median shuffled sizing. Report cell sizes and the full null distribution. Do not silently pool sparse cells.
6. S, the mandatory lag stress, has positive total incremental net and positive adjusted high-minus-low contrast.
   No alternate winner if R fails. A one-day-only result remains WATCH for timing sensitivity.

On any failure: report REJECT (or WATCH for unresolved data/timing), count the executed configurations,
and STOP. No new 2023+ scores/returns, full-sample mechanism study, funded simulations, parameter rescue
or negative-direction test. A nonsignificant result is not proof that LETF flows have no market effect.

## Only after design passes: replication and account gate

Freeze design outputs, implementation hash and result before the one planned 2023+ evaluation.
Require positive paired incremental net, positive adjusted high-minus-low contrast, positive lag-stress
incremental net, 90% paired block-bootstrap lower bound on incremental mean >0, and the same matched
placebo p<=.05. No year-specific or side-specific rescue. Report 2023+ as already-seen historical replication.

Only then use accepted account tools, not a new simulator. Reproduce B on the accepted roster first;
account numbers that differ from the marginal study must be explained before interpreting a gain.
Use 2,000 paired circular 20-day histories separately for design, replication and full history, 500-day horizon,
250-day year-1 checkpoint, seeds 2026102203/04/05 respectively. Keep all strategies on the same sampled day.
Resample each precomputed day's score/size with that day's paths; do not recompute ranks on shuffled dates.
Run B/R/S/A/E. Use the existing cushion and **floor(base_quantity*cushion_factor)** rounding unchanged.
Do not floor the two addition pieces independently or send opposing strategy orders as an artificial hedge.

R must improve mean year-1 and year-2 payouts over B, with a positive 90% paired uncertainty interval
on the expected year-1 gain; blow-ups may rise by <=1 percentage point; all-six probability may not fall;
median time to six payouts may not increase. Apply these gates separately to design and replication pools.
For the mean-gain interval, bootstrap paired history differences 5,000 times (seed 2026102206); distinguish
this Monte Carlo uncertainty from uncertainty in market history. Also report paired outcome quantiles
and baseline-relative wins/ties. Ten- and 60-day block sensitivity must preserve the signs of payout gains
and the blow-up budget. Historical inference remains conditional on the chosen data and rules.
Show R vs E, and A vs B/E, to distinguish LDF value from the resizing benefit; A cannot earn promotion.

Report conditional median days among six-payout completers AND completion probability; also report the
unconditional median with noncompleters at infinity. Do not hide failures by conditioning on survivors.
Run repository Monte Carlo at actual planned size and report one-year $2,000 trailing-DD hit probability.
Quantify incremental stop-dollar exposure, actual overlapping position minutes and costs at 1.5x baseline.

At a 0.5 cushion, a low-regime 1-MNQ base rounds to zero. This creates skipped LDF trades. List their
counterfactual baseline P&L and t, plus reduced/added contract-unit P&L. Apply the builder's filter checks:
the skipped trades must lose net and corresponding random removals must be beaten on total profit/DD;
report at least 2,000 matched removals. Never infer benefit from a higher kept-trade average alone.
If this cannot be reproduced consistently under state-dependent sizing, status stays WATCH.

## Reporting, forward evidence and boundaries

Use `analysis/metrics.py`, `resampling.py`, `montecarlo.py`, `funded_lab.py`, `funded_bootstrap.py` and the
accepted baseline reconstruction; extend only under allowed Codex paths. Explicitly verify no double slippage.
All/long/short: trades, win rate, gross/cost/net per full NQ and actual MNQ, t, Sharpe, Sortino, PF, Calmar,
Ulcer, max DD; yearly, 2018-22 and 2023+ tables, group counts, fallback dates, placebos and bootstrap intervals.
Report both fixed-size trade evidence and cushion-sized funded outcomes; neither substitutes for the other.
If actual micro commissions/fills differ from proportional research costs, obtain the applicable schedule
before a promotion claim and show sensitivity without selecting a new rule from it.

Even a historical pass stays WATCH until independent review, satisfactory data provenance and frozen
forward paper observation. Create `agents/codex/FORWARD_LOG.md` only after a pass, with rule/code/data hashes,
freeze date and timestamped issuer snapshots; append at Friday reviews. Minimum forward review point:
40 qualifying LDF entries AND six calendar months, with positive incremental net, high/low spread >0,
no adverse drift alarm and acceptable account risk. That review is not automatic authorization to trade.
This amendment authorizes the exploratory design screen and snapshot archive, not live changes, purchases,
external messages, an optional mechanism study or parameter rescue. Follow the existing hard stop on failure.
