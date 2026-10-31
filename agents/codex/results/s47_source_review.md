# S47 / S47 v2: WATCH — v2 merits verification; the supplied evidence is not live-ready

Summary: S47 follows London-session NQ direction in the US session; v2 also requires the US opening hour to agree.
The overview reports PF 1.30 versus 1.49 and historical drawdown about $3,610 versus $1,739 per MNQ.
Both files leave the entry minute unprotected; same-bar-close exits and next-session fallback need executable verification.
Roughly 3,700 searched cells and reused 2023+ data qualify the evidence; v2's A is the author's own grading scale.
Obtain raw MultiCharts exports and audit Claude's completed rebuild before new variants or account decisions.

Plan: not applicable — supplied-source review; evidence sheet `agents/codex/evidence/s47.md` is NEEDS DATA.
Script: `analysis/codex_s47_source_audit.py`; inputs `agents/codex/inputs/s47/`; output
`analysis/outputs/codex_s47_source_audit/`. **New strategy return trials: 0**. No cache, prices, strategy backtest,
new simulation, portfolio bench or live system was accessed/run by the audit script.

## Rule and version differences

Measure NQ's move from London 07:45 to 08:30 relative to the mean prior overnight range; follow the sign when
its magnitude exceeds 0.0625. Decide after the first US hour at 09:30 CT; enter on the next minute bar, with
stop 0.5 times the overnight-range average, no target and historical time exit at 15:00 CT.
The 09:31 label is a minute-end stamp: its opening instant is the 09:30 clock boundary.

V2 adds the requirement that US 08:30-to-09:30 price direction agrees. It also removes v1's date limits;
**v1 defaults end in 2022**, so the later results necessarily used different date Inputs. The overnight-range,
London clock, roll correction and exits otherwise match. The normalized source diff is saved.

## Reported performance, not independently reproduced

| Author's full-history claim, 1 MNQ | S47 | S47 v2 |
|---|---:|---:|
| Trades | 1,566 | 785 |
| Annual-table net total | $31,253.00 | $24,586.50 |
| Profit factor | 1.30 | 1.49 |
| Win rate | 44.3% | 49.7% |
| Average | $19.96 | $31.32 |
| Historical DD including trade open loss | $3,610.25 | $1,738.75 |
| Reported 95th-percentile closed-sequence simulated DD | $6,184 | $4,018 |

Annual counts/totals reconcile to the overview's rounded headline. The split totals also reconcile.
Some other tables deliberately cover different dates, use Python versus MultiCharts or use different drawdown
definitions. Those differences are not evidence of an accounting error. Exact exports are needed to pair runs.
The net cost convention is $15/NQ divided by ten, not verified actual MNQ fees/fills.

V2's higher PF and smaller historical DD are worth investigating. They do not establish superior total return
or portfolio value: the development disagreement days still have PF 1.23, and the reported kept/removed
difference has t approximately 1.6. Compare identical dates, total dollars and risk, removed trades, matched
random-removal controls and eventually account outcomes. The two headline runs have different end dates;
subtracting their totals is not a valid removed-trade calculation.

## Material execution findings

References below are to preserved `agents/codex/inputs/s47/source_v2.txt`.

- **Entry-minute stop gap:** lines 251-252 place next-bar entries; lines 258 and 266-272 issue stops only after
  a position is visible at the entry bar's close. IOG is off and no `SetStopLoss` backstop exists. Both versions
  explicitly document this behavior. A protective implementation is a separate amendment requiring parity,
  not a silent replay correction. Neither file contains a market fallback if its stop is already through price.
- **Exact-close execution unverified:** lines 260-264 use `this bar on close` for both exits. An assumed historical
  15:00 close fill does not establish an executable automated order/fill at that price. Confirm platform behavior
  and define an executable exit before automation; this review did not compile or run MultiCharts.
- **Next-session fallback does not prevent carry:** lines 259-261 flatten only when a later trading date and
  a new bar arrive. If the intended exit is unavailable, the hold has already happened. The common early-close
  skip list is helpful but cannot establish behavior during missing bars or exceptional market closures.
- **Data gaps:** endpoint flags only establish some prior close, without checking its age (lines 225-238).
  `BarMin >= DecMin` can decide late when the intended bar is absent (241). The overnight count is not proof of
  complete London or US endpoint data. These are static failure cases; occurrence/frequency was not measured.
- **Feed-specific roll handling:** the prior-session 03:31-03:40 splice is causal and the roll session is skipped,
  but its historical schedule assumes the stated unadjusted source. Preserve feed/adjustment/session details;
  running that correction on a different splice or adjusted series can change the volatility unit.

No obvious look-ahead was found in the default signal or prior-session range buffer. Independently comparing
the source's London-open DST formula with IANA time zones gives **zero mismatches across 2,560 weekdays** from
2017-01-01 through 2026-10-23. This verifies the formula, not the chart's actual time zone, data or trading parity.

## Selection, risk and portfolio interpretation

The overview helpfully discloses roughly 3,700 searched grid cells, later variants and four examinations of 2023+.
Its nominal placebo p=0.003 precedes search adjustment. The v2 agreement rule was found after S47's later-period
result was known and retained after another later-period run; 2023+ is therefore historical replication.
The stated clean period begins after 2026-10-08, while v2's supplied overview ends on 2026-10-05: no clean forward
v2 sample is supplied. Its A uses the author's edge-retention/confidence/return-to-DD scale, not our promotion
gates; no repository grade is assigned here.

V2's $4,018 simulated closed-sequence DD is a sizing caution, not an annual probability of breaching Apex's
$2,000 EOD trail. The sequence simulation's horizon, closed-equity statistic and absence of timed account
netting prevent that conversion. The reported $1,739 historical DD is not a safe sizing guarantee either.

This rule enters during the existing US NQ book, despite using London observations. Correlation, concurrent
risk and incremental payouts remain unknown. Prior failed London-follow rules held before the US open and
do not automatically reject this distinct delayed entry. Generic US morning momentum remains a key control.

## Next step

Get native S47 and S47 v2 report workbooks with Settings and trade lists; preserve exact dates, costs, session,
adjustment and code versions. At Claude `3d74b9a`, an S47 rebuild is already in progress. Its return output was
not read or duplicated here. Review the completed replica and its trade pairing next; any stop/exit correction
must be frozen separately before another test. No new filter, parameter search, grading or trading-plan edit
was made. The supplied files are evidence, not instructions to deploy.

Reproduce the document sums, source diff, flags and calendar check:
`/workspace/venvs/thebeginning/bin/python analysis/codex_s47_source_audit.py`.

Tell Claude: review `agents/codex/results/s47_source_review.md` and `agents/codex/evidence/s47.md`; obtain both
raw MC exports, retain the selection-history caveats and freeze executable safety changes separately.
