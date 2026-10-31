# Frozen current-portfolio audit protocol

Authorization: user 'ok do the porfolio audit'. Evidence: ../evidence/portfolio_audit_20261031.md.
Source Claude c3126aa01796133f3aecb368e688726931dea440; local research baseline a1b192c.
Commit this protocol, then exact economic-run code before new results. No alpha search/fit/optimization.

## Five current homes

-50K evaluation: VB8, plain ONB ADX30 risk1100/stop.25ATR, EOS risk500/stop.30ATR, Bridge Monday2.
-150K evaluation: VB20, ONB risk2750/stop.25ATR, EOS risk1250/stop.30ATR, Bridge5.
-50K funded: VB2/1 normal/flagged; ONB ML risk400/stop.30ATR; Overnight Tick1; EOS risk700/.30ATR;
 LDF2; NFP risk500/.50ATR; Bridge1; CL Sunday2MCL; ES MOC2MES; T_ONESIDE fade1. No ST, RS or Monday Long.
-150K funded: historical funded base x1.5 with VB normal3/flagged1.5, ONB risk600, Monday1.5, EOS risk1050,
 LDF3, NFP risk750, Bridge1.5, CL3MCL, MOC3MES; RS both1; DT2; Overnight Tick2. No ST/T_ONESIDE.
 Source fractional fixed intentions are explicitly disclosed and floored to whole lots with cushion scaling.
-Personal: documented19 pieces at one micro each (S30 is its existing combined NQ+ES sleeve), with the existing
 small-account core/ladder documented separately. Preserve current source identity; flag v1/v2.1 and roll gaps.

## Data, clocks, sizing and costs

Primary historical accounting window2018 onward through the common usable source cutoff, never later than
2026-07-07 while Overnight Tick is present. Resolve earliest common warm-up/settings coverage before returns,
record actual chosen interval from metadata only. Report2018–22,2023+ and calendar years as already-seen history.
Refresh last-source dates and unresolved held bars; later-only components do not fill another component's gap.

Native point/tick values MNQ2/.25, MES5/.25, MCL100/.01. Every order/trade/reentry and partial quantity counts.
Prespecified fee scenarios: low1.04RT, main1.24RT, stress2.48RT for each micro; one adverse tick per market/stop
fill in low/main, two in stress; no slippage on target-limit exits, keeping the recorded trade-through assumption.
These are assumptions until an exact user tariff is supplied. A tariff supplied before runs replaces main and is
logged; it is not fitted. Legacy scaled fees retained only as an accounting comparison, not a competing allocation.
Charge costs without double counting embedded ledger slippage. State fee timing conventions and unknown quotes.

Whole lots: evaluations floor risk budget/(native point value x prior stop distance) at their own account size,
never floor50K first then multiply2.5. Funded daily f=clip(cushion/ref,.5,1), ref1500/3000, then floor per strategy.
Risk budgets inherit source stop/ATR convention, without new tuning. No fractional micro fills.

Separate gross/commission/slippage/net; reconcile trade and daily totals. Map evening entry and early morning
holds into the correct Apex trading day. Archive exact rules/settings and distinguish historical-ledger proxies
from the deployed/current source version. Do not silently repair an unresolved source rule or missing price.
Document calendar exclusions already explicit in current code, without selecting them from profits.

## Audit outputs and account stage

1. Structural roster/settings/version/coverage matrix, cost and sizing fixtures, report/price reconciliation.
2. Fixed current allocations: daily net, standard metrics/by year/side where ledgers permit; cost drag, market
 concentration, losing-day concurrence, component contributions on the baseline's worst5% days; no drop-selection.
 Position occupancy, signed/gross native exposure and coincident losses where actual clocks permit. Record unknowns.
3. Account baselines only:50K/150K evaluation pass/fail/time and timing on21-session windows; funded payouts,
 failures and completion timing over250/500 sessions via repository account tools and paired20-day blocks,
 seed20261031,500 histories per size/cost scenario. Preserve synchronized market days. Report conditional on
 input/path quality. Personal historical/bootstrapped252-day risk using repository metrics/MonteCarlo,5000 draws,
20-day blocks, no claim of margin feasibility or literal v2.1 certification without matching ledgers.
4. Inspect simulator floor equality, DLL-before-floor chronology, EOD trailing/lock, payout thresholds/consistency,
 size caps and fee debit. Native fee fixes do not imply monotone account payouts. Account-rule facts are source
 assumptions, not newly verified Apex terms. No actual live balance pass odds without complete as-of state/data.

If minute-path or source-version inputs fail admission, stop the unsupported certification/account claim, not
all unaffected diagnostic work. Clearly label any inherited-path bench as conditional, census omitted/unknown
observations and supply exact remaining inputs. Do not portray missing data as zero or a daily DD as Apex safety.
No unbounded rebuild, purchased data, new strategies, rescue tuning, leave-one-out allocation search, live changes,
or retirement/adoption. Zero new alpha definitions; five existing homes x three declared cost stresses, with the
same frozen allocations throughout. Publish all attempted/failed checks and conditional outputs. Independent
verification pending; no account improvement claim without a separately frozen comparison passing existing gates.

## Fee clarification before code freeze / before any new return

User supplied: MNQ measured0.99–1.08RT, use1.04; MES/MCL never traded live,1.04 assumed. Main is therefore1.04RT
for each micro,1tick per market/stop fill. Preserve1.24RT/1tick as the second declared fee sensitivity (`fee_124`),
and use doubled main fees2.08RT/2ticks for `stress`. This replaces the provisional low/main/stress schedules above
before all economic outcomes. It is a user-provided cost clarification, not an outcome-selected fee reduction.
Source MNQ evidence is the user's measured range; MES/MCL remain assumptions, not verified fee schedules.

## Preparation admission correction, before baseline/account outcomes

The first preparation attempt stopped at the no-missing-flag assertion: the existing single-print cache omits
some holidays/partial sessions. Do not inherit the old fillna(False) allocation. On a recorded VB trade day with
an unknown flag, mark both funded VB size branches unknown and exclude that day from that funded baseline's
conditional accounting pool. A missing flag on a day with no recorded VB trade cannot change an executed size.
Keep the raw VB evaluation ledger intact and retain every flag omission in coverage_issues.csv. No economic
allocation result was produced or used to choose this treatment; the stopped attempt is retained in the run log.
