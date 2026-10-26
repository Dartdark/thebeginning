# TASK: strategy hunt v2 (replaces the open-ended t6 program) — written by Claude for the user, 2026-10-26

Read `agents/codex/BUILDER_BRIEF.md`, `LESSONS.md`, `TIER_LIST.md` (search it before every idea) and
`agents/codex/research/t6_program.md` first. Work on `codex/work`, write only where the brief allows.

## 1. What changed and why
The t6 program ran 65 evaluations, none passed. A NEW standalone t >= 6 is about twice the best piece in the book
(Vault Break t 4.6); the whole six-leg funded plan only reaches 6.8. Stop the t6 program at its current hypothesis.
**New goal: find strategies that IMPROVE THE BOOK**, not a single giant t-stat. A piece earns a place when it:
- passes the promotion bar: net trade t >= `metrics.t_threshold(N_items)` (about 3.6 now) on 2018-26, or DSR >= 0.95;
- is positive in 2018-22 design AND in 2023+, at native micro costs ($1.24 + 1 tick per market / stop fill per MNQ);
- beats random-time and random-side placebos at the same exits (p <= 0.05);
- AND improves at least one plan on the repo's own benches, against the plan AND the empty slot:
  personal book return/DD (`analysis/personal_portfolio.py`, 1-year block MC), 50K / 150K funded bootstrap
  (`analysis/funded_bootstrap.py`, paired histories), or 50K evaluation pass rate (`combine_levers_test.challenge`).
A strategy with t 3.5 and correlation ~0 to the book is worth more than t 5 that trades the same hours as VB / DT / RS.

## 2. Where to look (ranked by what has worked in THIS repo)
1. **Forced / scheduled flows** (every A / S item is one): someone must trade at a known time for a non-price reason.
   Ideas not yet in TIER_LIST to check first: month-end / quarter-end pension rebalancing into the close (use
   `data/SPX_daily.csv` for the month's equity move as the 'size'), options-expiry pinning on ES / NQ quarterlies,
   VIX futures settlement (Wednesday) hedging flow, index-reconstitution days (Nasdaq-100 December, S&P quarterly),
   CL / GC contract-roll windows (GSCI / BCOM roll was t 0.5: look at the front-month expiry squeeze instead),
   Treasury auction tails on ZN measured in yield (gross > cost first), CTA trigger levels only as filters.
2. **Hours the book leaves empty.** Your own occupancy map: Tue-Fri 01:00-03:00 CT always flat; 10:00-11:00 CT ~40% busy.
   Also instruments with ~0 weight: ZN, 6E, YM, CL intraday, GC intraday, MES. Same mechanism, different instrument =
   the cheapest real diversification.
3. **Data the book barely uses:** `data/OF` (order flow), `data/GEX*` (dealer gamma), `data/letf` (leveraged-ETF AUM),
   `data/cot`, `data/DIX.csv`, `data/VIX*` term structure, `data/treasury_auctions.csv`, earnings files. A filter or
   sizing rule on an EXISTING plan leg counts too (LDF + order flow was t 2.1 and is still open).
4. **Confirmation work on B items** (cheap, high value): Swing Target v3, FVB shorts, PAPERTREND v2, BB_MRM,
   S03 v2, T_ONESIDE. Do for each what you did for Day Flow Six: independent rebuild from the spec, MC-list parity,
   half-day / holiday holds, fill-through and real-fee stress. A B item confirmed into the plan beats a new idea.

## 3. How to spend trials (to keep the odds good)
- **Gross first:** before any rule, measure the raw effect (mean move in the window, t, by year) gross of costs. If gross
  < 2x the round-trip cost, stop: no trial counted beyond that screen.
- **Mechanism sheet before data:** who is forced, when, how big, why it isn't arbitraged away. No mechanism, no test
  (LESSONS: price patterns fail here again and again).
- Max 5 configurations per pre-registration; design 2018-22, then 2023+ once; never retune after seeing 2023+.
- Prefer rules with >= 100 trades and a simple exit (time exit or one stop); no optimized brackets.
- After a design pass, run the plan benches BEFORE more robustness work: if it can't improve a plan, stop there.
- **Budget:** at most 60 counted evaluations for this task (on top of the 65 already used), or 10 hypotheses,
  whichever comes first. Then write a summary and stop. Report the running count in every result.

## 4. Deliverable per candidate
`agents/codex/results/<name>.md`: mechanism, pre-registration commit, gross screen, design / 2023+ / by-year / long-short,
Sharpe / Sortino / PF / Calmar / Ulcer, placebos, Monte Carlo at plan size, the bench rows (add / replace / empty slot),
half-day and holiday check (no exits after 15:59 CT for Apex pieces), and a one-line verdict. If it passes: a
PowerLanguage draft under `agents/codex/` for Claude's MultiCharts check. Never touch live files, the VPS or `claude/*`.
