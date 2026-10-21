# Test 01: should this filter go into Vault Break?

Work on branch `codex/tests` only. Don't fetch or read other branches. Don't search the web for this strategy.
Follow `agents/codex/BUILDER_BRIEF.md` (plan file first, then test).

## The claim (from another research agent)

Vault Break is a live strategy (`apex_strategies/NQ_Vault_Break.txt`, Python rebuild `analysis/candidates24.vault_break24`).
It buys NQ when a 30-minute close is above the midnight open + 0.30 x 15-day ATR and above the midnight-anchored VWAP.
Decisions from 10:00 CT, target +40 points, stop -75 points, flat at 14:30 CT, max 3 trades a day.

The agent proposes adding two filters together ("Combined"):
1. **Runway cutoff:** only decision bars closing 10:00-12:30 CT. Reason given: later entries have too little time
   before the 14:30 flatten.
2. **VWAP stretch guard:** only enter when (decision close − midnight VWAP) <= 0.50 x 15-day daily ATR. Reason given:
   stretched entries buy a "climax" and get stopped on a VWAP retest.

Its reported results (2018-2026, 1 NQ, $17.25 commission + 1 tick per fill):

| Variant | Trades | Net $ | $ / trade | Max DD $ | t |
|---|---|---|---|---|---|
| Base | 1,744 | 143,396 | 82.22 | 17,204 | 3.83 |
| Combined | 1,307 | 136,764 | 104.64 | 12,609 | 4.09 |

It says: design 2018-22 passed (t 3.16) and holdout 2023+ passed (t 2.68). Max drawdown is cut by 26.7%. On 2 MNQ the
worst historical drawdown would be $1,260.90, "well below the $2,000 trailing limit". It was chosen after testing
each filter alone first.

## Your task

Decide whether the live Vault Break should adopt "Combined". Test it yourself with the repo's tools and our costs.
Check every claim above, and say which hold and which don't. Recommend ADOPT / REJECT / WATCH, with the evidence.

Output: `agents/codex/results/TEST_01.md` (brief's format), script `analysis/codex_test01.py`, output
`analysis/outputs/codex_test01_output.txt`. Commit and push to `codex/tests`.
