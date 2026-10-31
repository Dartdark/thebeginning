# Weekly cross-review: correction proposals only

Reviewed source: Claude `16145ab15c09fa9489a58ef651f5711c1ef2599f`.
No proposal below has been applied to shared strategy/monitoring code, a trading plan or the VPS.
Five offline defect reproductions: `analysis/codex_weekly_cross_review_checks_20261030.py`.
Fixed recorded-trade accounting: `analysis/codex_weekly_st_kind_audit_20261030.py`.

## 1. Watchdog floor-scan path

At `live/vps/watchdog.ps1:85`, replace the path literal containing U+0002:

```text
old bytes: "$Logs<0x02>*.csv"
new text:  "$Logs\2*.csv"
```

Retain the following filter/sort/iteration pipeline. Inspect the installed copy separately; this review never accessed it.
Acceptance: disconnected PowerShell fixture with temporary TradingLogs data and no network notification sender.
Verify a normal dated CSV is enumerated; room above the configured threshold, below it, and at/below zero produce
the intended no-alarm/near-floor/floor outcomes. Python byte/wildcard checks already reproduce the path failure;
they do not claim PowerShell execution or deployment validation.

## 2. Whole-contract final-risk sizing

In `analysis/ramp_budget_test.py`, construct the 150K quantities before combining paths:

```python
q = {"VB": 20.0, "ONB30": rk(2750, 0.25), "MON_BR": 5.0,
     "EOS": rk(1250, REPORTS["EOS"][1])}
# Feed Wc, Rc directly to evaluation; remove the outer * 2.5.
```

In `analysis/onb_cushion_test.py`, retain each strategy's per-micro path and stop dollars. Compute final ONB quantity
as `floor(final_account_risk * chosen_cushion_multiplier / stop_dollars_per_micro)` on each day; size EOS from the
account's final $500/$1,250 risk. Use integer VB8/20 and Bridge2/5. Do not multiply an already floored quantity by
2.5 or a continuous cushion factor. Honor the intended zero/minimum-quantity policy explicitly, with no new variant.

Acceptance: all per-strategy quantities integral and equal the executable risk formula. Frozen examples: ONB100pt
stop at150K ->13MNQ, not12.5; EOS150pt stop ->4, not2.5. For50K ONB risk capped to half a$1,100cushion ->2MNQ,
not2.5. Then rerun only the existing account variants/histories and reconcile pass/fail/timeout and budget percentiles.
This corrects accounting; it does not select a new strategy, change live risk or establish that a decision flips.

## 3. Swing Target exit-type adapter

Minimal changes to `analysis/swing_target_bench.py`:

```diff
-                          kind=t.reason, date=t.date, net=t.net))
+                          kind=t.kind, date=t.date, net=t.net))
-        x.loc[i, ["j1", "exit", "kind"]] = [last, g.c[d, last], "holiday flat"]
+        x.loc[i, ["j1", "exit", "kind"]] = [last, g.c[d, last], 2]
```

Assert kinds are numeric and a subset of{0,1,2}; preserve the exact three existing holiday repairs and frozen trades.
Acceptance: target exit pays the existing single market-entry tick, protective-stop exit-minute path ends at its
executed fill, and marked/closed totals reconcile to those fixed trades. The recorded-path check already measures
$132/MNQ closing-cashflow difference and48daily minima changes. Rerun the same funded histories for Swing Target
and downstream T_ONESIDE/Nocturne comparisons before retaining their small payout/risk differences. No claim of a
corrected payout improvement is made by this review.

## 4. G10/L1 same-bar coverage

In `analysis/leak_checks.py:report`, keep legitimate closed trades with equal entry/exit chart timestamps for L1.
Identify open-position sentinel rows positively in the report reader, using available closure/signal fields; do not
discard every same-bar trade to remove them. L2 can retain its separate delay-eligible subset.

Acceptance: the planted impossible same-bar fixture must fail L1/G10. The in-memory `>`→`>=` fixture repair changes
100%PASS back to66.7%valid fills; this is a minimal demonstration, not a complete open-sentinel reader fix.
Rerun L1 on every closed plan trade and report expected/checkable/missing fills explicitly. Vault Break alone has
572same-bar closed trades omitted from the existing1756-trade source report. This does not assert those fills fail.

## 5. Pre-market record freshness

Add an injectable as-of timestamp with `America/Chicago` timezone to `analysis/premarket_check.py:check`.
Parse each latest ACCT/POS/SIG capture date/time and require it to be recent; age the stored bar-age value by
elapsed time since capture. A fresh process-health row is not evidence that a particular chart is still updating.
Preserve historical reproducibility by allowing an explicit historical as-of time. Avoid a fixed UTC-5 date shortcut.

Acceptance: at2026-10-30 08:22CT, today's00:05snapshot alerts even if its captured bar_age was0;08:15snapshot remains
green under the existing15-minute feed tolerance. Check stale SIG/POS independently where installed. Exercise an
otherwise healthy snapshot to ensure no spurious alarm. The offline fixture uses fake files and stubs unrelated
floor/version helpers; integrated scheduled checks and the installed VPS remain unverified.

## Ownership and boundaries

Codex has reproduced all five defects offline and proposes the above acceptance checks. Claude owns review and
source-branch corrections; corrected account simulations remain open. Installed-system inspection/testing/deployment
is a separate authorized operational step, not part of this cross-review. Neither agreement nor a passing synthetic
fixture promotes a strategy or changes a trading allocation. No user risk-preference decision is required now.
