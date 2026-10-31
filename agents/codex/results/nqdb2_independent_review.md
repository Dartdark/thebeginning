# NQDB2 independent account/source review: WITH CONCERNS; scoring blocked

Summary: The reviewed adapter's fee/unit arithmetic and fill-phase handling pass source inspection.
Source/data validation remains WITH CONCERNS: two trades cross unexplained missing intraday minutes.
The account gate stopped before simulation; zero new account simulations or paired portfolio results exist.
Current rosters match the canonical specification; an earlier funded-reference mismatch remains unresolved.
This review supplies no account-gain, adoption or live-execution conclusion.

## Scope and provenance

Read-only review of the frozen test plan (`eb7b8b07`), existing outputs and source; no replay,
bootstrap, account simulation, cache rebuild or parameter selection was performed by this reviewer.
The accounts agent owns implementation and raw-export inspection. Source snapshots reviewed:

| Repository path | SHA256 |
|---|---|
| `analysis/codex_nqdb2_accounts.py` | `f18b5463739fc46ec4de20c52235dd83bccdaf0012d0d2ebbe6b5c3306a4c77d` |
| `analysis/codex_or_pullback_plan.py` | `4584ef1f9f6cffabcc3f8644c1794297590fea009c5ec92a7ca3a36ca5cfdec2` |
| `analysis/codex_ob_v2_accounts.py` | `3a44d30a96c63a2058ad847e4ebb4fa91d28318f7dd8a0f39b11ce366baa9878` |
| `analysis/codex_nqdb2_replay.py` | `965c137ffad088e7b989af88cc0cc3b54664347179fd2f0e4f5422c285158771` |

Pinned dependency manifest: `agents/codex/runtime/nqdb2_plan_analysis/manifest.json`, SHA256
`0a4189117d0139d937a5adfaf598dc68be6940e33cd5da1db2d2000249fccd9f`.
Its context artifact records unchanged blobs from `a67035be4189b493098c80f1def979348520fd5d`
to `e34d71cd3537a9f019d2521e280fc92f3ffdb4c6`. Canonical `analysis/real_fee_bench.py`
was read through GitHub at the former commit: Git blob `c5d29a7171bf5eceb6724e88d06e44c9294d5aca`.

## Arithmetic and execution inspection: PASS within this scope

`audit_ledger` enforces already-slipped prices, `slips=0`, one-NQ geometry and
`net=(exit-entry)*side*20-7.25`. `candidate_paths` converts prices directly to one MNQ
at $2/point and subtracts only the actual $1.04/$1.24 fee. It does not charge the ledger's
$0.725 scaled commission or slippage again. Entry slippage appears in held marks;
exit slippage appears at execution. Open exits exclude the exit minute's later range;
intrabar stops terminate at their executable fill; other held exit minutes retain adverse marks.
This establishes coherent accounting logic, not complete historical path verification.

## Data and comparison limits

Existing `accounts/candidate_full_audit.json` retains all 1,534 A1 trades and reports zero
carry, timing and raw-fill violations, but two unknown account dates. The accounts agent's
`accounts/candidate_raw_gap_evidence.json` confirms absence in both day and overnight CSVs:
2018-07-26 13:43–13:44 CT and 2025-06-02 11:03 CT. Its SHA256 is
`22e85eefaeaea35a12332743a75fd5b476afdaa30d8ea98ad5d7a30f82ad79c4`.
The separate 222 recurring 15:16–15:30 halt-pattern trades must not be presented as 222
additional unexplained data gaps. Missing intraday excursions leave stop/target and account
breach ordering unknown. The gate correctly blocks scoring without imputation or trade deletion.
Total-volume Python-proxy parity also does not establish MultiCharts up-volume parity.

The funded roster includes MOC 2 MES and RS longs 1 MNQ; evaluation is VB8 / ONB ADX30
risk$1,100 / EOS risk$500 / Bridge2. The earlier ORPullback
`analysis/outputs/codex_or_pullback_portfolio/baseline_reference.json` (Git blob
`7ea9abc6ed6962c2c338ec48729de820ab4d9f5b3`) reports $9,193.50/$11,976 versus published
$9,180/$11,982: differences +$13.50/−$6 exceed display rounding. Both use seeds1–4×250,
block20/H500; different random seeds are not an established explanation. Original cache/pool
provenance is insufficient to identify the cause. Accelerator parity against supplied paths
does not resolve canonical baseline parity. Any future account comparison requires both on
identical data, metadata and saved histories first.

Final-source reinspection confirms primary paired intervals use the preregistered 90% level,
with separately labeled secondary 95% intervals for funded and evaluation comparisons.
This coverage-label correction preceded any account simulation; it is resolved.
Audit-only and existing-VB reporting modes return before the gated account branch.
No new interval was computed here.
