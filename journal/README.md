# Trading journal (Obsidian vault)

Your notes, in plain Markdown, read by Claude when you push them. Set up 2026-10-17.

## Folders
| Folder | What goes there | Who writes |
|---|---|---|
| `journal/daily/` | one note per trading day, `YYYY-MM-DD.md` (made from the Daily template) | you |
| `journal/ideas/` | strategy ideas, one note each (Idea template) | you; Claude only updates the `Status:` line |
| `journal/templates/` | the Daily and Idea templates | Claude |
| `live/` | weekly MultiCharts reports `<KEY>_live.xlsx` (see `live/README.md`) | you |

Everything else in the repo is Claude's. Read it in Obsidian, but don't edit it there; ask Claude instead (if both of us
change one file, git has a conflict).

## One-time setup (PC)
1. **A separate copy of the repo for the vault** (not the Antigravity folder). In PowerShell:
   `git clone -b claude/nq-trading-strategy-params-5h9d20 https://github.com/Dartdark/thebeginning C:\TradingVault`
2. Install Obsidian (obsidian.md, free) → **Open folder as vault** → `C:\TradingVault`.
3. Settings → **Core plugins**: turn on **Daily notes** and **Templates**.
4. Settings → **Daily notes**: Date format `YYYY-MM-DD`; New file location `journal/daily`; Template file location
   `journal/templates/Daily`.
5. Settings → **Templates**: Template folder location `journal/templates`.
6. Settings → **Files and links**: Default location for new notes → `journal/ideas`.

## Every trading day (2 minutes)
1. Click the **calendar icon** (Open today's daily note) on the left bar. The template fills in.
2. Fill in balances, what traded, and any problem, especially the **exact text of error messages**.

## To send it to Claude (end of day, or Fridays with the weekly reports)
1. Close nothing; just open PowerShell in `C:\TradingVault` and run:
   `powershell -ExecutionPolicy Bypass -File journal\sync.ps1`
   It commits only `journal\` and `live\`, brings down Claude's latest files, and pushes.
2. Tell Claude: **"read my journal"** (or "read my journal and the live reports" on Fridays).

## What Claude does with it
- Compares your notes with the backtest trades of the same days (missed, extra or different fills), and
  `live/` reports with `analysis/live_vs_backtest.py`.
- Turns every problem into a fix or a `MULTICHARTS_PITFALLS.md` entry, and ticks `TODO.md`.
- Tests ideas in `journal/ideas/` and writes the grade on the note's `Status:` line (and in `TIER_LIST.md`).
- Keeps the running live tally for the mid-December gate (40-70 live trades at ≥ 75% of backtest).

Privacy: the repo is on GitHub. Never write passwords, API keys, account numbers or logins in the journal.
