# Standing task: weekly Claude-Codex cross-review (every Friday, after Claude's Friday review)

Agreed 2026-10-23 (user's idea; structure from Codex and Claude). Goal: find and resolve errors, not force agreement. Two
models agreeing still needs evidence.

When the user says "do the weekly cross-review":
1. **Scope:** everything Claude changed this week on `claude/nq-trading-strategy-params-5h9d20` (git log since last
   Friday): strategy rules and code, results and reviews, account / bench simulations, process changes, TIER_LIST moves.
2. **Independent first:** write your own assessment of the week's material items before reading Claude's file for the same
   week (`agents/cross_review/YYYY-MM-DD_claude.md`), to limit anchoring. Then read it.
3. **Write `agents/cross_review/YYYY-MM-DD_codex.md` (on codex/work):** at most 5 material disagreements, most important
   first. Each: the claim, your position, the evidence (file / line / number), the practical consequence, and **the smallest
   check that would settle it**. Priorities: costs, roll handling, execution assumptions, statistical claims, portfolio /
   account contribution. No wording or style points. "No material disagreements" is a valid result.
4. **One round each, then a check:** after reading the other's file, each may write ONE response per disputed item; then
   the agreed deciding check is run. Items still open stay listed as **unresolved** (no forced agreement) and carry forward;
   resolved items do not.
5. **Routine checks vs new research:** file comparisons, accounting reconciliation and code checks can be run at once by
   whoever raised the item. A new strategy backtest still needs a committed plan, trial counting and the existing
   validation gates.
6. **Consequential errors don't wait for Friday:** a confirmed accounting or execution defect (wrong costs, a bug that
   changes a live strategy's behaviour or a plan decision) goes to the user as soon as it is confirmed.
7. **Judgement calls go to the user properly:** a disagreement about assumptions or the user's risk preferences, that no
   test can settle, goes to the user with both views, the uncertainty and a recommendation (not a forced yes / no).
8. **Rules unchanged:** nobody changes the trading plan or the live setup through this review. Keep the weekly output
   short and link the evidence and fixes.
(Refinements 4-7 from Codex, 2026-10-23, agreed by Claude and the user.)

Claude does the same on its side inside the Friday review, then writes the joint summary
(`agents/cross_review/YYYY-MM-DD_summary.md`): agreed, disputed (with the settling check and who runs it), user decisions.
