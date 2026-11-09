# Evaluation-first baseline: WATCH — strategy-development mandate, no new alpha qualified

Summary: Evaluation work is now the active manual priority; current entries and sizes remain frozen.
On 2,234 fully covered starts, native-fee 30-calendar-day pass rates are 48.9% (50K) and 37.0% (150K).
A conservative adverse-minute DLL fill lowers them to 46.1% and 32.8%; these are execution bounds, not broker forecasts.
The calendar approximation is small; native costs, liquidation assumptions and sizing consistency matter more.
No new strategy qualifies yet; a free macro actual/consensus panel was acquired but fails current return-admission checks.

Plan: `agents/codex/plans/eval_focus_baseline_20261109.md`, commit `5815ed6`.
Script: `analysis/codex_eval_focus_baseline_20261109.py` (same commit).
Output: `analysis/outputs/codex_eval_focus_20261109/`.
Source: Claude `3e08d56`; raw NQ snapshot `fe35af99`; exact file hashes in `input_manifest.json`.
Trials run: **0 new alpha definitions; 4 predeclared account protocols on 2 frozen books**. No scout counters or prior trials reset. Independent verification: pending.

## What changed, and what did not

The user prioritizes an evaluation-specific strategy. This first phase audits the benchmark that will judge it. It does not optimize or adopt a strategy, change a trading plan, resume the paused lab/scout, run funded/personal searches or touch live systems.

Current 50K: VB 8 MNQ, ONB ADX30 risk $1,100, Bridge Monday 2 MNQ, EOS risk $500.
Current 150K: VB 20 MNQ, ONB ADX30 risk $2,750, Bridge Monday 5 MNQ, EOS risk $1,250, Twin cap1 v2.1 2 MNQ.
Risk quantities floor total risk divided by the native MNQ stop dollars. Floors keep trailing in evaluations. Target/trail/DLL: $3,000/$2,000/$1,000 on 50K, $9,000/$4,000/$2,000 on 150K.

Existing MultiCharts trade lists, source Twin simulator and source minute-path conventions are retained. This is a modelling check on the current stack, not a fresh independent validation of every strategy.

## Results: whole frozen books

Starts: 2018-01-02 through 2026-09-01; **2,234 common fully covered starting dates**. Calendar clock: first available trading date through the following 30-day exclusive boundary; earlier account purchase days are not included. Raw prices continue to 2026-11-04, while strategy export end dates differ. Fractions are rounded here; CSVs preserve exact values.

| Fixed protocol | 50K pass | Trail fail | Time-out | 150K pass | Trail fail | Time-out |
|---|---:|---:|---:|---:|---:|---:|
| Corrected-floor legacy: 21 sessions, standard net / 10, exact DLL clip | 49.42% | 48.93% | 1.66% | 38.27% | 60.74% | 0.98% |
| Actual 30-day clock; otherwise the same | 49.60% | 48.97% | 1.43% | 38.36% | 60.65% | 0.98% |
| 30-day clock + native MNQ commission | **48.93%** | 49.46% | 1.61% | **37.02%** | 62.44% | 0.54% |
| Same + adverse-minute DLL liquidation bound | **46.06%** | 52.60% | 1.34% | **32.77%** | 66.70% | 0.54% |

Native MNQ commission is the project's **assumed $1.25 round trip**, rather than $0.725 obtained by dividing $7.25/NQ by ten. Keep the existing slippage: one tick for a market/stop leg, no target-leg slip. This is not a newly confirmed broker fee schedule. The fee adjustment is $0.525 times each integer contract quantity/trade.

| Native 30-day results by era | 50K pass | Fail | Time-out | 150K pass | Fail | Time-out |
|---|---:|---:|---:|---:|---:|---:|
| Design, 2018–22; whole 30-day window ends before 2023 | 44.72% | 52.99% | 2.28% | 35.35% | 63.78% | 0.87% |
| Already-seen 2023+ historical replication | 54.60% | 44.66% | 0.74% | 39.05% | 60.85% | 0.11% |
| Recent, adverse-minute DLL bound | 50.79% | 48.36% | 0.85% | 31.64% | 68.25% | 0.11% |

