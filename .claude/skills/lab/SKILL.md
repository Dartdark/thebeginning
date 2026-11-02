---
name: lab
description: Strategy lab run - take the next queued idea in lab/IDEAS.md, pre-register it, test it stage by stage (design 2018-22, placebo, one sealed holdout look, Apex benches, checker), stop at the first failed gate, log one ledger row and a lesson. Use when the scheduled "Strategy lab" task fires or the user says "lab" / "run the lab".
---

# Strategy lab run (one study)

Read `lab/README.md` first (rules, stages, gates). Also `CLAUDE.md` (testing standard), `LESSONS.md`, `lab/LESSONS.md`,
and `agents/codex/EXECUTION_REFERENCES.md` for any fill question. Work on `claude/nq-trading-strategy-params-5h9d20`.

1. **Gate the run.** `git pull`, then `python3 analysis/lab_tools.py can_run`. Anything but `OK`: stop (no message, no
   commit), except `EMPTY`: propose 3 new ideas (step 7) and stop.
2. **Take the idea.** `python3 analysis/lab_tools.py next` -> ID. Set its status in `lab/IDEAS.md` to `running`, commit +
   push at once (another run must not take it). If the idea needs data we don't have, set `blocked` with the reason, log a
   BLOCKED row, take the next one (counts toward the cap only if you started testing).
3. **Pre-register (stage 0).** `checks/candidates/lab_<ID>/PREREG.md`: mechanism, exact rule, <= 3 variants, entry/exit
   clock (CT), costs, pass bars from the README, the t bar from `python3 analysis/lab_tools.py bar`. Commit it BEFORE
   running any return. Never add variants after seeing results.
4. **Test.** One script `analysis/lab_<ID>.py` (match the repo's style: grid24 / scratch_data pickles, our costs, entries at
   the next bar's open, stops filled at the stop + 1 tick, Apex flat by 15:59 CT unless personal-only).
   - Stage 1 on 2018-22 only; stage 2 placebo (same exits, random entries/days, >= 200 draws) + by year on 2018-22.
   - Stage 3 only if 1 and 2 pass: run 2023-onward once (`looks: 1`). Full-sample t vs the bar.
   - Stage 4 only if 3 passes: Apex benches (copy the pattern of `analysis/swing_target_bench.py`: evaluations + bootstrapped
     funded, add AND replace) or, if not Apex-legal, `analysis/personal_ladder.py`-style personal bench.
   - Stage 5 only if 4 passes: put trades in `checks/candidates/lab_<ID>/` and run the strategy-checker agent.
   Report Sharpe, Sortino, PF, Calmar, Ulcer (analysis/metrics.py) for the best variant, longs and shorts separately.
   Keep a run inside ~60 minutes: if a stage can't finish, log `ERROR` with what's missing and leave the idea `queued`.
5. **Record.** `python3 analysis/lab_tools.py log '<json>'` (id, title, market, stage reached, verdict, gate, t_design,
   t_holdout, looks, tier, lesson, follow_ups) **plus the receipt** (enforced): `verified` (what was actually run and
   checked), `not_verified` (what was NOT run: e.g. holdout, benches, checker, MultiCharts), `risks`. An ERROR row also
   needs `error_class`: missing_data / too_few_events (never retried), code_error / timeout (retried once; fix something
   first), other. Two ERROR rows hold the idea for the user. Set the idea `done` with a `result:` line. One line in `lab/LESSONS.md`.
   Rank it in `TIER_LIST.md` (stage 1-2 fail: F/D; 3: D/C; 4: C or the capital-expansion bench; 5 PASS: B candidate).
   Any fill / market-behavior finding -> `agents/codex/EXECUTION_REFERENCES.md` (next E number).
6. **Follow-ups.** After a FAIL, at most 2 new ideas with their own mechanism (not parameter tweaks), depth <= 2
   (`parent:`), appended to the END of `lab/IDEAS.md`.
7. **Refill.** If fewer than 3 ideas are queued, add up to 3 from: `papers/SCOUT_LOG.md` leads, `WATCHLIST.md` items due,
   `lab/LESSONS.md`, Codex's results on `codex/work` (read only). Prefer non-NQ / scheduled-flow mechanisms (the books
   are 92-96% NQ risk). Every new idea needs a `- tier_check:` line right under its heading, written after
   `python3 analysis/lab_tools.py dupcheck '<2-3 key words>'` (words used + result), and a `- who_pays:` line: one of
   risk premium / behavioral / structural / information, then who pays and why they keep paying. Without both lines `next`
   skips the idea. If you can't name who pays, it's noise: don't queue it.
   Never queue an idea `TIER_LIST.md` already ranked C/D/F for the same market and mechanism.
8. **Commit + push** to `claude/nq-trading-strategy-params-5h9d20`, `claude/quirky-noether-4dla64` and your designated
   branch (pull first). No model IDs in commits.
9. **Report.** Only a stage-4+ result or a stage-5 PASS is news: send the master session
   (`session_01Wk1fPYssjbaEfe21f4v6vD`) one short message (send_message) and `python3 analysis/send_alert.py "LAB: ..."`.
   Failures at stages 1-3 are silent (ledger only).

Never: change a plan, a chart, `live/`, the VPS or the trading settings; open a holdout before stages 1-2 pass; test more
than 3 variants; run when `lab/STOP` exists or the cap is reached; push to `codex/work`.
