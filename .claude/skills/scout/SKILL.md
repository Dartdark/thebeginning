---
name: scout
description: Paper scout - search arXiv, NBER, SSRN abstracts and free author copies for papers that could become NQ/ES strategy hypotheses, skip what we already reviewed, read and test the ones with a free full text, and list SSRN-only ones for the user to download. Use when the user says "scout", "/scout", "find papers" or when the scheduled paper-scout run fires.
---

# Paper scout (user, 2026-10-29: run on demand any time, plus the scheduled runs)

Goal: bring in strategy hypotheses for NQ / ES (Apex intraday, flat by 15:59 CT) without the user searching by hand.

## 1. Search (30-50 queries, newest first, enough to find ~10 readable papers; the user may add a topic after "/scout")
- arXiv API (works from the cloud): `https://export.arxiv.org/api/query?search_query=cat:q-fin.TR+OR+cat:q-fin.ST+OR+cat:q-fin.PM&sortBy=submittedDate&max_results=50`, plus keyword queries.
- NBER new working papers (`https://www.nber.org/api/v1/working_page_listing/contentType/working_paper/_/_/search?page=1&perPage=50`).
- SSRN through WebSearch (site:papers.ssrn.com ...). SSRN pages / PDFs answer 403 from the cloud: look for a free copy
  (author page, university repository, arXiv, Google Scholar "all versions") before asking the user.
- Topics that have worked for us (TIER_LIST): forced flows at a known time (index rebalancing / reconstitution, option
  dealer hedging, 0DTE, expiration, month-end / quarter-end, pension rebalancing, payroll, leveraged-ETF rebalancing,
  benchmark fixes, futures roll, MOC / closing auction); overnight vs intraday; intraday momentum / reversal in index
  futures; macro-announcement timing (FOMC, CPI, NFP, Treasury auctions); volatility / VRP timing; execution and
  slippage in futures. Low priority: single-stock cross-sections, daily multi-day holds, crypto-only, FX-only.

## 2. Deduplicate
Skip a paper already in `TIER_LIST.md`, `agents/codex/EXECUTION_REFERENCES.md`, `papers/`, `papers/SCOUT_LOG.md`, or
Codex's scout records (`git show origin/codex/work:agents/codex/research/scout/progress.json` and `records/`).

## 3. Triage (abstract) -> log every paper looked at in `papers/SCOUT_LOG.md`
One row: date, source id + link, title, verdict: SKIP (why, 5-10 words) / READ / NEED PDF.
READ only when: a mechanism that forces trading at a known time or a measurable market behaviour, transferable to
NQ / ES intraday (or a funded-safe overnight hold), with data we have (`data/`, 1-min NQ / ES / YM / CL / GC / BTC / 6E).

## 4. Read and test (user, 2026-10-29: up to 10 full reads per run; test every one that fits, each test counted in
##    `analysis/trials.py` so the multiple-testing bar rises with the search)
- Free full text: download to `papers/` (PDF, research papers only), answer the four questions (about / finds / why it
  should make money / can we build on it), test per CLAUDE.md 'Testing standard' (costs, by year, 2023+, placebo,
  longs / shorts), rank in `TIER_LIST.md`, add execution lessons to `EXECUTION_REFERENCES.md` (next free E number).
- Promising (C or better): also the plan benches (add AND replace), as usual.

## 5. Report
- Commit + push (CLAUDE.md 'Branches'; pull first).
- If running in the Papers session: send_message the master session (`session_01Wk1fPYssjbaEfe21f4v6vD`) one short
  verdict line per paper read, plus the NEED PDF list.
- Notify the user (PushNotification + `python3 analysis/send_alert.py`) ONLY when a paper rates C or better or a PDF is
  needed: "Scout: N new, best X (grade). Need PDFs: <links>". Nothing found -> no alert, just the log row.
