# FinRL 2020 paper: bounded reproduction-admission checks

Question: does the author's inspectable historical implementation justify a new strategy replication?
Source: SSRN 3690996, uploaded nine-page paper; the old paper URL redirects to FinRL-Trading.
Freeze the latest repository commit before the uploaded PDF's creation date:
`5b9290ed706efa34aaff96e10761af428a154076`, October 19, 2020. This is a paper-era snapshot,
not proof it generated Table II. Archive its inspected code, tree and hashes.

This plan permits only no-return data census, static source checks and five synthetic scenario groups.
No RL training, historical strategy returns, saved-equity performance selection, parameter search,
or portfolio/evaluation/funded bench is authorized by passing a mechanics test alone.

Predeclared checks, before running fixtures:
1. Execute original buy/sell methods with cash exactly equal to gross purchase cost; check fee-inclusive cash remains nonnegative.
2. Execute a fractional continuous action; compare actual shares with the source's integer-share specification.
3. Fully liquidate a position, normally and at high turbulence; reconcile cash fee with the reported fee counter.
4. Step an invented two-day, 30-stock frame: identify which observation's close feeds a decision and which price fills it.
   No next-bar prices or auction assumptions may be silently substituted. Record any unavailable executable clock.
5. Check source turbulence inputs, missing-value filling and fold windows; on an invented panel compare its Mahalanobis
   statistic with the paper's return-based definition. Compare paper/README/code validation lengths and dates.

Inspect only original class methods or named preprocessing functions via AST with minimal inert dependency stubs;
do not import/run foreign training, broker code or package instructions. No corrected version or rescue parameters.
Try the exact public pinned raw stock/benchmark CSVs; verify downloaded Git blob hashes, then census fields,
tickers, dates, missingness, duplicates, adjustments and panel alignment without price-return performance calculations.

Stop rule: a causal execution-clock, account constraint, schema, data-identity or paper/code mismatch blocks
economic reproduction and account stages. Record actual failures and limitations; a successful code-only check
does not establish alpha. A later corrected economic replication would be a separately frozen experiment,
not a claimed reproduction of the source result. Five groups maximum; zero strategy-economic definitions.

Preserve source claims separately: ensemble 13.0% annual return, Sharpe 1.30, -9.7% maximum drawdown,
2016-01-04 through 2020-05-08, $1m equity-share portfolio, modeled 0.1% per trade value.
The daily multi-stock rule has no earned intraday Apex implementation or current personal allocation.
