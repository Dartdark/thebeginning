# LDF flow sizing preregistration: WATCH — protocol frozen; timing evidence still needed
Summary: Registered one 1/2/3 MNQ LDF sizing rule; no strategy return test was run.
Date-only inventory confirms 492 design entries and 895 through the frozen 2026-10-09 cutoff.
Assuming $810 per-NQ trade SD: high-low hurdle $179 for t~2; $250 for approximate 80% power, before controls/clustering.
Free fund inputs pass 2017-onward identity checks; publication timing and revisions remain unresolved.
Next: Claude reviews the conditional protocol and data assumptions before any return screen; keep the trading roster unchanged.

Plan: `agents/codex/plans/ldf_flow_sizing.md`, initial commit `383014a`

Script: `analysis/codex_ldf_flow_prereg_inventory.py`

Output: `analysis/outputs/codex_ldf_flow_prereg/`

Return trials run: **0**. Account simulations: **0**. Research caches built: **0**.

## Rule (registered, not tested)

Use prior-NAV-date direct fund assets, weighted by L*(L-1), divided by the trailing 20 completed sessions'
median NQ 14:01-15:00 dollar volume. Rank reset pressure **per fixed 1% move** against its previous 252 cash
sessions; low/middle/high gives 1/2/3 MNQ, missing input gives the current 2 MNQ.
This isolates asset/liquidity variation from another price threshold; it is not a measured remaining-order signal.
Existing LDF entries, sides, stop and exits stay fixed. All LDF events enter the test regardless of roster occupancy.
Same-day eventual volume and same-day final NAV are forbidden. Two-NAV-session asset lag is a fixed timing stress.

## Results: input inventory only

| Item | Finding |
|---|---|
| Design MC entries, 2018-22 | 492: 103 / 89 / 89 / 109 / 102 by year |
| Entries through frozen cutoff | 895; one 2026-10-12 entry is outside the 2026-10-09 evaluation cutoff |
| Fund rows, 2018-01-02 to 2026-10-09 | 2,205 for each fund |
| Assets vs NAV*shares*1000, 2017 onward | Maximum relative error: TQQQ ~0, SQQQ 0.1012%, QLD ~0, QID 0.00165%; all <1% |
| Full-history caveat | 140 SQQQ rows in 2010 have zero reported shares despite positive NAV/assets; outside all proposed inputs |
| Illustrative thirds | 164 observations each before missing-input/rank effects; these are not actual candidate group counts |
| High-low gap for t~2 / ~80% power | $178.90 / $250.46 per full NQ, assuming IID and SD $810 |
| Publication time / original historical vintages | Neither verified by the files |

Fund data checks independently reproduce selected input claims, not Claude's complete gap/calendar audit or
his reset-dollar/market-volume estimates. The initial inventory assertion applied all-history share consistency
too broadly and failed on 2010 SQQQ; validation is explicitly scoped to 2017 warmup onward, with the excluded
rows recorded. No return-conditioned result or trading rule was changed after this check.

## Placebos and account level (registered only)

The design gate requires incremental net performance, a confound-adjusted high/low contrast, matched randomized
sizes and a positive two-session-lag stress. Any failure stops before 2023+ returns or the funded bench.
After a design pass, one already-seen historical replication precedes paired funded comparisons of baseline,
replacement, timing stress, addition and empty slot. Addition duplicates LDF exposure and cannot rescue a failed
replacement. The protocol includes skipped-trade/filter checks because cushion rounding can turn 1 MNQ into zero.
No placebo or account performance is reported here because none was run.

## What could make this wrong

Previous-date data may still be published late or revised. Lagging is not historical-vintage verification.
Fund assets grow with market regime; normalization and within-year controls help but do not establish causality.
Intraday capital flows and residual execution remain unseen. Power is optimistic before controls/dependence.
2023+ has already been seen repeatedly, so it is historical replication; frozen forward paper evidence remains mandatory.
The evidence sheet is NEEDS DATA, not TEST. The user requested the protocol while this gate was unresolved;
writing it does not authorize strategy returns or live adoption.

## Differences between MultiCharts code and the test

No MultiCharts code or strategy test written. No live, roster, broker, VPS or API-key change.

## Reproduction and reviewer handoff

Run `/workspace/venvs/thebeginning/bin/python -B analysis/codex_ldf_flow_prereg_inventory.py`.
It reads immutable `c23fc02:data/letf/*.csv` blobs and only Type/Date from the MC trade sheet, then records hashes.
It does not read strategy P&L, prices or exits, calculate candidate scores, build caches or call simulators.
The six required Python dependencies import successfully in that configured environment.

Tell Claude: review `agents/codex/results/ldf_flow_sizing_prereg.md` and the linked conditional plan before returns;
492 design entries, one primary sizing map, lagged liquidity, unresolved vintage/timing gate, zero return trials.
