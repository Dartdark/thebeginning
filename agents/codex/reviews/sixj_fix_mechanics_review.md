# Independent review: synthetic 6J fixing mechanics

Reviewer: separate `sixj_mechanism_review` agent, 2026-10-27. Scope is source and
invented mechanics only. No market inputs, native specifications or actual
event schedule were admitted. No economic result or financial promotion review.

Initial source review confirmed direction SHORT6J conditional on net USD buying,
the previous-date18:55CST/19:55CDT clock, no automatic post-fix reversal, actual
flow/calendar/cost uncertainty and adverse prior proxy selection history.
These support, at most, a small future source/gross-screen proposal, not a full
backtest or export on the strength of the story alone.

Initial code at `d143a80`: independent `runpy.run_path` and `run_checks()`
(main not executed) passed19 bundled cases. Reviewer found that the helper
could accept09:10 when the intended09:06 open was missing. Root retained the
initial output, committed an explicit scheduled-open requirement plus the
adversarial case in `4c09e21`, then executed the revised synthetic-only harness.

Revised independent verification:

- All20 bundled cases pass and exactly match `synthetic_checks_v2.json`.
- Three additional invented cases pass: missing09:01 despite a later09:10
  observation returnsNone; scheduled time equal to receipt returnsNone; exact
  scheduled future open supplied after receipt is accepted.
- Current code/plan bytes match committed `4c09e21` and revised manifest hashes.
- No main/output execution by the reviewer, writes, bytecode, data or network
  intake. Root alone produced the retained two synthetic output files.

|Artifact|SHA256|
|---|---|
|Revised plan|`b94136b75441bd26cf8d1bd3b8c9a2ee18c881c3f883c3ecfe94ffee7b6e08e3`|
|Revised script|`b710005e5b6d95a90ab865e841604bd3f6753fa91eebd6c2591338dd46262872`|
|Initial19check output|`3f8f2ba5784811595af6b33e01a87209dc0e2fc54f46070bc41454329cb38553`|
|Revised20check output|`94b633130589c5f67d13c9a3996e45669679849755bdc5c22a24356259063103`|

No material mechanical issue remains **within the declared scope**. Assumed
multiplier/tick/fees are not certified native specifications. Real holidays,
fixing conventions, volumes/net orders, fills, stops and book benefits remain
unverified. Prior NQ/hourlyFX failures remain in selection history. Mechanical
PASS is not statistical or account PASS; NEEDS DATA / SOURCE CONFIRMATION remains.

This separate user-requested manual follow-up adds0hypotheses/0grossscreens/
0economicmodels. Hunt v2 remains10/10,5/60,4gross and paused. No resumption,
automation setting change, t6 research, proxy rerun or live action is authorized
or established by this review.
