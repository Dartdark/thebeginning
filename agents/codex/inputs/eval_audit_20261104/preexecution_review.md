# Independent evaluation-pipeline pre-execution review — 2026-11-04

Summary: **PASS for bounded conditional research readiness**, subject to committing these exact reviewed artifacts before outcomes.
The finite policy menu, design-only nomination, committed derived registry and explicit target-guard separation pass the reviewed code checks.
Synthetic policy/selection/orchestration checks pass; no owned market outcomes were calculated by this reviewer.
The broad menu is bounded allocation research, not proof of optimality or broker execution parity.

Reviewer: `eval_loss_forensics`, independent of the registry, selector, orchestrator and account-engine implementers. This review does not re-approve the reviewer's own forensic/calendar notes. No implementation owned by another agent was edited.

## Scope and current gate

Read-only code review covers `analysis/codex_eval_policies_20261104.py`, `analysis/codex_eval_selection_20261104.py`, and `analysis/codex_eval_run_20261104.py`, with bounded interface inspection of the account engine, path builder and source adapter. No `prepare`, `screen`, `select`, `validate` or historical market command was called.

The final reviewed implementation/configuration hashes are recorded below and in `preexecution_review_receipt.json`. An earlier hash is not an approval of later code. A committed preregistration and frozen budget/input evidence remain prerequisites to any market calculation. No code edits or further optional stages are requested by this review.

## Checks that pass in the reviewed implementation

1. **Finite and counted allocation menu.** Pure generation yields **2,485** unique account/book/governor definitions: **1,242 for 50K** and **1,243 for 150K**. Empty and reference controls remain counted. Six synthetic registered parent nominees generate at most **30** additional definitions, bringing the maximum observed menu to **2,515**, below the registered hard cap of 3,000. Definitions are deduplicated by account, canonical book and governor. This is an audit-specific allocation budget; earlier scout selection history is not deleted or relabeled.

2. **Current target guard is not assumed installed.** Both CURRENT definitions explicitly carry `target_guard=False`. The runner uses `dataclasses.replace` to override the engine's default on every case. The four initial target-guard counterfactuals have separate labels/families and IDs. Derived target guards are separately registered and counted. Installed guard state remains unverified; these counterfactuals must not be described as the current live baseline.

3. **Design chronology.** `make_windows` permits Monday design starts in 2018–22 only and excludes every window whose complete modeled expiry reaches 2023. Its synthetic fixture confirms the final eligible 2022 start is **November 28**, not December 5. Prior-day **16:30 America/Chicago purchase** and purchase-date plus 30 calendar days at **17:00 Chicago expiry** are explicit. The latter is a registered convention, not the exact dashboard expiry of an actual purchased account.

4. **Complete tail and common starts.** Windows require their full expiry boundary within the prepared tape. The same start list is used for every policy in a phase. Missing source sampling coverage yields an UNKNOWN row rather than clipping the window or admitting only its successful prefix. This conservative full-window rule can mark a case UNKNOWN even if an early outcome could otherwise have been known; that limitation is visible and does not improve the pass rate selectively.

5. **No 2023 nomination.** Selection summaries use the saved design pool. The pure helper excludes years outside 2018–22 and requires every design year and matching yearly start-calendar fingerprints. Previously seen 2023+ appears only in the validation command after a committed final nomination. All weekday validation point estimates and Monday-only paired 4/8-weekly-start blocks have distinct labels; no claim that weekdays are independent trials is made.

6. **Committed derived-definition chain.** The orchestrator now checks the exact committed initial selection, its linked SHA256, nominee membership/full policy equality, deterministic `derived_governors` output and counts. Final validation nominees must exactly equal registered initial/derived policies and obey the three-per-account cap. This resolved the initially reported weakness where only counts and file presence were checked.

7. **UNKNOWN is separate.** Missing or invalid risk-sized entry stops become request `-1`, reaching the engine as UNKNOWN rather than a zero-sized success. Unallocated keys are filtered out entirely. Missing held prices, unmatched nonzero fills and uncovered source windows are not filled with prices or zero returns. The selector retains pass/fail/expire/unknown in unconditional denominators and reports identification bounds; the 1% aggregate UNKNOWN gate controls certifiable nomination. EMPTY has an explicit 22-component zero/governor vector and is retained as an unselectable outcome control.

