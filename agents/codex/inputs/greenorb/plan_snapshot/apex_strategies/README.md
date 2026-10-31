# Apex strategies (challenge only)

These strategies were built for one job: **passing the Apex 50K challenge** ($3,000
target before a $2,000 trailing drawdown, $1,000 daily loss limit). They are tuned for
pass rate and speed to a funded account, **not for making money**. Do not judge them on
profit, and do not treat them as the funded-phase strategies; those live in
`../funded_strategies/`.

## The challenge plan

One Apex 50K account at a time. Both strategies on MNQ, each in its own chart window
(CME 24-hour session, Exchange time zone):

| Strategy | File | Chart | Challenge inputs |
|---|---|---|---|
| Vault Break | `NQ_Vault_Break.txt` | 30 min | `NumContracts` 8 |
| Overnight Bias | `NQ_Overnight_Bias.txt` | 15 min | `RiskPerTrade` 1100, `NumContracts` 1, `ExitTime` 1430, `EarlyExitTime` 1130 |

Pass rate 44% (43–45% across periods), typically 12 trading days and about $117 per
funded account. With 1 tick of slippage on every fill: 42.8%. Full rules, backtests and
reasoning: `TWO_STRATEGY_PLAN.md`.

## Files

| File | What it is |
|---|---|
| `NQ_Vault_Break.txt` | Vault Break signal |
| `NQ_Overnight_Bias.txt` | Overnight Bias signal (`RiskPerTrade` sizing) |
| `NQ_Strategy_ATR.txt` | Indicator: 15-day ATR, its 30%, Overnight Bias's MNQ size |
| `NQ_ONB_ADX.txt` | Indicator: Overnight Bias's ADX(14) with the 20 line |
| `NQ_Vault_Break_VIX.txt` | Vault Break with VIX-regime sizing (needs daily VIX as data2; parked, the feed has no VIX) |
| `TWO_STRATEGY_PLAN.md` | The challenge plan: rules, results, why they work |
| `VIX_REGIME.md` | VIX regime test on Vault Break |

Analysis code for these is in `../analysis/` (`multi_strategy24.py`, `portfolio.py`,
`vix_regime.py`).

## Raw links (to paste into MultiCharts)

- https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Vault_Break.txt
- https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Overnight_Bias.txt

## NQ_Vault_Break_SP.txt (2026-10-15)

Vault Break plus the single-print day filter: `FlaggedContracts` contracts (instead of `NumContracts`) on the session after an
interior 30-minute TPO single print in the 8:30-15:00 CT session. -1 = off (identical to `NQ_Vault_Break.txt`). Funded candidate:
3 / 1. Prints each session's flag to the Output window (`ShowFlag`). Evidence: `TIER_LIST.md` (B), `analysis/single_print_test.py`.
