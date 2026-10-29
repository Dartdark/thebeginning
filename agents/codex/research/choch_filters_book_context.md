# Hourly two-candle CHoCH filters: adopted book and bench context

Read-only preparation, 2026-10-29. No price rows, return rows, account pickles or financial outputs were opened or calculated. CSV headers, opaque-byte hashes, source code, documentation and existing limitation records only. No new trial, backtest, branch change or shared/live-file write. This note is not a candidate or a placement result.

## Current authority and identity

Connected GitHub reads found `codex/work` at `1db9e8482405ef99a943f02bdb0fc50f1b815de0` and the read-only Claude source branch at `b6b20a3e7bc95ea665287cab2ac46447207b9aaf`. Relevant source Git blobs:

| Path on Claude branch | Blob |
|---|---|
| `NEW_CHAT_BRIEF.md` | `d93a8d2e3c7ffd8b3f923ca0d7d40815f76d6cd6` |
| `TIER_LIST.md` | `f7b592ecc7d60b6492a86c55b58a3de7289ff935` |
| `personal_strategies/PORTFOLIO.md` | `d175bfe07f183f05c05c3d56c88eb384c85821ee` |
| `analysis/personal_portfolio.py` | `80d90aca24b413957ea32721334bf08191d8f162` |
| `analysis/personal_variants.py` | `32a6d57deffc17dbef03c95acdde558834cd8aa2` |
| `funded_strategies/FUNDED_PLAN.md` | `895060c72d681629cea450e72d993ec3eb4f67ba` |
| `analysis/t_oneside_bench2.py` | `51e2aa26e44e84b205d890016e96e058ca6b4c88` |
| `analysis/swing_target_bench.py` | `882fa86a497ca84f2ddad3555deb042bb8ae8817` |

The personal portfolio documentation and both source files are byte-identical by Git blob hash to the retained `agents/codex/inputs/rebound/plan_update_afde088/` snapshot. Thus the existing retained personal19 baseline still matches the *adopted definition*, subject to its existing implementation limits. Current means 19 pieces at one micro each, including SwingTarget v3 and PaperTrend v2, with BB_MRM removed. The prospective aggressive version is not current.

Personal19 columns: VaultBreak, OvernightBiasML, MondayLong, ExpirationOpenShort, LateDayFlow, NFPFade, BridgeMondayLong, CLSundayFade_perMCL, ESMOCFollow_perMES, RelativeStrength, FC2B, TwinContinuation, OvernightTick, DualThrust, Kusho, S47, S30, SwingTarget, PaperTrend. S30 is a published combined MNQ/MES sleeve; preserve that convention rather than treating it as a second new candidate weight.

## Immediate feasible bench after a design pass

Use the existing current19 baseline:
`analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv`.
Its 19-column header was checked and its SHA256 is `d724c7d02b6db71e63ba705079dbea7fefaa42c6b4f436308a28993ca1908803`; the SUNDAY2 copy has the identical hash. No numeric CSV field was parsed here.

The safe design reader in `analysis/codex_hunt_v2_highwin_bench.py:date_first_rows/read_baseline` discards every non-2018--22 row by date string before float conversion. Its generic paired calculations and `codex_anson_personal.histories/simulate_daily` are reusable; do not call its candidate-specific reader, exact216-event checks, authorization marker or Twin replacement configuration for CHoCH.

For each design survivor, freeze the following new mappings at whole size 1 MNQ before book returns: BASE=sum of adopted19; ADD=BASE+CHoCH; EMPTY=BASE-SwingTarget; REPLACE=EMPTY+CHoCH. The overlapping replacement is SwingTarget, as requested by the parent experiment; do not search for a more favorable replacement. Use identical dates, fees and paired 252-day histories, with the declared 20-day blocks and fixed seed across all comparisons. Report BASE and EMPTY comparisons, by-year daily-book metrics, median annual profit / median maximum drawdown, DD95, paired effects, and aligned loss-day/correlation context versus VB/DT/RS/SwingTarget. Daily metrics cannot be used as candidate trade-t promotion statistics.

