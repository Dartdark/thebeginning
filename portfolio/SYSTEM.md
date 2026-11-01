# The research system

A loop that runs on a schedule and tests one idea per run, built to make honest results the easy path.

```
paper scout ──> idea queue ──> pre-registration ──> staged gates ──> ledger + lessons
 (5x a day)     who pays?       rule, ≤3 variants,   stop at the        every study counted,
                duplicate       pass bars, costs,    first failed gate   failures feed the queue
                check           written BEFORE data
```

**Gates (an idea stops at the first one it fails):**

| Stage | Test | Pass bar |
|---|---|---|
| 1 | Effect on the design period (2018–22), realistic costs | t ≥ 2, profit factor ≥ 1.15, enough trades |
| 2 | Random-entry / random-day placebo with the same exits; year by year | beats placebo (p < 0.05), ≥ 4 of 5 years positive |
| 3 | One counted look at 2023-onward data | same sign, t ≥ 1.5; full sample vs the multiple-testing bar |
| 4 | Account-level simulation under the prop firm's drawdown rules (add to and replace existing strategies) | improves pass rate, blow-up rate or payout timing |
| 5 | Independent rebuild from the written spec alone, compared trade by trade | matches |

**Rules enforced in code, not left to memory:**
- every study counts as a trial: the significance bar rises with the number of ideas tested (Bonferroni; t ≥ 3.63 at
  ~360 trials);
- holdout looks are budgeted (40 a quarter) and only allowed after stages 1–2 pass;
- an idea needs a "who pays" line and a recorded duplicate search before it can run;
- every ledger row carries a receipt: what was verified, what was not, the risks;
- failures are classified: missing data or too few events is never retried, a code error once, and two errors stop the idea;
- a kill switch and a daily cap.

**Independent review:** a second agent reviews the week's code and results and tries to break them; a separate code
reviewer checks new code against planted-error fixtures. Results go to a S–F ranked list kept across all research.

Outcome so far: of the first 13 studies, none passed stage 1. That's expected, and it's the point: the loop kills dead
ideas cheaply, before they cost money.
