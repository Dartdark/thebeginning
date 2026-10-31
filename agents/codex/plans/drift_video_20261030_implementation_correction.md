# Drift video: implementation correction before corrected outcomes

Summary: A second-agent audit found that the first implementation allowed half-day decisions through11:50CT.
The committed plan specifies11:30CT. Correct both source-signal and random-time cutoff to that frozen rule.
Also correct the stress metric's displayed fee/slippage subtotals; its net calculation was already correct.
No gate, source rule, parameter or economic definition changes. Preserve the original run, then rerun.

Original preregistration/code commit: ae629418567183d7b21c21c0c803027d801cd09e.
Original implementation SHA256:22a41b1ea4615f549cada46b2249ab4ebeb5bbb7d690c5237038f454760f794f.
Before correction:2,808primarytrades,$12,219.68net,daily t2.3122,side-null p0.0099,time-null p1.0; gatefailed.
There were **zero accepted primary trades after11:30CT on half-days**, but prospective signals and random-time
controls can differ. Do not assume no effect on those artifacts. Retain all originals under
analysis/outputs/codex_drift_video_20261030/pre_correction_halfday/ and rerun unchanged frozen five definitions.
This is an implementation rerun, not a new optimization or an independent sample. The failed original remains visible.

The random-time control conditions on each day's source signal count and side order. It is a retrospective
conditional timing null, not an executable alternative strategy: those complete-day labels are not known at earlier
randomized times. Its p-value must not be presented as profits from a deployable random-entry strategy or proof
that any hypothetical order can be moved earlier using later information. The failed daily-t gate independently stops
advancement. No replacement null or relaxed threshold is authorized after seeing these outcomes.