Candidate daily cash flows must reconcile completely to the hourly ledger. Do not silently delete candidate dates absent from the personal calendar, invent BASE zeros on absent dates, rebook unknowns, or let a post-design record enter selection. Explicitly retain the pre-existing design/validation and filter multiplicity history. This preparation does not loosen any design gate.

The reused book is a *conditional published-book comparison*. Core native-fee corrections count nonzero daily activity, undercharging some reentries; MOC/S30 have inherited fee/mark approximations; Twin is marked v1 rather than an exact v2.1 ledger; Kusho is exit-booked. An exact numeric fee/reentry/mark uncertainty bound has not been established. Native candidate costs can be exact while the inherited BASE remains conditional. The retained OvernightTick evidence ends 2026-07-07: later zeros are missing evidence, not verified no-trades. Design-only comparisons avoid that later cutoff but do not cure other limitations.

## Current funded/evaluation definitions and limits

Do not use `funded_bootstrap.PLAN` or its old VB_N3 constructor as adopted authority. Current source overlays are:

- **50K funded:** VB normal/flagged1/1, SwingTarget1, ONB ML risk400, OvernightTick1 replacing MondayLong, EOS risk700, LDF2, NFP risk500, BridgeMonday1, CL Sunday2MCL, ES MOC2MES, and **T_ONESIDE fade1 replacing RS longs since2026-10-28**. The current source table calls it ten strategies while listing eleven active line items; use explicit leg definitions rather than that headline count. VCS is dropped. Full cushion sizing uses f=clip(cushion/1500,.5,1), whole contracts floor after scaling; 1-lot pieces are off below full size.
- **150K funded:** source core plan scaling/cushion rules, RS both1, OvernightTick2 and SwingTarget2 replacing DualThrust2; MondayLong remains. DT stays personal. Use exact source integer flooring after cushion scaling and the3000 reference; do not silently round the pre-scaled1.5 bases into a new book. The source `t_oneside_bench2.plans150` routes through `swing_target_bench.plans150()['DT 2 -> ST 2']`.
- **50K evaluation:** VB8, plain ONB ADX30 risk1100, EOS risk500, BridgeMonday2. ST/DT/RS/OT/T are not adopted evaluation legs. ST replacement therefore is inapplicable for evaluation: ADD and BASE can be described, but do not invent a ST EMPTY or replacement allocation.
- **150K evaluation:** VB20, ONB risk2750, EOS risk1250, BridgeMonday5, with its own9000 target/4000 trail/2000 daily-loss rules and horizon. Floor risk-sized contracts from that account's own dollar risk, not50K floored quantities times2.5. Shared50K `combine_levers_test.challenge` constants cannot be reused unchanged as150K.

Funded shared engines require synchronized adverse/closed paths for all adopted legs (`funded_lab.Lab.W/C`, then paired `funded_bootstrap.Boot` and the account-size simulator); evaluations likewise need joint chronological paths. The hourly candidate's daily P&L and its valid intraday path alone cannot repair missing BASE paths. Existing source records document BridgeMonday omitting Sunday19:00--midnight adverse exposure; CLS/OT constant whole-day adverse proxies inventing simultaneous exposure; inherited MOC close-based paths; incomplete native per-trade fees. The relevant ready lab caches (`scratch_data/g24.pkl`, `ge.pkl`, `lab.pkl` and `agents/codex/runtime/or_pullback_current_lab.pkl`) are absent. This is preparation/reconstruction work, not evidence that raw data is inaccessible.

Consequently funded50K/funded150K/evaluation50K/evaluation150K must remain **not established** unless exact current joint paths and integer sizing are reconstructed and audited. No pass/payout benefit can be inferred from daily MC, saved old proxies or a favorable candidate t. The immediate design bench that is feasible with existing inputs is the conditional personal19 route above. No user action is required by this source review alone.
