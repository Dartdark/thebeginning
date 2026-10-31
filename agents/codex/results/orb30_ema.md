# ORB30 EMA: WATCH — profitable proxy; no current allocation recommendation

Summary: Full-session EMA wins design;1.85R PF1.31 design/1.21 validation,994 tickets overall.
4R/no target improve historical totals but paired exit evidence is weak; no validation-selected winner.
True1% fractional1.85R drawdown is13.3% floating; full-history closed-DD95 is17.5% block/20.9% permutation.
One-MNQ personal additions lower profit/DD95; ONB replacement uncertain. Four Apex contexts LIMITED.
18 unclassified held minutes in1.85R, absent original EA/ticks and uncompiled MC code prevent parity/promotion. No live change.

Plan: `agents/codex/plans/orb30_ema.md`,9fc1b3f; design selection savedc802c4c before validation. Personal amendmentb0b661d.
Scripts: `analysis/codex_orb30_ema.py`, `codex_orb30_personal.py`, `codex_orb30_report.py`, `codex_orb30_code.py`.
Code: `agents/codex/code/ORB30_EMA_Research.txt`. Outputs: `analysis/outputs/codex_orb30_ema/`.
Five economic models including unfiltered comparator; rejected CASH185 not validated; alternative CASH exits not run. Author search count unknown.
Previously seen2023+ is historical validation, not a new holdout. No claimed independent walk-forward replication.

## Review of the supplied claims

