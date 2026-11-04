# Frozen evaluation audit runner

`analysis/codex_eval_run_20261104.py` is research orchestration. No market preparation or account return work was executed while implementing it. Its `selftest` uses invented boundary-only prices/events and synthetic allocation inputs. It cannot change installed strategies, trading plans, actual accounts or broker settings.

The registered menu has2485 initial definitions, with at most30 deterministic derived policies (at most2515 total under3000). This separate user-requested portfolio audit does not resume/reset the scout, t6 or Strategy Hunt v2 budgets. Source entry/exit rules are frozen; no signal parameters are searched.

## Ordered commands and publication boundaries

Use `/workspace/venvs/thebeginning/bin/python`; run from repository root on `codex/work`. The examples use literal placeholders `PREREG_SHA`, `INITIAL_SELECTION_SHA` and `FINAL_SELECTION_SHA` for full40-character committed SHAs. First commit the final evidence, preregistration, exact configuration, policies and implementation; then:

```text
/workspace/venvs/thebeginning/bin/python analysis/codex_eval_run_20261104.py prepare --commit PREREG_SHA
/workspace/venvs/thebeginning/bin/python analysis/codex_eval_run_20261104.py screen --pool initial --commit PREREG_SHA --workers 4
/workspace/venvs/thebeginning/bin/python analysis/codex_eval_run_20261104.py select --stage initial --commit PREREG_SHA
```

Commit `design_selection_initial.json` and `derived_policies.json` before any derived account outcomes. Then:

```text
/workspace/venvs/thebeginning/bin/python analysis/codex_eval_run_20261104.py screen --pool derived --commit PREREG_SHA --selection-commit INITIAL_SELECTION_SHA --workers 4
/workspace/venvs/thebeginning/bin/python analysis/codex_eval_run_20261104.py select --stage final --commit PREREG_SHA --selection-commit INITIAL_SELECTION_SHA
```

Commit `frozen_validation_selection.json` before any validation outcomes. Then:

```text
/workspace/venvs/thebeginning/bin/python analysis/codex_eval_run_20261104.py validate --commit PREREG_SHA --selection-commit FINAL_SELECTION_SHA --workers 4
/workspace/venvs/thebeginning/bin/python analysis/codex_eval_run_20261104.py archive --commit PREREG_SHA
```

The runner verifies exact committed config/implementation/policies bytes, full-SHA ancestry, every registered input hash, prepare artifact hashes, definition counts and deterministic derived-parent policy equality. Frozen nominees must exactly match a reserved policy. Unrelated working-tree changes are preserved. No reset, staging, commit, fetch or push occurs inside the runner.

## Frozen timing, costs and selection

- Every start uses the prior calendar date16:30Chicago modeled purchase time, with explicit expiry30calendar dates later at17:00Chicago. Actual purchased-dashboard expiry would override this declared convention; these are synthetic fresh starts, not current open accounts.
- Design uses the same Monday start calendar for all definitions in2018–22. Its **entire expiry is before2023-01-01**, so late2022 account windows cannot leak2023 returns into selection. All starts must have full expiry within the prepared common source window; tail accounts are never shortened or padded.
- All registered definitions get the main cost: RT$1.24 per micro plus one adverse tick per market/stop fill. Only frozen validation nominees and identical-calendar reference controls receive low RT$1.04/one tick and stress RT$2.48/two ticks. Limits do not get fictitious adverse price adjustments; liquidations include market costs.
- The pure selection helper uses equal-year mean unconditional pass minus0.25population SD, with all2018–22 years, common yearly calendars, at most1% unknown outcomes and its preregistered family/book medoid rules. At most3 policies/account advance. Empty receives an explicit zero-allocation vector and is unselectable.
- Derived governors are the exact four declared floor-risk rules plus a separate target-guard-only counterfactual per nominee, deduplicated within the30-definition reservation. Each stage is design-only until the frozen validation commit.
- Historical validation uses all weekday starts in previously seen2023+ data, reporting2023–25 and2026 separately as well as pooled. It is not fresh out-of-sample evidence. Paired5000-resample4/8weekly-start moving-block confidence intervals use the Monday subset; all-weekday point estimates are still reported. Price bars are not resampled.

