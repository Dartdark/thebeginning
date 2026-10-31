# Swing Target exit-kind replay: WATCH — adoption gain remains inconclusive

Summary: The corrected adapter reconciles all 602 frozen trades; it adds $132 total per MNQ versus legacy accounting.
Neither selected replacement establishes a payout/risk gain over BASE on this 500-history replay.
50K replacement: two-year payouts −$7 (95% paired mean interval −$260 to +$243); 150K: −$7 (−$287 to +$280).
The accounting correction changes selected first-year payouts by −$10 / +$20 and leaves their two-year payouts/blown outcomes unchanged.
The claim that the correction can only strengthen adoption is contradicted; no plan/live change is proposed.

Plan: [preregistration](../plans/swing_kind_replay_20261031.md), **92d1ad0**, cache clarification and implementation **66bf4ee** before account outcomes.
Script: [codex_swing_kind_replay.py](../../../analysis/codex_swing_kind_replay.py).
Outputs: [summary](../../../analysis/outputs/codex_swing_kind_replay_20261031/summary.csv), [paired effects](../../../analysis/outputs/codex_swing_kind_replay_20261031/paired_effects.csv), [manifest](../../../analysis/outputs/codex_swing_kind_replay_20261031/manifest.json), [verification](../../../analysis/outputs/codex_swing_kind_replay_20261031/verification.json).
Trials: no new strategy definition, parameter search or side selection; rerun of the five existing allocations per account, with corresponding EMPTY controls and legacy accounting arms. All comparisons are retained, including failures.

## Rule and sample as tested

Use Claude's `analysis/swing_target_bench.py` at **86df2c0**, its historical `plans50()` / `plans150()` allocations and Codex's frozen CODE_BE ledger. Source rules and both sides remain unchanged. Map target=1, stop/breakeven=0, time=2; retain the adapter's three early-close repairs. Corrected post-repair counts: 264 targets, 82 protective exits, 256 time exits. Legacy accounting uses strings except the three repaired numeric time exits, reproducing the original adapter defect.

The frozen account universe has **2,262 trading days, 2018-01-02 through 2026-10-09**. These are historical validation dates, not a new holdout. No selection on plan occupancy, no model fitting or retuning. Every strategy's day stays together in circular 20-day blocks. Both accounting arms and all allocations receive the same **500 paired 500-day histories**: seeds 1/2, 250 each. First-year horizon is 250 trading days. Account paths use the repository's `funded_bootstrap.Boot` and unchanged 50K/150K simulators, including intraday adverse marks, daily loss pauses, floor checks, payout caps and cushion sizing (references $1,500/$3,000). Actual simulated quantities are floored to integers after cushion scaling.

This isolates the adapter defect with the historical roster. The 50K baseline still contains RS longs; today's roster has T_ONESIDE instead. The ST ledger repairs three held holiday trades at the early close; v3 skips those holidays. Neither current-roster validation nor exact v3 rule replication is claimed.

Fees preserve the historical comparison: **$7.25 per NQ round trip divided by 10**, plus **$0.50 per MNQ for each non-limit fill**. This is cheaper commission than actual micro costs and is not native-MNQ fee validation. Entry/exit signals and quantities have identical clocks in both accounting arms. There is no new fill-delay or liquidity assumption.

## Corrected account results

Payouts are mean dollars actually withdrawn per account, capped at $13,000 / $20,500 over six payouts. Blown/all-six are shares within the 500-day horizon. Days to sixth payout count unfinished or failed histories as infinity before taking the median. The fifth-percentile payout is an outcome percentile, not a confidence limit.