Neither post establishes a durable edge by itself. For fixed-fractional returns, B[t]=B[t-1]*(1+.01*R[t]); uniform initial-capital scaling preserves percentage drawdown. A consistently normalized contiguous subperiod cannot have a larger relative maxDD than its encompassing path. Thus16.07% OOS versus10.16% full-history needs different sizing, trades, costs, cash flows or definitions; ordinary compounding is not that explanation. Integer contracts/fees can break ideal scaling and must be reported separately.
The second reply correctly challenges the compounding story but overdiagnoses its cause: the original explicitly uses balance-at-entry in its R formula, which is the correct denominator. Doubling R alone does not prove a100k-denominator error. Obtain original ledgers/settings before identifying the error. PF can change under balance-weighted re-compounding/reordering, so it is not universally invariant.
MT5 distinguishes absolute drawdown (initial deposit versus minimum), maximal dollar drawdown and relative peak-to-trough percentage, separately for balance/equity. Its absolute figure is not inherently a percentage. [Official definitions](https://www.metatrader5.com/en/terminal/help/algotrading/testing_report).
Trade reshuffling conditions on already selected trades; it measures sequence risk, not trigger value. A10% drawdown exceedance is not ruin. Closed-trade curves hide floating drawdown even for same-day positions; the post’s mention of multi-day-held positions contradicts its claimed daily flatten and needs reconciliation.
The quoted independent futures/MC results and all-seven-positive walk-forward claim were not accompanied by code/data/ledgers. These results cannot certify them; our sample starts2018, our authorized flatten is15:55CT, and our bars are minute OHLC, not broker ticks.

## Fixed rule and execution

One-minute CT close labels511..540 form08:30–09:00 wall-time OR. At09:00, completed M30 close strictly exceeds EMA20 including that bar. FULL uses complete30-minute Globex bars; CASH uses complete cash bars09:00..15:00 close labels, preserving state across days. Missing minutes suppress a30-minute EMA observation rather than fabricating data. This strict proxy may differ from the original feed.
One stop at OR high, first active next minute open, no retries. Fill gaps at worse open; stop OR low; target actual modeled entry+RR*risk rounded up to tick, or disabled. One-point target-through. Cancel/flatten15:55CT (15:56-labeled open), including entry-bar protection. Exclude deterministic cash holidays/half-days at OR date. FULL chosen on2018–22 daily net-R Sharpe among passing models.

NQ costs$7.25RT plus$5 adverse cost each entry/stop/time fill; native MNQ$1.24RT (+$1.04 sensitivity),$.50 per such fill. Target no extra slippage. Slippage is a friction charge after nominal-price bracket placement; true slippage-dependent bracket reanchoring is not simulated. No extra spread double charge. Additional adverse tick and opposite minute path are diagnostics, not fitted variants.
Shorts zero; all and long statistics identical. Daily significance/Sharpe and standalone resampling use the full-session opportunity calendar (blocked holidays/half-days excluded consistently, EMA-failed normal days retained as zero);252-day annualization is per such opportunities, not a literal calendar-year forecast. Personal portfolio tests use the published book calendar instead. No actual broker equity/account results.

## Design selection and returns

|Design model|Trades|Win|PF|Mean netR/trade|Daily-R t|Pass|
|---|---:|---:|---:|---:|---:|---|
|FULL185|571|53.1%|1.31|0.149|3.40|True|
|CASH185|573|50.8%|1.24|0.079|1.87|False|
|NOEMA185|913|51.0%|1.17|0.077|2.28|True|
|SELECTED4|571|52.2%|1.35|0.175|3.61|True|
|SELECTED0|571|52.2%|1.37|0.186|3.68|True|

|Model|Period|Trades|Win|Net/NQ trade|PF|$ t|R t|Sharpe$|Sortino$|Calmar|Ulcer|EOD DD/NQ|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|FULL185|design|571|53.1%|$166|1.31|2.39|3.40|1.08|1.73|1.22|4.53|$15,800|
|FULL185|validation|423|51.5%|$192|1.21|1.59|1.85|0.82|1.31|0.76|8.27|$28,666|
|FULL185|all|994|52.4%|$177|1.25|2.72|3.80|0.93|1.48|0.71|4.49|$28,666|
|SELECTED4|design|571|52.2%|$192|1.35|2.67|3.61|1.20|2.00|1.41|3.87|$15,800|
|SELECTED4|validation|423|50.6%|$232|1.25|1.70|2.00|0.88|1.57|0.92|9.18|$28,666|
|SELECTED4|all|994|51.5%|$209|1.30|2.93|4.04|1.00|1.74|0.84|4.25|$28,666|
|SELECTED0|design|571|52.2%|$203|1.37|2.76|3.68|1.24|2.11|1.49|3.78|$15,800|
|SELECTED0|validation|423|50.4%|$246|1.27|1.68|1.92|0.87|1.67|0.97|9.41|$28,666|
|SELECTED0|all|994|51.4%|$221|1.31|2.94|4.05|1.00|1.84|0.89|4.15|$28,666|
|NOEMA185|design|913|51.0%|$101|1.17|1.79|2.28|0.80|1.26|0.64|7.49|$29,454|
|NOEMA185|validation|669|49.8%|$110|1.12|1.19|1.58|0.62|0.95|0.32|9.97|$62,363|
|NOEMA185|all|1582|50.5%|$105|1.14|2.06|2.76|0.70|1.08|0.31|6.96|$62,363|

By-year/all-long and author-window descriptive metrics are retained in metrics.csv and author_windows_descriptive.csv; exact author calendar is not complete before2018.

|Model|Year|Tickets|Net/NQ|PF|
|---|---|---:|---:|---:|
|FULL185|2018|120|$3,245|1.07|
|FULL185|2019|111|$19,785|1.81|
|FULL185|2020|121|$25,813|1.36|
|FULL185|2021|118|$27,940|1.41|
|FULL185|2022|101|$18,213|1.18|
|FULL185|2023|115|$29,111|1.37|
|FULL185|2024|102|$22,390|1.30|
|FULL185|2025|115|$7,076|1.06|
|FULL185|2026|91|$22,695|1.22|
|SELECTED4|2018|120|$11,505|1.25|
|SELECTED4|2019|111|$19,135|1.77|
|SELECTED4|2020|121|$29,053|1.41|
|SELECTED4|2021|118|$28,374|1.42|
|SELECTED4|2022|101|$21,838|1.21|
|SELECTED4|2023|115|$33,266|1.41|
|SELECTED4|2024|102|$21,810|1.29|
|SELECTED4|2025|115|$16,096|1.13|
|SELECTED4|2026|91|$26,920|1.26|
|SELECTED0|2018|120|$11,950|1.26|
|SELECTED0|2019|111|$19,135|1.77|
|SELECTED0|2020|121|$30,093|1.42|
|SELECTED0|2021|118|$28,374|1.42|
|SELECTED0|2022|101|$26,568|1.26|
|SELECTED0|2023|115|$29,861|1.37|
|SELECTED0|2024|102|$23,610|1.31|
|SELECTED0|2025|115|$23,541|1.19|
|SELECTED0|2026|91|$26,920|1.26|
|NOEMA185|2018|187|$2,434|1.03|
|NOEMA185|2019|176|$15,574|1.36|
|NOEMA185|2020|198|$10,260|1.07|
|NOEMA185|2021|180|$48,730|1.48|
|NOEMA185|2022|172|$15,388|1.08|
|NOEMA185|2023|180|$41,845|1.37|
|NOEMA185|2024|179|$26,272|1.20|
|NOEMA185|2025|175|$27,086|1.15|
|NOEMA185|2026|135|$-21,589|0.88|

## Placebos, filters and target comparisons

|Period|Breakout minus09:00 market R/day|Paired t|Random-time R p|Random-side R p|
|---|---:|---:|---:|---:|
|design|0.0179|1.21|0.003|0.001|
|validation|0.0058|0.35|0.032|0.014|
|all|0.0127|1.15|0.001|0.001|

1000 random-time and1000 actual-trigger-phase random-side controls perperiod. Fixed/random market controls use OR-width stops from their market fill; they change absolute stop geometry as well as timing. Therefore these are not proof that the trigger alone causes the difference. No control was selectable. Random sides condition on observed breakout days. All-null ledgers saved; initial side-null phase flaw corrected and candidate-return identity verified.
EMA removed trades and1000 random-drop controls are in diagnostics.json. Full-history removed profit is weakly negative, not significantly so; improvement over random drops does not establish a causal trend filter.

|Exit versus1.85R|Period|R/day difference|Paired t|
|---|---|---:|---:|
|SELECTED4|design|0.0122|1.57|
|SELECTED4|validation|0.0085|0.88|
|SELECTED4|all|0.0106|1.75|
|SELECTED0|design|0.0170|1.82|
|SELECTED0|validation|0.0078|0.70|
|SELECTED0|all|0.0131|1.82|

No exit improvement is called proven merely because total profit is higher. Target choices were not selected from validation. Trial/DSR audit is in trial_cost_audit.csv; dollar and R views are distinct, neither deletes prior author search.

## Drawdown at actual stated sizing units

|Model|Period|1% closed DD|1% floating DD|20-day block DD95|Permutation DD95|P shuffled DD>=10%|Missing held minutes|
|---|---|---:|---:|---:|---:|---:|---:|
|FULL185|design|12.8%|13.3%|15.4%|16.8%|69.4%|3163|
|FULL185|validation|7.4%|8.3%|16.8%|19.0%|82.5%|5|
|FULL185|all|12.8%|13.3%|17.5%|20.9%|95.7%|3168|
|SELECTED4|design|11.8%|13.0%|15.6%|17.2%|73.1%|3928|
|SELECTED4|validation|10.2%|11.5%|19.6%|20.0%|87.1%|8|
|SELECTED4|all|11.8%|13.0%|19.0%|21.4%|97.1%|3936|
|SELECTED0|design|11.2%|12.4%|15.2%|17.5%|71.7%|3974|
|SELECTED0|validation|10.2%|11.5%|20.7%|20.2%|90.2%|8|
|SELECTED0|all|11.2%|12.4%|19.8%|21.4%|97.7%|3982|

Recompute equity/risk on each resampled netR sequence; never permute original compounded dollars. 10000 permutations and10000 overlapping20-day blocks estimate full-sample closed-DD sequence risk; they are not one-year or floating-DD distributions. Floating values use minute OHLC path and ignore unknown path within missing minutes: incomplete risk estimates, not upper bounds. Integer100k MNQ1% sizing curves and excursions saved separately, without margin constraints; not an executable account certification. No observed unclosed ticket, but held gaps remain material.

## Current personal portfolio and Apex limits

Latest inspected Claude7f0800f personal roster/scripts/published outputs are blob-identical toafde088. Reuse reviewed19-leg native-fee baseline; do not assume funded changes absent. Fixed1MNQ ADD, EMPTY_ONB and REPLACE_ONB across A/B/C/D/FULL;1000 paired one-year10-day blocks, fee1.24 and1.04. Current common window ends at the earlier baseline/candidate date; manifest records it.

|Exit|2023+ FULL19 add annual mean|ADD DD95 change|90% annual effect interval|ONB replacement annual mean|Replacement interval|
|---|---:|---:|---|---:|---|
|FULL185|$2,426|+$815|[$-357,$4,609]|$-452|[$-3,521,$1,982]|
|SELECTED4|$2,901|+$824|[$-234,$5,489]|$23|[$-3,454,$2,893]|
|SELECTED0|$3,061|+$825|[$-215,$5,898]|$183|[$-3,431,$3,314]|

Intervals are5th/95th percentiles (90% intervals). All additions/replacements reduce FULL19 median-profit/DD95 relative to BASE. Read personal19/summary.csv, paired_effects.csv and joint_losses.csv for every cohort, native fee and joint-loss observation. Published book has approximate per-day fees, inherited Twin marks, pre2018 ledger booking and incomplete OT tail; no intraday margin or guaranteed hedge-delivery claim.
50K evaluation: LIMITED. 150K evaluation: LIMITED. 50K funded: LIMITED. 150K funded: LIMITED. Prepared baseline Bridge/OT/CLS paths do not establish causal joint overnight account exposure; source/native-platform parity is also absent. No new full-account pass/payout/blow-up numbers are invented. Standalone1MNQ EOD-only trail bootstrap is retained in diagnostics.json and is NOT a full-plan or intraday-breach estimate.

## Held-gap classification

Source audit after the initial raw-gap count: [CME SER8788R](https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2021/06/SER-8788R.pdf), section5, removes the daily15:15-15:30CT equity-index halt effective2021-06-28. Exactly3150 of3168 FULL185 held missing minutes match that scheduled pre-removal break; they are not missing tradable bars. The engine already preserves the position and takes worse reopening stop gaps; no returns or signals changed. Four other runs total18 minutes (2020-03-18:13;2025-04-02:1;2025-11-14:3;2026-08-06:1). Their cause remains unverified, including whether any was a regulatory halt. Do not fill them or label every absence bad data. held_gap_runs.csv and held_gap_classification.json retain all models and source mapping.
The table’s raw missing count includes scheduled halts. Floating OHLC equity still cannot certify latent liquidation/gap exposure or quote execution; sizing remains conditional on observed prices.
## Code and remaining checks

Generated PowerLanguage: agents/codex/code/ORB30_EMA_Research.txt; all code lives in research paths. User explicitly requested a code prototype before proof. Default full-session EMA20/RR1.85/integer1% sizing on100k strategy balance; UsePercentRisk=false uses fixed1contract for ledger reconciliation. CASH EMA and RR4/0 are explicit inputs. Use1-minute CENTRAL full-session chart, IOG and appropriate Bar Magnifier, with pre2018 history for warm-up. Native compiler/backtest unavailable here: code is NOT compiled or MC-confirmed.
Static review fixed midnight M30 continuity, preserved carried-position anchors across a missing flatten and blocked OR rebuild/entries until emergency exit; these cannot guarantee timer exits or broker acknowledgments. Built-in brackets initialize on entry bar and reanchor on observed actual fill; atomic gap behavior remains unverified. Code MaxContracts100 caps the otherwise uncapped Python integer diagnostic. Missing-bar carry guard exits at first available platform tick; Python instead flags an unclosed path. Author timer versus completed-minute flatten, native fills versus OHLC path, and entry-slip reanchoring are explicit differences.
Independent implementation review: agents/codex/results/orb30_ema_implementation_review.md;14 execution fixtures,2 midnight-counter fixtures,100 scaling/DD arithmetic paths. No independent raw-data replication, platform parity or promotion verdict.
Next: compile/replay the research code with exact session/input settings and export trades; repair/audit missing held minutes and roll-adjusted EMA provenance. No new target search, ranking or allocation change.
