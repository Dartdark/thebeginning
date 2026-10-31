# Exchange mechanics: bounded offline feasibility screen

Summary: NEEDS DATA. No distinct TEST candidate is supported by this repository-only screen outside the
recently screened EIA, COT, auction-imbalance, ETF closeout, Treasury, pension, expiry, index-roll, leveraged-ETF
and volatility-control families. This is a bounded assessment, not a claim that no distinct edge exists.

Scope: saved source-code definitions, evidence documents, filenames and CSV header lines only. No raw price
values, strategy return files, new return calculations, network requests or execution/account tests were used.
New economic configurations evaluated: zero. No new milestone, alert or reason to pause research.

## Price-limit or halt-release hypothesis: NEEDS DATA

A constraint-release mechanism would need the applicable exchange rule and historical version, official
reference settlement and price bands, actual trigger/halt/reopen times, and executable contract observations.
This bounded search found no saved source establishing that complete input set.

`analysis/codex_s03_accounts.py:262` states that the existing R2 calendar certifies no March2020 circuit-breaker
interval. Lines273-274 explicitly refuse to relabel those intervals as known closures without source evidence.
Its existing maintenance/holiday mask therefore cannot supply a historical halt-release event calendar.

The inspected header lines of `data/CL_1min_2018.csv`, `data/GC_1min_2018.csv`, `data/BTC_1min_2018.csv` and
`data/ES_1min_2018.csv` contain only `date,time,open,high,low,close,volume`. They do not identify official
settlement references, halt states or individual contract months. Missing bars alone do not establish a halt,
its reason, a legal trigger level, or the first executable reopening price. No band or reopening event was
inferred from OHLCV, and no hypothetical return test is justified.

## Other apparent alternatives

`analysis/overnight_round.py:2` describes the local research inputs as continuous futures. Line14 explicitly
says carry was not tested because the second contract month is absent. A calendar-spread, delivery squeeze or
term-structure mechanism cannot be manufactured by treating a continuous-series roll jump as a quoted spread.

`analysis/s_rank_btc_round1_test.py:1-23` already defines CME Bitcoin weekend/maintenance gaps, intraday
seasonality, the ETF benchmark window, NQ-engine ports and NQ spillover. A shifted clock, ticker port or new
threshold on those inputs would not independently establish the requested new mechanism. No derivative
funding-rate or futures/spot basis input was established by this screen.

## Next evidence needed

Before a new exchange-constraint hypothesis could receive a TEST evidence sheet, obtain and audit the official
historical rules, reference prices and event clocks, appropriate individual-contract observations and native
contract costs. Keep source feasibility separate from economic preregistration and return trial counts.
Continue the committed EIA source intake and later distinct evidence searches without rescuing failed families.
