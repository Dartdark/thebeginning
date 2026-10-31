# Extended-data rebuild: unfinished report trade confirmed; expected coverage still stale

Summary: NQ price files already reach October 30; the NQ and ES grids rebuilt successfully.
The documented lab rebuild crashes on an unfinished ONB ML trade, exported with an `open` pseudo-exit.
The four evaluation reports cover only October 9–13; rebuilding prices does not generate their later trades.
Do not treat a refreshed grid/cache as a completed October 12–28 missed-trade check.
Concurrent Codex work supplied an offline adapter; its five regression tests pass. Fresh expected trades are still needed.

Script: `analysis/codex_rebuild_readiness.py`

Output: `analysis/outputs/codex_rebuild_readiness/`

Source checked: `86df2c0fa4b0e530b2c29caddd364830d12edab3`

Trials run: 0 (input integrity and existing-code reproduction only).

## Verified results

The first open TODO asks for a cache rebuild, fresh plan benches and a comparison of each live strategy's
October 12–28 trades against expected trades. The audit distinguishes those separate prerequisites.

| Input | Verified coverage / status |
|---|---|
| `data/NQ_1min_2026.csv` | Last bar October 30, 15:15 CT; 92,585 rows, no duplicate date/time keys |
| `data/NQ_1min_ON_2026.csv` | Last bar October 30, 07:59 CT; 203,390 rows, no duplicate date/time keys |
| VB evaluation report | Settings End Date October 9, 16:00 |
| ONB ADX30 evaluation report | Settings End Date October 13, 04:45 |
| Bridge Monday evaluation report | Settings End Date October 13, 10:15 |
| EOS evaluation report | Settings End Date October 11, 19:35 |
| ONB ML funded report used by build_lab | One unfinished trade represented as an exit; see below |

Coverage ends come from the reports' Settings sheets, not their last trade. A strategy can correctly have no trades
near the end of its covered interval. Price endpoints and duplicate checks do not establish complete minute coverage.

## Reproduced rebuild failure

Ran the existing `analysis/build_lab.py scratch_data` with numba installed in an isolated workspace dependency directory.
It wrote `g24.pkl` and `ge.pkl`, loaded 1,743 VB trades, and then failed before writing `lab.pkl`:

```
portfolio.py, paths(): adv[-1]
IndexError: index -1 is out of bounds for axis 0 with size 0
```

The final ONB ML source pair (zero-based index 343) is:

- EntryShort: October 12, 09:15, 30,936.00, signal `ON Bias S`.
- ExitShort: October 12, 00:00, 30,860.75, signal `open`.

`portfolio.load_mc` accepts every `Exit*` row, including this unfinished-position marker. On the rebuilt grid it becomes
`j0=546`, `j1=0`, `kind=2`. `paths` receives an empty interval and indexes its last element. This is an import defect,
not evidence of an actual midnight broker exit. The unfinished mark must not be booked as a completed trade.

Smallest proposed core fix for Claude: exclude explicit unfinished/open report pairs before constructing closed trades;
check entry/exit pairing and date chronology; report exclusions. Preserve legitimate cross-date strategies using their
existing dedicated loaders. Do not silently clip `j1` to `j0`, replace the exit with a market price, or suppress the error.
Regression check: this report should supply 343 completed pairs rather than 344; closed-trade results should be unchanged.
Core loaders were left unchanged under the Codex builder's write boundaries.

## Why refreshing the dashboard is insufficient

`live_panels.py` uses `portfolio.load_mc` and `load_bridge_mc` to load saved trade lists. Its rebuild branch does not
execute VB, ONB ADX30, Bridge or EOS rules on the new dates. Extending the calendar therefore cannot verify new expected
trades. Days after each report ends must be treated as uncovered, not as verified zero-trade days.

The live files also contain repeated CLOSE rows: October 26 has 29 rows / 9 unique full rows, October 27 has 28 / 9,
October 30 has 9 / 2. These counts do not establish broker fills or independent market events. Existing deduplication
and account retirement rules remain necessary.

## Remaining work

Concurrent update: remote `codex/work` advanced during publication to `eac908f7`, adding
`analysis/codex_refresh_audit.py` and [its report](extended_data_refresh_20261030.md). It already implements the scoped
unfinished-position adapter proposed above. Its five regression tests were rerun successfully here; the same adapter
was used to recheck the rebuild (`build_recheck.txt`): it completed with 343 closed ONB ML trades and wrote all three
pickles. Its printed portfolio scores are historical builder examples, not a validation of the current plan.
This confirms the original source failure independently and
avoids a duplicate implementation. Execution-reference E39 already records the shared finding.

1. Adopt the checked unfinished-position handling in the production importer after review; its original direct command
   still fails. Use the scoped adapter for offline rebuilding meanwhile.
2. Regenerate expected trades with the already validated Python rules, checking their known parity limits, or obtain
   fresh MultiCharts backtest exports for VB, evaluation ONB ADX30, EOS and Bridge through October 30.
3. Compare against deduplicated chart logs within verified coverage; use native account-attributed order/fill exports
   for actual executions. The chart logger alone cannot settle fill or slippage questions.
4. Only then refresh the cache and account benches with explicit common coverage dates.

Validation: audit script completed on the real inputs; Python compilation passed. No trading rule, live configuration,
dashboard asset or plan was changed. The TODO's complete replay and bench refresh remain outstanding.
