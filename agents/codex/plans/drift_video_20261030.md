# Video Drift VWAP Pullback — frozen2026-10-30

Summary: Reconstruct the uploaded video's NQ strategy and test its earned portfolio contribution.
An existing DriftPullback family is already ranked; no novelty or fresh holdout is claimed.
Freeze two loss-counter interpretations, controls and costs before any new return.
Failed design stops2023+ and all account stages; no rescue optimization.

Evidence: [TEST sheet](../evidence/drift_video_20261030.md).
Source: [transcript](../inputs/drift_video_20261030/transcript.txt), rules14:24–18:37/21:32–23:20.
Exact implementation: analysis/codex_drift_video_20261030.py, committed with this plan.

## Frozen rule and assumptions

NQ price proxy,1MNQ economic units.15m and5m bars aligned to CT quarter-hours, built from close-stamped minutes.
VWAP resets at08:30CT; completed15m bars08:45onward contribute HLC3×total exported volume. At every15m close,
long bias iff close>VWAP, VWAP>previous15mVWAP and close/close4barsago−1≥0.001; short is mirrored≤−0.001.
Hold that bias until next completed15m close. This does not use a developing15m candle.

Trigger: current5m candle opposes held bias and previous5m candle was not the same opposing color. This is our
explicit definition of “first pullback”, not supplied source code; no VWAP touch/distance threshold. Bias and trigger
may become known together at09:30CT. First permitted decision09:30, last14:30inclusive, fills next5m open.
The first minute after decision dj is close-stamped dj+1; its open is the decision's civil-clock boundary, not a
five-minute delayed fill. Flatten at14:55CTclose. Known half-days: stop new decisions by11:30CT, flatten11:55CT.
No cash-holiday trades. Existing calendar has conservative July3handling; disclose, do not optimize it.

Stop80points both sides, target40long/50short. Protection active at entry, one position, max4entries/day.
Primary stops for the day after two **consecutive net losing trades**, since22:55explicitly says consecutive.
Alternate uses two **total net losing trades**. No selection between them: primary remains primary.
Shared grid.execute one-minute bracket path, stops gap to open, targets require1fullpointthrough, standard path tie-break.
No entry replacement or partial fill assumptions; exact native/code parity unavailable.

## Cost clock

Nominal NQ prices/exit brackets; native1MNQ net=gross/10−$1.04RT−$0.50permarket/stopfill.
NQ presentation bridge: gross−$7.25RT−$5permarket/stopfill. No scaling an NQ fee into a native micro fee.
Stress: $1.24RT−$1permarket/stopfill; replay the consecutive-loss cap using stressed net. Nominal bracket prices remain fixed; this is no native quote/fill replay.
Charges apply once per trade; both entry and non-limit exit pay slippage. Gross/fee/slippage/net and daily totals reconcile.

## Five economic definitions, no search

1. Primary consecutive-loss strategy.
2. Two-total-losses robustness version (not a selectable rescue).
3. Random-side placebo:100draws, prospective source signal times, random side with that side's40/50target,
   same stop/one-position/daily caps and flatten. Caps/position occupancy re-executed.
4. Random-time placebo:100draws, same dates/count and side-order of prospective signals but uniform distinct
   allowed5m slots, same execution/caps. It intentionally removes bias/counterbar alignment; not an incremental-filter claim.
5. Execution-cost stress with cost-dependent daily-cap replay. NQ/native fee bridge is unit accounting, not another selected rule.

Seed301034forcontrols; bootstrap301035. Existing family history retains≥15priorvariants and old placebos.
This direct upload is not a new scout hypothesis; no scout progress/history/schedule is changed.

## Chronology and exact design gate

Timestamp-only inventory hashes2018–22files. Require≥95%cash-session coverage, and complete08:30→flatten paths for
eligible dates.1,247/1,259sessions pass;12 remain unknown. No other years in the design input directory.
Primary alone must have≥500trades, positive1MNQnet, **daily t≥2.5**,≥4/5positive years, positive stressednet,
and empirical p≤0.05against **each** random-side/time total-profit null: (1+nulls≥actual)/101.
Report daily and trade t, all/long/short standard metrics, byyear, total-loss alternative, costs,100drawcontrols
and10dayblock bootstrap5,000draws. These gates are source-replication screens, not ranking/approval.
Known priorfamily/future results mean nothing here is a clean fresh statistical holdout.

If any gate fails: save complete negative result; do not open2023+or execute new account benches.
If all pass: unchanged primary and prespecified alternate on2023–2026-10-09once, with same controls and bootstrap.
Advance if primary recent net/stresspositive, daily t≥2and eachplacebo p≤.05; otherwise stop without retrospective changes.
No long-only/short-only selection; side tables are diagnostics only.

## Conditional account plan — all five homes

Authority: six-plan snapshot atClaude7a42ea76c62838109d45d168887f57a922933ef2.
Funded50K includes T_ONESIDEfade1replacingRS_L, ST1/OT1, VBnormal1/flag1, ONBMLrisk400, EOS700, LDF2,NFP500,
Bridge1,CL2,MOC2.150Kuses current150Kallocation(ST2/OT2/RSboth1; noDT).
Eval50K: VB8,ONBADX30risk1100,Bridge2,EOS500.150K: VB20,ONB2750,Bridge5,EOS1250.
Personal19pieces and A–D/core/full ladder; preserve source booking/overnight caveats.

If design+recent gates pass, first audit unchanged implementation/ledger. Independent economic review remains required
for promotion; provisional research benches may accompany the maker package, never an automatic admission.
Use existing funded_bootstrap/current-payout/OBv2lookup interfaces, current pinned source ledgers; no old roster substitution.
Common matched complete dates and coverage needed for all variants; OTends2026-07-07, so primary account window ends there.
Unknown candidate/current-book paths must not be silently zero-imputed; report exclusions and account-model limits.

At each funded/eval size: BASE; ADD1MNQprimary; EMPTYVB; REPLACEVBwith1MNQprimary. RemoveVB_N+VB_Ffunded,
VB8/20eval. No size search. All current lines and challenger use matched native fees; preserve frozen baselineothercosts.
Funded1,000paired20dayblockhistories,250/500sessions,existingcushionruleandintegerfloor; payouts,blown,first/6thpayouttiming,
paired90%CI. Evaleveryavailable21sessionstart,pass/blown/time,2018–22/2023+. Account gains need positiveuncertaintybound
and no>1percentagepointraise inblow-up; cap effects and possibletrade-offs visible, not automaticapproval.
Personal A/B ADDonly(noVBslot);C/D/core/full BASE/ADD/EMPTYVB/REPLACEVB,1MNQ,annualprofit,DD95,return/DD/capital20%rule,
pairedbootstrap. Need betterreturnperdrawdown or clearlypositiveequal-riskgain; rawprofitwithhighercapitalisnotanupgrade.
No strategy, ranking, plan, live, VPS, broker or key changes. If a prereq fails, report every home's unearned status plainly.

## Publication and verification

Report starts Summary≤5lines; key table also in chat. Archive transcript, inventory,codehashes,plancommit,ledgers,
dailycostbridge,controlresults,trialledger,excludedpaths and relevant frozenportfolio snapshot.
No new MCcode before a pass. No external message toClaude; give user resultpath for review.
