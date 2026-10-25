# NQ Overnight Rebound: TEST for a fixed source replication

Summary: The user supplied a cash-down-day overnight long and optional Sunday2 sizing, with966 claimed trades but no MC export.
Existing OvernightAnomaly/Drift research is a close comparator; a higher PF than all-night longs does not establish filter value.
The author inspected336 versions and filters;2023+ is previously seen validation, not a fresh holdout.
New York Fed's2026 follow-up reports disappearance of the narrow02–03ET drift, so older citations cannot substitute for this test.

Sources: user `NQ_Overnight_Rebound_strategy.txt`; preserved under `agents/codex/inputs/rebound/`.
Primary research links/limitations will be preserved by the independent source review. Latest plan snapshote1a94f7.

1. Mechanism: cash selling/inventory pressure can plausibly reverse after close. A down cash return is a proxy, not observed forced flow.
   The proposed European-open timing is a separate empirical claim; neither a rebound nor a current NQ effect follows from a citation alone.
2. Known: cash open/close/range at15CT, before evening entry. Prior-Friday arming remains through Sunday; no weekend future data required.
3. Instrument: NQ one-minute CT cache; native MNQ fills/prices unobserved. Normalize declared ET chart-minus60 into CT, do not shift CT again.
4. Data: cached2017-12-01–2026-10-09, no rebuild. Report authorJan2018–Jul2026 separately;966/923 matched-days cannot be verified without trades.
5. Cost/risk: native$1.24/$1.04 RT perMNQ plus one tick entry and stop/time exit; Sunday2 doubles fees and risk. Market stop gaps can exceed nominal.
6. Power/prior trials:336 reported fitted versions plus rejected filters, unknown additional search. Two supplied sizing models and an unfiltered
   all-nights control only; no new entry/exit/stop/regime search. Full significance must acknowledge prior tuning.
7. Falsifiers/portfolio: fails if costs erase returns, down-day removed trades are profitable enough that filter adds no total/account value,
   direction/timing controls explain it, or addition/replacement loses to current plan/empty slot. Most overlap is current OvernightTick and ONB.
   Overnight equity beta can share drawdowns despite low daily correlation; assess conditional losses and when any offset arrives before breach.

This is authorized research only. No live/VPS/broker settings or keys, ranking, account purchase or deployment.