## Allocation and account semantics

Lot allocations become integer micro quantities. Dollar-risk allocations become `floor(dollars / (signal-time stop points × micro point value))`. An unavailable/nonpositive stop becomes requested quantity−1 and yields UNKNOWN if the entry is reached; it is never zero-sized to hide missing risk. Unallocated strategy keys have no source events at all. Unit-source quantities are replaced, not multiplied again.

CURRENT and ordinary static/floor-risk policies explicitly have `target_guard=False`; installed current guard settings are unverified. A policy with `target_guard=True` is a separately labeled prospective counterfactual. It flattens at an observed modeled mark when equity reaches target+$50, pays costs and then checks realized target. It is not assumed installed.

No-stop BRIDGE/OT positions retain infinity as their known absence of a source stop. Static lot policies can request them; a floor-risk governor rejects an unbounded stop rather than inventing one. Thus a governor on a book containing BRIDGE may effectively remove its entries; rejection/trim counts are saved. Source schedules are frozen. After a source entry is denied, that key is blocked for the remainder of the session to avoid inventing conditional re-entry paths after a skipped base trade.

The engine separately models intraday inclusive floor failure, EOD floor updates, native net exposure caps, broker DLL liquidation at modeled prevailing marks and pause, and15:59Chicago flat deadlines. Source fills and all sleeves use one common asset OHLC chronology. UNKNOWN remains an outcome. Failure/pass/expiration/account death stop subsequent source P&L; no post-death chart trades are counted as account fills.

Thin-cushion tests start with zero profit and25/50/75% remaining floor headroom. They are explicitly synthetic account states, not reconstructions of a current purchased account. The common OHLC path, inferred source fill phases and quote synchronization remain model assumptions requiring independent raw-spec review. Fast segment bounds prove when intermediate quotes cannot hit a boundary; ambiguous segments are walked. The reported visited-node minimum is not mislabeled an exact portfolio drawdown; the separate conservative bound is retained.

## Saved outcomes, resumption and cost reporting

Runtime files are under `agents/codex/runtime/eval_audit_20261104`: immutable prepared tape/source receipts; per-candidate/start CSVs; per-candidate completion fingerprints; annual summaries; initial/derived design completion files; and validation reports for every cost/state scenario. Case rows include status/reason, purchase/expiry/start clocks, elapsed calendar days, observed NQ trading-session count, equity/cash/floor, commissions/slippage/liquidation costs, DLL halts, rejected/trimmed entries and maximum net micro exposure. Observed NQ session flags come from the owned grid and are not represented as a newly certified exchange calendar.

Each candidate has an advisory exclusive file lock. Partial rows are flushed after each historical start; resumed work requires an identical frozen definition/settings/input/calendar signature and a calendar prefix. Completed case hashes are checked and reused, never silently rerun. A durable completion receipt precedes atomic CSV publication, permitting crash recovery without re-observing completed outcomes. Design selection recomputes annual summaries from hash-checked saved case CSVs.

`archive` saves exact case CSVs/receipts in a compressed ZIP with a hash manifest, excluding the large reconstructible tape arrays. It does not publish anything. Root should stage only relevant reviewed artifacts and select a suitable archive size; runtime trees must not be blindly staged. `--workers 1` supports serial execution; parallel workers require POSIX fork and share the prepared tape without independent raw-data reloads.

Fee results report descriptive normalized fee/P(pass), including unknown-outcome identification bounds. Only150K adds a clearly conditional$249 purchase-price scenario;50K never receives an invented$249 fee. Activation/reset/other charges and correlated retries are not silently included in an expected-pipeline forecast. Independent economic verification stays pending until actually performed.
