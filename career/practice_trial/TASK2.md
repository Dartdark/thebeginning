# Practice 2: review a strategy submission (checklist only, no hints)

Same job as before: you're the reviewer. A contractor sent the note below and `cl_reversion.py`. The client trades on an
Apex account (intraday only, flat by 15:59 CT; 50K: $2,000 trailing drawdown, $1,000 daily loss limit).

Use the 7-question checklist (time travel, fills/costs, account rules, selection, out of sample, stats, data). For each
problem: where it is, which way it pushes the results (too good / too bad / unknown), and how bad it is (fatal / major /
minor). End with accept / revise / reject in 2-3 sentences. Take your time; plain English is fine.

---

## The submitted note: "Crude Oil Morning Reversion"

**Idea.** Crude oil overreacts in the first hour. When CL opens far from its recent average, it snaps back during the
morning.

**Market selection.** I ran the same rule on 10 futures (CL, NG, GC, SI, HG, ZC, ZS, ZW, 6E, 6J). CL, GC and 6E worked
best, so I focus on CL here.

**Rule (daily, CL).**
- z = (today's 08:00 CT open − average 08:00 open) / standard deviation of the 08:00 open.
- If z > 1.5, short at 08:00; if z < −1.5, buy at 08:00. Only if today's close confirms the reversion (for a short,
  close < open).
- Stop: 1% from entry. Exit at 11:00 CT.

**Cleaning.** I removed 14 trades with losses beyond 3 standard deviations as data errors.

**Results (1 MCL, 2018–2026).**
- 402 trades, 78% winners, +$46,900, profit factor 3.4.
- Never a losing year.
- Walk-forward: each year's threshold (1.0 / 1.5 / 2.0) chosen on that same year; every year profitable.
- Costs included ($2.50 per contract per round trip).

**Conclusion.** Trade 5 MCL on a 50K Apex account.
