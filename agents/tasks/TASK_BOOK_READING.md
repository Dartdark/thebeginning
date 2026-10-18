# Task BOOK: read a trading book and extract testable ideas (no backtesting)

Read `tasks/ANTIGRAVITY_BRIEF.md` first (rules 0, 6 and 7 apply here). One book per conversation.

## Input
- The book file the user names (PDF / EPUB) in `C:\Books\` or wherever the user says. **Never copy the book into the
  repo or commit it** (copyright). Only your notes go in git.
- Book short name for folders: `<book>` = e.g. `chan_algotrading`, `narang_blackbox` (lowercase, no spaces).

## What to do
1. Read the whole book.
2. Write `tasks/out_book_<book>/ideas.md` with **every concrete trading rule or market effect** the book describes,
   one block per idea, in this exact format:

```
### <n>. <short name>
- Where: chapter / section, page (or EPUB location)
- Quote: "<the book's own words for the rule or finding, 1-3 sentences>"
- Rule as written: <entry, exit, stop, sizing, market, bar size, holding time — only what the book states>
- Book's evidence: <what the book reports (market, years, numbers) — or "none given">
- Mechanism (the book's): <who is forced or paid to trade, and why they accept losing; "none given" if the book has none>
- Mechanism (my inference): <only if the book gives none; label it clearly as yours>
- Apex fit: <flat by 15:59 CT? markets NQ / ES / CL / GC / ZN / micros? single stop loss that fits a $2,000 trailing drawdown? yes / no + why>
- Already tested? <check the "Already tested and failed" list in the brief; say which item it matches, or "no">
```

3. At the end of `ideas.md`, a ranked short list: **at most 5 ideas** that are (a) Apex-compatible, (b) not already
   tested, (c) have a stated mechanism. Rank by how clear the forced trader is, not by the book's backtest numbers.
4. Write `tasks/out_book_<book>/summary.md` (one page): what the book is about, its main claims, and which parts are
   general advice (risk, backtesting hygiene, sizing) rather than trade rules.

## Rules
- **No backtests, no code, no optimisation** in this task. Claude tests the short list on its own data.
- **Do not invent:** if the book does not state a number, time, threshold or market, write "not stated". Never attach a
  rule to the book that it does not contain (this is what made NarangBlackBox and the academic write-up fail).
- Concepts without a rule (e.g. "use a transaction-cost model") go in `summary.md`, not in `ideas.md`.
- Skip pure options, stock-picking, crypto-spot and multi-day/overnight rules in the short list, but still list them
  in `ideas.md` with Apex fit = no.

## Output, then push
`tasks/out_book_<book>/ideas.md` and `summary.md` only. Then:
`git add tasks/out_book_<book>` → `git commit -m "book: <book>"` → `git push origin antigravity/jesse` → say "pushed".

Prompt for the user to paste:
`Read tasks/ANTIGRAVITY_BRIEF.md, then tasks/TASK_BOOK_READING.md, and do it for the book <file path>, short name <book>.`
