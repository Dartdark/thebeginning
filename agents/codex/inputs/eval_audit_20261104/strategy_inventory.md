# Evaluation strategy universe: source and data inventory

Summary: Screened the latest 368 ranked registry entries and mapped 36 strategy families without new returns.
Current evaluations still use VB/ONB30/EOS/Bridge; 18 established/conditional alternatives have a research route.
Sixteen saved native-unit ledgers exist; their old NPZ/pickle runtime paths are absent in this workspace.
Existing non-equity alternatives are limited; CL held-minute gaps and common equity exposure remain material.
Latest Claude adds NBL to personal, but its missing early-close exit prevents Apex use as written.

## Scope and source boundary

Pinned latest Claude: `13e29ca7b45daabeb0ed2d8c286448610f594dab` (read-only git show).
The full [ranked registry snapshot](tier_registry_snapshot_13e29ca.json) retains every row, including failed
families, papers, tools, sizing rules and repeated economic definitions. Its 368 rows are not 368 distinct strategies.
The [machine inventory](strategy_inventory.json) gives candidate status, exact ledger/source paths, schemas,
hashes, date metadata, entry-stop formula, units and documentary MC/checker status. This is not independent
historical replication, a new ranking, new hypothesis or allocation. No return, signal, sizing sweep or account
combination was run by this inventory script. Hash/schema/date reads do not certify native fills or data coverage.

## Current rosters and recent source changes

|Home|Existing eval inputs|
|---|---|
|50K|VB8MNQ; plain ONB ADX30 risk$1,100 at0.25ATR; EOS risk$500 at0.30ATR; Bridge2MNQ|
|150K|VB20MNQ; plain ONB ADX30 risk$2,750 at0.25ATR; EOS risk$1,250 at0.30ATR; Bridge5MNQ|

Verified workbook Settings: VB StopPts75/TargetPts40/AtrDays15; plain ONB ADXMin30/StopAtrPct0.25/
AtrDays15/RewardRisk3; EOS StopAtrPct0.30/AtrDays15; ONBML ADXMin20/StopAtrPct0.30/AtrDays15/RewardRisk3.
`build_lab.REPORTS['VB'][1]=0.30ATR` is sizing metadata, **not the actual fixed75point Vault Break stop**.
At entry, fixed stop risk perMNQ is points×$2; dollar-risk quantity must floor using its own account's dollar
budget before combining paths. Actual source default ONB0.30 does not override the evaluation's explicit0.25input.

Latest Claude NEW_CHAT_BRIEF confirms #2/#4 failedNovember4 and the eval roster is unchanged. Funded changes
are different:50KusesVB2/1plusTfade;150KkeepsDT2. Swing Target funded swaps were revertedOctober31after
corrected replay found the prior gain inconclusive. Do not use stale TIER/adoption prose as today's roster.
Latest personal pieces table adds RTH-anchored noise-area longs November3 (20labels), but its whole-book prose
still says19. This discrepancy is source-version bookkeeping, not permission to copy an outdated performance table.

## Core/conditional research universe

“Conditional” means a source/data route exists for a separately preregistered comparison. It does not mean the
strategy is already approved for the eval plan or that a new test will pass. All are subject to native paths/costs,
source clocks, original selection, integer quantities and chronological account replay.