Design has 1,270 starts; recent has 945. The 19 late-2022 boundary-crossing starts remain in full results but are in neither era comparison. Median successful duration under native 30-day modelling: **6 trading / 8 calendar days on 50K; 7 / 9 on 150K**. These durations condition on passing and do not describe the time or money needed to obtain a pass across repeated attempts.

No account fee is invented: idealized fees-per-pass index is **2.04 times the evaluation purchase fee (50K), 2.70 times (150K)**; under adverse-minute stress, 2.17 and 3.05. This is a conditional historical ratio, not a promise or an independence assumption about concurrent accounts.

## Paired uncertainty and interpretation

Paired moving-block resampling: 60 consecutive starting dates per block, 2,000 draws, seed 20261109. Overlapping starts are dependent. Bands are 90%, conditional on this history and model; they do not establish future stability.

| Incremental assumption | 50K pass change; 90% band | 150K pass change; 90% band |
|---|---:|---:|
| Actual calendar rather than 21 sessions | +0.18 pp; +0.04 to +0.31 | +0.09 pp; 0.00 to +0.18 |
| Native fees after calendar correction | −0.67 pp; −1.34 to −0.13 | −1.34 pp; −2.28 to −0.58 |
| Adverse DLL execution after native fees | −2.86 pp; −4.03 to −1.75 | −4.25 pp; −6.36 to −2.37 |

The first-passage tradeoff remains: reducing risk can save trail failures and simultaneously increase time-outs. Claude's capped-set study reduced failures but did not improve recent pass probability. We did not rerun or optimize that set here. Its cited 43.4% recent “current set” figure is not automatically the same benchmark as this report's 39.1% recent native baseline; see the sizing issue below.

## Material source issue: $250-unit rounding changes the “current” risk size

Claude's `eval_set_builder.py` builds risk units as:

```python
floor(250 / stop_dollars_per_MNQ) * 11  # labelled ONB $2,750
floor(250 / stop_dollars_per_MNQ) * 5   # labelled EOS $1,250
```

The current diagnosis / `bench150.setup` / this frozen baseline use:

```python
floor(2750 / ONB_stop_dollars_per_MNQ)
floor(1250 / EOS_stop_dollars_per_MNQ)
```

Those are different policies. For a hypothetical $150 native stop, ONB becomes 11 versus 18 MNQ, EOS 5 versus 8. This is arithmetic illustration, not a new return trial. Rounding risk units before combining can under-size both the supposed benchmark and optimized candidate. The standalone diagnosis's **38.3% overall 150K pass** is reproduced here at **38.27%** under its legacy convention; that does not certify the builder's portfolio comparison.

Smallest independent settling check for Claude: reconstruct daily quantities for the builder's reported current set versus `bench150.setup`, report mismatches and rerun its already frozen final portfolio against the actual unchanged current quantities, with the same date mask and consistent contract accounting. Do not retune the optimizer after this check or treat the already-seen period as untouched. No plan change follows from this source finding alone.

## Source/path caveats that block treating these as exact live probabilities

- Eight meaningful synthetic account checks passed before real outcomes: ongoing trail, calendar expiry, daily pause versus permanent fail, DLL overshoot and minute-tie ordering. All trade/path final-net reconciliations passed. These do not certify economic validity or actual fills.
- Original helpers add each position's adverse extreme within a minute. Different positions' extremes can occur at different instants. The stressed DLL protocol books that adverse combined mark; it can be pessimistic and is **not broker/tick replay**. The clipped protocol can be optimistic. Neither is a proven hard outer bound on all real execution paths.
- Bridge Sunday positions are booked to Monday; the inherited helper omits an exact Sunday mark path. Its diagnostic slice has 975 missing held closes across 217 exported trades, including session-time gaps; those are not automatically 975 unknown losing minutes. Audit which represent closed-market intervals, pre-entry minutes or genuine missing observations before any causal conclusion.
- Twin has 18 positions crossing midnight, **zero crossing a session break**. The inherited helper carries pre-midnight adverse risk into the exit date. These are different clocks. It has 316 missing held closes under the same diagnostic; VB has 3, EOS 1, ONB 0. Missing values in old path helpers are not evidence of zero risk.
- Report endpoints differ: VB 2026-10-06, ONB 10-12, EOS 09-18, Bridge 10-05; Twin rebuilt through 11-04. September 1 is the last admitted starting date, and not every component was newly natively replayed. Export absence later in history is not proof no new signal occurred.
- The public book/code status remains separate from compilation and actual use. Independent Claude/native execution review is pending. No new PowerLanguage was warranted by this phase.

