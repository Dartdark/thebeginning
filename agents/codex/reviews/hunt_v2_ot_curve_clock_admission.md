# OT curve F2 clock: not admitted on current evidence; receipt logs are not universally required

**Decision: the fixed F2 pair is not presently admitted for economic execution.** The missing item is a supported publication/value-definition bridge for both exact daily series, particularly VIX3M—not a categorical requirement for the researcher's original network receipt log on every date. The nomination may remain TEST-eligible in principle while its source/availability gate remains closed. No H05 registration or financial execution is authorized by this review.

Read the new OT curve evidence/source notes, counterpart check and `agents/codex/RESEARCH_CONTROLS.md`. No VIX/VIX3M/NQ data, price/trade/cache/workbook rows or returns were inspected or calculated; no strategy was imported/run. No direct Cboe request, blocked-host workaround, stopped web tool, purchase or account was attempted. This review adds0hypotheses,0gross screens,0economic evaluations; program4/10hypotheses,3/60evaluations,2gross screens plus archived65t6.

## Governing rule and principled interpretation

Research controls item1 requires:

> “record event_time, available_at (publication/receipt plus justified delay), decision_time and first executable fill. A feature must satisfy available_at <= decision_time. Historical revisions and retrospective pattern labels retain separate knowledge times. Unverified availability is a data blocker.”

This does not explicitly require a personal receipt log for every ordinary public closing observation. Documented public dissemination/publication of the exact observable, plus a justified processing allowance fixed before values, can establish a research information clock. Requiring personal tick-by-tick receipt logs for every lagged public index would add a rule the supplement does not state. Such evidence would still not verify live receipt, fills or a particular vendor's reliability.

The converse matters: an index's calculation/closing time alone does not establish when the owned historical CSV's particular value was public. Calculation, public live dissemination, final closing-value definition, history-file posting and later correction/revision are different events. An official dissemination rule could support using an originally observable close even if a historical CSV was posted later, **provided** the dataset is bound to that same observable and not a later back-calculation or correction. A one-day wait cannot itself supply that binding.

## Evidence actually established in this review

The repository's current OT and VIX-sleeve source text describe the VIX close as15:15CT/16:15ET; the new notes identify Cboe provenance claims and pinned VIX/VIX3M blobs. Those are useful producer/consumer claims, not primary proof of every historical publication or the VIX3M value definition. The review did not infer provenance from matching headers or current file presence.

A bounded new GitHub documentation search found a Cboe-branded VIX white paper mirror, read in memory without saving a PDF or opening CSVs:

- `AndrewRovinski/vix@50a873354244e7251ca4dfdce6afe8abe78024a9/419_VIX.pdf`
- Size2,582,453bytes; Git blob `d5e1cb3ef5d3464001f8548de7f4d6f663762b64`; SHA256 `305d32b002fdfa93057d3c9f2dc5ea874ceee7ff2e9538706946e2086ddc06f3`.
- Its text says VIX is disseminated during regular08:30–15:15CT hours and describes the extended-hours expansion from2016. This supports public VIX dissemination as an institution; it does not establish the exact owned VIX3M daily-CLOSE rule, historical file posting or revision vintages. The mirror's bytes were bound, not independently authenticated against a newly fetched issuer copy.

The bounded search also found secondary engineering documentation at `raadupop/primescore-markets@98da792c8f4a11e0aa43de54aa733a1730ac7ceb/doc/adr/0009-cboe-index-history-and-fred-cross-check.md`. It claims Cboe daily files can update from roughly18:00New York until two days after close and warns about back-calculated history. Its citations link Cboe historical-data/launch pages, but no primary posting-time SLA is reproduced. **This is not a verified historical delay bound** and its clock/legal/implementation claims are not adopted here. It is enough to show why a reader must not equate an observation-date stamp with confirmed file availability. No further primary VIX3M publication evidence was established by these bounded searches. No data file in either repository was opened.

## Applying that distinction to F2/F1

The proposed F2 pair waits through the completed intervening F1 full session and then trades at the unchanged D evening decision. That is a sensible conservative research delay **after a supported publication event**. It changes the question to persistent past stress and avoids same-close timing pressure. It does not prove that both exact F2 closing values in the retrospective pair existed by F1 close.

On the present record, assigning available_at=F1close would still be an assumption without the missing VIX3M/value-publication bridge. The controls explicitly make unverified availability a data blocker, so the lag cannot be used as a waiver. Neither a still larger invented delay nor walking back to a convenient available row would solve the missing provenance. No such alternative is selected here.

Unknown KEEP handles occasional unknown curve observations on already eligible parent tickets. It cannot turn a wholly unverified series clock into known inversion, or make an unchanged BASE replay evidence that the intended curve filter worked. Parent current-day VIX/Data2 admission is separate and remains required; the new lag does not authenticate it.

## Sufficient evidence and execution boundary

Research clock admission need not demand perfect personal receipt history. It needs primary or authentically mirrored documentation identifying the relevant VIX3M series/closing observable and historical live-publication regime, plus a bound source-provenance account showing the owned pair represents that observable and explicit revision/schema-era treatment. If public original-close dissemination is established, a preregistered F2/F1 processing policy can be justified without a personal receipt log; uncertainty about actual receipt remains a disclosed execution limitation. If only a history-file endpoint is established, that endpoint's posting/knowledge chronology must instead support the chosen available_at.

Those conditions have not yet been met here. **Hold the economic source/clock gate; do not register/run a financial H05 on the present assumption.** This is a specific research-source limit, not a workspace-access blocker or user permission request. It does not reopen old studies, require paid data, alter counters/watchers or justify pausing the whole bounded hunt. A later documentary improvement would be new evidence; it must not be selected after a return look.