| 50K allocation | Year 1 | Year 2 | Year 2 p5 | Blown | All six | Median days to sixth |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BASE: VB 2/1 | $9,818 | $12,182 | $1,500 | 6.4% | 93.0% | 244 |
| ADD ST 1 MNQ | $10,292 | $12,040 | $0 | 8.0% | 91.6% | 224.5 |
| RS longs → ST 1 | $10,178 | $12,198 | $1,500 | 6.4% | 92.8% | 238 |
| EOS → ST 1 | $9,595 | $12,213 | $1,500 | 6.2% | 93.2% | 248 |
| Selected: VB 2/1 → 1/1 + ST 1 | $9,822 | $12,175 | $1,500 | 6.2% | 92.2% | 242.5 |
| EMPTY: remove one normal VB | $9,284 | $12,205 | $1,500 | 6.2% | 92.8% | 264 |
| EMPTY RS longs | $9,354 | $12,114 | $1,425 | 7.0% | 92.4% | 264 |
| EMPTY EOS | $8,995 | $12,242 | $1,500 | 5.4% | 93.2% | 273.5 |

| 150K allocation | Year 1 | Year 2 | Year 2 p5 | Blown | All six | Median days to sixth |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BASE: DT 2 MNQ | $17,861 | $20,139 | $20,500 | 1.8% | 97.8% | 213.5 |
| ADD ST 1 MNQ | $18,088 | $19,985 | $20,500 | 2.6% | 97.2% | 204 |
| ADD ST 2 MNQ | $18,425 | $20,044 | $20,500 | 2.4% | 97.6% | 196.5 |
| Selected: DT 2 → ST 2 | $17,886 | $20,132 | $20,500 | 1.8% | 98.0% | 209 |
| DT 2 → DT 1 + ST 1 | $17,615 | $20,075 | $20,500 | 2.0% | 97.6% | 213 |
| EMPTY DT | $16,543 | $19,916 | $20,500 | 2.8% | 96.4% | 233 |
| EMPTY one DT | $17,085 | $19,903 | $20,500 | 3.0% | 96.6% | 225 |

The full `summary.csv` also retains first-year p5 and every legacy arm. The original published table is a separate historical run; its cached lab/run provenance was not available. This uses newly rebuilt, hashed inputs and declared seeds, so it is not a bit-for-bit reproduction of that table. Evaluate the paired correction within this replay; do not attribute every difference from the published table to the kind fix.

## Paired effects and verdict

Intervals below are 2.5–97.5% percentiles from 5,000 resamples of the paired simulated outcomes (seed 20261031). They measure sampling uncertainty under this fixed historical generator; they do not establish future edge or account for data/model/rule uncertainty.

| Selected allocation vs control | Year 1 difference [95%] | Year 2 difference [95%] | Blown difference [95%, percentage points] |
| --- | ---: | ---: | ---: |
| 50K swap vs BASE | +$4 [−$258, +$273] | −$7 [−$260, +$243] | −0.2 [−2.2, +1.8] |
| 50K swap vs EMPTY one normal VB | +$538 [+$312, +$765] | −$30 [−$215, +$154] | 0.0 [−1.6, +1.6] |
| 150K swap vs BASE | +$25 [−$315, +$345] | −$7 [−$287, +$280] | 0.0 [−1.4, +1.4] |
| 150K swap vs EMPTY DT | +$1,343 [+$1,049, +$1,641] | +$216 [−$52, +$497] | −1.0 [−2.4, +0.4] |

**Both existing adoption gains remain INCONCLUSIVE.** The selected swaps reach the sixth payout 1.5 / 4.5 median trading days sooner than BASE, but that point estimate does not demonstrate a reliable speed improvement. Versus EMPTY, ST improves first-year payouts; two-year and blown comparisons still include zero. No alternative allocation is selected after inspecting this run.

The correction itself, selected swap vs its identical legacy arm:

| Account | Year 1 effect [95%] | Year 2 effect | Blown effect | Histories with changed year 1 payout |
| --- | ---: | ---: | ---: | ---: |
| 50K | −$10 [−$30, +$9] | $0 | 0.0 points | 4 / 500 |
| 150K | +$20 [$0, +$46] | $0 | 0.0 points | 3 / 500 |

