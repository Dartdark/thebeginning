# S30 cash-session IBS: WATCH — personal-account hypothesis, ineligible for the Apex plan

Summary: S30 is personal-account-only as submitted; it holds for days without a stop.
Claude's latest rebuild reports PF 1.82 NQ / 1.85 ES, but its daily portfolio accounting is inconsistent.
Published daily P&L is $56,831.50 versus $53,833.33 corrected net trades for the same micro pair/endpoints.
The resulting $33k personal-capital recommendation needs recomputation before relying on it.
Keep it outside Apex; reconcile the existing model rather than treat it as an untested new rule.

Plan: not applicable — source/document audit, **0 new strategy return trials**.
Evidence: `agents/codex/evidence/s30.md`. Script: `analysis/codex_s30_source_audit.py`.
Output: `analysis/outputs/codex_s30_source_audit/`. Inputs: `agents/codex/inputs/s30/`.
No price/cache construction, strategy replay, compiler, Monte Carlo or account simulation was run.
Latest reviewer evidence: Claude `28be7aeb7b2ee2e4b9e10b3b157fe091fcdc2609`; scripts, outputs and existing
trade/daily ledgers are preserved in `agents/codex/inputs/s30/reviewer_snapshot/`. Those files were read,
not executed. The audit performs arithmetic on already-published results; it generates no new strategy returns.

## Rule (as submitted)

IBS measures where the cash session closed within its high/low range. At the completed 15:00 CT bar,
buy if flat and IBS<0.20; exit an existing long only when a later session has IBS>0.80. Source lines 86–106
collect 26 bars stamped 08:45–15:00. The next-bar market order refers to approximately actual 15:00,
the open of the bar stamped 15:15; it does not intentionally wait another fifteen minutes.

The rule is long only, with no stop, target or time exit. It deliberately holds overnight, over weekends,
holidays and potentially rolls (8–10,103–106). The PDF reports a four-calendar-day median hold. It therefore
cannot enter our current Apex account comparison as written. Flattening daily would change the central
holding rule, rather than merely adjust its operating hours.

## Results — author claims, not our backtest

Whole-sample figures below are from the overview's corrected-results header, per one micro. The code's
ContractQty 1 is one full contract when charted on @NQ/@ES/@RTY; no micro conversion is coded.

| Market | Trades | Reported net | PF | Win | Average | Reported open-inclusive DD | Closed DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| NQ / MNQ | 273 | $36,868 | 1.86 | 70.3% | $135.05 | $6,677 | $3,764 |
| ES / MES | 260 | $22,623 | 1.94 | 68.5% | $87.01 | $5,238 | $2,674 |
| RTY / M2K | 271 | $5,852 | 1.30 | 58.7% | $21.59 | $3,540 | $2,463 |

Published annual rows, summed arithmetically:

| Market | 2018–22 n | 2018–22 net / micro | 2023+ n | 2023+ net / micro | 2023+ average |
|---|---:|---:|---:|---:|---:|
| NQ | 157 | $21,537 | 100 | $13,633 | $136.33 |
| ES | 148 | $13,679 | 96 | $8,088 | $84.25 |
| RTY | 157 | $6,751 | 108 | −$837 | −$7.75 |

Annual trade counts agree with the headers. Summed annual nets differ by only +$1/−$1/−$2 for NQ/ES/RTY;
the component headers sum to $65,343 versus the combined rounded $65,342. These are ordinary rounding
differences, not evidence of an accounting defect. The saved CSV preserves every year, including losses.

NQ and ES show enough reported persistence to merit a personal-account verification. RTY is the weaker leg,
especially recently. The three long index exposures should not be treated as three independent diversifiers.
Our own t-stat, DSR, Sharpe, Sortino, Calmar, Ulcer, confidence intervals, placebo and account results are
**not available** from this source review; the PDF does not supply the ledgers needed to reconstruct them.
There is no traded short side. The PDF's historical mirrored-short experiment is a separate disclosed trial.

