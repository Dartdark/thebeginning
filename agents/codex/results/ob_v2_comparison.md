# Uploaded OB v2 versus our ONB: WATCH — different execution and filter; superiority is not established

Summary: OB v2 is the Bridge's close-confirmed ORB plus an ATR regime filter, rather than our ONB with one extra gate.
It reports PF 1.75 and $23,094.50/MNQ over 603 trades; its annual totals reconcile, but its raw report is absent.
Our ADX30/ML versions use different entries, ATR definitions, trade caps and account sizing; old direct tests favored ours.
Those old tests cover unfiltered Bridge ORB, not this new filter, whose lookback was selected using seen 2023+ data.
Keep our account-specific versions pending a frozen same-data/same-cost comparison and account-level evidence.

Plan: not applicable — source/evidence comparison, no new return test or parameter selection.
Script: `analysis/codex_ob_v2_comparison.py`; inputs `agents/codex/inputs/ob_v2/`; outputs
`analysis/outputs/codex_ob_v2_comparison/`. **New strategy return trials: 0**.
No price data/cache, strategy replay, new resampling, account run, live platform or broker settings were accessed.

## What "ours" means

The evaluation comparator is `apex_strategies/NQ_Overnight_Bias_ADX30.txt`; the funded comparator is
`funded_strategies/NQ_Overnight_Bias_ML.txt`. The latter is a different filter on our original stop-entry base,
not ADX30 plus ML. Both source files match fetched Claude `e7c394f`; no strategy files were changed.

| Rule | Uploaded OB v2 | Our evaluation ONB | Our funded ONB ML v2 |
|---|---|---|---|
| Overnight range | Midnight-date-reset range to 08:30 | After 23:00 to 08:30 | Same as our evaluation base |
| Entry | 15-minute close beyond OR, then next-bar market | Stop order at OR high/low, with market fallback near/through level | Same stop-entry base |
| Earliest decision | 09:00 close (`Time > 08:45`) | Can place orders at 08:45 | Same |
| ADX | ADX(16) >= 20 | ADX(14) > 30 | ADX(14) > 20 |
| Trade cap | Up to four entry attempts, re-entry allowed | One filled trade/day | One filled trade/day |
| Last entry | Through 12:00 | Before 14:00 | Before 14:00 |
| Stop distance | 0.30 x 15-day RTH true-range average | 0.25 x 15-day calendar-date true-range average | 0.30 x calendar-date average |
| Stop/target anchor | Signal close | Actual fill | Actual fill |
| Additional selection | OR-size/exhaustion gates; ATR15/ATR100 in 0.6-1.2 | No corresponding gates | Frozen ridge score from pre-open features; long >= 0.03 / short >= 0 |
| Quantity | Fixed contracts | Optional dollar-risk sizing | Optional dollar-risk sizing |
| Half-days | No dedicated calendar; fixed 14:30 + SetExitOnClose | Entry cutoff 11:00 / exit 11:30 | Same |

The two ATR denominators differ, so 0.30 versus 0.25 does not imply exactly 20% more dollar risk. Fixed-contract
and risk-sized account results are also different comparisons. The source's midnight reset includes its first
end-stamped bar; use the exact chart/bar definition for parity, not just the prose time label.

## What existing results say

`analysis/bridge_onb_orb_test.py` and its committed output already compared the unfiltered Bridge base on
2018-26 with our MultiCharts lists under the repo's cost convention:

| Existing comparison, per NQ | Trades | Average | PF | t |
|---|---:|---:|---:|---:|
| Unfiltered Bridge ORB replica | 779 | $313 | 1.52 | 4.4 |
| Our evaluation ADX30 MC | 676 | $372 | 1.66 | 4.9 |
| Our funded ML v2 MC | 343 | $636 | 2.12 | 5.0 |

In that earlier two-strategy VB+ONB evaluation test, replacing our ONB with Bridge passed 38.9% versus 46.9%.
The old funded historical-start bench likewise favored our ML version. These are older rosters/models and
the **unfiltered** Bridge rule; they are context, not an account verdict on uploaded v2 or today's bootstrap plan.
The new volatility filter could change risk and selection. No new account test was run here.

Our funded ML source explicitly discloses that frozen weights were fitted over all 2018-26. Its headline
backtest is in-sample; the separately reported walk-forward evidence is the fairer estimate. PF 2.12 alone
does not independently establish dominance over the uploaded candidate.

## What the uploaded evidence establishes

The PDF's annual rows sum to 603 trades and $23,094.50/MNQ, consistent with rounded headline $23,094.
Its design 2017-22 is 324 trades/$8,223; 2023+ is 279/$14,871.50. That is a different date range, data source
and unverified cost/fill accounting from the 2018-26 repo comparison. The implied full-sample average is about
$383/NQ under the author's scaling, not a matched experiment against our $372.

It reports smaller later-period closed DD versus its own unfiltered base, while surrendering some profit.
However, 80/100/120-day lookbacks were compared using 2023+, then 100 chosen from that plateau. This is
historical selection, not a clean holdout pass. The author also reports lower design profit ($8,223 versus
about $11,019.50); this is a risk-reduction claim, not proof that all excluded trades lose money.

Filter-off settings also remove the 100-session warm-up requirement, so a valid filter audit must equalize
history and start dates before measuring kept/removed trades or random-removal controls. The source's new
long ATR can otherwise confound missing warm-up trades with actual ratio exclusions.

The PDF's S uses the author's robustness scale, not the repository's promotion criteria. Its $1,178.25 DD
includes trade open loss; its closed DD is $1,088. Our displayed historical DD uses different dates and daily
closed-equity accounting. Match units, periods, costs and statistic before comparing them. The reported
$2,495 95th-percentile closed-sequence simulated DD is not annual Apex breach probability. Unresolved feed
differences are explicitly disclosed in the PDF and require native trade pairing.

## Execution differences that matter

The upload issues stop/target orders alongside the entry (source 187-205), so the absence of builtin stops is
not sufficient to declare its entry bar unprotected. Verify native order activation instead. Our implementation
uses builtin protection plus a through-stop market guard; no corresponding market fallback appears in the upload.
Signal-close stop anchoring also means fill gaps change actual stop distance and achieved reward/risk.

The upload has no early-close adjustment: a fixed 14:30 exit and `SetExitOnClose` do not establish flattening
before a holiday halt on a Globex chart. Its claim that nothing carries must be checked against actual exit
timestamps. Our existing half-day policy is more explicit, but no live order behavior was reverified here.

## Decision and next step

**Not shown better; retain our account-specific versions.** The added regime filter is a related challenger
worth verifying, not an established upgrade or independent diversifier. Obtain its raw workbook/Settings and
the exact unfiltered reference; preserve all lookback/search history. Before any new return comparison, write
the evidence sheet and commit a fixed plan with matching dates, data, warm-up, costs and fill conventions.
Judge the verified rule on evaluation passes and funded payouts/blown risk/time, including replacement and
empty-slot controls, rather than PF or the historical DD minimum alone. No new filter implementation is proposed here.

Reproduce source/default extraction and existing/published-number reconciliation:
`/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_comparison.py`.

Tell Claude: review `agents/codex/results/ob_v2_comparison.md`; uploaded OB v2 differs from our stop-entry ONB,
and its ATR-regime filter needs an honest matched comparison before calling it an upgrade.