|Key|Strategy|Reported tier / role|Entry-stop specification|Canonical raw ledger/source|
|---|---|---|---|---|
|VB|Vault Break|A;baseline|75points|`analysis/outputs/codex_portfolio_audit_20261031/VB_unit_ledger.csv`|
|ONB30|Plain Overnight Bias ADX30|A;baseline|0.25×prior15 prior_ATR_multiple|`analysis/outputs/codex_portfolio_audit_20261031/ONB30_unit_ledger.csv`|
|EOS|Expiration Open Short|A;baseline|0.3×prior15 prior_ATR_multiple|`analysis/outputs/codex_portfolio_audit_20261031/EOS_unit_ledger.csv`|
|BRIDGE|Bridge Monday Long|A;baseline|No protective stop|`analysis/outputs/codex_portfolio_audit_20261031/BRIDGE_unit_ledger.csv`|
|ONBML|Overnight Bias ML v2|S;conditional_existing_alternative|0.3×prior15 prior_ATR_multiple|`analysis/outputs/codex_portfolio_audit_20261031/ONBML_unit_ledger.csv`|
|LDF|Late-Day Flow|A;conditional_existing_alternative|0.25×prior15 prior_ATR_multiple|`analysis/outputs/codex_portfolio_audit_20261031/LDF_unit_ledger.csv`|
|MON|Monday Long|A;conditional_existing_alternative|0.5×prior15 prior_ATR_multiple|`analysis/outputs/codex_portfolio_audit_20261031/MON_unit_ledger.csv`|
|NFP|NFP Fade|B;conditional_existing_alternative|0.5×prior15 prior_ATR_multiple|`analysis/outputs/codex_portfolio_audit_20261031/NFP_unit_ledger.csv`|
|CLS|CL Sunday up-gap fade|A;conditional_existing_alternative|0.75×prior15 prior_ATR_multiple|`analysis/outputs/codex_portfolio_audit_20261031/CLS_unit_ledger.csv`|
|MOC|ES MOC Follow|B;conditional_existing_alternative|0.25×prior15 prior_ATR_multiple|`analysis/outputs/codex_portfolio_audit_20261031/MOC_unit_ledger.csv`|
|RS|Relative Strength NQ/ES|B;conditional_existing_alternative|0.6×prior20 prior_mean_RTH_range_multiple|`analysis/outputs/codex_portfolio_audit_20261031/RS_unit_ledger.csv`|
|DT|Dual Thrust v4|A;conditional_existing_alternative|50points|`analysis/outputs/codex_portfolio_audit_20261031/DT_unit_ledger.csv`|
|TOS|T_ONESIDE stopped fade T|B;conditional_existing_alternative|0.4×prior20 prior_mean_RTH_range_multiple|`analysis/outputs/codex_portfolio_audit_20261031/TOS_unit_ledger.csv`|
|OT|Overnight Tick/VIX|A;conditional_existing_alternative|No protective stop|`analysis/outputs/codex_portfolio_audit_20261031/OT_unit_ledger.csv`|
|FC2B|Flow-Confirmed Opening Drive v2|A;conditional_research_alternative|100points|`checks/candidates/fc_2b/mc_v2_trades_all.csv`|
|ST|Swing Target v3|B;conditional_research_alternative|0.7×prior20 prior_mean_RTH_range_multiple|`checks/candidates/swing_target/mc_trades_v3.csv`|
|PT|PAPERTREND v2|B;conditional_research_alternative|2.0×prior14 prior_mean_RTH_range_multiple|`checks/candidates/papertrend/mc_trades_claude.csv`|
|VCS|Vol-Control Sell Flow|B;conditional_research_alternative|0.25×prior15 prior_ATR_multiple|`mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Vol-Control Sell Flow.xlsx`|


For ONB/EOS/MON/LDF/NFP/VCS, reproduce the source's completed-day true-range/weekday calculation before sizing;
do not replace it with an unrelated RTH average. RS,Tfade,ST andPT use the specified mean RTHhigh-low ranges,
not WilderATR. Native point values:MNQ$2,MES$5,MCL$100; tick values differ. Bridge andOT have no source stop;
an invented stop-distance cap would change their strategy, not merely their lot count.

## Screened exclusions and research-only routes

|Key|Route|Reason retained|
|---|---|---|
|FVB|research_only_not_promotion|Fat-tail positive Bledger, prior all eval/funded comparisons worse; shorts-only improvement post-hoc. Freeze original whole rule if inspected; no rescued short selection.|
|S47|research_only_not_promotion|MCparity exists but~3700searches and agreement condition added after2023+. Entry/exit fixes/version mapping needed; personal forward only, prior evaltie/worse.|
|NBL|blocked_current_early_close_code|Newlatest11/03personal addition. MC98.9%entries and longs t5.4sourceclaims; raw code misses earlyclose flat (9port/4checker carries). No Apex admission until separately frozen repair; 1minute entry delay reduces edge. Prior50Kadd small,150Kno gain.|
|TWIN|blocked_current_Apex_path_and_risk|Personalonly: wide/multiday swing stop; v1ledger differs fromv2.1holiday/SetExitOnClose fixes. Prior capped Apex variants/36replacements mostlytie/worse. No new 15:45/stop-cap rescue.|
|KUSHO|blocked_original_multiday_held_exposure|Original21:00/weekend holds personal-only. Existing15:45RTHvariant ledger available separately but already weaker Apex bench; no silent shortening.|
|S30|blocked_multiday_no_stop|Personal-only multi-day/no-stop. Daily series not an evaluation native path. New daily-flat conversion would be a new strategy.|
|S03|research_only_not_promotion|Existing family tested extensively, account gains weak/negative; cannot treat BridgeNBLor recent uploaded15mcode as independent new evidence.|
|PVT|research_only_not_promotion|Prior Apex benches worse, placebo levels similarly strong; personal capital-expansion bench only.|
|BBMRM|closed_unless_forward_checkpoint|Removed byuser after MCweaker than Python; post-hoc49winning extra trades overstated original. Do not restore from old Bsectionheading.|
|REBOUND|closed_no_allocation|One thousand fixed-source trades positive but filter/timing benefit unproven and personal profit/DDworse; not new current risk diversifier.|
|NOCTURNE|closed_weak_recent_stop_kills|Recent2024–26t0.75, no stop; stop erases edge; frozen forward checkpoint not a new evalsearchcandidate.|
|PRIMESYNC|closed_failed_account_gates|Already tested one micro/frozen entry on all homes; no allocation gate passed. Code not compiled/trade matched.|
|R1144|closed_failed_design|Latest directupload two causal profiles fail adjusted significance and source/data gates. Not an eligible rescue through portfolio search.|
|GC_ASIA|closed_prior_eval_no_gain|Userparked10/14; filtered rarity/weak standalone; no prior evaluation improvement. Native MGCcosts/quote risk need distinct admission.|
|GC_COMBO|blocked_signed_tick_field_and_source_match|UpTicks/DownTicks sign missing from existing GCexports; price proxy fails. LucidFlexclaims are not Apex results.|
|ZN_AUCTION|closed_cost_failure|Prior intraday drift below roundtrip costs and postauctionrebound absent; COT/auctiondate new filters cannot silently revive.|
|NG_STORAGE|closed_source_gate_failure|Fullsource post2011netnegative; corrected NGdata retained for distinct ideas, not a late portfolio rescue.|
|6E_FIX|closed_design_reject|Existing scout failed gross/cost gate; source/data-blocked unrelated FXhypotheses do not make this eligible.|


