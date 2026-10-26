# NQ Cash-Open Repair: TEST for bounded new-rule research

Summary: The user requests a new standalone strategy, not a basket or renamed existing strategy, aiming for t>=6.
Test whether cash-open reversal repairs a large NQ-specific overnight move relative to ES.
Use new price-derived signals on 5/15-minute bars; no imported existing strategy trades or fitted ML weights.
This is an unproven cash-liquidity hypothesis; five fixed candidate/control configurations only.

Sources: repository db1c88b; current Claude 5d1096d. Read `analysis/relative_strength_test.py`,
`analysis/co_oc_reversal_test.py`, `analysis/anti_forced_flow_ideas_test.py`, relevant TIER_LIST rows,
`analysis/grid24.py`, `analysis/grid.py`, and `analysis/codex_s03_calendar.py`.
New return trials for this rule: zero. Related old RS/overnight/inventory searches are prior evidence, not ignored.

## 1. Participants and predicted mechanism

Cash stock baskets become broadly executable at 08:30 CT. Dealers/arbitrageurs and overnight futures
inventory holders can rebalance tech-index exposure against stocks or broad-index exposure then.
Hypothesis: an unusually large NQ-specific overnight displacement that begins reversing when cash
liquidity arrives can continue repairing during the morning. No known mandate forces this particular
direction, and no measured inventory is available. "Trapped traders" is a hypothesis, not an observed fact.

## 2. Available direction, size and timing

At today's 08:31-labeled open, compare NQ and ES returns from the preceding full cash session's 15:00 close.
Estimate NQ-on-ES overnight beta and residual dispersion using only the previous 60 matched observations.
Large positive residual predicts a possible short; negative a possible long, conditional on an actual
opposite-direction NQ opening bar. Decision at 08:35 or 08:45, next native minute open entry.
No flow dollar size/hedge fraction can be independently estimated from these price inputs; do not fabricate it.

## 3. Transmission

Trade NQ directly; ES is a contemporaneously known benchmark, not a second traded leg.
MNQ is independently fee-modeled. This is one position/entry rule, not the sum of old systems.

## 4. New information and data

NQ day/overnight and ES full-day minute files are committed through the joint October 9, 2026 cutoff.
Exact anchor bars, missing-input flags, prior-only beta/std and bar completeness can be checked without
forward P&L. No purchased input, key, account or external message is needed.
The new input is the prior-close-to-cash-open NQ-specific residual; existing RS uses an intraday residual
and follows it, whereas this rule fades an overnight residual only after a new cash-bar reversal.
The prior all-market CO-OC reversal and inventory-failure studies were negative, so these related stories
do not establish this rule. The unfiltered first-bar-momentum controls test whether the overnight input helps.

## 5. Costs and existing exposure

NQ primary commission $7.25 RT plus one tick ($5) per market/stop fill; target must trade one full point through.
MNQ primary $1.24 RT plus $0.50 per slipped fill, with $1.04 fee sensitivity if advanced.
Typical planned target 0.30 ATR, stop 0.15 ATR; economic feasibility must be measured, not inferred from distance.
Morning hours overlap ONB/RS/FC2B. No empty-window or hedge claim. All eligible events are tested regardless of plan positions.

## 6. Power

Assumptions only: roughly 1,200 design sessions before warm-up/calendar exclusions; |z|>=1 and reversal may
leave ~150-250 trades. At n=200 and SD=$1,000/NQ, t=2 needs $141 net/trade and t=6 needs $424.
Thus t6 is demanding. The five configurations and related historical family searches count toward selection.
Do not loosen the gate or add variants after a failure.

## 7. Prior work and falsifiers

Existing RS trades a 09:00 intraday residual in its own direction. Existing ONB trades a range breakout.
Neither supplies this signal. Trapped-inventory, ordinary overnight reversal, and opening-gap studies already
failed. New information here is the benchmark-adjusted overnight displacement plus a confirmed opening reversal.
Reject if design net/t/PF fail, removed momentum trades remain profitable, random removal is as good,
the overnight gate contributes no total-profit/risk improvement, or valid chronology cannot be established.
Do not reverse direction, change clocks, or substitute old trade ledgers to rescue the target.

## 8. Failure, risk and next gate

This takes liquidity and can lose when tech-specific news persists or a strong trend resumes. It may share
opening-drive losses with existing NQ legs; a late recovery cannot rescue an earlier account breach.
One position, one trade/day, stop 0.15 prior ATR, target 0.30 prior ATR, flat 11:00 CT. No holiday/early-close
entries; no overnight holdings. Missing anchors or opening-bar input skip before entry; missing held prices
are inventoried without profitable deletions or favorable interpolation. Gap stops may exceed the nominal stop.
Calendar roll exclusions are predeclared in the plan because unadjusted overnight contract switches can create false residuals.

TEST authorizes a fixed preregistration and design screen only. Only cheap-pass variants advance to previously
seen 2023+ validation, matched-exit placebos, uncertainty and valid account/portfolio controls. No live change.
