# Task PAPERS: screen a folder of research papers (no backtesting)

Read `tasks/ANTIGRAVITY_BRIEF.md` first (rules 0, 6 and 7 apply here). One folder per conversation.

## Input
- Every PDF in the folder the user names (default `C:\Papers\`). Only the shortlisted candidate PDFs in **Send to Claude** will be copied into the repo; never copy or commit skipped papers.
- Batch short name for the folder: `<batch>` = e.g. `2026_10_19` (the date).

## What to do
For **each** PDF, read at least the abstract, the introduction, the data section, the main results table and the
conclusion. Then write one block in `tasks/out_papers_<batch>/screen.md`, in this exact format:

```
### <n>. <title> (<authors>, <year>, SSRN <id> or "no id">)
- File: <file name>
- Has results? <yes / NO: framework, proposal or survey only>   (quote the sentence that shows it)
- Quote: "<the paper's own words for its main finding, 1-3 sentences>" (page)
- Market and data: <assets, bar size (daily / intraday / tick), years>
- Index or single stocks? <does the effect push the whole index / futures, or only some stocks vs the market
  ("abnormal returns", "additions and deletions", "cross-section") which nets out in NQ / ES?>
- Forced trader: <who must trade and why, in the paper's words; "none given" if none>
- Timing: <the exact time window of the effect, as stated; "not stated" if none>
- Costs included? <yes / no / not stated>
- Out of sample or other markets? <yes + what / no>
- Size: <the effect in bp, % or Sharpe, as stated>
- Score (1 point each): forced trader named / intraday or futures data / data runs to 2018 or later /
  out-of-sample or another market / costs included  =  <0-5>
- Apex fit: <tradeable on NQ / ES / YM / CL / GC / ZN or micros, entry and exit between 17:00 and 15:59 CT,
  one stop that fits a $2,000 trailing drawdown? yes / no + why>
- Already tested? <match against the "Already tested and failed" list in the brief; name the item, or "no">
```

At the end of `screen.md`:
1. **Send to Claude** (at most 5): papers with results, score ≥ 3, an index-level (not single-stock) effect, Apex fit
   yes, not already tested. Rank by how clear the forced trader and the time window are, not by the paper's returns.
   For each: one line on the trade it implies (market, entry time, exit time, direction rule) as **"my inference"**.
2. **Skip** list: every other paper, with the one reason (no results / single stocks / daily only / not Apex / tested).

## Rules
- **No backtests, no code, no optimisation.** Claude tests the "Send to Claude" papers on its own data.
- **Do not invent.** If a paper does not state a number, time, threshold, market or year, write "not stated". Never
  attach a finding to a paper that it does not contain; every Quote must be copied from the PDF with its page.
- A paper you could not open or read fully: say so in its block, score it 0, put it in Skip.
- Warning signs to name in the block when present: "machine learning predicts" with no mechanism, crypto / penny
  stocks only, sample ends before 2015, Sharpe above 3 on a simple rule, one unaffiliated author with huge returns.

## Output, then push
`tasks/out_papers_<batch>/screen.md` plus the shortlisted candidate PDFs in **Send to Claude** (at most 5) placed into `tasks/out_papers_<batch>/`. Then:
`git add tasks/out_papers_<batch>` → `git commit -m "papers: <batch>"` → `git push mine HEAD:antigravity/jesse` → say "pushed".

Prompt for the user to paste:
`Read tasks/ANTIGRAVITY_BRIEF.md, then tasks/TASK_PAPER_SCREEN.md, and screen every PDF in C:\Papers, batch name <batch>.`
