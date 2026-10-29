# Factor-beta session screen — preregistration
Date: 2026-10-29. User authorized testing and automatic investigation of worthwhile future papers.
No selected-basket returns computed before this commit. Source: SSRN 4138715 and factor_beta_sessions_review_20261029.md.

## Scope and data
Partial historical replication: point-in-time S&P 500 stocks from Johnbrick123/sp500-data public release,
not all CRSP common stocks and not the full FF5-conditional regression.
Data acquired before signals: prices.parquet SHA256 e1c518c398c9ebd63b7ead13871343d2a575090513885a42db75406bd6004833;
membership_intervals.parquet 1e22ffca5e15d52872912413c55e64ead85bbb835e2148f5bbaaf84f33ea7cd0.
Release metadata digest must match. Record all additional hashes and URLs in a manifest.
Publisher quality claims are not our validation. Data are third-party, revised histories; source-mixed and missing opens remain limitations.
Do not redistribute the full vendor-derived dataset; commit acquisition code, metadata, derived signals/results.
No owned individual-stock series or data credentials were found. A FF5 mirror ends April 2020, insufficient for full design/recent coverage.
Use SPY total-return proxy as a restricted single market factor, not a claimed exact FF5 replication.

## Frozen rule and clocks
Universe: names in S&P membership [start,end) as of the last session of the prior month.
Estimate each month's beta by OLS with intercept over prior 252 sessions of total returns against SPY,
at least 200 common observations. Require positive prior close >=$5, and usable open/close on all last 20 sessions.
No future outcomes or full-sample post-ranking exposures enter selection.
Sort ascending beta, tie-break ticker; low 20 and high 20 names, equal dollar weights, frozen for month.
Two variants only:
A overnight: long high-beta, short low-beta, prior close to next open.
B intraday: long low-beta, short high-beta, open to same close.
Account reference $100,000, gross 1x, $50,000 per side; each of 20 positions $2,500.
Report fractional-notional results as the diagnostic reference AND whole-share floor($2500/entry price) results.
Unused notional stays cash. This is a fixed-notional daily reopen screen, no compounding.
No stop or extra filter: full session exit, no concurrent same-name overlap between variants because evaluated separately.
No Apex placement; no live orders. Research execution at recorded opens/closes is an optimistic mark, not a verified auction fill.
Fit by prior month-end, allow one full trading-day publication/decision buffer: use betas frozen at penultimate prior-month session
and membership/price eligibility as of that same session. First new-month close entry (overnight) can use the new weights;
for first-session overnight ending at new-month open use previous month's weights, known at prior close.
Intraday uses new weights from first-session open. All calculations ET cash sessions with DST-aware economic interpretation.
No after-close fits reused at that same closing fill.

## Returns, corporate actions, gaps
Use source adj_close for total daily returns; intraday = close/open-1.
Overnight = (1+total_daily)/(1+intraday)-1, preserving dividends/splits/spinoffs encoded in source.
Reconcile (1+overnight)*(1+intraday) to (1+total).
Ratio convention is a total-return attribution, not a fully observable raw overnight cash flow.
For integer sizing, express previous close on current share basis using prev_close*(adj_prev/prev_close)/(adj_today/close_today);
entry overnight uses this reference; this includes source total-return adjustments and is not exact native historical shares.
Separate optimistic dollar diagnostics from true executable cash ledger.
Use only records on consecutive SPY session dates; no forward fills; flag no_trade_days and nonpositive/bad OHLC.
If any selected leg lacks an executable price, retain an unresolved-day record; never replace that leg by zero or rerank to winners.
Compute conditional complete-day diagnostics with missing count prominent. Any unresolved selected day fails promotion/data gate.
Record selected-day halts and terminal exits (exit_gaps) separately. No borrow availability assumption grants actual executability.

## Costs, controls and power
Per side one-way 2 bp all-in commission/spread/slip; RT 4 bp on actual notional.
Stress one-way 5 bp (RT10bp), fixed not a new tuned entry.
Short borrow assumed 3% annual, actual calendar elapsed days/365 overnight; one day/365 intraday conservatively.
Financing on cash-funded long side zero; no credit for short proceeds/collateral. Actual locate fees unknown, so estimates remain optimistic.
Report gross/fees+spread/borrow separately and breakeven extra RT cost in bp gross.
Controls: high and low legs separately; equal-weight eligible-universe session long, market-adjusted return using prior fitted beta;
and 1,000 monthly random 20/20 baskets on identical eligible months, seed4138715, same costs/coverage.
Do not count constituent-days as independent: aggregate daily book returns, HAC lag20 and 20-session block bootstrap 2000 draws seed4138716.
Power gate: need >=1000 covered design sessions and >90% coverage; t2 mean hurdle computed from day SD and effective sample caution.
Net screen pass needs positive design net mean and HAC t>=2, positive 90% block-mean lower bound, positive net in >=4 of5 years,
positive market-adjusted gross mean, random-basket one-sided p<=.05, no unresolved days, and positive mean under cost stress.
These gates intentionally separate statistical sign from practical tradability. Missing borrow/execution evidence blocks promotion even if pass.

## Split, stop and reporting
Design 2018-01-01..2022-12-31, warm-up2017. No candidate returns earlier used as a search.
Run design for A and B once. If neither passes, STOP: no2023+ book returns, funded bench, exit/filter/size rescue.
If one/both pass, choose greater design net HAC t (tie A); evaluate that one on 2023..2024 only, third-party data latest snapshot,
once. Source ends2020 so2021+ is temporal extension, but already seen repo history is historical validation, not pristine holdout.
No recent test while a design/data gate fails. Report missing-source and clock limitations and all looks.
Use metrics.py where applicable for daily$ standard metrics, years, longs/shorts; exact stock ledger costs additionally.
This screen cannot authorize live deployment; independent checker/native quotes/borrow/whole cash ledger and account suitability follow.
