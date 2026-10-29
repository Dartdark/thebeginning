# Clock-aligned Treasury month-end demand: REJECT

Summary: The new externally anchored benchmark clock does not make the ZN month-end adaptation tradable.
175longs in2018–22average+$15.89gross but−$29.86net per ZN; net t−3.45, PF0.45,0/5positiveyears.
Matched-calendar p0.001 supports a relative tilt; native$45.75RT costs exceed its gross dollars.
No2023+or account tests; retain the pricing-clock lesson and continue different source-supported families.

Plan:`agents/codex/plans/scout_treasury_close_20261029.md`, commit`352bbf8d075efca6375f50a5d37b9280198a7500`.
Code:`analysis/codex_scout_treasury_close_20261029.py`. Outputs:`analysis/outputs/codex_scout_treasury_close_20261029/`.
Trials:1candidate+2controls, all3executed. Earlier ZN month-end trials and all other multiplicity retained.

## Rule as tested

Long1ZN during the hour before the Treasury benchmark strike on each month's last3cash-bond business
dates.13:01-labelled open→14:00close before2021-01-14;14:01→15:00thereafter, following the independently
documented Bloomberg strike change. Protective lagged15-day ATR stop rounded outward to1/64point;
no target, no reentry, flat each date. Data gate175/180events; frozen exclusions are in coverage.csv.
This is an intraday adaptation of a multi-day source paper, not its exact replication. The old family's
failed intraday tests stopped at13:59even after the benchmark moved; they remain negative evidence.

## Results: whole strategy equals longs

|2018–22,1ZN|Gross|Net|
|---|---:|---:|
|Trades|175|175|
|Win rate|55.4%|37.1%|
|Average/trade|+$15.89|−$29.86|
|Total|+$2,781.25|−$5,225.00|
|Event t|1.84|−3.45|
|Daily Sharpe|0.82|−1.51|
|Sortino|1.31|−1.88|
|Profit factor|1.54|0.45|
|Close-to-close max drawdown|$1,125.00|$5,622.50|
|Calmar|0.50|−0.19|
|Ulcer index|0.62|5.38|

Costs:$7.25fee/fill+1tick($15.625)/fill=$45.75roundtrip. At2ticks/fill=$77,
netmean−$61.11. No fungible microZN or improved fills assumed. Ulcer referencecapital$50,000;
daily drawdown is not an Apex account simulation. Shorts not registered/run;2023+not opened.

|Year|Trades|Net1ZN|
|---|---:|---:|
|2018|36|−$412.63|
|2019|35|−$882.50|
|2020|33|−$1,462.88|
|2021|35|−$507.50|
|2022|36|−$1,959.50|

Exact CSV totals reconcile without rounding; the two .625year totals round to .63/.88when formatted here.

## Placebos and account level

1,000same-year/month/weekday non-event samples, identical costs/stops/clocks, average−$50.30net
versus−$29.86on events. One-sided p0.000999 demonstrates relative calendar differentiation in this screen,
not positive net returns. The2,000year-cluster bootstrap90%mean interval is−$42.94to−$17.50.
Only the matched-calendar gate passes; net,t,yearstability,bootstrap and executionstress fail.
No evaluation/funded/personal BASE/ADD/REPLACE/EMPTY runs are earned. No sizing or execution rescue.

## What could make this wrong

The calendar is a declared US federal-holiday+GoodFriday convention plus2018mourning closure, not historical
index-constituent membership. Early-close missing endpoints remain excluded, with no price imputation.
Before preregistration, a timestamps-only provisional99%convention was changed to an explicit one-missing-minute
98%convention; both inventories are preserved. No outcomes informed that choice. After registration no settings
changed. Continuous contracts, unobserved quote spreads and one-minute stop paths limit exact execution parity.
Fees are conservative native contract assumptions, not a broker statement. Lowering costs post-result would be
a new economic look; it is not permission to revive this failed candidate. No claim that every multi-day
Treasury month-end strategy is false follows from this one-hour adaptation.

## Four source questions

What is it about? Hartley/Schwarz study month-end Treasury returns and insurer purchases.
What does it find? Their1990–2018Table8 reports0.17%over the last3days for10-year futures,SE0.02%.
Why might it pay? Insurer/index demand can temporarily bid up duration; this does not guarantee net
buying at every futures timestamp. NYFed2026research independently establishes a2021pricing-clock shift,
not a return premium. Can we build on it? This registered intraday adaptation fails; preserve the clock
lesson, leave the old negative family evidence intact, and continue other mechanisms.

Sources:[Hartley/Schwarz primary PDF](https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2019/12/17-19.Schwarz.pdf);
[NYFed pricing-clock evidence](https://libertystreeteconomics.newyorkfed.org/2026/09/treasury-trading-at-the-close/).

## MultiCharts and verification

No MC code because the design fails. Independent economic verification pending; accounting checks are not
independent checking. No plan, live trading, VPS, broker settings or allocations changed.
