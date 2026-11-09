# Ingredient studies: Claude vs Codex, independent cross-check (2026-11-09; Dot's review item 3)

Where Claude and Codex both took a strategy apart on 2026-11-08, from separate rebuilds and separate pre-registrations, the conclusions
agree. This is the independent verification Dot asked for; the listed rows are the overlap, not every Codex case.

| Strategy | Claude (analysis/ingredient_ablation*.py) | Codex (agents/codex/results/ingredients_*_20261108.md) | Agree? |
|---|---|---|---|
| Base rebuilds | EOS 106 trades $501, NFP 78 $343, CL Sunday 96 $653 | EOS 105 $474, NFP 77 $353, CL 96 $653 | yes (within 1-2 trades) |
| Dual Thrust | range threshold is the engine (k 0: $74 vs $139) | range threshold improves total profit in both periods | yes |
| Relative Strength | the ES adjustment is the engine (own momentum $189 vs $306) | ES adjustment improves total profit in both periods | yes |
| Late-Day Flow | exit 14:30 vital (15:00: $72, 2023+ t 0.5) | 14:30 exit: $47.0k vs $16.4k at 15:00 since 2023 | yes |
| EOS / NFP / CL | direction is the engine everywhere; CL holds to Monday 09:00 (07:00 $415, 23:59 $146) | direction the clearest common contribution; CL's later morning hold adds profit in both eras | yes |
| CL stop | no stop $725 but a -$16.6k open loss (2026-03-08) | removing the stop hides a ~$16,007 intratrade loss | yes |
| Monday Long | needs the whole session (out 12:00: $282 vs $436) | benefits from the later hold | yes |
| S30 IBS | entry gate's value since 2023 is risk, not money (any-session entry $218k vs lead $185k, but DD $88.5k vs $45.3k) | entry advantage changes by era; marked DD $59.5k vs $37.7k booked | yes; Codex's marking caught Claude's booked-DD figure (fixed) |
| Anson / R2Vault / S03 | from Codex's ledgers: Anson settings and longs, R2 window, S03 v2 stop factor and longs | strength gate + direction (Anson), R2 gate (R2), entry band + stop as protection (S03) | yes |

Not cross-checked by both: FC 2B / ONB / T_ONESIDE, S47, Kusho, Bridge Monday, ES MOC (Codex only); Twin, Overnight Tick, noise-area,
Vault Break, PAPERTREND, Swing Target, FVB, Ricochet, RollZone, DriftPullBack (Claude only). Codex's ES MOC finding (2023+ $99 per ES,
t 1.2) is a watch item for the funded plan.
