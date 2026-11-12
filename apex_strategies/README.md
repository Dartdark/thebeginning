# Apex strategies (challenge only)

These strategies were built for one job: **passing the Apex 50K challenge** ($3,000
target before a $2,000 trailing drawdown, $1,000 daily loss limit). They are tuned for
pass rate and speed to a funded account, **not for making money**. Do not judge them on
profit, and do not treat them as the funded-phase strategies; those live in
`../funded_strategies/`.

## The evaluation plan NOW (150K No-Activation, account #5; updated 2026-11-12)

Source of truth: `../live/expected_setup.json` (the 16:40 job checks every chart against it) and `analysis/bench150.py`
`LIVE_EVAL` (the base every new candidate is benched against). Change all three in the same commit.

| Chart tag | Strategy (file) | Chart | Size |
|---|---|---|---|
| ONB150-5 | Overnight Bias ADX30 (`NQ_Overnight_Bias_ADX30.txt`) | 15 min MNQ | `RiskPerTrade` 3500 (max 25; was 2750 until 11/12) |
| ~~EOS150-5~~ | Expiration Open Short | | DROPPED 2026-11-12 (user: no proven help, mon_eos_contrib) |
| MON_BR150-5 | Bridge Monday Long | 5 min MNQ | 5 |
| TW150-5 | Twin Continuation (`Twin_Continuation_150K.txt`) | MNQ | 2 |
| DT150-5 | Dual Thrust v4 (`../funded_strategies/NQ_Dual_Thrust.txt`) | 1 min MNQ | 2 |
| JF150-5 | NQ Jump Fade v4 (`NQ_Jump_Fade.txt`, `MinVolRatio` 0) | 1 min MNQ, 24h | 1 (added 11/12 at 2; 1 from 11/12 evening while #5's cushion < ~$4,000) |
| NBL150-5 | NQ Noise Longs (`NQ_Noise_Longs.txt`, longs only) | 15 min MNQ, 24h | `ContractsPerTrade` 3 (added 11/12) |
| LDF150-5 | Late-Day Flow (`../funded_strategies/NQ_Late_Day_Flow.txt`) | 5 min MNQ, 24h, Bar Magnifier 1 min | `RiskPerTrade` 1000, `NumContracts` 1 (added 11/12) |
| (each chart) | Apex Chart Guard (`Apex_Chart_Guard.txt`) | | helper |

Vault Break: OUT of the evaluation since 2026-11-11 (DLL hit twice). Older 50K material below is history.

## The old 50K challenge plan (history)

One Apex 50K account at a time. Both strategies on MNQ, each in its own chart window
(CME 24-hour session, Exchange time zone):

| Strategy | File | Chart | Challenge inputs |
|---|---|---|---|
| Vault Break | `NQ_Vault_Break.txt` | 30 min | `NumContracts` 8 |
| Overnight Bias | `NQ_Overnight_Bias.txt` | 15 min | `RiskPerTrade` 1100, `NumContracts` 1, `ExitTime` 1430, `EarlyExitTime` 1130 |

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
