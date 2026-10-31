# Task: evidence sheets for 3-5 new candidate ideas (NO backtests)

Branch `codex/work`. Follow step 0 of `agents/codex/BUILDER_BRIEF.md` (the evidence sheet).

Write 3 to 5 evidence sheets in `agents/codex/evidence/`, one file per idea, plus `agents/codex/evidence/SUMMARY.md`
ranking them (best first) with each verdict (TEST / NEEDS DATA / DON'T TEST) and a one-line reason.

Rules:
- **No backtests, no return calculations on our price data** for these ideas: sheets only. You may read TIER_LIST,
  WATCHLIST, `analysis/`, the occupancy map and outside sources (papers, exchange / issuer documents), and you may count
  events (e.g. how many releases a year).
- Ideas must not already be ranked in TIER_LIST in the same form. Improving an existing plan strategy with better data is
  allowed if the sheet says so.
- Claude is writing its own sheets independently for comparison; don't look for them.
- Commit and push to `codex/work` and say "evidence sheets pushed".
