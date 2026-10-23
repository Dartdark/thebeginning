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
4. **Rules:** any new backtest still follows the pre-registration rules; nobody changes the trading plan or the live setup
   through this review; anything that needs the user's decision goes in one paragraph with both views and a yes / no question.

Claude does the same on its side inside the Friday review, then writes the joint summary
(`agents/cross_review/YYYY-MM-DD_summary.md`): agreed, disputed (with the settling check and who runs it), user decisions.
