# Task 01 verdict: CL Sunday Fade, Antigravity (Gemini) blind rebuild in Jesse (2026-10-17)

Output: branch `antigravity/jesse`, `tasks/out_01/` (report, strategy.py, trades.csv), commit c0d93a6.

## Result: PASS (with one data mix-up, found and reported by Antigravity itself)

| Run | Trades | Gross points |
|---|---|---|
| MultiCharts report | 97 | 65.98 |
| Claude's Jesse port (`analysis/jesse`) | 97 | 66.29 |
| Antigravity, data read as Eastern ("CSV = ET" variant) | 97 | 66.29 |
| Antigravity, data read as Central (its primary, as the task text said) | 96 | 54.96 |

- **The ET variant is the correct one for the files it used, and it equals Claude's Jesse run exactly.** It also
  matches MultiCharts within 0.5%.
- **The primary run used the wrong time reading.** Antigravity took its CL data from the user's own folder
  `C:\NQData` (its import script `research_scripts/ingest_batch.ps1`), not the repo copies in `research_scripts/data`.
  - The repo copies are stamped in Central time, with the daily break at 16:00-17:00, as the task said.
  - The `C:\NQData` files are stamped in Eastern time, with the break at 17:00-18:01; most likely they were exported
    from the Eastern-time CL chart.
  - Antigravity noticed the mismatch, followed the text as instructed and ran the other reading too. Reading Eastern
    data as Central moves the 10:00 ET exit to 9:00 ET, which explains the lower total.
  - Even in the primary run, signal Sundays match MultiCharts on 96 of 97 (missing 2018-04-22, at the start of its ATR
    warm-up).

## Quality of the work

- **Good:**
  - real data forensics: it found the Eastern stamps, the delayed Sunday opens (2019-09-15, 2020-03-08, 2026-03-01 open
    at 18:03) and the absent −$37 April 2020 print;
  - it found the missing-minute trap on its own (forward-filling before a bucket erases the Abqaiq gap);
  - it found a Jesse trap Claude had avoided without knowing: a 5-minute route only executes when the bucket's 5th minute
    exists;
  - it ran sensitivity variants.
- **To fix next time:**
  - it used `C:\NQData` instead of the task's files;
  - it imported every symbol in that folder;
  - it saved output in two places;
  - it ran an unrequested Golden Cross backtest (2024 overnight file only: −5.2%, consistent with the F rating).

## Consequence for tasks 02-08

`COMMON_NQ.md` now says which files to use. The `C:\NQData` NQ files are in Central time (per its report), so they are
fine if identical to the repo copies; the task asks it to check.