No daily-only S30, multi-day Twin/Kusho, missing-input GCCombo, failed R1144/PrimeSync/NGcalendar/6Efix, or
previously rejected generic families were promoted into the test pool. An explicit new bounded user-directed
comparison may include an existing eligible research alternative, but is not authority to erase prior failures,
choose a post-hoc short-only variant, silently shorten holds or count another ticker as independent evidence.

## Data availability and usable loaders

`analysis/outputs/codex_portfolio_audit_20261031/*_unit_ledger.csv` contains16 existing native-unit ledgers:
VB,VB_N,VB_F,ONB30,ONBML,EOS,BRIDGE,LDF,MON,NFP,RS,DT,TOS,OT,CLS,MOC. Schema:
`entry_at,exit_at,side,qty,entry,exit,kind,gross,fee_units,slippage_one_tick,missing_held_bars,exit_after_1559`.
`gross` is already native-micro dollars (NQ$2/point), not full-NQ dollars. Use raw prices/native values to
rebuild a consistent cost bridge. `j0/j1` are17→16account-session coordinates; datetime columns are safer
for reconstruction. Numeric stop0/target1/time2 mappings matter. Wrong string exit kinds previously changed
slippage and adverse paths; see [Swing Target correction](../../results/swing_kind_replay_20261031.md).

The pinned old normalized universe isApril2,2018–July7,2026. First/last actual trade timestamps in a CSV
are not proof of full no-signal coverage. Later absent OTrows represent an order-flow input cutoff, not zero
returns. The original MCreports/extended raw ledgers can extend some strategies independently only after
matching source version/calendar/clock/cost. No missing day may be converted into a known no-trade day.

Direct MCcandidate CSVs with raw prices and `date,t_in,t_out,exit_date,kind` exist for FC2Bv2,DT,STv3,PT,
Tfade,S47andBBMRM. Their HHMM fields are chart stamps, not certified native fill minutes. Some source
trade CSVs omit times entirely; use the corresponding MCworksheet/source adapter rather than fabricate them.
Latest NBLledgers/fills/source exist at Claude13e29ca, not necessarily the codex/work tree. All detected paths,
row counts, columns and first/last date fields are in the machine inventory.

The prior audit runtime `agents/codex/runtime/portfolio_audit_20261031/` is absent here; `/workspace/scratch`
is effectively empty and `scratch_data` only has a greenorb subfolder. Do not claim NPZ/pickle paths were loaded
without rebuilding them. `analysis/codex_portfolio_audit_prepare.py` documents the prior normalized loaders but
requires its pinned old source worktree and includes historical source approximations; it must not be blindly
executed/imported as a current selector. Importing some old test scripts also executes returns at module level.

Important prior audit limits: CL85/87andOT69/516trades have missing held-minute OHLC; Bridge has one touch
mismatch; VBsingle-print flags are missing on eight recorded days; ONBMLhas an explicit unfinished sentinel.
The relevant [portfolio audit](../../results/portfolio_audit_20261031.md) retains them. Source-minute extrema summed
across strategies are conservative account-risk proxies, not synchronized tick paths; a common bias can change
relative floor outcomes, so it does not automatically cancel between portfolios.

Current saved native audit used1.04microRTcommission as primary (user-reported MNQrange0.99–1.08),1.24fee
sensitivity and one native tick permarket/stop fill. MES/MCL1.04was assumed, not observed. Old benches often
used NQ$7.25/10=$0.725perMNQ and fractional “scale0.75” quantities. Reconcile actual chosen cost and whole
contracts before calling a size/mix optimal. This inventory creates no new comparison outcome.

## Reproduce this inventory only

`/workspace/venvs/thebeginning/bin/python analysis/codex_eval_strategy_inventory_20261104.py`

Reads the pinned Git objects and existing files, hashes/schema/date metadata, and writes this note plus JSON.
No local/VPS trading file, plan, broker setting, API key, paused program, return ledger or allocation is changed.
