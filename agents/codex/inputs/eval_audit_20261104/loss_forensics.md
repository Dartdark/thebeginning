# Four evaluation losses: committed-evidence audit

Summary: Latest Claude commit identifies all four accounts: #1 October26, #3 October30, #2/#4 November4.
The November4 account-equity records are below their trailing floors by09:50, before any later VB chart trades.
Chart-trade logs and fresh "15/15 live matches" are not a broker-fill reconciliation; several rows followed locks/rejections.
Full-stop risk exceeded the remaining cushion on the documented ONB failures; earlier routing/compile incidents also mattered.
These observations justify corrected account-path research, not a claim that a new portfolio or smaller size is already superior.

## Scope and pinned sources

Read-only examination of committed repository documents, CSVs and existing research outputs. No VPS/broker access,
settings, live code or trading action; no strategy-return replay, optimization or new account simulation was run.
Only this research note was written. No commit/push by this agent.

Main current source: Claude commit `13e29ca7b45daabeb0ed2d8c286448610f594dab`, fetched read-only by the parent.
It contains logs/health/journals through November4. The earlier local `codex/work` sources ended October30 and were
insufficient to identify the user's latest four losses. All November2–4 references below are to the pinned Claude
commit, not an installed VPS copy. Times are Chicago as recorded in the sources.

## Loss inventory

|Account|Repository failure date/status|Evidence and limit|
|---|---|---|
|#1,50Kevaluation|October26|`NEW_CHAT_BRIEF.md:10`, older `analysis/journal_trades.py:17` CLOSED registry and `TODO.md:42–44`. Exact last broker fill, final balance and failure-time floor are absent from the saved October26 journal.|
|#3,150Kevaluation|October30|`MULTICHARTS_PITFALLS.md:240–247` documents the broker liquidation; October30 ACCT equity corroborates the breached floor.|
|#2,50Kevaluation|November4|Pinned `live/expected_setup.json:4–8` marks closed; pinned `NEW_CHAT_BRIEF.md:21` reports failure. Raw November4 ACCT and floor alarms corroborate it by09:50.|
|#4,150Kevaluation|November4|Pinned `live/expected_setup.json:19–23` marks closed; same brief and raw ACCT/floor alarms. It began November2 and reused #3's150 tags from that date.|

The user describes four losses in a row. This inventory matches four reported account failures, but does not treat
them as four independent strategy experiments. #2 and #4 traded the same November4 signals; prior documents also
warn that shared/copied evaluations can fail together (`LESSONS.md:57`).

## October30: #3 hit its account floor before its strategy stop

Documented broker incident (`MULTICHARTS_PITFALLS.md:241–247`): start equity about$147,822.60, floor$146,000;
ONB150 short8MNQ at28,664.5 around09:30; Apex bought8 at28,780 at09:38:50. Planned strategy stop28,818 was not hit.

- Observed pre-entry cushion:$1,822.60.
- Nominal planned loss at that source stop:8×$2×(28,818−28,664.5)=$2,456 before costs, already above cushion.
- Gross loss at the documented liquidation prices:8×$2×115.5=$1,848.
- ACCT first reported below-floor observation: `live/trades/20261030.csv:7710`, MON_BR15009:40,equity$145,966.44.
  ONB150 later records the same equity at09:45 (`:7794`); end observations retain it (`:12941` vicinity).
- Starting-to-ending reported equity loss:$1,856.16; $8.16 remains after the documented gross loss. This is an
  observed residual consistent with costs, not an independently verified commission schedule.

The chart logger instead writes ONB150 short8 at28,666.50 and full-stop−$2,480 at its09:45chart marker
(`live/trades/20261030.csv:7569` and`:7750`). The chart remained out of sync after broker liquidation and generated
2,301 exit-rejection lines (`live/health/20261030.csv:2`; documented incident). Therefore the logged chart ticket
cannot be substituted for the actual broker liquidation price/time/P&L.

## November2–4: equity, ratcheted floors and morning failures

The following facts were extracted with Python's CSV reader from `git show13e29ca:<path>`, filtering ACCT field4
exactly for the account ID and reading equity field7. Repeated chart rows were not summed as transactions.
Route-account field9 matches the relevant typed/query account in the displayed November4 samples.

|Date/observation|#2,50K|#4,150K|
|---|---:|---:|
|November2 first ACCT|$49,828.36|$150,000.00|
|November2 final23:55ACCT|$50,767.30|$152,512.84|
|November3 final23:55ACCT|$49,698.64|$150,452.44|
|November4 first ACCT|$49,698.64|$150,452.44|
|November4 first observed below-floor ACCT,09:50|$48,734.58|$148,420.30|
|November4 final16:10ACCT|$48,734.58|$148,420.30|

Source line anchors: November2 final #2`:19134`,#4`:19132`; November3 final #2`:19480`,#4`:19476`;
November4 first #2`:117`,#4`:105`; first below-floor #2`:7900`,#4`:7902`; final #2`:13175`,#4`:13173`.

Using the documented EOD-trailing rules and November2 EOD equity yields floors$48,767.30 and$148,512.84.
The November4 watchdog independently reports the rounded floors48,767and148,513
(`live/health/20261104_alerts.txt:4–5`). Thus November4 opening cushions were about$931.34 and$1,939.60.
The floor reconstruction assumes the recorded November2 value is the relevant EOD high; the matching alarms
corroborate it. Full provider statements would settle exact official floor cents and timestamps.

