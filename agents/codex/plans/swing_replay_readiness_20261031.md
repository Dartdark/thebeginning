# Swing Target replay: reproducibility gate

Scope: continue the corrected-exit-kind replay requested in TODO and the 2026-10-31
brief. This is an implementation/reproducibility check, not a new strategy trial.
Sources: Claude 86df2c0 and Codex 70f708a, combined in e6cd629.

The clean `build_lab.py` run already failed in `portfolio.paths` on an empty
entry-to-exit slice. Before using any account result, identify the source record,
enumerate affected reports, and inventory missing cache prerequisites. Do not
drop trades silently, invent exits, substitute old outputs or claim a payout gain.

Check the corrected ST enum on its frozen ledger using the canonical adapter;
record input hashes and counts. Preserve the historical holiday repairs as a
separate known limitation: the traded v3 skips those dates, while this older bench
flattens them at their last available bar.

Only a valid, complete baseline permits a subsequent paired account replay. That
replay must include BASE/ADD/REPLACE/EMPTY at integer quantities, first-year payout
and p5, two-year payout and blown rate, days to sixth payout, fixed seeds/blocks,
and the current 50K T_ONESIDE roster separately from the historical RS roster.
No strategy parameters, allocations, live files, VPS settings or broker actions
are authorized by this check. New strategy-return trials: zero.
