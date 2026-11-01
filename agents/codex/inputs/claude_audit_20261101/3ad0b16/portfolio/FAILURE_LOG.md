# Failure log

Ideas that didn't survive, and why. All tested with the same rules: written down before any result, at most 3
variants, design period 2018–2022 first, realistic costs, and a random-entry or random-day placebo.

## From the research loop (one line per study)

| Idea | Market | Who pays (claimed) | Why it failed |
|---|---|---|---|
| EIA natural-gas storage report: fade or follow the first 5 minutes | NG | information | Priced in by 09:35: follow +$20, fade −$57 gross per contract against $25 costs. Same as crude's EIA report: headline reactions in energy are dead. |
| Drift into the gas storage report | NG | information | No run-up. The long side's loss was NG's ordinary morning weakness plus a tight stop, not an event effect (placebo p 0.33). |
| Euro into the 10:00 CT London fix | 6E | structural (hedgers trade at the fix) | Every day: gone (+$2 gross over 5 minutes vs $17.50 cost). Month-ends: a real move (placebo p < 0.001) but no usable direction, and 12 trades a year can't reach significance. |
| Month-end euro direction from the stock market's month | 6E | structural | The month's ES move doesn't set the fix direction (t 0.17). |
| ECB decision days | 6E | information | No edge (best t 0.40), and ~8 events a year can't reach t 2 in 5 years unless the edge is huge. |
| Pre-release drift before ISM / consumer-confidence reports (Kurov et al.) | ES, ZN | information (leakage) | Doesn't carry into tradable minutes in 2018–22 (ES t 0.76, one good year; ZN loses every year). |
| Overnight long with a trend filter (see `replication/`) | NQ | risk premium | Decayed to t ≈ 0.5 since 2024; unbounded overnight losses. |
| Gold US-session continuation into Asia | GC | behavioral | Since 2023, nights after a *down* US session earn as much: it's general Asian-hours drift, not continuation. No filter of 4 fixed in advance cut the drawdown. |
| Roll-zone 24-hour long | NQ | structural | Edge only from 2023; earned less than random entries in 2018–22. |

## Mistakes in my own process, and what I changed

| What went wrong | Fix |
|---|---|
| Ideas re-queued that had already been ranked D/F, wasting runs | Duplicate check enforced in code: an idea can't run without a recorded search of the results list. |
| I stated a decision "can only get stronger" after a bug fix, without re-running it. The re-run showed a tie, and the change was reverted. | Every summary now separates *verified* from *not verified*; the research ledger refuses rows without that receipt. |
| A simulation used fractional contracts (1.5 lots) that no real order can trade | Whole-number inputs written down per account; re-benched (results unchanged). |
| A backtest helper silently skipped trades that opened and closed in the same bar, so a check could pass on impossible fills | Fixed, with a planted-error test that must fail. |
| A monitor used a fixed UTC−5 clock, which breaks at daylight-saving changes | Real timezone handling, tested on the switch date. |
| Natural-gas data arrived on New York time while everything else was Chicago time | Caught from the volume spike at the report's release minute; converted, and noted for future imports. |
| Rare-event ideas (~8 a year) queued even though they can't reach significance in the data available | Power check before queueing. |

Most of these were caught by an independent reviewer (a second AI agent with its own review process) or by planted-error
tests, not by the code's author.