The stronger monotonicity claim is **CONTRADICTED**: for the 50K ADD arm, corrected accounting raises blown from 7.8% to 8.0% (one additional failed history) and lowers two-year payouts by $10. Better component equity can change subsequent integer sizing and payout timing. Account outcomes must be replayed; trade-level improvement does not determine their sign.

## Verification and material limits

- Corrected trade nets reconcile to the repaired ledger and daily totals: $198,478.35 per NQ; corrected minus legacy $132 total per MNQ. Shared BASE/EMPTY controls contain neither ST arm. Complete unique history keys and source hashes pass.
- Synthetic long stop/target fixtures reproduce both defects: numeric protective kind clamps the exit-minute adverse mark to the slipped stop; string kind retains the entire bar extreme. Numeric target charges one slipped fill, legacy string target two. These checks verify mechanics, not live execution.
- `build_lab.py` initially failed on ONB's 2026-10-12 midnight exit. The committed implementation applies the already-frozen cutoff before baseline paths and builds only required components; no in-window geometry failures were removed. The audit retains every loaded/excluded count. No shared loader, simulator or trading file was edited.
- Continuous NQ bars stand in for actual MNQ fills; inferred report fill minutes, same-minute path ordering, target trade-through, missing-data behavior and tick rounding remain inherited. OT and CLS use whole-day adverse approximations; MOC uses close-based marks. These may distort overlap and floor checks. OT source ends 2026-07-07; later zeros are missing coverage, not verified no-signal days.
- The historical report-driven roster retains its existing holiday/timing conventions; the adapter's early-close repair is not proof of exact v3 parity. Unknown author trial count and already-inspected 2023+ remain. No new significance test or placebos can make this accounting rerun fresh alpha evidence.
- Rebuilt research caches are ignored local artifacts. All report numbers come from the committed runner and retained per-history CSVs. Verification-only code was added after outcomes; worker/preparation/summary logic was unchanged.

No PowerLanguage was written. No VPS/broker/account settings, live trading, plan, tiers or external messages were changed. Claude should review this result before updating the existing adoption rationale; validating today's roster and exact v3 at native micro fees is a separate bounded task.

## Reproduction

Use the repository dependencies (`numpy pandas numba openpyxl scipy scikit-learn`). Build `g24.pkl`/`ge.pkl` with `Grid24` or run `analysis/build_lab.py scratch_data` (its later ONB failure is documented above; the two grid files are created first). Then:

```
python3 analysis/codex_swing_kind_replay.py prepare
python3 analysis/codex_swing_kind_replay.py worker 50 1 250
python3 analysis/codex_swing_kind_replay.py worker 50 2 250
python3 analysis/codex_swing_kind_replay.py worker 150 1 250
python3 analysis/codex_swing_kind_replay.py worker 150 2 250
python3 analysis/codex_swing_kind_replay.py summarize
python3 analysis/codex_swing_kind_replay.py verify
```

For Claude: `agents/codex/results/swing_kind_replay_20261031.md`.

## Concurrent result found during final pull

A separate committed Codex replay arrived during publication: [swing_replay_20261031.md](swing_replay_20261031.md), remote commit **8e3b62d**. It uses the same 2,262-day universe and 500 histories with seed 1 alone; this run uses seeds 1/2 with 250 each. Its selected swaps change two-year payouts versus BASE by −$83 (50K) / +$43 (150K), both with intervals crossing zero. Both runs find identical two-year outcomes for the selected corrected-versus-legacy arms and $132/MNQ ledger correction. The shared conclusion is inconclusive adoption evidence; neither run is independent strategy verification. Their histories overlap, so do not pool them as 1,000 independent histories or choose the more favorable table. Both records are preserved. The extended-data audit also independently identifies the ONB sentinel as an explicit unfinished `open` valuation. Execution references retain that remote entry as E39 and this run's accounting lesson as E43.
