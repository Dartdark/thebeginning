# Gold leveraged-fund reset input: NEEDS DATA

Source-only eligibility review,2026-10-26. This is an unregistered mechanism/input question, not H03,
a gross screen or a strategy result. New hypotheses/screens/evaluations:0/0/0. V2 remains3/60 counted
evaluations and2/10 hypotheses; H01/H02 stay closed. The archived t6 selection history is unchanged.

## Question and prior-family boundary

Could actual UGL/GLL fund assets and a verified gold-benchmark reset clock identify incremental
daily leverage-reset pressure in GC/MGC? Under the usual fixed-capital small-return approximation,
funds with leverage+2 and-2 generate modeled reset notional `r*(2*A_UGL+6*A_GLL)` in the direction of
the benchmark return r. This is a model of potential adjustment, not observed outstanding orders.
Creations/redemptions, swaps, anticipatory hedging and offsets can change the actual residual demand.
No fund assets, dollar-flow magnitude, contract weights, return or edge was measured here.

Current read-only ranking/source pin is Claude615485fca3160a4c48761f44b0d1972e7b623ef4. The scoped
TIER_LIST/MINED_INDEX and GC/LETF source review found no explicit UGL/GLL asset-weighted definition.
That is a bounded search result, not proof of universal novelty. Source `analysis/s_rank_gc_round1_test.py`,
lines426–440, already tests extensive GC settlement follow/fade rules into12:30CT and after settlement:
several price windows, thresholds, stops and shifts. A gold-clock/day-direction port is therefore prior
research. A genuinely admitted gold-fund asset input would be different information; a new name or
clock alone would not. The selected NQ asset-weighted LDF study also remains prior selection, with its
own failed design/limits, not a transferable exception for a new dataset.

## Public GitHub source inspected

Repository `opatel4/vix-etp-tracking`, immutable commit
`5401e0126249def156724f326e5531fb8cfc9204`:

| Source | Git blob SHA | What it establishes |
|---|---|---|
| [README.md](https://github.com/opatel4/vix-etp-tracking/blob/5401e0126249def156724f326e5531fb8cfc9204/README.md) |28a495bfa948c918c0c96f4be5fce548edd4cb44|Input price/NAV series are not redistributed; runnable stand-ins are synthetic|
| [data/README.md](https://github.com/opatel4/vix-etp-tracking/blob/5401e0126249def156724f326e5531fb8cfc9204/data/README.md) |3dd9e04b0b6c47bbdbf49984ff4304f8711917ad|Sponsor NAV endpoint instructions and `date,nav` schema; no actual fund-asset panel or receipt history|
| [src/prevalence_study.py](https://github.com/opatel4/vix-etp-tracking/blob/5401e0126249def156724f326e5531fb8cfc9204/src/prevalence_study.py) |1df5593d51611da4b068eccb653e33777b0f3101|Lists UGL/GLL as commodity+2/-2 and diagnoses sponsor NAV levels; this is secondary source code, not an issuer mandate/clock audit|
| [src/verify_restatement.py](https://github.com/opatel4/vix-etp-tracking/blob/5401e0126249def156724f326e5531fb8cfc9204/src/verify_restatement.py) |6a157666fea93330f2664843a29be2f26749d990|Normalizes sponsor files to `date,nav` and proposes a split-restatement diagnostic; no original vintages or historical posting times|

The recursive Git tree at that commit contains only README plus `.gitkeep` placeholders under input
directories: no archived UGL/GLL NAV/assets/holdings CSVs. Derived aggregate result tables were not
opened. No remote code, synthetic generator, issuer download or diagnostic was executed.

The documented endpoint is `accounts.profunds.com/etfdata/ByFund/<TICKER>-historical_nav.csv`.
That destination is outside the selected network policy; no request or policy bypass was attempted.
A documented URL is not an admitted historical input. The owned Claude `data/letf` tree at615485f has
only QID/QLD/SQQQ/TQQQ plus README, not UGL/GLL. No file data rows were opened.

## Distinguish the data hazards

The public repository concerns inconsistent split bases between NAV and market-price LEVELS.
Its scripts/readme do not establish that UGL/GLL total fund ASSETS were revised, nor that any specific
owned NQ AUM input is wrong. No such independent-review conclusion or notification is warranted.
Direct assets are split-invariant in principle; reconstructing assets from NAV and shares requires
matching contemporaneous units and split bases. Even internally consistent current history cannot
establish historical publication/receipt availability or rule out other revisions.

## Admission decision

**NEEDS DATA; no TEST and no preregistration.** Missing items are an authentic UGL/GLL asset/holdings
history with publication/vintage evidence, historical objectives and contract weights, and primary
benchmark/NAV reset versus actual hedge-execution clocks. COMEX settlement at12:30CT does not by
itself establish when these funds or counterparties must execute. Fund-close, NAV and futures-settlement
times must not be substituted for one another. Contemporary creations/redemptions remain unobserved.

The eight-question mechanism sheet `agents/codex/evidence/hunt_v2_gold_letf_reset.md` records these
conditions before any data. Only a later source-complete TEST could support a separately committed
at-most-five-configuration gross-first study. No NQ LDF publication-delay exception is borrowed.
Continue other v2 research; this source gate neither exhausts the universe nor pauses the program.