8. **Account death terminates processing.** The engine breaks on pass, floor failure, expiry or UNKNOWN; the runner uses the returned terminal row for elapsed time and observed-session counts. It does not add later source-trade P&L or include later chart re-entries as broker fills. DLL pauses and aggregate-position rejections differ from account failure. At the core interface, floor and DLL are checked before granting a target outcome, and liquidation uses modeled observed marks plus costs rather than snapping to a threshold.

9. **Actual integer units and explicit costs.** Lots use integer floors; risk requests are re-quantized by known entry-stop dollars and native micro point values, replacing source unit quantities rather than multiplying twice. The reviewed rules carry 60/120 aggregate micro limits. Main costs are $1.24 round trip per micro plus one tick per market side; stress doubles commission and uses two ticks. No fill slippage is imposed on limits. These are study assumptions; they do not certify every broker/instrument fee schedule. No-stop Bridge/OT trades remain distinct from a missing stop: governed profiles reject unbounded-stop entries rather than invent a source stop.

10. **Frozen artifacts and resumability.** The guard requires codex/work, exact committed implementation/config bytes and registered input hashes. The builder rejects actual glob-discovered raw inputs and static ledgers absent from the hash set; generated ledgers require the frozen adapter/source chain. Prepared tape artifacts and configuration are fingerprinted. Candidate outcomes have pre-outcome signatures, an exclusive writer lock, completion receipts and CSV hashes; selection recomputes annual summaries from those CSVs. These controls support reproducibility and concurrency safety, not independent economic verification.

11. **Uncertainty presentation.** Pure selection labels its output finite design nomination rather than global optimum. Equal-year unconditional pass minus a prespecified instability penalty, family/book neighborhoods, a risk-first pass-score band, and a conditional-speed role are defined before outcomes. Paired moving-block intervals retain unknowns and matched starts. Purchase-fee output is normalized for 50K; the $249 assumption is expressly a conditional 150K scenario, not a verified shared fee.

## Issues resolved before freeze

**B1 — Required risk-input completeness: resolved for this conditional model.** At first inspection, incomplete lookbacks could still grant finite sizing risk. The final builder/adapter mask every detected incomplete required risk input to NaN, retaining the owned-feed estimate only as a diagnostic. Whole missing internal candles are included in the source-span check; VCS reuses that strict bank. ST/PT check all OHLC constituents. Documented closure masks are distinct from missing open-market inputs. NaN risk-sized requests become UNKNOWN. Zero detected gaps still does not prove original feed parity or completeness of wholly absent edge days; the plan/evidence explicitly retain that limit. No completeness or native-source certification is claimed.

**B2 — Exact configuration, input manifest and source coverage: resolved as frozen conditional declarations.** The final config declares 2018-04-02 through 2026-07-07 full account dates for all 18 source keys, with source settings/compressions, original-study/workbook authority and limitations. Its 118 registered input hashes matched current bytes in a metadata/hash-only check. All 40 explicit raw files and 14 static ledgers belong to that hash set; four generated ledgers require the frozen adapter chain. Registered 2017 warmup has the dated normal closure masks before analysis starts. A declaration is not independent original-feed/no-signal verification; no absent history or post-tail hypothetical returns are admitted.

**B3 — Material target and unallocated-source uncertainty: resolved.** Frozen qualification is NQ 1.00 point, ES 1.00 point and CL 0.01. Trade-through must follow the target crossing on the modeled path, so an earlier high/low cannot qualify a later target. A declared source qualifier that is false or unknown fails admission; a source without such a field may use the conditional observed-path proof. An unmatched source order now carries its own NaN raw fill without replacing a shared observed asset price with NaN. Thus an unallocated uncertain source order cannot contaminate an unrelated held strategy; an allocated reached bad order remains UNKNOWN.

## Material limits even after blockers are resolved

