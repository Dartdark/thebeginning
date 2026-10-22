# TEST_02: static execution review and corrected reference

Branch `codex/tests`. Read the builder brief, MultiCharts pitfalls and live
Vault Break source before reviewing. TEST_01 is committed/pushed as cb8450b.

Scope: line-by-line review of the supplied signal against the fixed rule and
MultiCharts order timing; write a corrected research reference under results.
No new strategy experiment, threshold search or promotion. Performance trials:
zero. The mechanism/overlap is the identical Vault Break Combined idea, already
rejected for adoption by TEST_01; correcting code does not restore its edge.

Check calendar ATR and warm-up, midnight and VWAP/volume semantics, entry count
through same-bar round trips, entry-bar protective exits, time exits and early
closes, Rithmic rejection guards, quantity units, and whether any decision reads
future information. Confirm uncertain execution semantics using primary
MultiCharts documentation only; do not browse for the strategy.

Decision: the supplied code is NOT SAFE if any material mismatch or risk remains.
The corrected artifact is a static reference, not a verified live deployment:
do not claim compilation, exact Python/MultiCharts parity, guaranteed broker
fills, or an exception to TEST_01. Include line references, severity, concrete
backtest/live effect and fix; explicitly distinguish conditional concerns from
actual defects and harmless constructs.

Validation: reproducible source-line extraction and focused synthetic cases for
daily ATR/no partial startup dates, midnight reset, fast round-trip trade caps,
entry/exits timing, per-contract dollars and holiday schedules. Validate the
corrected text structurally and disclose that Python logic probes cannot compile
or execute PowerLanguage. Preserve all live strategy files and account settings.
