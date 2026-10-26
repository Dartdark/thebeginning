# H05 protected design: SOURCE/SYNTHETIC PASS

Independent review, 2026-10-26, before actual ATR admission or stopped outcomes. Reviewed on `codex/work`, HEAD `6dcad4f75b812e3a5ec49a16c1f13cea4c3df8a4`. Only source, the pre-outcome adjudication note and artificial in-memory inputs were examined. No actual native prices, ATR values, source/trade ledgers, cache, workbook or economic-output bodies were read. No actual phase was called. This review adds0 gross screens/evaluations and is not a strategy, book or promotion pass.

| Reviewed source | SHA256 |
|---|---|
| `analysis/codex_hunt_v2_highwin_design.py` | `86f90eac4a219559ba2840114ce54d26ccd6987494fd684f02cc07471d9c6502` |
| `analysis/codex_hunt_v2_highwin_execution.py` | `ae2da720de092fe2d9563f6ec9f48ed8ee62bd62e5b1ac98487e0c434baca5e3` |
| `agents/codex/research/hunt_v2_highwin_atr_adjudication.md` | `e0bdc3c9080c4b902f461557791096c5f9383e07a84cdc80d067c2c8c6adf04c` |

## ATR admission and outcome boundary

The root's pre-outcome policy admits the exact observed-date `Grid24.daily_atr(15)`, not an ideal full-session substitute. The implementation calls that shared function and its shared reference-membership audit. Every event requires15 stored weekday reference dates before the decision, references on/after fixed2017-09-01, shared-value equality and a finite positive ATR. Previous observed-close IDs used in true ranges are retained. An overnight-only normal date with observations remains a stored partial-date range; wholly absent dates remain absent. Partial normal RTH references, missing normal dates and every affected event remain explicit `SOURCE_LIMIT` records. No price/range substitution, entry deletion or denominator change is performed.

`--phase admit` loads the gross-bound native scope and exact216 unique parent IDs/dates, checks native entry prices against the unchanged gross proof, computes source/ATR facts and writes the private NPZ cache under the ignored `OUT/cache/` directory. It computes no new protected or TIME_CONTROL outcome. A failed admission retains source facts and cannot enable design. Missing ideal minutes and ordinary price-receipt logs do not acquire new fatal requirements beyond the frozen definition.

`--phase design` requires the explicit exact admission-marker SHA, matching preregistration/script and a PASS marker, unchanged admission artifacts and the exact private cache hash before loading execution inputs. Gross marker/artifact/input hashes, required code/dependency/preregistration/HEAD bytes and the branch are checked; hashes are rechecked after execution. Exclusive phase locking, write-once attempts/completions and the output-family retry guard prevent silent retries or alternate-directory reruns. No2023+, broad pickle, old financial maker or account engine is called. NPZ loading uses `allow_pickle=False`.

Source inspection confirms that the first new outcome call is `execute_native_models` after this boundary. Only `PROTECTED_HW` and matched `TIME_CONTROL` are executed. The final actual design marker adds2 economic evaluations; admission adds0. A later failure cannot erase the retained actual attempt. No delay configurations run at this stage.

## Execution and cost checks

The adapter clones the shared `grid.execute` function with a private globals dictionary; shared code/globals and native input arrays remain unchanged. Its private walker calls the shared Python walker once per trade. Stops/targets are active from the entry bar. Worse opening stop gaps retain the shared worse OPEN fill. If the shared path picks a target on a bar that also hits the stop, the declared override selects the stop and reconstructs stop-first excursion. Targets require1 NQ point of trade-through and receive the exact limit without favorable gap improvement. Long/short stop and target prices round outward to the frozen0.25 tick.

Protection scans through native890. Only the private copied close890 is replaced by nativeOPEN891 for a surviving time exit; the ledger relabels that endpoint891. High/low891 cannot affect protection after the time exit. Missing endpoints are rejected. All admitted entries must produce a trade in each model; an engine omission is fatal.

Native MNQ gross comes directly from price difference times2USD/point. Commission is1.24USD RT, entry adverse slippage0.50USD, and stop/time-exit slippage0.50USD; targets incur no second market slippage. Shared NQ engine net is retained as an ignored diagnostic, never divided to obtain native net. The cost bridge separates gross, commission and slippage; TIME_CONTROL must reconcile by event ID to the frozen raw endpoint gross.

## Fresh synthetic evidence

Re-ran5 author main groups and the final10 author adapter groups through pure functions with Python `-B`, actual `pandas.read_csv` and `numpy.load` denied. Fixture CLIs/writers were not called. The main sets the Codex-owned Numba cache location before imports; execution uses `_walk.py_func`, not a compiled run.

Four fresh independent main groups passed:

1. Fake wrong/failed admission SHA, preregistration and script markers reject before any cache/entry loading, writing or outcome call.
2. Artificial shared ATR references retain all216 partial-source events and15 past IDs. Poisoning future prices cannot change a prior event's ATR or reference IDs.
3. Zero ATR fails admission with all216 failure records retained.
4. NW5 matches an independently constructed Bartlett covariance calculation. Both models'36 period/side metric rows reconcile to their complete weekday daily series and long/short totals.

A focused independent execution review additionally passed4 groups covering mirrored stop-first behavior through890, short target gaps without improvement, native-fee independence from the shared NQ commission and outward tick rounding.

One synthetic defect was found and corrected BEFORE actual ATR/outcomes: the first adapter version omitted an adverse OPEN891 time gap from the shared engine's excursion. Root requested the correction. The final SHA above includes actual exit price in worst excursion for every exit kind and exposes `adapter_worst`. Fresh independent mirrored tests set otherwise-flat100 bars and nativeOPEN891 to70 long/130 short: both models exit exactly891, net−62.24USD/MNQ, shared-engine MAE600USD/NQ, no input mutation. P&L and statistical gates did not change. Old synthetic attempts remain retained; this is no new model/economic trial.

The cheap gate exactly requires primary≥100 trades, positive total, trade t≥2, daily NW5t≥2,≥4/5 positive years and positive total excluding each year. Metrics use the shared `metrics.perf`, frozen weekday axis and established NW5 estimator. A statistical PASS explicitly leaves source limits unresolved and directs the immediate frozen personal19 bench before robustness or2023+; a failure closes H05 at this stage.

## Verdict and limits

**SOURCE/SYNTHETIC PASS for the exact staged ATR admission and two-model native-cost design after the parent's commit.** No preexecution blocker remains. Parent owns the one actual admission, verifies its marker, then runs design only on PASS.

The observed partial ranges, external feed/contract mapping, zero additional receipt delay and NQ-to-MNQ fill assumption remain research limitations, not certified data or execution. The scalar excursion diagnostic is not a joint account path; no funded, payout or evaluation improvement follows from it. This review is not the later independent raw-spec trade checker. No statistical result can resolve these source limits, confer MC parity or approve trading. Immediate paired personal19 benches and all later selection/placebo/dependence/independent-review requirements remain as frozen.
