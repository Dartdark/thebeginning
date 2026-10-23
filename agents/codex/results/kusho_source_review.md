# Kusho FAR final / v9: WATCH — frequent retest candidates, but the supplied holds do not fit Apex

Summary: The overview reports PF 1.40/1.43 and $10.01/$11.24 per MNQ trade for FAR final/v9; annual totals reconcile.
Both rules permit evening and weekend holds, so they are unsuitable for the current Apex plans as supplied.
Stop activation, nonpositive swing risk, pre-fill break-even excursions and roll handling need verification.
The author's S grade is a different scale; failed validation checks and reused later data remain disclosed limits.
Obtain native reports and the already-tested intraday version before a new return trial or any account decision.

Plan: not applicable — uploaded-source/document review, not a strategy return test.
Evidence: `agents/codex/evidence/kusho.md` (NEEDS DATA). Script: `analysis/codex_kusho_source_audit.py`.
Inputs: `agents/codex/inputs/kusho/`; output: `analysis/outputs/codex_kusho_source_audit/`.
**New strategy return trials: 0**. No prices, cache, strategy replay, new bootstrap, account bench or live system was used.

## Rule and reported results

FAR buys a retest of a completed bullish 15-minute bar above EMA(50), with lower wick at most 70 ticks.
Its next-bar buy limit uses the signal bar's open. It chooses a recent fractal swing stop and 3R target when
the source accepts the risk; otherwise it uses 200-tick stop/target. Structural trades have an early half-R
break-even step. V9 adds mirrored shorts only when the prior-session daily-close regime is declining.
Both share one position slot and generate an evening market exit from 21:00 CT, permitting Friday-to-Sunday holds.

| Author's full-history claim, 1 MNQ | FAR final | V9 |
|---|---:|---:|
| Trades | 3,142 | 3,586 |
| Net after reported roll adjustment | $31,448 | $40,308 |
| Profit factor | 1.40 | 1.43 |
| Win rate | 58.4% | 58.3% |
| Average trade | $10.01 | $11.24 |
| Historical DD including trade open loss | $1,519.75 | $1,555.75 |
| Reported 95th-percentile closed-sequence simulated DD | $3,184 | $3,198 |

Annual totals reconcile exactly. The older robustness/development tables identify earlier exports and pre-roll
correction snapshots; those different counts/totals are not an unexplained contradiction. Actual fee/fill
accounting remains unverified: PDF cost wording differs in units from the per-side/per-order source headers.

V9's reported $8,860 improvement comprises $8,514 short net and $346 higher long net. It has 3,116 longs versus
FAR's 3,142, plus 470 shorts. Shorts share a position slot and can block long opportunities; exact changes need
paired native ledgers and identical settings. Do not treat the short ledger as an independent additive stream.

## Execution and data findings

Line references use preserved `far_final.txt` and `v9.txt` in the input directory.

- **Not Apex-eligible as supplied:** both default to 21:00 exits and permit weekend carry. The PDF reports 141
  weekend trades without a per-version breakdown. It already describes a separate 15:45 flattening version
  ($27,203 versus $32,562 on that older comparison, PF 1.36 versus 1.43). Obtain that code/report rather than
  silently change these files or label it a new finding. Its early-close behavior still needs confirmation.
- **Protection depends on missing calculation settings:** FAR 79-115 and v9 200-272 initialize exits only when
  a calculation sees an open position; subsequent exits are `next bar` orders (FAR 128-138, v9 293-315). Neither
  source forces IOG or contains builtin protective exits. Under bar-close calculation the filled 15-minute
  entry bar is unprotected. A one-minute Bar Magnifier alone does not establish recalculation on fills.
  Obtain IOG/recalculate-after-fill settings before asserting the precise historical activation time.
- **Zero/negative swing risk accepted:** FAR 106-112 and v9 227-233/263-269 check only the maximum distance.
  No positive-distance requirement exists. A swing on the wrong side of entry can therefore select an invalid
  stop and reversed target. Synthetic counterexamples are saved; historical occurrence is unknown.
- **Break-even chronology:** FAR 118-123 and v9 275-288 use the entire current bar's high/low. A retest limit can
  fill after the bar's favorable extreme, so break-even may arm without that excursion occurring after entry.
  This is not future leakage when orders are sent at bar close, but it differs from post-entry favorable movement.
  Both lack a market fallback when a newly raised stop is already through the market.
- **Roll accounting is not fully verified:** the PDF says four long trades in each run had $1,592.50/MNQ of
  artificial roll gain removed. That is a necessary disclosure, not a demonstration of the counterfactual trade
  exits or intratrade risk path. V9's correction (107-157) changes stored regime closes only, leaving raw EMA,
  swings and open-position levels. Its older gap measure includes ordinary bar movement, and the PDF admits
  the assumed later roll timing is wrong for some dxFeed rolls since mid-2024. Audit original/corrected trades
  and actual-contract/splice data; do not subtract the reported gap a second time.

The next-bar retest order is causal; it does not buy retroactively at the signal bar's open. The recent fractal
is based on already-known neighboring bars. V9's short filter uses completed prior-session closes; no obvious
future daily observation enters it. The unresolved issues concern execution chronology, data and validation,
not a claim that the entire signal looks ahead.

## Evidence and portfolio interpretation

The overview discloses optimized wick/break-even settings, a redesign that failed two of four preset validation
checks, an already-seen 2023+ window and another look for v9. Better risk outcomes can be useful, but should not
be described as passing the original full decision rule. A complete search count, raw ledger, t/DSR and independent
replication are absent. The author's S uses its own retention/confidence/return-to-DD scale; PF 1.40/1.43 is below
the repo's stated S PF requirement. No repository grade is assigned by this review.

Tail dependence is material but not an automatic rejection: the PDF says FAR's best 10% generate 232% of net,
with the remainder losing overall. Forward tracking must capture whether that tail remains available at
executable fills. Closed-sequence simulated DD is not an annual Apex breach probability and cannot establish
the safety of a historical $1,520-$1,556 drawdown. Overnight/weekend gaps add risks beyond nominal stop distance.

Its frequency and limit-entry design make it worth verification as a personal-account candidate. The US-session
entry window still overlaps the existing NQ book; the short label alone does not establish protection or
diversification. No exact Kusho item was found in TIER_LIST/WATCHLIST at Claude `e7c394f`; related wick/order-flow
and swing-risk ideas are not exact replicas.

## Next step and reproduction

Obtain both full native MultiCharts reports, their Settings and exact code versions, original/corrected roll
accounting and the already-tested intraday version. Check same-bar limit chronology, protective-order activation,
positive swing risk and post-fill break-even before independently reproducing returns. Any correction must be
a separately frozen implementation; no parameter rescue or funded bench was started here.

Reproduce the annual-claim sums, source flags and synthetic arithmetic with:
`/workspace/venvs/thebeginning/bin/python analysis/codex_kusho_source_audit.py`.
Uploaded originals are preserved byte-for-byte with hashes. Source instructions about auto-trading modes were
treated as document content, not authority to change broker/platform settings. No strategy/plan/live files changed.

Tell Claude: review `agents/codex/results/kusho_source_review.md` and `agents/codex/evidence/kusho.md`; get native
reports and the existing intraday version, and verify entry/BE/roll chronology before another trial.