## Strategy search: concrete source-feasibility progress, zero return tests

The next strategy needs an incremental return source that survives native costs, contributes within 30 calendar days and can help before common VB/ONB stops consume the daily budget. Testing more variants of the same concentrated stack is not the present work. See the active task and role packet: `agents/codex/TASK_eval_strategy_20261109.md`.

### New acquisition: historical actual / consensus releases

Downloaded the public repository `https://github.com/superpilot69/fred-us-macro-open-data`, pinned **`c3e2d4c79868ee516dc0ed111e1e4a28608a3a8b`**. Source data/notices, hashes and a reproducible no-return audit are saved under `agents/codex/inputs/eval_focus_20261109/macro_intake/`; script `analysis/codex_eval_macro_intake_20261109.py`. Upstream code was not executed.

| Raw occurrence series, design 2018–22 | Actual + forecast rows | Duplicate timestamps | Off 08:30 New York |
|---|---:|---:|---:|
| Headline CPI YoY | 60 | 0 | 0 |
| Core CPI YoY | 60 | 0 | 0 |
| Payrolls | 60 | 0 | **1** |
| Initial claims | 261 | 0 | 0 |
| Retail sales MoM | 60 | 0 | 0 |

Payroll 2020-03-06 is timestamped **12:30 UTC / 07:30 New York** in the vendor snapshot. That requires a primary release-clock check before use; no correction was silently made. There are no historical pre-release forecast receipt records or initial-actual primary-archive verification in this intake. FRED-derived current values and its assigned release timestamps must not be substituted for original announcement surprises.

**Decision: NEEDS DATA / provenance audit.** This is new acquisition progress on the previously blocked D51/shared macro-surprise inputs. It is not a strategy TEST verdict or a profitable result. A complete historical-looking file can still contain a one-hour clock error or revised values. No return, reaction or signal-value selection was computed.

### Other source-feasibility checks

**Dow opening reversal, SSRN7124578 / Lance Ladia:** five paper questions, source-only: (1) short-side YM opening reversal; (2) author reports 194 trades/59.79% wins, not reproduced; (3) proposed dealer hedge exhaustion, not observed signed dealer inventory; (4) potentially relevant to return-stream diversity, but exact overlap and risk are unmeasured; (5) exact replication code cannot be made from inspected material because full rule parameters/entry/exit clocks are missing. SSRN full-text attempts returned 403, and the author's public archive withholds strategy methodology. Do not guess rules and call them the paper's strategy. **NEEDS SOURCE**, no returns or new economic trial. Public source: `https://lanceladia.com/`; paper: `https://ssrn.com/abstract=7124578`.

**Actual auction information:** existing owned-price MOC tests do not supply auction messages. Prior Arca/NYSE evidence/data gates remain active; no new messages were acquired or paid request made. **Existing NEEDS DATA**, not a new candidate or trial.

Familiar London fixes, generic CL/NG inventory reactions, crude settlement/roll and other previously failed families were checked against the latest tier list and not rerun. The paused scout's seen/trial/reservation history remains untouched.

## Verdict and next admitted work

**WATCH on baseline readiness; evaluation-specific strategy development remains open.** No new strategy or live change is recommended. The immediate independent check is the risk-rounding / source-path discrepancy; the next candidate-building gate is a genuine macro-surprise source/clock/vintage admission or another distinct complete-source owned-data hypothesis. Follow the active task packet; any eligible return test gets its own exact committed plan/code before running. No background execution or program resume is claimed after this report.
