# ORB30: fixed current-personal19 diagnostic contrasts

Commit before accessing book returns. Original protocol9fc1b3f; source rule/selection unchanged.
Current latest Claude7f0800ffc04d56bd878750369a4abc2316ee01d8 inspected. The five personal roster/script/published-output blobs are identical to afde088, so reuse the reviewed saved19-column baseline at each native fee1.24/1.04 from analysis/outputs/codex_rebound/personal19/UNIFORM/fee_*/baseline_daily19.csv; verify blob equality again in script. No reconstructing caches or assuming updated funded roster identical.

Fixed models FULL185/SELECTED4/SELECTED0 already design-passed; no selecting or tuning from book results. Candidate exactly1MNQ per trade, proper native fee and adverse tick costs. Compare BASE, ADD1, EMPTY_ONB, REPLACE_ONB for A/B/C/D and FULL19, same fixed starters as prior reviewed scripts. ONB chosen before book returns because both trade morning upside breakouts; no loss-conditioned events.

Save daily baseline/candidate, total coverage/mapping, correlation and conditional candidate-on-book-loss-day P&L. All candidate dates must map exactly to baseline calendar; do not silently clip/rebook. If a date is absent, stop book test and report missing dates. Preserve baseline pre2018-to-first2018 ledger convention, flag it; primary2023+ avoids that issue. Baseline remains published research representation, including previously documented per-day fee approximation, incomplete OT tail and Twin marks; it is not verified live equity or joint intraday margin.

Use paired1000 one-year10-day block histories seed20261027, same histories for everyconfiguration/model. Report mean/median profit, DD95, median profit/DD95, loss probability, and fixed5%/95% daily-block annual contribution interval from5000 histories. Cohorts2018+ and2023+; use common native candidate window through2026-10-09 and report last baseline date. No Apex rules applied to personal.

This diagnostic can expose material harm/benefit; it cannot establish allocation readiness without independent raw-data replication and native platform parity. 50K/150K evaluation/funded remain separately LIMITED if causally joint overnight baseline paths are unavailable; no pass/payout probability invented. Keep one-contract standalone EOD-trail illustrations separate from full accounts. No live settings/allocations/ranking changes.
