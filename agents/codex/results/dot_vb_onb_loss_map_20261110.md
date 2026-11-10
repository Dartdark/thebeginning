# dot: VB/ONB terminal-loss map

Summary: The documented ONB losses show depleted cushion and a planned stop beyond the account floor.
The November 4 accounts were below reconstructed floors before later VB chart trades.
Those later chart rows are not established broker fills or causes of the terminal losses.
Account #1's final fill/floor path remains unresolved; no new protective strategy has been demonstrated.

Author/origin: **dot**. Prepared November 10, 2026 as a source-linked synthesis of existing evidence, not a new broker audit or return test.
Vault Break and Overnight Bias are the user's designs. The source forensics and existing Codex/Claude studies remain their authors' work.

## Evidence map
All dollar figures are USD. MNQ is $2 per point. Times below are Chicago as recorded in sources.
| Event | Remaining cushion | Nominal full-stop risk before costs | Established limit |
|---|---:|---:|---|
| October 30, account #3, 150K | $1,822.60 | 8 MNQ x $2 x 153.5 points = $2,456 | Documented liquidation gross loss $1,848 occurred before the strategy stop. |
| November 4, account #2, 50K | $931.34 | 3 MNQ x $2 x 177 points = $1,062 | First sampled below reconstructed floor at 09:50. Exact broker fills absent. |
| November 4, account #4, 150K | $1,939.60 | 7 MNQ x $2 x 177 points = $2,478 | First sampled below reconstructed floor at 09:50. Exact broker fills absent. |

November 4 exposure was the same directional event across 10 MNQ, but each account had its own cushion. It is not two independent experiments.
The observed equity samples are not tick-level worst excursions. The November 4 09:45 ONB chart marker conflicts with equity movement already visible by 09:35; chart timestamps cannot be assumed to be actual executions.
Later November 4 VB chart tickets followed the observed floor breaches and rejection alarms. They cannot establish that VB caused those failures.
The October 26 routing incident concentrated 28 MNQ on account #2; it does not by itself explain account #1's failure.

## The 89% distinction
The older simulation's 89% concerns failed starts where **any one of five components supplied over 70% of modeled failure-day loss**.
It is not a live-account statistic, a VB/ONB-only statistic, or a current forecast. The user's report of four recent failed accounts is a separate observation, not a long-run failure-rate estimate.
A source's historical account projection must retain its original sizing, costs, calendar and floor assumptions.

## Reproducible sources and unresolved work
- [Committed forensics](../inputs/eval_audit_20261104/loss_forensics.md) gives arithmetic, CSV extraction method, exact source lines and disagreements.
- [Pinned November 4 log](https://github.com/Dartdark/thebeginning/blob/13e29ca7b45daabeb0ed2d8c286448610f594dab/live/trades/20261104.csv).
- [Pinned October 30 incident](https://github.com/Dartdark/thebeginning/blob/13e29ca7b45daabeb0ed2d8c286448610f594dab/MULTICHARTS_PITFALLS.md).
- [Existing Codex tail review](vb_onb_tail_review_20261110.md) distinguishes existing management studies and later user scope correction.
- [Rejected split-stop study](vb_loss_split_20261110.md) is separate Codex work, not a dot test.

Final broker fills, official per-account floor history, commissions, liquidation and slippage remain missing. Account #1 cannot be fully reconstructed.
This map makes the risk mismatch visible; it does not prove that a cap, smaller size, different stop or replacement improves passes per fee without adding expirations.
No new hypothesis, return test, allocation, live code or program resume.
