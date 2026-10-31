# Context trim proposal (2026-10-28) — nothing changed yet, waiting for the user's yes

Every new chat starts with the opener "read NEW_CHAT_BRIEF.md, CLAUDE.md, TODO.md, LESSONS.md, MULTICHARTS_PITFALLS.md".
That is ~105 KB (~26k tokens) before any work, and the scheduled jobs pay part of it every day.

| File | Now | After | How |
|---|---|---|---|
| `CLAUDE.md` (loaded automatically) | 7.1 KB | ~5 KB | Move the Friday-review / monthly Monte Carlo / cross-review paragraph into a new `FRIDAY_REVIEW.md`; CLAUDE.md keeps one line pointing to it. |
| `NEW_CHAT_BRIEF.md` | 42.8 KB, 420 lines | ~10 KB | Rewrite the 'State' block to today (it still says 10/24). Move 'Latest (2026-10-17)', 'Live status (2026-10-14)' and 'Research state' (lines 117-407, mostly superseded) to `archive/brief_history_2026-10.md`. 'Who / what' stays, shortened. |
| `TODO.md` | 30.7 KB, 46 done + 29 open | ~12 KB | Move the 46 ticked items to `archive/TODO_done_2026-10.md`. Merge every 'when an account is funded' item (ES MOC, RS, Vault Break sizes, Swing Target, VIX step 3, funded files) into one 'When funded' section. Drop the 10/18 setup section (all done). |
| `LESSONS.md` | 6.0 KB | same | Short already; worth reading every time. |
| `MULTICHARTS_PITFALLS.md` | 18.8 KB | same | Keep the file, but drop it from the opener: CLAUDE.md already says to read it before writing MultiCharts code. |

Result: ~105 KB -> ~33 KB at the start of a chat (about 18k tokens saved per new chat, and the brief is current).

Nothing is deleted: everything moved stays in `archive/` and in git history.
New opener: *"Read NEW_CHAT_BRIEF.md, then CLAUDE.md, TODO.md and LESSONS.md in github.com/Dartdark/thebeginning (branch
claude/nq-trading-strategy-params-5h9d20) and continue from there."*
