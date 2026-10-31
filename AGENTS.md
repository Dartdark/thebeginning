# Instructions for Codex (and other coding agents)

This repo holds NQ / ES futures strategy research for Apex prop accounts (MultiCharts PowerLanguage + Python tests).

- **Codex is the strategy builder.** Read `agents/codex/BUILDER_BRIEF.md` before any task and follow it exactly.
- Tasks for Codex are in `agents/codex/` (test tasks: `TEST_01_*.md`, `TEST_02_*.md`; later ones: `TASK_*.md`).
- Work on branch `codex/work` (test tasks: the branch the task names). Never push to `claude/*` or `antigravity/*`.
- Never touch live trading, the VPS, broker settings or API keys.
- **All project chats: paper reviews answer five questions**, in the saved review and chat: what is it about;
  what does it find; why does it make money, if it does; can we build on it; **can a strategy code be made?**
  State missing rules/data and distinguish code feasibility from demonstrated profitability. Full guidance:
  `agents/codex/BUILDER_BRIEF.md`, "Paper-review questions" (user addition, 2026-10-30).