## Latest Claude review — accounting issue before portfolio sizing

The latest branch already tests this exact family and ranks it B for a personal account. That is separate
from the PDF's older grading. Its source file and PDF exactly match these uploads by Git blob hash; all saved
reviewer files match their pinned Git blobs. Its Python rebuild reports:

| Market | Trades | Net per full contract | Mean per full contract | PF | t |
|---|---:|---:|---:|---:|---:|
| NQ | 253 | $342,045.75 | $1,351.96 | 1.82 | 3.5 |
| ES | 240 | $196,287.50 | $817.86 | 1.85 | 3.6 |

These are positive closed-trade results at the modeled costs, not verified native-micro execution or a new
clean holdout. The central defect is a mismatch between that trade accounting and the daily equity used
for correlation, Monte Carlo and the personal-portfolio capital recommendation:

1. In preserved `s30_ibs_test.py` 41–49, trade net deducts identified roll jumps, commission and fill slippage.
   In 91–94, daily MTM is built independently as position × raw close change. It receives none of those
   adjustments, and its close marks are not reconciled to the entry/exit fill prices.
2. Its exported combined daily CSV totals **$56,831.50**, while the saved corrected net trades total
   **$53,833.325** after division by ten. Both legs and the daily series end 2026-10-07; the difference is
   **$2,998.175**. This is an accounting reconciliation failure over completed positions, not a newly
   simulated loss or a corrected performance forecast. See `reviewer_accounting_checks.json`.
3. Preserved `personal_portfolio.py` 82–88 imports that daily CSV unchanged, adds it to the personal book,
   and derives its return, Monte Carlo DD and roughly $33k capital threshold. S30 also misses the extra
   micro-fee charge applied to the other legs in 22/25. The reported portfolio gain/capital estimate therefore
   does not use consistent after-cost, roll-corrected accounting. The corrected change in DD/capital is unknown.
4. The holding benchmark and random-entry controls in 74–89 retain raw roll jumps, unlike candidate
   trade net. The output acknowledges that asymmetry. Random entries can overlap and can silently skip
   unavailable exit prices while still dividing by the requested count. Treat p≈0.03 and the claimed
   drift fraction as provisional until accounting/opportunity counts are comparable.
5. Daily reconstruction includes only closed trades and ends at the last closed exit. Partial cash sessions
   have missing marks which are forward-filled, moving their P&L into later days. The latest open position
   and omitted tail risk are not incorporated. These details matter to drawdown and bootstrap paths.

I agree with the personal-only classification and that NQ/ES warrant further validation. I would not
endorse the current capital threshold or portfolio forecast. Build one chronological, net marked ledger
using the same positions/fills/costs/roll corrections, including partial sessions and endpoint open equity;
reconcile it to net trades plus the final open mark, then rerun the existing portfolio and controls with
unchanged entry/exit rules. This audit has not made that repair or computed replacement returns.

## Placebos and account level

The PDF's B scale is not our S–F ranking, and those Bs were explicitly computed on earlier exports
**before roll correction**. The grading table's NQ count 274 versus the current 273 includes an earlier
then-open final trade, according to its footnote. Do not apply the old bootstrap expectations, probabilities
or trade-sequence Monte Carlo percentiles to the newly corrected results without recalculation.

The overview itself says recent NQ research profit was close to an exposure-adjusted holding benchmark.
Profitable mirrored shorts in design history and positive 2022 are useful observations; neither alone
establishes drift-independent alpha. A later validation needs comparable holding times/exposure/volatility,
random-entry controls and chronological open-equity risk, including any open position at the sample end.

No Apex bench was run: the submitted overnight holding rule is ineligible before profitability is considered.
This audit makes no personal-account capital recommendation or forward promotion. Historic drawdowns at even
one micro are materially larger than the current $2,000 Apex drawdown budget; historical DD is not a maximum
possible loss. Removing the prop rule does not remove overnight margin or liquidation risk.

