# Frozen FOMC-cycle246 ES reference screen

Summary:2018–22 only, one calendar signal; reserve1candidate+2controls including gross/cost views.
Evidence:`agents/codex/evidence/scout_fomc_cycle.md`; sourceSSRN2687614,2018-02-12manuscript.

## Rule

After each completed regular dated FOMC statement in the frozen calendar, count Monday–Friday slots since anchor0.
On ages9..13,19..23,29..33, long1standardES reference OPEN08:31-label→CLOSE15:00CT on full390-minute NYSE sessions.
No previous-anchor extrapolation before2018-01-31; no unscheduled reset; no future FOMC, return or news input.
No stop,target,price-decline filter, fitted parameter or overlap exclusion. This is a full-day-to-RTH adaptation,
not exact cash-equity replication. Require484candidate endpoint pairs and>=99%control-pool coverage,>=400events;
any candidate missing endpoint stops returns. Unknown non-event2020-11-30 stays visible and is excluded from pool.
No imputed return. Native contract/roll/path audit is required before further positive executable testing.

## Costs, controls and stopping

DefinitionFOMC246_ES_RTH:50USD/point,5commissionRT+25slippage(one0.25tick/side)=$30.
DefinitionFOMC246_CALENDAR_NULL:1,000draws without replacement within each year/month/weekday, same number
as candidate; same long RTH references/exits/costs, seed2687614. Use all complete full sessions after first anchor;
report the prespecified one-sided total-net p=(1+null>=candidate)/1001. No baseline selected on outcomes.
DefinitionFOMC246_COST_STRESS:same candidate references, two ticks/side, total55RT. No new clock/side.
Gross/net/yearly views are reporting for the same economic definition; original repo and current scout multiplicity
remain. Gate requires candidate netmean>0, trade t>=2, null p<=.05 and stress netmean>0. Failure closes family.
No2023+, stop search, accounts or MC after a failed cheap gate; continue other source families.

## Passing path

A gross pass is not executable design or an independent verification. Before more outcomes commit exact stopped
execution code/evidence/reservation, matched side/time placebos, dependence-aware uncertainty and the material
native contract/path/MES-cost audits. Only an executable design pass earns unchanged once-only2023+historical
validation, independent raw-spec review and current actual-size50K/150Keval/funded/personal comparisons.
Refresh current roster then; expected overlap slot is Vault Break, not selected using new outcomes.

## Reproduce

`analysis/codex_scout_fomc_cycle.py --inventory` reads timestamps only.
Before returns publish/fetch checked-head lease+reservation and run scout_gates on the envelope. Return command
`--envelope PATH --confirmed-claim SHA` repeats admission and verifies every frozen input hash before prices.
Saved source,calendar,code/input hashes,reference ledger,null draws,coverage and manifest support later review.
