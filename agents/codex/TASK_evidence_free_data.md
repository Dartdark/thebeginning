# Task 2 (after the live audit): evidence sheets, free data only

Branch `codex/work`. Follow step 0 of `agents/codex/BUILDER_BRIEF.md`. **No purchases** (the user can't buy data until
the plan produces live results). No backtests in this task: sheets only.

Write at most **3** evidence sheets in `agents/codex/evidence/` plus `agents/codex/evidence/SUMMARY_free_data.md`
(ranked, each with TEST / DON'T TEST and one line). Each idea must be testable with data that is:
- already in the repo (`data/`: NQ / ES / YM / CL / GC / ZN / 6E / BTC 1-minute, The Bridge GEX / OI / order flow,
  COT, DIX, VIX / VXN daily, SPY daily, treasury auctions, mega-cap earnings dates, `data/letf/` fund history), or
- free and downloadable with history back to 2018 (e.g. FINRA daily short-sale volume files, Cboe daily market
  statistics, FRED / ALFRED vintages, Fed / Treasury / BLS calendars, issuer NAV histories). Say exactly where and
  check that history and publication timing are available.

Each sheet must include the power check with numbers and a gap check against the occupancy map. Ideas already in
TIER_LIST (including this week's six Codex rejections) don't count. Prefer forced flows that land in NQ / ES.
Commit, push, say "free-data sheets pushed". Claude reviews before any test.