## What could make this wrong

1. **Roll correction remains unverified.** The PDF says 62 trades spanned rolls (NQ 17, ES 22, RTY 23), with
   $5,280 of gaps in micro-scaled accounting, and acknowledges two estimated gaps (June 2022 and ES September 2026).
   Source 23–26 describes the issue, but executable code contains no gap adjustment or rollover orders.
   A correction to exit profit alone does not establish corrected open-equity DD, MAE, portfolio aggregation
   or actual roll execution. A properly specified adjusted-price series also needs its relation to the held
   contracts and session extrema checked. Native exports and the signed roll ledger are the next evidence.
2. **Cost units are unresolved.** The PDF states $2.50 commission plus $5 slippage per trade on full-contract
   charts, then presents micro-scaled results. Verify whether those dollars were full-contract or native-micro
   costs and whether commission is round trip/per side. Dividing full-contract profits by ten does not establish
   actual MNQ/MES/M2K trading costs. There are additional costs when an open position is rolled.
3. **Closed-equity measures omit risk.** The PDF excludes still-open endpoint positions. Combined DD is
   closed-trade-only because positions overlap; individual DD combines closed equity with trade worst open
   losses. Trade-sequence Monte Carlo is not synchronized mark-to-market portfolio risk or a daily trail test.
   NQ/ES can both be exposed during the same extended sell-off.
4. **Skipped sessions prolong exposure.** A missing 08:45 start bar, ordinary missing interior bars, wrong
   end stamp or zero range generally suppresses the session decision (86–106), including an exit. The code
   validates count/end time, not the exact timestamp sequence or a complete cash-calendar policy. It never
   exits merely because a session is invalid. This is consistent with the stated design, with data-failure risk.
5. **Selection and implementation are not settled.** Source 38 forces IOG off, but chart/session, pyramiding,
   fill/fee properties and native compilation were not independently verified. The PDF discloses VWAP, short,
   multi-market and Nikkei trials, and prior ES exposure to 2023+. Future examination of that history is
   replication, not a fresh holdout. Published citations are not independently checked primary-paper evidence here.

## Existing-research overlap and next step

`TIER_LIST.md` already records IBS/pivot failures and the ES mean-reversion test. That specific F6 implementation
(`analysis/es_mean_reversion_test.py`) uses yesterday's IBS to trade the next 08:31–15:00 session, including
shorts and several thresholds. S30 enters immediately after 15:00 and holds until an upper-range close.
Do not equate the two rules or claim this exact implementation was already rejected. The latest Claude
`28be7ae` does now contain an exact S30 row/rebuild and personal-portfolio test, reviewed above.

Evidence status: **DON'T TEST in the current Apex plan; NEEDS DATA/accounting reconciliation for personal
decisions**. Repair and reconcile the current daily ledger before trusting its portfolio/MC figures.
Native corrected exports, Properties, endpoint positions and signed roll basis remain useful inputs.
NQ/ES deserve verification first based on already-seen evidence, not a clean unseen-data market selection.
Freeze any new calculation scope and criteria before new returns here; do not silently add a stop or intraday exit.

## Differences between the MultiCharts code and the test

No trading code or strategy test was written. This audit preserved the source and PDF unchanged and checked
their rules and arithmetic. Comments about synchronous auto-trading were treated as document content and
were not executed. No live, VPS, broker, API, trading-plan or TIER_LIST changes were made.

Reproduce the static audit with:
`/workspace/venvs/thebeginning/bin/python analysis/codex_s30_source_audit.py`.

Tell Claude: review `agents/codex/results/s30_source_review.md` and `agents/codex/evidence/s30.md`;
reconcile `s30_ibs_test.py` daily MTM to its net trade ledger and rerun the existing personal-portfolio sizing;
the current $33k threshold uses inconsistent costs/roll accounting. No entry-rule change is proposed.