- The common O→nearest-extreme→other→C path and cross-asset synchronization are conditional OHLC models. They do not recover quote order, broker fills, queue priority or source-feed parity. A saved report entry/exit is not a live trade match.
- Fast mode's `minimum_equity` is the visited-node/potential-risk minimum; `minimum_equity_lower_bound` is conservative, not exact joint drawdown. The reviewed runner does not yet include a raw survivor excursion rewalk or alternate chronology sensitivity. Freeze any such stage before execution, or retain these limits in final results. Synthetic raw/fast outcome parity is engineering evidence only.
- Thin-cushion states are fresh synthetic cash/floor states, not reconstructions of the four actual failed accounts. Exact historical purchased product, expiration, floor, fees and fills remain separate forensic evidence gaps.
- Current public rules distinguish Rithmic/WealthCharts evaluation floor caps from Tradovate's continuing trail. The reviewed capped rules do not represent every platform automatically. Before-target behavior is shared, but exact platform claims require their own receipt.
- Full dated 2018–26 holiday and exceptional closures are not admitted by missing timestamps. Proven scheduled nontrading intervals may omit price events; residual open-market holes remain UNKNOWN. Calendar handling must not manufacture prices, fills or flat returns.
- Reusing a source signal ledger after skipping, resizing or netting tickets is an explicit allocation/blocking model. Changed source-chart position state might alter future entries; native MultiCharts matching is still pending.
- No allocation, live trading, broker setting or deployment change is authorized by a research PASS. User/Claude review remains separate; no external message was sent.

## Synthetic checks run by this reviewer

- Imported and generated the policy registry in memory; checked unique signatures, account counts, CURRENT guard settings and a worst-case six-parent derivative reservation. No market files read.
- `python analysis/codex_eval_selection_20261104.py --selftest`: PASS, including unknown denominators, matching starts, excluded 2023 rows, risk-band boundaries, deterministic medoids and paired dependent blocks.
- `python analysis/codex_eval_run_20261104.py selftest`: PASS after orchestration hardening, including NaN risk requests, empty control, complete design expiry and validation-tail behavior. Its account case uses fabricated empty prices/events only.
- Final path-builder and extra-ledger synthetic selftests: PASS. No owned market data or outcomes were loaded by those commands.
- Config/input hash membership and exact-byte checks: PASS for 118 registered inputs, 40 explicit raw files, 14 static ledgers and 18 source declarations.

## Reviewed source hashes

|Artifact|SHA256|
|---|---|
|`analysis/codex_eval_policies_20261104.py`|`468be23ddbdd470ba217bbf87e0745f83cb3a640884a02fed5b6173acfef0a3a`|
|`analysis/codex_eval_selection_20261104.py`|`737d2e601a28ee0ceeecef76cb0ff4c5219c6b42137e80cedc47d9f8569a96bc`|
|`analysis/codex_eval_run_20261104.py`|`30c93b7354de9c969c3581ed8ffdf186d0477897387224d70152f28614966cf6`|
|`analysis/codex_eval_engine_20261104.py`|`cbbe04970b52c2bd2d2e088a6e146b044a611d812544a6fa15da37dda54f1996`|
|`analysis/codex_eval_paths_20261104.py`|`767694333f4eb69039ea5c6ed3568883a80abe5e0502f1baf4a188226b4d10b1`|
|`analysis/codex_eval_extra_ledgers_20261104.py`|`8d9b54b839fe227f7d7774032cc92d8140ea2d616e14abd606039501aaba9ae5`|
|`agents/codex/inputs/eval_audit_20261104/config.json`|`724faf41b75477eab74a814213f1c35dbcd56ff2424005311e14e920d0f7a438`|
|`agents/codex/inputs/eval_audit_20261104/policies.json`|`8feae0c4410ba7208c9f804c2492b28abb6671a2a017356e52f97d0e786bc321`|

No unresolved blocker remains for executing the bounded conditional study after the parent commits the exact preregistration. This is engineering/source-admission readiness, not a profitable-strategy finding, a global-optimality certificate or independent broker verification.