The November4 chart ONB ticket is long3MNQ/#2and7MNQ/#4 at28,816.50 with177-point full-stop losses
(`live/trades/20261104.csv:7555`,`:7585`,`:7858`,`:7867`): nominal full-stop risks$1,062/$2,478 before costs exceed
those opening cushions. Reported equity losses were$964.06/$2,032.14, with final equity already below the ratcheted
floors before any later VB entries. Exact native broker fills are not supplied for this event; do not infer them
from the chart close rows or reverse-engineer a liquidation price using assumed commissions.

For #4, ending equity$148,420.30 is only$1,579.70below its$150,000start, yet it is below the higher floor after the
November2 profit. Evaluating failure solely against starting balance minus$4,000 would miss the ratchet.

## Material discrepancy in the new "execution OK" narrative

Pinned `NEW_CHAT_BRIEF.md:21` describes November4 failure as "ONB full stop +2VB stops" and cites
`analysis/outputs/live_replay_1020_1104_output.txt` for15/15VBmatches and "execution OK". The saved evidence is narrower.

1. November4 floor alarms occur09:50; the journal's VB chart tickets start10:30,11:30and12:00. Raw ACCT equity
   remains at the failed balances through16:10. Rejection alarms already fire09:45–09:46 and explicitly identify
   VaultBreak orders by10:00 (`live/health/20261104_alerts.txt:3–9`). Those later chart losses are not needed to
   explain account failure and cannot be called broker fills without broker execution records.
2. November3 account equity declines by$1,068.66/#2and$2,060.40/#4. Yet the journal's three chart VB trades sum to
   **+$92/+$230gross** (−1,204+652+644;−3,010+1,630+1,610). Rejection bursts appear10:18–10:20 and AA-off alerts
   follow10:30 (`live/health/20261103_alerts.txt:1–6`). This is consistent with first-loss daily liquidation/lock
   followed by chart-only re-entries, not proof that all three later chart trades filled. Exact cause/fees need the
   broker order/fill statement; the discrepancy cannot be dismissed as routine commission differences.
3. The replay's15VBrows include October20 (`...live_replay...txt:8`), already documented as a rejected@MNQ entry
   rather than an actual fill (`live/orders_20261020_21.md:24–26`), November3later chart re-entries (`replay:18–19`),
   and November4post-floor chart trades (`replay:20–22`). Its conclusion is chart-signal similarity, not broker
   execution parity. The source itself marks its code provenance dirty (`replay:1`).
4. ONB's October27winner was missed after a compile failure (`MULTICHARTS_PITFALLS.md:209–214`); the new replay
   preserves that difference (`replay:26`) and also has different October30/November4ONBentries (`replay:27–29`).
   Matching eventual loss direction does not establish equal exposure, fill timing or account-survival path.

Do not replace these discrepancies with a claim that all four losses were software failures. A losing signal
stretch exists in the paper/model paths, and normal trading losses consumed the remaining cushion. What is not
established is the stronger assertion that the actual broker path matched all strategy chart trades.

## Earlier documented operational exposure

- October26copied chart routing sent #3's20MNQVBorders to #2, whose correct VBsize was8MNQ: combined28MNQ,
  nominal75-point stop$4,200 (`MULTICHARTS_PITFALLS.md:194–200`). This concerns #2, not proof of #1's failure cause.
- October19a50K daily-loss liquidation closed VB8 at about−$1,017 before its$1,200strategy stop, while the chart
  retained its position and resent exits (`MULTICHARTS_PITFALLS.md:106–115`). This is precedent for treating broker
  daily lock and strategy-state continuation separately.
- #1's charts continued after its reported October26failure; subsequent logged trades were rejected
  (`live/vps/LIVE_GUARD_PLAN.md:17–18`; `TODO.md:42–44`). Its October26journal Accounts table is blank, so a precise
  last-fill/equity-floor reconstruction is not available. October21dashboard evidence had already put its cushion
  around$398 (`live/orders_20261020_21.md:34–40`), but intervening equity is missing and that is not its proven failure-day cushion.

## Implications for the parent's bounded evaluation research

- Admit actual integer quantities, costs, within-day open equity, EOD ratchet and floor touch, daily-loss lock,
  cancellation of all later orders after lock/failure, time limit and account-specific starting state. An EOD-only
  daily sum cannot substitute for that path or recover lost re-entries after broker liquidation.
- Current `analysis/account_tools.py:14–16,85–104` states its dashboard pass-odds helper uses daily P&L and omits
  daily-loss limits; it only observes floor/target after each daily increment. It is not evidence that a thin
  intraday position can survive to its planned stop. Do not confuse this helper with the separate evaluation bench.
- The November4sizing bench's "no sizing would have survived" is a result for the listed finite configurations and
  simulator assumptions, not an exhaustive theorem. Pin its dirty provenance, reconcile its daily/pause/risk path
  before relying on the conclusion, and preserve all prior selection history.
- Tests of cushion-limited risk, smaller fixed size, different strategies and reduced common-direction exposure
  are justified research questions. The historical facts alone do not demonstrate higher pass rate, lower fee per
  success or an optimal replacement. Reduced failures can become time-outs; objective and uncertainty must be explicit.
- No fresh account/rule/deployment recommendation follows automatically. Raw broker statement/order history,
  official per-account floor ledger and dated actual settings would narrow unresolved incident attribution, but
  the parent can continue independent historical portfolio research without waiting on them.
