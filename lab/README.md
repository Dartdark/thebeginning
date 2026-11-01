# The Lab (autonomous research loop, user 2026-10-31)

One scheduled run = one study. 5 runs a day (scheduled task "Strategy lab", fresh session each time, skill
`.claude/skills/lab/SKILL.md`). Each run takes the top `queued` idea in `lab/IDEAS.md`, walks it through the stages below,
stops at the first failed gate, writes one ledger row (`lab/ledger.json`) and, on a failure, a lesson that can seed
follow-up ideas. **Nothing the lab finds goes into a plan, a chart or the VPS without the user's yes.**

- **Kill switch:** if `lab/STOP` exists, the run does nothing (create it to pause, delete it to resume).
- **Daily cap:** 5 studies per Chicago calendar day (`python3 analysis/lab_tools.py can_run` checks both).
- **Sealed looks:** every opening of a holdout (2023-onward data) is counted in the ledger (`looks`). The lab may open a
  holdout only for an idea that passed stages 1-2 on 2018-22. Budget: 40 looks per quarter; past it, ideas wait for the user.
- **Multiple testing:** every study is a trial. A lab idea needs t >= `metrics.t_threshold(N)` with N = ranked items in
  TIER_LIST + lab studies so far (`lab_tools.bar()`), unless pre-registered from a stated economic mechanism with <= 3
  variants (then t >= 2.0 and clean placebo). Each idea may test at most 3 variants, fixed before any return is seen.
- **Rules in code (2026-11-01):** `lab_tools.py` refuses ideas with no `- tier_check:` line or no `- who_pays:` line (risk premium / behavioral / structural /
  information + who and why; 'no one I can name' = noise, not queued), rows with no receipt
  (verified / not_verified / risks), ERROR rows with no `error_class`; non-retryable errors and a second error hold the idea
  for the user (shown as 'needs_user' in the panel data).
- **Follow-ups:** a failed idea may spawn at most 2 follow-up ideas, depth <= 2 (no fishing chains), each with its own
  mechanism; follow-ups go to the END of the queue.

## Stages (gate to pass each)
| Stage | What | Gate |
|---|---|---|
| 0 Pre-register | `checks/candidates/lab_<ID>/PREREG.md`: mechanism, exact rule, <= 3 variants, costs, pass bars, written BEFORE any return | file exists, committed |
| 1 Effect (design 2018-22) | Our costs ($7.25 NQ / $5 ES / CL, GC, ZN, 6E $5 + 1 tick per market/stop fill) | best variant t >= 2.0, PF >= 1.15, >= 80 trades (>= 40 for event studies) |
| 2 Controls (design) | Random-entry / random-day placebo with the same exits; by year | beats placebo (p < 0.05) and >= 4 of 5 years positive |
| 3 Holdout (one sealed look) | Same rule on 2023-onward | same sign, t >= 1.5, PF >= 1.1; full-sample t vs the bar |
| 4 Benches | Apex-legal: 50K/150K evaluation + funded bootstrapped bench, add AND replace; else the personal ladder bench | beats the plan (or capital-expansion bench) |
| 5 Checker | `checks/candidates/lab_<ID>/` + strategy-checker agent | PASS -> tier B candidate, message the master for the user |

A pass at stage 5 is still only a candidate: the user decides; MultiCharts check and forward log follow as usual
(`DEVELOPMENT_PROCESS.md`). Every finished study is ranked in `TIER_LIST.md` (failed at 1-2: F/D; at 3: D/C; at 4: C or bench).

## Files
- `lab/IDEAS.md` queue (status: queued / running / done / blocked), `lab/ledger.json` one row per study,
  `lab/LESSONS.md` what each failure taught, `analysis/lab_tools.py` (can_run, next, log, bar, summary),
  `analysis/outputs/dashboard/lab.json` (Lab panel on the Apex Live Desk).
