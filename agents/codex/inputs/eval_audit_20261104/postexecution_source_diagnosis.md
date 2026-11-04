# Postexecution source diagnosis: adapter error and genuine input gaps differ

Summary: DT has390kind2flat exits checked against the wrong minute phase in the frozen adapter.
Source logic uses next-bar OPEN; the prepared ledger wrongly leaves exit_open=False, so the builder demands CLOSE.
Separately, first-design ONB30 risk rejects31incomplete15-minute lookback candles, reproduced from raw availability.
That includes10candles missing17:01 plus other expected-open holes; it is not explained away as a holiday or a phase flag.
No frozen input, selection, account result or strategy was repaired by this diagnosis.

DT contains1,521trades:712stops,408targets and401kind2flat exits. Its446exit-phase UNKNOWN rows
comprise390flat phase mismatches and56target-through failures; the latter also have their own quality issue,
so they are not another56independent quote absences. Of401flat exits,400are stamped14:56and1at14:57.
Only11happen to match OPEN and CLOSE. On2018-04-11the14:56ledger exit6592equals the owned OPEN6592;
the same minute CLOSE is6588.25and missing_held_bars=0. This establishes an adapter-phase defect for that example.
Source`dual_thrust_test.py:65`returns the next observed bar's OPEN after the14:55flatten trigger.
Prior`codex_portfolio_audit_prepare.py:133`maps the time but drops this OPEN semantic through its default flag.

For ONB30on2018-04-02the source15-date risk bank covers2018-03-09through2018-03-29.
The31incomplete source candles contain35missing expected-open native minutes
and0observed-in-closed contradictions under the frozen schedule.
The10incomplete17:15candles include an absent17:01bar: raw data onMarch12and14start at17:02.
The other21bad candles contain additional overnight/closing holes. No ATR value, trade return or account outcome
was recomputed. A missing minute's extrema cannot be inferred from neighboring bars to certify sizing.

Reproduction:`postexecution_source_diagnosis.py`; exact counts, minute lists and hashes:
`postexecution_source_diagnosis.json`. The frozen original results remain intact. A causal factual adapter
correction needs a checked amendment, new reproducible tape receipt and separately labeled corrected-model
results; it does not authorize risk-gap weakening or selecting a more favorable path.
